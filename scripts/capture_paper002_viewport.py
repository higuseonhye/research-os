"""Real Isaac Sim viewport capture for Paper 002 figure/portfolio teasers.

STATUS: prepared 2026-07-31, NOT YET RUN OR VALIDATED — no GPU/Isaac Lab
available in the authoring session. Sanity-check output before promoting any
PNG into docs/paper002/figures/ or citing it as a real capture.

Distinct from the frozen confirmatory script (scripts/orbit_reach_drift.py):
this does NOT touch confirmatory logic, seeds, or results. It is a read-only
visualization pass over the same task/environment, replaying the scripted
controller for a handful of steps per arm and saving actual rendered camera
frames (not EE-trace JSON, unlike scripts/capture_study1_viewport.sh).

Usage (VESSL/RunPod, Isaac Sim 4.1 + Isaac Lab):
    ./isaaclab.sh -p scripts/capture_paper002_viewport.py \
        --headless --enable_cameras \
        --capture-dir docs/paper002/figures/isaac_captures \
        --capture-steps 0,20,40,80
"""

from __future__ import annotations

import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--task", type=str, default="Isaac-Reach-Dual-STAR-IK-Rel-Play-v0")
parser.add_argument("--seed", type=int, default=300, help="matches a real confirmatory seed for continuity")
parser.add_argument("--drift-axis", type=str, default="x", choices=["x", "y", "z"])
parser.add_argument("--drift-speed", type=float, default=0.01)
parser.add_argument("--drift-delay", type=int, default=0)
parser.add_argument("--drift-duration", type=int, default=40)
parser.add_argument("--onset", type=int, default=20)
parser.add_argument("--capture-steps", type=str, default="0,20,40,80", help="sim steps at which to save a frame")
parser.add_argument("--capture-dir", type=str, default="docs/paper002/figures/isaac_captures")
parser.add_argument("--gain", type=float, default=1.0)
parser.add_argument("--max-delta", type=float, default=0.08)
parser.add_argument("--disable_fabric", action="store_true", default=False)

from omni.isaac.lab.app import AppLauncher  # noqa: E402

AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()
if not args_cli.enable_cameras:
    raise SystemExit("Pass --enable_cameras — required for viewport capture in headless mode.")

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import gymnasium as gym  # noqa: E402
from omni.isaac.lab_tasks.utils import parse_env_cfg  # noqa: E402
from omni.kit.viewport.utility import capture_viewport_to_file, get_active_viewport  # noqa: E402

from orbit_reach_common import (  # noqa: E402
    find_robot_name,
    get_command_xyz,
    resolve_ee_body_index,
    scripted_action,
    set_command_xyz,
)


def main() -> None:
    capture_dir = Path(args_cli.capture_dir)
    capture_dir.mkdir(parents=True, exist_ok=True)
    capture_steps = {int(s.strip()) for s in str(args_cli.capture_steps).split(",") if s.strip()}

    env_cfg = parse_env_cfg(args_cli.task, num_envs=1, use_fabric=not args_cli.disable_fabric)
    env = gym.make(args_cli.task, cfg=env_cfg)
    try:
        env.reset(seed=args_cli.seed)
        robot_name = find_robot_name(env.unwrapped.scene)
        body_index = resolve_ee_body_index(env.unwrapped.scene[robot_name], -1)
        command_name = "ee_1_pose"
        viewport = get_active_viewport()

        for step in range(max(capture_steps) + 1):
            target_xyz = get_command_xyz(env, command_name)
            if step >= args_cli.onset + args_cli.drift_delay and step < (
                args_cli.onset + args_cli.drift_delay + args_cli.drift_duration
            ):
                axis_index = {"x": 0, "y": 1, "z": 2}[args_cli.drift_axis]
                target_xyz[..., axis_index] += args_cli.drift_speed
                set_command_xyz(env, command_name, target_xyz)

            action = scripted_action(
                env, robot_name, command_name, args_cli.gain, body_index, args_cli.max_delta
            )
            env.step(action)

            if step in capture_steps:
                frame_path = capture_dir / f"seed{args_cli.seed}_step{step:03d}.png"
                capture_viewport_to_file(viewport, str(frame_path))
                print(f"[capture] saved {frame_path}", flush=True)

        manifest_path = capture_dir / "capture_manifest.json"
        manifest_path.write_text(
            (
                '{\n'
                f'  "script": "scripts/capture_paper002_viewport.py",\n'
                f'  "seed": {args_cli.seed},\n'
                f'  "capture_steps": {sorted(capture_steps)},\n'
                f'  "task": "{args_cli.task}",\n'
                '  "note": "Read-only visualization pass, not confirmatory data. '
                'Review every frame before promoting any into docs/paper002/figures/."\n'
                '}\n'
            ),
            encoding="utf-8",
        )
    finally:
        env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
