"""Where does the SELF arm catch up? The time bound on H2's protection.

The preregistered comparison settled that arm D beats the single-entity arm in
the band the protocol commits in, [+4, +6]. It also recorded a limitation: SELF
loses there partly because it holds a median of 4 steps of its own motion
against a 14-step burst cycle, so the protection is bounded in time rather than
absolute. This measures where the bound is.

**Rule, fixed before running** (this is descriptive - it cannot rescue or kill
the paper, so it carries a lighter rule than the confirmatory comparison, but
the same discipline about fixing it first):

    seeds        from 1000 upward - disjoint from the 300..922 the
                 preregistered run consumed, so this is fresh data
    population   capture coupling, burst schedule, 1 body, condition `coupled`
    offsets      every commit offset from -6 to +40 relative to the arrival
    scoring      at each offset, both arms aim and are scored against the true
                 landing `dispense_latency` steps later
    bin size     at least 50 paired cells for an offset to be reported
    caught up    the first offset from which SELF is no longer beaten - a
                 one-sided exact McNemar at alpha = 0.05 fails - and stays that
                 way for the rest of the range

**This is an off-protocol probe and its numbers are not protocol results.** The
commit window admits only [-6, +6] around an arrival; everything outside that is
a commit the protocol would never make, evaluated here to characterise the arm
rather than to score it. It does not touch `run_cell`: the episode is replayed
over the recorded observations, which is exact, because the episode is
physics-agnostic and consumes only the (target, bodies) stream.

    python scripts/paper003_self_arm_bound.py
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from math import comb

import numpy as np

from wm_expansion.cell import CellSpec, contact_arrivals, run_cell
from wm_expansion.commitment_episode import CommitmentEpisode, EpisodeSpec
from wm_expansion.encounter import EncounterSpec

TARGET = np.array([0.20, 0.0, 0.40])

FIRST_SEED = 1000
OFFSETS = range(-6, 41)
MIN_BIN = 50
ALPHA = 0.05


def exact_mcnemar_one_sided(wins: int, losses: int) -> float:
    total = wins + losses
    if total == 0:
        return 1.0
    return sum(comb(total, k) for k in range(wins, total + 1)) / 2.0**total


def replay(record: dict, spec: EpisodeSpec) -> dict[int, tuple[bool, bool]]:
    """Score arm D and SELF at every step of one cell, keyed by commit offset."""

    observations = record["observations"]
    targets = np.asarray([o["target"] for o in observations])
    bodies = np.asarray([o["references"] for o in observations])
    arrivals = contact_arrivals(targets, bodies, spec.interaction_radius)
    if not arrivals:
        return {}

    episode = CommitmentEpisode(spec=spec)
    scored: dict[int, tuple[bool, bool]] = {}
    for step in range(len(observations)):
        episode.observe(targets[step], bodies[step])
        landing_step = step + spec.dispense_latency
        if landing_step >= len(targets) or len(episode.targets) < 2:
            continue
        if not episode.ready:
            continue
        landing = targets[landing_step]
        aims = episode.aims()
        offset = min((step - a for a in arrivals), key=abs)
        scored[offset] = (
            bool(np.linalg.norm(aims["D"] - landing) <= spec.tolerance),
            bool(np.linalg.norm(aims["SELF"] - landing) <= spec.tolerance),
        )
    return scored


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=400)
    parser.add_argument("--json", type=str, default=None)
    args = parser.parse_args()

    spec = EpisodeSpec()
    encounter = EncounterSpec(bodies=1, schedule="burst")
    bins: dict[int, list[tuple[bool, bool]]] = defaultdict(list)
    for seed in range(FIRST_SEED, FIRST_SEED + args.seeds):
        record = run_cell(
            TARGET, spec, encounter,
            CellSpec(condition="coupled", seed=seed, coupling="capture"),
            drive=lambda target: False,
        )
        for offset, outcome in replay(record, spec).items():
            if offset in OFFSETS:
                bins[offset].append(outcome)

    rows = []
    print(f"{'offset':>7} {'n':>5} {'D':>6} {'SELF':>6} {'D-only':>7} {'S-only':>7} {'p':>10}  beaten")
    for offset in sorted(bins):
        pairs = bins[offset]
        if len(pairs) < MIN_BIN:
            continue
        d = np.array([p[0] for p in pairs])
        s = np.array([p[1] for p in pairs])
        wins = int(np.count_nonzero(d & ~s))
        losses = int(np.count_nonzero(~d & s))
        p = exact_mcnemar_one_sided(wins, losses)
        beaten = p < ALPHA
        rows.append(
            {"offset": offset, "n": len(pairs), "p_D": float(d.mean()),
             "p_SELF": float(s.mean()), "D_only": wins, "SELF_only": losses,
             "p_value": p, "self_beaten": beaten}
        )
        print(f"{offset:+7d} {len(pairs):5d} {d.mean():6.2f} {s.mean():6.2f} "
              f"{wins:7d} {losses:7d} {p:10.2e}  {'yes' if beaten else 'NO'}")

    tail = [r for r in rows if not r["self_beaten"]]
    caught = None
    for index, row in enumerate(rows):
        if all(not later["self_beaten"] for later in rows[index:]):
            caught = row["offset"]
            break
    print()
    print(f"SELF caught up from offset {caught}" if caught is not None
          else "SELF never caught up within the measured range")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump({"rows": rows, "caught_up_from": caught}, handle, indent=2)


if __name__ == "__main__":
    main()
