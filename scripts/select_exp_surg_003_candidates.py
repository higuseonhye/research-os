"""Lock EXP-SURG-003 candidates using static-control outcomes only."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--seeds", required=True)
    parser.add_argument("--required", type=int, required=True)
    parser.add_argument("--tol-m", type=float, required=True)
    parser.add_argument("--onset", type=int, required=True)
    parser.add_argument("--max-steps", type=int, required=True)
    parser.add_argument("--prefix-max-steps", type=int, required=True)
    parser.add_argument("--prefix-stable-steps", type=int, required=True)
    parser.add_argument("--paired-start-tol-m", type=float, required=True)
    parser.add_argument("--drift-speed", type=float, required=True)
    parser.add_argument("--drift-axis", required=True)
    parser.add_argument("--drift-duration", type=int, required=True)
    args = parser.parse_args()

    candidate_seeds = [
        int(value.strip()) for value in args.seeds.split(",") if value.strip()
    ]
    if args.required < 1:
        raise ValueError("required eligible seed count must be >= 1")
    if len(candidate_seeds) < args.required:
        raise ValueError("candidate seed count must cover the required eligible quota")

    eligible_seeds = []
    evaluations = []
    for seed in candidate_seeds:
        for policy in ("TRACK_DRIFTING", "TRACK_FROZEN"):
            treatment_path = (
                args.out_dir
                / f"seed_{seed}"
                / policy
                / "isaac_drift_results.json"
            )
            if treatment_path.exists():
                raise RuntimeError(
                    f"treatment result exists before selection lock: {treatment_path}"
                )
        result_path = (
            args.out_dir
            / f"seed_{seed}"
            / "STATIC_CONTROL"
            / "isaac_drift_results.json"
        )
        if not result_path.is_file():
            raise FileNotFoundError(f"missing static-control result for seed {seed}")
        result = json.loads(result_path.read_text(encoding="utf-8"))
        if result.get("seeds") != [seed]:
            raise ValueError(f"seed mismatch in {result_path}")
        if result.get("isolated_policy_process") != "STATIC_CONTROL":
            raise ValueError(f"policy mismatch in {result_path}")
        preconditions = result.get("preconditions", [])
        records = result.get("records", [])
        if len(preconditions) != 1:
            raise ValueError(f"expected one precondition in {result_path}")

        precondition = preconditions[0]
        reasons = []
        if not precondition["prefix_ready"]:
            reasons.append(precondition["prefix_failure_reason"] or "prefix_not_ready")
        if precondition["prefix_ready"] and len(records) != 1:
            reasons.append("missing_static_control_record")
        record = records[0] if len(records) == 1 else None
        if record is not None:
            if not record["successful_resolution"]:
                reasons.append("static_control_failure")
            if record["max_distance_m"] > args.tol_m:
                reasons.append("static_control_exceeded_tolerance")
            if record["forbidden_violation"]:
                reasons.append("static_control_forbidden_violation")
            if record["unexpected_env_reset"]:
                reasons.append("static_control_unexpected_reset")

        eligible = not reasons
        if eligible:
            eligible_seeds.append(seed)
        evaluations.append(
            {
                "seed": seed,
                "eligible": eligible,
                "reasons": reasons,
                "prefix_steps": precondition["prefix_steps"],
                "prefix_final_distance_m": precondition["prefix_final_distance_m"],
                "reset_state_fingerprint": precondition["reset_state_fingerprint"],
                "branch_state_fingerprint": precondition[
                    "branch_state_fingerprint"
                ],
                "static_final_distance_m": (
                    record["final_distance_m"] if record is not None else None
                ),
                "static_max_distance_m": (
                    record["max_distance_m"] if record is not None else None
                ),
            }
        )

    selected_seeds = eligible_seeds[: args.required]
    selection_quota_met = len(selected_seeds) == args.required
    commit_path = args.out_dir / "git_commit.txt"
    manifest = {
        "protocol": "static_control_first_fixed_order_quota_v0.2",
        "candidate_seeds": candidate_seeds,
        "required_eligible_seed_count": args.required,
        "eligible_seeds": eligible_seeds,
        "selected_seeds": selected_seeds,
        "selection_quota_met": selection_quota_met,
        "selection_locked_before_treatment": True,
        "eligibility_rate": len(eligible_seeds) / len(candidate_seeds),
        "eligibility_tolerance_m": args.tol_m,
        "locked_parameters": {
            "onset": args.onset,
            "max_steps": args.max_steps,
            "tol_m": args.tol_m,
            "prefix_max_steps": args.prefix_max_steps,
            "prefix_stable_steps": args.prefix_stable_steps,
            "paired_start_tol_m": args.paired_start_tol_m,
            "drift_speed_m_per_step": args.drift_speed,
            "drift_axis": args.drift_axis,
            "drift_duration_steps": args.drift_duration,
        },
        "analysis_contract": {
            "moving_min_success_rate": 0.8,
            "frozen_max_success_rate": 0.2,
            "require_positive_mean_final_distance_improvement": True,
            "max_forbidden_violations": 0,
        },
        "candidate_evaluations": evaluations,
        "git_commit": (
            commit_path.read_text(encoding="utf-8").strip()
            if commit_path.is_file()
            else None
        ),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    manifest_path = args.out_dir / "selection_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    if not selection_quota_met:
        print(
            f"[FAIL] only {len(eligible_seeds)} eligible seeds; required {args.required}",
            file=sys.stderr,
        )
        raise SystemExit(2)
    print(",".join(str(seed) for seed in selected_seeds))


if __name__ == "__main__":
    main()
