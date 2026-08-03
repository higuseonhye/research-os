"""Contract tests for the contact-misspecification study.

CPU only. The study's whole purpose is to say what arm D does when its model is
wrong, so the parts that could quietly make the answer flattering - the choice
of scored steps, the encounter geometry, the friction law's magnitude - are
pinned here rather than trusted.
"""

from __future__ import annotations

import unittest

import numpy as np

from paper003_contact_robustness import (
    TRUE_GAIN,
    TRUE_RADIUS,
    evaluate_law,
    frictional_law,
    linear_law,
    power_law,
    required_cells,
    rollout,
    saturating_law,
    sign_test_power,
)


class ContactLawTests(unittest.TestCase):
    def test_every_law_is_silent_outside_the_interaction_radius(self) -> None:
        far_target = np.array([0.30, 0.0, 0.0])
        reference = np.array([0.0, 0.0, 0.0])
        for law in (linear_law, power_law(1.5), saturating_law(), frictional_law(0.4)):
            self.assertTrue(np.allclose(law(far_target, reference), 0.0))

    def test_friction_changes_direction_but_not_magnitude(self) -> None:
        """The point of the friction case: coefficients stay recoverable, aim does not.

        If friction also changed the magnitude, a direction failure could be
        mistaken for a coefficient failure and the diagnosis would be wrong.
        """
        target = np.array([0.20, 0.0, 0.0])
        reference = np.array([0.20 - 0.5 * TRUE_RADIUS, 0.0, 0.0])
        straight = linear_law(target, reference)
        rubbed = frictional_law(0.4)(target, reference)

        self.assertAlmostEqual(
            float(np.linalg.norm(straight)), float(np.linalg.norm(rubbed)), places=9
        )
        self.assertGreater(abs(float(rubbed[1])), 1e-4)  # deflected off the normal
        self.assertAlmostEqual(float(straight[1]), 0.0, places=12)

    def test_softer_bodies_push_less_at_the_same_penetration(self) -> None:
        target = np.array([0.20, 0.0, 0.0])
        reference = np.array([0.20 - 0.5 * TRUE_RADIUS, 0.0, 0.0])
        soft = float(np.linalg.norm(power_law(2.5)(target, reference)))
        hertz = float(np.linalg.norm(power_law(1.5)(target, reference)))
        straight = float(np.linalg.norm(linear_law(target, reference)))
        self.assertLess(soft, hertz)
        self.assertLess(hertz, straight)


class RolloutTests(unittest.TestCase):
    def test_azimuths_are_genuinely_different_encounters(self) -> None:
        """Not translations of one head-on pass - the degeneracy that hid a bug."""
        head_on = rollout(linear_law, seed=0, azimuth=0.0, noise=0.0)
        sideways = rollout(linear_law, seed=0, azimuth=np.pi / 2, noise=0.0)
        offset = head_on.truth - sideways.truth
        # A pure translation would leave a constant difference; this must not.
        self.assertGreater(float(np.ptp(np.linalg.norm(offset, axis=1))), 1e-3)

    def test_truth_is_noiseless_while_observations_are_not(self) -> None:
        run = rollout(linear_law, seed=3, azimuth=0.7, noise=0.001)
        self.assertGreater(float(np.max(np.abs(run.targets - run.truth))), 0.0)
        clean = rollout(linear_law, seed=3, azimuth=0.7, noise=0.0)
        self.assertTrue(np.allclose(clean.targets, clean.truth))

    def test_contact_actually_happens(self) -> None:
        run = rollout(linear_law, seed=0, azimuth=0.0, noise=0.0)
        separations = np.linalg.norm(run.truth - run.references, axis=1)
        self.assertLess(float(np.min(separations)), TRUE_RADIUS)


class EvaluationTests(unittest.TestCase):
    def test_correct_model_recovers_the_true_coefficients(self) -> None:
        result = evaluate_law("linear", linear_law, seeds=6, noise=0.0005)
        self.assertEqual(result.fits, 6)
        self.assertAlmostEqual(result.mean_gain, TRUE_GAIN, delta=0.06)
        self.assertAlmostEqual(result.mean_radius, TRUE_RADIUS, delta=0.006)

    def test_scored_steps_exclude_the_quiet_ones(self) -> None:
        """A quiet step scores zero for every arm and would flatter arm D.

        The first version of this analysis scored only post-contact steps and
        reported 0.0 mm for laws that are plainly misspecified.
        """
        result = evaluate_law("linear", linear_law, seeds=6, noise=0.0005)
        run = rollout(linear_law, seed=0, azimuth=0.0, noise=0.0005)
        self.assertLess(result.scored_steps, 6 * len(run.targets))
        self.assertGreater(result.scored_steps, 0)
        # arm B is badly wrong on the steps that count, which is what makes them
        # informative at all
        self.assertGreater(result.median_error_b, 0.02)

    def test_direction_error_costs_more_than_coefficient_error(self) -> None:
        """The study's finding: friction, not nonlinearity, is what threatens arm D."""
        hertz = evaluate_law("hertz", power_law(1.5), seeds=8, noise=0.0005)
        rubbed = evaluate_law("friction", frictional_law(1.0), seeds=8, noise=0.0005)

        # magnitude misspecification leaves the coefficients biased ...
        self.assertGreater(abs(hertz.mean_gain - TRUE_GAIN), 0.02)
        # ... while friction leaves them essentially correct ...
        self.assertAlmostEqual(rubbed.mean_gain, TRUE_GAIN, delta=0.02)
        self.assertAlmostEqual(rubbed.mean_radius, TRUE_RADIUS, delta=0.003)
        # ... and yet friction is the one that hurts the prediction more.
        self.assertGreater(rubbed.median_error_d, hertz.median_error_d)

    def test_friction_shortens_the_usable_contact(self) -> None:
        """Why engagement is expected to fall under real contact, not merely accuracy."""
        straight = evaluate_law("linear", linear_law, seeds=8, noise=0.0005)
        rubbed = evaluate_law("friction", frictional_law(0.4), seeds=8, noise=0.0005)
        self.assertLess(rubbed.scored_steps, straight.scored_steps)

    def test_the_guard_declines_rather_than_reporting_a_bad_fit(self) -> None:
        """Saturating contact is barely linear; refusing is the correct behaviour."""
        result = evaluate_law("saturating", saturating_law(), seeds=8, noise=0.0005)
        self.assertGreater(result.declined_rate, 0.5)


class PowerTests(unittest.TestCase):
    def test_power_rises_with_cells(self) -> None:
        low = sign_test_power(40, 0.56, trials=600)
        high = sign_test_power(160, 0.56, trials=600)
        self.assertGreater(high, low)

    def test_power_rises_with_engagement(self) -> None:
        self.assertGreater(
            sign_test_power(80, 0.75, trials=600), sign_test_power(80, 0.20, trials=600)
        )

    def test_the_pilot_was_far_too_small(self) -> None:
        """Nine cells could not have detected this effect even if it is real."""
        self.assertLess(sign_test_power(9, 0.56, trials=600), 0.10)

    def test_required_cells_grows_as_engagement_falls(self) -> None:
        generous = required_cells(0.75)
        meagre = required_cells(0.35)
        self.assertIsNotNone(generous)
        self.assertIsNotNone(meagre)
        self.assertGreater(meagre, generous)

    def test_required_cells_gives_up_rather_than_guessing(self) -> None:
        self.assertIsNone(required_cells(0.02, cap=60))


if __name__ == "__main__":
    unittest.main()
