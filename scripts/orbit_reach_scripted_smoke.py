"""EXP-SURG-001A helper: scripted reach smoke (NO target shift).

Goal: verify EE distance to ee_1_pose decreases under a body-frame P-controller
mapped into the first 6 of 12 IK-Rel action dims.

Run on Isaac host (skip full bootstrap if already done):

  cd /workspace/orbit-surgical
  export OMNI_KIT_ALLOW_ROOT=1
  /workspace/IsaacLab/isaaclab.sh -p /workspace/research-os/scripts/orbit_reach_scripted_smoke.py \\
    --task Isaac-Reach-Dual-STAR-IK-Rel-Play-v0 --num_envs 1 --steps 80 --seed 0 \\
    --out /workspace/research-os/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/artifacts/scripted_reach_smoke.json \\
    --headless
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from omni.isaac.lab.app import AppLauncher

parser = argparse.ArgumentParser(description="Scripted reach smoke (no shift)")
parser.add_argument("--task", type=str, default="Isaac-Reach-Dual-STAR-IK-Rel-Play-v0")
parser.add_argument("--num_envs", type=int, default=1)
parser.add_argument("--steps", type=int, default=150)
parser.add_argument("--seed", type=int, default=0)
parser.add_argument("--gain", type=float, default=1.0)
parser.add_argument("--max-delta", type=float, default=0.08, help="Per-step Cartesian clip (m / rad)")
parser.add_argument("--tol-m", type=float, default=0.02, help="Stop early when distance <= tol")
parser.add_argument("--episode-length-s", type=float, default=20.0, help="Override env episode horizon")
parser.add_argument("--body-index", type=int, default=-1, help="-1 = endo360_needle (typically 13)")
parser.add_argument("--out", type=Path, required=True)
parser.add_argument("--disable_fabric", action="store_true", default=False)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import gymnasium as gym
import torch
from omni.isaac.lab.utils.math import combine_frame_transforms, quat_apply, quat_inv
from omni.isaac.lab_tasks.utils import parse_env_cfg

import omni.isaac.lab_tasks  # noqa: F401
import orbit.surgical.tasks  # noqa: F401


def find_robot_name(scene: Any) -> str:
    for cand in ("robot_1", "robot", "star", "dual_star"):
        try:
            _ = scene[cand]
            return cand
        except Exception:
            continue
    return str(next(iter(scene.keys())))


def resolve_body_index(asset: Any, preferred: int) -> int:
    """Reach tracks endo360_needle (13); star_link_ee (9) is secondary."""
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


def scripted_ik_rel_action(
    env: Any,
    robot_name: str,
    command_name: str,
    body_index: int,
    gain: float,
    max_delta: float,
) -> tuple[torch.Tensor, float]:
    """Body-frame pose error → arm1 6D (xyz + axis-angle), arm2 zeros."""
    from omni.isaac.lab.utils.math import axis_angle_from_quat, quat_mul

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
    dist = float(torch.norm(err_world, dim=-1).mean().item())

    delta_pos = torch.clamp(gain * err_body, -max_delta, max_delta)
    q_err = quat_mul(desired_quat_world, quat_inv(current_quat_world))
    delta_rot = torch.clamp(gain * axis_angle_from_quat(q_err), -max_delta, max_delta)

    action = torch.zeros(env.action_space.shape, device=device)
    action[..., 0:3] = delta_pos
    action[..., 3:6] = delta_rot
    return action, dist


def main() -> None:
    if not hasattr(args_cli, "device"):
        args_cli.device = "cuda:0"

    env_cfg = parse_env_cfg(
        args_cli.task,
        num_envs=args_cli.num_envs,
        use_fabric=not args_cli.disable_fabric,
    )
    # Default Reach PLAY horizon is ~5s (~150 steps @ 30Hz). Longer control needs a longer episode.
    if hasattr(env_cfg, "episode_length_s"):
        env_cfg.episode_length_s = float(args_cli.episode_length_s)
    env = gym.make(args_cli.task, cfg=env_cfg)
    base = env.unwrapped
    robot_name = find_robot_name(base.scene)
    asset = base.scene[robot_name]
    body_index = resolve_body_index(asset, args_cli.body_index)
    command_name = "ee_1_pose"
    try:
        _ = base.command_manager.get_command(command_name)
    except Exception:
        names = list(getattr(base.command_manager, "active_terms", []) or [])
        command_name = str(names[0])

    print(
        f"[INFO] robot={robot_name} body_index={body_index} "
        f"command={command_name} action_shape={tuple(env.action_space.shape)} "
        f"episode_length_s={getattr(env_cfg, 'episode_length_s', None)}",
        flush=True,
    )

    torch.manual_seed(args_cli.seed)
    env.reset()

    # freeze initial command
    frozen = base.command_manager.get_command(command_name).clone()

    history: list[dict[str, float]] = []
    min_dist = float("inf")
    min_step = -1
    reached = False
    reset_seen = False
    for step in range(args_cli.steps):
        base.command_manager.get_command(command_name)[:] = frozen
        with torch.no_grad():
            action, dist = scripted_ik_rel_action(
                env, robot_name, command_name, body_index, args_cli.gain, args_cli.max_delta
            )
            _obs, _rew, terminated, truncated, _info = env.step(action)
        history.append({"step": float(step), "distance_m": dist})
        if dist < min_dist:
            min_dist = dist
            min_step = step
        if step % 10 == 0 or step == args_cli.steps - 1:
            print(f"[step {step:03d}] distance_m={dist:.4f}", flush=True)
        if dist <= args_cli.tol_m:
            reached = True
            print(f"[PASS] reached tol={args_cli.tol_m} at step={step} dist={dist:.4f}", flush=True)
            break
        if tensor_flag_local(terminated) or tensor_flag_local(truncated):
            reset_seen = True
            print(
                f"[WARN] env terminated/truncated at step={step} dist={dist:.4f} "
                f"(episode horizon). min_dist={min_dist:.4f} at step={min_step}",
                flush=True,
            )
            break

    d0 = history[0]["distance_m"]
    d1 = history[-1]["distance_m"]
    improved = min_dist < d0 - 0.01
    report = {
        "experiment_id": "EXP-SURG-001A-scripted-smoke",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "task": args_cli.task,
        "robot_name": robot_name,
        "body_index": body_index,
        "command_name": command_name,
        "gain": args_cli.gain,
        "max_delta": args_cli.max_delta,
        "episode_length_s": getattr(env_cfg, "episode_length_s", None),
        "distance_start_m": d0,
        "distance_end_m": d1,
        "distance_min_m": min_dist,
        "distance_min_step": min_step,
        "reached_tol": reached,
        "tol_m": args_cli.tol_m,
        "env_reset_or_timeout": reset_seen,
        "improved": improved,
        "pass_criterion": f"min_distance <= {args_cli.tol_m} (ignore post-timeout end distance)",
        "history_every_10": history[::10] + ([history[-1]] if history[-1] not in history[::10] else []),
    }
    args_cli.out.parent.mkdir(parents=True, exist_ok=True)
    args_cli.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                k: report[k]
                for k in (
                    "distance_start_m",
                    "distance_min_m",
                    "distance_min_step",
                    "distance_end_m",
                    "reached_tol",
                    "env_reset_or_timeout",
                )
            },
            indent=2,
        ),
        flush=True,
    )
    print(f"[INFO] wrote {args_cli.out}", flush=True)
    env.close()


def tensor_flag_local(value: object) -> bool:
    if torch.is_tensor(value):
        if value.dtype == torch.bool:
            return bool(value.any().item())
        return bool((value != 0).any().item())
    return bool(value)


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
