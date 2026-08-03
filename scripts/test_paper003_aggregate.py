"""Contract tests for the Paper 003 pilot aggregator.

CPU only. Exists so the summary the sweep is read through is not itself
guesswork - a miscounted land rate would misreport the pilot.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from aggregate_paper003_pilot import (
    bootstrap_difference_interval,
    bootstrap_rate_interval,
    load_records,
    miss_distances,
    render,
    summarise,
)


def record(condition: str, seed: int, misses: dict[str, float], gate: float = 0.0,
           committed: int | None = 14, estimated: bool = False) -> dict:
    aims = {"D_oracle": [0.0, 0.0, 0.0]}
    aims.update({arm: [value, 0.0, 0.0] for arm, value in misses.items()})
    return {
        "condition": condition,
        "seed": seed,
        "committed_at": committed,
        "valid": committed is not None,
        "d_estimated": estimated,
        "gate_fire_rate": gate,
        "aims": aims,
        "resolved": {},
    }


class MissDistanceTests(unittest.TestCase):
    def test_measures_from_each_arm_to_the_true_landing(self) -> None:
        distances = miss_distances(record("coupled", 300, {"B": 0.08, "D": 0.007}))
        self.assertAlmostEqual(distances["B"], 0.08)
        self.assertAlmostEqual(distances["D"], 0.007)

    def test_uncommitted_cells_yield_nothing(self) -> None:
        self.assertIsNone(miss_distances(record("drift", 300, {"B": 0.1}, committed=None)))


class SummaryTests(unittest.TestCase):
    def test_land_rate_counts_only_within_tolerance(self) -> None:
        records = [
            record("coupled", 300, {"B": 0.083, "D": 0.007}),
            record("coupled", 301, {"B": 0.090, "D": 0.025}),  # D outside 20 mm
        ]
        summary = summarise(records, tolerance=0.020)["coupled"]
        self.assertEqual(summary["land_rate"]["D"], 0.5)
        self.assertEqual(summary["land_rate"]["B"], 0.0)

    def test_dissociation_is_visible_in_the_summary(self) -> None:
        """The pilot's headline: each operator lands only on its own gap."""
        records = [record("coupled", s, {"B": 0.083, "C": 0.035, "D": 0.007}, gate=0.19)
                   for s in range(300, 305)]
        records += [record("drift", s, {"B": 0.090, "C": 0.000, "D": 0.090})
                    for s in range(300, 305)]
        summary = summarise(records, tolerance=0.020)
        self.assertEqual(summary["coupled"]["land_rate"]["D"], 1.0)
        self.assertEqual(summary["coupled"]["land_rate"]["C"], 0.0)
        self.assertEqual(summary["drift"]["land_rate"]["C"], 1.0)
        self.assertEqual(summary["drift"]["land_rate"]["D"], 0.0)

    def test_uncommitted_cells_are_counted_but_not_scored(self) -> None:
        records = [
            record("static", 300, {"B": 0.0}),
            record("static", 301, {"B": 0.0}, committed=None),
        ]
        summary = summarise(records, tolerance=0.020)["static"]
        self.assertEqual(summary["cells"], 2)
        self.assertEqual(summary["committed"], 1)
        self.assertEqual(summary["invalid"], 1)

    def test_gate_and_estimation_rates_average_across_cells(self) -> None:
        records = [
            record("coupled", 300, {"D": 0.007}, gate=0.20, estimated=True),
            record("coupled", 301, {"D": 0.007}, gate=0.10, estimated=False),
        ]
        summary = summarise(records, tolerance=0.020)["coupled"]
        self.assertAlmostEqual(summary["gate_fire_rate"], 0.15)
        self.assertAlmostEqual(summary["d_estimated_rate"], 0.5)


class ConditionalEstimateTests(unittest.TestCase):
    """Preregistered secondary estimate: performance where arm D actually acted."""

    def test_conditional_covers_only_engaged_cells(self) -> None:
        records = [
            record("coupled", 300, {"B": 0.008, "D": 0.001}, estimated=True),
            record("coupled", 301, {"B": 0.050, "D": 0.005}, estimated=True),
            # declined: arm D is identical to arm B by construction
            record("coupled", 302, {"B": 0.038, "D": 0.038}, estimated=False),
            record("coupled", 303, {"B": 0.037, "D": 0.037}, estimated=False),
        ]
        summary = summarise(records, tolerance=0.020)["coupled"]

        self.assertEqual(summary["engaged_cells"], 2)
        # marginal, over all four: B lands only on the 8 mm cell, D on the 1 mm
        # and 5 mm ones. The two declined cells miss for both arms alike.
        self.assertEqual(summary["land_rate"]["B"], 0.25)
        self.assertEqual(summary["land_rate"]["D"], 0.50)
        # conditional, over the two engaged: arm D lands both, arm B one.
        self.assertEqual(summary["land_rate_engaged"]["D"], 1.0)
        self.assertEqual(summary["land_rate_engaged"]["B"], 0.5)

    def test_conditional_is_empty_when_arm_d_never_engaged(self) -> None:
        records = [record("drift", s, {"B": 0.09, "D": 0.09}) for s in range(300, 305)]
        summary = summarise(records, tolerance=0.020)["drift"]
        self.assertEqual(summary["engaged_cells"], 0)
        self.assertEqual(summary["land_rate_engaged"], {})

    def test_both_estimates_are_always_rendered(self) -> None:
        """It must not be possible to report one without the other."""
        records = [record("coupled", 300, {"B": 0.008, "D": 0.001}, estimated=True)]
        text = render(summarise(records, tolerance=0.020), 0.020)
        self.assertIn("land rate", text)
        self.assertIn("conditional on arm D engaging", text)


class BootstrapTests(unittest.TestCase):
    """Intervals the preregistration requires, so a bare rate is never quoted alone."""

    def test_interval_brackets_the_point_estimate(self) -> None:
        outcomes = [True] * 6 + [False] * 3
        low, high = bootstrap_rate_interval(outcomes)
        self.assertLessEqual(low, 6 / 9)
        self.assertGreaterEqual(high, 6 / 9)

    def test_certain_outcomes_give_a_degenerate_interval(self) -> None:
        self.assertEqual(bootstrap_rate_interval([True] * 8), (1.0, 1.0))
        self.assertEqual(bootstrap_rate_interval([False] * 8), (0.0, 0.0))

    def test_small_samples_give_wide_intervals(self) -> None:
        """The point of reporting them at pilot size."""
        low, high = bootstrap_rate_interval([True] * 6 + [False] * 3)
        self.assertGreater(high - low, 0.3)

    def test_difference_is_paired_not_independent(self) -> None:
        """Arm D falls back to arm B's aim, so it can never score worse.

        Resampling the arms independently would produce negative differences
        that cannot occur, and would overstate the uncertainty.
        """
        left = [True, True, False, True, False]
        right = [True, False, False, True, False]  # D >= B cellwise
        low, high = bootstrap_difference_interval(left, right)
        self.assertGreaterEqual(low, 0.0)
        self.assertGreater(high, 0.0)

    def test_identical_arms_give_a_zero_interval(self) -> None:
        same = [True, False, True, True]
        self.assertEqual(bootstrap_difference_interval(same, same), (0.0, 0.0))

    def test_mismatched_lengths_are_refused(self) -> None:
        self.assertEqual(bootstrap_difference_interval([True], [True, False]), (0.0, 0.0))

    def test_intervals_appear_in_the_rendered_output(self) -> None:
        records = [record("coupled", s, {"B": 0.008, "D": 0.001}) for s in range(300, 305)]
        text = render(summarise(records, tolerance=0.020), 0.020)
        self.assertIn("95% bootstrap intervals", text)
        self.assertIn("D-B paired", text)


class LoadingTests(unittest.TestCase):
    def test_reads_a_directory_and_survives_a_corrupt_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "good.json").write_text(json.dumps(record("coupled", 300, {"B": 0.08})))
            (root / "bad.json").write_text("{not json")
            records = load_records([str(root)])
        self.assertEqual(len(records), 1)


if __name__ == "__main__":
    unittest.main()
