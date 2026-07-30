"""Aggregate isolated per-seed EXP-SURG-003 Isaac drift results."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from math import dist
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


def _trajectory_gap(
    left: list[dict[str, Any]], right: list[dict[str, Any]], key: str
) -> tuple[float | None, int]:
    left_by_t = {row["t"]: row for row in left}
    right_by_t = {row["t"]: row for row in right}
    shared_steps = sorted(set(left_by_t) & set(right_by_t))
    if not shared_steps:
        return None, 0
    return (
        max(dist(left_by_t[t][key], right_by_t[t][key]) for t in shared_steps),
        len(shared_steps),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--seeds", required=True)
    parser.add_argument("--selection-manifest", type=Path)
    args = parser.parse_args()

    seeds = [int(value.strip()) for value in args.seeds.split(",") if value.strip()]
    if not seeds:
        raise ValueError("at least one seed is required")

    arm_results = []
    trajectories = []
    source_dirs = []
    preconditions = []
    records = []
    prefix_match_by_seed = {}
    for seed in seeds:
        seed_preconditions = {}
        for policy in POLICIES:
            arm_dir = args.out_dir / f"seed_{seed}" / policy
            result_path = arm_dir / "isaac_drift_results.json"
            trajectory_path = arm_dir / "isaac_drift_trajectories.json"
            if not result_path.is_file() or not trajectory_path.is_file():
                raise FileNotFoundError(
                    f"missing isolated result for seed {seed}, policy {policy}: {arm_dir}"
                )
            result = json.loads(result_path.read_text(encoding="utf-8"))
            if result.get("seeds") != [seed]:
                raise ValueError(f"isolated result seed mismatch in {result_path}")
            if result.get("isolated_policy_process") != policy:
                raise ValueError(f"isolated policy mismatch in {result_path}")
            if len(result.get("preconditions", [])) != 1:
                raise ValueError(f"expected one precondition in {result_path}")
            arm_records = result.get("records", [])
            if arm_records and (
                len(arm_records) != 1 or arm_records[0]["policy"] != policy
            ):
                raise ValueError(f"unexpected policy records in {result_path}")
            seed_preconditions[policy] = result["preconditions"][0]
            arm_results.append(result)
            records.extend(arm_records)
            trajectories.extend(
                json.loads(trajectory_path.read_text(encoding="utf-8"))
            )
            source_dirs.append(str(arm_dir))

        reset_fingerprints = {
            policy: row["reset_state_fingerprint"]
            for policy, row in seed_preconditions.items()
        }
        branch_fingerprints = {
            policy: row["branch_state_fingerprint"]
            for policy, row in seed_preconditions.items()
        }
        prefix_steps = {
            policy: row["prefix_steps"] for policy, row in seed_preconditions.items()
        }
        prefix_distances = {
            policy: row["prefix_final_distance_m"]
            for policy, row in seed_preconditions.items()
        }
        ready_values = {
            policy: row["prefix_ready"] for policy, row in seed_preconditions.items()
        }
        distance_values = [
            value for value in prefix_distances.values() if value is not None
        ]
        prefix_distance_match = bool(
            len(distance_values) == len(POLICIES)
            and max(distance_values) - min(distance_values) <= 1e-6
        )
        prefix_match = bool(
            len(set(reset_fingerprints.values())) == 1
            and len(set(prefix_steps.values())) == 1
            and len(set(ready_values.values())) == 1
            and prefix_distance_match
        )
        prefix_match_by_seed[seed] = prefix_match
        canonical = dict(seed_preconditions[POLICIES[0]])
        if not prefix_match:
            canonical["prefix_ready"] = False
            canonical["prefix_failure_reason"] = "cross_policy_prefix_mismatch"
        canonical.update(
            {
                "cross_policy_prefix_match": prefix_match,
                "policy_reset_state_fingerprints": reset_fingerprints,
                "policy_branch_state_fingerprints": branch_fingerprints,
                "branch_state_fingerprint_exact_match": len(
                    set(branch_fingerprints.values())
                )
                == 1,
                "policy_prefix_steps": prefix_steps,
                "policy_prefix_final_distance_m": prefix_distances,
                "policy_readiness": ready_values,
            }
        )
        preconditions.append(canonical)

    arm_validities = [result["summary"]["validity"] for result in arm_results]
    paired_start_tolerance = arm_validities[0]["paired_start_tolerance_m"]
    branch_start_distance_limit = arm_validities[0]["branch_start_distance_limit_m"]
    static_tolerance = branch_start_distance_limit - paired_start_tolerance
    ready_seeds = [row["seed"] for row in preconditions if row["prefix_ready"]]
    failed_seeds = [row["seed"] for row in preconditions if not row["prefix_ready"]]
    records_by_seed_policy = {
        (row["seed"], row["policy"]): row for row in records
    }
    trajectories_by_seed_policy = {
        (row["seed"], row["policy"]): row["trajectory"] for row in trajectories
    }
    complete_seeds = [
        seed
        for seed in seeds
        if all((seed, policy) in records_by_seed_policy for policy in POLICIES)
    ]
    complete_branch_count = len(complete_seeds)

    ee_start_gaps = []
    command_start_gaps = []
    isolation_ee_gaps = []
    isolation_action_gaps = []
    isolation_overlap_steps = {}
    isolation_expected_steps = {}
    for seed in complete_seeds:
        drifting = records_by_seed_policy[(seed, "TRACK_DRIFTING")]
        for policy in ("STATIC_CONTROL", "TRACK_FROZEN"):
            other = records_by_seed_policy[(seed, policy)]
            ee_start_gaps.append(
                dist(drifting["branch_start_ee"], other["branch_start_ee"])
            )
            command_start_gaps.append(
                dist(drifting["branch_start_command"], other["branch_start_command"])
            )
        static_trace = trajectories_by_seed_policy[(seed, "STATIC_CONTROL")]
        frozen_trace = trajectories_by_seed_policy[(seed, "TRACK_FROZEN")]
        ee_gap, overlap = _trajectory_gap(static_trace, frozen_trace, "ee")
        action_gap, _ = _trajectory_gap(static_trace, frozen_trace, "action")
        isolation_overlap_steps[str(seed)] = overlap
        isolation_expected_steps[str(seed)] = records_by_seed_policy[
            (seed, "STATIC_CONTROL")
        ]["branch_horizon_steps"]
        isolation_ee_gaps.append(ee_gap)
        isolation_action_gaps.append(action_gap)

    max_ee_start_gap = _optional_max(ee_start_gaps)
    max_command_start_gap = _optional_max(command_start_gaps)
    max_isolation_ee_gap = _optional_max(isolation_ee_gaps)
    max_isolation_action_gap = _optional_max(isolation_action_gaps)
    branch_start_distances = [row["branch_start_distance_m"] for row in records]
    max_branch_start_distance = _optional_max(branch_start_distances)
    static_rows = [row for row in records if row["policy"] == "STATIC_CONTROL"]
    static_control_pass = bool(
        len(static_rows) == len(seeds)
        and all(
            row["successful_resolution"] and row["max_distance_m"] <= static_tolerance
            for row in static_rows
        )
    )
    evaluation_isolation_pass = bool(
        complete_branch_count == len(seeds)
        and max_isolation_ee_gap is not None
        and max_isolation_action_gap is not None
        and max_isolation_ee_gap <= paired_start_tolerance
        and max_isolation_action_gap <= paired_start_tolerance
        and isolation_overlap_steps == isolation_expected_steps
    )

    validity = {
        "requested_seed_count": len(seeds),
        "ready_seed_count": len(ready_seeds),
        "ready_seeds": ready_seeds,
        "failed_readiness_seeds": failed_seeds,
        "all_requested_seeds_ready": len(ready_seeds) == len(seeds),
        "complete_pair_count": complete_branch_count,
        "complete_branch_count": complete_branch_count,
        "cross_policy_prefix_pass": all(prefix_match_by_seed.values()),
        "max_branch_start_ee_gap_m": max_ee_start_gap,
        "max_branch_start_command_gap_m": max_command_start_gap,
        "paired_start_tolerance_m": paired_start_tolerance,
        "paired_start_pass": bool(
            complete_branch_count == len(seeds)
            and max_ee_start_gap is not None
            and max_command_start_gap is not None
            and max_ee_start_gap <= paired_start_tolerance
            and max_command_start_gap <= 1e-6
        ),
        "max_branch_start_distance_m": max_branch_start_distance,
        "branch_start_distance_limit_m": branch_start_distance_limit,
        "all_branch_starts_ready": bool(
            len(branch_start_distances) == len(POLICIES) * len(seeds)
            and max_branch_start_distance is not None
            and max_branch_start_distance <= branch_start_distance_limit
        ),
        "all_drift_exposed": bool(
            len(records) == len(POLICIES) * len(seeds)
            and all(
                row["completion_steps"] >= row["minimum_completion_steps"]
                for row in records
            )
        ),
        "no_unexpected_env_resets": all(
            not row["unexpected_env_reset"] for row in records
        ),
        "static_control_pass": static_control_pass,
        "max_static_frozen_ee_gap_m": max_isolation_ee_gap,
        "max_static_frozen_action_gap": max_isolation_action_gap,
        "evaluation_isolation_tolerance": paired_start_tolerance,
        "evaluation_isolation_overlap_steps": isolation_overlap_steps,
        "evaluation_isolation_expected_steps": isolation_expected_steps,
        "evaluation_isolation_pass": evaluation_isolation_pass,
    }
    validity["valid_pilot"] = bool(
        validity["all_requested_seeds_ready"]
        and validity["cross_policy_prefix_pass"]
        and validity["paired_start_pass"]
        and validity["all_branch_starts_ready"]
        and validity["all_drift_exposed"]
        and validity["no_unexpected_env_resets"]
        and validity["static_control_pass"]
        and validity["evaluation_isolation_pass"]
    )

    selection = None
    if args.selection_manifest is not None:
        selection = json.loads(args.selection_manifest.read_text(encoding="utf-8"))
        if selection["selected_seeds"] != seeds:
            raise ValueError("selection manifest does not match aggregated seed order")
        validity["selection_protocol"] = selection["protocol"]
        validity["candidate_seed_count"] = len(selection["candidate_seeds"])
        validity["eligible_seed_count"] = len(selection["eligible_seeds"])
        validity["required_eligible_seed_count"] = selection[
            "required_eligible_seed_count"
        ]
        validity["selection_quota_met"] = selection["selection_quota_met"]
        validity["selection_locked_before_treatment"] = selection[
            "selection_locked_before_treatment"
        ]
        validity["valid_pilot"] = bool(
            validity["valid_pilot"]
            and validity["selection_quota_met"]
            and validity["selection_locked_before_treatment"]
        )

    by_policy = _policy_summary(records)
    effect = None
    confirmatory_pass = None
    if selection is not None:
        moving = by_policy["TRACK_DRIFTING"]
        frozen = by_policy["TRACK_FROZEN"]
        contract = selection["analysis_contract"]
        moving_by_seed = {
            row["seed"]: row for row in records if row["policy"] == "TRACK_DRIFTING"
        }
        frozen_by_seed = {
            row["seed"]: row for row in records if row["policy"] == "TRACK_FROZEN"
        }
        paired_improvements = [
            frozen_by_seed[seed]["final_distance_m"]
            - moving_by_seed[seed]["final_distance_m"]
            for seed in seeds
        ]
        effect = {
            "mean_final_distance_improvement_m": fmean(paired_improvements),
            "paired_final_distance_improvements_m": paired_improvements,
            "moving_better_seed_count": sum(value > 0 for value in paired_improvements),
            "moving_better_seed_rate": fmean(value > 0 for value in paired_improvements),
            "success_rate_difference": moving["success_rate"]
            - frozen["success_rate"],
            "gates": {
                "moving_success_rate_pass": moving["success_rate"]
                >= contract["moving_min_success_rate"],
                "frozen_success_rate_pass": frozen["success_rate"]
                <= contract["frozen_max_success_rate"],
                "mean_final_distance_improvement_pass": fmean(paired_improvements)
                > 0,
                "forbidden_violations_pass": (
                    moving["forbidden_violations"]
                    + frozen["forbidden_violations"]
                    <= contract["max_forbidden_violations"]
                ),
            },
        }
        effect["effect_gate_pass"] = all(effect["gates"].values())
        confirmatory_pass = bool(
            validity["valid_pilot"] and effect["effect_gate_pass"]
        )

    combined = {
        "experiment": arm_results[0]["experiment"],
        "mode": "isaac",
        "n_records": len(records),
        "seeds": seeds,
        "preconditions": preconditions,
        "summary": {
            "by_policy": by_policy,
            "validity": validity,
        },
        "records": records,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "target_dynamics": arm_results[0]["target_dynamics"],
        "fresh_environment_per_seed": True,
        "isolated_isaac_process_per_seed": True,
        "isolated_isaac_process_per_policy": True,
        "source_result_dirs": source_dirs,
    }
    if selection is not None:
        combined["selection"] = selection
        combined["effect"] = effect
        combined["confirmatory_pass"] = confirmatory_pass
    args.out_dir.mkdir(parents=True, exist_ok=True)
    result_path = args.out_dir / "isaac_drift_results.json"
    result_path.write_text(json.dumps(combined, indent=2), encoding="utf-8")
    (args.out_dir / "isaac_drift_trajectories.json").write_text(
        json.dumps(trajectories, indent=2), encoding="utf-8"
    )
    print(f"[INFO] aggregated {len(seeds)} isolated seeds into {result_path}")


if __name__ == "__main__":
    main()
