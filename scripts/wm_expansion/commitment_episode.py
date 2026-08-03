"""Physics-agnostic driver for the Paper 003 commitment-point episode.

STATUS: design stage, 2026-07-31. Not preregistered.

Why this module exists separately from the Isaac runner: the Isaac script
cannot be executed or even syntax-checked without a GPU and Isaac Lab, so
anything placed in it is shipped blind. Everything that decides something -
when to commit, what each arm predicts, whether the placement landed - lives
here instead, where it runs on CPU and is covered by tests. The Isaac script
is left as a thin shell that builds a scene, steps physics, and hands
observations to this driver.

This mirrors how `orbit_reach_drift.py` already delegates its target models to
`target_dynamics`.

Dimension-agnostic: 2-D for the CPU proxy, 3-D for Isaac.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import numpy as np

from .commitment_task import ReferencePatternEstimator
from .relation_dynamics import (
    CouplingSpec,
    RelationGateDecision,
    RelationGateThresholds,
    coupling_displacement,
    evaluate_relation_gate,
)

ArrayLike = Sequence[float] | np.ndarray

#: Arms scored every episode. `D_oracle` is diagnostic and excluded from
#: primary estimates - see the preregistration draft.
EPISODE_ARMS = ("A", "B", "C", "D", "D_oracle")


@dataclass
class EpisodeSpec:
    """Task geometry in physical units. Values come from the calibration pilot."""

    tolerance: float = 0.020
    """Placement tolerance, metres.

    **Provenance matters here.** 20 mm is the success tolerance already
    established for this task family - `ReachDriftEnv.success_tol` and the
    Paper 002 preregistration's binary success criterion - both fixed long
    before Paper 003 existed and with no reference to its arms.

    It is inherited deliberately rather than chosen. The first Isaac run
    happened to show arm D missing by 6.97 mm against a placeholder 5 mm
    tolerance carried over from the CPU proxy, where the spatial scale was
    arbitrary. Raising the tolerance *because* that would let arm D pass is
    precisely the move preregistration exists to prevent, so the number is
    taken from prior work instead, and would stand even if it excluded D.
    """
    dispense_latency: int = 6
    interaction_radius: float = 0.05
    coupling_gain: float = 0.5
    min_history: int = 8

    def validate(self) -> None:
        if self.tolerance <= 0.0:
            raise ValueError("tolerance must be > 0")
        if self.dispense_latency < 1:
            raise ValueError("dispense_latency must be >= 1")
        if self.interaction_radius <= 0.0:
            raise ValueError("interaction_radius must be > 0")
        if not 0.0 < self.coupling_gain <= 1.0:
            raise ValueError("coupling_gain must be in (0, 1]")
        if self.min_history < 4:
            raise ValueError("min_history must be >= 4")


def project_reference_motion(
    target: np.ndarray,
    history: np.ndarray,
    horizon: int,
    estimator: ReferencePatternEstimator,
    coupling: CouplingSpec,
) -> np.ndarray | None:
    """Predict the *target's* displacement over `horizon` steps.

    The reference is rolled forward one step at a time using the estimated
    burst pattern, and the coupling is re-applied to a running copy of the
    target at each step - the same forward roll `RelationalTargetModel.predict`
    performs.

    An earlier version summed the reference's own displacement and applied it
    to the target directly. That is only correct for a perfectly head-on pass,
    where the contact normal happens to align with the reference's direction of
    travel. Under varied approach geometry the two diverge, and the Isaac sweep
    punished it immediately: arm D went from 7.0 mm on a fixed head-on encounter
    to 60.4 mm across randomised ones, worse than plain parameter repair. The
    target moves along the contact normal, not along the reference's heading.
    """

    if len(history) < 2:
        return None
    deltas = np.diff(history, axis=0)
    total = deltas.sum(axis=0)
    norm = float(np.linalg.norm(total))
    if norm <= 0.0:
        return np.zeros(history.shape[1])

    direction = total / norm
    steps = estimator.predict_steps(list(history @ direction), horizon)
    if steps is None:
        return None

    start = np.asarray(target, dtype=np.float64)
    rolling_target = start.copy()
    rolling_reference = np.asarray(history[-1], dtype=np.float64)
    for step in steps:
        rolling_reference = rolling_reference + float(step) * direction
        rolling_target = rolling_target + coupling_displacement(
            rolling_target, rolling_reference, coupling
        )
    return rolling_target - start


@dataclass
class CommitmentEpisode:
    """Drives one commit-and-dispense attempt from streamed observations.

    Usage per step:  observe(target, reference)  ->  contact_imminent()
    then, at the chosen commit step:  aims()  and later  resolve(true_landing).
    """

    spec: EpisodeSpec = field(default_factory=EpisodeSpec)
    estimator: ReferencePatternEstimator = field(default_factory=ReferencePatternEstimator)
    gate_thresholds: RelationGateThresholds = field(default_factory=RelationGateThresholds)
    targets: list[np.ndarray] = field(default_factory=list)
    references: list[np.ndarray] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.spec.validate()

    def observe(self, target: ArrayLike, reference: ArrayLike) -> None:
        target_arr = np.asarray(target, dtype=np.float64)
        reference_arr = np.asarray(reference, dtype=np.float64)
        if target_arr.shape != reference_arr.shape or target_arr.ndim != 1:
            raise ValueError("target and reference must be 1-D and share a shape")
        if not (np.isfinite(target_arr).all() and np.isfinite(reference_arr).all()):
            raise ValueError("observations must be finite")
        self.targets.append(target_arr)
        self.references.append(reference_arr)

    def _coupling(self) -> CouplingSpec:
        return CouplingSpec(
            interaction_radius=self.spec.interaction_radius,
            coupling_gain=self.spec.coupling_gain,
        )

    def gate_decision(self) -> RelationGateDecision:
        """Is the target's motion actually conditioned on the reference?

        This is the relation-adequacy gate, and arm D must not act without it.
        An earlier version applied the relation unconditionally, which the
        Isaac control conditions immediately punished: on a **static** target
        the reference still sweeps past, so arm D predicted 90 mm of motion
        for a target that never moved, while plain zero-order was exact. The
        gate is what distinguishes "the reference is moving" from "the target
        moves *because of* the reference".
        """

        if len(self.targets) < 2:
            return RelationGateDecision(False, 0, 0.0, 0.0, 0.0, 0.0, 0.0)
        return evaluate_relation_gate(
            self.targets,
            self.references,
            self.gate_thresholds,
            interaction_radius=self.spec.interaction_radius,
            horizon=self.spec.dispense_latency,
        )

    def _projection_available(self) -> bool:
        """Has enough history accumulated for the reference cycle to be identified?

        A property of the observation history alone, independent of whether the
        relation applies. The estimator needs one completed burst and one
        completed pause, which takes longer than any `min_history` shorter than
        a period - the first Isaac run committed at step 7 of a 14-step cycle
        and arm D silently degraded into arm B.
        """

        if len(self.references) < 2:
            return False
        return (
            project_reference_motion(
                self.targets[-1],
                np.asarray(self.references),
                self.spec.dispense_latency,
                self.estimator,
                self._coupling(),
            )
            is not None
        )

    def can_estimate(self) -> bool:
        """May arm D use a relational prediction? Gate **and** history required."""
        return self._projection_available() and self.gate_decision().fired

    @property
    def ready(self) -> bool:
        """Eligible to commit.

        Deliberately **not** conditioned on the gate. Whether a cell is worth
        committing is a property of the world - will the target move, and have
        we watched long enough to predict it - not of whether one particular
        arm is allowed to act. Requiring the gate here skipped every
        non-relational cell outright, which would have made H4 untestable:
        the hypothesis that arm D does not regress where the relation is
        absent cannot be checked on cells that never run.

        Arm D falling back to zero-order is legitimate arm behaviour and is
        scored as such, in `aims()`.
        """
        return len(self.targets) >= self.spec.min_history and self._projection_available()

    def motion_expected(self) -> bool:
        """Will the target move during the dispense window?

        This is the eligibility screen: where the target will not move, every
        arm is trivially right and committing there measures nothing. The
        preregistration treats it as a screen, not a result.

        Three regimes qualify. Earlier versions admitted only some of them and
        each omission silently discarded cells where the arms differ:

        1. **Already moving** - whatever the cause. A target drifting under its
           own dynamics will move during the dispense even with no reference
           anywhere near it, and that is a cell worth scoring: it is where a
           constant-velocity arm should win and a relational one should decline
           to act. Omitting it meant the drift condition never committed at
           all, so the two operators could never be shown to address different
           gaps.
        2. **Contact coming** - the reference is closing and will arrive inside
           the interaction radius within the dispense window.
        3. **Contact ongoing** - they are already within the interaction radius,
           so the target is being pushed right now.
        """

        if len(self.targets) < 2:
            return False
        target, previous_target = self.targets[-1], self.targets[-2]
        reference, previous_reference = self.references[-1], self.references[-2]

        # 1. the target is moving under any cause
        target_speed = float(np.linalg.norm(target - previous_target))
        if target_speed * self.spec.dispense_latency > self.spec.tolerance:
            return True

        separation = float(np.linalg.norm(target - reference))
        if separation < self.spec.interaction_radius:
            return True

        closing = float(np.linalg.norm(target - previous_reference)) - separation
        reach = separation - self.spec.interaction_radius
        return closing > 0.0 and 0.0 < reach <= closing * self.spec.dispense_latency

    def aims(self, true_landing: ArrayLike | None = None) -> dict[str, np.ndarray]:
        """Each arm's predicted landing point at the moment of commitment.

        `true_landing` is only consumed by the diagnostic oracle arm. Passing
        None omits that arm rather than letting it silently degrade into D.
        """

        if len(self.targets) < 2:
            raise RuntimeError("need at least two observations before committing")

        target = self.targets[-1]
        horizon = self.spec.dispense_latency
        velocity = target - self.targets[-2]

        out: dict[str, np.ndarray] = {
            "A": self.targets[0].copy(),
            "B": target.copy(),
            "C": target + horizon * velocity,
        }

        # Arm D acts only when the gate says the target's motion is actually
        # conditioned on the reference. Without this check it invents motion on
        # static and noise conditions, where the reference moves but the target
        # is uncoupled. An unusable estimate falls back the same way rather than
        # fabricating an aim; the arm is penalised for it, which is correct.
        predicted = (
            project_reference_motion(
                target, np.asarray(self.references), horizon, self.estimator, self._coupling()
            )
            if self.gate_decision().fired
            else None
        )
        out["D"] = target.copy() if predicted is None else target + predicted

        if true_landing is not None:
            out["D_oracle"] = np.asarray(true_landing, dtype=np.float64)
        return out

    def resolve(
        self, aims: dict[str, np.ndarray], true_landing: ArrayLike
    ) -> dict[str, bool]:
        """Score each arm: did the placement land within tolerance of the target?"""

        landing = np.asarray(true_landing, dtype=np.float64)
        return {
            arm: bool(np.linalg.norm(np.asarray(aim) - landing) <= self.spec.tolerance)
            for arm, aim in aims.items()
        }
