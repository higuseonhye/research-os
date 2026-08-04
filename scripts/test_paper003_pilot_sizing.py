"""Contract tests for the pilot's sizing arithmetic.

The numbers this produces go straight into a preregistration, so the failure
mode that matters is a plausible-looking `n` that is wrong. Every case here has
an answer derivable without the code.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from paper003_pilot_sizing import (
    cells_for_power,
    load,
    observation_noise,
    sign_test_power,
)
from wm_expansion.cell import CellSpec, run_cell
from wm_expansion.commitment_episode import EpisodeSpec
from wm_expansion.encounter import EncounterSpec


class PowerTests(unittest.TestCase):
    def test_no_engagement_has_no_power_at_any_size(self) -> None:
        """Arm D that never acts is arm B, and no sample size rescues that."""
        for cells in (10, 100, 1000):
            self.assertEqual(sign_test_power(cells, engagement=0.0, d_conditional=0.78), 0.0)
        self.assertIsNone(cells_for_power(0.0, 0.78, cap=300))

    def test_power_rises_with_cells_and_with_engagement(self) -> None:
        rising = [sign_test_power(n, 0.23, 0.78) for n in (20, 40, 60, 80)]
        self.assertEqual(rising, sorted(rising))
        by_engagement = [sign_test_power(40, e, 0.78) for e in (0.10, 0.23, 0.50)]
        self.assertEqual(by_engagement, sorted(by_engagement))

    def test_it_reproduces_the_preregistered_table(self) -> None:
        """The table in paper003_prereg_v1.0.md, recomputed.

        If this drifts, the document and the code disagree about the rule, and
        the document is the one that was locked.
        """
        self.assertEqual(cells_for_power(0.10, 0.78), 101)
        self.assertEqual(cells_for_power(0.15, 0.78), 67)
        self.assertEqual(cells_for_power(0.23, 0.78), 43)
        self.assertEqual(cells_for_power(0.35, 0.78), 28)
        self.assertEqual(cells_for_power(0.50, 0.78), 19)

    def test_a_comparator_that_also_lands_costs_power(self) -> None:
        """Arm B landing 0.00 is what makes capture cheap to test. If real
        contact lets arm B land sometimes, the requirement must rise."""
        cheap = cells_for_power(0.23, 0.78)
        costly = next(
            n for n in range(5, 2000)
            if sign_test_power(n, 0.23, 0.78, b_rate=0.30) >= 0.90
        )
        self.assertGreater(costly, cheap)


class NoiseTests(unittest.TestCase):
    def test_noise_comes_from_static_cells_only(self) -> None:
        target = np.array([0.20, 0.0, 0.40])
        static = run_cell(
            target, EpisodeSpec(), EncounterSpec(bodies=1, schedule="burst"),
            CellSpec(condition="static", seed=300), drive=lambda t: False,
        )
        coupled = run_cell(
            target, EpisodeSpec(), EncounterSpec(bodies=1, schedule="burst"),
            CellSpec(condition="coupled", seed=300, coupling="capture"),
            drive=lambda t: False,
        )
        # A static target in the CPU cell is exactly still, so the estimate is
        # zero - and the coupled cell must not contribute to it.
        self.assertEqual(observation_noise([static]), 0.0)
        self.assertIsNone(observation_noise([coupled]))

    def test_records_load_from_a_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            (path / "cell_coupled_seed300.json").write_text(json.dumps({"condition": "coupled"}))
            (path / "notes.txt").write_text("ignored")
            records = load([path])
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["condition"], "coupled")


if __name__ == "__main__":
    unittest.main()
