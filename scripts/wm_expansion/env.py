"""2D reach environment with static / drift / gate negative-control modes."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import numpy as np


class TargetMode(str, Enum):
    STATIC = "static"
    DRIFT = "drift"
    NOISE = "noise"
    IMPULSE = "impulse"


@dataclass
class DriftSpec:
    mode: TargetMode = TargetMode.DRIFT
    onset_step: int = 20
    velocity: np.ndarray = field(default_factory=lambda: np.array([0.01, 0.0], dtype=np.float64))
    duration_steps: int = 30
    noise_std: float = 0.0
    impulse_delta: np.ndarray | None = None
    impulse_settle_step: int | None = None

    def to_dict(self) -> dict:
        return {
            "mode": self.mode.value,
            "onset_step": self.onset_step,
            "velocity": self.velocity.tolist(),
            "duration_steps": self.duration_steps,
            "noise_std": self.noise_std,
            "impulse_delta": None if self.impulse_delta is None else self.impulse_delta.tolist(),
            "impulse_settle_step": self.impulse_settle_step,
        }


@dataclass
class StepLog:
    t: int
    ee: np.ndarray
    target_true: np.ndarray
    target_obs: np.ndarray
    action: np.ndarray
    obs: np.ndarray
    distance: float
    success: bool


class ReachDriftEnv:
    """Planar reach: EE chases observed target; true target may drift."""

    def __init__(
        self,
        max_steps: int = 100,
        success_tol: float = 0.02,
        success_hold: int = 3,
        action_scale: float = 0.012,
        ee_gain: float = 0.85,
        obs_noise_std: float = 0.0,
    ) -> None:
        self.max_steps = max_steps
        self.success_tol = success_tol
        self.success_hold = success_hold
        self.action_scale = action_scale
        self.ee_gain = ee_gain
        self.obs_noise_std = obs_noise_std
        self.rng = np.random.default_rng(0)
        self.reset_internal()

    def reset_internal(self) -> None:
        self.t = 0
        self.ee = np.zeros(2, dtype=np.float64)
        self.ee_vel = np.zeros(2, dtype=np.float64)
        self.target_true = np.zeros(2, dtype=np.float64)
        self.target_obs = np.zeros(2, dtype=np.float64)
        self.drift: DriftSpec | None = None
        self.hold_success = 0
        self.done = False
        self.logs: list[StepLog] = []

    def reset(
        self,
        seed: int,
        target_start: np.ndarray,
        drift: DriftSpec | None = None,
    ) -> np.ndarray:
        self.rng = np.random.default_rng(seed)
        self.reset_internal()
        self.target_true = np.asarray(target_start, dtype=np.float64).copy()
        self.target_obs = self.target_true.copy()
        self.ee = self.rng.normal(0.0, 0.005, size=2)
        self.drift = drift
        return self._obs()

    def _obs(self) -> np.ndarray:
        noise = self.rng.normal(0.0, self.obs_noise_std, size=2) if self.obs_noise_std > 0 else 0.0
        self.target_obs = self.target_true + noise
        return np.concatenate([self.ee, self.ee_vel, self.target_obs]).astype(np.float32)

    def _update_target(self) -> None:
        if self.drift is None:
            return
        d = self.drift
        t = self.t
        if t < d.onset_step:
            return
        rel = t - d.onset_step
        if d.mode == TargetMode.STATIC:
            return
        if d.mode == TargetMode.DRIFT:
            if rel < d.duration_steps:
                self.target_true = self.target_true + d.velocity
            return
        if d.mode == TargetMode.NOISE:
            self.target_obs = self.target_true + self.rng.normal(0.0, d.noise_std, size=2)
            return
        if d.mode == TargetMode.IMPULSE and d.impulse_delta is not None:
            if rel == 0:
                self.target_true = self.target_true + d.impulse_delta
            return

    def step(self, action: np.ndarray) -> tuple[np.ndarray, float, bool, dict]:
        if self.done:
            raise RuntimeError("episode already done")
        action = np.asarray(action, dtype=np.float64).reshape(2)
        action = np.clip(action, -1.0, 1.0) * self.action_scale

        prev_ee = self.ee.copy()
        # Simple point-mass EE dynamics toward commanded delta
        self.ee_vel = self.ee_gain * self.ee_vel + (1.0 - self.ee_gain) * action
        self.ee = self.ee + self.ee_vel

        self._update_target()
        obs = self._obs()
        dist = float(np.linalg.norm(self.ee - self.target_true))
        if dist <= self.success_tol:
            self.hold_success += 1
        else:
            self.hold_success = 0
        success = self.hold_success >= self.success_hold

        self.logs.append(
            StepLog(
                t=self.t,
                ee=self.ee.copy(),
                target_true=self.target_true.copy(),
                target_obs=self.target_obs.copy(),
                action=action.copy(),
                obs=obs.copy(),
                distance=dist,
                success=success,
            )
        )
        self.t += 1
        timed_out = self.t >= self.max_steps
        self.done = success or timed_out
        reward = -dist
        info = {
            "distance": dist,
            "success": success,
            "target_true": self.target_true.copy(),
            "timed_out": timed_out and not success,
        }
        return obs, reward, self.done, info

    def scripted_action_toward_observed_target(self) -> np.ndarray:
        err = self.target_obs - self.ee
        norm = np.linalg.norm(err) + 1e-8
        return np.clip(err / norm, -1.0, 1.0)
