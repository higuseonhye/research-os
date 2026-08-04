"""Contract tests for the capture relation.

CPU only. Capture was chosen over two alternatives after all three were
measured, and the properties that made it the choice are what these pin:

  1. Before capture the target does not move **at all**, so its own history
     carries no information about what is about to happen. That is what makes
     the relation necessary, and a single-entity model matched zero-order
     exactly because of it.
  2. After capture the effect accumulates without bound, which is what the
     collision coupling could not do - its displacement was capped at the order
     of the interaction radius, below the placement tolerance.
"""

from __future__ import annotations

import unittest

import numpy as np

from wm_expansion.commitment_task import ReferencePatternEstimator
from wm_expansion.relation_dynamics import (
    CaptureSpec,
    capture_displacement,
    predict_capture,
)

STEP = np.array([0.008, 0.0, 0.0])


def rollout(seed: int, speed: float = 0.008, on: int = 8, off: int = 4,
            steps: int = 90, noise: float = 0.0) -> tuple[np.ndarray, np.ndarray, int | None]:
    """A still target; a body approaches in bursts, captures it, carries it off."""
    rng = np.random.default_rng(seed)
    azimuth = rng.uniform(0.0, 2.0 * np.pi)
    axis = np.array([np.cos(azimuth), np.sin(azimuth), 0.0])
    spec = CaptureSpec()
    target = np.array([0.20, 0.0, 0.0])
    reference = target - axis * (speed * 22 + 0.5 * spec.capture_radius)
    held, captured_at = False, None
    targets, references = [], []
    for step in range(steps):
        motion = speed * axis if (step % (on + off)) < on else np.zeros(3)
        reference = reference + motion
        delta, held_now = capture_displacement(target, reference, motion, spec, held)
        if held_now and not held:
            captured_at = step
        held = held_now
        target = target + delta
        targets.append(target + rng.normal(0.0, noise, 3))
        references.append(reference.copy())
    return np.array(targets), np.array(references), captured_at


class CouplingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = CaptureSpec()

    def test_a_distant_body_moves_the_target_not_at_all(self) -> None:
        """Not a small push - nothing. A still target's history must stay empty,
        or a single-entity model has something to learn from it."""
        delta, held = capture_displacement(
            np.array([0.20, 0.0, 0.0]), np.array([0.10, 0.0, 0.0]), STEP, self.spec, False
        )
        np.testing.assert_array_equal(delta, np.zeros(3))
        self.assertFalse(held)

    def test_arrival_takes_hold_and_the_target_inherits_the_motion(self) -> None:
        delta, held = capture_displacement(
            np.array([0.20, 0.0, 0.0]), np.array([0.195, 0.0, 0.0]), STEP, self.spec, False
        )
        np.testing.assert_allclose(delta, STEP)
        self.assertTrue(held)

    def test_once_held_it_stays_held_however_far_the_body_goes(self) -> None:
        """Capture is a state change, not a proximity condition - which is why
        the effect accumulates and the collision coupling's ceiling does not
        apply."""
        delta, held = capture_displacement(
            np.array([0.20, 0.0, 0.0]), np.array([9.0, 0.0, 0.0]), STEP, self.spec, True
        )
        np.testing.assert_allclose(delta, STEP)
        self.assertTrue(held)

    def test_mismatched_shapes_are_refused(self) -> None:
        with self.assertRaises(ValueError):
            capture_displacement(np.zeros(3), np.zeros(2), STEP, self.spec, False)

    def test_a_non_positive_radius_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            CaptureSpec(capture_radius=0.0).validate()


class RolloutTests(unittest.TestCase):
    def test_the_target_is_perfectly_still_until_capture(self) -> None:
        targets, _, captured = rollout(300)
        self.assertIsNotNone(captured)
        # Up to but not including the capture step, which is the first on which
        # it moves.
        before = np.linalg.norm(np.diff(targets[: captured + 1], axis=0), axis=1)[:-1]
        self.assertEqual(float(np.max(before)), 0.0)

    def test_the_effect_accumulates_past_the_placement_tolerance(self) -> None:
        """The collision coupling could not do this at any speed or gain: its
        displacement was capped near the interaction radius, below 20 mm."""
        targets, _, captured = rollout(300)
        travelled = float(np.linalg.norm(targets[-1] - targets[captured]))
        self.assertGreater(travelled, 0.020)

    def test_capture_happens_at_all_across_seeds(self) -> None:
        for seed in range(300, 320):
            _, _, captured = rollout(seed)
            self.assertIsNotNone(captured, f"seed {seed} never captured")


class PredictionTests(unittest.TestCase):
    """Arm D, and the two phases that make it more than the crude proxy."""

    def setUp(self) -> None:
        self.spec = CaptureSpec()
        self.estimator = ReferencePatternEstimator()

    def _predict(self, targets, references, index, horizon=6, held=False):
        return predict_capture(
            targets[index], references[: index + 1], horizon,
            self.estimator, self.spec, held,
        )

    def test_it_predicts_nothing_while_the_body_is_still_far(self) -> None:
        """A body that cannot reach within the horizon changes nothing, and a
        prediction that moves the target anyway is the crude proxy's error.

        Taken well after the pattern becomes identifiable - before that the arm
        declines, which is a different behaviour and tested separately.
        """
        targets, references, captured = rollout(300)
        index = max(14, captured - 12)
        predicted = self._predict(targets, references, index)
        self.assertIsNotNone(predicted)
        self.assertLess(float(np.linalg.norm(predicted)), 0.002)

    def test_it_predicts_the_carry_once_the_body_will_arrive(self) -> None:
        targets, references, captured = rollout(300)
        predicted = self._predict(targets, references, captured - 2)
        self.assertIsNotNone(predicted)
        self.assertGreater(float(np.linalg.norm(predicted)), 0.005)

    def test_a_held_target_is_carried_from_the_first_step(self) -> None:
        """The two states differ only before the body arrives. Afterwards both
        predict a carry, because the free one captures on the first rolled step
        anyway - which is why the comparison is taken early.
        """
        targets, references, captured = rollout(300)
        index = max(14, captured - 10)
        free = self._predict(targets, references, index, held=False)
        held = self._predict(targets, references, index, held=True)
        self.assertGreater(float(np.linalg.norm(held)), float(np.linalg.norm(free)))

    def test_it_beats_zero_order_over_the_capture(self) -> None:
        """The property the paper rests on, at the commitment that matters."""
        wins = trials = 0
        for seed in range(300, 320):
            targets, references, captured = rollout(seed)
            if captured is None or captured + 6 >= len(targets):
                continue
            for index in range(max(9, captured - 6), captured):
                predicted = self._predict(targets, references, index)
                if predicted is None:
                    continue
                truth = targets[index + 6]
                relational = float(np.linalg.norm(targets[index] + predicted - truth))
                zero_order = float(np.linalg.norm(targets[index] - truth))
                trials += 1
                wins += int(relational <= zero_order)
        self.assertGreater(trials, 0)
        self.assertGreater(wins / trials, 0.8)

    def test_it_declines_rather_than_guessing_on_an_unusable_history(self) -> None:
        self.assertIsNone(
            predict_capture(np.zeros(3), np.zeros((1, 3)), 6, self.estimator, self.spec)
        )

    def test_a_negative_horizon_is_refused(self) -> None:
        targets, references, _ = rollout(300)
        with self.assertRaises(ValueError):
            predict_capture(targets[10], references[:11], -1, self.estimator, self.spec)


if __name__ == "__main__":
    unittest.main()
