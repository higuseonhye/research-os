"""EXP-SURG-001D Isaac runner: occlusion proxy v0.1 × multi-mode CF branches.

Fork of orbit_reach_study1a_counterfactual.py — adds P3 gain-scale occlusion,
REOBSERVE hold, RESHAPE/HANDOVER proxies (D1 modes via --modes).

Contract: experiments/.../docs/study1d_occlusion_proxy_v0.1.md
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from omni.isaac.lab.app import AppLauncher

parser = argparse.ArgumentParser(description="EXP-SURG-001D occlusion multi-mode Isaac runner")
parser.add_argument("--task", type=str, default="Isaac-Reach-Dual-STAR-IK-Rel-Play-v0")
parser.add_argument("--num_envs", type=int, default=1)
parser.add_argument("--seed", type=int, default=0)
parser.add_argument("--seeds", type=str, default="")
parser.add_argument("--experiment-id", type=str, default="EXP-SURG-001D")
parser.add_argument("--episodes", type=int, default=5)
parser.add_argument("--onset", type=int, default=20)
parser.add_argument("--max-steps", type=int, default=160)
parser.add_argument("--shift-m", type=float, default=0.06)
parser.add_argument("--tol-m", type=float, default=0.02)
parser.add_argument("--gain", type=float, default=1.0)
parser.add_argument("--max-delta", type=float, default=0.08)
parser.add_argument("--episode-length-s", type=float, default=20.0)
parser.add_argument("--body-index", type=int, default=-1)
parser.add_argument("--replan-delay", type=int, default=20)
parser.add_argument("--occlusion-level", type=int, default=1)
parser.add_argument("--visibility-fraction", type=float, default=0.35)
parser.add_argument("--reobserve-hold-steps", type=int, default=10)
parser.add_argument("--reshape-steps", type=int, default=20)
parser.add_argument(
    "--modes",
    type=str,
    default="CONTINUE,REPLAN,REOBSERVE",
    help="Comma-separated: CONTINUE, REPLAN, REOBSERVE, RESHAPE, HANDOVER",
)
parser.add_argument("--out-dir", type=str, required=True)
parser.add_argument("--disable_fabric", action="store_true", default=False)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import gymnasium as gym
import torch
from omni.isaac.lab.utils.math import combine_frame_transforms
from omni.isaac.lab_tasks.utils import parse_env_cfg

import omni.isaac.lab_tasks  # noqa: F401
import orbit.surgical.tasks  # noqa: F401

MODE_CLASS = {
    "CONTINUE": "policy",
    "REPLAN": "policy",
    "REOBSERVE": "policy_information",
    "RESHAPE": "environment",
    "HANDOVER": "collaboration",
}


def tensor_flag(value: object) -> bool:
    if torch.is_tensor(value):
        if value.dtype == torch.bool:
            return bool(value.any().item())
        return bool((value != 0).any().item())
    if isinstance(value, (list, tuple)):
        return any(bool(v) for v in value)
    return bool(value)


def tensor_to_np(value: object) -> np.ndarray:
    if torch.is_tensor(value):
        return value.detach().cpu().numpy()
    return np.asarray(value)


def find_robot_name(scene: Any) -> str:
    for cand in ("robot_1", "robot", "star", "dual_star"):
        try:
            _ = scene[cand]
            return cand
        except Exception:
            continue
    return str(next(iter(scene.keys())))


def resolve_ee_body_index(asset: Any, preferred: int = -1) -> int:
    n = int(asset.data.body_state_w.shape[1])
    if preferred >= 0 and preferred < n:
        return preferred
    names: list[str] = []
    for attr in ("body_names", "body_names_list"):
        val = getattr(asset.data, attr, None) or getattr(asset, attr, None)
        if val is not None:
            names = [str(x) for x in val]
            break
    for target in ("endo360_needle", "endo360_calibrated", "star_link_ee"):
        if target in names:
            return names.index(target)
    return 13 if n > 13 else n - 1


def ee_distance(env: Any, robot_name: str, command_name: str, body_index: int) -> tuple[float, np.ndarray, np.ndarray]:
    base = env.unwrapped
    asset = base.scene[robot_name]
    command = base.command_manager.get_command(command_name)
    desired_pos_body = command[:, :3]
    desired_pos_world, _ = combine_frame_transforms(
        asset.data.root_state_w[:, :3],
        asset.data.root_state_w[:, 3:7],
        desired_pos_body,
    )
    current_pos_world = asset.data.body_state_w[:, body_index, :3]
    dist = torch.norm(current_pos_world - desired_pos_world, dim=1)
    return float(dist.mean().item()), tensor_to_np(current_pos_world[0]), tensor_to_np(desired_pos_world[0])


def get_command_xyz(env: Any, command_name: str) -> torch.Tensor:
    cmd = env.unwrapped.command_manager.get_command(command_name)
    return cmd[:, :3].clone()


def set_command_xyz(env: Any, command_name: str, xyz: torch.Tensor) -> None:
    cmd = env.unwrapped.command_manager.get_command(command_name)
    cmd[:, :3] = xyz


def scripted_action(
    env: Any,
    robot_name: str,
    command_name: str,
    gain: float,
    body_index: int,
    max_delta: float = 0.05,
    gain_scale: float = 1.0,
    freeze: bool = False,
) -> torch.Tensor:
    from omni.isaac.lab.utils.math import (
        axis_angle_from_quat,
        quat_apply,
        quat_inv,
        quat_mul,
    )

    base = env.unwrapped
    device = base.device
    action = torch.zeros(env.action_space.shape, device=device)
    if freeze:
        return action

    asset = base.scene[robot_name]
    command = base.command_manager.get_command(command_name)
    desired_pos_body = command[:, :3]
    desired_quat_body = command[:, 3:7]
    root_pos = asset.data.root_state_w[:, :3]
    root_quat = asset.data.root_state_w[:, 3:7]
    desired_pos_world, desired_quat_world = combine_frame_transforms(
        root_pos, root_quat, desired_pos_body, desired_quat_body
    )
    current_pos_world = asset.data.body_state_w[:, body_index, :3]
    current_quat_world = asset.data.body_state_w[:, body_index, 3:7]

    g = gain * gain_scale
    err_world = desired_pos_world - current_pos_world
    err_body = quat_apply(quat_inv(root_quat), err_world)
    delta_pos = torch.clamp(g * err_body, -max_delta, max_delta)
    q_err = quat_mul(desired_quat_world, quat_inv(current_quat_world))
    delta_rot = torch.clamp(g * axis_angle_from_quat(q_err), -max_delta, max_delta)

    action[..., 0:3] = delta_pos
    action[..., 3:6] = delta_rot
    return action


def in_forbidden(ee_world: np.ndarray, center: np.ndarray, half: np.ndarray) -> bool:
    return bool(np.all(np.abs(ee_world - center) <= half))


def classify(success: bool, violation: bool, timed_out: bool, handover: bool = False) -> str:
    if handover:
        return "handover_proxy"
    if violation:
        return "unsafe_failure"
    if success:
        return "successful_resolution"
    if timed_out:
        return "timeout_failure"
    return "safe_unresolved"


def run_branch(
    env: Any,
    robot_name: str,
    command_name: str,
    body_index: int,
    pre_actions: list[torch.Tensor],
    frozen_xyz: torch.Tensor,
    shifted_xyz: torch.Tensor,
    mode: str,
    onset: int,
    max_steps: int,
    tol: float,
    gain: float,
    max_delta: float,
    forbidden_center: np.ndarray,
    forbidden_half: np.ndarray,
    replan_delay: int,
    visibility_fraction: float,
    reobserve_hold: int,
    reshape_steps: int,
    occlusion_level: int,
) -> dict[str, Any]:
    path = 0.0
    prev_ee = None
    violation = False
    shifted_target_np = tensor_to_np(shifted_xyz[0])
    visibility_cleared = False

    for act in pre_actions:
        with torch.no_grad():
            env.step(act)
        _, ee, _ = ee_distance(env, robot_name, command_name, body_index)
        if prev_ee is not None:
            path += float(np.linalg.norm(ee - prev_ee))
        prev_ee = ee
        if in_forbidden(ee, forbidden_center, forbidden_half):
            violation = True

    is_continue = mode == "CONTINUE"
    is_reobserve = mode == "REOBSERVE"
    is_reshape = mode == "RESHAPE"
    is_handover = mode == "HANDOVER"
    is_replan = mode == "REPLAN"

    if is_continue:
        switch_step = onset
        response_start = onset
        response_label = "CONTINUE"
        replan_delay_out = None
    elif is_reobserve:
        switch_step = onset + reobserve_hold
        response_start = onset
        response_label = "REOBSERVE"
        replan_delay_out = None
    elif is_reshape:
        switch_step = onset + reshape_steps
        response_start = onset
        response_label = "RESHAPE"
        replan_delay_out = None
    elif is_handover:
        switch_step = onset
        response_start = onset
        response_label = "HANDOVER"
        replan_delay_out = None
    elif is_replan:
        switch_step = onset + replan_delay
        response_start = switch_step
        response_label = f"REPLAN_d{replan_delay}"
        replan_delay_out = replan_delay
    else:
        raise ValueError(f"Unknown mode {mode}")

    final_dist = 999.0
    completion = max_steps
    success = False
    handover_done = False

    for t in range(onset, max_steps):
        if is_handover:
            set_command_xyz(env, command_name, frozen_xyz)
            with torch.no_grad():
                act = scripted_action(
                    env, robot_name, command_name, gain, body_index, max_delta, freeze=True
                )
                _, _, terminated, truncated, _ = env.step(act)
            handover_done = True
            completion = t + 1
            _, ee, _ = ee_distance(env, robot_name, command_name, body_index)
            final_dist = float(np.linalg.norm(ee - shifted_target_np))
            break

        if is_continue or (is_replan and t < switch_step) or (is_reobserve and t < switch_step) or (
            is_reshape and t < switch_step
        ):
            set_command_xyz(env, command_name, frozen_xyz)
        else:
            set_command_xyz(env, command_name, shifted_xyz)
            if is_reobserve or is_reshape:
                visibility_cleared = True

        if is_reobserve and t < onset + reobserve_hold:
            gain_scale = 0.0
            freeze = True
        elif visibility_cleared or t >= switch_step:
            gain_scale = 1.0
            freeze = False
        else:
            gain_scale = visibility_fraction
            freeze = False

        with torch.no_grad():
            act = scripted_action(
                env, robot_name, command_name, gain, body_index, max_delta, gain_scale, freeze
            )
            _, _, terminated, truncated, _ = env.step(act)

        _, ee, _ = ee_distance(env, robot_name, command_name, body_index)
        final_dist = float(np.linalg.norm(ee - shifted_target_np))
        if prev_ee is not None:
            path += float(np.linalg.norm(ee - prev_ee))
        prev_ee = ee
        if in_forbidden(ee, forbidden_center, forbidden_half):
            violation = True

        if final_dist <= tol:
            success = not violation
            completion = t + 1
            break
        if tensor_flag(terminated) or tensor_flag(truncated):
            completion = t + 1
            break

    timed_out = completion >= max_steps and not success and not handover_done
    return {
        "response": response_label,
        "response_class": MODE_CLASS.get(mode, "policy"),
        "replan_delay": replan_delay_out,
        "final_distance_m": final_dist,
        "path_length_m": path,
        "completion_steps": completion,
        "recovery_duration": max(0, completion - response_start),
        "forbidden_violation": violation,
        "successful_resolution": bool(success and not violation and not handover_done),
        "terminal_category": classify(success and not violation, violation, timed_out, handover_done),
        "response_start_step": response_start,
        "branch_replay_ok": True,
        "body_index": body_index,
        "perturbation_id": "P3",
        "occlusion_proxy": "gain_scale_flag_v0.1",
        "occlusion_level": occlusion_level,
        "visibility_fraction": visibility_fraction,
        "visibility_cleared": visibility_cleared,
    }


def main() -> None:
    if not hasattr(args_cli, "device"):
        args_cli.device = "cuda:0"

    out_dir = Path(args_cli.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []

    env_cfg = parse_env_cfg(
        args_cli.task,
        num_envs=args_cli.num_envs,
        use_fabric=not args_cli.disable_fabric,
    )
    if hasattr(env_cfg, "episode_length_s"):
        env_cfg.episode_length_s = float(args_cli.episode_length_s)
    env = gym.make(args_cli.task, cfg=env_cfg)
    robot_name = find_robot_name(env.unwrapped.scene)
    body_index = resolve_ee_body_index(env.unwrapped.scene[robot_name], args_cli.body_index)
    command_name = "ee_1_pose"
    try:
        _ = env.unwrapped.command_manager.get_command(command_name)
    except Exception:
        cm = env.unwrapped.command_manager
        names = list(getattr(cm, "active_terms", []) or [])
        command_name = str(names[0])
        print(f"[WARN] command fallback {command_name}", flush=True)

    forbidden_center = np.array([0.45, 0.0, 0.15], dtype=np.float64)
    forbidden_half = np.array([0.04, 0.04, 0.04], dtype=np.float64)
    mode_list = [m.strip() for m in args_cli.modes.split(",") if m.strip()]

    if str(args_cli.seeds).strip():
        seed_list = [int(x.strip()) for x in str(args_cli.seeds).split(",") if x.strip()]
    else:
        seed_list = [args_cli.seed * 100 + ep for ep in range(args_cli.episodes)]

    print(
        f"[INFO] EXP-SURG-001D modes={mode_list} shift={args_cli.shift_m} "
        f"vis={args_cli.visibility_fraction} replan_d={args_cli.replan_delay}",
        flush=True,
    )

    for seed in seed_list:
        torch.manual_seed(seed)
        env.reset()
        pre_actions: list[torch.Tensor] = []
        for _ in range(args_cli.onset):
            with torch.no_grad():
                act = scripted_action(
                    env, robot_name, command_name, args_cli.gain, body_index, args_cli.max_delta
                )
                pre_actions.append(act.clone())
                env.step(act)

        frozen_xyz = get_command_xyz(env, command_name)
        shift_vec = torch.zeros_like(frozen_xyz)
        shift_vec[:, 1] = args_cli.shift_m
        shifted_xyz = frozen_xyz + shift_vec

        for mode in mode_list:
            torch.manual_seed(seed)
            env.reset()
            result = run_branch(
                env,
                robot_name,
                command_name,
                body_index,
                pre_actions,
                frozen_xyz,
                shifted_xyz,
                mode,
                args_cli.onset,
                args_cli.max_steps,
                args_cli.tol_m,
                args_cli.gain,
                args_cli.max_delta,
                forbidden_center,
                forbidden_half,
                args_cli.replan_delay,
                args_cli.visibility_fraction,
                args_cli.reobserve_hold_steps,
                args_cli.reshape_steps,
                args_cli.occlusion_level,
            )
            result.update(
                {
                    "seed": seed,
                    "episode": seed,
                    "onset_step": args_cli.onset,
                    "shift_distance_m": args_cli.shift_m,
                    "mode": "isaac",
                    "task": args_cli.task,
                    "experiment_id": args_cli.experiment_id,
                }
            )
            records.append(result)
            print(json.dumps(result), flush=True)

    summary = {
        "experiment": args_cli.experiment_id,
        "mode": "isaac",
        "records": records,
        "occlusion_proxy": "gain_scale_flag_v0.1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    out_json = out_dir / "isaac_results.json"
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[INFO] wrote {out_json}")
    env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
