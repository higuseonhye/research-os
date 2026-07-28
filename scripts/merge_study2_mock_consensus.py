#!/usr/bin/env python3
"""Merge multi-seed mock records into consensus scores (Paper 002 v0.3)."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _spec_key(record: dict) -> tuple:
    spec = record["spec"]
    return (
        round(float(spec["shift_m"]), 4),
        int(spec["onset_step"]),
        round(float(spec.get("occlusion_gain", 0.0)), 3),
    )


def merge_consensus(seed_records: dict[int, dict[str, list[dict]]]) -> dict[str, list[dict]]:
    """Median mock_score per unique spec key, pooled across seeds."""
    buckets: dict[str, dict[tuple, list[dict]]] = {}

    for seed, raw in sorted(seed_records.items()):
        for dreamer, records in raw.items():
            buckets.setdefault(dreamer, {})
            for rec in records:
                key = _spec_key(rec)
                buckets[dreamer].setdefault(key, []).append({**rec, "_mock_seed": seed})

    merged: dict[str, list[dict]] = {}
    for dreamer, by_key in buckets.items():
        out: list[dict] = []
        for key, group in by_key.items():
            scores = [float(g.get("mock_score", 0.0)) for g in group]
            median_score = float(statistics.median(scores))
            # Representative record: highest mock_score appearance
            rep = max(group, key=lambda g: float(g.get("mock_score", 0.0)))
            spec = dict(rep["spec"])
            out.append(
                {
                    "goal": rep.get("goal", {}),
                    "spec": spec,
                    "continue_success": rep.get("continue_success"),
                    "replan_success": rep.get("replan_success"),
                    "mock_score": median_score,
                    "mock_score_median": median_score,
                    "mock_score_n_seeds": len(scores),
                    "informative": bool(rep.get("informative", False)),
                    "consensus_seeds": sorted({g["_mock_seed"] for g in group}),
                }
            )
        merged[dreamer] = out
    return merged


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge Study2 mock seeds → consensus records")
    parser.add_argument(
        "--results-dir",
        type=Path,
        required=True,
        help="e.g. experiments/.../results/mock_confirmatory_v0.1",
    )
    parser.add_argument("--seeds", type=str, default="42,43,44,45,46")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--planner", type=str, default="rule", choices=("rule", "llm"))
    args = parser.parse_args()

    seeds = [int(s.strip()) for s in args.seeds.split(",") if s.strip()]
    seed_records: dict[int, dict[str, list[dict]]] = {}
    for seed in seeds:
        path = args.results_dir / f"records_seed{seed}.json"
        if not path.exists():
            parser.error(f"Missing {path}")
        seed_records[seed] = json.loads(path.read_text(encoding="utf-8"))

    merged = merge_consensus(seed_records)
    payload = {
        "planner": args.planner,
        "consensus_seeds": seeds,
        "aggregation": "median_mock_score",
        "spec_key": "(shift_m_4dp, onset_step, occlusion_gain_3dp)",
        "dreamers": merged,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    for dreamer, recs in merged.items():
        print(f"  [{dreamer}] unique specs={len(recs)}")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
