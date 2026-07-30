"""EXP-SURG-003 Isaac runner: persistent target drift (M1) for WM expansion pilot.

Extends 001A action-replay pattern with per-step command drift after onset.
Launched via isaaclab.sh (see scripts/run_exp_surg_003_drift_runpod.sh).
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from omni.isaac.lab.app import AppLauncher

parser = argparse.ArgumentParser(description="EXP-SURG-003 drift Isaac data collection")
parser.add_argument("--task", type=str, default="Isaac-Reach-Dual-STAR-IK-Rel-Play-v0")
parser.add_argument("--num_envs", type=int, default=1)
parser.add_argument("--seed", type=int, default=0)
parser.add_argument("--seeds", type=str, default="")
parser.add_argument("--experiment-id", type=str, default="EXP-SURG-003-drift")
parser.add_argument("--episodes", type=int, default=5)
parser.add_argument("--onset", type=int, default=20)
parser.add_argument("--max-steps", type=int, default=160)
parser.add_argument(
    "--prefix-max-steps",
    type=int,
    default=200,
    help="maximum shared-prefix steps allowed while waiting for a reachable static target",
)
parser.add_argument(
    "--prefix-stable-steps",
    type=int,
    default=5,
    help="consecutive in-tolerance shared-prefix steps required before branching",
)
parser.add_argument(
    "--paired-start-tol-m",
    type=float,
    default=0.001,
    help="maximum EE gap allowed between restored policy branches",
)
parser.add_argument("--drift-speed", type=float, default=0.01, help="m/s per step (sim units)")
parser.add_argument("--drift-axis", type=str, default="x", choices=["x", "y", "z"])
parser.add_argument("--drift-duration", type=int, default=40, help="steps of drift after onset")
parser.add_argument("--drift-delay", type=int, default=0, help="static branch steps before drift")
parser.add_argument(
    "--drift-vector",
    type=str,
    default="",
    help="optional x,y,z displacement per step; overrides drift-axis and drift-speed",
)
parser.add_argument("--tol-m", type=float, default=0.02)
parser.add_argument("--gain", type=float, default=1.0)
parser.add_argument("--max-delta", type=float, default=0.08)
parser.add_argument("--episode-length-s", type=float, default=20.0)
parser.add_argument("--body-index", type=int, default=-1)
parser.add_argument(
    "--policy",
    type=str,
    default="TRACK_DRIFTING",
    choices=[
        "STATIC_CONTROL",
        "TRACK_DRIFTING",
        "TRACK_FROZEN",
        "A_ZERO_ORDER_FROZEN",
        "B_L1_ZERO_ORDER",
        "C_L3_CONSTANT_VELOCITY",
        "D_ORACLE_VELOCITY",
    ],
    help="single policy arm to execute in this isolated Isaac process",
)
parser.add_argument(
    "--target-mode",
    choices=["auto", "static", "persistent_drift"],
    default="auto",
)
parser.add_argument("--condition-id", default="default")
parser.add_argument(
    "--conditions-config",
    default="",
    help="optional JSON config whose conditions are run sequentially in one process",
)
parser.add_argument("--prediction-horizon", type=int, default=10)
parser.add_argument("--a-position-alpha", type=float, default=0.5)
parser.add_argument("--l1-position-alpha", type=float, default=1.0)
parser.add_argument("--l3-position-alpha", type=float, default=1.0)
parser.add_argument("--l3-velocity-alpha", type=float, default=1.0)
parser.add_argument("--gate-window", type=int, default=8)
parser.add_argument("--gate-min-deltas", type=int, default=4)
parser.add_argument("--gate-speed-floor", type=float, default=0.0005)
parser.add_argument("--gate-min-active-fraction", type=float, default=0.75)
parser.add_argument("--gate-min-directional-consistency", type=float, default=0.90)
parser.add_argument("--gate-min-cv-improvement", type=float, default=0.50)
parser.add_argument("--out-dir", type=str, required=True)
parser.add_argument("--disable_fabric", action="store_true", default=False)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import gymnasium as gym
import torch
from omni.isaac.lab_tasks.utils import parse_env_cfg

import omni.isaac.lab_tasks  # noqa: F401
import orbit.surgical.tasks  # noqa: F401

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from orbit_reach_common import (  # noqa: E402
    classify,
    ee_distance,
    find_robot_name,
    in_forbidden,
    resolve_ee_body_index,
    scripted_action,
)
from wm_expansion.target_dynamics import (  # noqa: E402
    ConstantVelocityTargetModel,
    GateThresholds,
    ZeroOrderTargetModel,
)


def drift_vector(device: torch.device) -> torch.Tensor:
    if str(args_cli.drift_vector).strip():
        values = [
            float(value.strip())
            for value in str(args_cli.drift_vector).split(",")
            if value.strip()
        ]
        if len(values) != 3:
            raise ValueError("drift-vector must contain exactly three comma-separated values")
        return torch.tensor([values], dtype=torch.float32, device=device)
    axis = {"x": 0, "y": 1, "z": 2}[args_cli.drift_axis]
    v = torch.zeros(1, 3, device=device)
    v[:, axis] = args_cli.drift_speed
    return v


def _target_mode(policy: str) -> str:
    if args_cli.target_mode != "auto":
        return str(args_cli.target_mode)
    return "static" if policy == "STATIC_CONTROL" else "persistent_drift"


def _gate_thresholds() -> GateThresholds:
    return GateThresholds(
        min_deltas=args_cli.gate_min_deltas,
        speed_floor_m_per_step=args_cli.gate_speed_floor,
        min_active_fraction=args_cli.gate_min_active_fraction,
        min_directional_consistency=args_cli.gate_min_directional_consistency,
        min_cv_error_improvement=args_cli.gate_min_cv_improvement,
    )


def _target_model(policy: str) -> ZeroOrderTargetModel | None:
    if policy == "A_ZERO_ORDER_FROZEN":
        return ZeroOrderTargetModel(position_alpha=args_cli.a_position_alpha)
    if policy == "B_L1_ZERO_ORDER":
        return ZeroOrderTargetModel(position_alpha=args_cli.l1_position_alpha)
    if policy == "C_L3_CONSTANT_VELOCITY":
        return ConstantVelocityTargetModel(
            position_alpha=args_cli.l3_position_alpha,
            velocity_alpha=args_cli.l3_velocity_alpha,
            gate_thresholds=_gate_thresholds(),
            gate_window=args_cli.gate_window,
        )
    return None


def _get_command(env: Any, command_name: str) -> torch.Tensor:
    return env.unwrapped.command_manager.get_command(command_name).clone()


def _set_command(env: Any, command_name: str, command: torch.Tensor) -> None:
    env.unwrapped.command_manager.get_command(command_name)[:] = command


def _step_reset(step_result: tuple[Any, ...]) -> bool:
    terminated, truncated = step_result[2], step_result[3]
    for value in (terminated, truncated):
        if torch.is_tensor(value):
            if bool(value.any().item()):
                return True
        elif bool(np.asarray(value).any()):
            return True
    return False


def _capture_branch_state(env: Any, command_name: str) -> dict[str, Any]:
    base = env.unwrapped
    articulations = {}
    for name, asset in base.scene.articulations.items():
        articulations[name] = {
            "root_state": asset.data.root_state_w.clone(),
            "joint_position": asset.data.joint_pos.clone(),
            "joint_velocity": asset.data.joint_vel.clone(),
            "joint_position_target": asset.data.joint_pos_target.clone(),
            "joint_velocity_target": asset.data.joint_vel_target.clone(),
            "joint_effort_target": asset.data.joint_effort_target.clone(),
        }

    rigid_objects = {}
    for name, asset in base.scene.rigid_objects.items():
        rigid_objects[name] = {"root_state": asset.data.root_state_w.clone()}

    return {
        "articulations": articulations,
        "rigid_objects": rigid_objects,
        "command": _get_command(env, command_name),
    }


def _state_fingerprint(state: dict[str, Any]) -> str:
    digest = hashlib.sha256()
    for group_name in ("articulations", "rigid_objects"):
        for asset_name, values in sorted(state[group_name].items()):
            digest.update(group_name.encode("utf-8"))
            digest.update(asset_name.encode("utf-8"))
            for value_name, value in sorted(values.items()):
                digest.update(value_name.encode("utf-8"))
                array = value.detach().cpu().numpy()
                digest.update(np.ascontiguousarray(array).tobytes())
    command = state["command"].detach().cpu().numpy()
    digest.update(np.ascontiguousarray(command).tobytes())
    return digest.hexdigest()


def _prepare_branch_state(
    env: Any,
    robot_name: str,
    command_name: str,
    body_index: int,
    seed: int,
) -> dict[str, Any]:
    torch.manual_seed(seed)
    env.reset(seed=seed)
    reset_state = _capture_branch_state(env, command_name)
    static_command = reset_state["command"].clone()
    reset_state_fingerprint = _state_fingerprint(reset_state)
    stable_steps = 0
    prefix_steps = 0
    prefix_final_distance = None
    failure_reason = "static_target_not_reached"

    for prefix_step in range(args_cli.prefix_max_steps):
        _set_command(env, command_name, static_command)
        with torch.no_grad():
            action = scripted_action(
                env, robot_name, command_name, args_cli.gain, body_index, args_cli.max_delta
            )
            _set_command(env, command_name, static_command)
            step_result = env.step(action)
        _set_command(env, command_name, static_command)
        prefix_steps = prefix_step + 1
        if _step_reset(step_result):
            failure_reason = "unexpected_env_reset"
            break

        prefix_final_distance, _, _ = ee_distance(
            env, robot_name, command_name, body_index
        )
        if prefix_steps >= args_cli.onset and prefix_final_distance <= args_cli.tol_m:
            stable_steps += 1
        else:
            stable_steps = 0
        if stable_steps >= args_cli.prefix_stable_steps:
            failure_reason = ""
            break

    state = _capture_branch_state(env, command_name)
    branch_state_fingerprint = _state_fingerprint(state)
    state.update(
        {
            "prefix_ready": not failure_reason,
            "prefix_failure_reason": failure_reason or None,
            "prefix_steps": prefix_steps,
            "prefix_stable_steps": stable_steps,
            "prefix_final_distance_m": prefix_final_distance,
            "reset_state_fingerprint": reset_state_fingerprint,
            "reset_command": static_command[0, :3].detach().cpu().numpy().tolist(),
            "branch_state_fingerprint": branch_state_fingerprint,
        }
    )
    return state


def run_drift_branch(
    env: Any,
    robot_name: str,
    command_name: str,
    body_index: int,
    seed: int,
    policy: str,
    branch_state: dict[str, Any],
) -> dict[str, Any]:
    drift_step = drift_vector(env.unwrapped.device)
    drift_step_np = drift_step[0, :3].detach().cpu().numpy().astype(np.float64)
    target_mode = _target_mode(policy)
    is_static_target = target_mode == "static"
    model = _target_model(policy)
    forbidden_center = np.array([0.45, 0.0, 0.15], dtype=np.float64)
    forbidden_half = np.array([0.04, 0.04, 0.04], dtype=np.float64)

    frozen_command = branch_state["command"].clone()
    evaluation_command = frozen_command.clone()
    if model is not None:
        model.observe(
            frozen_command[0, :3].detach().cpu().numpy().astype(np.float64)
        )
    path = 0.0
    prev_ee = None
    violation = False
    trajectory: list[dict[str, Any]] = []
    prediction_errors: list[float] = []
    gate_states: list[bool] = []
    prefix_steps = int(branch_state["prefix_steps"])
    branch_horizon_steps = args_cli.max_steps - args_cli.onset
    exposure_steps = args_cli.drift_delay + args_cli.drift_duration
    min_completion_steps = prefix_steps + exposure_steps
    branch_timeout_step = prefix_steps + branch_horizon_steps
    _, branch_start_ee, branch_start_command = ee_distance(
        env, robot_name, command_name, body_index
    )
    success = False
    unexpected_reset = False
    completion = branch_timeout_step

    for rel in range(branch_horizon_steps):
        t = prefix_steps + rel
        drift_active = bool(
            not is_static_target
            and args_cli.drift_delay <= rel
            and rel < exposure_steps
        )
        if drift_active:
            evaluation_command[:, :3] += drift_step

        observed_xyz = (
            evaluation_command[0, :3].detach().cpu().numpy().astype(np.float64)
        )
        gate_fired = False
        gate_metrics = None
        if model is not None:
            model.observe(observed_xyz)
            predicted_xyz = model.predict(args_cli.prediction_horizon)
            if isinstance(model, ConstantVelocityTargetModel):
                gate_fired = model.gate_fired
                gate_metrics = model.gate_decision.to_dict()
        elif policy == "D_ORACLE_VELOCITY":
            gate_fired = drift_active
            predicted_xyz = observed_xyz + (
                float(args_cli.prediction_horizon) * drift_step_np
                if drift_active
                else 0.0
            )
        elif policy == "TRACK_DRIFTING":
            predicted_xyz = observed_xyz.copy()
        elif policy in {"TRACK_FROZEN", "STATIC_CONTROL"}:
            predicted_xyz = (
                frozen_command[0, :3].detach().cpu().numpy().astype(np.float64)
            )
        else:
            raise ValueError(f"unsupported policy: {policy}")

        policy_command = evaluation_command.clone()
        policy_command[:, :3] = torch.as_tensor(
            predicted_xyz, dtype=policy_command.dtype, device=policy_command.device
        )
        _set_command(env, command_name, policy_command)

        with torch.no_grad():
            act = scripted_action(
                env, robot_name, command_name, args_cli.gain, body_index, args_cli.max_delta
            )
            _set_command(env, command_name, evaluation_command)
            step_result = env.step(act)

        _set_command(env, command_name, evaluation_command)
        unexpected_reset = _step_reset(step_result)
        dist, ee, des = ee_distance(env, robot_name, command_name, body_index)
        if prev_ee is not None:
            path += float(np.linalg.norm(ee - prev_ee))
        prev_ee = ee
        if in_forbidden(ee, forbidden_center, forbidden_half):
            violation = True

        prediction_error = None
        if is_static_target:
            prediction_error = float(np.linalg.norm(predicted_xyz - observed_xyz))
        elif drift_active:
            drift_index = rel - args_cli.drift_delay
            if drift_index + args_cli.prediction_horizon < args_cli.drift_duration:
                actual_future = (
                    observed_xyz
                    + float(args_cli.prediction_horizon) * drift_step_np
                )
                prediction_error = float(np.linalg.norm(predicted_xyz - actual_future))
        if prediction_error is not None:
            prediction_errors.append(prediction_error)
        gate_states.append(gate_fired)

        trajectory.append(
            {
                "t": t,
                "drift_exposure_complete": t + 1 >= min_completion_steps,
                "distance_m": dist,
                "ee": ee.tolist(),
                "command": des.tolist(),
                "policy_command": policy_command[0, :3].detach().cpu().numpy().tolist(),
                "predicted_target_horizon": np.asarray(predicted_xyz).tolist(),
                "prediction_error_horizon_m": prediction_error,
                "prediction_horizon_steps": args_cli.prediction_horizon,
                "gate_fired": gate_fired,
                "gate_metrics": gate_metrics,
                "action": act[0].detach().cpu().numpy().tolist(),
                "policy": policy,
                "condition_id": args_cli.condition_id,
                "target_mode": target_mode,
            }
        )

        if unexpected_reset:
            completion = t + 1
            break
        if (
            not is_static_target
            and t + 1 >= min_completion_steps
            and dist <= args_cli.tol_m
            and not violation
        ):
            success = True
            completion = t + 1
            break

    max_distance = max(row["distance_m"] for row in trajectory)
    if is_static_target and not unexpected_reset:
        success = bool(
            dist <= args_cli.tol_m
            and max_distance <= args_cli.tol_m
            and not violation
        )
        completion = branch_timeout_step

    terminal = (
        "unexpected_env_reset"
        if unexpected_reset
        else classify(success and not violation, violation, completion >= branch_timeout_step)
    )

    evaluation_target = "STATIC" if is_static_target else "PERSISTENT_DRIFT"
    final_gate_metrics = (
        model.gate_decision.to_dict()
        if isinstance(model, ConstantVelocityTargetModel)
        else None
    )
    return {
        "seed": seed,
        "policy": policy,
        "condition_id": args_cli.condition_id,
        "target_mode": target_mode,
        "evaluation_target": evaluation_target,
        "policy_target": policy,
        "branch_source": "isolated_process_deterministic_prefix",
        "branch_start_ee": branch_start_ee.tolist(),
        "branch_start_command": branch_start_command.tolist(),
        "branch_start_distance_m": float(
            np.linalg.norm(branch_start_ee - branch_start_command)
        ),
        "prefix_ready": branch_state["prefix_ready"],
        "prefix_steps": prefix_steps,
        "prefix_stable_steps": branch_state["prefix_stable_steps"],
        "prefix_final_distance_m": branch_state["prefix_final_distance_m"],
        "reset_state_fingerprint": branch_state["reset_state_fingerprint"],
        "branch_state_fingerprint": branch_state["branch_state_fingerprint"],
        "reset_command": branch_state["reset_command"],
        "configured_minimum_onset_step": args_cli.onset,
        "drift_delay_steps": args_cli.drift_delay,
        "minimum_completion_steps": min_completion_steps,
        "onset_step": prefix_steps,
        "branch_horizon_steps": branch_horizon_steps,
        "branch_timeout_step": branch_timeout_step,
        "drift_speed_m_per_step": float(np.linalg.norm(drift_step_np)),
        "drift_vector_m_per_step": drift_step_np.tolist(),
        "drift_axis": args_cli.drift_axis,
        "drift_duration_steps": args_cli.drift_duration,
        "prediction_horizon_steps": args_cli.prediction_horizon,
        "mean_prediction_error_horizon_m": (
            float(np.mean(prediction_errors)) if prediction_errors else None
        ),
        "n_prediction_windows": len(prediction_errors),
        "gate_fired_any": any(gate_states),
        "gate_fire_rate": float(np.mean(gate_states)) if gate_states else 0.0,
        "final_gate_metrics": final_gate_metrics,
        "final_distance_m": dist,
        "max_distance_m": max_distance,
        "path_length_m": path,
        "completion_steps": completion,
        "forbidden_violation": violation,
        "unexpected_env_reset": unexpected_reset,
        "successful_resolution": bool(success and not violation and not unexpected_reset),
        "terminal_category": terminal,
        "trajectory": trajectory,
        "mode": "isaac",
        "experiment_id": args_cli.experiment_id,
    }


def _summarize_records(
    records: list[dict[str, Any]],
    seeds: list[int],
    preconditions: list[dict[str, Any]],
) -> dict[str, Any]:
    by_policy = {}
    policies = ("STATIC_CONTROL", "TRACK_DRIFTING", "TRACK_FROZEN")
    for policy in policies:
        rows = [row for row in records if row["policy"] == policy]
        by_policy[policy] = {
            "n": len(rows),
            "success_rate": (
                float(np.mean([row["successful_resolution"] for row in rows]))
                if rows
                else None
            ),
            "mean_final_distance_m": (
                float(np.mean([row["final_distance_m"] for row in rows])) if rows else None
            ),
            "mean_completion_steps": (
                float(np.mean([row["completion_steps"] for row in rows])) if rows else None
            ),
            "forbidden_violations": int(sum(row["forbidden_violation"] for row in rows)),
            "unexpected_env_resets": int(sum(row["unexpected_env_reset"] for row in rows)),
        }

    ee_gaps = []
    command_gaps = []
    complete_branch_count = 0
    for seed in seeds:
        pair = {row["policy"]: row for row in records if row["seed"] == seed}
        if set(pair) != set(policies):
            continue
        complete_branch_count += 1
        drifting = pair["TRACK_DRIFTING"]
        frozen = pair["TRACK_FROZEN"]
        for other in (frozen, pair["STATIC_CONTROL"]):
            ee_gaps.append(
                float(
                    np.linalg.norm(
                        np.asarray(drifting["branch_start_ee"])
                        - other["branch_start_ee"]
                    )
                )
            )
            command_gaps.append(
                float(
                    np.linalg.norm(
                        np.asarray(drifting["branch_start_command"])
                        - other["branch_start_command"]
                    )
                )
            )

    max_ee_gap = max(ee_gaps, default=None)
    max_command_gap = max(command_gaps, default=None)
    ready_seeds = [row["seed"] for row in preconditions if row["prefix_ready"]]
    failed_seeds = [row["seed"] for row in preconditions if not row["prefix_ready"]]
    complete_pair_count = complete_branch_count
    branch_start_distances = [row["branch_start_distance_m"] for row in records]
    max_branch_start_distance = max(branch_start_distances, default=None)
    static_rows = [row for row in records if row["policy"] == "STATIC_CONTROL"]
    static_control_pass = bool(
        len(static_rows) == len(seeds)
        and all(
            row["successful_resolution"] and row["max_distance_m"] <= args_cli.tol_m
            for row in static_rows
        )
    )
    validity = {
        "requested_seed_count": len(seeds),
        "ready_seed_count": len(ready_seeds),
        "ready_seeds": ready_seeds,
        "failed_readiness_seeds": failed_seeds,
        "all_requested_seeds_ready": len(ready_seeds) == len(seeds),
        "complete_pair_count": complete_pair_count,
        "complete_branch_count": complete_branch_count,
        "max_branch_start_ee_gap_m": max_ee_gap,
        "max_branch_start_command_gap_m": max_command_gap,
        "paired_start_tolerance_m": args_cli.paired_start_tol_m,
        "paired_start_pass": bool(
            complete_branch_count == len(seeds)
            and max_ee_gap is not None
            and max_command_gap is not None
            and max_ee_gap <= args_cli.paired_start_tol_m
            and max_command_gap <= 1e-6
        ),
        "max_branch_start_distance_m": max_branch_start_distance,
        "branch_start_distance_limit_m": args_cli.tol_m
        + args_cli.paired_start_tol_m,
        "all_branch_starts_ready": bool(
            len(branch_start_distances) == len(policies) * len(seeds)
            and max_branch_start_distance is not None
            and max_branch_start_distance
            <= args_cli.tol_m + args_cli.paired_start_tol_m
        ),
        "all_drift_exposed": bool(
            len(records) == len(policies) * len(seeds)
            and all(
                row["completion_steps"] >= row["minimum_completion_steps"]
                for row in records
            )
        ),
        "no_unexpected_env_resets": bool(
            all(not row["unexpected_env_reset"] for row in records)
        ),
        "static_control_pass": static_control_pass,
    }
    validity["valid_pilot"] = bool(
        validity["all_requested_seeds_ready"]
        and validity["paired_start_pass"]
        and validity["all_branch_starts_ready"]
        and validity["all_drift_exposed"]
        and validity["no_unexpected_env_resets"]
        and validity["static_control_pass"]
    )
    return {"by_policy": by_policy, "validity": validity}


def main() -> None:
    if args_cli.prefix_max_steps < args_cli.onset:
        raise ValueError(
            f"prefix_max_steps={args_cli.prefix_max_steps} must be >= onset={args_cli.onset}"
        )
    if args_cli.prefix_stable_steps < 1:
        raise ValueError("prefix_stable_steps must be >= 1")
    if args_cli.paired_start_tol_m <= 0:
        raise ValueError("paired_start_tol_m must be > 0")
    if args_cli.drift_delay < 0:
        raise ValueError("drift_delay must be >= 0")
    if args_cli.drift_duration < 1:
        raise ValueError("drift_duration must be >= 1")
    if args_cli.prediction_horizon < 1:
        raise ValueError("prediction_horizon must be >= 1")
    _gate_thresholds().validate()

    if str(args_cli.conditions_config).strip():
        condition_config = json.loads(
            Path(args_cli.conditions_config).read_text(encoding="utf-8")
        )
        conditions = condition_config.get("conditions", [])
        if not conditions:
            raise ValueError("conditions-config contains no conditions")
    else:
        conditions = [
            {
                "id": args_cli.condition_id,
                "drift_vector_m_per_step": None,
                "delay_steps": args_cli.drift_delay,
                "duration_steps": args_cli.drift_duration,
                "max_steps": args_cli.max_steps,
            }
        ]

    out_dir = Path(args_cli.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if str(args_cli.seeds).strip():
        seed_list = [int(x.strip()) for x in str(args_cli.seeds).split(",") if x.strip()]
    else:
        seed_list = [args_cli.seed * 100 + ep for ep in range(args_cli.episodes)]
    if len(seed_list) != 1:
        raise ValueError(
            "orbit_reach_drift.py accepts one seed per Isaac process; "
            "use run_exp_surg_003_drift.sh to orchestrate multiple seeds"
        )

    records: list[dict[str, Any]] = []
    preconditions: list[dict[str, Any]] = []
    for seed in seed_list:
        env_cfg = parse_env_cfg(
            args_cli.task,
            num_envs=args_cli.num_envs,
            use_fabric=not args_cli.disable_fabric,
        )
        if hasattr(env_cfg, "episode_length_s"):
            env_cfg.episode_length_s = float(args_cli.episode_length_s)
        env = gym.make(args_cli.task, cfg=env_cfg)
        try:
            robot_name = find_robot_name(env.unwrapped.scene)
            body_index = resolve_ee_body_index(
                env.unwrapped.scene[robot_name], args_cli.body_index
            )
            command_name = "ee_1_pose"
            for condition in conditions:
                args_cli.condition_id = str(condition["id"])
                vector = condition.get("drift_vector_m_per_step")
                if vector is not None:
                    args_cli.drift_vector = ",".join(str(value) for value in vector)
                args_cli.drift_delay = int(condition["delay_steps"])
                args_cli.drift_duration = int(condition["duration_steps"])
                args_cli.max_steps = int(
                    condition.get(
                        "max_steps",
                        args_cli.onset
                        + args_cli.drift_delay
                        + args_cli.drift_duration,
                    )
                )
                if args_cli.drift_delay < 0:
                    raise ValueError("drift_delay must be >= 0")
                if args_cli.drift_duration < 1:
                    raise ValueError("drift_duration must be >= 1")
                minimum_steps = (
                    args_cli.onset + args_cli.drift_delay + args_cli.drift_duration
                )
                if args_cli.max_steps < minimum_steps:
                    raise ValueError(
                        f"max_steps={args_cli.max_steps} must cover "
                        f"onset+delay+duration={minimum_steps}"
                    )
                _ = drift_vector(torch.device("cpu"))

                branch_state = _prepare_branch_state(
                    env, robot_name, command_name, body_index, seed
                )
                precondition = {
                    "seed": seed,
                    "condition_id": args_cli.condition_id,
                    "prefix_ready": branch_state["prefix_ready"],
                    "prefix_failure_reason": branch_state["prefix_failure_reason"],
                    "prefix_steps": branch_state["prefix_steps"],
                    "prefix_stable_steps": branch_state["prefix_stable_steps"],
                    "prefix_final_distance_m": branch_state["prefix_final_distance_m"],
                    "reset_state_fingerprint": branch_state["reset_state_fingerprint"],
                    "reset_command": branch_state["reset_command"],
                    "branch_state_fingerprint": branch_state[
                        "branch_state_fingerprint"
                    ],
                }
                preconditions.append(precondition)
                print(json.dumps({"precondition": precondition}), flush=True)
                if not branch_state["prefix_ready"]:
                    continue
                rec = run_drift_branch(
                    env,
                    robot_name,
                    command_name,
                    body_index,
                    seed,
                    args_cli.policy,
                    branch_state,
                )
                records.append(rec)
                print(
                    json.dumps({k: rec[k] for k in rec if k != "trajectory"}),
                    flush=True,
                )
        finally:
            env.close()

    summary = {
        "experiment": args_cli.experiment_id,
        "mode": "isaac",
        "n_records": len(records),
        "seeds": seed_list,
        "preconditions": preconditions,
        "summary": _summarize_records(records, seed_list, preconditions),
        "records": [{k: r[k] for k in r if k != "trajectory"} for r in records],
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "target_dynamics": _target_mode(args_cli.policy),
        "condition_ids": [str(condition["id"]) for condition in conditions],
        "fresh_environment_per_seed": True,
        "isolated_policy_process": args_cli.policy,
    }
    out_json = out_dir / "isaac_drift_results.json"
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out_dir / "isaac_drift_trajectories.json").write_text(
        json.dumps(records, indent=2), encoding="utf-8"
    )
    print(f"[INFO] wrote {out_json}")


if __name__ == "__main__":
    main()
    simulation_app.close()
