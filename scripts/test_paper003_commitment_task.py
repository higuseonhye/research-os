"""Contract tests for the Paper 003 commitment-point task.

Design-stage evidence, not a preregistered result. These pin the property the
capability endpoint depends on: a task variant exists where arm B is at 0% and
arm D is not, which the earlier continuous reach-and-hold probe could not
produce.
"""

from __future__ import annotations

import unittest

from wm_expansion.commitment_task import CommitmentTaskSpec, run_trial, success_rate


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


if __name__ == "__main__":
    unittest.main()
