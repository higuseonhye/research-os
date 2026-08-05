"""Paper 003's commitment cell against a real rigid object.

STATUS: **never run.** The first cell in which the target is a physical body
rather than a point written into a command.

A conflict found on CPU and since resolved, recorded because the diagnosis was
wrong twice before it was right. Eligibility never opened in any cell. It looked
like a sampling problem - contact happens at 2 to 5 mm here while moving the
block needs about 40 mm/step - but the real cause was a confusion between two
different speeds.

`--approach-speed` is what the arm is *commanded*; `EncounterSpec.reference_speed`
is the rate at which the scripted goal point advances, and it must be the
achievable speed, or the script runs away from an arm that cannot follow it.

**"Roughly a sixth of the commanded value" was wrong**, and the first GPU pilot
is what showed it. Doubling the command from 40 to 80 mm/step changed nothing at
all - identical tracking error to the millimetre - because the arm saturates at
its own limit, measured here at **2.8 to 3.3 mm/step** whatever it is told. The
command is not the lever; the script speed is. That claim could not have been
checked on CPU, where there is no command and no arm.

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
parser.add_argument("--seeds", type=int, default=1,
                    help="how many consecutive seeds to run from --seed, "
                         "in ONE Isaac launch. The simulator's startup "
                         "dominates a single cell, so a 40-cell sweep was "
                         "40 launches before this. 1 is the old behaviour")
parser.add_argument("--condition", type=str, default="coupled",
                    choices=["coupled", "drift", "static", "noise", "slide"])
parser.add_argument("--episode-steps", type=int, default=90)
parser.add_argument("--bodies", type=int, choices=[1, 2], default=1)
parser.add_argument("--tolerance", type=float, default=0.020,
                    help="metres; the lift task's own object-placement threshold "
                         "from mdp/terminations.py, not a value chosen here")
parser.add_argument("--dispense-latency", type=int, default=None,
                    help="defaults to EpisodeSpec's value, which is derived from "
                         "this scene: ceil(20 mm tolerance / 2.86 mm carried per "
                         "step) = 8. It was hard-coded to 6 here, which silently "
                         "measured a task the scene cannot pose - six steps leave "
                         "the target inside tolerance and every arm is right. The "
                         "default is resolved after the Isaac imports, since "
                         "nothing from the project is importable before them")
parser.add_argument("--interaction-radius", type=float, default=0.012,
                    help="metres; observed contact in this scene is 2-5 mm. The "
                         "50 mm of the injected design marks non-contact as "
                         "contact here")
parser.add_argument("--approach-speed", type=float, default=0.04,
                    help="metres per step the arm is COMMANDED toward the "
                         "scripted point. Raising it does NOT make the arm "
                         "faster - measured, 40 and 80 gave identical tracking "
                         "to the millimetre, because the arm saturates near "
                         "3 mm/step. Set --script-speed below that instead")
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
                         "point reached 0.3 mm from its centre without moving it. "
                         "Ignored when --grasp is set, which schedules it")
parser.add_argument("--grasp", action="store_true",
                    help="produce a CAPTURE rather than a collision: approach "
                         "with the gripper OPEN, close it at the closest "
                         "approach to the block, and keep it closed. Also aims "
                         "the encounter at the block's centre rather than up to "
                         "6 mm off it, because a grasp is a rendezvous and a "
                         "jaw closing off-centre ejects the block. "
                         "This is the whole capture relation, physically. The "
                         "straddling that made an open gripper useless for a "
                         "push probe - the frame point reached 0.3 mm from the "
                         "block's centre without moving it - is exactly what "
                         "capture needs: the target must be *perfectly* still "
                         "before the arrival, or its own history carries "
                         "information and the single-entity arm has something "
                         "to learn from. Closing then takes hold, and the block "
                         "rides. Nothing before, everything after")
parser.add_argument("--approach", type=str, default="script",
                    choices=["script", "servo"],
                    help="`script` chases the encounter's scripted point, "
                         "which cannot produce a capture here: the arm's "
                         "steady-state error is 7.3 mm against a measured "
                         "capture radius under 1 mm. `servo` goes to the "
                         "object until it takes hold, then carries along "
                         "the drawn axis on the burst schedule")
parser.add_argument("--grasp-closing-steps", type=int, default=4,
                    help="consecutive steps of genuine approach required "
                         "before a halt counts as an arrival. Without it "
                         "the gripper closed on step 1, because the first "
                         "separation always improves on an infinite "
                         "initial best and the second barely moved")
parser.add_argument("--grasp-epsilon", type=float, default=0.0002,
                    help="metres of decrease that still counts as approaching. "
                         "Below this the separation is treated as no longer "
                         "closing, which is the arrival")
parser.add_argument("--grasp-radius", type=float, default=0.030,
                    help="metres. No longer the trigger - the gripper closes at "
                         "the closest approach - but a sanity bound on it, so a "
                         "pass that never got near the block cannot be read as "
                         "an arrival. Deliberately loose. Arm D does not receive "
                         "the capture radius either way; it estimates it from "
                         "the observed onset, the same refusal "
                         "`estimate_coupling` makes")
parser.add_argument("--gripper-open", type=float, default=1.0)
parser.add_argument("--gripper-close", type=float, default=-1.0)
parser.add_argument("--schedule", type=str, default="probe",
                    choices=["probe", "burst"],
                    help="`burst` only ever advances and is what capture is "
                         "paired with: a body that arrives and carries the "
                         "target off has no reason to withdraw. `probe` "
                         "withdraws, which under capture drags the captured "
                         "block back and breaks the pattern estimator")
parser.add_argument("--burst-on", type=int, default=10)
parser.add_argument("--burst-off", type=int, default=4)
parser.add_argument("--preroll", type=int, default=160,
                    help="steps allowed to bring the arm to the encounter's "
                         "first point BEFORE the episode starts. The arm begins "
                         "wherever the scene resets it - a fixed 50.2 mm from "
                         "the script's start in the first pilot, at every speed "
                         "tried - and those steps are travel to the start line, "
                         "not tracking. 0 disables it")
parser.add_argument("--settle", type=int, default=30,
                    help="steps of physics with no action before anything is "
                         "read, so the block's own settling after reset is not "
                         "attributed to the arm and does not enter the encounter "
                         "geometry as a stale position")
parser.add_argument("--preroll-tolerance", type=float, default=0.003,
                    help="metres; how close is close enough to start")
parser.add_argument("--preroll-clearance", type=float, default=0.0,
                    help="metres to rise before crossing to the start point, and "
                         "descend after. 0, the default, goes straight there. "
                         "This was 0.05 for one run, on the theory that a direct "
                         "line was brushing the block - it disturbed it by 10.1 "
                         "mm before the episode began. **That was the wrong "
                         "diagnosis.** Going up and over reported the same 10.1 "
                         "mm to eight decimal places, so the arm was never "
                         "touching it; the block settles after `reset_object_"
                         "position` under gravity, and `--settle` is what "
                         "addresses that. The detour meanwhile spent all 80 "
                         "pre-roll steps and left the arm 66 mm from the start "
                         "line, where the direct path had converged in 16")
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
parser.add_argument("--episode-length-s", type=float, default=120.0,
                    help="seconds before the environment truncates the "
                         "episode and RESETS, which teleports the object "
                         "and looks exactly like a violent ejection. The "
                         "scene's own value cut every run short at about "
                         "93 steps; generous here because nothing in this "
                         "design wants an episode to end on its own")
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
from wm_expansion.capture_verdict import capture_verdict  # noqa: E402
from wm_expansion.encounter import (  # noqa: E402
    EncounterSpec,
    bodies_at,
    draw_geometry,
)


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

        # Under `--approach servo` the encounter supplies a *direction*, not
        # positions. The measured capture radius is under 1 mm and the arm's
        # steady-state error following a moving script is 7.3 mm, so no script
        # can put the end effector where a grasp is possible; only going to the
        # object can. After the grasp the arm runs the burst schedule along the
        # drawn axis, from where it actually is.
        # See docs/paper003/paper003_servo_encounter_v0.1.md.
        if args.approach == "servo":
            if place.grasped:
                moving = (
                    (place.carry_step % (args.burst_on + args.burst_off))
                    < args.burst_on
                )
                place.carry_step += 1  # type: ignore[attr-defined]
                goal = place.goal + (
                    geometry.prober_axis * args.script_speed if moving
                    else np.zeros(3)
                )
            else:
                goal = read_object()
            place.goal = np.asarray(goal, dtype=np.float64)  # type: ignore[attr-defined]
            bodies = place.goal[None, :]

        commanded.append(np.asarray(bodies[0], dtype=np.float64).tolist())
        aim = np.asarray(bodies[0], dtype=np.float64) - read_ee()
        reach = float(np.linalg.norm(aim))
        step = aim if reach <= args.approach_speed else aim / reach * args.approach_speed
        action = torch.zeros((args.num_envs, action_dim), device=env.unwrapped.device)
        action[0, :3] = torch.as_tensor(step, device=action.device, dtype=action.dtype)

        # The gripper is what makes this a capture rather than a collision, so
        # it is scheduled on the *observed* separation rather than on a step
        # count: the block is taken hold of when the arm actually reaches it,
        # not when the script says it should have.
        gripper = args.gripper
        if args.grasp:
            if not place.grasped:
                # Close at the closest approach, not at a threshold.
                #
                # A radius is a knob: too small and the gripper never closes,
                # too large and it closes harder off-centre, driving a jaw into
                # the block - measured, the block left at 2.6 m/s from an arm
                # moving 2 mm/step. The arrival is an observable event instead:
                # the separation stops decreasing. That is what
                # `capture_displacement` means by taking hold.
                #
                # It costs one step of lateness, because a minimum is only
                # recognisable once passed. At 2 mm/step that is 2 mm.
                separation = float(np.linalg.norm(read_object() - read_ee()))
                closing = separation < place.closest - args.grasp_epsilon
                if closing:
                    place.closest = separation  # type: ignore[attr-defined]
                    place.closing_steps += 1  # type: ignore[attr-defined]
                # "Stopped decreasing" is only an arrival if an approach
                # happened first. Without the run requirement this fired on
                # **step 1**: `closest` starts at infinity, so the first
                # separation is always an improvement, and the second step -
                # with the arm still on the start line and the burst barely
                # under way - moved less than epsilon and was read as arrival.
                # It closed the gripper at 20.5 mm, nowhere near the 10.3 mm it
                # would reach at step 18.
                elif (
                    place.closing_steps >= args.grasp_closing_steps
                    and place.closest < args.grasp_radius
                ):
                    place.grasped = True  # type: ignore[attr-defined]
                    place.grasp_step = len(commanded) - 1  # type: ignore[attr-defined]
                    place.grasp_separation = separation  # type: ignore[attr-defined]
                else:
                    place.closing_steps = 0  # type: ignore[attr-defined]
            gripper = args.gripper_close if place.grasped else args.gripper_open
        if gripper != 0.0 and action_dim >= 4:
            action[0, -1] = float(gripper)
        place.gripper_series.append(float(gripper))  # type: ignore[attr-defined]
        place.pending = action  # type: ignore[attr-defined]

    place.grasped = False  # type: ignore[attr-defined]
    place.grasp_step = None  # type: ignore[attr-defined]
    place.closest = float("inf")  # type: ignore[attr-defined]
    place.goal = read_ee()  # type: ignore[attr-defined]
    place.carry_step = 0  # type: ignore[attr-defined]
    place.closing_steps = 0  # type: ignore[attr-defined]
    place.grasp_separation = None  # type: ignore[attr-defined]
    place.gripper_series = []  # type: ignore[attr-defined]

    def step_physics() -> bool:
        action = getattr(place, "pending", None)
        if action is None:
            action = torch.zeros((args.num_envs, action_dim), device=env.unwrapped.device)
        with torch.no_grad():
            _, _, terminated, truncated, _ = env.step(action)
        observed_ee.append(read_ee().tolist())
        return bool(terminated[0]) or bool(truncated[0])

    # Let the scene settle before anything is measured from it.
    #
    # The block moves 10.1 mm after `reset_object_position` regardless of what
    # the arm does - identical to eight decimal places across two completely
    # different pre-roll paths - so it is the block finding its own rest under
    # gravity, not contact. Reading `target0` before that settles wrote a stale
    # position into the encounter geometry, and charged the arm with a
    # disturbance it had not caused.
    #
    # It matters beyond bookkeeping: capture requires the target to be
    # *perfectly* still before the arrival, and a block still settling is not.
    for _ in range(args.settle):
        with torch.no_grad():
            env.step(torch.zeros((args.num_envs, action_dim), device=env.unwrapped.device))
    settled = read_object()

    target0 = settled

    encounter = EncounterSpec(
        interaction_radius=args.interaction_radius,
        reference_speed=args.script_speed,
        pusher_speed=args.script_speed,
        schedule=args.schedule,
        burst_on=args.burst_on,
        burst_off=args.burst_off,
        # A grasp has to meet the block, not pass beside it. See
        # docs/paper003/paper003_rendezvous_v0.1.md.
        lateral_offset_scale=0.0 if args.grasp else 0.5,
        probe_advance=args.probe_advance,
        probe_withdraw=args.probe_withdraw,
        probe_hold=args.probe_hold,
        bodies=args.bodies,
    )

    # Put the arm where the encounter starts, before the encounter starts.
    #
    # Measured on the first pilot: the arm begins wherever the scene resets it,
    # which was a fixed 50.2 mm from the script's first point regardless of
    # every speed setting tried. Those steps are the arm travelling to the start
    # line, not following the encounter, and they were being scored as tracking
    # error - and worse, the block's neighbourhood was being crossed on the way.
    #
    # The geometry is redrawn identically inside `run_cell` from the same seed
    # and the same `target0`, so this reaches the true step-0 position rather
    # than an approximation of it.
    geometry = draw_geometry(args.seed, target0, encounter)
    # Under `servo` the arm makes its own way to the object, so there is no
    # start line to walk to and the pre-roll would only waste steps.
    start = read_ee() if args.approach == "servo" else bodies_at(0, geometry, encounter)[0]

    # Over the block, across, and down - not straight there.
    #
    # A direct line disturbed the block by 10.1 mm before the episode began,
    # which is fatal rather than untidy: capture requires the target to be
    # *perfectly* still before the arrival, or its own history carries
    # information and the single-entity arm has something to learn from. The
    # lift scene resets the arm beside the block and the encounter runs at the
    # block's own height, so the direct path grazes it with an open jaw.
    lift = np.array([0.0, 0.0, args.preroll_clearance])
    waypoints = (
        [read_ee() + lift, start + lift, start] if args.preroll_clearance > 0.0
        else [start]
    )

    def toward(goal: np.ndarray) -> None:
        gap = goal - read_ee()
        reach = float(np.linalg.norm(gap))
        delta = gap if reach <= args.approach_speed else gap / reach * args.approach_speed
        action = torch.zeros((args.num_envs, action_dim), device=env.unwrapped.device)
        action[0, :3] = torch.as_tensor(delta, device=action.device, dtype=action.dtype)
        # Open on the way in, always. A closed gripper crossing the block's
        # neighbourhood is a collision before the encounter has begun.
        if action_dim >= 4:
            action[0, -1] = float(args.gripper_open if args.grasp else args.gripper)
        with torch.no_grad():
            env.step(action)

    preroll_steps = 0
    budget = args.preroll
    for goal in waypoints:
        while budget > 0:
            if float(np.linalg.norm(goal - read_ee())) <= args.preroll_tolerance:
                break
            toward(goal)
            budget -= 1
            preroll_steps += 1
    preroll_gap = float(np.linalg.norm(start - read_ee()))
    # The block must not have been touched getting here, or `target0` is stale
    # and the geometry `run_cell` redraws is not the one just used.
    preroll_disturbed = float(np.linalg.norm(read_object() - target0))

    record = run_cell(
        target0,
        EpisodeSpec(
            tolerance=args.tolerance,
            dispense_latency=(
                EpisodeSpec().dispense_latency
                if args.dispense_latency is None
                else args.dispense_latency
            ),
            interaction_radius=args.interaction_radius,
        ),
        encounter,
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
    # Whether the scene produced a capture at all - the first thing that could
    # end this design, and not something the runner may assume. Everything
    # measured so far is arithmetic: the cell computed the block's motion and
    # wrote it into the command. Here it is read back out of physics, and the
    # same statistic the gate and arm D use decides what happened.
    verdict = capture_verdict(record)
    record["capture"] = verdict
    record["grasp"] = {
        "requested": bool(args.grasp),
        "radius": args.grasp_radius,
        "closed_at": place.grasp_step,
        "closed_at_separation": place.grasp_separation,
        "closest_seen": None if place.closest == float("inf") else place.closest,
        "closing_steps_at_close": place.closing_steps,
        "gripper_series": place.gripper_series,
    }
    record["schedule"] = args.schedule
    # A cell whose pre-roll did not converge started somewhere other than the
    # encounter's first point, so its tracking error is not the encounter's.
    record["preroll"] = {
        "steps": preroll_steps,
        "gap": preroll_gap,
        "converged": preroll_gap <= args.preroll_tolerance,
        "block_disturbed": preroll_disturbed,
    }
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


def report(record: dict[str, Any], out_dir: Path, args: argparse.Namespace) -> list[str]:
    name = f"cell_{args.condition}_seed{args.seed}.json"
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
            f"(script {1000 * args.script_speed:.1f} mm/step, "
            f"commanded {1000 * args.approach_speed:.1f})"
        )
        # Judged against the interaction radius, not the script speed. An error
        # of half the radius already means the body is not where the script says
        # it is, so the contact geometry the gate reasons about is wrong -
        # regardless of how fast the script happens to be moving. The first real
        # cell had a median error of 9.5 mm against a 12 mm radius and passed a
        # script-speed test, while eligibility never opened.
        if (record["ee_error_median"] or 0) > 0.5 * args.interaction_radius:
            lines.append(
                f"ARM LAGGING - median error "
                f"{1000 * record['ee_error_median']:.1f} mm against a "
                f"{1000 * args.interaction_radius:.1f} mm radius. The body "
                "is not where the script says; lower --script-speed or raise "
                "--approach-speed before reading anything from this cell"
            )
    # The pilot's first question, printed where it cannot be missed.
    verdict = record.get("capture") or {}
    if verdict:
        lines.append(
            f"CAPTURE VERDICT: {verdict.get('verdict', '?').upper()}"
            f"  ({verdict.get('reason', '')})"
        )
        if verdict.get("verdict") != "capture":
            lines.append(
                "  -> this cell is NOT the relation the paper is about. Arm "
                "scores from it must not be pooled with capture cells."
            )
    (out_dir / f"cell_{args.condition}_seed{args.seed}.txt").write_text(
        "\n".join(lines) + "\n"
    )
    print("\n".join(lines))
    return lines


def main() -> None:
    """One Isaac launch, many cells.

    Each `env.reset(seed=...)` redraws the encounter, and the simulator's
    startup dominates a single cell's cost, so the seed loop lives inside one
    launch rather than in the shell. A forty-cell sweep was forty launches
    before this.

    **Untested on GPU at the time of writing** - there was no Isaac in the
    environment this was authored in. `--seeds 1` is the old single-cell
    behaviour exactly, and is the fallback if the loop misbehaves.
    """

    cfg = parse_env_cfg(args_cli.task, num_envs=args_cli.num_envs)
    # Before `gym.make`, or the env is built with the old limit.
    cfg.episode_length_s = float(args_cli.episode_length_s)
    env = gym.make(args_cli.task, cfg=cfg)
    out_dir = Path(args_cli.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    verdicts: list[str] = []
    engaged: list[bool] = []
    first_seed = args_cli.seed
    try:
        for index in range(max(1, args_cli.seeds)):
            args_cli.seed = first_seed + index
            record = run(env, args_cli)
            report(record, out_dir, args_cli)
            if not record.get("failed"):
                verdicts.append((record.get("capture") or {}).get("verdict", "?"))
                engaged.append(bool(record.get("d_estimated")))
            print()
    finally:
        args_cli.seed = first_seed
        env.close()

    if len(verdicts) > 1:
        captures = verdicts.count("capture")
        summary = [
            f"cells: {len(verdicts)}",
            f"  capture   {captures}",
            f"  collision {verdicts.count('collision')}",
            f"  none      {verdicts.count('none')}",
            "",
            # The number the preregistration's sizing rule reads, and the reason
            # this sweep exists at all. It must come from real contact.
            f"engagement (arm D acted): "
            f"{sum(engaged) / len(engaged):.2f} over {len(engaged)} cells",
        ]
        if captures == 0:
            summary.append("")
            summary.append(
                "NO CAPTURE IN ANY CELL. The scene did not produce the relation "
                "the paper is about, and no amount of arm scoring fixes that. "
                "Read paper003_prereg_v1.0.md, 'What the calibration pilot must "
                "produce', before changing anything else."
            )
        (out_dir / "SUMMARY.txt").write_text("\n".join(summary) + "\n")
        print("\n".join(summary))


if __name__ == "__main__":
    main()
    simulation_app.close()
