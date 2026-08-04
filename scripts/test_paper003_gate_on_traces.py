"""Contract tests for running the gate on recorded contact traces.

CPU only. The point of this analysis is to replace a proxy threshold with the
gate itself, so the one thing it must not be is an analysis that can never
report a firing gate. A tool that always says "no" would make real contact look
like it fails the design when the failure was in the reader.

The positive control is therefore data the gate is already known to fire on,
pushed through the same function the real traces go through.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from paper003_gate_characterisation import RADIUS, slide_rollout
from paper003_gate_on_traces import judge, load_traces, render
from wm_expansion.relation_dynamics import RelationGateThresholds


def rollout_record(damping: float, seed: int) -> dict:
    targets, bodies = slide_rollout(damping, seed=seed, encounter="probe")
    return {
        "seed": seed,
        "struck_at": 10,
        "positions": [t.tolist() for t in targets],
        "ee_positions": [b.tolist() for b in bodies],
        "stopping": {"retention": damping, "coast_distance": 0.0},
        "_source": "rollout",
    }


class ControlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.thresholds = RelationGateThresholds()

    def _rate(self, damping: float, seeds: int = 6) -> float:
        rows = [
            judge(rollout_record(damping, seed), self.thresholds, RADIUS, 6)
            for seed in range(seeds)
        ]
        return float(np.mean([row["trial"] for row in rows]))

    def test_the_analysis_can_report_a_firing_gate(self) -> None:
        """Without this the whole exercise proves nothing: an analysis that
        always says no would make real contact look like a design failure."""
        self.assertEqual(self._rate(0.0), 1.0)

    def test_and_still_refuses_a_slide(self) -> None:
        self.assertEqual(self._rate(1.0), 0.0)


class RobustnessTests(unittest.TestCase):
    def test_a_trace_without_end_effector_poses_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "a.json").write_text(json.dumps({"positions": [[0, 0, 0]] * 20}))
            self.assertEqual(load_traces([tmp]), [])

    def test_a_short_trace_is_marked_unusable_rather_than_scored(self) -> None:
        record = {"seed": 1, "positions": [[0, 0, 0]] * 4,
                  "ee_positions": [[1, 0, 0]] * 4}
        self.assertFalse(judge(record, RelationGateThresholds(), RADIUS, 6)["usable"])

    def test_mismatched_lengths_are_refused(self) -> None:
        record = {"seed": 1, "positions": [[0, 0, 0]] * 20,
                  "ee_positions": [[1, 0, 0]] * 19}
        self.assertFalse(judge(record, RelationGateThresholds(), RADIUS, 6)["usable"])

    def test_the_output_states_what_h3_asks_for(self) -> None:
        rows = [judge(rollout_record(0.0, 0), RelationGateThresholds(), RADIUS, 6)]
        text = render(rows)
        self.assertIn("0.90", text)
        self.assertIn("per-trial", text)

    def test_unusable_traces_are_counted_not_hidden(self) -> None:
        rows = [
            judge(rollout_record(0.0, 0), RelationGateThresholds(), RADIUS, 6),
            {"usable": False},
        ]
        self.assertIn("1 trace(s) unusable", render(rows))


if __name__ == "__main__":
    unittest.main()
