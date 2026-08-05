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
    references = _reference_array(reference_positions)
    if len(targets) != len(references) or len(targets) < min_contacts + 1:
        return None
    if search_radius <= 0.0:
        raise ValueError("search_radius must be > 0")

    # The displacement between steps i and i+1 is produced by the separation
    # between the target at i and the reference at **i+1** - the reference moves
    # first, then pushes. Pairing against the reference at i instead is an
    # off-by-one that biased the fitted gain by up to 40%.
    #
    # With more than one body, the separation is to whichever is nearest. That
    # is what lets one coupling be fitted from contacts with several bodies -
    # the point of the two-body encounter, where the relation is demonstrated by
    # one body and applied to another.
    deltas = np.linalg.norm(np.diff(targets, axis=0), axis=1)
    separations, _ = _nearest_reference(targets[:-1], references[1:])

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
    references = _reference_array(reference_positions)
    if len(targets) != len(references) or len(targets) < 2:
        return None
    if interaction_radius <= 0.0:
        raise ValueError("interaction_radius must be > 0")

    steps = np.diff(targets, axis=0)
    lengths = np.linalg.norm(steps, axis=1)
    largest = float(np.max(lengths)) if lengths.size else 0.0
    if largest <= 0.0:
        return None

    # Same contact screen as the estimator, so the two describe the same steps.
    separations, nearest = _nearest_reference(targets[:-1], references[1:])
    offsets = targets[:-1] - references[1:][np.arange(len(nearest)), nearest]
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
    # Evidence from before the first contact is not evidence. A target that has
    # not yet been touched is still because nothing has happened to it, not
    # because contact ended and it stopped - yet the far-field class was being
    # filled with exactly those steps, which inflated `proximity_contrast`
    # toward +1 for any target that had ever been struck.
    #
    # Measured trial-by-trial, that made the gate fire on **100% of trials in
    # every condition**, including a frictionless slide that a constant-velocity
    # model explains outright. The per-step rate of 12-16% concealed it: firing
    # on one step in eight still means firing somewhere in every trial, and H3
    # is stated per trial.
    #
    # Restricting the contrast to the first contact onward, and refusing to
    # decide until enough far-field steps have accrued *after* it, separates
    # them completely - treatment 1.00, frictionless slide 0.00.
    contrast_from_first_contact: bool = True
    # A separate threshold set for the capture relation was written and then
    # deleted. The reasoning behind it was that capture inverts the evidence:
    # the body never leaves, so there is no post-contact far-field period and
    # restricting the contrast to one should make the gate abstain.
    #
    # That reasoning was right. It was recorded as refuted on 2026-08-04 by a
    # measurement showing 20 usable far-field deltas and a 1.00 fire rate, and
    # both came from an off-by-one in `capture_displacement` that threw a
    # captured target one body-step past its carrier: the riding separation
    # landed outside the radius, the near-field allowance covered it during
    # motion but not during a pause, and the pauses sorted into the far field.
    # With that fixed the contrast has nothing to compare on any capture cell,
    # in any of 20 rollouts.
    #
    # One gate still covers both relations, but not by sharing this statistic -
    # by admitting a second form of positive evidence that does not need a far
    # field at all. See `min_carriage_agreement`.
    # Compare net displacement per step rather than mean per-step speed. A still
    # target under observation noise moves every step but goes nowhere, so its
    # path length grows with the window while its net displacement does not.
    # Keeping the old statistic left the gate usable only at implausibly clean
    # observations - coupled contrast 0.47 at 0.5 mm of noise, 0.04 at 5 mm,
    # against 0.86 and 0.66 for this one. Since the real noise has never been
    # measured, the gate should not depend on it being small.
    contrast_uses_displacement: bool = True
    # Count a step as near if the body could have been within the radius at any
    # point during it, allowing for how far it moved since the last observation.
    #
    # A body travelling further per step than the radius crosses the
    # neighbourhood between observations, so both samples show it far even
    # though it was near. Calling that step "far" is an artefact of discrete
    # sampling, not a fact about the world, and it is the same correction
    # `estimate_stopping` already makes.
    #
    # It cannot manufacture a relation on its own: the contrast also requires
    # the target to have *moved* in those steps, and a fly-by that never touches
    # leaves it still. Pinned by a test.
    proximity_allows_travel: bool = True
    # A statistic crossing a threshold once is a draw, not evidence. With ~70
    # prefixes evaluated per episode, the observation-noise control crossed by
    # chance in 0.30 of trials against H3's 0.10 ceiling; requiring two
    # consecutive crossings put it at 0.00 with the treatment still at 1.00.
    min_consecutive_fires: int = 2
    # One is the minimum that makes the contrast non-degenerate, and it is also
    # what holds up best as observation noise rises: with the target still after
    # contact, every far-field sample is pure noise, so demanding more of them
    # buys nothing and costs firing rate. See the noise sweep in the gate
    # characterisation - the whole discriminating power lies in requiring at
    # least one, not in requiring several.
    min_post_contact_far_deltas: int = 1
    # Positive evidence: target moves when the reference body is near, not when
    # it is far. Separates coupling (+1.0) from drift and noise (-1.0).
    min_proximity_contrast: float = 0.50
    # Negative evidence against the Paper 002 explanation: a constant-velocity
    # model must NOT already account for the motion. Separates coupling
    # (cv_gain ~= 0) from persistent drift (cv_gain ~= 0.8), which is arm C's case.
    #
    # Applies to *both* forms of positive evidence, and that is what makes the
    # second one safe. The `drift` control's target runs along the first body's
    # own axis at its own speed, so its displacement agrees with that body's on
    # 0.71 of moving steps under a burst schedule - it would pass a carriage
    # test outright. Its cv_gain is 0.99, and this clause is what rejects it.
    max_constant_velocity_gain: float = 0.89
    """Re-derived 2026-08-05 for the one-step statistic, and 0.30 did not transfer.

    The old value belonged to an H-step `cv_gain` that decayed with the horizon,
    so a threshold calibrated at `dispense_latency` 6 stopped rejecting the
    steadily-closing pusher at 8 - the control the clause exists for - while the
    motion was unchanged. Carrying the number across to a different statistic is
    the mistake that document is about.

    Derived the way `min_proximity_contrast` was, and by a rule fixed before the
    measurement: the interval of thresholds separating treatment from every
    control identically, then its midpoint. Measured over 40 seeds each,

        highest admitted   0.796   (capture under burst)
        lowest rejected    0.985   (post-contact slide)

    so the plateau is [0.796, 0.985) and its midpoint is 0.89. Collision sits far
    below at 0.060 and drift at 1.000, and the separation is identical at every
    horizon from 4 to 12, which is the property the replacement was written for.
    """
    # Second admissible form of positive evidence: the target's displacement is
    # a *body's* displacement. Required because the proximity contrast cannot
    # see a capture at all - a carrier that never leaves supplies no far field,
    # so the contrast abstains on every capture cell however it is tuned, and
    # with it arm D never acts and scores exactly arm B.
    #
    # This is not a second gate and not a relation-specific threshold set. It is
    # one more way for the same gate to find positive evidence, and every other
    # clause - the constant-velocity ceiling above all - applies unchanged.
    #
    # 0.80 rather than something near 1.0 leaves room for contact jitter, and
    # sits clear of the highest a control reaches: `drift` under burst at 0.71.
    min_carriage_agreement: float = 0.80
    # And the run, for the reason `estimate_capture` requires one: a struck
    # target has an equilibrium separation where the push equals the body's own
    # advance, and there collision and carriage are momentarily the same
    # observation. Three consecutive steps is what a collision passes through
    # and a carry does not.
    min_carriage_run: int = 3

    def validate(self) -> None:
        if self.min_deltas < 3:
            raise ValueError("min_deltas must be >= 3")
        if self.speed_floor <= 0.0:
            raise ValueError("speed_floor must be > 0")
        if not -1.0 <= self.min_proximity_contrast <= 1.0:
            raise ValueError("min_proximity_contrast must be in [-1, 1]")
        if not 0.0 <= self.max_constant_velocity_gain <= 1.0:
            raise ValueError("max_constant_velocity_gain must be in [0, 1]")
        if self.min_post_contact_far_deltas < 0:
            raise ValueError("min_post_contact_far_deltas must be >= 0")
        if self.min_consecutive_fires < 1:
            raise ValueError("min_consecutive_fires must be >= 1")
        if not 0.0 <= self.min_carriage_agreement <= 1.0:
            raise ValueError("min_carriage_agreement must be in [0, 1]")
        if self.min_carriage_run < 1:
            raise ValueError("min_carriage_run must be >= 1")


@dataclass(frozen=True)
class RelationGateDecision:
    fired: bool
    n_deltas: int
    proximity_contrast: float
    constant_velocity_gain: float
    directional_consistency: float
    near_fraction: float
    mean_speed: float
    #: Far-field steps observed *after* the first contact. Zero means the
    #: contrast has nothing to compare against and the proximity path abstains.
    post_contact_far_deltas: int = 0
    #: Fraction of moving steps whose displacement is some body's displacement,
    #: and the longest run of it with a single body. The carriage path.
    carriage_agreement: float = 0.0
    carriage_run: int = 0
    #: Which form of positive evidence fired, for diagnosis. A capture cell that
    #: reports "proximity" is measuring something other than the carry.
    evidence: str = "none"

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


def _reference_array(values: Iterable[ArrayLike]) -> np.ndarray:
    """Normalise reference history to ``[time, body, dim]``.

    The two-body encounter needs more than one reference: the relation is
    demonstrated by a body that then leaves, and applied to a different body
    that arrives later. A single-body history is accepted unchanged and simply
    reports one body, so every existing caller keeps working.
    """

    array = np.asarray(list(values), dtype=np.float64)
    if array.size == 0:
        return np.empty((0, 0, 0), dtype=np.float64)
    if array.ndim == 2:
        array = array[:, None, :]
    if array.ndim != 3:
        raise ValueError("expected shape [time, dim] or [time, body, dim]")
    if not np.isfinite(array).all():
        raise ValueError("values must be finite")
    return array


def _nearest_reference(
    targets: np.ndarray, references: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Per timestep, the separation to the closest body and that body's index.

    Only the closest body can be in contact - the interaction radius is smaller
    than the separation the encounter keeps between bodies - so "the reference"
    in every statistic below means the nearest one at that instant. Pooling all
    bodies instead would let a distant body's stillness dilute a real contact.
    """

    if targets.shape[0] != references.shape[0]:
        raise ValueError("target and reference histories must align in time")
    offsets = targets[:, None, :] - references
    distances = np.linalg.norm(offsets, axis=2)
    index = np.argmin(distances, axis=1)
    return distances[np.arange(len(distances)), index], index


def _contiguous_runs(mask: np.ndarray) -> list[tuple[int, int]]:
    """Half-open [start, end) index ranges over which `mask` stays True."""

    runs: list[tuple[int, int]] = []
    index = 0
    while index < len(mask):
        if not mask[index]:
            index += 1
            continue
        end = index
        while end < len(mask) and mask[end]:
            end += 1
        runs.append((index, end))
        index = end
    return runs


def _displacement_rate(points: np.ndarray, mask: np.ndarray, window: int = 3) -> float | None:
    """Net displacement per step over fixed `window`-step spans inside each run.

    Not mean per-step speed, and the difference is the gate's whole tolerance
    for observation noise. A still target under noise moves every step but goes
    nowhere: its path length grows with the span while its net displacement
    stays at the noise scale. Per-step speed cannot tell that from slow genuine
    motion, so the far-field term floors at the noise level and the contrast
    collapses - measured, from 0.47 at 0.5 mm of noise to 0.04 at 5 mm. This
    statistic holds the same comparison at 0.86 and 0.66.

    The window is **fixed rather than each run's own length**, and that is not a
    detail. Dividing a run's total displacement by its own length makes short
    runs look fast, which independent observation noise exploits directly:
    contact spans are short and far-field spans are long, so the noise control
    fired on 90% of trials until both classes were measured at the same scale.

    Recorded contact spans in the pilot run 6 to 15 steps, so a 3-step window
    fits inside them with room to spare.
    """

    if window < 1:
        raise ValueError("window must be >= 1")
    rates = [
        float(np.linalg.norm(points[start + window] - points[start])) / window
        for run_start, run_end in _contiguous_runs(mask)
        for start in range(run_start, run_end - window + 1)
    ]
    return float(np.mean(rates)) if rates else None


def _constant_velocity_gain(target_arr: np.ndarray, horizon: int = 1) -> float:
    """Fraction of zero-order **one-step** error a constant-velocity model removes.

    High for persistent drift (Paper 002's case, handled by arm C); near zero for
    proximity-driven bumps, whose direction reverses and whose quiet gaps a
    velocity extrapolation overshoots.

    **`horizon` is accepted and ignored, deliberately.** The previous version
    extrapolated the last one-step velocity `horizon` steps and compared H-step
    errors, which made the statistic decay with the horizon on any curving
    trajectory - a longer extrapolation overshoots further, so a
    constant-velocity model looks worse the further ahead it is asked. On the
    steadily-closing pusher, the control built for this clause, the same
    unchanged motion gave +0.406 at horizon 6 and +0.219 at horizon 8, crossing
    the 0.30 ceiling without moving.

    That mattered because the physical scene forces `dispense_latency` to 8, so a
    threshold calibrated at 6 silently stopped rejecting the case it exists to
    reject. The horizon was being measured alongside the motion; asking one step
    ahead removes it from the expression entirely.

    See docs/paper003/paper003_cv_gain_horizon_v0.1.md. The parameter is kept in
    the signature so existing callers need no change and so that the ignoring is
    visible here rather than at every call site.
    """

    del horizon  # see above: measuring it was the defect
    if len(target_arr) < 3:
        return 0.0

    steps = np.diff(target_arr, axis=0)
    zero_errors = np.linalg.norm(steps[1:], axis=1)
    cv_errors = np.linalg.norm(steps[1:] - steps[:-1], axis=1)
    zero_mean = float(np.mean(zero_errors)) if zero_errors.size else 0.0
    if zero_mean <= 0.0:
        return 0.0
    return float((zero_mean - float(np.mean(cv_errors))) / zero_mean)


def gate_fired_persistently(
    target_positions: Iterable[ArrayLike],
    reference_positions: Iterable[ArrayLike],
    thresholds: RelationGateThresholds,
    interaction_radius: float = 0.05,
    horizon: int = 10,
) -> bool:
    """Has the gate fired on the last `min_consecutive_fires` prefixes running?

    A single crossing is not evidence of a relation; it is one draw of a
    statistic. Under the observation-noise control the target jitters
    independently every step, and with roughly seventy prefixes evaluated per
    episode some prefix will cross any fixed threshold by chance - that alone
    put the noise control at 0.30 of trials, against H3's 0.10 ceiling. Two
    consecutive crossings put it at 0.00 while leaving the treatment at 1.00.

    Kept as a separate function so `evaluate_relation_gate` stays pure and its
    statistics remain readable per step for diagnosis.
    """

    targets = list(target_positions)
    references = list(reference_positions)
    needed = max(1, thresholds.min_consecutive_fires)
    if len(targets) < needed:
        return False
    return all(
        evaluate_relation_gate(
            targets[: len(targets) - back],
            references[: len(references) - back],
            thresholds,
            interaction_radius=interaction_radius,
            horizon=horizon,
        ).fired
        for back in range(needed)
    )


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
    reference_arr = _reference_array(reference_positions)
    if len(target_arr) != len(reference_arr):
        raise ValueError("target and reference histories must align in time")
    if reference_arr.size and target_arr.shape[1] != reference_arr.shape[2]:
        raise ValueError("target and reference must share a dimension")
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
    # "Near" means near the closest body: with two bodies the target is in
    # contact whenever either is within the radius, and a distant body must not
    # make a real contact look far.
    all_separations, nearest_body = _nearest_reference(target_arr, reference_arr)
    separations = all_separations[:-1]
    allowance = np.zeros_like(separations)
    if thresholds.proximity_allows_travel and len(reference_arr) > 1:
        # The *nearest* body's own travel, not the smallest across bodies: it is
        # the one whose crossing could have been missed.
        body_steps = np.linalg.norm(np.diff(reference_arr, axis=0), axis=2)
        index = nearest_body[: len(separations)]
        allowance = body_steps[np.arange(len(index)), index]
    near = separations < interaction_radius + allowance
    near_fraction = float(np.mean(near))

    # Only evidence gathered from the first contact onward can distinguish "the
    # target stops when the reference leaves" from "the target had not been
    # touched yet". Both look like a still target beside a distant reference.
    contrast_near, contrast_speeds = near, speeds
    contrast_points = target_arr
    if thresholds.contrast_from_first_contact and near.any():
        first_contact = int(np.argmax(near))
        contrast_near = near[first_contact:]
        contrast_speeds = speeds[first_contact:]
        contrast_points = target_arr[first_contact:]
    post_contact_far = int(np.count_nonzero(~contrast_near)) if near.any() else 0

    if thresholds.contrast_uses_displacement:
        rate_near = _displacement_rate(contrast_points, contrast_near)
        rate_far = _displacement_rate(contrast_points, ~contrast_near)
        # A class with no run long enough to measure contributes nothing rather
        # than a zero, which would read as strong evidence for the other side.
        speed_near = rate_near if rate_near is not None else 0.0
        speed_far = rate_far if rate_far is not None else 0.0
        measurable = rate_near is not None and rate_far is not None
    else:
        speed_near = (
            float(np.mean(contrast_speeds[contrast_near])) if contrast_near.any() else 0.0
        )
        speed_far = (
            float(np.mean(contrast_speeds[~contrast_near])) if (~contrast_near).any() else 0.0
        )
        measurable = True

    denominator = speed_near + speed_far
    proximity_contrast = (
        float((speed_near - speed_far) / denominator) if denominator > 0.0 else 0.0
    )

    # Negative evidence: does constant velocity already explain this?
    cv_gain = _constant_velocity_gain(target_arr, horizon)

    # Positive evidence, in two admissible forms. The first is proximity
    # conditioning; the second is that the target's displacement is a second
    # body's own displacement. A capture has only the second, because its
    # carrier never leaves and there is no far field to contrast against.
    proximity_evidence = bool(
        proximity_contrast >= thresholds.min_proximity_contrast
        # With no far-field steps after contact the contrast has nothing to
        # compare against and reads +1.0 by construction. Abstain instead.
        and (
            not thresholds.contrast_from_first_contact
            or post_contact_far >= thresholds.min_post_contact_far_deltas
        )
        # Both classes must contain a run long enough to measure a displacement
        # rate; otherwise the contrast is comparing against a fabricated zero.
        and measurable
    )
    carriage_agreement, carriage_run = carriage_evidence(
        target_arr, reference_arr, interaction_radius=interaction_radius
    )
    carriage = bool(
        carriage_agreement >= thresholds.min_carriage_agreement
        and carriage_run >= thresholds.min_carriage_run
    )

    # Each form of positive evidence carries its own negative evidence, because
    # one clause cannot serve both. The constant-velocity ceiling was derived
    # where the treatment is episodic; a captured target rides smoothly and is
    # *more* constant-velocity than a sustained push, so applying it to the
    # carriage path admits nothing the design wants. Contact does that work
    # there instead - see `carriage_evidence`.
    #
    # What this gives up is stated rather than hidden: the gate now fires on a
    # sustained push, where a relation is present and the mode operator already
    # suffices. That is H2's question - arm D must beat arm C by a margin - and
    # H2 tests it on outcomes rather than on a threshold being right.
    fired = bool(
        n_deltas >= thresholds.min_deltas
        and mean_speed >= thresholds.speed_floor
        and (
            (proximity_evidence and cv_gain <= thresholds.max_constant_velocity_gain)
            or carriage
        )
    )
    return RelationGateDecision(
        fired=fired,
        n_deltas=n_deltas,
        proximity_contrast=proximity_contrast,
        constant_velocity_gain=cv_gain,
        directional_consistency=directional_consistency,
        near_fraction=near_fraction,
        mean_speed=mean_speed,
        post_contact_far_deltas=post_contact_far,
        carriage_agreement=carriage_agreement,
        carriage_run=carriage_run,
        evidence=(
            "proximity" if proximity_evidence else "carriage" if carriage else "none"
        ),
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


# --------------------------------------------------------------------------
# Capture: the reference arrives at a still target and carries it away
# --------------------------------------------------------------------------


@dataclass
class CaptureSpec:
    """The relation the paper is actually about.

    Two other relations were measured and rejected, and the reasons are the
    design (see docs/paper003/paper003_capture_design_v0.1.md):

    **Collision** - struck and released - makes the relation necessary, since
    nothing in a still target's history predicts an approaching body. But the
    push moves the target away, which reduces penetration, which reduces the
    push, so displacement per contact is on the order of the interaction radius
    and never clears the placement tolerance. Measured five independent ways.

    **Carriage** - riding throughout - clears the tolerance easily, and fails
    the paper's central claim: a single-entity model that learns the burst
    pattern of the *target's own* trajectory matches the relational arm exactly.
    The relation is not necessary, so H2 fails.

    **Capture** has neither failure. Before the arrival the target is still, so
    its own history says nothing; afterwards it rides, so the effect accumulates
    without bound.
    """

    capture_radius: float = 0.012
    """Separation at which the reference takes hold. Once held, held."""

    def validate(self) -> None:
        if self.capture_radius <= 0.0:
            raise ValueError("capture_radius must be > 0")


def capture_displacement(
    target: ArrayLike,
    reference: ArrayLike,
    reference_step: ArrayLike,
    spec: CaptureSpec,
    held: bool,
) -> tuple[np.ndarray, bool]:
    """The target's displacement this step, and whether it is now held.

    `reference_step` is the reference's own displacement this step, which is
    what a held target inherits. Before capture the target does not move at all
    - not a small push, nothing - which is exactly what makes its own history
    uninformative and the relation necessary.

    **The step it takes hold on is not a carrying step.** `reference` is the
    body where it now is, having already moved; the target is where it still
    is. Handing it the body's step as well moved it away from its carrier by
    exactly that step, so a target captured at 49.9 mm rode at 64.7 mm - outside
    the radius it was captured at, permanently, and by a margin that grows with
    the approach speed. That put a false arrival in every burst cycle for
    anything reading separations, `contact_arrivals` included.
    """

    spec.validate()
    target_arr = np.asarray(target, dtype=np.float64)
    reference_arr = np.asarray(reference, dtype=np.float64)
    step_arr = np.asarray(reference_step, dtype=np.float64)
    if target_arr.shape != reference_arr.shape or target_arr.shape != step_arr.shape:
        raise ValueError("target, reference and step must share a shape")

    if not held:
        separation = float(np.linalg.norm(target_arr - reference_arr))
        if separation >= spec.capture_radius:
            return np.zeros_like(target_arr), False
        return np.zeros_like(target_arr), True
    return step_arr.copy(), True


def _ride_mask(
    targets: np.ndarray,
    references: np.ndarray,
    motion_floor_ratio: float,
    agreement: float,
    interaction_radius: float | None = None,
    min_ride_steps: int = 3,
) -> tuple[np.ndarray, np.ndarray] | None:
    """``[step, body]`` - did the target move by what this body moved by.

    Shared by `estimate_capture` and the gate's carriage evidence so the two
    cannot drift apart: what the gate admits as a carry must be the same thing
    the arm then estimates from, or the arm is licensed to act on a relation it
    cannot fit. Returns the mask and the per-step mask of *moving* steps, or
    None when the target never moved and there is nothing to attribute.
    """

    target_steps = np.diff(targets, axis=0)
    lengths = np.linalg.norm(target_steps, axis=1)
    largest = float(np.max(lengths)) if lengths.size else 0.0
    if largest <= 0.0:
        return None
    moving = lengths >= motion_floor_ratio * largest
    if not moving.any():
        return None
    mismatch = np.linalg.norm(np.diff(references, axis=0) - target_steps[:, None, :], axis=2)
    rides = moving[:, None] & (mismatch <= agreement * lengths[:, None])

    # A carry keeps its distance, and agreeing step by step does not imply it.
    # The per-step test tolerates `agreement` of the target's own step, so a
    # target losing a fraction of a millimetre every step scores near-perfect
    # agreement while drifting arbitrarily far - measured in the Isaac pilot,
    # objects "carried" at 0.98 over a run of 111 had reached separations of
    # 50 to 209 mm from the arm supposedly holding them.
    #
    # **Bounded, not small.** An earlier version required the separation to stay
    # inside the interaction radius, and that rejected a cell holding at a
    # perfectly constant 3.35 mm - `ee_frame` is a virtual point between the
    # jaws, so an object genuinely held sits a few millimetres from it by
    # construction. What distinguishes carrying is that the separation does not
    # *grow*, whatever its value.
    #
    # So: the share of the carrier's motion the target failed to inherit,
    # measured over each body's ride and bounded by `agreement` - the same
    # quarter that is already declared acceptable per step, now applied to the
    # run, which is where it was accumulating without limit. See
    # docs/paper003/paper003_carry_is_not_slip_v0.1.md.
    # A release needs to persist, exactly as a ride does.
    #
    # `min_ride_steps` consecutive agreeing steps are required before a carry is
    # believed; one *disagreeing* step was enough to end it. That asymmetry
    # fragmented real carries - a single noisy step split a 178-step ride into
    # pieces, and then the pieces failed twice over: too short to make a run,
    # and starting after the object had drifted, so with no moment of contact
    # in them. Measured, it put 23 of 24 physical captures into `collision`,
    # under two different reasons that were the same defect.
    #
    # So gaps shorter than `min_ride_steps` do not break a ride. Nothing new is
    # introduced: it is the same number, applied to the other direction.
    # Only *moving* steps can agree or disagree; a pause neither breaks a ride
    # nor bridges one, so the gap is measured over moving steps alone. Filling
    # non-moving steps instead marks a stationary target as riding, which broke
    # nine tests when it was tried.
    moving_at = np.flatnonzero(moving)
    for body in range(rides.shape[1]):
        agreeing = rides[moving_at, body]
        for start, stop in _runs(~agreeing):
            if 0 < start and stop < len(agreeing) - 1 and stop - start + 1 < min_ride_steps:
                rides[moving_at[start : stop + 1], body] = True

    separations = np.linalg.norm(references - targets[:, None, :], axis=2)
    for body in range(rides.shape[1]):
        for start, stop in _runs(rides[:, body]):
            # Taking hold comes *before* riding, so contact is looked for up to
            # the run rather than inside it.
            #
            # Traced step by step in a physical cell: the arm closes at 0.65 mm
            # while the block is still at rest, the block accelerates from rest
            # over the next three steps, and only from the fourth does it match
            # the arm - by which point it has settled to a constant 2.95 mm.
            # Every step of that ride is a clean carry, mismatch under 0.3 mm,
            # separation flat to a hundredth of a millimetre. Looking for
            # contact *within* the run finds 2.95 mm against a 2.5 mm radius and
            # throws the whole thing away, which is how a run of clean carries
            # became `collision` in 24 cells out of 24.
            #
            # `drift` is still rejected: its body never comes within 183 mm of
            # the target at any point, so there is no moment of contact anywhere
            # before or during the ride.
            closest = float(np.min(separations[: stop + 2, body]))
            if interaction_radius is not None and closest >= interaction_radius:
                rides[start : stop + 1, body] = False
                continue

            # No bound on how far it slips while riding, and that is not an
            # oversight. The design names two properties of a capture - the
            # target is still before the arrival, and the effect then
            # accumulates without bound - and a target that inherits 85% of its
            # carrier's motion has both. What a slip costs is *prediction*, and
            # over one dispense window at this carry speed it costs 3.6 mm
            # against a 20 mm tolerance, so arm D still lands. Whether it does
            # is a question for the scoring, which measures it, rather than for
            # a verdict that would decide it in advance.
    return rides, moving


def _runs(flags: np.ndarray) -> list[tuple[int, int]]:
    """Inclusive [start, stop] index pairs of each True run."""

    spans, start = [], None
    for index, flag in enumerate(flags):
        if flag and start is None:
            start = index
        elif not flag and start is not None:
            spans.append((start, index - 1))
            start = None
    if start is not None:
        spans.append((start, len(flags) - 1))
    return spans


def carriage_evidence(
    target_positions: Iterable[ArrayLike],
    reference_positions: Iterable[ArrayLike],
    motion_floor_ratio: float = 0.25,
    agreement: float = 0.25,
    interaction_radius: float | None = None,
) -> tuple[float, int]:
    """How much of the target's motion is a body's own motion, and for how long.

    The gate's second admissible form of positive evidence, for the relation
    proximity contrast cannot see. Under a capture the carrier never leaves, so
    there is no far field to contrast against and the contrast abstains however
    the thresholds are set - the evidence that a relation is present is of a
    different kind, and this is it: the target's displacement *is* a second
    body's displacement, which no property of the target alone can produce.

    Returns the fraction of moving steps that agree with some body, and the
    longest consecutive run of agreement with a *single* body. The run is what
    separates a carry from a collision at its equilibrium separation, where the
    push momentarily equals the body's own advance; see `estimate_capture`.
    """

    targets = _paired_array(target_positions)
    references = _reference_array(reference_positions)
    if len(targets) != len(references) or len(targets) < 2:
        return 0.0, 0
    masked = _ride_mask(
        targets, references, motion_floor_ratio, agreement, interaction_radius
    )
    if masked is None:
        return 0.0, 0
    rides, moving = masked

    # You cannot carry what you are not touching.
    #
    # `drift` runs its target along the first body's own axis at its own speed,
    # so it agrees with that body on 0.71 of moving steps and passes a pure
    # agreement test - while the body stays 183 mm away and never comes within
    # the radius. The constant-velocity ceiling used to be what rejected it, and
    # that ceiling cannot be kept here: a captured target rides smoothly and is
    # *more* constant-velocity than a pushed one, so no ceiling admits capture
    # and rejects a sustained push.
    #
    # Contact is the definition of carrying rather than a tuned threshold, and
    # it separates the two outright.
    # See docs/paper003/paper003_where_collapse_is_defended_v0.1.md.
    if not moving.any() or not rides.shape[1]:
        return 0.0, 0
    fraction = float(np.mean(rides.any(axis=1)[moving]))
    longest = 0
    for body in range(rides.shape[1]):
        run = 0
        for riding in rides[:, body]:
            run = run + 1 if riding else 0
            longest = max(longest, run)
    return fraction, longest


def _first_run(rides: np.ndarray, length: int) -> tuple[int | None, int]:
    """Start and body of the earliest run of `length` consecutive True steps.

    `rides` is ``[step, body]``. Runs are looked for within a single body's
    column: a run assembled from whichever body matched best on each step is
    not one carrier holding on, which is the thing being detected.
    """

    best: tuple[int, int] | None = None
    for body in range(rides.shape[1]):
        column = rides[:, body]
        run = 0
        for index, riding in enumerate(column):
            run = run + 1 if riding else 0
            if run >= length:
                start = index - length + 1
                if best is None or start < best[0]:
                    best = (start, body)
                break
    return (None, -1) if best is None else best


@dataclass(frozen=True)
class CaptureEstimate:
    """What an arm can infer about a capture from observation alone.

    The parallel to `estimate_coupling` is deliberate and for the same reason:
    an arm handed `CaptureSpec.capture_radius` from the harness would be rolling
    forward with the generating model, and its accuracy would measure the loan.
    """

    capture_radius: float
    """Separation at the step the target began to ride. The only observable
    estimate of the radius: it is where taking hold actually happened."""
    held: bool
    """Is the target riding *now*. False after a release, which stops the arm
    from carrying a target that has already been let go."""
    onset: int
    """Index of the first riding step, in the observation history."""
    body: int
    """Which body took hold. Not merely that one did - with two bodies the
    prediction must be rolled forward with the carrier, not the nearest."""


def estimate_capture(
    target_positions: Iterable[ArrayLike],
    reference_positions: Iterable[ArrayLike],
    motion_floor_ratio: float = 0.25,
    agreement: float = 0.25,
    min_ride_steps: int = 3,
    interaction_radius: float | None = None,
) -> CaptureEstimate | None:
    """Recover a capture from observation: did a body take hold, and where.

    A riding target and its carrier move by the *same* displacement, so the test
    is that the two deltas agree to within `agreement` of the target's own step.
    Nothing about the generating process enters; the same statistic would
    identify a carried object in an Isaac trace.

    **A single agreeing step is not evidence**, and this is not a noise
    argument. A struck target has an equilibrium separation where the push
    exactly equals the body's own advance - with gain 0.5 and a 50 mm radius,
    20 mm - and at that separation collision and carriage are the same
    observation. What separates them is persistence: the equilibrium is passed
    through, a capture holds. `min_ride_steps` consecutive agreeing steps is the
    requirement, and it is why one agreeing step is discarded.

    Returns None when no such run is observed, which is the honest answer
    before a capture has happened and is what makes the arm decline rather than
    invent an onset. Note what that implies: in an encounter where the tested
    capture is the *first* one, there is nothing to estimate from, and the
    relational arm cannot act before the arrival. An encounter that wants arm D
    to predict the onset has to demonstrate a capture first.
    """

    targets = _paired_array(target_positions)
    references = _reference_array(reference_positions)
    if len(targets) != len(references) or len(targets) < 2:
        return None
    if not 0.0 < agreement < 1.0:
        raise ValueError("agreement must be in (0, 1)")
    if min_ride_steps < 1:
        raise ValueError("min_ride_steps must be >= 1")

    # A pause is not a release. Under the burst schedule the carrier stops for
    # `burst_off` steps and the target stops with it, so those steps carry no
    # evidence either way and must not be read as divergence - an earlier
    # version scored them as a release and reported `held=False` on every
    # captured cell it saw.
    #
    # The mask is the same one the gate's carriage evidence is computed from, so
    # a cell the gate admitted as a carry is one this can fit.
    masked = _ride_mask(
        targets, references, motion_floor_ratio, agreement, interaction_radius,
        min_ride_steps,
    )
    if masked is None:
        return None
    rides, moving = masked
    lengths = np.linalg.norm(np.diff(targets, axis=0), axis=1)
    largest = float(np.max(lengths))
    mismatch = np.linalg.norm(
        np.diff(references, axis=0) - np.diff(targets, axis=0)[:, None, :], axis=2
    )

    onset, body = _first_run(rides, min_ride_steps)
    if onset is None:
        return None

    radius = float(np.linalg.norm(targets[onset] - references[onset][body]))
    if radius <= 0.0:
        return None

    # Held means riding **now**, read off the same mask everything else uses.
    #
    # This was "no moving step after the onset ever disagreed", which is a far
    # stronger claim: one noisy step in a hundred and seventy-eight ended the
    # hold. Together with runs being split by the same single steps, that put 23
    # of 24 physical captures into `collision` under two different reasons which
    # were the same defect.
    #
    # The mask already treats a gap shorter than `min_ride_steps` as noise
    # rather than a release - the same number that is required to believe a ride
    # in the first place - so the last moving step being inside a ride is the
    # honest reading of "still held".
    moving_steps = np.flatnonzero(moving)
    still_held = bool(rides[moving_steps[-1], body]) if moving_steps.size else False

    return CaptureEstimate(
        capture_radius=radius,
        held=still_held,
        onset=onset,
        body=body,
    )


def predict_capture(
    target: ArrayLike,
    reference_history: ArrayLike,
    horizon: int,
    estimator,
    spec: CaptureSpec,
    held: bool = False,
) -> np.ndarray | None:
    """Arm D under capture: predict *when* the reference arrives, then carry.

    The two phases are the whole point. A prediction that applies the
    reference's motion to the target immediately is wrong before the capture,
    because the target is not attached yet - it scored 0.50 against arm B's 0.33
    as a deliberately crude proxy, and that number is a floor rather than a
    ceiling on this design.

    Returns the predicted displacement, or None when the reference's pattern is
    not identifiable and the arm must decline rather than guess.
    """

    if horizon < 0:
        raise ValueError("horizon must be >= 0")
    spec.validate()
    history = _paired_array(reference_history)
    if len(history) < 2:
        return None

    deltas = np.diff(history, axis=0)
    total = deltas.sum(axis=0)
    norm = float(np.linalg.norm(total))
    start = np.asarray(target, dtype=np.float64)
    if norm <= 0.0:
        return np.zeros_like(start)

    direction = total / norm
    steps = estimator.predict_steps(list(history @ direction), horizon)
    if steps is None:
        return None

    rolling_reference = np.asarray(history[-1], dtype=np.float64)
    rolling_target = start.copy()
    for step in steps:
        motion = float(step) * direction
        rolling_reference = rolling_reference + motion
        # The arrival step carries nothing, matching `capture_displacement`. A
        # prediction that carried on it would be a step ahead of the world for
        # the rest of the horizon.
        if held:
            rolling_target = rolling_target + motion
        elif float(np.linalg.norm(rolling_target - rolling_reference)) < spec.capture_radius:
            held = True
    return rolling_target - start
