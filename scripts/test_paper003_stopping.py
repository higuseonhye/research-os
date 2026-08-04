"""Contract tests for the stopping-time measurement.

CPU only. This number decides whether Paper 003's relation gate can work under
real contact, so the ways it could be quietly wrong - counting a trace with no
strike, mistaking a still object for one that stopped, reading a coast that runs
past the end of the recording - are pinned here.
"""

from __future__ import annotations

import unittest

import numpy as np

from wm_expansion.stopping import (
    GATE_VIABLE_RETENTION,
    estimate_stopping,
    gate_outlook,
)

RADIUS = 0.05


def trace(speeds: list[float], contact_steps: int, start: float = 0.20):
    """Build a pose trace and its separations from a list of per-step speeds."""
    positions = [np.array([start, 0.0, 0.0])]
    for speed in speeds:
        positions.append(positions[-1] + np.array([speed, 0.0, 0.0]))
    separations = [
        0.5 * RADIUS if index <= contact_steps else 3.0 * RADIUS
        for index in range(len(positions))
    ]
    return positions, separations


class MeasurementTests(unittest.TestCase):
    def test_an_object_that_halts_at_once_reports_zero(self) -> None:
        """The injected coupling's regime, which every pilot so far has run in."""
        positions, separations = trace([0.01, 0.01, 0.0, 0.0, 0.0, 0.0], contact_steps=2)
        estimate = estimate_stopping(positions, separations, RADIUS)
        self.assertIsNotNone(estimate)
        self.assertEqual(estimate.steps_to_stop, 0)
        self.assertEqual(estimate.retention, 0.0)

    def test_a_coast_is_counted_in_steps(self) -> None:
        positions, separations = trace(
            [0.01, 0.01, 0.008, 0.005, 0.002, 0.0, 0.0], contact_steps=2
        )
        estimate = estimate_stopping(positions, separations, RADIUS)
        self.assertEqual(estimate.steps_to_stop, 3)
        self.assertGreater(estimate.coast_distance, 0.0)

    def test_retention_recovers_a_geometric_decay(self) -> None:
        speeds = [0.02, 0.02] + [0.02 * 0.5**k for k in range(1, 7)]
        positions, separations = trace(speeds, contact_steps=1)
        estimate = estimate_stopping(positions, separations, RADIUS)
        self.assertAlmostEqual(estimate.retention, 0.5, delta=0.08)

    def test_an_object_still_moving_at_the_end_reports_no_stop(self) -> None:
        """Not a large stopping time - the trace simply cannot say."""
        positions, separations = trace([0.01] * 8, contact_steps=1)
        estimate = estimate_stopping(positions, separations, RADIUS)
        self.assertIsNone(estimate.steps_to_stop)

    def test_a_trace_with_no_contact_is_refused(self) -> None:
        positions = [np.array([0.2, 0.0, 0.0])] * 8
        self.assertIsNone(estimate_stopping(positions, [3.0 * RADIUS] * 8, RADIUS))

    def test_a_strike_that_moved_nothing_is_refused(self) -> None:
        """Otherwise a missed strike reads as an object that stops instantly."""
        positions, separations = trace([0.0] * 8, contact_steps=2)
        self.assertIsNone(estimate_stopping(positions, separations, RADIUS))

    def test_settling_before_contact_does_not_count_as_a_strike(self) -> None:
        """The real trace that made this guard necessary.

        On the first Isaac run the block settled under gravity in the opening
        steps - 10.1 mm while the end effector was 57 mm away and receding - and
        then never moved again. The end effector approached to 37.5 mm, missed,
        and retreated. Judged on the trace's global peak speed the settling
        cleared the old guard, and the probe reported "stops within a step":
        the one answer that would have rescued the design, from a trace with no
        strike in it at all.
        """
        positions = [np.array([0.20, 0.0, 0.0])]
        # settle: moves while nothing is near
        for delta in (0.0025, 0.0064, 0.0013, 0.0):
            positions.append(positions[-1] + np.array([delta, 0.0, 0.0]))
        # then a near pass that never touches it
        positions.extend([positions[-1].copy() for _ in range(12)])
        separations = [0.058] * 5 + [0.038] * 6 + [0.052] * 6

        self.assertEqual(len(positions), len(separations))
        self.assertIsNone(estimate_stopping(positions, separations, RADIUS))

    def test_contact_running_to_the_end_leaves_no_coast_to_measure(self) -> None:
        positions, separations = trace([0.01] * 6, contact_steps=6)
        self.assertIsNone(estimate_stopping(positions, separations, RADIUS))

    def test_degenerate_inputs_are_refused(self) -> None:
        positions, separations = trace([0.01] * 6, contact_steps=2)
        self.assertIsNone(estimate_stopping(positions[:2], separations[:2], RADIUS))
        self.assertIsNone(estimate_stopping(positions, separations[:-1], RADIUS))
        with self.assertRaises(ValueError):
            estimate_stopping(positions, separations, 0.0)


class SamplingTests(unittest.TestCase):
    """A fast body crosses the contact zone between samples."""

    def test_a_strike_missed_between_samples_is_recovered(self) -> None:
        """The failure at 50 mm/step: the block moved, and every recorded
        separation sat outside the radius, so the strike was refused."""
        positions, _ = trace([0.01, 0.008, 0.004, 0.0, 0.0, 0.0], contact_steps=0)
        # The body passes through: every sample sits outside a 12 mm radius
        # while it moved 40 mm between them, then it leaves for good.
        separations = [0.030, 0.030, 0.030] + [0.200] * (len(positions) - 3)
        travel = [0.040, 0.040, 0.040] + [0.040] * (len(positions) - 3)
        self.assertIsNone(estimate_stopping(positions, separations, 0.012))
        recovered = estimate_stopping(
            positions, separations, 0.012, body_travel=travel
        )
        self.assertIsNotNone(recovered)
        self.assertGreater(recovered.peak_in_contact, 0.0)

    def test_the_allowance_does_not_manufacture_contact_from_nothing(self) -> None:
        """A stationary body far away stays far away however it is sampled."""
        positions, _ = trace([0.01] * 6, contact_steps=0)
        separations = [0.30] * len(positions)
        self.assertIsNone(
            estimate_stopping(positions, separations, 0.012,
                              body_travel=[0.001] * len(positions))
        )

    def test_a_misaligned_or_negative_allowance_is_refused(self) -> None:
        positions, separations = trace([0.01] * 6, contact_steps=2)
        with self.assertRaises(ValueError):
            estimate_stopping(positions, separations, RADIUS, body_travel=[0.01])
        with self.assertRaises(ValueError):
            estimate_stopping(positions, separations, RADIUS,
                              body_travel=[-0.01] * len(separations))


class OutlookTests(unittest.TestCase):
    """The run must state its own implication rather than leave a bare number."""

    def _estimate(self, speeds, contact_steps=1):
        positions, separations = trace(speeds, contact_steps)
        return estimate_stopping(positions, separations, RADIUS)

    def test_an_instant_stop_is_named_as_the_assumed_regime(self) -> None:
        outlook = gate_outlook(self._estimate([0.01, 0.01, 0.0, 0.0, 0.0, 0.0], 2))
        self.assertIn("injected", outlook)

    def test_a_free_slide_is_named_outright(self) -> None:
        self.assertIn("never stopped", gate_outlook(self._estimate([0.01] * 8)))

    def test_a_slow_decay_warns_that_constant_velocity_explains_it(self) -> None:
        """Long enough to actually come to rest: a trace that ends while the
        object is still moving reports "never stopped", which is a different
        finding and must not be conflated with a slow one."""
        speeds = [0.02] + [0.02 * 0.7**k for k in range(1, 18)]
        estimate = self._estimate(speeds)
        self.assertIsNotNone(estimate.steps_to_stop)
        self.assertGreater(estimate.retention, GATE_VIABLE_RETENTION)
        self.assertIn("gate is expected to decline", gate_outlook(estimate))

    def test_no_strike_says_so_rather_than_guessing(self) -> None:
        self.assertIn("no usable strike", gate_outlook(None))


if __name__ == "__main__":
    unittest.main()
