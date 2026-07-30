"""Aggregate and analyze isolated Isaac runs for EXP-SURG-003 model order."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from math import dist, sqrt
from pathlib import Path
from statistics import fmean
from typing import Any

import numpy as np

from wm_expansion.target_dynamics import (
    GateThresholds,
    evaluate_structure_gate,
    fit_smoothing_parameter,
    synthetic_gate_controls,
)


EP2_ARMS = (
    "A_ZERO_ORDER_FROZEN",
    "B_L1_ZERO_ORDER",
    "C_L3_CONSTANT_VELOCITY",
    "D_ORACLE_VELOCITY",
)
RETENTION_ARMS = ("B_L1_ZERO_ORDER", "C_L3_CONSTANT_VELOCITY")
EXECUTION_ISOLATION = "fresh_isaac_process_per_seed_arm_condition"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_arm(
    arm_dir: Path, expected_policy: str
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    result_path = arm_dir / "isaac_drift_results.json"
    trajectory_path = arm_dir / "isaac_drift_trajectories.json"
    if not result_path.is_file() or not trajectory_path.is_file():
        raise FileNotFoundError(f"missing isolated arm output: {arm_dir}")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    records = result.get("records", [])
    trajectories = json.loads(trajectory_path.read_text(encoding="utf-8"))
    if not records or len(records) != len(trajectories):
        raise ValueError(f"record/trajectory count mismatch in {arm_dir}")
    if any(row["policy"] != expected_policy for row in records + trajectories):
        raise ValueError(f"policy mismatch in {arm_dir}")
    return result, trajectories


def _arm_summary(records: list[dict[str, Any]], arms: tuple[str, ...]) -> dict[str, Any]:
    output = {}
    for arm in arms:
        rows = [row for row in records if row["policy"] == arm]
        errors = [row["mean_prediction_error_horizon_m"] for row in rows]
        output[arm] = {
            "n": len(rows),
            "success_rate": fmean(row["successful_resolution"] for row in rows) if rows else None,
            "mean_prediction_error_horizon_m": fmean(errors) if errors else None,
            "mean_final_distance_m": fmean(row["final_distance_m"] for row in rows) if rows else None,
            "mean_completion_steps": fmean(row["completion_steps"] for row in rows) if rows else None,
            "forbidden_violations": sum(row["forbidden_violation"] for row in rows),
            "unexpected_env_resets": sum(row["unexpected_env_reset"] for row in rows),
        }
    return output


def _crossed_bootstrap_ci(
    values: dict[tuple[int, str], float],
    seeds: list[int],
    conditions: list[str],
    rng: np.random.Generator,
    repetitions: int = 10000,
) -> list[float]:
    draws = np.empty(repetitions, dtype=np.float64)
    seed_array = np.asarray(seeds)
    condition_array = np.asarray(conditions)
    for index in range(repetitions):
        sampled_seeds = rng.choice(seed_array, size=len(seeds), replace=True)
        sampled_conditions = rng.choice(
            condition_array, size=len(conditions), replace=True
        )
        draws[index] = np.mean(
            [values[(int(seed), str(condition))] for seed in sampled_seeds for condition in sampled_conditions]
        )
    return [float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))]


def _paired_seed_bootstrap_ci(
    values: dict[int, float], rng: np.random.Generator, repetitions: int = 10000
) -> list[float]:
    seeds = np.asarray(sorted(values))
    draws = np.empty(repetitions, dtype=np.float64)
    for index in range(repetitions):
        sampled = rng.choice(seeds, size=len(seeds), replace=True)
        draws[index] = np.mean([values[int(seed)] for seed in sampled])
    return [float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))]


def _wilson_interval(successes: int, total: int) -> list[float]:
    if total == 0:
        return [float("nan"), float("nan")]
    z = 1.959963984540054
    p = successes / total
    denominator = 1.0 + z * z / total
    center = (p + z * z / (2.0 * total)) / denominator
    half = z * sqrt((p * (1.0 - p) + z * z / (4.0 * total)) / total) / denominator
    return [max(0.0, center - half), min(1.0, center + half)]


def _gate_thresholds(config: dict[str, Any]) -> GateThresholds:
    gate = config["gate"]
    return GateThresholds(
        min_deltas=int(gate["min_deltas"]),
        speed_floor_m_per_step=float(gate["speed_floor_m_per_step"]),
        min_active_fraction=float(gate["min_active_fraction"]),
        min_directional_consistency=float(gate["min_directional_consistency"]),
        min_cv_error_improvement=float(gate["min_cv_error_improvement"]),
    )


def _ep1_diagnostics(config: dict[str, Any], thresholds: GateThresholds) -> dict[str, Any]:
    ep1 = config["ep1_adaptation"]
    horizon = int(config["shared"]["prediction_horizon_steps"])
    steps = int(ep1["steps"])
    drift = np.asarray(ep1["drift_vector_m_per_step"], dtype=np.float64)
    positions = np.arange(steps + horizon + 1)[:, None] * drift[None, :]
    candidates = [float(value) for value in ep1["parameter_candidates"]]
    held_out_start = int(ep1["held_out_start_step"])
    l1 = fit_smoothing_parameter(
        positions,
        candidates=candidates,
        horizon=horizon,
        held_out_start=held_out_start,
        model_order=0,
    )
    l3 = fit_smoothing_parameter(
        positions,
        candidates=candidates,
        horizon=horizon,
        held_out_start=held_out_start,
        model_order=1,
        gate_thresholds=thresholds,
        gate_window=int(config["gate"]["window"]),
    )
    gate = evaluate_structure_gate(positions[:steps], thresholds)
    return {
        "shared_transition_count": steps - 1,
        "repair_attempt_count": len(candidates),
        "l1_zero_order_repair": l1,
        "l3_constant_velocity_fit": l3,
        "structural_gate": gate.to_dict(),
        "l3_vs_l1_prediction_error_improvement_m": float(
            l1["selected_mean_prediction_error_m"]
            - l3["selected_mean_prediction_error_m"]
        ),
    }


def _h4_controls(
    config: dict[str, Any], selected_seeds: list[int], thresholds: GateThresholds
) -> dict[str, Any]:
    counts: dict[str, list[bool]] = {}
    noise_sigma = float(config["gate"]["negative_control_noise_sigma_m"])
    for seed in selected_seeds:
        for condition in config["conditions"]:
            histories = synthetic_gate_controls(
                seed=seed * 1000 + int(str(condition["id"])[1:]),
                steps=max(40, thresholds.min_deltas + 4),
                drift_step=condition["drift_vector_m_per_step"],
                noise_sigma_m=noise_sigma,
            )
            for name, history in histories.items():
                counts.setdefault(name, []).append(
                    evaluate_structure_gate(history, thresholds).fired
                )
    summary = {}
    for name, values in counts.items():
        successes = sum(values)
        summary[name] = {
            "n": len(values),
            "gate_fired_count": successes,
            "gate_fire_rate": successes / len(values),
            "wilson_95_ci": _wilson_interval(successes, len(values)),
        }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    if config.get("execution_isolation") != EXECUTION_ISOLATION:
        raise ValueError("aggregation requires process-isolated condition outputs")
    selection_path = args.out_dir / "selection_manifest.json"
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    if selection["config_sha256"] != _sha256(args.config):
        raise ValueError("selection manifest config checksum mismatch")
    selected_seeds = [int(seed) for seed in selection["selected_seeds"]]
    condition_ids = [str(row["id"]) for row in config["conditions"]]

    records = []
    trajectories = []
    preconditions: dict[tuple[int, str], dict[str, Any]] = {}
    for seed in selected_seeds:
        for arm in EP2_ARMS:
            arm_dir = args.out_dir / "ep2" / f"seed_{seed}" / arm
            for condition_id in condition_ids:
                condition_dir = arm_dir / f"condition_{condition_id}"
                result, condition_trajectories = _load_arm(condition_dir, arm)
                condition_records = result["records"]
                condition_preconditions = result["preconditions"]
                if len(condition_records) != 1 or len(condition_preconditions) != 1:
                    raise ValueError(
                        f"expected one isolated condition record in {condition_dir}"
                    )
                record = condition_records[0]
                trajectory = condition_trajectories[0]
                precondition = condition_preconditions[0]
                if any(
                    row["condition_id"] != condition_id
                    for row in (record, trajectory, precondition)
                ):
                    raise ValueError(f"condition ID mismatch in {condition_dir}")
                records.append(record)
                trajectories.append(trajectory)
                preconditions[(seed, f"{condition_id}:{arm}")] = precondition

    retention_records = []
    retention_trajectories = []
    for seed in selected_seeds:
        for arm in RETENTION_ARMS:
            arm_dir = args.out_dir / "retention" / f"seed_{seed}" / arm
            result, arm_trajectories = _load_arm(arm_dir, arm)
            if len(result["records"]) != 1:
                raise ValueError(f"expected one retention record in {arm_dir}")
            retention_records.append(result["records"][0])
            retention_trajectories.append(arm_trajectories[0])

    expected_ep2 = len(selected_seeds) * len(condition_ids) * len(EP2_ARMS)
    expected_retention = len(selected_seeds) * len(RETENTION_ARMS)
    start_ee_gaps = []
    start_command_gaps = []
    prefix_match = []
    for condition_id in condition_ids:
        for seed in selected_seeds:
            pair = {
                row["policy"]: row
                for row in records
                if row["seed"] == seed and row["condition_id"] == condition_id
            }
            baseline = pair["B_L1_ZERO_ORDER"]
            for arm in EP2_ARMS:
                start_ee_gaps.append(dist(baseline["branch_start_ee"], pair[arm]["branch_start_ee"]))
                start_command_gaps.append(
                    dist(baseline["branch_start_command"], pair[arm]["branch_start_command"])
                )
            rows = [preconditions[(seed, f"{condition_id}:{arm}")] for arm in EP2_ARMS]
            prefix_match.append(
                len({row["reset_state_fingerprint"] for row in rows}) == 1
                and len({row["prefix_steps"] for row in rows}) == 1
                and len({row["prefix_ready"] for row in rows}) == 1
            )

    tolerance = float(config["shared"]["paired_start_tolerance_m"])
    branch_start_distances = [row["branch_start_distance_m"] for row in records]
    branch_start_limit = (
        float(config["shared"]["success_tolerance_m"]) + tolerance
    )
    validity = {
        "selection_quota_met": bool(selection["selection_quota_met"]),
        "selection_locked_before_treatment": bool(selection["selection_locked_before_treatment"]),
        "expected_ep2_record_count": expected_ep2,
        "actual_ep2_record_count": len(records),
        "complete_ep2_grid": len(records) == expected_ep2,
        "expected_retention_record_count": expected_retention,
        "actual_retention_record_count": len(retention_records),
        "complete_retention_grid": len(retention_records) == expected_retention,
        "cross_policy_prefix_pass": all(prefix_match),
        "all_prefixes_ready": all(row["prefix_ready"] for row in preconditions.values()),
        "max_branch_start_ee_gap_m": max(start_ee_gaps),
        "max_branch_start_command_gap_m": max(start_command_gaps),
        "paired_start_tolerance_m": tolerance,
        "paired_start_pass": max(start_ee_gaps) <= tolerance and max(start_command_gaps) <= 1e-6,
        "max_branch_start_distance_m": max(branch_start_distances),
        "branch_start_distance_limit_m": branch_start_limit,
        "all_branch_starts_ready": max(branch_start_distances) <= branch_start_limit,
        "all_prediction_windows_present": all(row["n_prediction_windows"] > 0 for row in records),
        "all_drift_exposed": all(
            row["completion_steps"] >= row["minimum_completion_steps"] for row in records
        ),
        "no_unexpected_env_resets": all(
            not row["unexpected_env_reset"] for row in records + retention_records
        ),
        "no_forbidden_violations": all(
            not row["forbidden_violation"] for row in records + retention_records
        ),
    }
    validity["valid_run"] = all(
        value
        for key, value in validity.items()
        if key
        in {
            "selection_quota_met",
            "selection_locked_before_treatment",
            "complete_ep2_grid",
            "complete_retention_grid",
            "cross_policy_prefix_pass",
            "all_prefixes_ready",
            "paired_start_pass",
            "all_branch_starts_ready",
            "all_prediction_windows_present",
            "all_drift_exposed",
            "no_unexpected_env_resets",
            "no_forbidden_violations",
        }
    )

    by_arm = _arm_summary(records, EP2_ARMS)
    row_map = {(row["seed"], row["condition_id"], row["policy"]): row for row in records}
    prediction_differences = {
        (seed, condition): row_map[(seed, condition, "C_L3_CONSTANT_VELOCITY")][
            "mean_prediction_error_horizon_m"
        ]
        - row_map[(seed, condition, "B_L1_ZERO_ORDER")][
            "mean_prediction_error_horizon_m"
        ]
        for seed in selected_seeds
        for condition in condition_ids
    }
    success_differences = {
        (seed, condition): float(
            row_map[(seed, condition, "C_L3_CONSTANT_VELOCITY")]["successful_resolution"]
        )
        - float(row_map[(seed, condition, "B_L1_ZERO_ORDER")]["successful_resolution"])
        for seed in selected_seeds
        for condition in condition_ids
    }
    rng = np.random.default_rng(20260730)
    primary_effect = {
        "contrast": "C_L3_CONSTANT_VELOCITY_minus_B_L1_ZERO_ORDER",
        "mean_prediction_error_difference_m": fmean(prediction_differences.values()),
        "prediction_error_difference_crossed_bootstrap_95_ci_m": _crossed_bootstrap_ci(
            prediction_differences, selected_seeds, condition_ids, rng
        ),
        "success_rate_difference": fmean(success_differences.values()),
        "success_rate_difference_crossed_bootstrap_95_ci": _crossed_bootstrap_ci(
            success_differences, selected_seeds, condition_ids, rng
        ),
        "l3_lower_prediction_error_pair_rate": fmean(
            value < 0 for value in prediction_differences.values()
        ),
        "l3_success_better_pair_rate": fmean(value > 0 for value in success_differences.values()),
    }

    retention_by_arm = _arm_summary(retention_records, RETENTION_ARMS)
    retention_map = {(row["seed"], row["policy"]): row for row in retention_records}
    retention_differences = {
        seed: float(retention_map[(seed, "C_L3_CONSTANT_VELOCITY")]["successful_resolution"])
        - float(retention_map[(seed, "B_L1_ZERO_ORDER")]["successful_resolution"])
        for seed in selected_seeds
    }
    retention = {
        "by_arm": retention_by_arm,
        "l3_minus_l1_success_rate": fmean(retention_differences.values()),
        "l3_minus_l1_paired_bootstrap_95_ci": _paired_seed_bootstrap_ci(
            retention_differences, rng
        ),
        "non_inferiority_margin": -0.05,
    }
    retention["non_inferiority_pass"] = (
        retention["l3_minus_l1_paired_bootstrap_95_ci"][0]
        > retention["non_inferiority_margin"]
    )

    thresholds = _gate_thresholds(config)
    ep1 = _ep1_diagnostics(config, thresholds)
    h4 = _h4_controls(config, selected_seeds, thresholds)
    rules = config["pilot_decision_rules"]
    decisions = {
        "validity_pass": validity["valid_run"],
        "ep1_parameter_lock_pass": bool(
            abs(
                ep1["l1_zero_order_repair"]["selected"]
                - config["models"]["B_L1_ZERO_ORDER"]["position_alpha"]
            )
            <= 1e-12
            and abs(
                ep1["l3_constant_velocity_fit"]["selected"]
                - config["models"]["C_L3_CONSTANT_VELOCITY"]["velocity_alpha"]
            )
            <= 1e-12
        ),
        "oracle_behavior_pass": by_arm["D_ORACLE_VELOCITY"]["success_rate"]
        >= rules["oracle_min_success_rate"],
        "h1_prediction_pass": primary_effect["mean_prediction_error_difference_m"] < 0,
        "h2_l3_success_floor_pass": by_arm["C_L3_CONSTANT_VELOCITY"]["success_rate"]
        >= rules["l3_min_success_rate"],
        "h2_l1_failure_regime_pass": by_arm["B_L1_ZERO_ORDER"]["success_rate"]
        <= rules["l1_max_success_rate"],
        "h3_static_retention_pass": retention_by_arm["C_L3_CONSTANT_VELOCITY"]["success_rate"]
        >= rules["static_retention_min_success_rate"],
        "h4_drift_pass": h4["M1_PERSISTENT_DRIFT"]["gate_fire_rate"]
        >= rules["gate_drift_min_rate"],
        "h4_controls_pass": all(
            h4[name]["gate_fire_rate"] <= rules["gate_control_max_rate"]
            for name in ("M0_STATIC", "N1_OBSERVATION_NOISE", "N2_SINGLE_IMPULSE")
        ),
    }
    pilot_pass = all(decisions.values())

    combined = {
        "experiment_id": config["experiment_id"],
        "status": config["status"],
        "mode": "isaac",
        "config_path": str(args.config),
        "config_sha256": _sha256(args.config),
        "selection": selection,
        "selected_seeds": selected_seeds,
        "condition_ids": condition_ids,
        "prediction_horizon_steps": config["shared"]["prediction_horizon_steps"],
        "execution_isolation": EXECUTION_ISOLATION,
        "validity": validity,
        "ep1_diagnostics": ep1,
        "ep2_by_arm": by_arm,
        "primary_effect": primary_effect,
        "static_retention": retention,
        "h4_gate_controls": h4,
        "pilot_decisions": decisions,
        "pilot_pass": pilot_pass,
        "records": records,
        "retention_records": retention_records,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "isaac_model_order_results.json").write_text(
        json.dumps(combined, indent=2), encoding="utf-8"
    )
    (args.out_dir / "isaac_model_order_trajectories.json").write_text(
        json.dumps(
            {"ep2": trajectories, "retention": retention_trajectories}, indent=2
        ),
        encoding="utf-8",
    )
    print(json.dumps({
        "validity": validity,
        "ep2_by_arm": by_arm,
        "primary_effect": primary_effect,
        "static_retention": retention,
        "h4_gate_controls": h4,
        "pilot_decisions": decisions,
        "pilot_pass": pilot_pass,
    }, indent=2))


if __name__ == "__main__":
    main()
