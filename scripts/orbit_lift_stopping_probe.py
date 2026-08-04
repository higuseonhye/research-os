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
parser.add_argument("--strike-steps", type=int, default=40,
                    help="maximum steps spent driving at the block; the approach "
                         "ends early once the block actually moves")
parser.add_argument("--retreat-steps", type=int, default=10)
parser.add_argument("--strike-motion", type=float, default=0.0005,
                    help="metres of block movement that counts as contact made")
parser.add_argument("--gripper", type=float, default=-1.0,
                    help="value written to the last action element. The first "
                         "run reached 0.3 mm from the block's centre without "
                         "moving it, which is what an open gripper straddling "
                         "it looks like: `ee_frame` is a virtual point, not a "
                         "collision body. -1 closes on most binary-joint "
                         "actions; use 0 to leave the gripper alone")
parser.add_argument("--aim-offset", type=float, default=0.0,
                    help="metres to aim below the block's centre, so a jaw "
                         "rather than the gap between jaws meets it")
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
    #: The end effector's pose every step. Needed because the relation gate
    #: reads both trajectories, and the decisive test is not the toy model's
    #: retention proxy but the real gate run on a real-contact trace.
    ee_positions: list[list[float]] = []
    separations: list[float] = []
    phases: list[str] = []
    struck_at: int | None = None
    #: Settling under gravity happens in the opening steps and is not a strike.
    settle_steps = 6

    for step in range(args.episode_steps):
        obj = object_pose()
        ee = ee_pose()
        positions.append(obj.tolist())
        ee_positions.append(ee.tolist())
        separations.append(float(np.linalg.norm(obj - ee)))
        if (
            struck_at is None
            and step > settle_steps
            and float(np.linalg.norm(obj - np.asarray(positions[-2]))) >= args.strike_motion
        ):
            struck_at = step

        # Relative IK: the first three components are a cartesian delta.
        #
        # The approach is closed-loop rather than a fixed step count, because
        # the first run failed on exactly that. Driving for a fixed 14 steps
        # left the end effector 37.5 mm short, the block never moved, and the
        # probe still produced a stopping time - from a trace with no strike in
        # it. It now steers at the block's *current* pose and keeps going until
        # the block actually moves, so a miss shows up as an approach that never
        # ends rather than as a fast stop.
        aim = obj - np.array([0.0, 0.0, args.aim_offset]) - ee_pose()
        reach = float(np.linalg.norm(aim))
        aim = aim / reach if reach > 0.0 else heading

        if struck_at is None and step < args.strike_steps:
            phase, delta = "approach", aim * args.approach_speed
        elif struck_at is not None and step < struck_at + args.retreat_steps:
            phase, delta = "retreat", -aim * args.approach_speed
        else:
            phase, delta = "hold", np.zeros(3)
        phases.append(phase)

        action = torch.zeros((args.num_envs, action_dim), device=env.unwrapped.device)
        action[0, :3] = torch.as_tensor(delta, device=action.device, dtype=action.dtype)
        if args.gripper != 0.0 and action_dim >= 4:
            action[0, -1] = float(args.gripper)

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
        "struck_at": struck_at,
        "action_dim": int(action_dim),
        "gripper": args.gripper,
        "aim_offset": args.aim_offset,
        "min_separation": float(min(separations)) if separations else None,
        "phases": phases,
        "stopping": None if estimate is None else estimate.to_dict(),
        "outlook": gate_outlook(estimate, args.dispense_latency),
        "positions": positions,
        "ee_positions": ee_positions,
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
        lines.append(f"struck_at: {record['struck_at']}  "
                     f"min_sep: {1000 * (record['min_separation'] or 0):.1f} mm  "
                     f"action_dim: {record['action_dim']}  "
                     f"gripper: {record['gripper']}")
        lines.append(f"stopping: {json.dumps(record['stopping'])}")
        lines.append(f"outlook : {record['outlook']}")
        if record["struck_at"] is None:
            lines.append("NO STRIKE - the end effector never moved the block; "
                         "any stopping time here is meaningless")
    summary.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
    simulation_app.close()
