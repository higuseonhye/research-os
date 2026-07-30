"""Interpretable target-dynamics models for EXP-SURG-003.

The confirmatory comparison is deliberately a model-order test.  L1 may tune
parameters of a zero-order (static-target) estimator, while L3 adds a velocity
state and a gate.  The separation is architectural: no L1 parameter value can
produce a non-zero open-loop target velocity.
"""

from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
from typing import Iterable, Sequence

import numpy as np


ArrayLike = Sequence[float] | np.ndarray


@dataclass(frozen=True)
class GateThresholds:
    """Pre-registered thresholds for the structural-expansion gate."""

    min_deltas: int = 4
    speed_floor_m_per_step: float = 5e-4
    min_active_fraction: float = 0.75
    min_directional_consistency: float = 0.90
    min_cv_error_improvement: float = 0.50

    def validate(self) -> None:
        if self.min_deltas < 2:
            raise ValueError("min_deltas must be >= 2")
        if self.speed_floor_m_per_step <= 0:
            raise ValueError("speed_floor_m_per_step must be > 0")
        for name in (
            "min_active_fraction",
            "min_directional_consistency",
            "min_cv_error_improvement",
        ):
            value = float(getattr(self, name))
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0, 1]")


@dataclass(frozen=True)
class GateDecision:
    fired: bool
    n_deltas: int
    mean_speed_m_per_step: float
    active_fraction: float
    directional_consistency: float
    zero_order_rmse_m: float
    constant_velocity_rmse_m: float
    cv_error_improvement: float

    def to_dict(self) -> dict[str, float | int | bool]:
        return asdict(self)


def _positions_array(positions: Iterable[ArrayLike]) -> np.ndarray:
    array = np.asarray(list(positions), dtype=np.float64)
    if array.size == 0:
        return np.empty((0, 3), dtype=np.float64)
    if array.ndim != 2 or array.shape[1] != 3:
        raise ValueError("positions must have shape [time, 3]")
    if not np.isfinite(array).all():
        raise ValueError("positions must be finite")
    return array


def evaluate_structure_gate(
    positions: Iterable[ArrayLike], thresholds: GateThresholds
) -> GateDecision:
    """Evaluate whether a position history supports a velocity-state expert."""

    thresholds.validate()
    array = _positions_array(positions)
    deltas = np.diff(array, axis=0)
    n_deltas = int(len(deltas))
    if n_deltas == 0:
        return GateDecision(False, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    speeds = np.linalg.norm(deltas, axis=1)
    mean_speed = float(np.mean(speeds))
    active_fraction = float(np.mean(speeds >= thresholds.speed_floor_m_per_step))
    speed_sum = float(np.sum(speeds))
    directional_consistency = (
        float(np.linalg.norm(np.sum(deltas, axis=0)) / speed_sum)
        if speed_sum > 0.0
        else 0.0
    )
    zero_order_rmse = float(np.sqrt(np.mean(np.square(speeds))))
    if n_deltas >= 2:
        acceleration = np.diff(deltas, axis=0)
        cv_rmse = float(
            np.sqrt(np.mean(np.sum(np.square(acceleration), axis=1)))
        )
    else:
        cv_rmse = zero_order_rmse
    improvement = (
        float((zero_order_rmse - cv_rmse) / zero_order_rmse)
        if zero_order_rmse > 0.0
        else 0.0
    )

    fired = bool(
        n_deltas >= thresholds.min_deltas
        and mean_speed >= thresholds.speed_floor_m_per_step
        and active_fraction >= thresholds.min_active_fraction
        and directional_consistency >= thresholds.min_directional_consistency
        and improvement >= thresholds.min_cv_error_improvement
    )
    return GateDecision(
        fired=fired,
        n_deltas=n_deltas,
        mean_speed_m_per_step=mean_speed,
        active_fraction=active_fraction,
        directional_consistency=directional_consistency,
        zero_order_rmse_m=zero_order_rmse,
        constant_velocity_rmse_m=cv_rmse,
        cv_error_improvement=improvement,
    )


class ZeroOrderTargetModel:
    """L1-compatible target model: filtered position with zero future velocity."""

    def __init__(self, position_alpha: float = 1.0) -> None:
        if not 0.0 < position_alpha <= 1.0:
            raise ValueError("position_alpha must be in (0, 1]")
        self.position_alpha = float(position_alpha)
        self.position: np.ndarray | None = None

    def observe(self, position: ArrayLike) -> None:
        value = np.asarray(position, dtype=np.float64)
        if value.shape != (3,):
            raise ValueError("position must have shape [3]")
        if self.position is None:
            self.position = value.copy()
        else:
            self.position = (
                self.position_alpha * value
                + (1.0 - self.position_alpha) * self.position
            )

    def predict(self, horizon: int) -> np.ndarray:
        if horizon < 0:
            raise ValueError("horizon must be >= 0")
        if self.position is None:
            raise RuntimeError("observe must be called before predict")
        return self.position.copy()


class ConstantVelocityTargetModel(ZeroOrderTargetModel):
    """L3 target model: adds a gated velocity state to the L1 position state."""

    def __init__(
        self,
        position_alpha: float = 1.0,
        velocity_alpha: float = 1.0,
        gate_thresholds: GateThresholds | None = None,
        gate_window: int = 8,
    ) -> None:
        super().__init__(position_alpha=position_alpha)
        if not 0.0 < velocity_alpha <= 1.0:
            raise ValueError("velocity_alpha must be in (0, 1]")
        if gate_window < 3:
            raise ValueError("gate_window must be >= 3")
        self.velocity_alpha = float(velocity_alpha)
        self.gate_thresholds = gate_thresholds or GateThresholds()
        self.gate_thresholds.validate()
        self.history: deque[np.ndarray] = deque(maxlen=int(gate_window) + 1)
        self.velocity = np.zeros(3, dtype=np.float64)
        self.gate_decision = evaluate_structure_gate([], self.gate_thresholds)

    def observe(self, position: ArrayLike) -> None:
        value = np.asarray(position, dtype=np.float64)
        if value.shape != (3,):
            raise ValueError("position must have shape [3]")
        previous_raw = self.history[-1] if self.history else None
        super().observe(value)
        self.history.append(value.copy())
        if previous_raw is not None:
            delta = value - previous_raw
            self.velocity = (
                self.velocity_alpha * delta
                + (1.0 - self.velocity_alpha) * self.velocity
            )
        self.gate_decision = evaluate_structure_gate(
            self.history, self.gate_thresholds
        )

    @property
    def gate_fired(self) -> bool:
        return self.gate_decision.fired

    def predict(self, horizon: int) -> np.ndarray:
        base = super().predict(horizon)
        if not self.gate_fired:
            return base
        return base + float(horizon) * self.velocity


def online_horizon_errors(
    positions: Iterable[ArrayLike],
    model: ZeroOrderTargetModel,
    horizon: int,
    start_index: int = 0,
) -> list[float]:
    """Compute causal open-loop errors without teacher forcing inside a rollout."""

    if horizon < 1:
        raise ValueError("horizon must be >= 1")
    array = _positions_array(positions)
    errors = []
    for index, position in enumerate(array):
        model.observe(position)
        future = index + horizon
        if index >= start_index and future < len(array):
            errors.append(float(np.linalg.norm(model.predict(horizon) - array[future])))
    return errors


def fit_smoothing_parameter(
    positions: Iterable[ArrayLike],
    candidates: Sequence[float],
    horizon: int,
    held_out_start: int,
    model_order: int,
    gate_thresholds: GateThresholds | None = None,
    gate_window: int = 8,
) -> dict[str, object]:
    """Select an L1 position alpha or L3 velocity alpha on held-out Ep1 data."""

    array = _positions_array(positions)
    attempts = []
    for candidate in candidates:
        if model_order == 0:
            model: ZeroOrderTargetModel = ZeroOrderTargetModel(candidate)
        elif model_order == 1:
            model = ConstantVelocityTargetModel(
                position_alpha=1.0,
                velocity_alpha=candidate,
                gate_thresholds=gate_thresholds,
                gate_window=gate_window,
            )
        else:
            raise ValueError("model_order must be 0 or 1")
        errors = online_horizon_errors(
            array, model, horizon=horizon, start_index=held_out_start
        )
        mean_error = float(np.mean(errors)) if errors else float("inf")
        attempts.append(
            {
                "candidate": float(candidate),
                "mean_prediction_error_m": mean_error,
                "n_predictions": len(errors),
            }
        )
    best = min(attempts, key=lambda row: row["mean_prediction_error_m"])
    return {
        "model_order": model_order,
        "horizon": horizon,
        "held_out_start": held_out_start,
        "attempts": attempts,
        "selected": best["candidate"],
        "selected_mean_prediction_error_m": best["mean_prediction_error_m"],
    }


def synthetic_gate_controls(
    seed: int,
    steps: int,
    drift_step: ArrayLike,
    noise_sigma_m: float,
) -> dict[str, np.ndarray]:
    """Create matched M0/M1/N1/N2 target histories for H4."""

    if steps < 8:
        raise ValueError("steps must be >= 8")
    rng = np.random.default_rng(seed)
    origin = rng.uniform(-0.1, 0.1, size=3)
    drift = np.asarray(drift_step, dtype=np.float64)
    if drift.shape != (3,):
        raise ValueError("drift_step must have shape [3]")
    static = np.repeat(origin[None, :], steps, axis=0)
    persistent = static + np.arange(steps, dtype=np.float64)[:, None] * drift
    noise = static + rng.normal(0.0, noise_sigma_m, size=static.shape)
    impulse = static.copy()
    impulse_at = steps // 2
    impulse[impulse_at] += drift * 8.0
    return {
        "M0_STATIC": static,
        "M1_PERSISTENT_DRIFT": persistent,
        "N1_OBSERVATION_NOISE": noise,
        "N2_SINGLE_IMPULSE": impulse,
    }
