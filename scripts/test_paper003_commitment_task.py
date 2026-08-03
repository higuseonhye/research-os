"""Contract tests for the Paper 003 commitment-point task.

Design-stage evidence, not a preregistered result. These pin the property the
capability endpoint depends on: a task variant exists where arm B is at 0% and
arm D is not, which the earlier continuous reach-and-hold probe could not
produce.
"""

from __future__ import annotations

import unittest

import numpy as np

from wm_expansion.commitment_task import (
    CommitmentTaskSpec,
    ReferencePatternEstimator,
    run_trial,
    success_rate,
)


class SpecGeometryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = CommitmentTaskSpec()
        self.spec.validate()

    def test_every_dispense_window_contains_moving_steps(self) -> None:
        """If some window were fully paused, arm B could never be locked out."""
        self.assertGreaterEqual(self.spec.min_moving_steps_in_window(), 1)

    def test_zero_order_cutoff_matches_geometry(self) -> None:
        expected = self.spec.tolerance / self.spec.min_moving_steps_in_window()
        self.assertAlmostEqual(self.spec.predicted_zero_order_cutoff(), expected)
        self.assertAlmostEqual(self.spec.predicted_zero_order_cutoff(), 0.010)

    def test_constant_velocity_fraction_is_a_lower_bound_not_the_ceiling(self) -> None:
        """Guards the correction: the exact-fraction underestimates arm C."""
        bound = self.spec.constant_velocity_exact_fraction()
        observed_plateau = success_rate("C", 0.020, spec=self.spec)
        self.assertLessEqual(bound, observed_plateau)

    def test_invalid_specs_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            CommitmentTaskSpec(tolerance=0.0).validate()
        with self.assertRaises(ValueError):
            CommitmentTaskSpec(commit_high=10, commit_low=20).validate()
        with self.assertRaises(ValueError):
            CommitmentTaskSpec(episode_steps=20, commit_high=40).validate()


class CapabilityCrossingTests(unittest.TestCase):
    """The property the whole endpoint rests on."""

    def setUp(self) -> None:
        self.spec = CommitmentTaskSpec()

    def test_all_arms_succeed_when_the_tray_is_slow(self) -> None:
        for arm in "BCD":
            self.assertEqual(success_rate(arm, 0.002, spec=self.spec), 1.0)

    def test_zero_order_is_locked_out_well_above_the_cutoff(self) -> None:
        cutoff = self.spec.predicted_zero_order_cutoff()
        self.assertEqual(success_rate("B", cutoff * 1.5, spec=self.spec), 0.0)

    def test_relation_arm_still_succeeds_where_zero_order_cannot(self) -> None:
        """0% -> achievable: the transition the tracking task never produced."""
        speed = self.spec.predicted_zero_order_cutoff() * 1.5
        self.assertEqual(success_rate("B", speed, spec=self.spec), 0.0)
        self.assertGreater(success_rate("D", speed, spec=self.spec), 0.9)

    def test_mode_expansion_helps_but_plateaus(self) -> None:
        """Arm C is partially right and structurally capped, not merely worse."""
        fast = success_rate("C", 0.020, spec=self.spec)
        self.assertGreater(fast, 0.2)
        self.assertLess(fast, 0.6)

    def test_success_is_monotone_non_increasing_in_tray_speed_for_zero_order(self) -> None:
        rates = [success_rate("B", v, spec=self.spec) for v in (0.002, 0.006, 0.010, 0.015)]
        self.assertEqual(rates, sorted(rates, reverse=True))

    def test_trials_are_deterministic_given_a_seed(self) -> None:
        first = run_trial("D", 7, 0.012, self.spec)
        second = run_trial("D", 7, 0.012, self.spec)
        self.assertEqual(first, second)

    def test_unknown_arm_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            run_trial("Z", 0, 0.01, self.spec)


class ReferenceEstimatorTests(unittest.TestCase):
    """Arm D must infer the reference pattern, not be handed it."""

    def setUp(self) -> None:
        self.spec = CommitmentTaskSpec()
        self.estimator = ReferencePatternEstimator()

    def _observed(self, speed: float = 0.015, steps: int = 40) -> list[float]:
        offset, history = 0.0, []
        for step in range(steps):
            if self.spec.is_moving(step):
                offset += speed
            history.append(offset)
        return history

    def test_declines_to_guess_without_a_complete_cycle(self) -> None:
        """No completed burst and pause means the cycle is not identifiable."""
        self.assertIsNone(self.estimator.predict_displacement([0.0, 0.0, 0.0], 6))
        self.assertIsNone(self.estimator.predict_displacement([0.0, 0.1, 0.2, 0.3, 0.4], 6))

    def test_predicts_no_motion_when_nothing_has_moved(self) -> None:
        self.assertEqual(self.estimator.predict_displacement([0.4] * 8, 6), 0.0)

    def test_recovers_the_pattern_from_clean_observations(self) -> None:
        speed, horizon = 0.015, self.spec.dispense_latency
        history = self._observed(speed=speed, steps=40)
        predicted = self.estimator.predict_displacement(history, horizon)
        self.assertIsNotNone(predicted)
        truth = sum(speed for h in range(1, horizon + 1) if self.spec.is_moving(39 + h))
        self.assertAlmostEqual(predicted, truth, delta=speed)

    def test_arm_d_never_beats_its_own_oracle(self) -> None:
        for noise in (0.0, 0.003):
            spec = CommitmentTaskSpec(observation_noise=noise)
            estimated = success_rate("D", 0.015, seeds=200, spec=spec)
            oracle = success_rate("D_oracle", 0.015, seeds=200, spec=spec)
            self.assertLessEqual(estimated, oracle)

    def test_capability_crossing_survives_a_real_estimator_under_noise(self) -> None:
        """The claim that matters: B locked out, D still succeeding, no oracle."""
        speed = 0.015
        spec = CommitmentTaskSpec(observation_noise=0.20 * speed)
        zero_order = success_rate("B", speed, seeds=300, spec=spec)
        relation = success_rate("D", speed, seeds=300, spec=spec)
        self.assertEqual(zero_order, 0.0)
        self.assertGreater(relation, 0.5)

    def test_estimator_degrades_as_observations_get_noisier(self) -> None:
        speed = 0.015
        rates = [
            success_rate("D", speed, seeds=300, spec=CommitmentTaskSpec(observation_noise=n * speed))
            for n in (0.0, 0.35, 1.0)
        ]
        self.assertGreater(rates[0], rates[1])
        self.assertGreater(rates[1], rates[2])


class IrregularTimingTests(unittest.TestCase):
    """Arm D assumes the reference repeats. Test what that assumption is worth."""

    def test_no_jitter_schedule_matches_the_periodic_function(self) -> None:
        spec = CommitmentTaskSpec()
        schedule = spec.motion_schedule(40)
        self.assertEqual(schedule, [spec.is_moving(s) for s in range(40)])

    def test_jitter_needs_an_rng_and_stays_within_bounds(self) -> None:
        spec = CommitmentTaskSpec(timing_jitter=2)
        with self.assertRaises(ValueError):
            spec.motion_schedule(20)
        schedule = spec.motion_schedule(200, np.random.default_rng(0))
        self.assertEqual(len(schedule), 200)
        self.assertNotEqual(schedule, [spec.is_moving(s) for s in range(200)])

    def test_jitter_larger_than_the_shorter_run_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            CommitmentTaskSpec(timing_jitter=4, burst_off=4).validate()

    def test_estimator_degrades_as_timing_gets_irregular(self) -> None:
        """It does exploit periodicity - that dependence should be visible."""
        speed = 0.015
        rates = [
            success_rate("D", speed, seeds=400, spec=CommitmentTaskSpec(timing_jitter=j))
            for j in (0, 2, 3)
        ]
        self.assertGreater(rates[0], rates[1])
        self.assertGreater(rates[1], rates[2])

    def test_capability_gap_survives_irregular_timing_and_noise_together(self) -> None:
        """The worst case tested: jittered timing and noisy observation at once."""
        speed = 0.015
        spec = CommitmentTaskSpec(timing_jitter=3, observation_noise=0.20 * speed)
        zero_order = success_rate("B", speed, seeds=400, spec=spec)
        relation = success_rate("D", speed, seeds=400, spec=spec)
        self.assertLess(zero_order, 0.15)
        self.assertGreater(relation, 0.40)
        self.assertGreater(relation - zero_order, 0.30)

    def test_jitter_softens_the_geometric_lockout(self) -> None:
        """Arm B is no longer exactly zero, which the prereg threshold must allow."""
        speed = 0.015
        strict = success_rate("B", speed, seeds=400, spec=CommitmentTaskSpec())
        jittered = success_rate("B", speed, seeds=400, spec=CommitmentTaskSpec(timing_jitter=3))
        self.assertEqual(strict, 0.0)
        self.assertGreater(jittered, 0.0)


if __name__ == "__main__":
    unittest.main()
