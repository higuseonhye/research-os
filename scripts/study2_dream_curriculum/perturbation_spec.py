"""Perturbation spec + taxonomy helpers for EXP-SURG-002."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PerturbationSpec:
    """v0.1 dream output — maps to 001A/D injection knobs."""

    family: str
    severity: str
    shift_m: float
    onset_step: int
    occlusion_gain: float
    seed: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise SystemExit(f"PyYAML required for {path}") from exc
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_taxonomy(repo_root: Path, rel_path: str) -> dict[str, Any]:
    return load_yaml(repo_root / rel_path)


def severity_to_shift(severity: str, cfg: dict[str, Any]) -> float:
    lo = float(cfg["dream_space"]["shift_m"]["min"])
    hi = float(cfg["dream_space"]["shift_m"]["max"])
    mid = (lo + hi) / 2
    mapping = {"small": lo + 0.2 * (mid - lo), "mid": mid, "unreachable": hi}
    return mapping.get(severity, mid)


def severity_to_occlusion(severity: str) -> float:
    mapping = {
        "mild_blur": 0.2,
        "partial": 0.45,
        "persistent_full": 0.75,
        "small": 0.0,
        "mid": 0.35,
        "unreachable": 0.5,
    }
    return mapping.get(severity, 0.3)
