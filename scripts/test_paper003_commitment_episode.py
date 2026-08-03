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
) -> tuple[list[np.ndarray], list[np.ndarray]]:
    """Stand-in for Isaac: same structure, no physics engine."""

    target = np.zeros(dims)
    target[0] = 0.20
    reference = np.zeros(dims)
    targets, references = [], []
    for step in range(steps):
        moving = (step % (burst_on + burst_off)) < burst_on
        if moving:
            reference = reference.copy()
            reference[0] += speed
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

    def test_returns_none_when_history_is_too_short(self) -> None:
        self.assertIsNone(project_reference_motion(np.zeros((1, 3)), 6, self.estimator))

    def test_stationary_reference_predicts_no_motion(self) -> None:
        history = np.tile(np.array([0.1, 0.2, 0.3]), (10, 1))
        predicted = project_reference_motion(history, 6, self.estimator)
        np.testing.assert_allclose(predicted, np.zeros(3), atol=1e-12)

    def test_prediction_follows_the_direction_of_travel(self) -> None:
        _, references = fake_world(steps=40, dims=3)
        predicted = project_reference_motion(np.asarray(references), 6, self.estimator)
        self.assertIsNotNone(predicted)
        # motion is along +x only
        self.assertGreater(predicted[0], 0.0)
        np.testing.assert_allclose(predicted[1:], 0.0, atol=1e-9)

    def test_works_in_two_dimensions_as_well_as_three(self) -> None:
        for dims in (2, 3):
            _, references = fake_world(steps=40, dims=dims)
            predicted = project_reference_motion(np.asarray(references), 6, self.estimator)
            self.assertIsNotNone(predicted)
            self.assertEqual(predicted.shape, (dims,))


class EpisodeDriverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = EpisodeSpec()
        self.targets, self.references = fake_world(steps=40, dims=3)

    def _drive(self, upto: int) -> CommitmentEpisode:
        episode = CommitmentEpisode(spec=self.spec)
        for target, reference in zip(self.targets[:upto], self.references[:upto]):
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
        self.assertFalse(self._drive(3).motion_expected())

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
        self.assertEqual(set(with_oracle), {"A", "B", "C", "D", "D_oracle"})

    def test_oracle_always_lands_and_resolve_reports_per_arm(self) -> None:
        episode = self._drive(20)
        landing = self.targets[20 + self.spec.dispense_latency]
        result = episode.resolve(episode.aims(true_landing=landing), landing)
        self.assertTrue(result["D_oracle"])
        self.assertEqual(set(result), {"A", "B", "C", "D", "D_oracle"})

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
        self.assertTrue(self._drive(18).can_estimate())
        self.assertTrue(self._drive(18).ready)

    def test_arm_d_differs_from_arm_b_once_it_can_estimate(self) -> None:
        """If D still equals B after the gate, the gate is not doing its job."""
        episode = self._drive(18)
        aims = episode.aims()
        self.assertFalse(
            np.allclose(aims["D"], aims["B"]),
            "arm D fell back to zero order despite can_estimate() being true",
        )

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

    def test_gate_fires_and_arm_d_acts_when_the_target_is_actually_coupled(self) -> None:
        episode = self._drive(20)
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


if __name__ == "__main__":
    unittest.main()
