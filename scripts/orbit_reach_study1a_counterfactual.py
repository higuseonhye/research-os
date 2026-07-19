"""EXP-SURG-001A Isaac runner: counterfactual CONTINUE vs REPLAN after target shift.

Launched via isaaclab.sh (see scripts/run_study1a_counterfactual_runpod.sh).

Branching method: deterministic action replay to onset, then diverge responses.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from omni.isaac.lab.app import AppLauncher

parser = argparse.ArgumentParser(description="EXP-SURG-001A counterfactual Isaac runner")
parser.add_argument("--task", type=str, default="Isaac-Reach-Dual-STAR-IK-Rel-Play-v0")
parser.add_argument("--num_envs", type=int, default=1)
parser.add_argument("--seed", type=int, default=0)
parser.add_argument(
    "--seeds",
    type=str,
    default="",
    help="Comma-separated seeds (e.g. 0,1,2). If set, overrides --episodes loop.",
)
parser.add_argument("--experiment-id", type=str, default="EXP-SURG-001A")
parser.add_argument("--episodes", type=int, default=5)
parser.add_argument("--onset", type=int, default=20)
parser.add_argument("--max-steps", type=int, default=160)
parser.add_argument("--shift-m", type=float, default=0.03)
parser.add_argument("--tol-m", type=float, default=0.02)
parser.add_argument("--gain", type=float, default=1.0)
parser.add_argument("--max-delta", type=float, default=0.08, help="Per-step Cartesian clip for IK-Rel")
parser.add_argument("--episode-length-s", type=float, default=20.0, help="Override env episode horizon")
parser.add_argument(
    "--body-index",
    type=int,
    default=-1,
    help="EE body index on robot_1; -1 = endo360_needle (task track body, typically 13)",
)
parser.add_argument(
    "--include-continue",
    action=argparse.BooleanOptionalAction,
    default=True,
    help="Include CONTINUE branch (chase frozen target after onset)",
)
parser.add_argument(
    "--replan-delays",
    type=str,
    default="0",
    help="Comma-separated delays (steps after onset) before switching to shifted target. "
    "001A: '0'. 001B timing curve: '0,5,10,20'.",
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


def tensor_mean(value: object) -> float:
    if torch.is_tensor(value):
        if value.dtype == torch.bool:
            return float(value.float().mean().item())
        return float(value.mean().item())
    return float(value)


def tensor_flag(value: object) -> bool:
    """True if any element is true (works for bool / float tensors and scalars)."""
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
    # fallback first key
    try:
        return str(next(iter(scene.keys())))
    except Exception:
        return "robot"


def resolve_ee_body_index(asset: Any, preferred: int = -1) -> int:
    """Reach reward tracks endo360_needle (13); star_link_ee (9) is a secondary candidate."""
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
) -> torch.Tensor:
    """Body-frame P-control → arm1 6D IK-Rel (xyz + axis-angle); arm2 hold."""
    from omni.isaac.lab.utils.math import (
        axis_angle_from_quat,
        quat_apply,
        quat_inv,
        quat_mul,
    )

    base = env.unwrapped
    device = base.device
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

    err_world = desired_pos_world - current_pos_world
    err_body = quat_apply(quat_inv(root_quat), err_world)
    delta_pos = torch.clamp(gain * err_body, -max_delta, max_delta)

    # orientation error as axis-angle (pose_rel convention)
    q_err = quat_mul(desired_quat_world, quat_inv(current_quat_world))
    delta_rot = torch.clamp(gain * axis_angle_from_quat(q_err), -max_delta, max_delta)

    action = torch.zeros(env.action_space.shape, device=device)
    action[..., 0:3] = delta_pos
    action[..., 3:6] = delta_rot
    return action


def in_forbidden(ee_world: np.ndarray, center: np.ndarray, half: np.ndarray) -> bool:
    return bool(np.all(np.abs(ee_world - center) <= half))


def classify(success: bool, violation: bool, timed_out: bool) -> str:
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
    response: str,
    onset: int,
    max_steps: int,
    tol: float,
    gain: float,
    max_delta: float,
    forbidden_center: np.ndarray,
    forbidden_half: np.ndarray,
    replan_delay: int = 0,
) -> dict[str, Any]:
    """Reset already done; replay pre_actions then apply response policy.

    CONTINUE: chase frozen target after onset.
    REPLAN_*: chase frozen for ``replan_delay`` steps after onset, then shifted target.
    """
    path = 0.0
    prev_ee = None
    violation = False
    shifted_target_np = tensor_to_np(shifted_xyz[0])
    is_continue = response == "CONTINUE"
    switch_step = onset if is_continue else onset + max(0, int(replan_delay))

    # ensure we start from same command trajectory as recording
    for t, act in enumerate(pre_actions):
        with torch.no_grad():
            env.step(act)
        _, ee, _ = ee_distance(env, robot_name, command_name, body_index)
        if prev_ee is not None:
            path += float(np.linalg.norm(ee - prev_ee))
        prev_ee = ee
        if in_forbidden(ee, forbidden_center, forbidden_half):
            violation = True

    response_start = switch_step
    final_dist = 999.0
    completion = max_steps
    success = False

    for t in range(onset, max_steps):
        # pin command: CONTINUE always frozen; REPLAN switches at onset+delay
        if is_continue or t < switch_step:
            set_command_xyz(env, command_name, frozen_xyz)
        else:
            set_command_xyz(env, command_name, shifted_xyz)

        with torch.no_grad():
            act = scripted_action(env, robot_name, command_name, gain, body_index, max_delta)
            obs, reward, terminated, truncated, info = env.step(act)

        dist, ee, des = ee_distance(env, robot_name, command_name, body_index)
        # distance to SHIFTED target (not frozen)
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

    return {
        "response": response,
        "replan_delay": None if is_continue else int(replan_delay),
        "final_distance_m": final_dist,
        "path_length_m": path,
        "completion_steps": completion,
        "recovery_duration": max(0, completion - response_start),
        "forbidden_violation": violation,
        "successful_resolution": bool(success and not violation),
        "terminal_category": classify(success and not violation, violation, completion >= max_steps),
        "response_start_step": response_start,
        "branch_replay_ok": True,
        "body_index": body_index,
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
    # Reach PLAY default ~5s (~150 steps). Counterfactual needs room after onset.
    if hasattr(env_cfg, "episode_length_s"):
        env_cfg.episode_length_s = float(args_cli.episode_length_s)
    env = gym.make(args_cli.task, cfg=env_cfg)
    robot_name = find_robot_name(env.unwrapped.scene)
    body_index = resolve_ee_body_index(env.unwrapped.scene[robot_name], args_cli.body_index)
    command_name = "ee_1_pose"
    # try resolve command name
    try:
        _ = env.unwrapped.command_manager.get_command(command_name)
    except Exception:
        # probe first available
        cm = env.unwrapped.command_manager
        names = list(getattr(cm, "active_terms", []) or [])
        if not names:
            raise RuntimeError("No command terms found for target shift")
        command_name = str(names[0])
        print(f"[WARN] falling back to command term {command_name}")

    forbidden_center = np.array([0.45, 0.0, 0.15], dtype=np.float64)
    forbidden_half = np.array([0.04, 0.04, 0.04], dtype=np.float64)

    print(
        f"[INFO] task={args_cli.task} robot={robot_name} body_index={body_index} "
        f"command={command_name} max_delta={args_cli.max_delta} "
        f"experiment={args_cli.experiment_id} replan_delays={args_cli.replan_delays} "
        f"include_continue={args_cli.include_continue}",
        flush=True,
    )

    delays = [int(x.strip()) for x in str(args_cli.replan_delays).split(",") if x.strip() != ""]
    if not delays and not args_cli.include_continue:
        raise RuntimeError("No branches requested: set --include-continue and/or --replan-delays")

    if str(args_cli.seeds).strip():
        seed_list = [int(x.strip()) for x in str(args_cli.seeds).split(",") if x.strip() != ""]
    else:
        seed_list = [args_cli.seed * 100 + ep for ep in range(args_cli.episodes)]

    for seed in seed_list:
        torch.manual_seed(seed)
        obs, _ = env.reset()

        pre_actions: list[torch.Tensor] = []
        frozen_xyz = None
        shifted_xyz = None

        # Phase A: run to onset, record actions, then shift
        for t in range(args_cli.onset):
            with torch.no_grad():
                act = scripted_action(
                    env, robot_name, command_name, args_cli.gain, body_index, args_cli.max_delta
                )
                pre_actions.append(act.clone())
                env.step(act)

        frozen_xyz = get_command_xyz(env, command_name)
        shift_vec = torch.zeros_like(frozen_xyz)
        shift_vec[:, 1] = args_cli.shift_m  # +Y
        shifted_xyz = frozen_xyz + shift_vec

        # CONTINUE once per seed; REPLAN for each delay (001C dedupe)
        branches: list[tuple[str, int | None]] = []
        if args_cli.include_continue:
            branches.append(("CONTINUE", None))
        for d in delays:
            branches.append((f"REPLAN_d{d}", d))

        for response, delay in branches:
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
                response,
                args_cli.onset,
                args_cli.max_steps,
                args_cli.tol_m,
                args_cli.gain,
                args_cli.max_delta,
                forbidden_center,
                forbidden_half,
                replan_delay=0 if delay is None else int(delay),
            )
            result.update(
                {
                    "seed": seed,
                    "episode": seed,
                    "onset_step": args_cli.onset,
                    "shift_distance_m": args_cli.shift_m,
                    "mode": "isaac",
                    "task": args_cli.task,
                    "robot_name": robot_name,
                    "command_name": command_name,
                    "body_index": body_index,
                    "experiment_id": args_cli.experiment_id,
                    "branch_replay_ok": True,
                }
            )
            records.append(result)
            print(json.dumps(result), flush=True)

    summary = {
        "experiment": args_cli.experiment_id,
        "mode": "isaac",
        "task": args_cli.task,
        "n_records": len(records),
        "seeds": seed_list,
        "replan_delays": delays,
        "include_continue": bool(args_cli.include_continue),
        "shift_m": args_cli.shift_m,
        "records": records,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "branch_method": "action_replay_to_onset_then_diverge",
    }
    out_json = out_dir / "isaac_results.json"
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    # also CSV-ish lines
    lines = [
        "seed,episode,response,replan_delay,successful_resolution,final_distance_m,"
        "forbidden_violation,terminal_category,completion_steps,response_start_step,branch_replay_ok"
    ]
    for r in records:
        delay = r.get("replan_delay")
        delay_s = "" if delay is None else str(delay)
        lines.append(
            f"{r['seed']},{r['episode']},{r['response']},{delay_s},{int(r['successful_resolution'])},"
            f"{r['final_distance_m']:.6f},{int(r['forbidden_violation'])},{r['terminal_category']},"
            f"{r['completion_steps']},{r['response_start_step']},{int(r['branch_replay_ok'])}"
        )
    (out_dir / "isaac_results.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[INFO] wrote {out_json}")
    env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
