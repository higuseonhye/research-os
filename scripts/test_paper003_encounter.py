"""Contract tests for the encounter geometry.

CPU only. This logic used to live inside the Isaac runner, where it could not be
imported let alone tested, and that surface has produced eight defects in this
project. Everything the encounter decides is pinned here.
"""

from __future__ import annotations

import unittest

import numpy as np

from wm_expansion.encounter import (
    EncounterSpec,
    bodies_at,
    bodies_over,
    draw_geometry,
    reference_offset,
    schedule_direction,
)

TARGET = np.array([0.20, 0.0, 0.0])


class ScheduleTests(unittest.TestCase):
    def test_burst_only_ever_advances_or_holds(self) -> None:
        spec = EncounterSpec(schedule="burst")
        directions = {schedule_direction(step, spec) for step in range(50)}
        self.assertEqual(directions, {0, 1})

    def test_probe_withdraws(self) -> None:
        spec = EncounterSpec(schedule="probe")
        directions = {schedule_direction(step, spec) for step in range(50)}
        self.assertIn(-1, directions)

    def test_probe_offset_returns_to_the_start_of_each_cycle_lower_than_its_peak(self) -> None:
        """A withdrawal must actually undo distance, not merely pause."""
        spec = EncounterSpec(schedule="probe")
        offsets = [reference_offset(step, spec) for step in range(spec.period)]
        self.assertLess(offsets[-1], max(offsets))

    def test_the_withdrawal_must_clear_the_interaction_radius(self) -> None:
        """Otherwise the target is never seen after the body leaves, and the
        relation stays unidentifiable however long the episode runs."""
        with self.assertRaises(ValueError):
            EncounterSpec(probe_withdraw=1).validate()

    def test_an_unknown_schedule_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            EncounterSpec(schedule="pursue").validate()


class GeometryTests(unittest.TestCase):
    def test_seeds_give_genuinely_different_encounters(self) -> None:
        """Not translations of one another - the degeneracy that hid a bug.

        Ten seeds once gave ten positions but a single head-on encounter, and
        every arm's miss distance came out identical every time.
        """
        spec = EncounterSpec()
        azimuths = {round(draw_geometry(s, TARGET, spec).azimuth, 6) for s in range(10)}
        self.assertEqual(len(azimuths), 10)

    def test_the_draw_is_reproducible_from_the_seed(self) -> None:
        spec = EncounterSpec()
        first = draw_geometry(7, TARGET, spec)
        second = draw_geometry(7, TARGET, spec)
        np.testing.assert_allclose(first.prober_start, second.prober_start)
        np.testing.assert_allclose(first.pusher_start, second.pusher_start)

    def test_probe_starts_close_enough_to_complete_a_contact_early(self) -> None:
        spec = EncounterSpec(schedule="probe")
        for seed in range(20):
            geometry = draw_geometry(seed, TARGET, spec)
            approach = float(np.linalg.norm(geometry.prober_start - TARGET))
            self.assertLessEqual(approach, 3.0 * spec.interaction_radius)

    def test_burst_starts_far_enough_for_one_full_cycle(self) -> None:
        spec = EncounterSpec(schedule="burst")
        floor = spec.burst_on * spec.reference_speed + spec.interaction_radius
        for seed in range(20):
            geometry = draw_geometry(seed, TARGET, spec)
            self.assertGreaterEqual(
                float(np.linalg.norm(geometry.prober_start - TARGET)), floor
            )

    def test_the_second_body_approaches_from_a_different_direction(self) -> None:
        """Otherwise the two are one approach in two parts, not two encounters."""
        spec = EncounterSpec(bodies=2)
        for seed in range(20):
            geometry = draw_geometry(seed, TARGET, spec)
            angle = abs(geometry.pusher_azimuth - geometry.azimuth) % (2 * np.pi)
            angle = min(angle, 2 * np.pi - angle)
            self.assertGreaterEqual(angle, np.pi / 3.0 - 1e-9)


class BodiesTests(unittest.TestCase):
    def test_one_body_reports_one_body(self) -> None:
        spec = EncounterSpec(bodies=1)
        geometry = draw_geometry(0, TARGET, spec)
        self.assertEqual(bodies_at(5, geometry, spec).shape, (1, 3))

    def test_two_bodies_report_two(self) -> None:
        spec = EncounterSpec(bodies=2)
        geometry = draw_geometry(0, TARGET, spec)
        self.assertEqual(bodies_at(5, geometry, spec).shape, (2, 3))

    def test_adding_a_body_does_not_move_the_first(self) -> None:
        """A one-body run and a two-body run share the prober's trajectory."""
        one = EncounterSpec(bodies=1)
        two = EncounterSpec(bodies=2)
        geometry = draw_geometry(3, TARGET, one)
        for step in range(30):
            np.testing.assert_allclose(
                bodies_at(step, geometry, one)[0], bodies_at(step, geometry, two)[0]
            )

    def test_the_second_body_waits_then_moves_at_a_constant_speed(self) -> None:
        """Not tested as monotonically closing: the body passes the target and
        its separation grows again afterwards. What matters is that it never
        pauses, because a pause is what the pattern estimator looks for and the
        constant-motion fallback exists precisely for a body that has none."""
        spec = EncounterSpec(bodies=2, pusher_start_step=16)
        geometry = draw_geometry(0, TARGET, spec)
        positions = np.array([bodies_at(step, geometry, spec)[1] for step in range(40)])
        speeds = np.linalg.norm(np.diff(positions, axis=0), axis=1)
        self.assertTrue(np.allclose(speeds[:16], 0.0), "pusher moved before its start")
        moving = speeds[16:]
        self.assertTrue(np.allclose(moving, spec.pusher_speed), "pusher speed varied")

    def test_the_second_body_arrives_only_after_the_first_has_withdrawn(self) -> None:
        """The whole point of the design: at the commitment the target is still."""
        spec = EncounterSpec(bodies=2, schedule="probe")
        for seed in range(10):
            geometry = draw_geometry(seed, TARGET, spec)
            prober_in = [
                step
                for step in range(60)
                if np.linalg.norm(bodies_at(step, geometry, spec)[0] - TARGET)
                < spec.interaction_radius
            ]
            pusher_in = [
                step
                for step in range(60)
                if np.linalg.norm(bodies_at(step, geometry, spec)[1] - TARGET)
                < spec.interaction_radius
            ]
            if not prober_in or not pusher_in:
                continue
            self.assertLess(min(prober_in), min(pusher_in))

    def test_a_negative_step_is_refused_rather_than_wrapped(self) -> None:
        spec = EncounterSpec()
        with self.assertRaises(ValueError):
            bodies_at(-1, draw_geometry(0, TARGET, spec), spec)


class WindowTests(unittest.TestCase):
    def test_the_window_has_one_entry_per_step(self) -> None:
        spec = EncounterSpec(bodies=2)
        geometry = draw_geometry(0, TARGET, spec)
        window = bodies_over(10, 6, geometry, spec)
        self.assertEqual(window.shape, (6, 2, 3))

    def test_the_window_matches_stepping_one_at_a_time(self) -> None:
        spec = EncounterSpec(bodies=2)
        geometry = draw_geometry(1, TARGET, spec)
        window = bodies_over(12, 6, geometry, spec)
        for offset in range(6):
            np.testing.assert_allclose(
                window[offset], bodies_at(12 + offset, geometry, spec)
            )

    def test_an_empty_window_is_allowed_but_a_negative_one_is_not(self) -> None:
        spec = EncounterSpec()
        geometry = draw_geometry(0, TARGET, spec)
        self.assertEqual(len(bodies_over(0, 0, geometry, spec)), 0)
        with self.assertRaises(ValueError):
            bodies_over(0, -1, geometry, spec)


if __name__ == "__main__":
    unittest.main()
