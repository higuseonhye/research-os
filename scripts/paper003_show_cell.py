"""Print what a pilot cell actually did, in the order that decides anything.

Exists because reading a cell was taking a dozen lines of inline python pasted
into a terminal, and a mangled paste is a wasted GPU run. Plain stdlib, no
imports from the project, so it runs under any interpreter on the pod.

    python3 scripts/paper003_show_cell.py results/paper003_capture_pilot/coupled
    python3 scripts/paper003_show_cell.py results/.../cell_coupled_seed300.json
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path


def mm(value: float | None) -> str:
    return "-" if value is None else f"{1000 * value:.2f} mm"


def show(path: Path) -> None:
    record = json.loads(path.read_text())
    print(f"== {path.name}")
    if record.get("failed"):
        print(f"   FAILED: {record['failed']}")
        return

    observations = record.get("observations") or []
    targets = [o["target"] for o in observations]
    bodies = [o["references"] for o in observations]
    steps = [math.dist(targets[i], targets[i + 1]) for i in range(len(targets) - 1)]
    separations = [
        min(math.dist(o["target"], b) for b in o["references"]) for o in observations
    ]
    moved = next((i for i, s in enumerate(steps) if s > 0.0008), None)

    # 1. Did the environment let the cell finish.
    print(f"   valid {record.get('valid')}   early_termination "
          f"{record.get('early_termination')}   steps {len(observations)}")
    if record.get("early_termination"):
        print("   -> the environment ended this cell. Nothing below measures contact.")
        return

    # 2. Did the arm get where it was told.
    print(f"   ee_error median {mm(record.get('ee_error_median'))}   "
          f"max {mm(record.get('ee_error_max'))}")
    preroll = record.get("preroll") or {}
    if preroll:
        print(f"   preroll steps {preroll.get('steps')}  converged "
              f"{preroll.get('converged')}  block_disturbed "
              f"{mm(preroll.get('block_disturbed'))}")

    # 3. Did a capture happen.
    grasp = record.get("grasp") or {}
    print(f"   grasp closed_at step {grasp.get('closed_at')} at "
          f"{mm(grasp.get('closed_at_separation'))}   closest seen "
          f"{mm(grasp.get('closest_seen'))}")
    print(f"   closest EE-target {mm(min(separations) if separations else None)}"
          f"   block travelled {mm(math.dist(targets[0], targets[-1]) if targets else None)}"
          f"   first motion step {moved}")
    verdict = record.get("capture")
    if verdict is None:
        # Only the Isaac adapter computes one. Saying NONE here would read as
        # "the scene produced nothing", which is a different claim entirely.
        print("   VERDICT not computed - no `capture` key, so this is a CPU cell")
    else:
        print(f"   VERDICT {str(verdict.get('verdict')).upper()}  "
              f"({verdict.get('reason')})")
        print(f"   carriage agreement {verdict.get('carriage_agreement')}   "
              f"run {verdict.get('carriage_run')}")

    # 4. Where the commit landed, and whether any arm could act.
    print(f"   arrivals {record.get('arrivals')}   committed_at "
          f"{record.get('committed_at')}   offset {record.get('commit_offset')}"
          f"   in_window {record.get('committed_in_window')}")
    print(f"   gate_fire_rate {record.get('gate_fire_rate')}   d_estimated "
          f"{record.get('d_estimated')}   self_estimated {record.get('self_estimated')}")
    if record.get("resolved"):
        print(f"   resolved {record['resolved']}")
    print(f"   normal_alignment {record.get('normal_alignment')}")


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for argument in sys.argv[1:]:
        path = Path(argument)
        files = sorted(path.glob("cell_*.json")) if path.is_dir() else [path]
        if not files:
            print(f"no cell_*.json under {path}")
        for file in files:
            show(file)


if __name__ == "__main__":
    main()
