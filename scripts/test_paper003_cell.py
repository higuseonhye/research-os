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

from wm_expansion.cell import CONDITIONS, CellSpec, run_cell
from wm_expansion.commitment_episode import EpisodeSpec
from wm_expansion.encounter import EncounterSpec, bodies_at, draw_geometry

TARGET = np.array([0.20, 0.0, 0.40])


def cell(condition: str = "coupled", seed: int = 300, bodies: int = 1, **kwargs) -> dict:
    return run_cell(
        TARGET,
        EpisodeSpec(),
        EncounterSpec(bodies=bodies),
        CellSpec(condition=condition, seed=seed, **kwargs),
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

        Not asserted at exactly 1.0: a slide that begins late in the dispense
        window leaves the velocity estimate short, and one seed in twenty misses.
        What matters is that the mode operator dominates and the relational one
        declines outright.
        """
        rates = self._rates("slide")
        self.assertGreaterEqual(rates["C"], 0.9)
        self.assertEqual(rates["D"], 0.0)

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
        arrive to apply it. Either missing makes the encounter meaningless."""
        radius = EncounterSpec().interaction_radius
        for seed in range(300, 320):
            closest = separations(cell("coupled", seed=seed, bodies=2))
            with self.subTest(seed=seed):
                self.assertLess(closest[0], radius, "first body never made contact")
                self.assertLess(closest[1], radius, "second body never made contact")

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
