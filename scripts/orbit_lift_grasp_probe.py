"""What grasp does this scene actually support? Measure it, do not assume it.

The capture pilot cannot produce a carry. With the encounter aimed at the
block's centre and the gripper closing at the true closest approach after 15
steps of genuine approach, the block is still ejected - 72 mm in one 0.02 s
step. Two explanations remain and the pilot cannot separate them:

    the gripper cannot take hold of this block at all
    the gripper could, but 9.7 mm of misalignment is too much

9.7 mm is not a tuning failure. It is the IK controller's steady-state tracking
error while following a moving script, and it does not go away by slowing the
script - measured, 7.5 mm at 2 mm/step and 7.7 mm at 2.5.

So this takes the script away. The arm is servoed to the block's centre with
nothing else happening, held until it converges, and only then does the gripper
close. Whatever separation it reaches is the best this scene can offer, and what
happens at that separation is the scene's answer rather than the encounter's.

Three things come out, in the order they decide anything:

    1. how close the end effector can actually get, standing still
    2. at that separation, does closing hold the block or throw it
    3. if it holds, does the block ride when the arm then moves

Only the third is a capture. `--close-at` closes at a chosen separation instead
of the closest, so a sweep over it maps where holding turns into throwing - the
capture radius the preregistration lists as PENDING and as a physical property
of the scene.

    isaaclab.sh -p scripts/orbit_lift_grasp_probe.py --headless
    isaaclab.sh -p scripts/orbit_lift_grasp_probe.py --headless --close-at 0.004
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

from omni.isaac.lab.app import AppLauncher

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--task", type=str, default="Isaac-Lift-Block-PSM-IK-Rel-Play-v0")
parser.add_argument("--num_envs", type=int, default=1)
parser.add_argument("--seed", type=int, default=300)
parser.add_argument("--seeds", type=int, default=1)
parser.add_argument("--settle", type=int, default=30,
                    help="steps of physics with no action before anything is read")
parser.add_argument("--servo", type=int, default=400,
                    help="steps allowed to bring the end effector onto the block. "
                         "Generous on purpose: this is measuring the best the "
                         "scene can do, not what it can do quickly")
parser.add_argument("--servo-tolerance", type=float, default=0.0005,
                    help="metres; converged when the separation stops improving "
                         "by more than this over --servo-patience steps")
parser.add_argument("--servo-patience", type=int, default=25)
parser.add_argument("--approach-speed", type=float, default=0.04)
parser.add_argument("--close-at", type=float, default=-1.0,
                    help="metres; close the gripper at this separation instead of "
                         "at the closest the arm can reach. A sweep over this "
                         "maps where holding turns into throwing")
parser.add_argument("--hold", type=int, default=20,
                    help="steps to hold still after closing. An ejection shows "
                         "here, before the arm has moved at all")
parser.add_argument("--carry", type=int, default=60,
                    help="steps of burst motion after the hold, to see whether "
                         "the block rides")
parser.add_argument("--carry-speed", type=float, default=0.002)
parser.add_argument("--burst-on", type=int, default=10)
parser.add_argument("--burst-off", type=int, default=4)
parser.add_argument("--gripper-open", type=float, default=1.0)
parser.add_argument("--gripper-close", type=float, default=-1.0)
parser.add_argument("--out-dir", type=str, default="results/paper003_grasp_probe")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()
args_cli.headless = True
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import gymnasium as gym  # noqa: E402
import torch  # noqa: E402
from omni.isaac.lab_tasks.utils import parse_env_cfg  # noqa: E402
import orbit.surgical.tasks  # noqa: E402,F401

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wm_expansion.relation_dynamics import carriage_evidence  # noqa: E402


def run(env: Any, args: argparse.Namespace) -> dict[str, Any]:
    env.reset(seed=args.seed)
    scene = env.unwrapped.scene
    if "object" not in sorted(getattr(scene, "rigid_objects", {})):
        return {"failed": "no rigid object named 'object'"}

    device = env.unwrapped.device
    action_dim = env.action_space.shape[-1]

    def block() -> np.ndarray:
        return scene["object"].data.root_pos_w[0].detach().cpu().numpy().astype(np.float64)

    def ee() -> np.ndarray:
        return scene["ee_frame"].data.target_pos_w[0, 0].detach().cpu().numpy().astype(np.float64)

    def step(delta: np.ndarray | None, gripper: float) -> None:
        action = torch.zeros((args.num_envs, action_dim), device=device)
        if delta is not None:
            action[0, :3] = torch.as_tensor(delta, device=device, dtype=action.dtype)
        if action_dim >= 4:
            action[0, -1] = float(gripper)
        with torch.no_grad():
            env.step(action)

    for _ in range(args.settle):
        step(None, args.gripper_open)
    block0 = block()

    # 1. How close can it get, with nothing else happening.
    separations: list[float] = []
    best, since_improved, closed_at = float("inf"), 0, None
    for index in range(args.servo):
        gap = block() - ee()
        separation = float(np.linalg.norm(gap))
        separations.append(separation)
        if args.close_at > 0.0 and separation <= args.close_at:
            closed_at = separation
            break
        if separation < best - args.servo_tolerance:
            best, since_improved = separation, 0
        else:
            since_improved += 1
            if since_improved >= args.servo_patience:
                closed_at = separation
                break
        reach = separation
        move = gap if reach <= args.approach_speed else gap / reach * args.approach_speed
        step(move, args.gripper_open)
    if closed_at is None:
        closed_at = float(np.linalg.norm(block() - ee()))

    before_close = block()

    # 2. Close, and hold still. An ejection shows here, before anything moves.
    hold_positions = []
    for _ in range(args.hold):
        step(None, args.gripper_close)
        hold_positions.append(block().tolist())
    after_hold = block()
    hold_travel = float(np.linalg.norm(after_hold - before_close))
    hold_steps = np.linalg.norm(np.diff(np.asarray(hold_positions), axis=0), axis=1)
    hold_max_step = float(np.max(hold_steps)) if len(hold_steps) else 0.0

    # 3. Move, and see whether the block comes.
    axis = np.array([1.0, 0.0, 0.0])
    targets, bodies = [], []
    for index in range(args.carry):
        moving = (index % (args.burst_on + args.burst_off)) < args.burst_on
        step(args.carry_speed * axis if moving else None, args.gripper_close)
        targets.append(block().tolist())
        bodies.append([ee().tolist()])
    agreement, run_length = carriage_evidence(targets, bodies)
    carried = float(np.linalg.norm(np.asarray(targets[-1]) - after_hold))

    if hold_max_step > 0.010:
        verdict = "ejected"
        reason = f"the block left at {1000 * hold_max_step:.1f} mm in one step on closing"
    elif run_length >= 3 and agreement >= 0.80:
        verdict = "held_and_carried"
        reason = f"rode the arm for {run_length} consecutive steps"
    elif hold_travel <= 0.002:
        verdict = "held_not_carried"
        reason = "stayed put on closing, but did not follow the arm"
    else:
        verdict = "nudged"
        reason = f"moved {1000 * hold_travel:.1f} mm without riding"

    return {
        "seed": args.seed,
        "settled_block": block0.tolist(),
        "closest_reachable": float(np.min(separations)) if separations else None,
        "servo_steps": len(separations),
        "closed_at": closed_at,
        "close_at_requested": args.close_at if args.close_at > 0.0 else None,
        "hold_travel": hold_travel,
        "hold_max_step": hold_max_step,
        "carry_travel": carried,
        "carriage_agreement": float(agreement),
        "carriage_run": int(run_length),
        "verdict": verdict,
        "reason": reason,
    }


def main() -> None:
    cfg = parse_env_cfg(args_cli.task, num_envs=args_cli.num_envs)
    env = gym.make(args_cli.task, cfg=cfg)
    out_dir = Path(args_cli.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    first = args_cli.seed
    try:
        for index in range(max(1, args_cli.seeds)):
            args_cli.seed = first + index
            record = run(env, args_cli)
            rows.append(record)
            name = (f"grasp_seed{args_cli.seed}"
                    + (f"_at{args_cli.close_at:.4f}" if args_cli.close_at > 0 else "")
                    + ".json")
            (out_dir / name).write_text(json.dumps(record, indent=2))
            if record.get("failed"):
                print(f"seed {args_cli.seed}: FAILED {record['failed']}")
                continue
            print(
                f"seed {args_cli.seed}: closest "
                f"{1000 * (record['closest_reachable'] or 0):.2f} mm | closed at "
                f"{1000 * record['closed_at']:.2f} mm | hold max step "
                f"{1000 * record['hold_max_step']:.2f} mm | carry "
                f"{1000 * record['carry_travel']:.1f} mm | run "
                f"{record['carriage_run']} | {record['verdict'].upper()} "
                f"({record['reason']})"
            )
    finally:
        args_cli.seed = first
        env.close()

    good = [r for r in rows if not r.get("failed")]
    if len(good) > 1:
        from collections import Counter
        counts = Counter(r["verdict"] for r in good)
        print("\n" + "  ".join(f"{k} {v}" for k, v in counts.most_common()))
        print(f"closest reachable, median: "
              f"{1000 * float(np.median([r['closest_reachable'] for r in good])):.2f} mm")


if __name__ == "__main__":
    main()
    simulation_app.close()
