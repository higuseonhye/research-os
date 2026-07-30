"""Aggregate isolated per-seed EXP-SURG-003 Isaac drift results."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import fmean
from typing import Any


POLICIES = ("STATIC_CONTROL", "TRACK_DRIFTING", "TRACK_FROZEN")


def _optional_max(values: list[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    return max(present) if present else None


def _policy_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    summary = {}
    for policy in POLICIES:
        rows = [row for row in records if row["policy"] == policy]
        summary[policy] = {
            "n": len(rows),
            "success_rate": fmean(row["successful_resolution"] for row in rows)
            if rows
            else None,
            "mean_final_distance_m": fmean(row["final_distance_m"] for row in rows)
            if rows
            else None,
            "mean_completion_steps": fmean(row["completion_steps"] for row in rows)
            if rows
            else None,
            "forbidden_violations": sum(row["forbidden_violation"] for row in rows),
            "unexpected_env_resets": sum(row["unexpected_env_reset"] for row in rows),
        }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--seeds", required=True)
    args = parser.parse_args()

    seeds = [int(value.strip()) for value in args.seeds.split(",") if value.strip()]
    if not seeds:
        raise ValueError("at least one seed is required")

    seed_results = []
    trajectories = []
    source_dirs = []
    for seed in seeds:
        seed_dir = args.out_dir / f"seed_{seed}"
        result_path = seed_dir / "isaac_drift_results.json"
        trajectory_path = seed_dir / "isaac_drift_trajectories.json"
        if not result_path.is_file() or not trajectory_path.is_file():
            raise FileNotFoundError(f"missing isolated result for seed {seed}: {seed_dir}")
        result = json.loads(result_path.read_text(encoding="utf-8"))
        if result.get("seeds") != [seed]:
            raise ValueError(f"isolated result seed mismatch in {result_path}")
        seed_results.append(result)
        trajectories.extend(json.loads(trajectory_path.read_text(encoding="utf-8")))
        source_dirs.append(str(seed_dir))

    preconditions = [
        row for result in seed_results for row in result.get("preconditions", [])
    ]
    records = [row for result in seed_results for row in result.get("records", [])]
    validities = [result["summary"]["validity"] for result in seed_results]
    ready_seeds = [row["seed"] for row in preconditions if row["prefix_ready"]]
    failed_seeds = [row["seed"] for row in preconditions if not row["prefix_ready"]]
    complete_branch_count = sum(row["complete_branch_count"] for row in validities)

    validity = {
        "requested_seed_count": len(seeds),
        "ready_seed_count": len(ready_seeds),
        "ready_seeds": ready_seeds,
        "failed_readiness_seeds": failed_seeds,
        "all_requested_seeds_ready": len(ready_seeds) == len(seeds),
        "complete_pair_count": complete_branch_count,
        "complete_branch_count": complete_branch_count,
        "max_branch_start_ee_gap_m": _optional_max(
            [row["max_branch_start_ee_gap_m"] for row in validities]
        ),
        "max_branch_start_command_gap_m": _optional_max(
            [row["max_branch_start_command_gap_m"] for row in validities]
        ),
        "paired_start_tolerance_m": validities[0]["paired_start_tolerance_m"],
        "paired_start_pass": bool(
            complete_branch_count == len(seeds)
            and all(row["paired_start_pass"] for row in validities)
        ),
        "max_branch_start_distance_m": _optional_max(
            [row["max_branch_start_distance_m"] for row in validities]
        ),
        "branch_start_distance_limit_m": validities[0][
            "branch_start_distance_limit_m"
        ],
        "all_branch_starts_ready": bool(
            complete_branch_count == len(seeds)
            and all(row["all_branch_starts_ready"] for row in validities)
        ),
        "all_drift_exposed": bool(
            complete_branch_count == len(seeds)
            and all(row["all_drift_exposed"] for row in validities)
        ),
        "no_unexpected_env_resets": all(
            row["no_unexpected_env_resets"] for row in validities
        ),
        "static_control_pass": bool(
            complete_branch_count == len(seeds)
            and all(row["static_control_pass"] for row in validities)
        ),
    }
    validity["valid_pilot"] = bool(
        validity["all_requested_seeds_ready"]
        and validity["paired_start_pass"]
        and validity["all_branch_starts_ready"]
        and validity["all_drift_exposed"]
        and validity["no_unexpected_env_resets"]
        and validity["static_control_pass"]
    )

    combined = {
        "experiment": seed_results[0]["experiment"],
        "mode": "isaac",
        "n_records": len(records),
        "seeds": seeds,
        "preconditions": preconditions,
        "summary": {
            "by_policy": _policy_summary(records),
            "validity": validity,
        },
        "records": records,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "target_dynamics": seed_results[0]["target_dynamics"],
        "fresh_environment_per_seed": True,
        "isolated_isaac_process_per_seed": True,
        "source_result_dirs": source_dirs,
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    result_path = args.out_dir / "isaac_drift_results.json"
    result_path.write_text(json.dumps(combined, indent=2), encoding="utf-8")
    (args.out_dir / "isaac_drift_trajectories.json").write_text(
        json.dumps(trajectories, indent=2), encoding="utf-8"
    )
    print(f"[INFO] aggregated {len(seeds)} isolated seeds into {result_path}")


if __name__ == "__main__":
    main()
