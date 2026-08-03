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
from typing import Any, Callable

import numpy as np

from .commitment_episode import CommitmentEpisode, EpisodeSpec
from .encounter import EncounterGeometry, EncounterSpec, bodies_at, bodies_over
from .relation_dynamics import CouplingSpec, coupling_displacement, normal_alignment

#: Called once per step with the target position. Returns True if the episode
#: terminated or was truncated, which ends the cell and marks it invalid.
Drive = Callable[[np.ndarray], bool]

CONDITIONS = ("coupled", "drift", "static", "noise", "slide")


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

    def validate(self) -> None:
        if self.condition not in CONDITIONS:
            raise ValueError(f"condition must be one of {CONDITIONS}")
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
) -> tuple[np.ndarray, np.ndarray]:
    """The condition's effect on the target this step, and the carried velocity."""

    if cell.condition == "coupled":
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
    return target, slide_velocity


def run_cell(
    target0: np.ndarray,
    spec: EpisodeSpec,
    encounter: EncounterSpec,
    cell: CellSpec,
    drive: Drive,
    coupling: CouplingSpec | None = None,
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
    episode = CommitmentEpisode(spec=spec)

    target = target0.copy()
    observations: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    trajectory: list[np.ndarray] = []
    slide_velocity = np.zeros_like(target0)
    violations = 0

    for step in range(cell.episode_steps):
        bodies = bodies_at(step, geometry, encounter)
        target, slide_velocity = _advance_target(
            target, target0, bodies, geometry, encounter, coupling, cell, step,
            slide_velocity,
        )

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
                "reference": bodies[0].tolist(),
                "references": bodies.tolist(),
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
        if drive(target):
            violations += 1
            break

    committed_at: int | None = None
    d_estimated = False
    aims: dict[str, np.ndarray] | None = None
    resolved: dict[str, bool] | None = None

    usable = [
        c for c in candidates if c["step"] + spec.dispense_latency < len(trajectory)
    ]
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
        **geometry.to_dict(),
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
