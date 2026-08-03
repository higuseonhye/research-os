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

ArrayLike = Sequence[float] | np.ndarray

#: Arms scored every episode. `D_oracle` is diagnostic and excluded from
#: primary estimates - see the preregistration draft.
EPISODE_ARMS = ("A", "B", "C", "D", "D_oracle")


@dataclass
class EpisodeSpec:
    """Task geometry in physical units. Values come from the calibration pilot."""

    tolerance: float = 0.005
    dispense_latency: int = 6
    interaction_radius: float = 0.05
    min_history: int = 8

    def validate(self) -> None:
        if self.tolerance <= 0.0:
            raise ValueError("tolerance must be > 0")
        if self.dispense_latency < 1:
            raise ValueError("dispense_latency must be >= 1")
        if self.interaction_radius <= 0.0:
            raise ValueError("interaction_radius must be > 0")
        if self.min_history < 4:
            raise ValueError("min_history must be >= 4")


def project_reference_motion(
    history: np.ndarray, horizon: int, estimator: ReferencePatternEstimator
) -> np.ndarray | None:
    """Predict the reference body's displacement over `horizon` steps.

    The estimator reasons about a scalar burst/pause pattern, so the vector
    history is projected onto its own dominant direction of travel, estimated
    there, and re-embedded. A reference that reverses direction within the
    observed window will violate that reduction; the caller sees `None` only
    when the estimator itself declines, so this is a modelling limit worth
    stating rather than a silent failure.
    """

    if len(history) < 2:
        return None
    deltas = np.diff(history, axis=0)
    total = deltas.sum(axis=0)
    norm = float(np.linalg.norm(total))
    if norm <= 0.0:
        return np.zeros(history.shape[1])

    direction = total / norm
    scalar_history = history @ direction
    magnitude = estimator.predict_displacement(list(scalar_history), horizon)
    if magnitude is None:
        return None
    return float(magnitude) * direction


@dataclass
class CommitmentEpisode:
    """Drives one commit-and-dispense attempt from streamed observations.

    Usage per step:  observe(target, reference)  ->  contact_imminent()
    then, at the chosen commit step:  aims()  and later  resolve(true_landing).
    """

    spec: EpisodeSpec = field(default_factory=EpisodeSpec)
    estimator: ReferencePatternEstimator = field(default_factory=ReferencePatternEstimator)
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

    @property
    def ready(self) -> bool:
        return len(self.targets) >= self.spec.min_history

    def motion_expected(self) -> bool:
        """Will the target move during the dispense window?

        This is the eligibility screen: where the target will not move, every
        arm is trivially right and committing there measures nothing. The
        preregistration treats it as a screen, not a result.

        Two regimes qualify, and an earlier version wrongly admitted only the
        first, which silently discarded the cells where the arms differ most:

        1. **Contact coming** - the reference is closing and will arrive inside
           the interaction radius within the dispense window.
        2. **Contact ongoing** - they are already within the interaction radius,
           so the target is being pushed right now.
        """

        if len(self.targets) < 2:
            return False
        target = self.targets[-1]
        reference, previous = self.references[-1], self.references[-2]
        separation = float(np.linalg.norm(target - reference))

        if separation < self.spec.interaction_radius:
            return True

        closing = float(np.linalg.norm(target - previous)) - separation
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

        predicted = project_reference_motion(
            np.asarray(self.references), horizon, self.estimator
        )
        # An unusable estimate falls back to the zero-order aim rather than
        # inventing one. The arm is penalised for it, which is correct.
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
