"""Minimal 1D reach mock — aligned with run_study1a.py logic."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from scripts.study2_dream_curriculum.perturbation_spec import PerturbationSpec


@dataclass
class MockOutcome:
    response: str
    successful_resolution: bool
    final_distance_m: float
    forbidden_violation: bool


def _run_response(
    seed: int,
    spec: PerturbationSpec,
    response: str,
    max_steps: int,
    tol: float,
) -> MockOutcome:
    rng = np.random.default_rng(seed * 1009 + spec.onset_step * 17)
    ee = 0.0
    target0 = 0.10 + float(rng.uniform(-0.01, 0.01))
    target_shift = target0 + spec.shift_m
    frozen = target0
    chase = target0
    violation = False
    forbidden_x = 0.115
    onset = int(spec.onset_step)
    gain = max(0.05, 1.0 - spec.occlusion_gain)
    step_size = 0.008 * gain

    for t in range(max_steps):
        if t == onset:
            if response == "CONTINUE":
                chase = frozen
            elif response == "REPLAN":
                chase = target_shift
        prev = ee
        ee = ee + step_size * np.sign(chase - ee)
        if abs(chase - ee) < step_size:
            ee = chase
        if prev <= forbidden_x <= ee or ee <= forbidden_x <= prev:
            if response == "CONTINUE" and spec.shift_m >= 0.025:
                violation = True
        if violation:
            break

    final_dist = abs(ee - target_shift)
    success = final_dist <= tol and not violation
    return MockOutcome(
        response=response,
        successful_resolution=success,
        final_distance_m=float(final_dist),
        forbidden_violation=violation,
    )


def evaluate_spec(
    spec: PerturbationSpec,
    max_steps: int = 80,
    tol: float = 0.02,
) -> dict[str, MockOutcome]:
    return {
        "CONTINUE": _run_response(spec.seed, spec, "CONTINUE", max_steps, tol),
        "REPLAN": _run_response(spec.seed, spec, "REPLAN", max_steps, tol),
    }


def is_informative(outcomes: dict[str, MockOutcome]) -> bool:
    cont = outcomes["CONTINUE"]
    repl = outcomes["REPLAN"]
    return (not cont.successful_resolution) and repl.successful_resolution


def cf_margin(outcomes: dict[str, MockOutcome], tol: float = 0.02) -> float:
    """Continuous counterfactual informativeness margin for proxy ranking (Paper 002 v0.3)."""
    cont = outcomes["CONTINUE"]
    repl = outcomes["REPLAN"]
    success_gap = float(repl.successful_resolution) - float(cont.successful_resolution)
    dist_gap = (cont.final_distance_m - repl.final_distance_m) / max(tol * 4.0, 1e-9)
    dist_gap = max(0.0, min(float(dist_gap), 1.0))
    violation_lift = (
        0.25 if cont.forbidden_violation and not repl.forbidden_violation else 0.0
    )
    return success_gap + dist_gap + violation_lift


def is_informative_from_margin(margin: float, threshold: float = 0.5) -> bool:
    return margin >= threshold
