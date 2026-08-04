"""Score the arms under each relation, in the commit window, on CPU.

The measurement open item 3 of the Paper 003 README asks for: the relation and
the cell loop now meet, so put every arm through them and read the result.

CPU only, injected coupling. That makes this a calibration device and not
confirmatory evidence - `normal_alignment` is 1.0 by construction and there is
no contact jitter - but the loop is the same code the Isaac runner executes, so
what it says about which arms can *act* transfers.

    python scripts/paper003_capture_arms.py --seeds 40
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict

import numpy as np

from wm_expansion.cell import CellSpec, run_cell
from wm_expansion.commitment_episode import EpisodeSpec
from wm_expansion.encounter import EncounterSpec

TARGET = np.array([0.20, 0.0, 0.40])
ARMS = ("B", "C", "D")

#: label, condition, coupling, schedule, bodies
CASES = (
    ("capture / burst / 1 body", "coupled", "capture", "burst", 1),
    ("capture / probe / 1 body", "coupled", "capture", "probe", 1),
    ("capture / probe / 2 bodies", "coupled", "capture", "probe", 2),
    ("collision / probe / 1 body", "coupled", "collision", "probe", 1),
    ("collision / probe / 2 bodies", "coupled", "collision", "probe", 2),
    ("slide", "slide", "collision", "probe", 1),
    ("drift", "drift", "collision", "probe", 1),
    ("static", "static", "collision", "probe", 1),
    ("noise", "noise", "collision", "probe", 1),
)


def sweep(condition: str, coupling: str, schedule: str, bodies: int, seeds: int) -> list[dict]:
    records = []
    for seed in range(300, 300 + seeds):
        record = run_cell(
            TARGET,
            EpisodeSpec(),
            EncounterSpec(bodies=bodies, schedule=schedule),
            CellSpec(condition=condition, seed=seed, coupling=coupling),
            drive=lambda target: False,
        )
        if record["resolved"] is not None:
            records.append(record)
    return records


def summarise(records: list[dict]) -> dict:
    offsets = [r["commit_offset"] for r in records if r["commit_offset"] is not None]
    return {
        "n": len(records),
        **{arm: float(np.mean([r["resolved"][arm] for r in records])) for arm in ARMS},
        # The number that decides whether the rest of the row means anything: an
        # arm that never estimated is arm B under another name.
        "d_estimated": float(np.mean([r["d_estimated"] for r in records])),
        "in_window": float(np.mean([r["committed_in_window"] for r in records])),
        "median_offset": float(np.median(offsets)) if offsets else None,
    }


def by_offset(records: list[dict]) -> dict[int, dict]:
    buckets: dict[int, list[dict]] = defaultdict(list)
    for record in records:
        if record["commit_offset"] is not None:
            buckets[record["commit_offset"]].append(record)
    return {
        offset: {
            "n": len(rows),
            **{arm: float(np.mean([r["resolved"][arm] for r in rows])) for arm in ARMS},
        }
        for offset, rows in sorted(buckets.items())
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=40)
    parser.add_argument("--json", type=str, default=None)
    args = parser.parse_args()

    out = {}
    print(f"{'case':<30} {'B':>5} {'C':>5} {'D':>5}  {'D-est':>6} {'window':>7} {'offset':>7}  n")
    for label, condition, coupling, schedule, bodies in CASES:
        records = sweep(condition, coupling, schedule, bodies, args.seeds)
        row = summarise(records)
        out[label] = {"summary": row, "by_offset": by_offset(records)}
        offset = "-" if row["median_offset"] is None else f"{row['median_offset']:+.0f}"
        print(
            f"{label:<30} {row['B']:5.2f} {row['C']:5.2f} {row['D']:5.2f}  "
            f"{row['d_estimated']:6.2f} {row['in_window']:7.2f} {offset:>7}  {row['n']}"
        )

    if args.json:
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump(out, handle, indent=2)


if __name__ == "__main__":
    main()
