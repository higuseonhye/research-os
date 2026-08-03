"""CPU-only contract tests for the Paper 003 relational target model.

Design-stage evidence, not a preregistered result. These tests pin the two
properties Paper 003 depends on:

  1. The relation gate fires on proximity-driven coupling and stays silent on
     Paper 002's persistent drift - if it fired on drift, arm C would already
     explain the failure and Paper 003 would have no contribution.
  2. The relation model's advantage is real but small on open-loop prediction,
     which is why the paper's primary endpoint is capability threshold
     crossing rather than a Paper-002-style prediction-error contrast.
"""

from __future__ import annotations

import unittest

import numpy as np

from wm_expansion.relation_dynamics import (
    CouplingSpec,
    RelationGateThresholds,
    RelationalTargetModel,
    coupling_displacement,
    _displacement_rate,
    evaluate_relation_gate,
    gate_fired_persistently,
    normal_alignment,
)
from wm_expansion.target_dynamics import ConstantVelocityTargetModel, ZeroOrderTargetModel


CENTER = np.array([0.10, 0.02])
ONSET = 10
STEPS = 70
HORIZON = 10
RADIUS = 0.05
AMPLITUDE = 0.035
PERIOD = 20


def rollout_coupling(seed: int, gain: float = 0.40, radius: float = RADIUS) -> tuple[np.ndarray, np.ndarray]:
    """Reference sweeps back and forth through the target band, bumping it."""

    spec = CouplingSpec(interaction_radius=radius, coupling_gain=gain)
    rng = np.random.default_rng(seed)
    target = CENTER + rng.normal(0.0, 0.003, 2)
    targets, references = [], []
    for step in range(STEPS):
        phase = 2 * np.pi * max(step - ONSET, 0) / PERIOD
        reference = CENTER + np.array([AMPLITUDE * np.sin(phase), 0.0])
        targets.append(target.copy())
        references.append(reference.copy())
        if step >= ONSET:
            target = target + coupling_displacement(target, reference, spec)
    return np.array(targets), np.array(references)


def rollout_drift(seed: int, velocity: float = 0.008) -> tuple[np.ndarray, np.ndarray]:
    """Paper 002's positive case: persistent drift, reference body irrelevant."""

    rng = np.random.default_rng(seed)
    target = CENTER + rng.normal(0.0, 0.003, 2)
    reference = np.array([0.10, 0.40])
    targets, references = [], []
    for step in range(STEPS):
        targets.append(target.copy())
        references.append(reference.copy())
        if step >= ONSET:
            target = target + np.array([velocity, 0.0])
        reference = reference + np.array([0.01, 0.0])
    return np.array(targets), np.array(references)


def rollout_static(seed: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    target = CENTER + rng.normal(0.0, 0.003, 2)
    reference = np.array([0.10, 0.40])
    targets, references = [], []
    for _ in range(STEPS):
        targets.append(target.copy())
        references.append(reference.copy())
        reference = reference + np.array([0.01, 0.0])
    return np.array(targets), np.array(references)


def rollout_observation_noise(seed: int, std: float = 0.003) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    reference = np.array([0.10, 0.40])
    targets, references = [], []
    for _ in range(STEPS):
        targets.append(CENTER + rng.normal(0.0, std, 2))
        references.append(reference.copy())
        reference = reference + np.array([0.01, 0.0])
    return np.array(targets), np.array(references)


class CouplingDisplacementTests(unittest.TestCase):
    def test_no_displacement_outside_interaction_radius(self) -> None:
        spec = CouplingSpec(interaction_radius=0.05)
        push = coupling_displacement(np.array([0.5, 0.0]), np.array([0.0, 0.0]), spec)
        np.testing.assert_allclose(push, np.zeros(2))

    def test_push_is_along_the_contact_normal(self) -> None:
        spec = CouplingSpec(interaction_radius=0.05, coupling_gain=0.5)
        push = coupling_displacement(np.array([0.02, 0.0]), np.array([0.0, 0.0]), spec)
        self.assertGreater(push[0], 0.0)
        self.assertAlmostEqual(push[1], 0.0)

    def test_works_in_three_dimensions(self) -> None:
        spec = CouplingSpec(interaction_radius=0.05, coupling_gain=0.5)
        push = coupling_displacement(np.zeros(3) + np.array([0.02, 0, 0]), np.zeros(3), spec)
        self.assertEqual(push.shape, (3,))


class RelationGateSpecificityTests(unittest.TestCase):
    """The gate must separate a relational gap from Paper 002's mode gap."""

    def setUp(self) -> None:
        self.thresholds = RelationGateThresholds()

    def _fire_count(self, rollout, seeds: int = 10) -> int:
        fired = 0
        for seed in range(seeds):
            targets, references = rollout(seed)
            decision = evaluate_relation_gate(
                targets, references, self.thresholds, interaction_radius=RADIUS
            )
            fired += int(decision.fired)
        return fired

    def test_fires_on_proximity_coupling(self) -> None:
        self.assertEqual(self._fire_count(rollout_coupling), 10)

    def test_silent_on_persistent_drift(self) -> None:
        """Critical: drift is arm C's case. Firing here would void the paper."""
        self.assertEqual(self._fire_count(rollout_drift), 0)

    def test_silent_on_static_and_observation_noise(self) -> None:
        self.assertEqual(self._fire_count(rollout_static), 0)
        self.assertEqual(self._fire_count(rollout_observation_noise), 0)

    def test_drift_is_explained_by_constant_velocity_but_coupling_is_not(self) -> None:
        drift_gain = evaluate_relation_gate(
            *rollout_drift(0), self.thresholds, interaction_radius=RADIUS
        ).constant_velocity_gain
        coupling_gain = evaluate_relation_gate(
            *rollout_coupling(0), self.thresholds, interaction_radius=RADIUS
        ).constant_velocity_gain
        self.assertGreater(drift_gain, 0.5)
        self.assertLess(coupling_gain, 0.3)


class RelationalModelPredictionTests(unittest.TestCase):
    def _mean_errors(self, seeds: int = 10) -> tuple[float, float, float]:
        zero, const, relation = [], [], []
        for seed in range(seeds):
            targets, references = rollout_coupling(seed)
            padded = np.hstack([targets, np.zeros((len(targets), 1))])
            b_model = ZeroOrderTargetModel()
            c_model = ConstantVelocityTargetModel()
            d_model = RelationalTargetModel(interaction_radius=RADIUS, gate_window=12)
            eb, ec, ed = [], [], []
            for index in range(len(targets) - HORIZON):
                b_model.observe(padded[index])
                c_model.observe(padded[index])
                d_model.observe(targets[index], references[index])
                eb.append(np.linalg.norm(b_model.predict(HORIZON) - padded[index + HORIZON]))
                ec.append(np.linalg.norm(c_model.predict(HORIZON) - padded[index + HORIZON]))
                ed.append(np.linalg.norm(d_model.predict(HORIZON) - targets[index + HORIZON]))
            zero.append(np.mean(eb))
            const.append(np.mean(ec))
            relation.append(np.mean(ed))
        return float(np.mean(zero)), float(np.mean(const)), float(np.mean(relation))

    def test_relation_model_beats_both_paper002_arms(self) -> None:
        zero, const, relation = self._mean_errors()
        self.assertLess(relation, zero)
        self.assertLess(relation, const)

    def test_advantage_is_small_relative_to_paper002(self) -> None:
        """Pins the finding that motivates the capability endpoint.

        Paper 002 saw a 10.8 mm C-B prediction gap. Here the D-B gap is ~1 mm,
        so Paper 003 cannot rest on a prediction-error contrast; the capability
        threshold crossing metric has to carry the claim.
        """
        zero, _, relation = self._mean_errors()
        advantage_mm = (zero - relation) * 1000.0
        self.assertGreater(advantage_mm, 0.5)
        self.assertLess(advantage_mm, 5.0)

    def test_degrades_to_zero_order_before_the_gate_fires(self) -> None:
        targets, references = rollout_coupling(0)
        model = RelationalTargetModel(interaction_radius=RADIUS, gate_window=12)
        model.observe(targets[0], references[0])
        self.assertFalse(model.gate_fired)
        np.testing.assert_allclose(model.predict(HORIZON), targets[0])


class ContrastStatisticTests(unittest.TestCase):
    """The two corrections that let the gate survive observation noise."""

    RADIUS = 0.05

    def _jitter(self, steps: int, scale: float, seed: int = 0) -> np.ndarray:
        """A target going nowhere, observed noisily - not a moving target."""
        rng = np.random.default_rng(seed)
        return np.array([np.array([0.20, 0.0]) + rng.normal(0, scale, 2) for _ in range(steps)])

    def test_fixed_window_does_not_reward_short_runs(self) -> None:
        """The regression that a run-length-normalised rate introduced.

        Dividing each run's total displacement by its own length makes short
        runs look fast. Contact runs are short and far-field runs are long, so
        independent observation noise alone produced a strong false contrast -
        the noise control fired on 90% of trials.
        """
        points = self._jitter(40, 0.01, seed=3)
        short = np.zeros(39, dtype=bool)
        short[4:9] = True  # a 5-step run, like a contact span
        long_run = np.zeros(39, dtype=bool)
        long_run[12:36] = True  # a 24-step run, like a far-field span

        def run_normalised(mask: np.ndarray) -> float:
            """What the statistic did before: each run divided by its own length."""
            start = int(np.argmax(mask))
            end = start + int(np.count_nonzero(mask))
            return float(np.linalg.norm(points[end] - points[start])) / (end - start)

        # The artefact, shown directly: the same jitter looks several times
        # faster when measured over a short run.
        self.assertGreater(run_normalised(short) / run_normalised(long_run), 2.0)
        # The fixed window measures both at the same scale.
        fast = _displacement_rate(points, short)
        slow = _displacement_rate(points, long_run)
        self.assertLess(max(fast, slow) / min(fast, slow), 1.7)

    def test_a_still_target_scores_far_below_a_moving_one(self) -> None:
        moving = np.array([np.array([0.20 + 0.01 * i, 0.0]) for i in range(20)])
        mask = np.ones(19, dtype=bool)
        self.assertGreater(
            _displacement_rate(moving, mask), 5.0 * _displacement_rate(self._jitter(20, 0.001), mask)
        )

    def test_a_class_with_no_full_window_is_unmeasurable(self) -> None:
        points = self._jitter(10, 0.001)
        tiny = np.zeros(9, dtype=bool)
        tiny[3:5] = True  # 2 steps, shorter than the 3-step window
        self.assertIsNone(_displacement_rate(points, tiny))


class PersistenceTests(unittest.TestCase):
    """A statistic crossing a threshold once is a draw, not evidence."""

    RADIUS = 0.05

    def _coupled_history(self, steps: int = 30) -> tuple[list, list]:
        target = np.array([0.20, 0.0])
        # Close enough that the first advance actually reaches contact: 7 steps
        # at 15 mm covers 105 mm, so a 2.4-radius start makes contact by step 4.
        reference = np.array([0.20 - 2.4 * self.RADIUS, 0.0])
        spec = CouplingSpec(interaction_radius=self.RADIUS, coupling_gain=0.5)
        targets, references = [], []
        for step in range(steps):
            cycle = step % 14
            direction = 1 if cycle < 7 else (-1 if cycle < 12 else 0)
            reference = reference + np.array([direction * 0.015, 0.0])
            target = target + coupling_displacement(target, reference, spec)
            targets.append(target.copy())
            references.append(reference.copy())
        return targets, references

    def test_a_sustained_relation_still_fires(self) -> None:
        targets, references = self._coupled_history()
        self.assertTrue(
            gate_fired_persistently(
                targets, references, RelationGateThresholds(), interaction_radius=self.RADIUS,
                horizon=6,
            )
        )

    def test_requiring_more_agreement_is_never_more_permissive(self) -> None:
        targets, references = self._coupled_history(steps=16)
        fired = [
            gate_fired_persistently(
                targets, references,
                RelationGateThresholds(min_consecutive_fires=need),
                interaction_radius=self.RADIUS, horizon=6,
            )
            for need in (1, 2, 4, 8)
        ]
        for stricter, looser in zip(fired[1:], fired[:-1]):
            self.assertTrue(looser or not stricter)

    def test_a_history_shorter_than_the_requirement_cannot_fire(self) -> None:
        self.assertFalse(
            gate_fired_persistently(
                [np.array([0.2, 0.0])], [np.array([0.0, 0.0])],
                RelationGateThresholds(min_consecutive_fires=3), interaction_radius=self.RADIUS,
            )
        )

    def test_zero_agreement_is_refused_as_a_setting(self) -> None:
        with self.assertRaises(ValueError):
            RelationGateThresholds(min_consecutive_fires=0).validate()


class NormalAlignmentTests(unittest.TestCase):
    """The diagnostic for the one failure mode no other recorded statistic sees.

    `estimate_coupling` fits magnitude against separation, so a tangential push
    leaves the gain and radius correct while arm D aims the wrong way.
    """

    RADIUS = 0.05

    def _contact_history(self, deflection: float, gain: float = 0.5) -> tuple[list, list]:
        """Reference walks into a target that is pushed at an angle to the normal."""
        target = np.array([0.20, 0.0])
        reference = np.array([0.20 - 3.0 * self.RADIUS, 0.0])
        targets, references = [], []
        for _ in range(30):
            reference = reference + np.array([0.008, 0.0])
            offset = target - reference
            distance = float(np.linalg.norm(offset))
            if 0.0 < distance < self.RADIUS:
                normal = offset / distance
                tangent = np.array([-normal[1], normal[0]])
                push = normal + deflection * tangent
                push = push / float(np.linalg.norm(push))
                target = target + gain * ((self.RADIUS - distance) / self.RADIUS) * self.RADIUS * push
            targets.append(target.copy())
            references.append(reference.copy())
        return targets, references

    def test_a_purely_normal_push_scores_near_one(self) -> None:
        targets, references = self._contact_history(0.0)
        self.assertAlmostEqual(
            normal_alignment(targets, references, self.RADIUS), 1.0, delta=0.02
        )

    def test_tangential_deflection_lowers_the_score(self) -> None:
        straight = normal_alignment(*self._contact_history(0.0), self.RADIUS)
        rubbed = normal_alignment(*self._contact_history(1.0), self.RADIUS)
        self.assertLess(rubbed, straight)
        # a 45-degree deflection; cos 45 = 0.707
        self.assertAlmostEqual(rubbed, 0.707, delta=0.05)

    def test_no_contact_yields_nothing_rather_than_a_number(self) -> None:
        static = [np.array([0.2, 0.0]) for _ in range(10)]
        far = [np.array([0.0, 0.0]) for _ in range(10)]
        self.assertIsNone(normal_alignment(static, far, self.RADIUS))

    def test_it_is_blind_to_magnitude_misspecification(self) -> None:
        """Deliberately: it must isolate direction, or it cannot diagnose anything.

        A far weaker contact still pushes along the normal, so the statistic
        should barely move even though the fitted gain would differ fourfold.
        """
        firm = normal_alignment(*self._contact_history(0.0, gain=0.8), self.RADIUS)
        feeble = normal_alignment(*self._contact_history(0.0, gain=0.2), self.RADIUS)
        self.assertGreater(feeble, 0.95)
        self.assertAlmostEqual(feeble, firm, delta=0.05)


if __name__ == "__main__":
    unittest.main()
