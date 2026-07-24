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
parser.add_argument(
    "--baseline",
    type=str,
    default="none",
    choices=("none", "b2", "b3"),
    help="External rule baseline (pre-reg v2.0 D2/D3). Overrides --modes.",
)
parser.add_argument("--vis-thresh", type=float, default=0.5, help="B2: visibility threshold")
parser.add_argument("--dist-thresh", type=float, default=0.15, help="B2: EE-to-shifted distance threshold (m)")
parser.add_argument("--dist-check-step", type=int, default=10, help="B2: steps after onset before distance check")
parser.add_argument("--shift-thresh-m", type=float, default=0.06, help="B3: minimum shift for replan/occluded tags")
parser.add_argument("--out-dir", type=str, default="")
parser.add_argument("--capture", action="store_true", help="Save EE traces for figure reproduction")
parser.add_argument("--capture-dir", type=str, default="")
parser.add_argument("--capture-seed", type=int, default=0)
parser.add_argument("--capture-modes", type=str, default="CONTINUE,REPLAN")
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


def probe_shifted_distance_after_continue_steps(
    env: Any,
    robot_name: str,
    command_name: str,
    body_index: int,
    pre_actions: list[torch.Tensor],
    frozen_xyz: torch.Tensor,
    shifted_xyz: torch.Tensor,
    onset: int,
    probe_steps: int,
    gain: float,
    max_delta: float,
    visibility_fraction: float,
) -> float:
    """Replay to S, run probe_steps with frozen target + occluded gain; return dist to shifted target."""
    for act in pre_actions:
        with torch.no_grad():
            env.step(act)
    shifted_target_np = tensor_to_np(shifted_xyz[0])
    for _t in range(probe_steps):
        set_command_xyz(env, command_name, frozen_xyz)
        with torch.no_grad():
            act = scripted_action(
                env,
                robot_name,
                command_name,
                gain,
                body_index,
                max_delta,
                visibility_fraction,
                False,
            )
            env.step(act)
    _, ee, _ = ee_distance(env, robot_name, command_name, body_index)
    return float(np.linalg.norm(ee - shifted_target_np))


def resolve_b2_mode(
    env: Any,
    robot_name: str,
    command_name: str,
    body_index: int,
    pre_actions: list[torch.Tensor],
    frozen_xyz: torch.Tensor,
    shifted_xyz: torch.Tensor,
    onset: int,
    visibility_fraction: float,
    vis_thresh: float,
    dist_thresh: float,
    dist_check_step: int,
    gain: float,
    max_delta: float,
) -> tuple[str, dict[str, Any]]:
    risk = 1 if visibility_fraction < vis_thresh else 0
    dist_m = probe_shifted_distance_after_continue_steps(
        env,
        robot_name,
        command_name,
        body_index,
        pre_actions,
        frozen_xyz,
        shifted_xyz,
        onset,
        dist_check_step,
        gain,
        max_delta,
        visibility_fraction,
    )
    if dist_m > dist_thresh:
        risk = max(risk, 1)
    mode = "HANDOVER" if risk else "CONTINUE"
    meta = {
        "baseline_id": "B2",
        "baseline_rule": "uq_inspired_binary",
        "b2_risk": risk,
        "b2_probe_distance_m": dist_m,
        "b2_vis_thresh": vis_thresh,
        "b2_dist_thresh": dist_thresh,
        "b2_dist_check_step": dist_check_step,
        "resolved_mode": mode,
    }
    return mode, meta


def resolve_b3_mode(
    shift_m: float,
    occlusion_level: int,
    shift_thresh_m: float,
) -> tuple[str, dict[str, Any]]:
    if occlusion_level >= 1 and shift_m >= shift_thresh_m:
        mode = "REOBSERVE"
        tag = "occluded_shift"
    elif shift_m >= shift_thresh_m:
        mode = "REPLAN"
        tag = "shift_only"
    else:
        mode = "CONTINUE"
        tag = "nominal"
    meta = {
        "baseline_id": "B3",
        "baseline_rule": "situation_rule",
        "b3_situation_tag": tag,
        "b3_shift_thresh_m": shift_thresh_m,
        "resolved_mode": mode,
    }
    return mode, meta


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
    ee_trace: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    path = 0.0
    prev_ee = None
    violation = False
    shifted_target_np = tensor_to_np(shifted_xyz[0])
    visibility_cleared = False

    step_idx = 0
    for act in pre_actions:
        with torch.no_grad():
            env.step(act)
        _, ee, _ = ee_distance(env, robot_name, command_name, body_index)
        if ee_trace is not None:
            ee_trace.append({"step": step_idx, "ee": ee.tolist(), "phase": "nominal"})
        if prev_ee is not None:
            path += float(np.linalg.norm(ee - prev_ee))
        prev_ee = ee
        if in_forbidden(ee, forbidden_center, forbidden_half):
            violation = True
        step_idx += 1

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
        if ee_trace is not None:
            ee_trace.append({"step": step_idx, "ee": ee.tolist(), "phase": "post_onset", "dist_shifted_m": final_dist})
        if prev_ee is not None:
            path += float(np.linalg.norm(ee - prev_ee))
        prev_ee = ee
        if in_forbidden(ee, forbidden_center, forbidden_half):
            violation = True
        step_idx += 1

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

    out_dir = Path(args_cli.out_dir or args_cli.capture_dir or "artifacts/study1d_capture")
    out_dir.mkdir(parents=True, exist_ok=True)
    capture_dir = Path(args_cli.capture_dir) if args_cli.capture_dir else out_dir
    capture_modes = {m.strip() for m in str(args_cli.capture_modes).split(",") if m.strip()}
    do_capture = bool(args_cli.capture)
    if do_capture:
        capture_dir.mkdir(parents=True, exist_ok=True)
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
    baseline = str(args_cli.baseline).lower()
    if baseline != "none":
        mode_list: list[str] = []
    else:
        mode_list = [m.strip() for m in args_cli.modes.split(",") if m.strip()]

    if str(args_cli.seeds).strip():
        seed_list = [int(x.strip()) for x in str(args_cli.seeds).split(",") if x.strip()]
    else:
        seed_list = [args_cli.seed * 100 + ep for ep in range(args_cli.episodes)]

    print(
        f"[INFO] EXP-SURG-001D baseline={baseline} modes={mode_list or '(rule)'} "
        f"shift={args_cli.shift_m} vis={args_cli.visibility_fraction} replan_d={args_cli.replan_delay}",
        flush=True,
    )

    for seed in seed_list:
        torch.manual_seed(seed)
        env.reset()
        pre_actions: list[torch.Tensor] = []
        baseline_meta: dict[str, Any] = {}
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

        if baseline == "b2":
            torch.manual_seed(seed)
            env.reset()
            mode, baseline_meta = resolve_b2_mode(
                env,
                robot_name,
                command_name,
                body_index,
                pre_actions,
                frozen_xyz,
                shifted_xyz,
                args_cli.onset,
                args_cli.visibility_fraction,
                args_cli.vis_thresh,
                args_cli.dist_thresh,
                args_cli.dist_check_step,
                args_cli.gain,
                args_cli.max_delta,
            )
            branch_modes = [mode]
        elif baseline == "b3":
            mode, baseline_meta = resolve_b3_mode(
                args_cli.shift_m,
                args_cli.occlusion_level,
                args_cli.shift_thresh_m,
            )
            branch_modes = [mode]
        else:
            branch_modes = mode_list

        for mode in branch_modes:
            torch.manual_seed(seed)
            env.reset()
            ee_trace: list[dict[str, Any]] | None = None
            if do_capture and seed == args_cli.capture_seed and mode in capture_modes:
                ee_trace = []
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
                ee_trace=ee_trace,
            )
            if ee_trace is not None:
                trace_path = capture_dir / f"seed{seed}_{mode}_ee_trace.json"
                trace_payload = {
                    "seed": seed,
                    "mode": mode,
                    "onset_step": args_cli.onset,
                    "shift_m": args_cli.shift_m,
                    "frozen_xyz": tensor_to_np(frozen_xyz[0]).tolist(),
                    "shifted_xyz": tensor_to_np(shifted_xyz[0]).tolist(),
                    "forbidden_center": forbidden_center.tolist(),
                    "forbidden_half": forbidden_half.tolist(),
                    "trace": ee_trace,
                    "terminal": {k: result[k] for k in ("final_distance_m", "successful_resolution", "terminal_category")},
                }
                trace_path.write_text(json.dumps(trace_payload, indent=2), encoding="utf-8")
                print(f"[INFO] capture trace {trace_path}", flush=True)
            result.update(
                {
                    "seed": seed,
                    "episode": seed,
                    "onset_step": args_cli.onset,
                    "shift_distance_m": args_cli.shift_m,
                    "mode": "isaac",
                    "task": args_cli.task,
                    "experiment_id": args_cli.experiment_id,
                    "baseline": baseline,
                }
            )
            result.update(baseline_meta)
            records.append(result)
            print(json.dumps(result), flush=True)

    summary = {
        "experiment": args_cli.experiment_id,
        "mode": "isaac",
        "records": records,
        "occlusion_proxy": "gain_scale_flag_v0.1",
        "baseline": baseline,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    out_json = out_dir / "isaac_results.json"
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[INFO] wrote {out_json}")
    env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
