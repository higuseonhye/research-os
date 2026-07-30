"""CPU-only contract tests for the EXP-SURG-003 target models."""

from __future__ import annotations

import unittest

import numpy as np

from wm_expansion.target_dynamics import (
    ConstantVelocityTargetModel,
    GateThresholds,
    ZeroOrderTargetModel,
    evaluate_structure_gate,
    fit_smoothing_parameter,
    online_horizon_errors,
    synthetic_gate_controls,
)


class TargetDynamicsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.thresholds = GateThresholds()
        self.drift = np.array([0.002, 0.0, 0.0])
        self.positions = np.arange(40)[:, None] * self.drift[None, :]

    def test_gate_separates_persistent_drift_from_controls(self) -> None:
        controls = synthetic_gate_controls(
            seed=17,
            steps=40,
            drift_step=self.drift,
            noise_sigma_m=0.0002,
        )
        decisions = {
            name: evaluate_structure_gate(values, self.thresholds).fired
            for name, values in controls.items()
        }
        self.assertTrue(decisions["M1_PERSISTENT_DRIFT"])
        self.assertFalse(decisions["M0_STATIC"])
        self.assertFalse(decisions["N1_OBSERVATION_NOISE"])
        self.assertFalse(decisions["N2_SINGLE_IMPULSE"])

    def test_l3_reduces_true_open_loop_horizon_error(self) -> None:
        l1 = ZeroOrderTargetModel(position_alpha=1.0)
        l3 = ConstantVelocityTargetModel(
            position_alpha=1.0,
            velocity_alpha=1.0,
            gate_thresholds=self.thresholds,
        )
        l1_error = np.mean(online_horizon_errors(self.positions, l1, horizon=10))
        l3_error = np.mean(online_horizon_errors(self.positions, l3, horizon=10))
        self.assertGreater(l1_error, 0.019)
        self.assertLess(l3_error, l1_error * 0.25)

    def test_l1_parameter_search_cannot_add_velocity_state(self) -> None:
        result = fit_smoothing_parameter(
            self.positions,
            candidates=[0.25, 0.5, 0.75, 1.0],
            horizon=10,
            held_out_start=20,
            model_order=0,
        )
        self.assertEqual(result["selected"], 1.0)
        self.assertGreater(result["selected_mean_prediction_error_m"], 0.019)

    def test_l3_static_retention_matches_l1(self) -> None:
        static = np.repeat(np.array([[0.1, -0.2, 0.3]]), 20, axis=0)
        l1 = ZeroOrderTargetModel(position_alpha=1.0)
        l3 = ConstantVelocityTargetModel(gate_thresholds=self.thresholds)
        for position in static:
            l1.observe(position)
            l3.observe(position)
            np.testing.assert_allclose(l1.predict(10), l3.predict(10))
            self.assertFalse(l3.gate_fired)


if __name__ == "__main__":
    unittest.main()
