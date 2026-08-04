"""Contract tests for the whole commitment cell, simulator excluded.

CPU only. The loop these exercise is the *same code* the Isaac runner executes -
not a mirror of it - because the simulator sits behind a one-line callback. A
mirror would drift and give false confidence; this cannot.

Two defects in the two-body path were caught here before any GPU time was spent,
and both would have been silent on the GPU: a cycling first body dragged the
target out of the second body's approach line, and a phase offset started the
first body past its only advance. Each produced records byte-identical to a
one-body run.
"""

from __future__ import annotations

import unittest

import numpy as np

from wm_expansion.cell import CONDITIONS, CellSpec, ContactWorld, run_cell
from wm_expansion.commitment_episode import EpisodeSpec
from wm_expansion.encounter import EncounterSpec, bodies_at, draw_geometry

TARGET = np.array([0.20, 0.0, 0.40])


def cell(condition: str = "coupled", seed: int = 300, bodies: int = 1,
         coupling: str = "collision", schedule: str = "probe", **kwargs) -> dict:
    return run_cell(
        TARGET,
        EpisodeSpec(),
        EncounterSpec(bodies=bodies, schedule=schedule),
        CellSpec(condition=condition, seed=seed, coupling=coupling, **kwargs),
        drive=lambda target: False,
    )


def separations(record: dict) -> np.ndarray:
    """Closest approach of each body to the target over the episode."""
    targets = np.array([o["target"] for o in record["observations"]])
    bodies = np.array([o["references"] for o in record["observations"]])
    return np.linalg.norm(bodies - targets[:, None, :], axis=2).min(axis=0)


class RecordTests(unittest.TestCase):
    def test_every_condition_produces_a_valid_scored_cell(self) -> None:
        for condition in CONDITIONS:
            for bodies in (1, 2):
                record = cell(condition, bodies=bodies)
                with self.subTest(condition=condition, bodies=bodies):
                    self.assertTrue(record["valid"], "cell did not resolve")
                    self.assertIsNotNone(record["committed_at"])
                    self.assertEqual(
                        set(record["resolved"]), {"A", "B", "C", "D", "D_oracle"}
                    )

    def test_the_oracle_always_lands(self) -> None:
        for condition in CONDITIONS:
            self.assertTrue(cell(condition)["resolved"]["D_oracle"], condition)

    def test_the_record_carries_what_the_analyses_read(self) -> None:
        record = cell(bodies=2)
        for key in (
            "seed", "condition", "bodies", "encounter", "committed_at", "d_estimated",
            "gate_fire_rate", "normal_alignment", "eligible_steps", "aims",
            "observations", "valid",
        ):
            self.assertIn(key, record)
        step = record["observations"][0]
        for key in ("step", "target", "reference", "references",
                    "gate_crossed", "gate_fired", "proximity_contrast"):
            self.assertIn(key, step)

    def test_a_terminating_simulator_invalidates_the_cell(self) -> None:
        record = run_cell(
            TARGET, EpisodeSpec(), EncounterSpec(), CellSpec(),
            drive=lambda target: True,
        )
        self.assertEqual(record["early_termination"], 1)
        self.assertFalse(record["valid"])

    def test_the_same_seed_gives_the_same_cell(self) -> None:
        first, second = cell(seed=311), cell(seed=311)
        self.assertEqual(first["committed_at"], second["committed_at"])
        np.testing.assert_allclose(first["aims"]["D"], second["aims"]["D"])


class ConditionTests(unittest.TestCase):
    """Each operator must have a regime where it is the right one."""

    def _rates(self, condition: str, bodies: int = 1, seeds: int = 20) -> dict:
        landed = {arm: [] for arm in ("B", "C", "D")}
        for seed in range(300, 300 + seeds):
            record = cell(condition, seed=seed, bodies=bodies)
            if record["resolved"] is None:
                continue
            for arm in landed:
                landed[arm].append(record["resolved"][arm])
        return {arm: float(np.mean(values)) for arm, values in landed.items()}

    def test_a_static_target_is_trivial_for_everyone(self) -> None:
        rates = self._rates("static")
        self.assertEqual((rates["B"], rates["C"], rates["D"]), (1.0, 1.0, 1.0))

    def test_drift_belongs_to_the_mode_operator(self) -> None:
        """If arm D won here, the gate would not be distinguishing anything."""
        rates = self._rates("drift")
        self.assertEqual(rates["C"], 1.0)
        self.assertEqual(rates["D"], 0.0)

    def test_a_post_contact_slide_also_belongs_to_the_mode_operator(self) -> None:
        """The control that would collapse Paper 003 into Paper 002.

        The threshold here was 0.9 until the commit window was fixed to the
        arrival on 2026-08-04. That number described the old commit
        distribution - uniform over every eligible step, so almost always deep
        into the slide - rather than anything the control claims. The window now
        also admits commits in the first steps after the strike, where a
        constant-velocity model has not yet seen two steps of velocity and
        cannot extrapolate. That is a property of the arm, measured, not a
        weakening of the control.

        So the claim is asserted where it lives: the mode operator dominates
        overall, is *exact* once its estimate exists, and the relational one
        declines outright at every offset.
        """

        records = [
            record
            for seed in range(300, 320)
            if (record := cell("slide", seed=seed))["resolved"] is not None
        ]
        rates = self._rates("slide")
        self.assertGreaterEqual(rates["C"], 0.7)
        self.assertEqual(rates["D"], 0.0)
        self.assertEqual(rates["B"], 0.0)

        settled = [
            r["resolved"]["C"]
            for r in records
            if r["commit_offset"] is not None and r["commit_offset"] >= 3
        ]
        self.assertTrue(settled, "no cell committed clear of the strike")
        self.assertEqual(float(np.mean(settled)), 1.0)

    def test_the_mode_operator_is_actively_harmful_on_noise(self) -> None:
        rates = self._rates("noise")
        self.assertLess(rates["C"], rates["B"])

    def test_the_relation_operator_leads_where_the_relation_is_present(self) -> None:
        rates = self._rates("coupled", bodies=2)
        self.assertGreater(rates["D"], rates["C"])
        self.assertGreaterEqual(rates["D"], rates["B"])


class TwoBodyTests(unittest.TestCase):
    """Both defects that made a two-body run silently identical to a one-body one."""

    def test_both_bodies_actually_reach_the_target(self) -> None:
        """The first must strike to demonstrate the relation; the second must
        arrive to apply it. Either missing makes the encounter meaningless.

        Checked under the collision coupling, because separation is the right
        measure only there. Under capture the target is picked up where it was
        and then moves with its carrier, so the recorded separation is the one
        from before the carrier's step - a whole step stale, and above the
        capture radius even though the capture happened.
        """
        radius = EncounterSpec().interaction_radius
        for seed in range(300, 320):
            record = cell("coupled", seed=seed, bodies=2, coupling="collision")
            closest = separations(record)
            with self.subTest(seed=seed):
                self.assertLess(closest[0], radius, "first body never made contact")
                self.assertLess(closest[1], radius, "second body never made contact")

    def test_capture_takes_hold_and_carries(self) -> None:
        """The capture relation's own check: the target is still, then moves,
        and keeps going past the placement tolerance - which is exactly what a
        collision cannot do, its displacement being capped near the interaction
        radius.

        Run on the `burst` schedule, which is capture's pairing: a body that
        arrives and carries the target off has no reason to withdraw, and under
        `probe` the carried target is dragged back with it.
        """
        tolerance = EpisodeSpec().tolerance
        for seed in range(300, 312):
            record = cell("coupled", seed=seed, bodies=1,
                          coupling="capture", schedule="burst")
            targets = np.array([o["target"] for o in record["observations"]])
            moved = np.linalg.norm(np.diff(targets, axis=0), axis=1)
            with self.subTest(seed=seed):
                self.assertEqual(float(moved[0]), 0.0, "moved before any contact")
                self.assertGreater(float(np.max(moved)), 0.0, "never captured")
                travelled = float(np.linalg.norm(targets[-1] - targets[0]))
                self.assertGreater(travelled, tolerance, "capped like a collision")

    def test_the_first_body_stops_after_one_strike(self) -> None:
        """A cycling first body keeps pushing the target, and the second body's
        approach was aimed at where the target started. Measured, that carried
        the target 74 mm away and the second body's closest approach became
        61 mm against a 50 mm radius."""
        spec = EncounterSpec(bodies=2)
        geometry = draw_geometry(300, TARGET, spec)
        positions = np.array([bodies_at(step, geometry, spec)[0] for step in range(60)])
        speeds = np.linalg.norm(np.diff(positions, axis=0), axis=1)
        settled = spec.probe_advance + spec.probe_withdraw
        self.assertTrue(np.allclose(speeds[settled:], 0.0), "first body did not stop")

    def test_a_second_body_changes_the_outcome(self) -> None:
        """The regression guard for the whole defect class: if these agree, the
        second body is doing nothing and the encounter is not what it claims."""
        one = cell("coupled", seed=300, bodies=1)
        two = cell("coupled", seed=300, bodies=2)
        first = np.array([o["target"] for o in one["observations"]])
        second = np.array([o["target"] for o in two["observations"]])
        self.assertGreater(float(np.abs(first - second).max()), 1e-6)

    def test_the_controls_still_dissociate_with_two_bodies(self) -> None:
        for condition, winner in (("drift", "C"), ("slide", "C")):
            record = cell(condition, bodies=2)
            self.assertTrue(record["resolved"][winner], condition)
            self.assertFalse(record["resolved"]["D"], condition)


class ContactWorldTests(unittest.TestCase):
    """The target read from a simulator rather than computed by the cell."""

    def _world(self, poses: list[np.ndarray], terminate_at: int | None = None):
        state = {"i": 0, "placed": []}

        def place(bodies):
            state["placed"].append(np.asarray(bodies).copy())

        def step():
            state["i"] += 1
            return terminate_at is not None and state["i"] >= terminate_at

        def read():
            return poses[min(state["i"], len(poses) - 1)]

        return ContactWorld(place, step, read), state

    def test_the_target_comes_from_the_simulator_not_the_cell(self) -> None:
        """The whole point of the branch: nothing the cell computes moves it."""
        poses = [TARGET + np.array([0.001 * i, 0.0, 0.0]) for i in range(90)]
        world, state = self._world(poses)
        record = run_cell(TARGET, EpisodeSpec(), EncounterSpec(), CellSpec(), world=world)
        observed = np.array([o["target"] for o in record["observations"]])
        np.testing.assert_allclose(observed[0], poses[1])
        self.assertEqual(record["world"], "ContactWorld")

    def test_the_bodies_are_still_commanded(self) -> None:
        poses = [TARGET.copy() for _ in range(90)]
        world, state = self._world(poses)
        run_cell(TARGET, EpisodeSpec(), EncounterSpec(bodies=2), CellSpec(), world=world)
        self.assertGreater(len(state["placed"]), 0)
        self.assertEqual(state["placed"][0].shape, (2, 3))

    def test_termination_from_the_simulator_invalidates_the_cell(self) -> None:
        poses = [TARGET.copy() for _ in range(90)]
        world, _ = self._world(poses, terminate_at=5)
        record = run_cell(TARGET, EpisodeSpec(), EncounterSpec(), CellSpec(), world=world)
        self.assertEqual(record["early_termination"], 1)
        self.assertFalse(record["valid"])

    def test_a_malformed_pose_is_refused_rather_than_broadcast(self) -> None:
        world = ContactWorld(lambda b: None, lambda: False, lambda: np.zeros((2, 3)))
        with self.assertRaises(ValueError):
            run_cell(TARGET, EpisodeSpec(), EncounterSpec(), CellSpec(), world=world)

    def test_injected_and_contact_worlds_are_labelled_apart(self) -> None:
        """A calibration cell must never be poolable with a contact cell."""
        injected = cell()
        self.assertEqual(injected["world"], "InjectedWorld")

    def test_one_source_of_truth_or_the_other_but_not_both(self) -> None:
        world, _ = self._world([TARGET.copy()] * 90)
        with self.assertRaises(ValueError):
            run_cell(TARGET, EpisodeSpec(), EncounterSpec(), CellSpec(),
                     drive=lambda t: False, world=world)
        with self.assertRaises(ValueError):
            run_cell(TARGET, EpisodeSpec(), EncounterSpec(), CellSpec())


class SpecTests(unittest.TestCase):
    def test_unknown_conditions_and_policies_are_refused(self) -> None:
        with self.assertRaises(ValueError):
            CellSpec(condition="pushed").validate()
        with self.assertRaises(ValueError):
            CellSpec(commit_policy="last").validate()

    def test_slide_damping_outside_the_unit_interval_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            CellSpec(slide_damping=1.5).validate()


if __name__ == "__main__":
    unittest.main()
