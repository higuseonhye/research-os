"""Rule-based model-adequacy expansion gate (pre-registered structure)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .world_model import StaticWorldModel


@dataclass
class GateThresholds:
    tau_error: float = 0.015
    tau_autocorr: float = 0.35
    tau_delta_nll: float = 0.002
    K_repairs: int = 3


@dataclass
class GateResult:
    fired: bool
    mean_residual: float
    autocorr: float
    delta_nll: float
    reasons: dict[str, bool]


def residual_autocorr(residuals: np.ndarray) -> float:
    if len(residuals) < 3:
        return 0.0
    x = residuals - residuals.mean()
    denom = float(np.dot(x, x)) + 1e-8
    return float(np.dot(x[:-1], x[1:]) / denom)


def mean_step_residual(wm: StaticWorldModel, obs_seq: np.ndarray, act_seq: np.ndarray) -> float:
    state = wm.init_state()
    residuals: list[float] = []
    for i in range(len(act_seq)):
        _, state, r = wm.predict_step(obs_seq[i], act_seq[i], state)
        residuals.append(r)
    return float(np.mean(residuals)) if residuals else 0.0


def measure_f1_nll_proxy(
    wm: StaticWorldModel,
    obs_seq: np.ndarray,
    act_seq: np.ndarray,
    modular_wm,
) -> float:
    """Mean squared one-step error using F1 expert only."""
    state = modular_wm.init_state()
    errs: list[float] = []
    for i in range(len(act_seq)):
        pred, state, _, _ = modular_wm.predict_step(obs_seq[i], act_seq[i], state, force_expert=1)
        if i + 1 < len(obs_seq):
            errs.append(float(np.mean((pred - obs_seq[i + 1]) ** 2)))
    return float(np.mean(errs)) if errs else 0.0


def evaluate_gate(
    wm: StaticWorldModel,
    obs_seq: np.ndarray,
    act_seq: np.ndarray,
    repair_residuals: list[float],
    thresholds: GateThresholds,
) -> GateResult:
    """Gate after K L1 repair attempts."""
    state = wm.init_state()
    step_residuals: list[float] = []
    for i in range(len(act_seq)):
        _, state, r = wm.predict_step(obs_seq[i], act_seq[i], state)
        step_residuals.append(r)

    mean_res = float(np.mean(step_residuals)) if step_residuals else 0.0
    ac = residual_autocorr(np.asarray(step_residuals, dtype=np.float64))
    nll_f0 = float(np.mean([r**2 for r in step_residuals])) if step_residuals else 0.0
    delta_nll = 0.0  # protocol patches after F1 probe training

    repairs_failed = (
        len(repair_residuals) >= thresholds.K_repairs
        and repair_residuals[-1] > thresholds.tau_error
    )

    reasons = {
        "residual_high": mean_res > thresholds.tau_error,
        "K_repairs_failed": repairs_failed,
        "autocorr_high": ac > thresholds.tau_autocorr,
        "delta_nll_high": False,
    }
    return GateResult(
        fired=False,
        mean_residual=mean_res,
        autocorr=ac,
        delta_nll=delta_nll,
        reasons=reasons,
    )
