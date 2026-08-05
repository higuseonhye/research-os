"""Sweep the carrier's settling time, and watch Paper 002's operator return.

The manuscript's §4.3 asserts a criterion it does not measure: the carrier must
come to rest inside the time it holds the target, and its settling time must be
short relative to the action's commitment latency. That is an inference from two
separate physical measurements, and an inference is not a result.

Settling time is a property of the *carrier*, and on CPU the carrier is ours to
specify. So inject settling into the injected coupling, sweep it over the one
configuration where the relation is known to be necessary, and see whether the
mode operator comes back.

The rule and four numbered predictions were fixed before this file existed:
docs/paper003/paper003_settling_sweep_prereg_v1.0.md

    python scripts/paper003_settling_sweep.py --seeds 60
    python scripts/paper003_settling_sweep.py --seeds 60 --derived-pause

`--derived-pause` is P4: raise `burst_off` to settling + `min_ride_steps`, the
rule already applied physically, and check whether arm B rises with arm D. If it
does, the physical `burst_off` 25 anomaly belongs to the commit policy rather
than to Isaac.

CPU, injected coupling. Not confirmatory, and no score here may be reported
beside a physical one without that label.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from wm_expansion.cell import CellSpec, run_cell
from wm_expansion.commitment_episode import EpisodeSpec
from wm_expansion.encounter import EncounterSpec

TARGET = np.array([0.20, 0.0, 0.40])
ARMS = ("B", "C", "SELF", "D")

#: Preregistered. 22 is the arm's measured settling time, so that row is the CPU
#: counterpart of the physical run.
SETTLINGS = (0, 1, 2, 3, 4, 6, 9, 14, 22)

#: Fresh, and distinct from 300 (arm sweeps) and 3000 (the amended SELF band), so
#: no configuration is re-read on cells it was tuned against.
FIRST_SEED = 7000

#: The gate's own requirement, and the term the physical repair rule added to the
#: settling time. Not a free parameter here.
MIN_RIDE_STEPS = 3


def row(settling: int, seeds: int, derived_pause: bool) -> dict:
    burst_off = settling + MIN_RIDE_STEPS if derived_pause else 4
    encounter = EncounterSpec(
        bodies=1,
        schedule="burst",
        settling_steps=settling,
        burst_off=burst_off,
    )
    records = []
    for seed in range(FIRST_SEED, FIRST_SEED + seeds):
        record = run_cell(
            TARGET,
            EpisodeSpec(),
            encounter,
            CellSpec(condition="coupled", seed=seed, coupling="capture"),
            drive=lambda target: False,
        )
        if record["resolved"] is not None:
            records.append(record)
    if not records:
        return {"settling": settling, "burst_off": burst_off, "n": 0}

    scores = {arm: float(np.mean([r["resolved"][arm] for r in records])) for arm in ARMS}
    engaged = [bool(r["d_estimated"]) for r in records]
    landed = [bool(r["resolved"]["D"]) for r in records]
    # Discordant pairs, the statistic the physical run turned on: cells where
    # exactly one of the two arms lands. A marginal rate hides which arm is
    # winning where.
    d_only = sum(1 for r in records if r["resolved"]["D"] and not r["resolved"]["SELF"])
    self_only = sum(1 for r in records if r["resolved"]["SELF"] and not r["resolved"]["D"])
    return {
        "settling": settling,
        "burst_off": burst_off,
        "n": len(records),
        **scores,
        "D_minus_B": scores["D"] - scores["B"],
        "engagement": float(np.mean([float(e) for e in engaged])),
        "D_given_engaged": (
            float(np.mean([float(l) for l, e in zip(landed, engaged) if e]))
            if any(engaged) else None
        ),
        "discordant_D_only": d_only,
        "discordant_SELF_only": self_only,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=60)
    parser.add_argument("--derived-pause", action="store_true",
                        help="P4: burst_off = settling + min_ride_steps")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    rows = [row(s, args.seeds, args.derived_pause) for s in SETTLINGS]

    label = "burst_off = settling + 3" if args.derived_pause else "burst_off = 4"
    print(f"capture / burst / 1 body, {label}, seeds "
          f"{FIRST_SEED}..{FIRST_SEED + args.seeds - 1}")
    print()
    print(f"{'settle':>6} {'off':>4} {'n':>4} "
          f"{'B':>6} {'C':>6} {'SELF':>6} {'D':>6} {'D-B':>6} "
          f"{'eng':>5} {'D|eng':>6}  D:SELF")
    for r in rows:
        if not r.get("n"):
            print(f"{r['settling']:>6} {r['burst_off']:>4}    0")
            continue
        conditional = r["D_given_engaged"]
        print(f"{r['settling']:>6} {r['burst_off']:>4} {r['n']:>4} "
              f"{r['B']:>6.3f} {r['C']:>6.3f} {r['SELF']:>6.3f} {r['D']:>6.3f} "
              f"{r['D_minus_B']:>6.3f} {r['engagement']:>5.2f} "
              f"{('  n/a' if conditional is None else f'{conditional:>6.3f}')}"
              f"  {r['discordant_D_only']}:{r['discordant_SELF_only']}")

    # The predictions, checked here rather than by eye, because reading a table
    # and deciding afterwards what it showed is the failure this project has a
    # written rule against.
    print()
    by_settling = {r["settling"]: r for r in rows if r.get("n")}
    if not args.derived_pause:
        at_four = by_settling.get(4)
        if at_four:
            print(f"P1  C >= 0.90 at settling 4      : {at_four['C']:.3f}  "
                  f"{'PASS' if at_four['C'] >= 0.90 else 'FAIL'}")
            monotone = all(
                by_settling[a]["C"] <= by_settling[b]["C"] + 1e-9
                for a, b in zip(SETTLINGS, SETTLINGS[1:])
                if a in by_settling and b in by_settling
            )
            print(f"P1  C monotone in settling       : "
                  f"{'PASS' if monotone else 'FAIL (see table)'}")
            print(f"P2  D - B <= 0.05 at settling 4  : {at_four['D_minus_B']:.3f}  "
                  f"{'PASS' if at_four['D_minus_B'] <= 0.05 else 'FAIL'}")
        crossing = next((r["settling"] for r in rows
                         if r.get("n") and r["C"] >= r["D"]), None)
        print(f"P3  C overtakes D within [2, 6]  : {crossing}  "
              f"{'PASS' if crossing is not None and 2 <= crossing <= 6 else 'FAIL'}")
    else:
        at_22 = by_settling.get(22)
        if at_22:
            print(f"P4  B >= 0.40 at settling 22, burst_off 25 : {at_22['B']:.3f}  "
                  f"{'PASS' if at_22['B'] >= 0.40 else 'FAIL'}")

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(rows, indent=2))
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
