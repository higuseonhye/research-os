"""Read the capture pilot, and turn it into the four numbers the prereg waits on.

`docs/paper003/paper003_prereg_v1.0.md` is locked in design and open in numbers.
Eleven parameters are `PENDING`, and the calibration pilot is asked for four
things that unlock most of them:

    1. the capture verdict distribution - did the scene produce the relation
    2. engagement under real contact  -> the confirmatory n
    3. normal_alignment under real contact
    4. observation noise

This computes all four from the written cell records, and applies the sizing
rule exactly as preregistered rather than eyeballing the printed table:

> The confirmatory `n` is read off this table using the engagement rate observed
> in the **real-contact** calibration pilot, not the injected-coupling one.

There is no flag to relax it, and none to substitute an engagement figure by
hand. It reads what the pilot measured.

    python scripts/paper003_pilot_sizing.py results/paper003_capture_pilot/coupled
    python scripts/paper003_pilot_sizing.py results/paper003_capture_pilot/* --noise-from results/paper003_capture_pilot/static
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from math import comb
from pathlib import Path
from typing import Any

import numpy as np

#: Preregistered: one-sided paired sign test on discordant cells.
ALPHA = 0.05
TARGET_POWER = 0.90
#: Arm D's success *when it engages*. The CPU calibration puts this at 0.78; the
#: pilot's own conditional rate replaces it when there are enough engaged cells
#: to estimate one, which is the honest thing to size on.
D_CONDITIONAL_FALLBACK = 0.78


def sign_test_power(cells: int, engagement: float, d_conditional: float,
                    b_rate: float = 0.0, alpha: float = ALPHA) -> float:
    """Power of the preregistered test at this many cells.

    Arm B lands `b_rate` - 0.00 under capture, because the target travels far
    enough during the dispense that a zero-order aim cannot survive a carry.
    That is what makes the capture structure need so many fewer cells than the
    collision structure the v0.1 table was built on.
    """

    d_wins = engagement * d_conditional * (1.0 - b_rate)
    b_wins = b_rate * (1.0 - engagement * d_conditional)
    discordant = d_wins + b_wins
    if discordant <= 0.0:
        return 0.0
    share = d_wins / discordant

    total = 0.0
    for n in range(1, cells + 1):
        p_n = comb(cells, n) * discordant**n * (1.0 - discordant) ** (cells - n)
        critical = None
        for wins in range(n + 1):
            if sum(comb(n, k) for k in range(wins, n + 1)) / 2.0**n <= alpha:
                critical = wins
                break
        if critical is None:
            continue
        total += p_n * sum(
            comb(n, w) * share**w * (1.0 - share) ** (n - w)
            for w in range(critical, n + 1)
        )
    return total


def cells_for_power(engagement: float, d_conditional: float,
                    power: float = TARGET_POWER, cap: int = 2000) -> int | None:
    for cells in range(5, cap):
        if sign_test_power(cells, engagement, d_conditional) >= power:
            return cells
    return None


def load(paths: list[Path]) -> list[dict[str, Any]]:
    records = []
    for path in paths:
        for file in sorted(path.glob("cell_*.json")) if path.is_dir() else [path]:
            record = json.loads(file.read_text())
            record["_file"] = str(file)
            records.append(record)
    return records


def observation_noise(records: list[dict[str, Any]]) -> float | None:
    """Per-step motion of a target that should not be moving.

    Estimated from `static` cells, where the target is uncoupled by
    construction, so everything it appears to do is measurement. The gate's
    statistics were re-derived once already to stop depending on this being
    small, and it has never been measured.
    """

    steps = []
    for record in records:
        if record.get("condition") != "static":
            continue
        targets = np.asarray(
            [o["target"] for o in record.get("observations", [])], dtype=np.float64
        )
        if len(targets) > 1:
            steps.extend(np.linalg.norm(np.diff(targets, axis=0), axis=1).tolist())
    return float(np.median(steps)) if steps else None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--noise-from", type=Path, default=None,
                        help="a directory of `static` cells; defaults to whatever "
                             "static cells appear in `paths`")
    args = parser.parse_args()

    records = load(args.paths)
    usable = [r for r in records if not r.get("failed")]
    if not usable:
        raise SystemExit(f"no usable records in {[str(p) for p in args.paths]}")

    treatment = [r for r in usable if r.get("condition") == "coupled"]
    print(f"cells: {len(usable)} usable of {len(records)} "
          f"({len(treatment)} coupled)")

    # 1. Did the scene produce the relation.
    verdicts = Counter((r.get("capture") or {}).get("verdict", "?") for r in treatment)
    print("\n1. capture verdict (coupled cells)")
    for verdict, count in verdicts.most_common():
        print(f"     {verdict:10} {count}")
    captures = verdicts.get("capture", 0)
    if treatment and captures == 0:
        print("\n   NO CAPTURE IN ANY CELL. Nothing below is meaningful: the")
        print("   scene did not produce the relation the paper is about.")
        return

    # Arm scores may only be pooled across cells that are the same relation.
    scored = [r for r in treatment
              if (r.get("capture") or {}).get("verdict") == "capture"
              and r.get("resolved")]
    if not scored:
        print("\n   captures present but none resolved; no arm scores to size on")
        return

    # 2. Engagement -> n.
    engaged = np.array([bool(r["d_estimated"]) for r in scored])
    engagement = float(engaged.mean())
    landed = np.array([bool(r["resolved"]["D"]) for r in scored])
    b_rate = float(np.mean([bool(r["resolved"]["B"]) for r in scored]))
    conditional = (
        float(landed[engaged].mean()) if engaged.sum() >= 5 else D_CONDITIONAL_FALLBACK
    )
    source = "measured here" if engaged.sum() >= 5 else "CPU fallback 0.78"

    print(f"\n2. engagement       {engagement:.2f}  over {len(scored)} capture cells")
    print(f"   arm D | engaged  {conditional:.2f}  ({source})")
    print(f"   arm B            {b_rate:.2f}")
    required = cells_for_power(engagement, conditional)
    print(f"\n   confirmatory n = {required if required else '> 2000'}"
          f"   (one-sided paired sign test, alpha {ALPHA}, power {TARGET_POWER})")
    if engagement <= 0.0:
        print("   arm D never engaged: no n can rescue this. The gate is not")
        print("   firing under real contact, which is a finding, not a sample size.")

    # 3. normal_alignment.
    alignments = [r["normal_alignment"] for r in scored
                  if r.get("normal_alignment") is not None]
    print("\n3. normal_alignment "
          + (f"{np.median(alignments):.3f}  (median of {len(alignments)})"
             if alignments else "unavailable - no usable contact steps"))
    if alignments and float(np.median(alignments)) < 0.9:
        print("   BELOW 0.9. A contact pushing off-normal returns correct")
        print("   coefficients while arm D aims the wrong way, and that is")
        print("   invisible in every other statistic here.")

    # 4. Observation noise.
    noise_records = load([args.noise_from]) if args.noise_from else records
    noise = observation_noise(noise_records)
    print("\n4. observation noise "
          + (f"{1000 * noise:.2f} mm per step (median, static cells)"
             if noise is not None else "unavailable - no static cells supplied"))

    print("\nWrite these into docs/paper003/paper003_prereg_v1.0.md, each beside")
    print("the measurement it came from, before any confirmatory cell is run.")


if __name__ == "__main__":
    main()
