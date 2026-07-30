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
parser.add_argument("--tol-m", type=float, default=0.02)
parser.add_argument("--gain", type=float, default=1.0)
parser.add_argument("--max-delta", type=float, default=0.08)
parser.add_argument("--episode-length-s", type=float, default=20.0)
parser.add_argument("--body-index", type=int, default=-1)
parser.add_argument(
    "--policy",
    type=str,
    default="TRACK_DRIFTING",
    choices=["TRACK_DRIFTING", "TRACK_FROZEN"],
    help="TRACK_DRIFTING follows moving command; TRACK_FROZEN keeps pre-drift command (failure mode)",
)
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


def drift_vector(device: torch.device) -> torch.Tensor:
    axis = {"x": 0, "y": 1, "z": 2}[args_cli.drift_axis]
    v = torch.zeros(1, 3, device=device)
    v[:, axis] = args_cli.drift_speed
    return v


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


def _restore_branch_state(env: Any, command_name: str, state: dict[str, Any]) -> None:
    base = env.unwrapped
    for name, saved in state["articulations"].items():
        asset = base.scene.articulations[name]
        root_state = saved["root_state"]
        asset.write_root_pose_to_sim(root_state[:, :7])
        asset.write_root_velocity_to_sim(root_state[:, 7:])
        asset.write_joint_state_to_sim(saved["joint_position"], saved["joint_velocity"])
        asset.set_joint_position_target(saved["joint_position_target"])
        asset.set_joint_velocity_target(saved["joint_velocity_target"])
        asset.set_joint_effort_target(saved["joint_effort_target"])

    for name, saved in state["rigid_objects"].items():
        asset = base.scene.rigid_objects[name]
        root_state = saved["root_state"]
        asset.write_root_pose_to_sim(root_state[:, :7])
        asset.write_root_velocity_to_sim(root_state[:, 7:])

    _set_command(env, command_name, state["command"])
    base.scene.write_data_to_sim()
    base.sim.step(render=False)
    base.scene.update(dt=base.physics_dt)

    env_ids = torch.arange(base.num_envs, dtype=torch.int64, device=base.device)
    for manager_name in ("action_manager", "reward_manager", "termination_manager"):
        manager = getattr(base, manager_name, None)
        if manager is not None:
            manager.reset(env_ids)
    for buffer_name in ("episode_length_buf", "reset_buf", "reset_terminated", "reset_time_outs"):
        buffer = getattr(base, buffer_name, None)
        if buffer is not None:
            buffer.zero_()
    _set_command(env, command_name, state["command"])


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
    state.update(
        {
            "prefix_ready": not failure_reason,
            "prefix_failure_reason": failure_reason or None,
            "prefix_steps": prefix_steps,
            "prefix_stable_steps": stable_steps,
            "prefix_final_distance_m": prefix_final_distance,
            "reset_state_fingerprint": reset_state_fingerprint,
            "reset_command": static_command[0, :3].detach().cpu().numpy().tolist(),
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
    _restore_branch_state(env, command_name, branch_state)
    drift_step = drift_vector(env.unwrapped.device)
    forbidden_center = np.array([0.45, 0.0, 0.15], dtype=np.float64)
    forbidden_half = np.array([0.04, 0.04, 0.04], dtype=np.float64)

    frozen_command = branch_state["command"].clone()
    evaluation_command = frozen_command.clone()
    path = 0.0
    prev_ee = None
    violation = False
    trajectory: list[dict[str, Any]] = []
    prefix_steps = int(branch_state["prefix_steps"])
    branch_horizon_steps = args_cli.max_steps - args_cli.onset
    min_completion_steps = prefix_steps + args_cli.drift_duration
    branch_timeout_step = prefix_steps + branch_horizon_steps
    _, branch_start_ee, branch_start_command = ee_distance(
        env, robot_name, command_name, body_index
    )
    success = False
    unexpected_reset = False
    completion = branch_timeout_step

    for rel in range(branch_horizon_steps):
        t = prefix_steps + rel
        if policy != "STATIC_CONTROL" and rel < args_cli.drift_duration:
            evaluation_command[:, :3] += drift_step
        policy_command = (
            evaluation_command if policy == "TRACK_DRIFTING" else frozen_command
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

        trajectory.append(
            {
                "t": t,
                "drift_exposure_complete": t + 1 >= min_completion_steps,
                "distance_m": dist,
                "ee": ee.tolist(),
                "command": des.tolist(),
                "policy_command": policy_command[0, :3].detach().cpu().numpy().tolist(),
                "policy": policy,
            }
        )

        if unexpected_reset:
            completion = t + 1
            break
        if t + 1 >= min_completion_steps and dist <= args_cli.tol_m and not violation:
            success = True
            completion = t + 1
            break

    terminal = (
        "unexpected_env_reset"
        if unexpected_reset
        else classify(success and not violation, violation, completion >= branch_timeout_step)
    )

    evaluation_target = "STATIC" if policy == "STATIC_CONTROL" else "PERSISTENT_DRIFT"
    return {
        "seed": seed,
        "policy": policy,
        "evaluation_target": evaluation_target,
        "policy_target": policy,
        "branch_source": "shared_pre_drift_snapshot",
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
        "reset_command": branch_state["reset_command"],
        "configured_minimum_onset_step": args_cli.onset,
        "minimum_completion_steps": min_completion_steps,
        "onset_step": prefix_steps,
        "branch_horizon_steps": branch_horizon_steps,
        "branch_timeout_step": branch_timeout_step,
        "drift_speed_m_per_step": args_cli.drift_speed,
        "drift_axis": args_cli.drift_axis,
        "drift_duration_steps": args_cli.drift_duration,
        "final_distance_m": dist,
        "max_distance_m": max(row["distance_m"] for row in trajectory),
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
    min_steps = args_cli.onset + args_cli.drift_duration
    if args_cli.max_steps < min_steps:
        raise ValueError(
            f"max_steps={args_cli.max_steps} must cover onset+duration={min_steps}"
        )
    if args_cli.prefix_max_steps < args_cli.onset:
        raise ValueError(
            f"prefix_max_steps={args_cli.prefix_max_steps} must be >= onset={args_cli.onset}"
        )
    if args_cli.prefix_stable_steps < 1:
        raise ValueError("prefix_stable_steps must be >= 1")
    if args_cli.paired_start_tol_m <= 0:
        raise ValueError("paired_start_tol_m must be > 0")

    out_dir = Path(args_cli.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if str(args_cli.seeds).strip():
        seed_list = [int(x.strip()) for x in str(args_cli.seeds).split(",") if x.strip()]
    else:
        seed_list = [args_cli.seed * 100 + ep for ep in range(args_cli.episodes)]

    records = []
    preconditions = []
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
            branch_state = _prepare_branch_state(
                env, robot_name, command_name, body_index, seed
            )
            precondition = {
                "seed": seed,
                "prefix_ready": branch_state["prefix_ready"],
                "prefix_failure_reason": branch_state["prefix_failure_reason"],
                "prefix_steps": branch_state["prefix_steps"],
                "prefix_stable_steps": branch_state["prefix_stable_steps"],
                "prefix_final_distance_m": branch_state["prefix_final_distance_m"],
                "reset_state_fingerprint": branch_state["reset_state_fingerprint"],
                "reset_command": branch_state["reset_command"],
            }
            preconditions.append(precondition)
            print(json.dumps({"precondition": precondition}), flush=True)
            if not branch_state["prefix_ready"]:
                continue
            for policy in ("STATIC_CONTROL", "TRACK_DRIFTING", "TRACK_FROZEN"):
                rec = run_drift_branch(
                    env,
                    robot_name,
                    command_name,
                    body_index,
                    seed,
                    policy,
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
        "target_dynamics": "persistent_drift",
        "fresh_environment_per_seed": True,
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
