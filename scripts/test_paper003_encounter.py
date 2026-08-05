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


class SettlingTests(unittest.TestCase):
    """`settling_steps` is the one carrier property the physical result turns on.

    A scripted point stops the instant its schedule says so; a real arm needs 22
    steps at the median. The parameter exists so that difference can be swept
    rather than argued about, and these tests pin what it means.
    """

    def _velocity(self, settling: int, steps: int = 24) -> list[float]:
        spec = EncounterSpec(schedule="burst", burst_on=10, burst_off=4,
                             settling_steps=settling, reference_speed=1.0)
        offsets = [reference_offset(step, spec) for step in range(steps + 1)]
        return [round(offsets[i + 1] - offsets[i], 9) for i in range(steps)]

    def test_zero_settling_reproduces_the_scripted_point_exactly(self) -> None:
        """The default must not perturb a single earlier CPU result."""
        spec = EncounterSpec(schedule="burst")
        default = EncounterSpec(schedule="burst", settling_steps=0)
        for step in range(60):
            self.assertEqual(reference_offset(step, spec),
                             reference_offset(step, default))

    def test_the_body_coasts_for_exactly_settling_steps_past_a_stop(self) -> None:
        """The parameter *is* the measured quantity - steps until it reads as
        stopped - so that a sweep's x-axis is comparable to the arm's 22."""
        velocity = self._velocity(3)
        # burst_on 10, so the command stops entering at step 9; the body must
        # still be moving on 9, 10, 11 and at rest on 12.
        self.assertGreater(velocity[11], 0.0)
        self.assertEqual(velocity[12], 0.0)

    def test_settling_beyond_the_pause_leaves_no_rest_at_all(self) -> None:
        """The physical case: 22 steps of settling against a commanded pause of
        4, where the pause never begins and the carry is a smooth ride."""
        self.assertTrue(all(v > 0.0 for v in self._velocity(22)))

    def test_the_schedule_survives_as_a_ripple_and_vanishes_only_on_a_multiple(self) -> None:
        """The scale is the period, not the pause - and the erasure is not total.

        This test failed on its first, stronger form, which asserted the velocity
        goes exactly constant at settling = period. It does not: a boxcar of
        width `period + 1` over a period-`p` square wave leaves a ripple of about
        1/width. Exact cancellation happens only when the width is an integer
        multiple of the period, at settling = k*period - 1.

        The distinction matters because arm C's score tracks the *ripple*, at
        r = -0.94 across the sweep - which is why arm C is not monotone in
        settling, scoring 0.917 at settling 14 and 0.800 at 22.
        """

        spec = EncounterSpec(schedule="burst", burst_on=10, burst_off=4)
        tail = slice(2 * spec.period, None)

        unsmoothed = self._velocity(0, steps=4 * spec.period)[tail]
        self.assertAlmostEqual(max(unsmoothed) - min(unsmoothed), 1.0)

        # Width = period: exact cancellation.
        exact = self._velocity(spec.period - 1, steps=4 * spec.period)[tail]
        self.assertLess(max(exact) - min(exact), 1e-9)

        # Width = period + 1: a ripple, small but real.
        ripple = self._velocity(spec.period, steps=4 * spec.period)[tail]
        self.assertGreater(max(ripple) - min(ripple), 1e-9)
        self.assertLess(max(ripple) - min(ripple), 0.10)

    def test_a_negative_settling_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            EncounterSpec(settling_steps=-1).validate()


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

    def test_a_body_faster_than_the_radius_is_refused(self) -> None:
        """It steps over the contact zone between observations, so the encounter
        contains no contact to observe however the gate is configured.

        The design was drawn at 15 mm against a 50 mm radius. Porting it to a
        scene where contact happens at 2 to 5 mm silently broke it - 40 mm
        against 12 mm - and eligibility never opened in any cell.
        """
        with self.assertRaises(ValueError):
            EncounterSpec(interaction_radius=0.012, reference_speed=0.04).validate()
        with self.assertRaises(ValueError):
            EncounterSpec(interaction_radius=0.012, reference_speed=0.006,
                          pusher_speed=0.04).validate()
        EncounterSpec(interaction_radius=0.012, reference_speed=0.006,
                      pusher_speed=0.006, probe_withdraw=5).validate()

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

    def test_adding_a_body_deliberately_changes_the_first_ones_schedule(self) -> None:
        """This once asserted the opposite, and the opposite was wrong.

        With one body the schedule repeats, because recurring contacts are what
        give the coupling estimator enough points to fit. With two, the first
        body must strike once and stop: a cycling one keeps pushing the target,
        and the second body's approach was aimed at where the target started.
        Measured, cycling carried the target 74 mm away and the second body's
        closest approach became 61 mm against a 50 mm radius - it never touched,
        and a two-body run came out byte-identical to a one-body one.

        So the two schedules must differ, and they must agree up to the first
        body's single advance-and-withdraw.
        """
        one = EncounterSpec(bodies=1)
        two = EncounterSpec(bodies=2)
        geometry = draw_geometry(3, TARGET, two)  # phase offset 0 for two bodies
        settled = two.probe_advance + two.probe_withdraw
        for step in range(settled):
            np.testing.assert_allclose(
                bodies_at(step, geometry, one)[0], bodies_at(step, geometry, two)[0]
            )
        later = [
            float(np.linalg.norm(bodies_at(step, geometry, one)[0]
                                 - bodies_at(step, geometry, two)[0]))
            for step in range(settled + 2, 40)
        ]
        self.assertGreater(max(later), 0.01, "the first body kept cycling")

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


class LateralOffsetTests(unittest.TestCase):
    """A grasp is a rendezvous; a collision is a fly-by.

    See docs/paper003/paper003_rendezvous_v0.1.md.
    """

    def test_zero_scale_aims_at_the_centre(self) -> None:
        target = np.array([0.20, 0.0, 0.40])
        spec = EncounterSpec(lateral_offset_scale=0.0)
        for seed in range(300, 320):
            geometry = draw_geometry(seed, target, spec)
            with self.subTest(seed=seed):
                self.assertEqual(geometry.lateral_offset, 0.0)

    def test_the_approach_azimuth_stays_random_either_way(self) -> None:
        """The substantive variation must survive. Fixing the axis once made the
        whole interaction translation-invariant - ten seeds, one encounter."""

        target = np.array([0.20, 0.0, 0.40])
        for scale in (0.0, 0.5):
            spec = EncounterSpec(lateral_offset_scale=scale)
            azimuths = {
                round(draw_geometry(seed, target, spec).azimuth, 6)
                for seed in range(300, 320)
            }
            with self.subTest(scale=scale):
                self.assertGreater(len(azimuths), 15)

    def test_a_centred_approach_passes_through_the_target(self) -> None:
        target = np.array([0.20, 0.0, 0.40])
        spec = EncounterSpec(lateral_offset_scale=0.0, schedule="burst",
                             reference_speed=0.002, pusher_speed=0.002,
                             interaction_radius=0.012)
        for seed in range(300, 310):
            geometry = draw_geometry(seed, target, spec)
            closest = min(
                float(np.linalg.norm(bodies_at(step, geometry, spec)[0] - target))
                for step in range(200)
            )
            with self.subTest(seed=seed):
                self.assertLess(closest, 0.001, "the script never reaches the block")

    def test_an_out_of_range_scale_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            EncounterSpec(lateral_offset_scale=1.5).validate()
