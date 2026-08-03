"""Relational target dynamics and the relation-adequacy gate for Paper 003.

STATUS: design sketch, 2026-07-31. Not preregistered, not run in Isaac.
Written to make the Paper 003 thresholds decidable on evidence rather than
guessed; see docs/paper003/paper003_description_v0.1.md.

Paper 002 asked whether a missing *dynamic mode* (static vs. drift) justifies a
model-order expansion. Paper 003 asks the next taxonomy cell: a missing
*relation* between two entities. The target's motion is driven by a second body
(`reference`) that intermittently contacts and displaces it.

The discrimination that makes this a separate paper rather than a rerun:

    Paper 002 gate  fires on persistent, directional target motion.
    Paper 003 gate  must fire on motion that is *proximity-conditioned* -
                    episodic, correlated with the reference body's relative
                    state, and NOT well explained by a constant velocity.

A coupling that produced smooth persistent drift would be absorbed by the
Paper 002 constant-velocity arm, and Paper 003 would have no claim. The
relation gate therefore requires positive evidence of proximity conditioning
AND negative evidence against the constant-velocity explanation.

Dimension-agnostic: works for the 2D CPU env (scripts/wm_expansion/env.py) and
the 3D Isaac path (scripts/orbit_reach_drift.py).
"""

from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass, field
from typing import Iterable, Sequence

import numpy as np


ArrayLike = Sequence[float] | np.ndarray


# --------------------------------------------------------------------------
# True (hidden) coupling - the generating process the agent cannot represent
# --------------------------------------------------------------------------


@dataclass
class CouplingSpec:
    """Hidden relational mechanism: reference body displaces the target on contact.

    The agent's initial model class assumes the target is an independent entity,
    so this coupling is unrepresentable, not merely mis-parameterised.
    """

    onset_step: int = 20
    interaction_radius: float = 0.06
    coupling_gain: float = 0.55
    reference_start: np.ndarray | None = None
    reference_velocity: np.ndarray = field(
        default_factory=lambda: np.array([0.012, 0.0], dtype=np.float64)
    )
    duration_steps: int = 40

    def to_dict(self) -> dict:
        return {
            "onset_step": self.onset_step,
            "interaction_radius": self.interaction_radius,
            "coupling_gain": self.coupling_gain,
            "reference_start": (
                None if self.reference_start is None else np.asarray(self.reference_start).tolist()
            ),
            "reference_velocity": np.asarray(self.reference_velocity).tolist(),
            "duration_steps": self.duration_steps,
        }

    def validate(self) -> None:
        if self.interaction_radius <= 0.0:
            raise ValueError("interaction_radius must be > 0")
        if not 0.0 < self.coupling_gain <= 1.0:
            raise ValueError("coupling_gain must be in (0, 1]")
        if self.duration_steps < 1:
            raise ValueError("duration_steps must be >= 1")


def coupling_displacement(
    target: ArrayLike, reference: ArrayLike, spec: CouplingSpec
) -> np.ndarray:
    """Displacement applied to the target by the reference body this step.

    Zero outside the interaction radius - this is what makes the residual
    episodic rather than persistently directional, and is the property the
    relation gate keys on.
    """

    target_arr = np.asarray(target, dtype=np.float64)
    reference_arr = np.asarray(reference, dtype=np.float64)
    if target_arr.shape != reference_arr.shape:
        raise ValueError("target and reference must share a shape")

    offset = target_arr - reference_arr
    distance = float(np.linalg.norm(offset))
    if distance >= spec.interaction_radius or distance == 0.0:
        return np.zeros_like(target_arr)

    # Push along the contact normal, scaled by penetration depth.
    penetration = (spec.interaction_radius - distance) / spec.interaction_radius
    direction = offset / distance
    return spec.coupling_gain * penetration * spec.interaction_radius * direction


def estimate_coupling(
    target_positions: Iterable[ArrayLike],
    reference_positions: Iterable[ArrayLike],
    search_radius: float,
    min_contacts: int = 4,
    motion_floor_ratio: float = 0.25,
    min_fit_quality: float = 0.80,
) -> CouplingSpec | None:
    """Recover the coupling's radius and gain from observation alone.

    Without this, an arm that "predicts the relation" is really being handed
    the generating model: it rolls forward with the same `coupling_gain` and
    `interaction_radius` used to produce the ground truth, and its accuracy
    measures the loan rather than any inference.

    The model is linear in separation, which makes it identifiable. Since
    ``penetration = (radius - d) / radius``,

        |dtarget| = gain * penetration * radius = gain * (radius - d)

    so a least-squares line through the observed (separation, displacement)
    pairs in contact gives ``gain = -slope`` and ``radius = intercept / gain``.

    `search_radius` bounds which steps are considered candidates for contact;
    it is a coarse screen, not the estimate. Returns None when the fit is not
    identifiable - too few contacts, no spread in separation, or coefficients
    outside physical range - so a caller can decline rather than act on noise.
    """

    targets = _paired_array(target_positions)
    references = _paired_array(reference_positions)
    if targets.shape != references.shape or len(targets) < min_contacts + 1:
        return None
    if search_radius <= 0.0:
        raise ValueError("search_radius must be > 0")

    # The displacement between steps i and i+1 is produced by the separation
    # between the target at i and the reference at **i+1** - the reference moves
    # first, then pushes. Pairing against the reference at i instead is an
    # off-by-one that biased the fitted gain by up to 40%.
    deltas = np.linalg.norm(np.diff(targets, axis=0), axis=1)
    separations = np.linalg.norm(targets[:-1] - references[1:], axis=1)

    # A bare `deltas > 0` admits every step once observations carry any noise,
    # dragging the fit toward the far-field points where the true displacement
    # is zero. At 0.1 mm of noise that alone put the gain estimate 68% low, and
    # silently - the fit still succeeded. Require displacement well above the
    # per-episode noise floor instead.
    largest = float(np.max(deltas)) if deltas.size else 0.0
    if largest <= 0.0:
        return None
    moving = deltas >= motion_floor_ratio * largest
    near = separations < search_radius
    contact = moving & near
    if int(np.count_nonzero(contact)) < min_contacts:
        return None

    x = separations[contact]
    y = deltas[contact]
    if float(np.ptp(x)) <= 0.0:
        return None  # no spread in separation; slope is unidentifiable

    slope, intercept = np.polyfit(x, y, 1)
    gain = float(-slope)
    if gain <= 0.0:
        return None  # displacement should fall as separation grows
    radius = float(intercept) / gain
    if not (0.0 < gain <= 1.0) or radius <= 0.0:
        return None

    # A plausible-looking line can still be fitted to points that are mostly
    # noise. Past roughly 1 mm of observation noise the coefficients were still
    # returned while being 70% wrong, which is worse than declining. Require
    # the linear model to actually explain the data.
    residual = float(np.sum((y - (slope * x + intercept)) ** 2))
    total = float(np.sum((y - np.mean(y)) ** 2))
    if total <= 0.0 or 1.0 - residual / total < min_fit_quality:
        return None

    return CouplingSpec(interaction_radius=radius, coupling_gain=gain)


def normal_alignment(
    target_positions: Iterable[ArrayLike],
    reference_positions: Iterable[ArrayLike],
    interaction_radius: float,
    motion_floor_ratio: float = 0.25,
) -> float | None:
    """Mean cosine between observed displacement and the contact normal.

    `estimate_coupling` fits magnitude against separation and never inspects
    direction, so a contact that pushes off-normal - friction being the obvious
    case - returns a **correct** gain and radius while arm D aims the wrong way.
    That failure is invisible in every statistic the runner currently records.

    A CPU study of misspecified contact laws
    (scripts/paper003_contact_robustness.py) found this to be the dominant
    threat under realistic contact: nonlinear penetration laws cost arm D a few
    millimetres, whereas tangential deflection pushed it past the 20 mm
    tolerance while the fitted coefficients still looked perfect.

    Returns 1.0 for a purely normal push, falls toward 0 as the displacement
    turns tangential, and None when there are no usable contact steps. Purely
    diagnostic: nothing gates on it, so recording it cannot change an arm's
    behaviour.
    """

    targets = _paired_array(target_positions)
    references = _paired_array(reference_positions)
    if targets.shape != references.shape or len(targets) < 2:
        return None
    if interaction_radius <= 0.0:
        raise ValueError("interaction_radius must be > 0")

    steps = np.diff(targets, axis=0)
    lengths = np.linalg.norm(steps, axis=1)
    largest = float(np.max(lengths)) if lengths.size else 0.0
    if largest <= 0.0:
        return None

    # Same contact screen as the estimator, so the two describe the same steps.
    offsets = targets[:-1] - references[1:]
    separations = np.linalg.norm(offsets, axis=1)
    usable = (
        (lengths >= motion_floor_ratio * largest)
        & (separations < interaction_radius)
        & (separations > 0.0)
    )
    if not usable.any():
        return None

    normals = offsets[usable] / separations[usable][:, None]
    directions = steps[usable] / lengths[usable][:, None]
    return float(np.mean(np.sum(normals * directions, axis=1)))


# --------------------------------------------------------------------------
# Relation-adequacy gate
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class RelationGateThresholds:
    """Candidate thresholds.

    NOT preregistered. Originally derived 2026-07-31 from a CPU proxy with no
    contact noise, which produced an unrealistically clean `proximity_contrast`
    of exactly 1.0. **Re-derived 2026-08-04 from the 40-record Isaac v5 sweep**
    (`scripts/paper003_gate_characterisation.py`), which found two things:

    `min_proximity_contrast` is not doing fitted work. Every value from 0.30 to
    0.90 separates the treatment from all three controls identically, with the
    coupled fire rate moving only 0.91 -> 0.80 across that range. 0.50 sits in
    the middle of the plateau.

    `max_constant_velocity_gain` is **untested**. Across all 2,960 decidable
    steps of the sweep, zero passed the contrast test and were then rejected by
    this clause. The `drift` control is degenerate - its target runs along the
    reference's axis at the reference's speed, so the reference never came
    within 92 mm and the gate rejects it merely for want of anything nearby.

    The case that would collapse Paper 003 into Paper 002 is a target that is
    genuinely struck and then *slides on at constant velocity*, which real rigid
    contact produces. On that case this gate leaks: it still fires on 14-19% of
    steps in the near-frictionless limit, against H3's 10% ceiling. The `slide`
    condition in `orbit_reach_relation_pilot.py` exists to measure it under
    Isaac, and the thresholds are not adjusted to accommodate the result.

    Observed on the original CPU proxy (5 seeds each), retained for provenance:

        case          contrast   cv_gain
        coupling        +1.000    -0.036     <- must fire
        drift (P002)    -1.000    +0.807     <- must not (arm C explains it)
        static           0.000     0.000     <- must not
        obs noise       -1.000     0.000     <- must not
    """

    min_deltas: int = 6
    speed_floor: float = 5e-4
    # Positive evidence: target moves when the reference body is near, not when
    # it is far. Separates coupling (+1.0) from drift and noise (-1.0).
    min_proximity_contrast: float = 0.50
    # Negative evidence against the Paper 002 explanation: a constant-velocity
    # model must NOT already account for the motion. Separates coupling
    # (cv_gain ~= 0) from persistent drift (cv_gain ~= 0.8), which is arm C's case.
    max_constant_velocity_gain: float = 0.30

    def validate(self) -> None:
        if self.min_deltas < 3:
            raise ValueError("min_deltas must be >= 3")
        if self.speed_floor <= 0.0:
            raise ValueError("speed_floor must be > 0")
        if not -1.0 <= self.min_proximity_contrast <= 1.0:
            raise ValueError("min_proximity_contrast must be in [-1, 1]")
        if not 0.0 <= self.max_constant_velocity_gain <= 1.0:
            raise ValueError("max_constant_velocity_gain must be in [0, 1]")


@dataclass(frozen=True)
class RelationGateDecision:
    fired: bool
    n_deltas: int
    proximity_contrast: float
    constant_velocity_gain: float
    directional_consistency: float
    near_fraction: float
    mean_speed: float

    def to_dict(self) -> dict[str, float | int | bool]:
        return asdict(self)


def _paired_array(values: Iterable[ArrayLike]) -> np.ndarray:
    array = np.asarray(list(values), dtype=np.float64)
    if array.size == 0:
        return np.empty((0, 0), dtype=np.float64)
    if array.ndim != 2:
        raise ValueError("expected shape [time, dim]")
    if not np.isfinite(array).all():
        raise ValueError("values must be finite")
    return array


def _constant_velocity_gain(target_arr: np.ndarray, horizon: int) -> float:
    """Fraction of zero-order H-step error that a constant-velocity model removes.

    High for persistent drift (Paper 002's case, handled by arm C); near zero for
    proximity-driven bumps, whose direction reverses and whose quiet gaps a
    velocity extrapolation overshoots.
    """

    if len(target_arr) <= horizon:
        return 0.0

    zero_errors = []
    cv_errors = []
    velocity = np.zeros(target_arr.shape[1], dtype=np.float64)
    for index in range(len(target_arr) - horizon):
        if index > 0:
            velocity = target_arr[index] - target_arr[index - 1]
        truth = target_arr[index + horizon]
        zero_errors.append(float(np.linalg.norm(target_arr[index] - truth)))
        cv_errors.append(float(np.linalg.norm(target_arr[index] + horizon * velocity - truth)))

    zero_mean = float(np.mean(zero_errors))
    if zero_mean <= 0.0:
        return 0.0
    return float((zero_mean - float(np.mean(cv_errors))) / zero_mean)


def evaluate_relation_gate(
    target_positions: Iterable[ArrayLike],
    reference_positions: Iterable[ArrayLike],
    thresholds: RelationGateThresholds,
    interaction_radius: float = 0.05,
    horizon: int = 10,
) -> RelationGateDecision:
    """Test whether target motion is proximity-conditioned on the reference body.

    Requires *both* positive evidence (the target moves when the reference is
    near and not when it is far) and negative evidence against the Paper 002
    explanation (a constant-velocity model does not already account for the
    motion). Without the second condition, any coupling that happened to look
    like smooth drift would trigger a relational claim that arm C could equally
    well satisfy, and the paper would have no contribution over Paper 002.
    """

    thresholds.validate()
    target_arr = _paired_array(target_positions)
    reference_arr = _paired_array(reference_positions)
    if target_arr.shape != reference_arr.shape:
        raise ValueError("target and reference histories must align in shape")
    if interaction_radius <= 0.0:
        raise ValueError("interaction_radius must be > 0")

    empty = RelationGateDecision(False, 0, 0.0, 0.0, 0.0, 0.0, 0.0)
    if len(target_arr) < 2:
        return empty

    deltas = np.diff(target_arr, axis=0)
    n_deltas = int(len(deltas))
    speeds = np.linalg.norm(deltas, axis=1)
    mean_speed = float(np.mean(speeds))

    speed_sum = float(np.sum(speeds))
    directional_consistency = (
        float(np.linalg.norm(np.sum(deltas, axis=0)) / speed_sum) if speed_sum > 0.0 else 0.0
    )

    # Positive evidence: speed contrast between near and far separations.
    separations = np.linalg.norm(target_arr - reference_arr, axis=1)[:-1]
    near = separations < interaction_radius
    near_fraction = float(np.mean(near))
    speed_near = float(np.mean(speeds[near])) if near.any() else 0.0
    speed_far = float(np.mean(speeds[~near])) if (~near).any() else 0.0
    denominator = speed_near + speed_far
    proximity_contrast = (
        float((speed_near - speed_far) / denominator) if denominator > 0.0 else 0.0
    )

    # Negative evidence: does constant velocity already explain this?
    cv_gain = _constant_velocity_gain(target_arr, horizon)

    fired = bool(
        n_deltas >= thresholds.min_deltas
        and mean_speed >= thresholds.speed_floor
        and proximity_contrast >= thresholds.min_proximity_contrast
        and cv_gain <= thresholds.max_constant_velocity_gain
    )
    return RelationGateDecision(
        fired=fired,
        n_deltas=n_deltas,
        proximity_contrast=proximity_contrast,
        constant_velocity_gain=cv_gain,
        directional_consistency=directional_consistency,
        near_fraction=near_fraction,
        mean_speed=mean_speed,
    )


# --------------------------------------------------------------------------
# Arm D: relation-module target model
# --------------------------------------------------------------------------


class RelationalTargetModel:
    """L3-relation model: predicts target motion as a function of the reference body.

    Structurally distinct from both Paper 002 arms in the same way arm C was
    distinct from arm B: no parameter setting of a zero-order or
    constant-velocity model can make the prediction depend on a second entity's
    position. Before the gate fires this degrades to the zero-order prediction,
    so activation is the only thing being tested.
    """

    def __init__(
        self,
        position_alpha: float = 1.0,
        coupling_alpha: float = 0.5,
        gate_thresholds: RelationGateThresholds | None = None,
        gate_window: int = 12,
        interaction_radius: float = 0.06,
    ) -> None:
        if not 0.0 < position_alpha <= 1.0:
            raise ValueError("position_alpha must be in (0, 1]")
        if not 0.0 < coupling_alpha <= 1.0:
            raise ValueError("coupling_alpha must be in (0, 1]")
        if gate_window < 4:
            raise ValueError("gate_window must be >= 4")
        if interaction_radius <= 0.0:
            raise ValueError("interaction_radius must be > 0")

        self.position_alpha = float(position_alpha)
        self.coupling_alpha = float(coupling_alpha)
        self.interaction_radius = float(interaction_radius)
        self.gate_thresholds = gate_thresholds or RelationGateThresholds()
        self.gate_thresholds.validate()

        self.position: np.ndarray | None = None
        self.reference: np.ndarray | None = None
        self.reference_velocity: np.ndarray | None = None
        self.coupling_gain = 0.0
        self.target_history: deque[np.ndarray] = deque(maxlen=int(gate_window) + 1)
        self.reference_history: deque[np.ndarray] = deque(maxlen=int(gate_window) + 1)
        self.gate_decision = RelationGateDecision(False, 0, 0.0, 0.0, 0.0, 0.0, 0.0)

    def observe(self, target: ArrayLike, reference: ArrayLike) -> None:
        target_arr = np.asarray(target, dtype=np.float64)
        reference_arr = np.asarray(reference, dtype=np.float64)
        if target_arr.shape != reference_arr.shape:
            raise ValueError("target and reference must share a shape")

        prev_target = self.target_history[-1] if self.target_history else None
        prev_reference = self.reference_history[-1] if self.reference_history else None

        if self.position is None:
            self.position = target_arr.copy()
        else:
            self.position = (
                self.position_alpha * target_arr + (1.0 - self.position_alpha) * self.position
            )
        self.reference = reference_arr.copy()

        if prev_reference is not None:
            velocity = reference_arr - prev_reference
            self.reference_velocity = (
                velocity
                if self.reference_velocity is None
                else self.coupling_alpha * velocity
                + (1.0 - self.coupling_alpha) * self.reference_velocity
            )

        # Online estimate of coupling strength from observed in-contact steps.
        if prev_target is not None and prev_reference is not None:
            separation = float(np.linalg.norm(prev_target - prev_reference))
            if separation < self.interaction_radius and separation > 0.0:
                observed = float(np.linalg.norm(target_arr - prev_target))
                penetration = (self.interaction_radius - separation) / self.interaction_radius
                scale = penetration * self.interaction_radius
                if scale > 0.0:
                    estimate = observed / scale
                    self.coupling_gain = (
                        self.coupling_alpha * estimate
                        + (1.0 - self.coupling_alpha) * self.coupling_gain
                    )

        self.target_history.append(target_arr.copy())
        self.reference_history.append(reference_arr.copy())
        self.gate_decision = evaluate_relation_gate(
            self.target_history,
            self.reference_history,
            self.gate_thresholds,
            interaction_radius=self.interaction_radius,
        )

    @property
    def gate_fired(self) -> bool:
        return self.gate_decision.fired

    def predict(self, horizon: int) -> np.ndarray:
        """Roll the relation forward: advance the reference, re-apply coupling."""

        if horizon < 0:
            raise ValueError("horizon must be >= 0")
        if self.position is None:
            raise RuntimeError("observe must be called before predict")
        if not self.gate_fired or self.reference is None or self.reference_velocity is None:
            return self.position.copy()

        target = self.position.copy()
        reference = self.reference.copy()
        spec = CouplingSpec(
            interaction_radius=self.interaction_radius,
            coupling_gain=float(np.clip(self.coupling_gain, 1e-6, 1.0)),
        )
        for _ in range(horizon):
            reference = reference + self.reference_velocity
            target = target + coupling_displacement(target, reference, spec)
        return target
