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
    evaluate_relation_gate,
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


if __name__ == "__main__":
    unittest.main()
