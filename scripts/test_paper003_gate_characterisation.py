"""Contract tests for the relation gate's characterisation.

CPU only. This analysis is what a frozen preregistration would cite for the
gate's thresholds, so the pieces that could quietly flatter it - which steps are
decidable, what "separates" means, and the configuration the sliding study runs
under - are pinned here.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from paper003_gate_characterisation import (
    COMMIT_WINDOW_END,
    GAIN,
    HORIZON,
    MIN_DELTAS,
    RADIUS,
    V5_GATE,
    constant_velocity_clause_work,
    gate_comparison,
    gate_under_sliding,
    load_gate_statistics,
    render,
    slide_rollout,
    threshold_plateau,
)
from wm_expansion.relation_dynamics import (
    CouplingSpec,
    RelationGateThresholds,
    coupling_displacement,
    evaluate_relation_gate,
)


def record(condition: str, pairs: list[tuple[float, float]], first_step: int = 0) -> dict:
    return {
        "condition": condition,
        "observations": [
            {
                "step": first_step + index,
                "proximity_contrast": contrast,
                "constant_velocity_gain": gain,
            }
            for index, (contrast, gain) in enumerate(pairs)
        ],
    }


class LoadingTests(unittest.TestCase):
    def test_early_steps_are_excluded_because_the_gate_cannot_decide_yet(self) -> None:
        """The gate needs min_deltas of history; counting undecidable steps as
        'did not fire' would understate every fire rate."""
        data = record("coupled", [(0.9, 0.0)] * 10, first_step=0)
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "a.json").write_text(json.dumps(data))
            statistics = load_gate_statistics([tmp])
        self.assertEqual(len(statistics["coupled"]), 10 - MIN_DELTAS)

    def test_groups_by_condition_and_survives_a_corrupt_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "a.json").write_text(json.dumps(record("coupled", [(0.9, 0.0)] * 10)))
            Path(tmp, "b.json").write_text(json.dumps(record("drift", [(-1.0, 0.9)] * 10)))
            Path(tmp, "bad.json").write_text("{not json")
            statistics = load_gate_statistics([tmp])
        self.assertEqual(sorted(statistics), ["coupled", "drift"])


class PlateauTests(unittest.TestCase):
    def _statistics(self) -> dict:
        return {
            "coupled": [(0.95, -0.2)] * 20,
            "drift": [(-1.0, 0.9)] * 20,
        }

    def test_separation_requires_the_treatment_to_fire_and_controls_not_to(self) -> None:
        rows = threshold_plateau(self._statistics(), grid=(0.50, 0.99))
        by_threshold = {row["threshold"]: row for row in rows}
        self.assertTrue(by_threshold[0.50]["separates"])
        # above the treatment's own contrast nothing fires, which is not separation
        self.assertFalse(by_threshold[0.99]["separates"])

    def test_a_firing_control_breaks_separation(self) -> None:
        statistics = self._statistics()
        statistics["drift"] = [(0.95, -0.2)] * 20  # indistinguishable from treatment
        rows = threshold_plateau(statistics, grid=(0.50,))
        self.assertFalse(rows[0]["separates"])


class ClauseTests(unittest.TestCase):
    def test_counts_only_steps_the_clause_alone_rejects(self) -> None:
        statistics = {
            "x": [
                (0.9, 0.9),  # passes contrast, blocked by constant velocity
                (0.9, 0.0),  # passes both
                (-1.0, 0.9),  # fails contrast; the clause is not what rejected it
            ]
        }
        work = constant_velocity_clause_work(statistics)["x"]
        self.assertEqual(work["passed_contrast"], 2)
        self.assertEqual(work["blocked_by_constant_velocity"], 1)

    def test_the_sweeps_own_shape_gives_the_clause_nothing_to_do(self) -> None:
        """Every control fails on contrast, so the clause is never the reason."""
        statistics = {"drift": [(-1.0, 0.9)] * 10, "static": [(0.0, 0.0)] * 10}
        work = constant_velocity_clause_work(statistics)
        self.assertEqual(sum(v["blocked_by_constant_velocity"] for v in work.values()), 0)


class SlideRolloutTests(unittest.TestCase):
    def test_full_damping_carries_no_velocity_between_steps(self) -> None:
        """Each step's displacement is exactly the instantaneous push, nothing more.

        Not tested as "the target stops once contact ends": with damping 0 the
        target barely outruns the reference, so contact does not end within the
        rollout and that assertion fails for a reason unrelated to damping.
        """
        targets, references = slide_rollout(0.0, seed=0, noise=0.0)
        spec = CouplingSpec(interaction_radius=RADIUS, coupling_gain=GAIN)
        for index in range(1, len(targets)):
            expected = coupling_displacement(targets[index - 1], references[index], spec)
            actual = targets[index] - targets[index - 1]
            np.testing.assert_allclose(actual, expected, atol=1e-12)

    def test_no_damping_accumulates_velocity_instead(self) -> None:
        travelled = lambda d: float(  # noqa: E731
            np.sum(np.linalg.norm(np.diff(np.asarray(slide_rollout(d, 0, noise=0.0)[0]), axis=0), axis=1))
        )
        self.assertGreater(travelled(1.0), 2.0 * travelled(0.0))

    def test_damping_outside_the_unit_interval_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            slide_rollout(1.5, seed=0)

    def test_a_frictionless_slide_is_explained_by_constant_velocity(self) -> None:
        """Which is what makes it arm C's case rather than arm D's."""
        targets, references = slide_rollout(1.0, seed=0, noise=0.0)
        decision = evaluate_relation_gate(
            targets, references, RelationGateThresholds(),
            interaction_radius=RADIUS, horizon=HORIZON,
        )
        self.assertGreater(decision.constant_velocity_gain, 0.30)


class SlidingGateTests(unittest.TestCase):
    def test_the_original_gate_leaks_on_the_case_that_would_collapse_the_paper(self) -> None:
        """A frictionless slide is arm C's case, and the original gate claims it.

        Per *trial*, which is H3's unit, it claimed every single one. The
        per-step rate of 12-16% concealed that entirely.
        """
        result = gate_under_sliding(1.0, V5_GATE, seeds=4, encounter="burst")
        self.assertEqual(result["trial_rate"], 1.0)
        self.assertLess(result["fire_rate"], 0.5)  # the per-step rate that hid it

    def test_the_corrected_gate_refuses_it(self) -> None:
        self.assertEqual(gate_under_sliding(1.0, seeds=4)["trial_rate"], 0.0)

    def test_it_still_fires_on_a_genuine_relation(self) -> None:
        self.assertEqual(gate_under_sliding(0.0, seeds=4)["trial_rate"], 1.0)

    def test_only_gate_and_encounter_together_satisfy_h3(self) -> None:
        """Neither change is sufficient alone, which is the whole finding.

        Fixing the gate without adding a withdrawal makes it abstain until long
        after the commitment; adding a withdrawal without fixing the gate leaves
        the slide claimed as a relation.
        """
        rows = {(r["encounter"], r["gate"]): r for r in gate_comparison(seeds=8)}
        self.assertFalse(rows[("burst", "all-history")]["passes_h3"])
        self.assertFalse(rows[("burst", "post-contact")]["passes_h3"])
        self.assertFalse(rows[("probe", "all-history")]["passes_h3"])
        self.assertTrue(rows[("probe", "post-contact")]["passes_h3"])

    def test_deciding_late_is_not_deciding(self) -> None:
        """Under the advance-only schedule the corrected gate does fire - at
        around step 34, against a commit window ending at 25."""
        row = next(
            r for r in gate_comparison(seeds=8)
            if r["encounter"] == "burst" and r["gate"] == "post-contact"
        )
        self.assertIsNotNone(row["median_first_fire"])
        self.assertGreater(row["median_first_fire"], COMMIT_WINDOW_END)
        self.assertEqual(row["coupled_in_time"], 0.0)

    def test_the_constant_velocity_statistic_ignores_the_horizon(self) -> None:
        """**This test asserted the opposite, and the opposite was the defect.**

        It pinned that `cv_gain` moved with the horizon - "enough to flip the
        verdict during this analysis" - and treated that as a property worth
        keeping. It is not a property, it is two things measured at once: the
        old statistic extrapolated a one-step velocity `horizon` steps, so on any
        curving trajectory a longer extrapolation overshoots further and a
        constant-velocity model looks worse the further ahead it is asked.

        It stayed invisible while `dispense_latency` never moved. When physics
        forced it from 6 to 8, the steadily-closing pusher - the control this
        clause exists for - went from +0.406 to +0.219 and crossed the ceiling
        while its motion was unchanged.

        Asking one step ahead removes the horizon from the expression, so the
        threshold means the same thing whatever the action's length. That is the
        property, and this is now what pins it.
        """
        targets, references = slide_rollout(1.0, seed=0)
        at_six = evaluate_relation_gate(
            targets, references, RelationGateThresholds(),
            interaction_radius=RADIUS, horizon=HORIZON,
        ).constant_velocity_gain
        at_ten = evaluate_relation_gate(
            targets, references, RelationGateThresholds(),
            interaction_radius=RADIUS, horizon=10,
        ).constant_velocity_gain
        self.assertAlmostEqual(at_six, at_ten, places=9)


class RenderTests(unittest.TestCase):
    def test_the_leak_is_stated_rather_than_left_in_a_table(self) -> None:
        statistics = {"coupled": [(0.95, -0.2)] * 20, "drift": [(-1.0, 0.9)] * 20}
        text = render(
            threshold_plateau(statistics, grid=(0.50,)),
            constant_velocity_clause_work(statistics),
            [gate_under_sliding(1.0, seeds=2)],
            gate_comparison(seeds=2),
        )
        self.assertIn("Never.", text)
        # both halves of the fix must be visible, not just the passing row
        self.assertIn("Firing eventually is not the same as firing in time.", text)
        self.assertIn("FAIL", text)


if __name__ == "__main__":
    unittest.main()
