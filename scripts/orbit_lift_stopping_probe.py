"""Strike the lift task's block and measure how long it keeps moving.

STATUS: never run. This is the measurement Paper 003 waits on.

Why it exists: the relation gate requires the target to stop when the pushing
body leaves. A struck rigid body slides instead, and a constant-velocity model -
Paper 002's operator - explains a slide. Driving the cell through toy contact
physics found the gate firing on **0.00** of steps when the object coasted, and
recovering only when it halted within a step or two. So the design's viability
reduces to a property of this scene:

    how many steps does a struck block take to stop, against a 6-step window?

Everything decidable is in wm_expansion/stopping.py, under test. This file only
drives the arm into the block and records poses.

Usage:
    /workspace/IsaacLab/isaaclab.sh -p scripts/orbit_lift_stopping_probe.py \
        --headless --seed 300 --out-dir results/paper003_stopping
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np

from omni.isaac.lab.app import AppLauncher

parser = argparse.ArgumentParser(description=__doc__)
#: The lift family, not reach: this is the task with a rigid object. The
#: bootstrap used to delete it as "incompatible"; the incompatibility was two
#: lines setting a debug marker's scale.
parser.add_argument("--task", type=str, default="Isaac-Lift-Block-PSM-IK-Rel-Play-v0")
parser.add_argument("--num_envs", type=int, default=1)
parser.add_argument("--seed", type=int, default=300)
parser.add_argument("--episode-steps", type=int, default=90)
parser.add_argument("--approach-speed", type=float, default=0.015,
                    help="metres per step the end effector is driven at")
parser.add_argument("--strike-steps", type=int, default=14,
                    help="steps spent driving into the block before retreating")
parser.add_argument("--retreat-steps", type=int, default=8)
parser.add_argument("--interaction-radius", type=float, default=0.05)
parser.add_argument("--dispense-latency", type=int, default=6)
parser.add_argument("--out-dir", type=str, default="results/paper003_stopping")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import gymnasium as gym  # noqa: E402
import torch  # noqa: E402

import orbit.surgical.tasks  # noqa: E402,F401
from omni.isaac.lab_tasks.utils import parse_env_cfg  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wm_expansion.stopping import estimate_stopping, gate_outlook  # noqa: E402


def run_probe(env: Any, args: argparse.Namespace) -> dict[str, Any]:
    """Drive the end effector into the block, retreat, and record poses."""

    env.reset(seed=args.seed)
    scene = env.unwrapped.scene
    inventory = {
        "articulations": sorted(getattr(scene, "articulations", {}).keys()),
        "rigid_objects": sorted(getattr(scene, "rigid_objects", {}).keys()),
        "sensors": sorted(getattr(scene, "sensors", {}).keys()),
    }
    if "object" not in inventory["rigid_objects"]:
        return {"failed": "no rigid object named 'object'", "scene_inventory": inventory}

    def object_pose() -> np.ndarray:
        return scene["object"].data.root_pos_w[0].detach().cpu().numpy().astype(np.float64)

    def ee_pose() -> np.ndarray:
        frame = scene["ee_frame"]
        return frame.data.target_pos_w[0, 0].detach().cpu().numpy().astype(np.float64)

    start_object = object_pose()
    start_ee = ee_pose()
    heading = start_object - start_ee
    norm = float(np.linalg.norm(heading))
    if norm <= 0.0:
        return {"failed": "end effector starts on top of the object",
                "scene_inventory": inventory}
    heading = heading / norm

    action_dim = env.action_space.shape[-1]
    positions: list[list[float]] = []
    separations: list[float] = []

    for step in range(args.episode_steps):
        obj = object_pose()
        positions.append(obj.tolist())
        separations.append(float(np.linalg.norm(obj - ee_pose())))

        # Relative IK: the first three components are a cartesian delta. Drive
        # into the block, then back out; afterwards hold still so the coast is
        # observed with nothing near it, which is the whole measurement.
        action = torch.zeros((args.num_envs, action_dim), device=env.unwrapped.device)
        if step < args.strike_steps:
            delta = heading * args.approach_speed
        elif step < args.strike_steps + args.retreat_steps:
            delta = -heading * args.approach_speed
        else:
            delta = np.zeros(3)
        action[0, :3] = torch.as_tensor(delta, device=action.device, dtype=action.dtype)

        _, _, terminated, truncated, _ = env.step(action)
        if bool(terminated[0]) or bool(truncated[0]):
            break

    estimate = estimate_stopping(
        positions, separations, args.interaction_radius
    )
    return {
        "task": args.task,
        "seed": args.seed,
        "scene_inventory": inventory,
        "start_object": start_object.tolist(),
        "start_ee": start_ee.tolist(),
        "dispense_latency": args.dispense_latency,
        "stopping": None if estimate is None else estimate.to_dict(),
        "outlook": gate_outlook(estimate, args.dispense_latency),
        "positions": positions,
        "separations": separations,
    }


def main() -> None:
    env_cfg = parse_env_cfg(args_cli.task, num_envs=args_cli.num_envs)
    env = gym.make(args_cli.task, cfg=env_cfg)
    try:
        record = run_probe(env, args_cli)
    finally:
        env.close()

    out_dir = Path(args_cli.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"stopping_seed{args_cli.seed}.json"
    path.write_text(json.dumps(record, indent=2))

    # Written to a file as well as printed: Isaac's app swallows stdout, which
    # cost a diagnostic earlier today.
    summary = out_dir / f"stopping_seed{args_cli.seed}.txt"
    lines = [f"wrote {path}"]
    if record.get("failed"):
        lines.append(f"FAILED: {record['failed']}")
    else:
        lines.append(f"stopping: {json.dumps(record['stopping'])}")
        lines.append(f"outlook : {record['outlook']}")
    summary.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
    simulation_app.close()
