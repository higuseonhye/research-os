"""Failure-scenario dreamers: Gaussian baseline + toy diffusion (ReSYNC-style probe)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np

from scripts.study2_dream_curriculum.perturbation_spec import PerturbationSpec


def _normalize_params(
    shift_m: float,
    onset_step: int,
    occlusion_gain: float,
    cfg: dict,
) -> np.ndarray:
    ds = cfg["dream_space"]
    x0 = (shift_m - ds["shift_m"]["min"]) / (ds["shift_m"]["max"] - ds["shift_m"]["min"])
    x1 = (onset_step - ds["onset_step"]["min"]) / (
        ds["onset_step"]["max"] - ds["onset_step"]["min"]
    )
    x2 = occlusion_gain / max(ds["occlusion_gain"]["max"], 1e-6)
    return np.clip(np.array([x0, x1, x2], dtype=np.float64), 0.0, 1.0)


def _denormalize_params(vec: np.ndarray, cfg: dict) -> tuple[float, int, float]:
    ds = cfg["dream_space"]
    v = np.clip(vec, 0.0, 1.0)
    shift = float(ds["shift_m"]["min"] + v[0] * (ds["shift_m"]["max"] - ds["shift_m"]["min"]))
    onset = int(round(ds["onset_step"]["min"] + v[1] * (ds["onset_step"]["max"] - ds["onset_step"]["min"])))
    occ = float(v[2] * ds["occlusion_gain"]["max"])
    return shift, onset, occ


class Dreamer(ABC):
    @abstractmethod
    def fit(self, informative_specs: list[PerturbationSpec], cfg: dict) -> None:
        ...

    @abstractmethod
    def sample(
        self,
        n: int,
        family: str,
        severity: str,
        cfg: dict,
        rng: np.random.Generator,
    ) -> list[PerturbationSpec]:
        ...


class GaussianDreamer(Dreamer):
    def fit(self, informative_specs: list[PerturbationSpec], cfg: dict) -> None:
        return  # no-op

    def sample(
        self,
        n: int,
        family: str,
        severity: str,
        cfg: dict,
        rng: np.random.Generator,
    ) -> list[PerturbationSpec]:
        g = cfg["dreamers"]["gaussian"]
        out: list[PerturbationSpec] = []
        for i in range(n):
            shift = float(rng.normal(g["shift_mean"], g["shift_std"]))
            onset = int(round(rng.normal(g["onset_mean"], g["onset_std"])))
            occ = float(max(0.0, rng.normal(g["occlusion_mean"], g["occlusion_std"])))
            ds = cfg["dream_space"]
            shift = float(np.clip(shift, ds["shift_m"]["min"], ds["shift_m"]["max"]))
            onset = int(np.clip(onset, ds["onset_step"]["min"], ds["onset_step"]["max"]))
            occ = float(np.clip(occ, ds["occlusion_gain"]["min"], ds["occlusion_gain"]["max"]))
            out.append(
                PerturbationSpec(
                    family=family,
                    severity=severity,
                    shift_m=shift,
                    onset_step=onset,
                    occlusion_gain=occ,
                    seed=int(rng.integers(0, 1_000_000)),
                )
            )
        return out


@dataclass
class _DiffusionState:
    betas: np.ndarray
    alphas: np.ndarray
    alpha_bars: np.ndarray
    train_data: np.ndarray


class SimpleDiffusionDreamer(Dreamer):
    """Toy DDPM on normalized [shift, onset, occlusion] — desk-only."""

    def __init__(self) -> None:
        self._state: _DiffusionState | None = None

    def fit(self, informative_specs: list[PerturbationSpec], cfg: dict) -> None:
        dc = cfg["dreamers"]["diffusion"]
        n_steps = int(dc["sample_steps"])
        betas = np.linspace(dc["beta_start"], dc["beta_end"], n_steps)
        alphas = 1.0 - betas
        alpha_bars = np.cumprod(alphas)

        if informative_specs:
            data = np.stack(
                [
                    _normalize_params(s.shift_m, s.onset_step, s.occlusion_gain, cfg)
                    for s in informative_specs
                ]
            )
        else:
            rng = np.random.default_rng(0)
            n_train = int(dc["n_train_seeds"])
            data = rng.uniform(0.25, 0.85, size=(n_train, 3))

        self._state = _DiffusionState(
            betas=betas,
            alphas=alphas,
            alpha_bars=alpha_bars,
            train_data=data,
        )

    def sample(
        self,
        n: int,
        family: str,
        severity: str,
        cfg: dict,
        rng: np.random.Generator,
    ) -> list[PerturbationSpec]:
        if self._state is None:
            self.fit([], cfg)
        assert self._state is not None
        st = self._state
        out: list[PerturbationSpec] = []
        for _ in range(n):
            # Start from random training point + noise (dream around informative region)
            idx = int(rng.integers(0, len(st.train_data)))
            x = st.train_data[idx].copy()
            t_start = len(st.betas) - 1
            noise = rng.normal(0, 1, size=3)
            x = np.sqrt(st.alpha_bars[t_start]) * x + np.sqrt(1 - st.alpha_bars[t_start]) * noise

            for t in reversed(range(len(st.betas))):
                eps = rng.normal(0, 1, size=3) if t > 0 else np.zeros(3)
                alpha = st.alphas[t]
                alpha_bar = st.alpha_bars[t]
                x = (1 / np.sqrt(alpha)) * (
                    x - (st.betas[t] / np.sqrt(1 - alpha_bar)) * eps
                )
                if t > 0:
                    x += np.sqrt(st.betas[t]) * rng.normal(0, 1, size=3)

            shift, onset, occ = _denormalize_params(x, cfg)
            out.append(
                PerturbationSpec(
                    family=family,
                    severity=severity,
                    shift_m=shift,
                    onset_step=onset,
                    occlusion_gain=occ,
                    seed=int(rng.integers(0, 1_000_000)),
                )
            )
        return out


def make_dreamer(name: str) -> Dreamer:
    if name == "gaussian":
        return GaussianDreamer()
    if name == "diffusion":
        return SimpleDiffusionDreamer()
    raise ValueError(f"Unknown dreamer: {name}")
