"""Paper 002 WM expansion — mock-first pilot implementation (EXP-SURG-003)."""

from __future__ import annotations

from typing import Any

__all__ = ["DriftSpec", "ReachDriftEnv", "TargetMode", "PilotConfig", "run_pilot"]


def __getattr__(name: str) -> Any:
    """Avoid importing the PyTorch pilot for lightweight model-order tools."""

    if name in {"DriftSpec", "ReachDriftEnv", "TargetMode"}:
        from .env import DriftSpec, ReachDriftEnv, TargetMode

        return {
            "DriftSpec": DriftSpec,
            "ReachDriftEnv": ReachDriftEnv,
            "TargetMode": TargetMode,
        }[name]
    if name in {"PilotConfig", "run_pilot"}:
        from .protocol import PilotConfig, run_pilot

        return {"PilotConfig": PilotConfig, "run_pilot": run_pilot}[name]
    raise AttributeError(name)
