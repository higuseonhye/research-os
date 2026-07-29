"""EXP-SURG-003 mock pilot protocol — Phase 0 through Ep2 + gate controls."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from .env import DriftSpec, ReachDriftEnv, TargetMode
from .gate import GateResult, GateThresholds, evaluate_gate, mean_step_residual, measure_f1_nll_proxy
from .mpc import mpc_action
from .world_model import ModularWorldModel, StaticWorldModel, multi_step_prediction_error


@dataclass
class PilotConfig:
    max_steps: int = 80
    success_tol: float = 0.02
    pretrain_static_episodes: int = 40
    pretrain_steps: int = 250
    repair_steps: int = 120
    expansion_steps: int = 280
    K_repairs: int = 3
    prediction_horizon: int = 10
    gate: GateThresholds = field(default_factory=GateThresholds)
    device: str = "cpu"
    seed: int = 0


@dataclass
class EpisodeResult:
    seed: int
    arm: str
    phase: str
    condition_id: str
    success: bool
    prediction_error_h10: float
    final_distance: float
    gate_fired: bool | None = None
    gate_details: dict[str, Any] | None = None


def _collect_static_data(cfg: PilotConfig, n_episodes: int) -> tuple[np.ndarray, np.ndarray]:
    env = ReachDriftEnv(max_steps=cfg.max_steps, success_tol=cfg.success_tol)
    obs_list: list[np.ndarray] = []
    act_list: list[np.ndarray] = []
    rng = np.random.default_rng(cfg.seed)
    for ep in range(n_episodes):
        target = rng.uniform([0.08, -0.05], [0.14, 0.05])
        obs = env.reset(seed=cfg.seed * 1000 + ep, target_start=target, drift=None)
        while not env.done:
            action = env.scripted_action_toward_observed_target()
            obs, _, _, _ = env.step(action)
            obs_list.append(obs.copy())
            act_list.append(action.copy())
    return np.asarray(obs_list, dtype=np.float32), np.asarray(act_list, dtype=np.float32)


def _run_episode_mpc(
    wm: StaticWorldModel | ModularWorldModel,
    cfg: PilotConfig,
    seed: int,
    target_start: np.ndarray,
    drift: DriftSpec | None,
    force_expert: int | None = None,
) -> tuple[list[np.ndarray], list[np.ndarray], bool, float]:
    env = ReachDriftEnv(max_steps=cfg.max_steps, success_tol=cfg.success_tol)
    obs = env.reset(seed=seed, target_start=target_start, drift=drift)
    state = wm.init_state()
    obs_seq = [obs.copy()]
    act_seq: list[np.ndarray] = []
    while not env.done:
        action, state = mpc_action(wm, obs, state, force_expert=force_expert)
        obs, _, done, info = env.step(action)
        act_seq.append(action.copy())
        obs_seq.append(obs.copy())
    return obs_seq[:-1], act_seq, bool(info.get("success", False)), float(info["distance"])


def _ep1_drift_spec(onset: int = 20) -> DriftSpec:
    return DriftSpec(
        mode=TargetMode.DRIFT,
        onset_step=onset,
        velocity=np.array([0.012, 0.0], dtype=np.float64),
        duration_steps=35,
    )


def _ep2_drift_spec(ep1: DriftSpec) -> DriftSpec:
    return DriftSpec(
        mode=TargetMode.DRIFT,
        onset_step=max(8, ep1.onset_step - 8),
        velocity=np.array([0.0, 0.010], dtype=np.float64),
        duration_steps=ep1.duration_steps,
    )


def _target_for_seed(seed: int, ep2: bool = False) -> np.ndarray:
    rng = np.random.default_rng(seed)
    base = rng.uniform([0.09, -0.04], [0.13, 0.04])
    if ep2:
        base += np.array([0.02, -0.02])
    return base


def run_arm(
    cfg: PilotConfig,
    arm: str,
    seed: int,
    wm_static: StaticWorldModel,
) -> tuple[list[EpisodeResult], dict[str, Any]]:
    """Run full protocol for one arm on one seed."""
    ep1_drift = _ep1_drift_spec()
    ep2_drift = _ep2_drift_spec(ep1_drift)
    target_ep1 = _target_for_seed(seed, ep2=False)
    target_ep2 = _target_for_seed(seed, ep2=True)

    # Ep1 data collection with W0 (shared evidence)
    ep1_obs, ep1_act, _, _ = _run_episode_mpc(wm_static, cfg, seed, target_ep1, ep1_drift)

    # Phase 2: K L1 repairs
    wm_b = StaticWorldModel(device=cfg.device)
    wm_b.f0.load_state_dict(wm_static.f0.state_dict())
    repair_residuals: list[float] = []
    for _k in range(cfg.K_repairs):
        wm_b.train_on_trajectory(np.asarray(ep1_obs), np.asarray(ep1_act), steps=cfg.repair_steps)
        repair_residuals.append(mean_step_residual(wm_b, np.asarray(ep1_obs), np.asarray(ep1_act)))

    # Quick F1 candidate for gate delta NLL
    wm_probe = ModularWorldModel(wm_b.clone_f0(), device=cfg.device)
    wm_probe.train_expansion(np.asarray(ep1_obs), np.asarray(ep1_act), steps=cfg.expansion_steps // 2)
    nll_f0 = float(np.mean(repair_residuals)) if repair_residuals else 0.0
    nll_f1 = measure_f1_nll_proxy(wm_b, np.asarray(ep1_obs), np.asarray(ep1_act), wm_probe)

    gate = evaluate_gate(
        wm_b,
        np.asarray(ep1_obs),
        np.asarray(ep1_act),
        repair_residuals,
        cfg.gate,
    )
    # Patch delta_nll with measured values
    gate.delta_nll = nll_f0 - nll_f1
    gate.reasons["delta_nll_high"] = gate.delta_nll > cfg.gate.tau_delta_nll
    gate.fired = all(gate.reasons.values())

    # Phase 4: arm intervention
    if arm == "A":
        wm_eval: StaticWorldModel | ModularWorldModel = wm_static
    elif arm == "B":
        wm_eval = wm_b
    elif arm == "C":
        wm_eval = ModularWorldModel(wm_b.clone_f0(), device=cfg.device)
        wm_eval.train_expansion(np.asarray(ep1_obs), np.asarray(ep1_act), steps=cfg.expansion_steps)
    elif arm == "D":
        wm_eval = wm_probe
    else:
        raise ValueError(f"unknown arm {arm}")

    force = 1 if arm == "D" else None
    ep2_obs, ep2_act, ep2_success, ep2_dist = _run_episode_mpc(
        wm_eval, cfg, seed + 10000, target_ep2, ep2_drift, force_expert=force
    )
    pe = multi_step_prediction_error(
        wm_eval,
        np.asarray(ep2_obs),
        np.asarray(ep2_act),
        horizon=cfg.prediction_horizon,
        force_expert=force,
    )

    # Static retention
    static_obs, static_act, static_success, static_dist = _run_episode_mpc(
        wm_eval, cfg, seed + 20000, _target_for_seed(seed + 20000), drift=None, force_expert=force
    )

    results = [
        EpisodeResult(
            seed=seed,
            arm=arm,
            phase="ep2",
            condition_id="held_out_drift",
            success=ep2_success,
            prediction_error_h10=pe,
            final_distance=ep2_dist,
            gate_fired=gate.fired,
            gate_details=asdict(gate),
        ),
        EpisodeResult(
            seed=seed,
            arm=arm,
            phase="retention",
            condition_id="static",
            success=static_success,
            prediction_error_h10=multi_step_prediction_error(
                wm_eval, np.asarray(static_obs), np.asarray(static_act), cfg.prediction_horizon, force
            ),
            final_distance=static_dist,
        ),
    ]
    meta = {
        "repair_residuals": repair_residuals,
        "gate": asdict(gate),
        "ep1_len": len(ep1_obs),
    }
    return results, meta


def run_gate_controls(cfg: PilotConfig, wm: StaticWorldModel, seed: int) -> list[dict[str, Any]]:
    """H4 negative controls: noise, impulse, static."""
    controls = [
        ("static", DriftSpec(mode=TargetMode.STATIC)),
        ("noise_N1", DriftSpec(mode=TargetMode.NOISE, onset_step=20, noise_std=0.025, duration_steps=30)),
        (
            "impulse_N2",
            DriftSpec(
                mode=TargetMode.IMPULSE,
                onset_step=20,
                impulse_delta=np.array([0.03, 0.0]),
                duration_steps=5,
            ),
        ),
        ("drift_M1", _ep1_drift_spec()),
    ]
    out: list[dict[str, Any]] = []
    for name, spec in controls:
        obs, act, _, _ = _run_episode_mpc(wm, cfg, seed + hash(name) % 1000, _target_for_seed(seed), spec)
        repair_residuals = []
        wm_local = StaticWorldModel(device=cfg.device)
        wm_local.f0.load_state_dict(wm.f0.state_dict())
        for _ in range(cfg.K_repairs):
            wm_local.train_on_trajectory(np.asarray(obs), np.asarray(act), steps=cfg.repair_steps)
            repair_residuals.append(mean_step_residual(wm_local, np.asarray(obs), np.asarray(act)))
        gate = evaluate_gate(wm_local, np.asarray(obs), np.asarray(act), repair_residuals, cfg.gate)
        out.append({"control": name, "seed": seed, "gate_fired": gate.fired, "gate": asdict(gate)})
    return out


def run_pilot(cfg: PilotConfig, arms: list[str] | None = None, seeds: list[int] | None = None) -> dict[str, Any]:
    arms = arms or ["A", "B", "C"]
    seeds = seeds or [0, 1, 2, 3, 4]

    # Phase 0
    static_obs, static_act = _collect_static_data(cfg, cfg.pretrain_static_episodes)
    wm0 = StaticWorldModel(device=cfg.device)
    pretrain_loss = wm0.train_on_trajectory(static_obs, static_act, steps=cfg.pretrain_steps)

    all_results: list[EpisodeResult] = []
    arm_meta: dict[str, Any] = {}
    for seed in seeds:
        for arm in arms:
            res, meta = run_arm(cfg, arm, seed, wm0)
            all_results.extend(res)
            arm_meta[f"{arm}_{seed}"] = meta
        arm_meta[f"gate_controls_{seed}"] = run_gate_controls(cfg, wm0, seed)

    summary = _aggregate(all_results, arms)
    return {
        "experiment": "EXP-SURG-003-pilot-mock",
        "tier": "pilot",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "config": {**asdict(cfg), "gate": asdict(cfg.gate)},
        "pretrain_loss": pretrain_loss,
        "results": [asdict(r) for r in all_results],
        "summary": summary,
        "arm_meta": arm_meta,
    }


def _aggregate(results: list[EpisodeResult], arms: list[str]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for arm in arms:
        ep2 = [r for r in results if r.arm == arm and r.phase == "ep2"]
        ret = [r for r in results if r.arm == arm and r.phase == "retention"]
        if not ep2:
            continue
        summary[arm] = {
            "n_ep2": len(ep2),
            "mean_prediction_error_h10": float(np.nanmean([r.prediction_error_h10 for r in ep2])),
            "success_rate_ep2": float(np.mean([r.success for r in ep2])),
            "mean_final_distance_ep2": float(np.mean([r.final_distance for r in ep2])),
            "success_rate_static": float(np.mean([r.success for r in ret])) if ret else None,
            "gate_fire_rate": float(np.mean([bool(r.gate_fired) for r in ep2 if r.gate_fired is not None])),
        }
    if "B" in summary and "C" in summary:
        summary["C_vs_B"] = {
            "delta_prediction_error": summary["B"]["mean_prediction_error_h10"]
            - summary["C"]["mean_prediction_error_h10"],
            "delta_success_rate": summary["C"]["success_rate_ep2"] - summary["B"]["success_rate_ep2"],
        }
    return summary


def write_pilot_artifacts(out_dir: Path, payload: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (out_dir / "RUN_MANIFEST.json").write_text(
        json.dumps(
            {
                "experiment": payload["experiment"],
                "tier": payload["tier"],
                "timestamp_utc": payload["timestamp_utc"],
                "summary": payload["summary"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
