"""Paper 003's commitment cell against a real rigid object.

STATUS: **never run.** The first cell in which the target is a physical body
rather than a point written into a command.

A conflict found on CPU and since resolved, recorded because the diagnosis was
wrong twice before it was right. Eligibility never opened in any cell. It looked
like a sampling problem - contact happens at 2 to 5 mm here while moving the
block needs about 40 mm/step - but the real cause was a confusion between two
different speeds.

`--approach-speed` is what the arm is *commanded*; the arm's achievable speed is
roughly a sixth of it. `EncounterSpec.reference_speed` is the rate at which the
scripted goal point advances, and it must be the achievable speed, or the script
runs away from an arm that cannot follow it. Set to the commanded value it was
3.3 times the interaction radius, so the scripted body stepped clean over the
contact zone every time and the encounter contained no contact to observe.

`EncounterSpec.validate` now refuses a speed at or above the radius, the same
way it already refuses a withdrawal that does not clear it.

What is different from `orbit_reach_relation_pilot.py`:

    reach                     lift
    robot_1, robot_2          robot
    ee_1_frame                ee_frame
    ee_1_pose                 object_pose
    target written each step  target READ from the scene

The last row is the whole point. Under injected coupling the cell computed where
the target should be and told the simulator; contact was arithmetic and the
simulator never resisted. Here the arm is commanded and the object moves because
something pushed it.

Everything that decides anything is in `wm_expansion.cell`, which runs this same
loop on CPU with a fake simulator. This file supplies three callbacks: place the
pushers, step physics, read the object.

The second body is a limitation to state plainly. The scene has one arm, so a
two-body encounter needs a second pusher this scene does not provide;
`--bodies 2` therefore drives the arm to the first body's script and treats the
second as a *virtual* pusher whose contact is injected. That cell is a hybrid
and is labelled as one in the record. The handover task has two arms and an
object, and is the candidate for a fully physical two-body encounter.

Usage:
    /workspace/IsaacLab/isaaclab.sh -p scripts/orbit_lift_relation_cell.py \
        --headless --seed 300 --condition coupled --out-dir results/lift_cells
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
parser.add_argument("--condition", type=str, default="coupled",
                    choices=["coupled", "drift", "static", "noise", "slide"])
parser.add_argument("--episode-steps", type=int, default=90)
parser.add_argument("--bodies", type=int, choices=[1, 2], default=1)
parser.add_argument("--tolerance", type=float, default=0.020,
                    help="metres; the lift task's own object-placement threshold "
                         "from mdp/terminations.py, not a value chosen here")
parser.add_argument("--dispense-latency", type=int, default=6)
parser.add_argument("--interaction-radius", type=float, default=0.012,
                    help="metres; observed contact in this scene is 2-5 mm. The "
                         "50 mm of the injected design marks non-contact as "
                         "contact here")
parser.add_argument("--approach-speed", type=float, default=0.04,
                    help="metres per step the arm is COMMANDED toward the "
                         "scripted point. The arm achieves roughly a sixth of "
                         "this, so it is not the encounter's speed")
parser.add_argument("--script-speed", type=float, default=0.006,
                    help="metres per step the encounter's scripted point "
                         "advances. This must be the arm's ACHIEVABLE speed, "
                         "and below the interaction radius, or the script runs "
                         "away from an arm that cannot follow and the scripted "
                         "body steps over its own contact zone. Passing the "
                         "commanded value here is what left every cell without "
                         "an eligible step")
parser.add_argument("--gripper", type=float, default=-1.0,
                    help="closed. An open gripper straddles the block: the frame "
                         "point reached 0.3 mm from its centre without moving it")
parser.add_argument("--probe-advance", type=int, default=7)
parser.add_argument("--probe-withdraw", type=int, default=5,
                    help="steps of withdrawal. It must clear the interaction "
                         "radius: withdraw * script-speed > radius. With the "
                         "default 5 and a 12 mm radius, no script slower than "
                         "2.4 mm/step is admissible, which is a tight window "
                         "against the ~5 mm/step the arm can actually track")
parser.add_argument("--probe-hold", type=int, default=2)
parser.add_argument("--commit-policy", type=str, default="uniform",
                    choices=["uniform", "first"])
parser.add_argument("--out-dir", type=str, default="results/lift_cells")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import gymnasium as gym  # noqa: E402
import torch  # noqa: E402

import orbit.surgical.tasks  # noqa: E402,F401
from omni.isaac.lab_tasks.utils import parse_env_cfg  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wm_expansion.cell import CellSpec, ContactWorld, run_cell  # noqa: E402
from wm_expansion.commitment_episode import EpisodeSpec  # noqa: E402
from wm_expansion.encounter import EncounterSpec  # noqa: E402


def run(env: Any, args: argparse.Namespace) -> dict[str, Any]:
    env.reset(seed=args.seed)
    scene = env.unwrapped.scene
    inventory = {
        "articulations": sorted(getattr(scene, "articulations", {}).keys()),
        "rigid_objects": sorted(getattr(scene, "rigid_objects", {}).keys()),
        "sensors": sorted(getattr(scene, "sensors", {}).keys()),
    }
    if "object" not in inventory["rigid_objects"]:
        return {"failed": "no rigid object named 'object'", "scene_inventory": inventory}

    def read_object() -> np.ndarray:
        return scene["object"].data.root_pos_w[0].detach().cpu().numpy().astype(np.float64)

    def read_ee() -> np.ndarray:
        return scene["ee_frame"].data.target_pos_w[0, 0].detach().cpu().numpy().astype(np.float64)

    action_dim = env.action_space.shape[-1]
    commanded: list[list[float]] = []
    observed_ee: list[list[float]] = []

    def place(bodies: np.ndarray) -> None:
        """Steer the arm at the first body's scripted position for this step.

        The command is a cartesian delta, so this is a proportional step toward
        the scripted point rather than a teleport - the arm has to get there,
        and whether it does is visible in `ee_error` afterwards.
        """
        place.scripted = np.asarray(bodies, dtype=np.float64)  # type: ignore[attr-defined]
        commanded.append(np.asarray(bodies[0], dtype=np.float64).tolist())
        aim = np.asarray(bodies[0], dtype=np.float64) - read_ee()
        reach = float(np.linalg.norm(aim))
        step = aim if reach <= args.approach_speed else aim / reach * args.approach_speed
        action = torch.zeros((args.num_envs, action_dim), device=env.unwrapped.device)
        action[0, :3] = torch.as_tensor(step, device=action.device, dtype=action.dtype)
        if args.gripper != 0.0 and action_dim >= 4:
            action[0, -1] = float(args.gripper)
        place.pending = action  # type: ignore[attr-defined]

    def step_physics() -> bool:
        action = getattr(place, "pending", None)
        if action is None:
            action = torch.zeros((args.num_envs, action_dim), device=env.unwrapped.device)
        with torch.no_grad():
            _, _, terminated, truncated, _ = env.step(action)
        observed_ee.append(read_ee().tolist())
        return bool(terminated[0]) or bool(truncated[0])

    target0 = read_object()
    record = run_cell(
        target0,
        EpisodeSpec(
            tolerance=args.tolerance,
            dispense_latency=args.dispense_latency,
            interaction_radius=args.interaction_radius,
        ),
        EncounterSpec(
            interaction_radius=args.interaction_radius,
            reference_speed=args.script_speed,
            pusher_speed=args.script_speed,
            probe_advance=args.probe_advance,
            probe_withdraw=args.probe_withdraw,
            probe_hold=args.probe_hold,
            bodies=args.bodies,
        ),
        CellSpec(
            condition=args.condition,
            seed=args.seed,
            episode_steps=args.episode_steps,
            commit_policy=args.commit_policy,
        ),
        # The arm is commanded, not teleported, so the gate must see where it
        # actually got to. With one body that is the end effector itself; the
        # virtual second pusher is reported at its scripted point, which is
        # true of it because nothing physical resists it.
        world=ContactWorld(
            place, step_physics, read_object,
            read_bodies=lambda: (
                read_ee()[None, :]
                if args.bodies == 1
                else np.stack([read_ee(), np.asarray(place.scripted[1])])
            ),
        ),
    )

    # How far the arm actually got from where it was told to be. A cell where
    # this is large is not measuring contact, it is measuring an arm that could
    # not follow the script, and must not be pooled with one that could.
    errors = [
        float(np.linalg.norm(np.asarray(c) - np.asarray(e)))
        for c, e in zip(commanded, observed_ee)
    ]
    record["scene_inventory"] = inventory
    record["commanded_bodies"] = commanded
    record["observed_ee"] = observed_ee
    record["script_speed"] = args.script_speed
    record["approach_speed"] = args.approach_speed
    record["ee_error_median"] = float(np.median(errors)) if errors else None
    record["ee_error_max"] = float(np.max(errors)) if errors else None
    #: A two-body cell here is a hybrid: the scene has one arm, so the second
    #: pusher is virtual and its contact is injected.
    record["contact"] = "physical" if args.bodies == 1 else "hybrid"
    return record


def main() -> None:
    cfg = parse_env_cfg(args_cli.task, num_envs=args_cli.num_envs)
    env = gym.make(args_cli.task, cfg=cfg)
    try:
        record = run(env, args_cli)
    finally:
        env.close()

    out_dir = Path(args_cli.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    name = f"cell_{args_cli.condition}_seed{args_cli.seed}.json"
    (out_dir / name).write_text(json.dumps(record, indent=2))

    lines = [f"wrote {out_dir / name}"]
    if record.get("failed"):
        lines.append(f"FAILED: {record['failed']}")
    else:
        lines.append(
            f"contact={record['contact']}  committed_at={record['committed_at']}  "
            f"valid={record['valid']}  estD={record['d_estimated']}  "
            f"gate={record['gate_fire_rate']:.2f}"
        )
        lines.append(f"resolved: {record['resolved']}")
        lines.append(
            f"ee_error median={1000 * (record['ee_error_median'] or 0):.1f} mm "
            f"max={1000 * (record['ee_error_max'] or 0):.1f} mm  "
            f"(script {1000 * args_cli.script_speed:.1f} mm/step, "
            f"commanded {1000 * args_cli.approach_speed:.1f})"
        )
        # Judged against the interaction radius, not the script speed. An error
        # of half the radius already means the body is not where the script says
        # it is, so the contact geometry the gate reasons about is wrong -
        # regardless of how fast the script happens to be moving. The first real
        # cell had a median error of 9.5 mm against a 12 mm radius and passed a
        # script-speed test, while eligibility never opened.
        if (record["ee_error_median"] or 0) > 0.5 * args_cli.interaction_radius:
            lines.append(
                f"ARM LAGGING - median error "
                f"{1000 * record['ee_error_median']:.1f} mm against a "
                f"{1000 * args_cli.interaction_radius:.1f} mm radius. The body "
                "is not where the script says; lower --script-speed or raise "
                "--approach-speed before reading anything from this cell"
            )
    (out_dir / f"cell_{args_cli.condition}_seed{args_cli.seed}.txt").write_text(
        "\n".join(lines) + "\n"
    )
    print("\n".join(lines))


if __name__ == "__main__":
    main()
    simulation_app.close()
