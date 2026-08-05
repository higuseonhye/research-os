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
    CaptureEstimate,
    CaptureSpec,
    CouplingSpec,
    estimate_capture,
    estimate_coupling,
    RelationGateDecision,
    RelationGateThresholds,
    coupling_displacement,
    evaluate_relation_gate,
    gate_fired_persistently,
    predict_capture,
)

ArrayLike = Sequence[float] | np.ndarray

#: Arms scored every episode. `D_oracle` is diagnostic and excluded from
#: primary estimates - see the preregistration draft.
#:
#: `SELF` is the hypothesis's most dangerous competitor and the arm that already
#: killed one design: under carriage it matched the relational arm exactly, and
#: that is why capture was chosen instead. See
#: docs/paper003/paper003_self_arm_prereg_v1.0.md.
EPISODE_ARMS = ("A", "B", "C", "D", "SELF", "D_oracle")


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
    dispense_latency: int = 8
    interaction_radius: float = 0.05
    coupling_gain: float = 0.5
    min_history: int = 8
    min_contact_steps: int = 2
    """How many steps of the dispense window a contact must occupy to count.

    The action takes `dispense_latency` steps and lands wherever the target is
    at completion. A contact that begins on the final step has no time to move
    the target before the action is over, so admitting that cell scores a task
    that was never posed - every arm is trivially right there.

    Two steps is the minimum overlap that leaves the contact any room to act. It
    is set from the structure of the action, not from any arm's performance.
    """

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
        if not 1 <= self.min_contact_steps <= self.dispense_latency:
            raise ValueError("min_contact_steps must be in [1, dispense_latency]")


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
        """Record one step. `reference` may be one body or several.

        The two-body encounter needs several: the relation is demonstrated by a
        body that then leaves and applied to a different body that arrives
        later. A single body is stored as a one-body list, so nothing that
        passes one array changes behaviour.
        """

        target_arr = np.asarray(target, dtype=np.float64)
        reference_arr = np.asarray(reference, dtype=np.float64)
        if target_arr.ndim != 1:
            raise ValueError("target must be 1-D")
        if reference_arr.ndim == 1:
            reference_arr = reference_arr[None, :]
        if reference_arr.ndim != 2 or reference_arr.shape[1] != target_arr.shape[0]:
            raise ValueError("reference must be [dim] or [body, dim] matching the target")
        if not (np.isfinite(target_arr).all() and np.isfinite(reference_arr).all()):
            raise ValueError("observations must be finite")
        self.targets.append(target_arr)
        self.references.append(reference_arr)

    @property
    def single_reference(self) -> bool:
        """True while only one body has ever been observed."""
        return bool(self.references) and self.references[0].shape[0] == 1

    def _acting_body(self) -> int | None:
        """Which body will act over the dispense window: the one closing fastest.

        With two bodies the prediction must be rolled forward with the body that
        is *arriving*, not the one that happens to be nearest now - after the
        prober leaves it may still be closer than the pusher for several steps
        while having no further effect. Closing rate is observable and does not
        depend on any arm's model.
        """

        if len(self.references) < 2:
            return None
        target = self.targets[-1]
        now = np.linalg.norm(self.references[-1] - target, axis=1)
        before = np.linalg.norm(self.references[-2] - target, axis=1)
        closing = before - now
        # Prefer a body already inside the radius; otherwise the fastest closer.
        inside = np.flatnonzero(now < self.spec.interaction_radius)
        if inside.size:
            return int(inside[np.argmax(closing[inside])])
        if float(np.max(closing)) <= 0.0:
            return None
        return int(np.argmax(closing))

    def _coupling(self) -> CouplingSpec | None:
        """The coupling arm D will roll forward with, estimated from observation.

        Previously this handed back the spec's own `interaction_radius` and
        `coupling_gain` - the very values used to generate the ground truth. Arm
        D was then rolling forward with the true model and its accuracy measured
        that loan rather than any inference.

        Both are now fitted from the observed (separation, displacement) pairs.
        `spec.interaction_radius` survives only as a coarse search window for
        which steps to consider as contact candidates; it does not enter the
        prediction. Returns None when the fit is not identifiable, which stops
        arm D from acting rather than letting it act on noise.
        """

        if len(self.targets) < 3:
            return None
        return estimate_coupling(
            self.targets,
            self.references,
            search_radius=self.spec.interaction_radius * 3.0,
        )

    def _capture(self) -> CaptureEstimate | None:
        """Is the target being carried, and by whom - inferred, not declared.

        The episode is not told which relation it is watching. Being told would
        hand arm D the generating model, the same loan `_coupling` exists to
        refuse, and would make a capture result unfalsifiable: the arm would
        succeed because the harness selected its model for it.

        Under a capture the collision fit is not merely worse but wrong in kind
        - displacement does not fall off with separation, it equals the
        carrier's own step - so `estimate_coupling` declines and arm D would
        silently degrade into arm B. This is what it degrades into instead.
        """

        if len(self.targets) < 2:
            return None
        return estimate_capture(self.targets, self.references)

    def _body_history(self, body: int) -> np.ndarray:
        """One body's trajectory as [time, dim]."""
        return np.asarray([step[body] for step in self.references], dtype=np.float64)

    def _project(
        self, target: np.ndarray, horizon: int, coupling: CouplingSpec
    ) -> np.ndarray | None:
        """Arm D's displacement prediction, rolled forward with the acting body.

        The coupling is fitted from contacts with whichever body was nearest -
        so, in the two-body encounter, mostly from the prober. It is then
        applied to the pusher. That transfer is the point: a relation that only
        described the body it was learned on would be an extrapolation of one
        trajectory, not a relation.
        """

        body = self._acting_body()
        if body is None:
            return None
        return project_reference_motion(
            target, self._body_history(body), horizon, self.estimator, coupling
        )

    def _project_self(self, horizon: int) -> np.ndarray | None:
        """The SELF arm: the target's own trajectory, and nothing else.

        No reference body is read here at all - not the acting one, not the
        carrier, not their number. The arm is the claim that whatever the target
        is about to do is already written in what it has been doing, which under
        an intermittent carry is a live possibility rather than a straw man: a
        carried target rides its carrier's bursts, so the carrier's pattern
        appears in the target's own history a few steps after the capture.

        Same estimator and same horizon as arm D uses on the carrier, so the two
        differ in *what they observe* and in nothing else. Returns None when the
        pattern is not identifiable, and the caller then falls back to the
        target's current position - the same fallback arm D takes.
        """

        history = np.asarray(self.targets, dtype=np.float64)
        if len(history) < 2:
            return None
        total = np.diff(history, axis=0).sum(axis=0)
        norm = float(np.linalg.norm(total))
        if norm <= 0.0:
            return np.zeros(history.shape[1])  # a still target continues still

        direction = total / norm
        steps = self.estimator.predict_steps(list(history @ direction), horizon)
        if steps is None:
            return None
        # No coupling to re-apply at each step: this arm has no second entity to
        # roll forward, which is the whole of what distinguishes it from arm D.
        return float(np.sum(steps)) * direction

    def _project_capture(
        self, target: np.ndarray, horizon: int, capture: CaptureEstimate
    ) -> np.ndarray | None:
        """Arm D under capture: roll the carrier forward and ride it.

        Rolled with the body that took hold rather than with `_acting_body`.
        The two agree while the carrier is the only body inside the radius, and
        differ exactly where it matters - a second body closing on an
        already-carried target is not what moves it.
        """

        return predict_capture(
            target,
            self._body_history(capture.body),
            horizon,
            self.estimator,
            CaptureSpec(capture_radius=capture.capture_radius),
            held=capture.held,
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

    def gate_fired(self) -> bool:
        """The decision arm D acts on: the gate, sustained.

        `gate_decision()` reports this step's statistics and stays available for
        diagnosis, but a single crossing is one draw rather than evidence. Under
        the observation-noise control some prefix crosses any fixed threshold by
        chance, which alone put that control at 0.30 of trials against H3's 0.10
        ceiling.
        """

        if len(self.targets) < 2:
            return False
        return gate_fired_persistently(
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
        body = self._acting_body()
        if body is None:
            return True  # nothing is approaching; a still reference is predictable
        history = self._body_history(body)
        total = np.diff(history, axis=0).sum(axis=0)
        norm = float(np.linalg.norm(total))
        if norm <= 0.0:
            return True  # a stationary reference is trivially predictable
        steps = self.estimator.predict_steps(
            list(history @ (total / norm)), self.spec.dispense_latency
        )
        return steps is not None

    def can_estimate(self) -> bool:
        """May arm D use a relational prediction?

        Three things must hold, and each has cost a round-trip to learn:

        1. the reference pattern is identifiable from history;
        2. the gate says the target's motion is conditioned on the reference;
        3. the coupling itself is estimable from the observed contacts.

        The third is what stops arm D from being handed the generating model.
        Note that none of these belong in `ready` - they govern whether this arm
        may act, not whether the cell is worth measuring.
        """
        return (
            self._projection_available()
            and self.gate_fired()
            and (self._coupling() is not None or self._capture() is not None)
        )

    def can_estimate_self(self) -> bool:
        """Is the SELF arm acting, or falling back to zero-order?

        Diagnostic only, and it decides nothing - but without it a SELF arm that
        never identified a pattern is indistinguishable in the output from one
        that identified a pattern and was wrong, and those are opposite readings
        of the same number.
        """

        return self._project_self(self.spec.dispense_latency) is not None

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

    def motion_expected(self, reference_future: ArrayLike | None = None) -> bool:
        """Will the target move during the dispense window?

        `reference_future` is the bodies' positions over the next
        `dispense_latency` steps, supplied by the harness. It must come from the
        harness rather than from `self.estimator`: predicting it would make
        eligibility depend on arm D's pattern estimator, and eligibility has to
        be a property of the world, not of one arm's readiness.

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

        # 1. The target is already moving, under any cause. A target drifting
        #    under its own dynamics moves during the dispense even with no body
        #    near it, and that cell is worth scoring: it is where a
        #    constant-velocity arm should win and a relational one decline.
        if self.already_moving():
            return True

        # 2. A body will be in contact for long enough during the window to act.
        if reference_future is not None:
            return self.contact_within_window(reference_future)

        # Fallback when the harness does not supply the bodies' future.
        #
        # It is a proxy, and a poor one: it reads the *instantaneous* closing
        # rate, which a schedule that ever reverses breaks in both directions -
        # a body inside the radius but leaving still counts as contact, and a
        # body paused between advances counts as receding. Measured against
        # ground truth it admits cells where the target does not move in 51% of
        # advance-only encounters and 84% of ones with a withdrawal.
        #
        # Kept only so existing single-body callers keep working. Anything that
        # knows the schedule should pass `reference_future`.
        distances = np.linalg.norm(self.references[-1] - target, axis=1)
        body = int(np.argmin(distances))
        reference = self.references[-1][body]
        previous_reference = self.references[-2][min(body, len(self.references[-2]) - 1)]
        separation = float(np.linalg.norm(target - reference))
        if separation < self.spec.interaction_radius:
            return True
        closing = float(np.linalg.norm(target - previous_reference)) - separation
        reach = separation - self.spec.interaction_radius
        return closing > 0.0 and 0.0 < reach <= closing * self.spec.dispense_latency

    def already_moving(self) -> bool:
        """Would the target's present motion alone carry it out of tolerance?

        The first clause of the eligibility screen, exposed separately because
        the commit window needs it negated - see `transition_in_window`.
        """

        if len(self.targets) < 2:
            return False
        speed = float(np.linalg.norm(self.targets[-1] - self.targets[-2]))
        return speed * self.spec.dispense_latency > self.spec.tolerance

    def contact_within_window(self, reference_future: ArrayLike) -> bool:
        """Will a body be in contact long enough during the dispense to act?

        The second clause of the screen. `reference_future` comes from the
        harness for the reason `motion_expected` gives: predicting it would
        route eligibility through arm D's estimator.
        """

        if len(self.targets) < 2:
            return False
        target = self.targets[-1]
        future = np.asarray(reference_future, dtype=np.float64)
        if future.ndim == 2:
            future = future[:, None, :]
        if future.ndim != 3 or future.shape[2] != target.shape[0]:
            raise ValueError("reference_future must be [step, dim] or [step, body, dim]")
        horizon = min(len(future), self.spec.dispense_latency)
        in_contact = sum(
            1
            for step in range(horizon)
            if float(np.min(np.linalg.norm(future[step] - target, axis=1)))
            < self.spec.interaction_radius
        )
        return in_contact >= self.spec.min_contact_steps

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
        # Two relations, and the order between them is not a preference. The
        # collision fit is the more constrained model - it requires displacement
        # to fall off linearly with separation, across a spread of separations,
        # at 0.80 fit quality - so where it succeeds it has been tested against
        # data a carry cannot produce. Under a carry the separation is constant,
        # there is no spread, and it declines. Capture is what is left when
        # displacement does not depend on separation at all.
        #
        # Trying capture first would break the collision path: a struck target
        # rides at the body's speed while it sits at the equilibrium separation,
        # so a carry is briefly the correct reading of a collision trace.
        predicted = None
        if self.gate_fired():
            coupling = self._coupling()
            if coupling is not None:
                predicted = self._project(target, horizon, coupling)
            else:
                capture = self._capture()
                if capture is not None:
                    predicted = self._project_capture(target, horizon, capture)
        out["D"] = target.copy() if predicted is None else target + predicted

        # Deliberately outside the gate. Arm D may act only when the relation
        # gate fires; this arm acts whenever its own pattern is identifiable.
        # The asymmetry favours SELF and is not to be corrected - a relation
        # that beats an ungated single-entity competitor has answered the
        # objection in its strongest form, and gating SELF would be tuning the
        # competitor down. Fixed in the preregistration.
        own = self._project_self(horizon)
        out["SELF"] = target.copy() if own is None else target + own

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
