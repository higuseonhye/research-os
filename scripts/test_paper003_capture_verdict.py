"""Contract tests for the pilot's first question: was that a capture?

CPU only, and deliberately so - the verdict has to be exercised on traces whose
answer is known before it is pointed at an Isaac trace whose answer is not.
"""

from __future__ import annotations

import unittest

import numpy as np

from wm_expansion.capture_verdict import capture_verdict
from wm_expansion.cell import CellSpec, run_cell
from wm_expansion.commitment_episode import EpisodeSpec
from wm_expansion.encounter import EncounterSpec

TARGET = np.array([0.20, 0.0, 0.40])


def cell(condition: str = "coupled", coupling: str = "capture",
         schedule: str = "burst", seed: int = 300) -> dict:
    return run_cell(
        TARGET, EpisodeSpec(), EncounterSpec(bodies=1, schedule=schedule),
        CellSpec(condition=condition, seed=seed, coupling=coupling),
        drive=lambda target: False,
    )


class VerdictTests(unittest.TestCase):
    def test_a_capture_cell_reads_as_a_capture(self) -> None:
        for seed in range(300, 315):
            verdict = capture_verdict(cell(seed=seed))
            with self.subTest(seed=seed):
                self.assertEqual(verdict["verdict"], "capture", verdict.get("reason"))
                self.assertGreaterEqual(verdict["still_steps"], 3)

    def test_a_collision_cell_does_not(self) -> None:
        """The interesting failure: the relation is real and the effect
        self-limits, which is exactly why collision was rejected."""

        for seed in range(300, 315):
            verdict = capture_verdict(cell(coupling="collision", schedule="probe", seed=seed))
            with self.subTest(seed=seed):
                self.assertNotEqual(verdict["verdict"], "capture", verdict.get("reason"))

    def test_a_static_target_reads_as_nothing(self) -> None:
        self.assertEqual(capture_verdict(cell(condition="static"))["verdict"], "none")

    def test_a_drifting_target_is_not_a_capture(self) -> None:
        """`drift` moves along the body's own axis at its own speed, so its
        displacement agrees with that body's - it is the trace most likely to be
        mistaken for a carry, and the pilot must not certify it."""

        for seed in range(300, 310):
            verdict = capture_verdict(cell(condition="drift"))
            with self.subTest(seed=seed):
                self.assertNotEqual(verdict["verdict"], "capture", verdict.get("reason"))

    def test_a_target_already_moving_before_the_carry_is_refused(self) -> None:
        """The carriage failure, stated as a test.

        A target that has travelled before being picked up has a history, and a
        single-entity model has something to learn from it. That is what killed
        carriage, and a pilot that certified it would hand the paper back the
        design it already rejected.
        """

        record = cell()
        targets = np.asarray([o["target"] for o in record["observations"]])
        # Give it a drift of its own from the first step onward, so it is never
        # still and its own trajectory carries information throughout.
        drift = np.linspace(0.0, 0.20, len(targets))[:, None] * np.array([0.0, 1.0, 0.0])
        for observation, offset in zip(record["observations"], drift):
            observation["target"] = (np.asarray(observation["target"]) + offset).tolist()

        verdict = capture_verdict(record)
        self.assertNotEqual(verdict["verdict"], "capture")

    def test_an_empty_record_is_refused_rather_than_guessed(self) -> None:
        self.assertEqual(capture_verdict({"observations": []})["verdict"], "none")
        self.assertEqual(capture_verdict({})["verdict"], "none")


if __name__ == "__main__":
    unittest.main()
