"""EXP-SURG-003 Isaac runner: persistent target drift (M1) for WM expansion pilot.

Extends 001A action-replay pattern with per-step command drift after onset.
Launched via isaaclab.sh (see scripts/run_exp_surg_003_drift_runpod.sh).
"""

from __future__ import annotations

import argparse
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
    get_command_xyz,
    in_forbidden,
    resolve_ee_body_index,
    scripted_action,
    set_command_xyz,
)


def drift_vector(device: torch.device) -> torch.Tensor:
    axis = {"x": 0, "y": 1, "z": 2}[args_cli.drift_axis]
    v = torch.zeros(1, 3, device=device)
    v[:, axis] = args_cli.drift_speed
    return v


def run_drift_episode(
    env: Any,
    robot_name: str,
    command_name: str,
    body_index: int,
    seed: int,
    policy: str,
) -> dict[str, Any]:
    torch.manual_seed(seed)
    env.reset()
    device = env.unwrapped.device
    drift_step = drift_vector(device)
    forbidden_center = np.array([0.45, 0.0, 0.15], dtype=np.float64)
    forbidden_half = np.array([0.04, 0.04, 0.04], dtype=np.float64)

    frozen_xyz = None
    cmd_xyz = None
    path = 0.0
    prev_ee = None
    violation = False
    trajectory: list[dict[str, Any]] = []

    for t in range(args_cli.max_steps):
        if t == args_cli.onset:
            frozen_xyz = get_command_xyz(env, command_name)
            cmd_xyz = frozen_xyz.clone()

        if t >= args_cli.onset and cmd_xyz is not None:
            rel = t - args_cli.onset
            if rel < args_cli.drift_duration:
                cmd_xyz = cmd_xyz + drift_step
            if policy == "TRACK_DRIFTING":
                set_command_xyz(env, command_name, cmd_xyz)
            else:
                set_command_xyz(env, command_name, frozen_xyz)

        with torch.no_grad():
            act = scripted_action(
                env, robot_name, command_name, args_cli.gain, body_index, args_cli.max_delta
            )
            env.step(act)

        dist, ee, des = ee_distance(env, robot_name, command_name, body_index)
        if prev_ee is not None:
            path += float(np.linalg.norm(ee - prev_ee))
        prev_ee = ee
        if in_forbidden(ee, forbidden_center, forbidden_half):
            violation = True

        trajectory.append(
            {
                "t": t,
                "distance_m": dist,
                "ee": ee.tolist(),
                "command": des.tolist(),
                "policy": policy,
            }
        )

        if dist <= args_cli.tol_m and not violation:
            success = True
            completion = t + 1
            break
    else:
        success = False
        completion = args_cli.max_steps

    return {
        "seed": seed,
        "policy": policy,
        "onset_step": args_cli.onset,
        "drift_speed_m_per_step": args_cli.drift_speed,
        "drift_axis": args_cli.drift_axis,
        "drift_duration_steps": args_cli.drift_duration,
        "final_distance_m": dist,
        "path_length_m": path,
        "completion_steps": completion,
        "forbidden_violation": violation,
        "successful_resolution": bool(success and not violation),
        "terminal_category": classify(success and not violation, violation, completion >= args_cli.max_steps),
        "trajectory": trajectory,
        "mode": "isaac",
        "experiment_id": args_cli.experiment_id,
    }


def main() -> None:
    out_dir = Path(args_cli.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

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

    if str(args_cli.seeds).strip():
        seed_list = [int(x.strip()) for x in str(args_cli.seeds).split(",") if x.strip()]
    else:
        seed_list = [args_cli.seed * 100 + ep for ep in range(args_cli.episodes)]

    records = []
    for seed in seed_list:
        for policy in ("TRACK_DRIFTING", "TRACK_FROZEN"):
            rec = run_drift_episode(env, robot_name, command_name, body_index, seed, policy)
            records.append(rec)
            print(json.dumps({k: rec[k] for k in rec if k != "trajectory"}), flush=True)

    summary = {
        "experiment": args_cli.experiment_id,
        "mode": "isaac",
        "n_records": len(records),
        "seeds": seed_list,
        "records": [{k: r[k] for k in r if k != "trajectory"} for r in records],
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "target_dynamics": "persistent_drift",
    }
    out_json = out_dir / "isaac_drift_results.json"
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out_dir / "isaac_drift_trajectories.json").write_text(
        json.dumps(records, indent=2), encoding="utf-8"
    )
    print(f"[INFO] wrote {out_json}")
    env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
