"""Read the achievable carry speed off a set of pilot cells, and derive the latency.

Applies the rule in `docs/paper003/paper003_derived_from_physics_v0.1.md`
exactly, and has no flag to relax any part of it:

    carry speed of a cell = block travel / riding steps, capture cells only
    achievable speed      = tenth percentile across seeds
    dispense_latency      = ceil(tolerance / achievable speed), no margin

Cells that are not captures are excluded and counted, not silently dropped: a
cell where the grasp failed says nothing about how fast a grasp can be carried.

    python3 scripts/paper003_carry_speed.py results/carry_speed
"""

from __future__ import annotations

import json
import math
import sys
from collections import Counter
from pathlib import Path

TOLERANCE = 0.020
PERCENTILE = 10


def percentile(values: list[float], pct: float) -> float:
    """Linear interpolation, so this needs no numpy on the pod."""
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * pct / 100.0
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return ordered[low]
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)

    speeds: list[tuple[int, float]] = []
    verdicts: Counter[str] = Counter()
    for argument in sys.argv[1:]:
        path = Path(argument)
        files = sorted(path.rglob("cell_*.json")) if path.is_dir() else [path]
        for file in files:
            record = json.loads(file.read_text())
            if record.get("failed") or record.get("early_termination"):
                verdicts["unusable"] += 1
                continue
            capture = record.get("capture") or {}
            verdicts[str(capture.get("verdict"))] += 1
            if capture.get("verdict") != "capture":
                continue
            run = capture.get("carriage_run") or 0
            travel = capture.get("travel_after_onset")
            if travel is None:
                targets = [o["target"] for o in record.get("observations", [])]
                travel = math.dist(targets[0], targets[-1]) if targets else 0.0
            if run >= 3 and travel > 0:
                speeds.append((record.get("seed", -1), travel / run))

    print(f"cells: {dict(verdicts)}")
    if not speeds:
        raise SystemExit("no capture cells with a usable carry; nothing to derive")

    values = [s for _, s in speeds]
    print(f"carry speed mm/step over {len(values)} capture cells:")
    print(f"   min {1000 * min(values):.2f}   p10 {1000 * percentile(values, 10):.2f}"
          f"   median {1000 * percentile(values, 50):.2f}   max {1000 * max(values):.2f}")

    if len(values) < 20:
        print(f"\n   WARNING: the rule asks for at least 20 seeds and this has "
              f"{len(values)}. A tenth percentile over fewer is reading noise.")

    achievable = percentile(values, PERCENTILE)
    latency = math.ceil(TOLERANCE / achievable)
    print()
    print(f"   achievable (p{PERCENTILE})  {1000 * achievable:.3f} mm/step")
    print(f"   tolerance             {1000 * TOLERANCE:.1f} mm")
    print(f"   dispense_latency    = ceil({1000 * TOLERANCE:.1f} / "
          f"{1000 * achievable:.3f}) = {latency}")
    print()
    print("   Write this into docs/paper003/paper003_prereg_v1.0.md with this")
    print("   measurement beside it. The commit window is one dispense-length")
    print("   either side of the arrival, so it changes with this number, and")
    print("   the SELF comparison must then be re-run on fresh seeds.")


if __name__ == "__main__":
    main()
