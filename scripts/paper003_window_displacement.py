"""Derive `dispense_latency` from how far the target actually moves in a window.

Applies the corrected rule in
`docs/paper003/paper003_derived_from_physics_v0.1.md`:

    dispense_latency = smallest L whose tenth-percentile L-step displacement
                       exceeds the placement tolerance

and nothing else. There is no speed in it, which is the point: a speed measured
over riding steps divides out the pauses, and a dispense window contains them.
That is how a latency of 7 was derived at which arm B still lands 0.58.

Only capture cells count, and only from the target's first motion - a window
before anything has happened measures the stillness, not the carry.

Plain stdlib, so it runs under the pod's own interpreter.

    python3 scripts/paper003_window_displacement.py results/carry8
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

TOLERANCE = 0.020
PERCENTILE = 10


def percentile(values: list[float], pct: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * pct / 100.0
    low, high = math.floor(position), math.ceil(position)
    if low == high:
        return ordered[low]
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def displacements(record: dict, horizon: int) -> list[float]:
    """Every `horizon`-step displacement from the target's first motion on."""

    targets = [o["target"] for o in record.get("observations", [])]
    if len(targets) <= horizon:
        return []
    steps = [math.dist(targets[i], targets[i + 1]) for i in range(len(targets) - 1)]
    largest = max(steps) if steps else 0.0
    if largest <= 0.0:
        return []
    floor = 0.25 * largest
    first = next((i for i, s in enumerate(steps) if s > floor), None)
    if first is None:
        return []
    return [
        math.dist(targets[i], targets[i + horizon])
        for i in range(first, len(targets) - horizon)
    ]


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)

    records = []
    for argument in sys.argv[1:]:
        path = Path(argument)
        files = sorted(path.glob("cell_*.json")) if path.is_dir() else [path]
        for file in files:
            record = json.loads(file.read_text())
            if record.get("failed") or record.get("early_termination"):
                continue
            if (record.get("capture") or {}).get("verdict") == "capture":
                records.append(record)

    print(f"capture cells: {len(records)}")
    if len(records) < 20:
        print(f"   WARNING: the rule's percentile wants at least 20 cells.")
    if not records:
        raise SystemExit("nothing to derive from")

    print(f"\n{'L':>3} {'cells':>6} {'p10 mm':>8} {'median mm':>10}  clears 20 mm")
    chosen = None
    for horizon in range(1, 25):
        pooled: list[float] = []
        for record in records:
            pooled.extend(displacements(record, horizon))
        if not pooled:
            continue
        p10 = percentile(pooled, PERCENTILE)
        clears = p10 > TOLERANCE
        if clears and chosen is None:
            chosen = horizon
        print(f"{horizon:3d} {len(pooled):6d} {1000 * p10:8.2f} "
              f"{1000 * percentile(pooled, 50):10.2f}  {'yes' if clears else 'no'}")
        if chosen is not None and horizon >= chosen + 2:
            break

    print()
    if chosen is None:
        print("   No horizon clears the tolerance. The scene cannot pose this task:")
        print("   the target never leaves tolerance during any window, so arm B is")
        print("   right by aiming where it already is, and no latency fixes that.")
    else:
        print(f"   dispense_latency = {chosen}")
        print("   Write it into paper003_prereg_v1.0.md beside this measurement.")


if __name__ == "__main__":
    main()
