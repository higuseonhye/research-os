"""Contract tests for the physics-agnostic commitment episode driver.

These exist so the Paper 003 decision logic is exercised on CPU before any GPU
time is spent. The Isaac runner is a thin shell over this module; if these pass,
what remains unvalidated there is scene construction, not science.

Design stage, not preregistered.
"""

from __future__ import annotations

import unittest

import numpy as np

from wm_expansion.commitment_episode import (
    CommitmentEpisode,
    EpisodeSpec,
    project_reference_motion,
)
from wm_expansion.commitment_task import ReferencePatternEstimator
from wm_expansion.relation_dynamics import (
    CouplingSpec,
    RelationGateThresholds,
    coupling_displacement,
)


# --------------------------------------------------------------------------
# fake physics: a reference body sweeping in bursts, pushing a target on contact
# --------------------------------------------------------------------------


def fake_world(
    steps: int = 40,
    dims: int = 3,
    speed: float = 0.015,
    burst_on: int = 10,
    burst_off: int = 4,
    radius: float = 0.05,
    gain: float = 0.5,
    encounter: str = "burst",
    start: float = 0.12,
) -> tuple[list[np.ndarray], list[np.ndarray]]:
    """Stand-in for Isaac: same structure, no physics engine.

    `probe` withdraws after striking; `burst` only ever advances, which is the
    v5 sweep's schedule. The difference is not cosmetic - under `burst` the
    target is never seen after the reference departs, and a struck target and a
    sliding one are the same history until then, so the gate cannot fire.
    """

    target = np.zeros(dims)
    target[0] = 0.20
    reference = np.zeros(dims)
    if encounter == "probe":
        reference[0] = target[0] - start
    targets, references = [], []
    for step in range(steps):
        if encounter == "burst":
            direction = 1 if (step % (burst_on + burst_off)) < burst_on else 0
        else:
            # 7 + 5 + 2 = 14, matching the burst period so only the withdrawal
            # differs. Contact recurs, which the coupling estimator needs.
            cycle = step % 14
            direction = 1 if cycle < 7 else (-1 if cycle < 12 else 0)
        reference = reference.copy()
        reference[0] += direction * speed
        offset = target - reference
        distance = float(np.linalg.norm(offset))
        if 0.0 < distance < radius:
            penetration = (radius - distance) / radius
            target = target + gain * penetration * radius * (offset / distance)
        targets.append(target.copy())
        references.append(reference.copy())
    return targets, references


class ProjectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.estimator = ReferencePatternEstimator()
        self.coupling = CouplingSpec(interaction_radius=0.05, coupling_gain=0.5)

    def _project(self, target, history, horizon=6):
        return project_reference_motion(
            np.asarray(target), np.asarray(history), horizon, self.estimator, self.coupling
        )

    def test_returns_none_when_history_is_too_short(self) -> None:
        self.assertIsNone(self._project(np.zeros(3), np.zeros((1, 3))))

    def test_stationary_reference_predicts_no_motion(self) -> None:
        history = np.tile(np.array([0.1, 0.2, 0.3]), (10, 1))
        predicted = self._project(np.array([0.2, 0.2, 0.3]), history)
        np.testing.assert_allclose(predicted, np.zeros(3), atol=1e-12)

    def test_predicts_along_the_contact_normal_not_the_reference_heading(self) -> None:
        """The defect the Isaac sweep exposed.

        With the reference approaching along +x but offset in +y, the target is
        pushed along the contact normal, which has a +y component. Summing the
        reference's own displacement would predict pure +x and miss.
        """
        targets, references = fake_world(steps=40, dims=3)
        offset_target = targets[19] + np.array([0.0, 0.02, 0.0])
        predicted = self._project(offset_target, references[:20])
        self.assertIsNotNone(predicted)
        self.assertGreater(abs(predicted[1]), 0.0, "no lateral component predicted")

    def test_works_in_two_dimensions_as_well_as_three(self) -> None:
        for dims in (2, 3):
            targets, references = fake_world(steps=40, dims=dims)
            predicted = self._project(targets[19], references[:20])
            self.assertIsNotNone(predicted)
            self.assertEqual(predicted.shape, (dims,))


class SelfArmTests(unittest.TestCase):
    """The single-entity competitor, pinned to its preregistered definition.

    Every fixture here is synthetic or collision-based. None of them is a
    `capture` + `burst` cell in the [+4, +6] band, which is the population the
    decision rule in `docs/paper003/paper003_self_arm_prereg_v1.0.md` reserves
    for the confirmatory run - implementing an arm against the data that is
    meant to judge it is the thing preregistration exists to prevent.
    """

    def setUp(self) -> None:
        self.spec = EpisodeSpec()

    def _episode(self, targets, references) -> CommitmentEpisode:
        episode = CommitmentEpisode(spec=self.spec)
        for target, reference in zip(targets, references):
            episode.observe(target, reference)
        return episode

    def _riding(self, steps: int = 40, on: int = 10, off: int = 4, speed: float = 0.015):
        """A target moving in bursts, and a body doing something unrelated."""
        axis = np.array([1.0, 0.0, 0.0])
        target = np.array([0.20, 0.0, 0.40])
        targets, references = [], []
        for step in range(steps):
            if (step % (on + off)) < on:
                target = target + speed * axis
            targets.append(target.copy())
            references.append(np.array([0.0, float(step), 0.0]))
        return targets, references

    def test_it_does_not_look_at_the_reference_at_all(self) -> None:
        """The defining property. Same target history, any body: same aim.

        If this ever fails, the arm has stopped being a single-entity model and
        the comparison it exists for is void.
        """

        targets, references = self._riding()
        elsewhere = [r * 3.0 + np.array([1.0, 2.0, 3.0]) for r in references]
        first = self._episode(targets, references).aims()["SELF"]
        second = self._episode(targets, elsewhere).aims()["SELF"]
        np.testing.assert_allclose(first, second)

    def test_it_predicts_a_target_that_carries_its_own_pattern(self) -> None:
        """The hazard, in its simplest form: the burst pattern is in the target.

        Not a capture cell - the body here is nowhere near and moving on an
        unrelated axis - but the same statistical situation, and the arm has to
        be able to exploit it or the comparison is not adversarial.
        """

        targets, references = self._riding(steps=40)
        episode = self._episode(targets[:30], references[:30])
        self.assertTrue(episode.can_estimate_self())
        aim = episode.aims()["SELF"]
        self.assertFalse(np.allclose(aim, episode.aims()["B"]))
        landing = targets[30 - 1 + self.spec.dispense_latency]
        self.assertLess(float(np.linalg.norm(aim - landing)), self.spec.tolerance)

    def test_a_still_target_gives_it_nothing_and_it_becomes_zero_order(self) -> None:
        """The argument capture was chosen on, stated as a test.

        Before the arrival the target has not moved, so its own history contains
        no information about what is about to happen to it and this arm can only
        aim where the target already is.
        """

        targets = [np.array([0.20, 0.0, 0.40]) for _ in range(20)]
        references = [np.array([0.0, float(step) * 0.01, 0.0]) for step in range(20)]
        episode = self._episode(targets, references)
        np.testing.assert_allclose(episode.aims()["SELF"], episode.aims()["B"])

    def test_it_is_not_gated(self) -> None:
        """Deliberately the easier deal, and fixed in the preregistration.

        Arm D may act only when the relation gate fires. This arm acts whenever
        its own pattern is identifiable, which favours it - and a relation that
        beats an ungated competitor has answered the objection in its strongest
        form. A change that gates SELF fails here.
        """

        targets, references = self._riding()
        episode = self._episode(targets[:30], references[:30])
        self.assertFalse(episode.gate_fired(), "fixture should not fire the gate")
        self.assertTrue(episode.can_estimate_self())
        self.assertFalse(np.allclose(episode.aims()["SELF"], episode.aims()["B"]))


class EpisodeDriverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = EpisodeSpec()
        self.targets, self.references = fake_world(steps=40, dims=3)

    def _drive(self, upto: int) -> CommitmentEpisode:
        episode = CommitmentEpisode(spec=self.spec)
        for target, reference in zip(self.targets[:upto], self.references[:upto]):
            episode.observe(target, reference)
        return episode

    def _drive_probe(self, upto: int) -> CommitmentEpisode:
        """Same, in a world where the reference withdraws after striking.

        Anything that depends on the relation gate needs this world: without a
        withdrawal the target is never observed after the reference leaves, and
        the gate abstains by design.
        """
        targets, references = fake_world(steps=40, dims=3, encounter="probe")
        episode = CommitmentEpisode(spec=self.spec)
        for target, reference in zip(targets[:upto], references[:upto]):
            episode.observe(target, reference)
        return episode

    def test_rejects_mismatched_or_non_finite_observations(self) -> None:
        episode = CommitmentEpisode(spec=self.spec)
        with self.assertRaises(ValueError):
            episode.observe(np.zeros(3), np.zeros(2))
        with self.assertRaises(ValueError):
            episode.observe(np.array([np.nan, 0.0, 0.0]), np.zeros(3))

    def test_will_not_commit_before_two_observations(self) -> None:
        episode = self._drive(1)
        with self.assertRaises(RuntimeError):
            episode.aims()

    def test_no_motion_expected_while_the_reference_is_far(self) -> None:
        """How far is "far" scales with the action, and that is correct.

        This asserted at step 3 while `dispense_latency` was 6. At 8 the same
        body is admitted there - a longer dispense means a body further out can
        still arrive before it completes - so the assertion moved to step 2 and
        the *transition* is pinned alongside it, which is the part that carries
        meaning.
        """

        self.assertFalse(self._drive(2).motion_expected())
        self.assertTrue(self._drive(6).motion_expected())

    def test_eligibility_covers_both_approach_and_sustained_contact(self) -> None:
        approach = [self._drive(n).motion_expected() for n in range(4, 10)]
        sustained = [self._drive(n).motion_expected() for n in range(16, 25)]
        self.assertTrue(all(approach), "approach window not admitted")
        self.assertTrue(all(sustained), "sustained contact wrongly excluded")

    def test_all_arms_are_scored_and_oracle_is_optional(self) -> None:
        episode = self._drive(20)
        without = episode.aims()
        self.assertNotIn("D_oracle", without)
        with_oracle = episode.aims(true_landing=np.zeros(3))
        self.assertEqual(set(with_oracle), {"A", "B", "C", "D", "SELF", "D_oracle"})

    def test_oracle_always_lands_and_resolve_reports_per_arm(self) -> None:
        episode = self._drive(20)
        landing = self.targets[20 + self.spec.dispense_latency]
        result = episode.resolve(episode.aims(true_landing=landing), landing)
        self.assertTrue(result["D_oracle"])
        self.assertEqual(set(result), {"A", "B", "C", "D", "SELF", "D_oracle"})

    def test_relation_arm_beats_zero_order_on_a_coupled_landing(self) -> None:
        """The property the whole paper rests on, exercised end to end."""
        wins = 0
        trials = 0
        for commit in range(4, 34):
            if commit + self.spec.dispense_latency >= len(self.targets):
                continue
            episode = self._drive(commit)
            if not episode.motion_expected():
                continue
            landing = self.targets[commit + self.spec.dispense_latency]
            aims = episode.aims()
            error_b = np.linalg.norm(aims["B"] - landing)
            error_d = np.linalg.norm(aims["D"] - landing)
            trials += 1
            wins += int(error_d <= error_b)
        self.assertGreater(trials, 0, "no eligible commit found in the fake world")
        self.assertEqual(wins, trials, "relation arm lost to zero order on a coupled landing")

    def test_not_ready_before_a_full_cycle_has_been_seen(self) -> None:
        """Pins the first Isaac run's failure.

        It committed at step 7 of a 14-step cycle, before any pause had
        occurred, so the estimator could not identify the period and arm D
        silently degraded into arm B - scoring identically to it. Readiness is
        now gated on the estimator actually working, not on a step count.
        """
        self.assertFalse(self._drive(8).ready, "committed before a pause was ever seen")
        self.assertFalse(self._drive(8).can_estimate())

    def test_ready_once_a_burst_and_a_pause_are_both_complete(self) -> None:
        # burst_on=10, burst_off=4 -> a pause completes around step 15
        self.assertTrue(self._drive(18).ready)
        self.assertTrue(self._drive_probe(20).can_estimate())

    def test_no_completed_contact_means_no_relation_claim(self) -> None:
        """The identifiability limit, pinned.

        Under the advance-only schedule the reference arrives and stays, so the
        target is never seen after it departs. A struck target and a target
        still sliding from an earlier strike are then the same history, and the
        second is what a constant-velocity model already explains. The gate must
        abstain rather than claim a relation it cannot have established - even
        though the world here really is coupled.
        """
        self.assertFalse(self._drive(18).gate_decision().fired)
        self.assertEqual(self._drive(18).gate_decision().post_contact_far_deltas, 0)
        # the same coupling, once a withdrawal has actually been observed
        self.assertTrue(self._drive_probe(20).gate_decision().fired)

    def test_arm_d_differs_from_arm_b_once_it_can_estimate(self) -> None:
        """If D still equals B after the gate, the gate is not doing its job."""
        episode = self._drive_probe(20)
        aims = episode.aims()
        self.assertFalse(
            np.allclose(aims["D"], aims["B"]),
            "arm D fell back to zero order despite can_estimate() being true",
        )

    def test_a_one_body_list_behaves_exactly_like_a_bare_array(self) -> None:
        """Multi-body support must not change anything that passes one body."""
        bare = CommitmentEpisode(spec=self.spec)
        listed = CommitmentEpisode(spec=self.spec)
        for index in range(20):
            target = np.array([0.20 + 0.001 * index, 0.0, 0.0])
            reference = np.array([0.10 + 0.005 * index, 0.0, 0.0])
            bare.observe(target, reference)
            listed.observe(target, reference[None, :])
        np.testing.assert_allclose(bare.aims()["D"], listed.aims()["D"])
        self.assertEqual(bare.gate_fired(), listed.gate_fired())
        self.assertEqual(bare.motion_expected(), listed.motion_expected())

    def test_reference_shape_is_checked(self) -> None:
        episode = CommitmentEpisode(spec=self.spec)
        with self.assertRaises(ValueError):
            episode.observe(np.zeros(3), np.zeros((2, 2)))  # wrong dimension
        with self.assertRaises(ValueError):
            episode.observe(np.zeros(3), np.zeros((2, 2, 3)))  # too many axes


    @staticmethod
    def _moving_reference(steps=40, dims=3, speed=0.015, on=10, off=4):
        reference = np.zeros(dims)
        out = []
        for step in range(steps):
            if (step % (on + off)) < on:
                reference = reference + np.array([speed] + [0.0] * (dims - 1))
            out.append(reference.copy())
        return out

    def test_gate_refuses_a_static_target_while_the_reference_moves(self) -> None:
        """Pins the Isaac control-condition failure.

        On a static target the reference still sweeps past. Without consulting
        the relation gate, arm D predicted 90 mm of motion for a target that
        never moved, while plain zero-order was exact. Arm D must be identical
        to arm B here.
        """
        episode = CommitmentEpisode(spec=self.spec)
        for reference in self._moving_reference()[:20]:
            episode.observe(np.array([0.20, 0.0, 0.0]), reference)
        self.assertFalse(episode.gate_decision().fired)
        self.assertFalse(episode.can_estimate())
        aims = episode.aims()
        np.testing.assert_allclose(aims["D"], aims["B"])

    @staticmethod
    def _drift_world(steps=40, dims=3, speed=0.015):
        """Target drifts under its own dynamics; the reference is far and irrelevant."""
        target = np.array([0.20] + [0.0] * (dims - 1))
        reference = np.array([-0.5] + [0.0] * (dims - 1))
        targets, references = [], []
        for _ in range(steps):
            target = target + np.array([speed] + [0.0] * (dims - 1))
            targets.append(target.copy())
            references.append(reference.copy())
        return targets, references

    def test_drift_commits_and_the_mode_arm_wins_there(self) -> None:
        """The two operators must win on different gaps, not one dominate.

        On drift the target moves under its own constant velocity, so arm C is
        the right tool and arm D should decline. Until eligibility admitted
        self-driven motion, drift never committed at all and this could not be
        shown.
        """
        targets, references = self._drift_world()
        episode = CommitmentEpisode(spec=self.spec)
        for target, reference in zip(targets[:20], references[:20]):
            episode.observe(target, reference)

        self.assertTrue(episode.motion_expected(), "drift cell was never eligible")
        self.assertFalse(episode.gate_decision().fired, "relation gate fired on drift")

        aims = episode.aims()
        landing = targets[20 + self.spec.dispense_latency]
        miss = {a: float(np.linalg.norm(aims[a] - landing)) for a in ("B", "C", "D")}
        self.assertLess(miss["C"], miss["B"], "constant velocity should win on drift")
        self.assertLess(miss["C"], self.spec.tolerance, "arm C should land on drift")
        np.testing.assert_allclose(aims["D"], aims["B"])

    def test_non_relational_cells_still_commit_so_h4_is_testable(self) -> None:
        """Eligibility is a property of the world, not of arm D's permission.

        Requiring the gate for readiness skipped every non-relational cell, so
        the hypothesis that arm D does not regress where the relation is absent
        could not be checked at all - those cells never ran.
        """
        episode = CommitmentEpisode(spec=self.spec)
        for reference in self._moving_reference()[:20]:
            episode.observe(np.array([0.20, 0.0, 0.0]), reference)
        self.assertTrue(episode.ready, "non-relational cell was skipped entirely")
        self.assertFalse(episode.can_estimate(), "arm D should still be barred from acting")

    def test_coupling_is_estimated_not_supplied(self) -> None:
        """Arm D must not be handed the generating model.

        The fake world uses radius 0.05 and gain 0.5; the driver is never told
        either. If this recovers them, arm D's accuracy is inference rather
        than a loan of the true parameters.
        """
        episode = self._drive(22)
        coupling = episode._coupling()
        self.assertIsNotNone(coupling, "coupling was not identifiable")
        self.assertAlmostEqual(coupling.interaction_radius, 0.05, delta=0.005)
        self.assertAlmostEqual(coupling.coupling_gain, 0.5, delta=0.05)

    def test_arm_d_declines_when_the_coupling_cannot_be_fitted(self) -> None:
        """No contacts to fit means no relational prediction, not a guess."""
        episode = CommitmentEpisode(spec=self.spec)
        for reference in self._moving_reference()[:20]:
            episode.observe(np.array([0.20, 0.0, 0.0]), reference)
        self.assertIsNone(episode._coupling())
        self.assertFalse(episode.can_estimate())
        aims = episode.aims()
        np.testing.assert_allclose(aims["D"], aims["B"])

    def test_gate_fires_and_arm_d_acts_when_the_target_is_actually_coupled(self) -> None:
        # probe world: the gate needs a completed contact, not merely a coupled one
        episode = self._drive_probe(20)
        self.assertTrue(episode.gate_decision().fired)
        aims = episode.aims()
        self.assertFalse(np.allclose(aims["D"], aims["B"]))

    def test_degrades_to_zero_order_rather_than_inventing_an_aim(self) -> None:
        """With no usable pattern, arm D must fall back, not fabricate."""
        episode = CommitmentEpisode(spec=self.spec)
        for _ in range(10):
            episode.observe(np.array([0.2, 0.0, 0.0]), np.array([0.0, 0.0, 0.0]))
        aims = episode.aims()
        np.testing.assert_allclose(aims["D"], aims["B"])

class TwoBodyTests(unittest.TestCase):
    """The encounter where one body demonstrates the relation and another applies it."""

    RADIUS = 0.05

    def setUp(self) -> None:
        self.spec = EpisodeSpec(interaction_radius=self.RADIUS)

    def _two_body(self, steps: int = 32) -> CommitmentEpisode:
        """Prober strikes and withdraws; pusher closes steadily from the far side.

        The default was 28 while `dispense_latency` was 6. Projecting eight
        steps needs more history than projecting six, and below 30 the
        estimator declines - which is arm D behaving as designed, refusing to
        act rather than guessing, and not a regression.
        """
        episode = CommitmentEpisode(spec=self.spec)
        target = np.array([0.20, 0.0, 0.0])
        prober = np.array([0.20 - 1.9 * self.RADIUS, 0.0, 0.0])
        pusher = np.array([0.20 + 0.30, 0.0, 0.0])
        coupling = CouplingSpec(interaction_radius=self.RADIUS, coupling_gain=0.5)
        for step in range(steps):
            if step < 10:
                prober = prober + np.array([0.010, 0.0, 0.0])
            elif step < 22:
                prober = prober - np.array([0.030, 0.0, 0.0])
            if step >= 14:
                pusher = pusher - np.array([0.015, 0.0, 0.0])
            target = (
                target
                + coupling_displacement(target, prober, coupling)
                + coupling_displacement(target, pusher, coupling)
            )
            episode.observe(target, np.stack([prober, pusher]))
        return episode

    def test_the_acting_body_is_the_one_arriving_not_the_one_nearest(self) -> None:
        """After the prober leaves it can still be nearer while having no effect.

        Rolling the prediction forward with it would predict a contact that is
        over, which is why the acting body is chosen by closing rate.
        """
        episode = self._two_body(steps=34)
        target = episode.targets[-1]
        separations = np.linalg.norm(episode.references[-1] - target, axis=1)
        acting = episode._acting_body()
        self.assertEqual(acting, 1, "should follow the pusher")
        # and it is not simply the nearest, at least somewhere in the approach
        nearest_history = []
        probe = CommitmentEpisode(spec=self.spec)
        for target, bodies in zip(episode.targets, episode.references):
            probe.observe(target, bodies)
            if len(probe.references) >= 2:
                nearest = int(np.argmin(np.linalg.norm(bodies - target, axis=1)))
                nearest_history.append((nearest, probe._acting_body()))
        self.assertTrue(
            any(n != a for n, a in nearest_history if a is not None),
            "acting body never differed from the nearest, so the test proves nothing",
        )

    def test_the_gate_fires_on_a_relation_carried_by_two_bodies(self) -> None:
        self.assertTrue(self._two_body().gate_fired())

    def test_a_pusher_that_never_stops_is_arm_c_s_case_and_the_gate_lets_it_through(
        self,
    ) -> None:
        """Still arm C's case. **No longer the gate's job to say so.**

        This asserted that the gate declines here, and that assertion was the
        belt-and-braces the design has now given up deliberately. A body that
        pushes without pause settles the target into a steady drift a
        constant-velocity model explains - but a relation *is* present, contact
        really does cause the motion, so refusing it is not gate specificity.

        The clause that refused it cannot be kept in any case: a captured target
        rides smoothly and is more constant-velocity than a pushed one, so no
        ceiling admits capture and rejects this. The ceiling is now scoped to
        the proximity path.

        Where the collapse threat is defended instead is H2, on outcomes: arm D
        must beat the mode operator by a margin, and where a constant-velocity
        model suffices arm C succeeds and the margin vanishes. That does not
        depend on a threshold being right.

        See docs/paper003/paper003_where_collapse_is_defended_v0.1.md.
        """

        late = self._two_body(steps=40)
        # Arm C's case: a constant-velocity model explains this motion well.
        self.assertGreater(late.gate_decision().constant_velocity_gain, 0.5)
        # And the gate no longer refuses it, which is the deliberate change.
        self.assertTrue(late.gate_fired())

    def test_the_coupling_is_fitted_across_both_bodies(self) -> None:
        coupling = self._two_body()._coupling()
        self.assertIsNotNone(coupling)
        self.assertAlmostEqual(coupling.coupling_gain, 0.5, delta=0.15)
        self.assertAlmostEqual(coupling.interaction_radius, self.RADIUS, delta=0.015)

    def test_arm_d_predicts_motion_the_other_arms_cannot(self) -> None:
        """At the commitment the target is still, so B and C both predict nothing."""
        episode = self._two_body(steps=32)
        aims = episode.aims()
        self.assertTrue(episode.can_estimate())
        self.assertFalse(np.allclose(aims["D"], aims["B"]))


class EligibilityTests(unittest.TestCase):
    """The screen deciding which cells are measurements at all.

    It must be a property of the world: the future is supplied by the harness,
    never predicted, because predicting it would route eligibility through arm
    D's pattern estimator and make it depend on one arm's readiness.
    """

    RADIUS = 0.05

    def setUp(self) -> None:
        self.spec = EpisodeSpec(interaction_radius=self.RADIUS)

    def _still(self) -> CommitmentEpisode:
        """A stationary target with a body parked far away."""
        episode = CommitmentEpisode(spec=self.spec)
        for _ in range(6):
            episode.observe(np.array([0.20, 0.0, 0.0]), np.array([0.60, 0.0, 0.0]))
        return episode

    def _future(self, distances: list[float]) -> np.ndarray:
        """Body positions over the window, given separations from the target."""
        return np.array([[[0.20 + d, 0.0, 0.0]] for d in distances])

    def test_contact_that_occupies_the_window_is_admitted(self) -> None:
        near = 0.5 * self.RADIUS
        self.assertTrue(self._still().motion_expected(self._future([near] * 6)))

    def test_contact_beginning_on_the_final_step_is_refused(self) -> None:
        """The action completes before the displacement happens, so the task
        was never posed and every arm is trivially right."""
        far, near = 2.0 * self.RADIUS, 0.5 * self.RADIUS
        self.assertFalse(
            self._still().motion_expected(self._future([far] * 5 + [near]))
        )

    def test_no_contact_at_all_is_refused(self) -> None:
        self.assertFalse(self._still().motion_expected(self._future([2.0 * self.RADIUS] * 6)))

    def test_a_moving_target_is_admitted_even_with_no_body_near(self) -> None:
        """Drift is a cell worth scoring: arm C should win and arm D decline."""
        episode = CommitmentEpisode(spec=self.spec)
        for index in range(6):
            episode.observe(
                np.array([0.20 + 0.01 * index, 0.0, 0.0]), np.array([0.60, 0.0, 0.0])
            )
        self.assertTrue(episode.motion_expected(self._future([2.0 * self.RADIUS] * 6)))

    def test_the_required_overlap_is_configurable_and_monotone(self) -> None:
        far, near = 2.0 * self.RADIUS, 0.5 * self.RADIUS
        window = self._future([far] * 3 + [near] * 3)
        lenient = CommitmentEpisode(spec=EpisodeSpec(interaction_radius=self.RADIUS,
                                                     min_contact_steps=2))
        strict = CommitmentEpisode(spec=EpisodeSpec(interaction_radius=self.RADIUS,
                                                    min_contact_steps=5))
        for episode in (lenient, strict):
            for _ in range(6):
                episode.observe(np.array([0.20, 0.0, 0.0]), np.array([0.60, 0.0, 0.0]))
        self.assertTrue(lenient.motion_expected(window))
        self.assertFalse(strict.motion_expected(window))

    def test_an_impossible_overlap_requirement_is_refused_at_construction(self) -> None:
        with self.assertRaises(ValueError):
            EpisodeSpec(dispense_latency=6, min_contact_steps=7).validate()
        with self.assertRaises(ValueError):
            EpisodeSpec(min_contact_steps=0).validate()

    def test_a_malformed_future_is_rejected_rather_than_guessed(self) -> None:
        with self.assertRaises(ValueError):
            self._still().motion_expected(np.zeros((6, 1, 2)))

    def test_the_fallback_is_reachable_and_documented_as_a_proxy(self) -> None:
        """Passing no future still works, so single-body callers are unaffected."""
        self.assertIsInstance(self._still().motion_expected(), bool)


class ConstantMotionTests(unittest.TestCase):
    """A body that never pauses is the simplest pattern, and was being refused."""

    def test_a_steadily_moving_body_is_predictable(self) -> None:
        estimator = ReferencePatternEstimator()
        history = [0.015 * step for step in range(20)]
        steps = estimator.predict_steps(history, 6)
        self.assertIsNotNone(steps)
        self.assertEqual(len(steps), 6)
        for value in steps:
            self.assertAlmostEqual(value, 0.015, places=6)

    def test_a_bursting_body_that_has_not_paused_yet_is_still_refused(self) -> None:
        """The defect this must not revive: a commitment at step 7 of a 14-step
        cycle, with arm D predicting continuous motion and silently degrading."""
        estimator = ReferencePatternEstimator()
        history = [0.015 * step for step in range(8)]  # shorter than 2 * horizon
        self.assertIsNone(estimator.predict_steps(history, 6))

    def test_direction_is_taken_from_the_observed_motion(self) -> None:
        estimator = ReferencePatternEstimator()
        steps = estimator.predict_steps([-0.02 * step for step in range(20)], 4)
        self.assertIsNotNone(steps)
        self.assertTrue(all(value < 0 for value in steps))





if __name__ == "__main__":
    unittest.main()
