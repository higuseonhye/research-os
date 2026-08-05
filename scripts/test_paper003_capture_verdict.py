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


class SlipTests(unittest.TestCase):
    """What a slipping carry is, and what it is not.

    Three positions were held here in one afternoon, and the middle one was
    wrong in both directions, so the reasoning is recorded rather than the
    conclusion alone.

    A target that inherits most but not all of its carrier's motion drifts
    steadily behind it - measured in the Isaac pilot, out to 68-209 mm over a
    carry of 178 steps. It was first certified as a capture, then rejected as a
    slip, and is now certified again, for a reason neither earlier position had.

    **It is a capture by the design's own definition.** Capture names two
    properties: the target is perfectly still before the arrival, and the effect
    then accumulates without bound. A target inheriting 85% of its carrier's
    motion has both.

    What a slip costs is *prediction*, and that is a different question from
    what the relation is. Over one dispense window at this carry speed it costs
    about 3.6 mm against a 20 mm tolerance, so arm D still lands - and whether
    it does is measured by the scoring rather than decided in advance by a
    verdict.

    What does disqualify a trace is never having taken hold at all, which is
    `drift`: separation constant, slip zero, and the body 183 mm away
    throughout. That is what the contact requirement rejects, and it is required
    once in a run rather than at every step, because an object genuinely held
    sits a few millimetres from `ee_frame` - one cell holds at a constant
    3.35 mm.
    """

    def _slipping(self, per_step: float) -> dict:
        """A capture cell with the target losing `per_step` metres each step."""

        record = cell()
        targets = [np.asarray(o["target"]) for o in record["observations"]]
        moved = [
            index
            for index in range(1, len(targets))
            if float(np.linalg.norm(targets[index] - targets[index - 1])) > 1e-9
        ]
        onset = moved[0] if moved else len(targets)
        drift = np.array([0.0, 1.0, 0.0])
        for index, observation in enumerate(record["observations"]):
            if index >= onset:
                observation["target"] = (
                    np.asarray(observation["target"]) + (index - onset) * per_step * drift
                ).tolist()
        return record

    def test_a_carry_that_slips_is_still_a_capture(self) -> None:
        """Deliberately, and this test asserted the opposite for one commit."""

        verdict = capture_verdict(self._slipping(0.002), interaction_radius=0.05)
        self.assertEqual(verdict["verdict"], "capture", verdict.get("reason"))

    def test_a_body_that_never_took_hold_is_not_carrying(self) -> None:
        """`drift` agrees with its body step for step and never touches it."""

        for seed in range(300, 310):
            verdict = capture_verdict(
                cell(condition="drift", schedule="burst", seed=seed),
                interaction_radius=0.05,
            )
            with self.subTest(seed=seed):
                self.assertNotEqual(verdict["verdict"], "capture", verdict.get("reason"))

    def test_contact_is_required_once_in_a_run_not_at_every_step(self) -> None:
        """An object held at a constant separation wider than the radius.

        `ee_frame` is a virtual point between the jaws, so this is what a real
        grasp looks like, and requiring contact at every step rejected it.
        """

        record = cell()
        targets = [np.asarray(o["target"]) for o in record["observations"]]
        moved = [
            index
            for index in range(1, len(targets))
            if float(np.linalg.norm(targets[index] - targets[index - 1])) > 1e-9
        ]
        onset = moved[0] if moved else len(targets)
        # Contact at the onset, then settling wider and staying there - which is
        # what a real grasp looks like, since `ee_frame` sits between the jaws.
        # An earlier version of this fixture offset the target from the first
        # step of the ride, which is a body that never touched at all, and the
        # contact requirement rejected it correctly.
        settle = np.array([0.0, 0.020, 0.0])  # 20 mm, past a 50 mm radius once added
        for index, observation in enumerate(record["observations"]):
            if index > onset:
                fraction = min(1.0, (index - onset) / 3.0)
                observation["target"] = (
                    np.asarray(observation["target"]) + fraction * settle
                ).tolist()

        verdict = capture_verdict(record, interaction_radius=0.05)
        self.assertEqual(verdict["verdict"], "capture", verdict.get("reason"))

    def test_a_true_carry_still_passes(self) -> None:
        for seed in range(300, 310):
            verdict = capture_verdict(cell(seed=seed), interaction_radius=0.05)
            with self.subTest(seed=seed):
                self.assertEqual(verdict["verdict"], "capture", verdict.get("reason"))
