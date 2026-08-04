"""One commitment cell, end to end, with the simulator behind a callback.

The Isaac runner needs exactly three things from a simulator: write the target
command, take a physics step, and say whether the episode terminated. Everything
else the cell does - drive the condition, screen eligibility, choose a commit,
score the arms, assemble the record - is arithmetic, and lived in a file that
cannot be imported without a GPU.

That file has produced eight defects in this project. Every one of them was in
code that no test could reach. Putting the loop here means a run with
`drive=lambda target: False` exercises the same code path the GPU does, so a
crash or a malformed record shows up on a laptop instead of twenty minutes into
a cloud session.

The runner keeps `env.reset`, the scene inventory, and the three-line callback.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Protocol

import numpy as np

from .commitment_episode import CommitmentEpisode, EpisodeSpec
from .encounter import EncounterGeometry, EncounterSpec, bodies_at, bodies_over
from .relation_dynamics import (
    CaptureSpec,
    CouplingSpec,
    capture_displacement,
    coupling_displacement,
    normal_alignment,
)

#: Called once per step with the target position. Returns True if the episode
#: terminated or was truncated, which ends the cell and marks it invalid.
Drive = Callable[[np.ndarray], bool]


class World(Protocol):
    """Where the target's pose comes from.

    The distinction this abstraction exists for is the difference between the
    calibration pilots and the real thing. Under injected coupling the cell
    *computes* the target and writes it into the simulator's command; the
    contact is arithmetic and the simulator never resists it. Under real
    contact the cell commands the pushing bodies, steps physics, and **reads**
    where the object ended up. Nothing else in the cell changes, which is why it
    is worth separating: the gate, the arms, the eligibility screen and the
    scoring are identical in both, so a result cannot differ because the loop
    differed.
    """

    def advance(
        self, step: int, bodies: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, bool]:
        """Take one step.

        Returns the target's pose, **where the bodies actually ended up**, and
        whether the episode ended.

        The middle value is not redundant. `bodies` is the encounter's script -
        where the pushers were told to be. Under injected coupling that is also
        where they are. On a real arm it is not: a stub following at 60% lagged
        the command by 24 mm, and feeding the script to the gate and the
        coupling estimator would have had them fitting a body that was never
        there.
        """
        ...

CONDITIONS = ("coupled", "drift", "static", "noise", "slide")

#: Which relation the treatment condition instantiates.
#:
#: `collision` - the body strikes and releases. Makes the relation necessary,
#: since nothing in a still target's history predicts an approaching body, but
#: cannot clear the placement tolerance: the push moves the target away, which
#: reduces penetration, which reduces the push.
#:
#: `capture` - the body arrives at a still target and carries it off. Same
#: necessity, and the effect accumulates without bound. Chosen after measuring
#: both against a single-entity control; see
#: docs/paper003/paper003_capture_design_v0.1.md.
COUPLINGS = ("collision", "capture")


@dataclass(frozen=True)
class CellSpec:
    """Run-level choices for one cell."""

    condition: str = "coupled"
    seed: int = 300
    episode_steps: int = 80
    commit_policy: str = "uniform"
    #: -1 leaves the policy to decide; otherwise commit nearest this step.
    commit_step: int = -1
    slide_damping: float = 1.0
    coupling: str = "capture"

    def validate(self) -> None:
        if self.condition not in CONDITIONS:
            raise ValueError(f"condition must be one of {CONDITIONS}")
        if self.coupling not in COUPLINGS:
            raise ValueError(f"coupling must be one of {COUPLINGS}")
        if self.commit_policy not in ("uniform", "first"):
            raise ValueError("commit_policy must be 'uniform' or 'first'")
        if self.episode_steps < 2:
            raise ValueError("episode_steps must be >= 2")
        if not 0.0 <= self.slide_damping <= 1.0:
            raise ValueError("slide_damping must be in [0, 1]")


def _advance_target(
    target: np.ndarray,
    target0: np.ndarray,
    bodies: np.ndarray,
    geometry: EncounterGeometry,
    encounter: EncounterSpec,
    coupling: CouplingSpec,
    cell: CellSpec,
    step: int,
    slide_velocity: np.ndarray,
    previous_bodies: np.ndarray | None = None,
    holder: int | None = None,
) -> tuple[np.ndarray, np.ndarray, int | None]:
    """The condition's effect on the target this step, plus which body holds it.

    `holder` persists across steps: once a body has taken hold it does not let
    go, which is what makes the effect accumulate instead of capping at the
    interaction radius the way a collision does.

    It records *which* body, not merely that one does. A boolean was tried and
    is wrong with more than one body: whichever body came first in the list then
    carried the target, even when a different one had captured it, and the
    target rode away from the body actually holding it.
    """

    if cell.condition == "coupled":
        if cell.coupling == "capture":
            # The body's own displacement this step is what a held target
            # inherits, so the previous positions are needed - a carried target
            # moves *with* its carrier rather than away from it.
            steps = (
                np.asarray(bodies) - np.asarray(previous_bodies)
                if previous_bodies is not None
                else np.zeros_like(np.asarray(bodies))
            )
            spec = CaptureSpec(capture_radius=encounter.interaction_radius)
            if holder is not None:
                target = target + steps[holder]
            else:
                for index, (body, body_step) in enumerate(zip(bodies, steps)):
                    delta, took = capture_displacement(
                        target, body, body_step, spec, False
                    )
                    if took:
                        target = target + delta
                        holder = index
                        break
        else:
            # Summed over bodies; with one body this is the original behaviour.
            for body in bodies:
                target = target + coupling_displacement(target, body, coupling)
    elif cell.condition == "drift":
        # Paper 002's positive case: motion unrelated to any body.
        #
        # Weaker than it looks. The target runs along the first body's own axis
        # at its own speed, so the two never close - across the whole v5 sweep
        # no body came within 92 mm. The gate rejects `drift` because nothing is
        # nearby, not because it distinguished proximity-conditioned motion from
        # constant-velocity motion. `slide` is the control that asks that.
        target = target + geometry.prober_axis * encounter.reference_speed
    elif cell.condition == "slide":
        # Adversarial control for H2. Contact genuinely causes the motion, so
        # the relation is real, but the target then keeps its velocity and a
        # constant-velocity model absorbs the result. That is the case which
        # would collapse Paper 003 into Paper 002, and it is what real
        # rigid-body contact produces: struck objects slide.
        kick = sum(
            (coupling_displacement(target, body, coupling) for body in bodies),
            np.zeros_like(target),
        )
        slide_velocity = cell.slide_damping * slide_velocity + kick
        target = target + slide_velocity
    elif cell.condition == "noise":
        target = target0 + np.random.default_rng(cell.seed + step).normal(
            0.0, 0.5 * 0.020, len(target0)
        )
    # "static" leaves the target where it is.
    return target, slide_velocity, holder


@dataclass
class InjectedWorld:
    """The target moves by arithmetic; the simulator is only told where it is.

    This is what every pilot so far has run. It is honest about being a
    calibration device: the coupling is a formula, so `normal_alignment` is 1.0
    by construction and there is no contact jitter to measure.
    """

    target0: np.ndarray
    geometry: EncounterGeometry
    encounter: EncounterSpec
    coupling: CouplingSpec
    cell: CellSpec
    drive: Drive

    def __post_init__(self) -> None:
        self.target = np.asarray(self.target0, dtype=np.float64).copy()
        self.slide_velocity = np.zeros_like(self.target)
        self.holder: int | None = None
        self.previous_bodies: np.ndarray | None = None

    def advance(
        self, step: int, bodies: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, bool]:
        self.target, self.slide_velocity, self.holder = _advance_target(
            self.target, self.target0, bodies, self.geometry, self.encounter,
            self.coupling, self.cell, step, self.slide_velocity,
            self.previous_bodies, self.holder,
        )
        self.previous_bodies = np.asarray(bodies).copy()
        # The script is the truth here: these bodies are moving points.
        return self.target, bodies, bool(self.drive(self.target))


@dataclass
class ContactWorld:
    """The target is a rigid body: command the pushers, step physics, read it.

    The three callbacks are the entire simulator-facing surface. Everything the
    cell decides stays on the other side of them, so this can be exercised on a
    laptop against a toy physics function and the code path is the one the GPU
    runs.

    `place` receives the bodies' target positions for this step. Under Isaac
    those are poses the arm is commanded toward, not teleports - the object
    moves because something pushed it, which is the whole point of the branch.
    """

    place: Callable[[np.ndarray], None]
    step_physics: Callable[[], bool]
    read_target: Callable[[], np.ndarray]
    read_bodies: Callable[[], np.ndarray] | None = None
    """Where the pushers actually are after the step.

    Optional only so a caller whose bodies genuinely follow their script need
    not supply it. On a real arm it is required: the command is a target, not a
    teleport, and the gate must see the body that did the pushing.
    """

    def advance(
        self, step: int, bodies: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, bool]:
        self.place(bodies)
        terminated = bool(self.step_physics())
        target = np.asarray(self.read_target(), dtype=np.float64)
        if target.ndim != 1:
            raise ValueError("read_target must return a 1-D pose")
        observed = bodies
        if self.read_bodies is not None:
            observed = np.asarray(self.read_bodies(), dtype=np.float64)
            if observed.ndim == 1:
                observed = observed[None, :]
            if observed.shape != np.asarray(bodies).shape:
                raise ValueError("read_bodies must return one pose per commanded body")
        return target, observed, terminated


def contact_arrivals(
    targets: np.ndarray, bodies: np.ndarray, radius: float
) -> list[int]:
    """Steps at which a body crossed into contact range of the target.

    The anchor for the commit window. Two anchors that look simpler were tried
    and are wrong:

    **The target's first motion.** Wrong for the two-body encounter, which
    contains two transitions on purpose - the prober demonstrates the relation
    and the pusher applies it - and the one being predicted is the second.
    Anchored on the first, no eligible step in a two-body collision cell fell
    inside the window at all, and every cell silently took the fallback.

    **Every step the target resumes moving.** Wrong under a burst schedule: a
    carried target stops with its carrier and starts again, and reading those as
    transitions puts the commit window on the target's *own* intermittency -
    which is the carriage regime, where a single-entity model matches the
    relational one and H2 fails. A pause is not a new relation.

    A body crossing into range is neither. It is observable, it happens once per
    approach whatever the target then does, and nothing about which arm profits
    enters it.
    """

    if len(targets) < 2 or radius <= 0.0:
        return []
    inside = np.linalg.norm(bodies - targets[:, None, :], axis=2).min(axis=1) < radius
    return [
        int(step)
        for step in range(len(inside))
        if inside[step] and not (step and inside[step - 1])
    ]


def run_cell(
    target0: np.ndarray,
    spec: EpisodeSpec,
    encounter: EncounterSpec,
    cell: CellSpec,
    drive: Drive | None = None,
    coupling: CouplingSpec | None = None,
    world: World | None = None,
) -> dict[str, Any]:
    """Drive one episode, commit once, score every arm, return the record."""

    cell.validate()
    spec.validate()
    encounter.validate()
    target0 = np.asarray(target0, dtype=np.float64)
    coupling = coupling or CouplingSpec(
        interaction_radius=spec.interaction_radius, coupling_gain=spec.coupling_gain
    )
    from .encounter import draw_geometry  # local: keeps the import graph shallow

    geometry = draw_geometry(cell.seed, target0, encounter)
    if world is None:
        if drive is None:
            raise ValueError("pass either `drive` (injected coupling) or `world`")
        world = InjectedWorld(target0, geometry, encounter, coupling, cell, drive)
    elif drive is not None:
        raise ValueError("pass `drive` or `world`, not both")
    episode = CommitmentEpisode(spec=spec)

    observations: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    trajectory: list[np.ndarray] = []
    violations = 0
    terminated = False

    for step in range(cell.episode_steps):
        commanded = bodies_at(step, geometry, encounter)
        target, bodies, terminated = world.advance(step, commanded)

        episode.observe(target, bodies)
        # Recorded every step, not only at commitment: H3 has to be evaluable on
        # conditions that never commit, and `drift` produced no commit at all in
        # the first control run.
        gate = episode.gate_decision()
        observations.append(
            {
                "step": step,
                "target": target.tolist(),
                # `reference` is the first body, kept so existing readers of
                # these records keep working; `references` is the full set.
                "reference": np.asarray(bodies)[0].tolist(),
                "references": np.asarray(bodies).tolist(),
                # What the encounter asked for, kept apart from what happened.
                # A cell where these diverge is measuring an arm that could not
                # follow the script, not the contact it was meant to.
                "commanded": np.asarray(commanded).tolist(),
                # This step's crossing, for diagnosis, and the sustained
                # decision arm D acts on. A lone crossing is one draw of a
                # statistic: under the noise control some prefix crosses by
                # chance in 0.30 of trials.
                "gate_crossed": bool(gate.fired),
                "gate_fired": bool(episode.gate_fired()),
                "proximity_contrast": float(gate.proximity_contrast),
                "constant_velocity_gain": float(gate.constant_velocity_gain),
            }
        )

        # The bodies' future comes from the harness, which generated the
        # schedule. Predicting it instead would route eligibility through arm
        # D's pattern estimator and make it depend on one arm's readiness.
        future = bodies_over(step + 1, spec.dispense_latency, geometry, encounter)
        if episode.motion_expected(future) and episode.ready:
            # Every eligible step is a candidate; the policy chooses afterwards,
            # so the choice cannot depend on how the cell happened to unfold.
            candidates.append(
                {
                    "step": step,
                    # Whether arm D estimated or fell back to zero-order.
                    # Without this the two are indistinguishable in the output
                    # and a fallback reads as a failed relational prediction.
                    "d_estimated": episode.can_estimate(),
                    "aims": {k: v.copy() for k, v in episode.aims().items()},
                }
            )

        trajectory.append(target.copy())
        if terminated:
            violations += 1
            break

    committed_at: int | None = None
    d_estimated = False
    aims: dict[str, np.ndarray] | None = None
    resolved: dict[str, bool] | None = None

    usable = [
        c for c in candidates if c["step"] + spec.dispense_latency < len(trajectory)
    ]
    # The commit window: within one dispense-length of the transition, on
    # either side.
    #
    # Fixed on the structure of the action, which is the only ground available
    # that no arm appears in. The dispense takes `dispense_latency` steps and
    # lands where the target then is, so a commit further than that before the
    # transition completes before anything has happened to the target, and one
    # further than that after it is measuring a regime the transition no longer
    # governs. Symmetric because there is no reason to prefer a side, and
    # preferring one is exactly how "so that arm B fails" would enter.
    #
    # What it fixes is not a preference but an artefact. The eligibility screen
    # admits any step where the target will move, and under capture that is
    # every step after the arrival, because a carried target rides forever. So
    # the size of the eligible set - and with it the commit distribution - was
    # set by `episode_steps`, an arbitrary number, and almost all of its mass
    # sat in the riding tail where a constant-velocity model absorbs the motion.
    # The same cell scored differently for running longer.
    #
    # Applied uniformly, and it is not selective: `drift`, `noise` and `static`
    # have no arrival in them at all, keep every eligible step, and commit
    # exactly as they did before, which is what leaves H4 testable. `slide`
    # keeps its post-strike steps, which is what makes it the control that could
    # collapse this paper into Paper 002.
    arrivals = contact_arrivals(
        np.asarray([o["target"] for o in observations]),
        np.asarray([o["references"] for o in observations]),
        spec.interaction_radius,
    )
    in_window = [
        c for c in usable
        if any(abs(c["step"] - a) <= spec.dispense_latency for a in arrivals)
    ]
    usable = in_window or usable
    if usable:
        if cell.commit_step >= 0:
            chosen = min(usable, key=lambda c: abs(c["step"] - cell.commit_step))
        elif cell.commit_policy == "first":
            chosen = usable[0]
        else:
            chosen = usable[int(np.random.default_rng(cell.seed).integers(len(usable)))]
        committed_at = int(chosen["step"])
        d_estimated = bool(chosen["d_estimated"])
        landing = trajectory[committed_at + spec.dispense_latency]
        aims = dict(chosen["aims"])
        aims["D_oracle"] = landing.copy()
        resolved = episode.resolve(aims, landing)

    return {
        "seed": cell.seed,
        "condition": cell.condition,
        "reference_speed": encounter.reference_speed,
        "commit_policy": cell.commit_policy,
        "bodies": encounter.bodies,
        "encounter": encounter.schedule,
        # Which world produced the target. An injected cell is a calibration
        # device and must never be pooled with a contact cell.
        "world": type(world).__name__,
        **geometry.to_dict(),
        "eligible_steps": [c["step"] for c in candidates],
        # Where the arrivals were, and whether the commit landed in a window.
        # A cell that committed outside one is not invalid - the conditions with
        # no arrival in them are meant to - but pooling the two without being
        # able to tell them apart is how the capture bias got in, and
        # `commit_offset` is what the analysis reads to check it.
        "arrivals": arrivals,
        "commit_offset": (
            None
            if (not arrivals or committed_at is None)
            else min((committed_at - a for a in arrivals), key=abs)
        ),
        "committed_in_window": bool(in_window),
        "committed_at": committed_at,
        "d_estimated": d_estimated,
        "gate_fire_rate": (
            sum(o["gate_fired"] for o in observations) / len(observations)
            if observations
            else 0.0
        ),
        # Diagnostic only, nothing gates on it. Arm D fits displacement
        # magnitude against separation and never inspects direction, so a
        # contact pushing off the normal returns correct coefficients while the
        # aim is wrong. Under injected coupling this is ~1.0 by construction;
        # under real contact it is the first thing to read if arm D
        # underperforms with a healthy gate and a clean fit.
        "normal_alignment": normal_alignment(
            episode.targets, episode.references, spec.interaction_radius
        ),
        "resolved": resolved,
        "aims": {k: v.tolist() for k, v in (aims or {}).items()},
        "observations": observations,
        "early_termination": violations,
        "valid": resolved is not None and violations == 0,
    }
