"""Paper 003 Isaac calibration pilot: relational coupling at a commitment point.

STATUS: first ran successfully in Isaac 2026-08-03, after eight defects that a
GPU-less authoring environment could not catch. Still a pilot: read the records
before trusting anything.

THIS IS AN ENGINEERING CALIBRATION PILOT, NOT A CONFIRMATORY RUN. Its output is
excluded from every confirmatory estimate, exactly as Paper 002's
`isaac_model_order_pilot_v0.3` was. Its job is to produce the five things the
draft preregistration says it must:

  1. the environment runs end to end, process-isolated per cell
  2. measured observation noise and timing irregularity under real physics
  3. a speed sweep locating where arm B falls into the near-zero band
  4. gate statistics on coupled / drift / static / noise conditions
  5. confirmation that the oracle arm clears 80%, i.e. the task is solvable

See docs/paper003/paper003_prereg_draft_v0.1.md.

Design note: every decision - eligibility, each arm's prediction, scoring - is
delegated to `wm_expansion.commitment_episode`, which is CPU-testable and
covered by tests. What lives here is scene manipulation and record-keeping, so
the unvalidated surface is as small as it can be made.

Structure follows `orbit_reach_drift.py`: one policy-free process per cell,
argparse before AppLauncher, Isaac imports after.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from omni.isaac.lab.app import AppLauncher

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--task", type=str, default="Isaac-Reach-Dual-STAR-IK-Rel-Play-v0")
parser.add_argument("--num_envs", type=int, default=1)
parser.add_argument("--seed", type=int, required=True)
parser.add_argument("--body-index", type=int, default=-1)
parser.add_argument("--gain", type=float, default=1.0)
parser.add_argument("--max-delta", type=float, default=0.05)
parser.add_argument(
    "--condition",
    choices=["coupled", "drift", "static", "noise", "slide"],
    default="coupled",
    help="coupled is the treatment; the others are gate-specificity controls",
)
parser.add_argument(
    "--slide-damping", type=float, default=1.0,
    help="velocity retained per step in the `slide` control; 1.0 is a "
         "frictionless slide, which is precisely arm C's case",
)
parser.add_argument("--reference-speed", type=float, default=0.015,
                    help="metres per step while the reference body is moving")
parser.add_argument("--burst-on", type=int, default=10)
parser.add_argument("--burst-off", type=int, default=4)
parser.add_argument(
    "--encounter", choices=["probe", "burst"], default="probe",
    help="probe withdraws after striking, so one completed contact precedes the "
         "commit window; burst is the v5 schedule, which never retreats and "
         "leaves coupling and sliding unidentifiable at commit time",
)
#: 7 + 5 + 2 = 14, the same period as the burst schedule it replaces, so the
#: encounter's timing stays comparable to the v5 sweep and only the withdrawal
#: is new. The withdrawal must exceed the interaction radius: 5 * 15 mm = 75 mm
#: against a 50 mm radius, so contact genuinely releases rather than easing off.
parser.add_argument("--probe-advance", type=int, default=7)
parser.add_argument("--probe-withdraw", type=int, default=5)
parser.add_argument("--probe-hold", type=int, default=2)
parser.add_argument(
    "--bodies", type=int, choices=[1, 2], default=1,
    help="2 adds a second reference body: the first strikes early and leaves, "
         "the second arrives during the dispense window. At the commitment the "
         "target is then stationary, so zero-order and constant velocity both "
         "predict no motion and only a relation applied to the *second* body "
         "predicts the displacement",
)
parser.add_argument("--pusher-speed", type=float, default=0.015,
                    help="metres per step for the second body, which never pauses")
parser.add_argument("--pusher-start-step", type=int, default=16,
                    help="step at which the second body begins to close")
parser.add_argument("--interaction-radius", type=float, default=0.05)
parser.add_argument("--coupling-gain", type=float, default=0.5)
parser.add_argument("--tolerance", type=float, default=0.020,
                    help="metres; inherited from this task family's established "
                         "20 mm success criterion (Paper 001/002), not fitted here")
parser.add_argument("--dispense-latency", type=int, default=6)
parser.add_argument("--episode-steps", type=int, default=80)
parser.add_argument(
    "--commit-policy",
    choices=["uniform", "first"],
    default="uniform",
    help=(
        "which eligible step to commit at. 'uniform' draws one from the seed; "
        "'first' takes the earliest. Uniform is the default because 'first' is "
        "not a policy an agent would follow - nobody places at the earliest "
        "physically possible instant - and because it concentrates every "
        "measurement in the approach phase, where no arm has information yet."
    ),
)
parser.add_argument("--commit-step", type=int, default=-1,
                    help="force a specific step; overrides --commit-policy")
parser.add_argument("--max-cells", type=int, default=1,
                    help="smoke guard; keep at 1 until the environment is trusted")
parser.add_argument("--out-dir", type=str, required=True)
parser.add_argument("--disable_fabric", action="store_true", default=False)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import gymnasium as gym  # noqa: E402
import torch  # noqa: E402
from omni.isaac.lab_tasks.utils import parse_env_cfg  # noqa: E402

import omni.isaac.lab_tasks  # noqa: F401,E402
import orbit.surgical.tasks  # noqa: F401,E402

import sys  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from orbit_reach_common import (  # noqa: E402
    find_robot_name,
    resolve_ee_body_index,
    scripted_action,
)
from wm_expansion.commitment_episode import (  # noqa: E402
    CommitmentEpisode,
    EpisodeSpec,
)
from wm_expansion.encounter import (  # noqa: E402
    EncounterSpec,
    bodies_at,
    bodies_over,
    draw_geometry,
)
from wm_expansion.relation_dynamics import (  # noqa: E402
    CouplingSpec,
    coupling_displacement,
    normal_alignment,
)

#: Matches orbit_reach_drift.py. This task exposes `ee_1_pose`, not `ee_pose`;
#: an earlier version of this file invented the latter and could never have run.
COMMAND_NAME = "ee_1_pose"


def _get_command(env: Any) -> torch.Tensor:
    return env.unwrapped.command_manager.get_command(COMMAND_NAME).clone()


def _set_command(env: Any, command: torch.Tensor) -> None:
    env.unwrapped.command_manager.get_command(COMMAND_NAME)[:] = command


def run_cell(env: Any, args: argparse.Namespace) -> dict[str, Any]:
    """One episode: drive the coupling, commit once, score every arm."""

    spec = EpisodeSpec(
        tolerance=args.tolerance,
        dispense_latency=args.dispense_latency,
        interaction_radius=args.interaction_radius,
    )
    coupling = CouplingSpec(
        interaction_radius=args.interaction_radius,
        coupling_gain=args.coupling_gain,
    )
    episode = CommitmentEpisode(spec=spec)

    env.reset(seed=args.seed)
    robot_name = find_robot_name(env.unwrapped.scene)
    body_index = resolve_ee_body_index(env.unwrapped.scene[robot_name], args.body_index)

    # What is actually in this scene? Needed to decide whether a real-contact
    # version can reuse an existing rigid body as the pushed target or has to
    # add one, and that cannot be determined without a GPU. Recording it costs
    # nothing and answers the question on the next run rather than by guesswork.
    scene = env.unwrapped.scene
    scene_inventory = {
        "articulations": sorted(getattr(scene, "articulations", {}).keys()),
        "rigid_objects": sorted(getattr(scene, "rigid_objects", {}).keys()),
        "sensors": sorted(getattr(scene, "sensors", {}).keys()),
    }

    command = _get_command(env)
    target0 = command[0, :3].detach().cpu().numpy().astype(np.float64)

    # The reference bodies are moving points rather than rigid assets: this
    # pilot measures prediction, not contact dynamics. Real contact needs a
    # rigid body added to the scene, which the inventory shows has none.
    #
    # All of the geometry lives in wm_expansion.encounter, where tests can
    # reach it. It used to be inline here, in a file that cannot be imported
    # without a GPU - the surface that produced eight defects, among them a
    # fixed +x axis that made ten seeds one translation-invariant encounter.
    encounter = EncounterSpec(
        interaction_radius=args.interaction_radius,
        reference_speed=args.reference_speed,
        schedule=args.encounter,
        burst_on=args.burst_on,
        burst_off=args.burst_off,
        probe_advance=args.probe_advance,
        probe_withdraw=args.probe_withdraw,
        probe_hold=args.probe_hold,
        bodies=args.bodies,
        pusher_speed=args.pusher_speed,
        pusher_start_step=args.pusher_start_step,
    )
    geometry = draw_geometry(args.seed, target0, encounter)
    azimuth = geometry.azimuth
    offset = geometry.lateral_offset
    phase_offset = geometry.phase_offset
    pusher_azimuth = geometry.pusher_azimuth

    target = target0.copy()
    observations: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    trajectory: list[np.ndarray] = []
    committed_at: int | None = None
    d_estimated = False
    aims: dict[str, np.ndarray] | None = None
    resolved: dict[str, bool] | None = None
    violations = 0
    slide_velocity = np.zeros(3)  # carried across steps by the `slide` control

    for step in range(args.episode_steps):
        bodies = bodies_at(step, geometry, encounter)
        reference = bodies[0]

        if args.condition == "coupled":
            # Summed over bodies: with one body this is the previous behaviour.
            for body in bodies:
                target = target + coupling_displacement(target, body, coupling)
        elif args.condition == "drift":
            # Paper 002's positive case: motion unrelated to the reference.
            #
            # Note this control is weaker than it looks. The target runs along
            # the reference's own axis at the reference's own speed, so the two
            # never close: across the whole v5 sweep the reference never came
            # within 92 mm. The gate rejects `drift` because nothing is nearby,
            # not because it distinguished proximity-conditioned motion from
            # constant-velocity motion. `slide` below is the control that
            # actually puts that question to it.
            target = target + geometry.prober_axis * args.reference_speed
        elif args.condition == "slide":
            # Adversarial control for H2. Contact genuinely causes the motion -
            # so the relation is real - but the target then keeps its velocity,
            # and a constant-velocity model absorbs the result. This is the case
            # that would collapse Paper 003 into Paper 002, and it is also what
            # real rigid-body contact produces: struck objects slide.
            #
            # The gate must stay silent here. On CPU it does not: in the
            # near-frictionless regime it still fired on 14-19% of steps
            # (scripts/paper003_gate_characterisation.py).
            kick = sum(
                (coupling_displacement(target, body, coupling) for body in bodies),
                np.zeros(3),
            )
            slide_velocity = args.slide_damping * slide_velocity + kick
            target = target + slide_velocity
        elif args.condition == "noise":
            target = target0 + np.random.default_rng(args.seed + step).normal(
                0.0, args.tolerance * 0.5, 3
            )
        # "static" leaves the target where it is.

        command[0, :3] = torch.as_tensor(target, device=command.device, dtype=command.dtype)
        _set_command(env, command)

        episode.observe(target, bodies)
        # Record the gate every step, not only at commitment. H3 (gate
        # specificity) has to be evaluable on conditions that never commit -
        # `drift` produced no commit at all in the first control run, which
        # would otherwise leave the paper's key control untestable.
        gate = episode.gate_decision()
        gate_sustained = episode.gate_fired()
        observations.append(
            {
                "step": step,
                "target": target.tolist(),
                # `reference` is the first body, kept so every existing reader
                # of these records keeps working; `references` is the full set.
                "reference": reference.tolist(),
                "references": bodies.tolist(),
                # This step's crossing, kept for diagnosis, and the sustained
                # decision arm D actually acts on. They differ: a lone crossing
                # is one draw of a statistic, and under the noise control some
                # prefix crosses by chance in 0.30 of trials.
                "gate_crossed": bool(gate.fired),
                "gate_fired": bool(gate_sustained),
                "proximity_contrast": float(gate.proximity_contrast),
                "constant_velocity_gain": float(gate.constant_velocity_gain),
            }
        )

        # The reference's schedule is the harness's own, so its future is known
        # exactly. Handing it to the eligibility screen is what keeps that screen
        # a property of the world: predicting the future instead would route it
        # through arm D's pattern estimator and make eligibility depend on one
        # arm's readiness.
        reference_future = bodies_over(
            step + 1, args.dispense_latency, geometry, encounter
        )
        eligible = episode.motion_expected(reference_future) and episode.ready
        if eligible:
            # Every eligible step is a commit candidate. The policy below picks
            # among them; recording all of them keeps that choice out of the
            # loop, so it cannot depend on how a cell happened to unfold.
            candidates.append(
                {
                    "step": step,
                    # Whether arm D actually estimated or fell back to
                    # zero-order. Without this the two are indistinguishable in
                    # the output and a fallback reads as a failed relational
                    # prediction.
                    "d_estimated": episode.can_estimate(),
                    "aims": {k: v.copy() for k, v in episode.aims().items()},
                }
            )

        trajectory.append(target.copy())

        with torch.no_grad():
            action = scripted_action(
                env, robot_name, COMMAND_NAME, args.gain, body_index, args.max_delta
            )
        _, _, terminated, truncated, _ = env.step(action)
        if bool(terminated[0]) or bool(truncated[0]):
            violations += 1
            break

    # ---- commit policy -----------------------------------------------------
    # Only candidates whose dispense completes within the episode are usable.
    usable = [
        c for c in candidates if c["step"] + args.dispense_latency < len(trajectory)
    ]
    if usable:
        if args.commit_step >= 0:
            chosen = min(usable, key=lambda c: abs(c["step"] - args.commit_step))
        elif args.commit_policy == "first":
            chosen = usable[0]
        else:
            chosen = usable[int(np.random.default_rng(args.seed).integers(len(usable)))]

        committed_at = int(chosen["step"])
        d_estimated = bool(chosen["d_estimated"])
        landing = trajectory[committed_at + args.dispense_latency]
        aims = dict(chosen["aims"])
        aims["D_oracle"] = landing.copy()
        resolved = episode.resolve(aims, landing)

    return {
        "seed": args.seed,
        "condition": args.condition,
        "reference_speed": args.reference_speed,
        "approach_azimuth": azimuth,
        "approach_offset": offset,
        "phase_offset": phase_offset,
        "commit_policy": args.commit_policy,
        "scene_inventory": scene_inventory,
        "bodies": args.bodies,
        "pusher_azimuth": pusher_azimuth if args.bodies == 2 else None,
        "eligible_steps": [c["step"] for c in candidates],
        "committed_at": committed_at,
        "d_estimated": d_estimated,
        "gate_fire_rate": (
            sum(o["gate_fired"] for o in observations) / len(observations)
            if observations
            else 0.0
        ),
        # Diagnostic only, nothing gates on it. Arm D fits displacement
        # magnitude against separation and never inspects direction, so a
        # contact that pushes off the normal returns correct coefficients while
        # the aim is wrong. Under injected coupling this is ~1.0 by
        # construction; under real contact it is the first thing to check if
        # arm D underperforms with a healthy gate and a clean fit.
        "normal_alignment": normal_alignment(
            episode.targets, episode.references, args.interaction_radius
        ),
        "resolved": resolved,
        "aims": {k: v.tolist() for k, v in (aims or {}).items()},
        "observations": observations,
        "early_termination": violations,
        "valid": resolved is not None and violations == 0,
    }


def main() -> None:
    out_dir = Path(args_cli.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    env_cfg = parse_env_cfg(
        args_cli.task,
        num_envs=args_cli.num_envs,
        use_fabric=not args_cli.disable_fabric,
    )
    env = gym.make(args_cli.task, cfg=env_cfg)

    record = run_cell(env, args_cli)
    record["created_utc"] = datetime.now(timezone.utc).isoformat()
    record["source"] = Path(__file__).name
    record["status"] = "CALIBRATION PILOT - excluded from confirmatory estimates"

    payload = json.dumps(record, indent=2, sort_keys=True)
    record["sha256"] = hashlib.sha256(payload.encode()).hexdigest()

    name = f"pilot_{args_cli.condition}_seed{args_cli.seed}.json"
    (out_dir / name).write_text(json.dumps(record, indent=2, sort_keys=True))
    print(f"wrote {out_dir / name}")
    print(f"  committed_at={record['committed_at']}  valid={record['valid']}")
    print(f"  resolved={record['resolved']}")

    env.close()
    simulation_app.close()


if __name__ == "__main__":
    main()
