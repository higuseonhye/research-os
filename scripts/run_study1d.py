#!/usr/bin/env python3
"""EXP-SURG-001D — Occlusion × multi-mode counterfactual orchestration.

Modes:
  --mock     Kinematic mock (default for D0 smoke).
  --isaac    Launch Isaac runner (GPU / RunPod).
  --merge    Re-analyze existing isaac_results.json only.

Contract: experiments/.../docs/study1d_occlusion_proxy_v0.1.md
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[1]
EXP_ROOT = REPO / "experiments/surgical_intelligence/exp_surg_001_execute_or_defer"
DEFAULT_CFG = EXP_ROOT / "config/study1d_occlusion_multimode.yaml"
ARTIFACT_ROOT = EXP_ROOT / "artifacts/study1d_occlusion_multimode"
ISAAC_SCRIPT = REPO / "scripts/orbit_reach_study1d_counterfactual.py"

TOL_M = 0.02
EXPERIMENT_ID = "EXP-SURG-001D"


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise SystemExit("PyYAML required: pip install pyyaml") from exc
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def git_commit() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO,
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return out.strip()
    except Exception:
        return "unknown"


def occlusion_level_cfg(cfg: dict[str, Any], level: int) -> dict[str, Any]:
    levels = cfg["perturbation"]["levels"]
    key = str(level)
    if key not in levels and level in levels:
        return dict(levels[level])
    if key in levels:
        return dict(levels[key])
    raise KeyError(f"Unknown occlusion level {level}")


def terminal_category(success: bool, violation: bool, timed_out: bool, handover: bool = False) -> str:
    if handover:
        return "handover_proxy"
    if violation:
        return "unsafe_failure"
    if success:
        return "successful_resolution"
    if timed_out:
        return "timeout_failure"
    return "safe_unresolved"


@dataclass
class BranchRecord:
    seed: int
    episode: int
    response: str
    response_class: str
    replan_delay: int | None
    shift_distance_m: float
    onset_step: int
    response_start_step: int
    final_distance_m: float
    path_length_m: float
    completion_steps: int
    recovery_duration: int
    forbidden_violation: bool
    successful_resolution: bool
    terminal_category: str
    branch_replay_ok: bool
    perturbation_id: str = "P3"
    occlusion_proxy: str = "gain_scale_flag_v0.1"
    occlusion_level: int = 1
    visibility_fraction: float = 0.35
    visibility_cleared: bool = False
    mode: str = "mock"
    experiment_id: str = EXPERIMENT_ID
    extra: dict[str, Any] = field(default_factory=dict)


def mock_branch(
    seed: int,
    shift_m: float,
    response: str,
    response_class: str,
    replan_delay: int | None,
    occlusion_level: int,
    occ_cfg: dict[str, Any],
    reobserve_hold: int,
    onset: int,
    max_steps: int,
    tol: float,
    step_size: float = 0.012,
) -> BranchRecord:
    """2D Y-axis reach mock with gain-scale occlusion proxy v0.1."""
    vis_frac = float(occ_cfg["visibility_fraction"])
    rng = np.random.default_rng(seed * 1009 + int(round(shift_m * 10000)) * 17 + occlusion_level * 31)
    ee_y = float(rng.uniform(-0.005, 0.005))
    target0_y = 0.10 + float(rng.uniform(-0.01, 0.01))
    frozen = target0_y
    shifted = target0_y + shift_m
    path = 0.0
    violation = False
    forbidden_y = target0_y + shift_m * 0.45
    visibility_cleared = False

    for _ in range(onset):
        prev = ee_y
        ee_y += step_size * float(np.sign(target0_y - ee_y))
        if abs(target0_y - ee_y) < step_size:
            ee_y = target0_y
        path += abs(ee_y - prev)

    delay = 0 if replan_delay is None else int(replan_delay)
    is_continue = response == "CONTINUE"
    is_reobserve = response == "REOBSERVE"
    is_handover = response == "HANDOVER"
    is_reshape = response == "RESHAPE"
    is_replan = response.startswith("REPLAN")

    if is_continue:
        switch_step = onset
        response_start = onset
    elif is_reobserve:
        switch_step = onset + reobserve_hold
        response_start = onset
    elif is_handover:
        switch_step = onset
        response_start = onset
    elif is_reshape:
        switch_step = onset + int(occ_cfg.get("reshape_steps", 20))
        response_start = onset
    elif is_replan:
        switch_step = onset + delay
        response_start = switch_step
    else:
        switch_step = onset
        response_start = onset

    handover_terminal = False
    for t in range(onset, max_steps):
        if is_handover:
            handover_terminal = True
            break

        eff_step = step_size
        chase = frozen

        if is_continue:
            chase = frozen
            if not visibility_cleared:
                eff_step = step_size * vis_frac
        elif is_reobserve:
            if t < onset + reobserve_hold:
                eff_step = 0.0
                chase = frozen
            else:
                visibility_cleared = True
                chase = shifted
                eff_step = step_size
        elif is_reshape:
            if t < switch_step:
                eff_step = step_size * vis_frac
                chase = frozen
            else:
                visibility_cleared = True
                chase = shifted
                eff_step = step_size
        elif is_replan:
            if t < switch_step:
                chase = frozen
                if not visibility_cleared:
                    eff_step = step_size * vis_frac
            else:
                chase = shifted
                eff_step = step_size

        prev = ee_y
        if eff_step > 0:
            ee_y += eff_step * float(np.sign(chase - ee_y))
            if abs(chase - ee_y) < eff_step:
                ee_y = chase
        path += abs(ee_y - prev)

        if not is_continue and shift_m > 0.015:
            if min(prev, ee_y) <= forbidden_y <= max(prev, ee_y) and t < switch_step:
                violation = True

        if t + 1 >= max_steps:
            break

    if is_handover:
        success = False
        timed_out = False
        completion = onset + 1
        final_dist = abs(ee_y - shifted)
    else:
        remaining = max_steps - switch_step
        base_steps = shift_m / step_size
        delay_penalty = 0.04 * delay * (shift_m / 0.01)
        occl_penalty = 0.0 if visibility_cleared else 0.15 * (1.0 - vis_frac) * (shift_m / 0.03)
        steps_needed = math.ceil(base_steps * (1.0 + delay_penalty + occl_penalty)) + int(rng.integers(0, 3))
        timed_out = remaining < steps_needed and not is_continue
        final_dist = abs(ee_y - shifted)

        if is_continue:
            success = shift_m <= tol and final_dist <= tol and not violation
        else:
            success = (
                not timed_out
                and not violation
                and final_dist <= tol
                and (is_reobserve or is_reshape or remaining >= steps_needed)
            )

        completion = max_steps if timed_out or (not success and final_dist > tol) else min(
            max_steps, switch_step + steps_needed
        )
        if success:
            completion = min(max_steps, switch_step + steps_needed)

    return BranchRecord(
        seed=seed,
        episode=seed,
        response=response,
        response_class=response_class,
        replan_delay=replan_delay,
        shift_distance_m=shift_m,
        onset_step=onset,
        response_start_step=response_start,
        final_distance_m=final_dist if success else max(final_dist, shift_m * 0.5),
        path_length_m=path,
        completion_steps=completion,
        recovery_duration=max(0, completion - response_start),
        forbidden_violation=violation,
        successful_resolution=bool(success and not handover_terminal),
        terminal_category=terminal_category(bool(success), violation, timed_out if not is_handover else False, handover_terminal),
        branch_replay_ok=True,
        occlusion_level=occlusion_level,
        visibility_fraction=vis_frac,
        visibility_cleared=visibility_cleared,
        mode="mock",
    )


def response_specs(cfg: dict[str, Any], mode_names: list[str]) -> list[tuple[str, str, int | None]]:
    """Return (response_id, response_class, replan_delay)."""
    by_id = {r["id"]: r for r in cfg["responses"]}
    specs: list[tuple[str, str, int | None]] = []
    replan_delay = int(cfg.get("replan_delay_steps", 20))
    for name in mode_names:
        if name not in by_id:
            raise KeyError(f"Unknown mode {name}")
        meta = by_id[name]
        cls = str(meta.get("class", "policy"))
        if name == "REPLAN":
            specs.append((f"REPLAN_d{replan_delay}", cls, replan_delay))
        else:
            specs.append((name, cls, None))
    return specs


def run_mock_grid(cfg: dict[str, Any], smoke: bool) -> list[BranchRecord]:
    block = cfg["smoke"] if smoke else cfg.get("full", cfg["smoke"])
    seeds = list(block["seeds"])
    modes = list(block["modes"])
    levels = list(block["occlusion_levels"])
    shift_m = float(cfg["target_shift_m"])
    onset = int(cfg["onset"])
    max_steps = int(cfg["max_steps"])
    reobserve_hold = int(
        next(r["reobserve_hold_steps"] for r in cfg["responses"] if r["id"] == "REOBSERVE")
    )

    records: list[BranchRecord] = []
    for level in levels:
        occ = occlusion_level_cfg(cfg, int(level))
        for seed in seeds:
            for resp, rcls, delay in response_specs(cfg, modes):
                records.append(
                    mock_branch(
                        seed=seed,
                        shift_m=shift_m,
                        response=resp,
                        response_class=rcls,
                        replan_delay=delay,
                        occlusion_level=int(level),
                        occ_cfg=occ,
                        reobserve_hold=reobserve_hold,
                        onset=onset,
                        max_steps=max_steps,
                        tol=TOL_M,
                    )
                )
    return records


def records_to_dicts(records: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for r in records:
        if isinstance(r, dict):
            out.append(r)
        else:
            d = asdict(r)
            d.pop("extra", None)
            out.append(d)
    return out


def aggregate_by_mode(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for r in records:
        groups.setdefault(str(r["response"]), []).append(r)
    rows: list[dict[str, Any]] = []
    for response, xs in sorted(groups.items()):
        n = len(xs)
        rows.append(
            {
                "response": response,
                "response_class": xs[0].get("response_class"),
                "n": n,
                "successful_resolution_rate": sum(1 for x in xs if x["successful_resolution"]) / n,
                "forbidden_violation_rate": sum(1 for x in xs if x["forbidden_violation"]) / n,
                "mean_final_distance_m": float(np.mean([x["final_distance_m"] for x in xs])),
                "mean_completion_steps": float(np.mean([x["completion_steps"] for x in xs])),
            }
        )
    return rows


def write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        return
    keys = list(records[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in records:
            w.writerow({k: r.get(k) for k in keys})


def run_manifest(cfg: dict[str, Any], mode: str, smoke: bool, commit: str) -> dict[str, Any]:
    phase = "D0_smoke" if smoke else "D1_full"
    block = cfg["smoke"] if smoke else cfg.get("full", cfg["smoke"])
    return {
        "experiment_id": EXPERIMENT_ID,
        "phase": phase,
        "mode": mode,
        "smoke": smoke,
        "modes": list(block["modes"]),
        "seeds": list(block["seeds"]),
        "git_commit": commit,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "occlusion_proxy_version": cfg["perturbation"].get("proxy_version", "v0.1"),
        "occlusion_proxy_type": cfg["perturbation"].get("proxy_type", "gain_scale_flag"),
        "target_shift_m": cfg["target_shift_m"],
        "replan_delay_steps": cfg["replan_delay_steps"],
        "blockers_waived": ["occlusion_proxy"],
        "blockers_deferred": ["reshape_skill", "handover_proxy"],
        "contract_doc": "experiments/surgical_intelligence/exp_surg_001_execute_or_defer/docs/study1d_occlusion_proxy_v0.1.md",
    }


def run_isaac(cfg: dict[str, Any], artifact_root: Path, smoke: bool) -> None:
    isaaclab = Path(cfg.get("isaaclab_path", "/workspace/IsaacLab/isaaclab.sh"))
    if not isaaclab.exists():
        raise SystemExit(f"Isaac not found at {isaaclab}; use --mock or RunPod")

    block = cfg["smoke"] if smoke else cfg.get("full", cfg["smoke"])
    out_dir = artifact_root / ("isaac_smoke" if smoke else "isaac_full")
    out_dir.mkdir(parents=True, exist_ok=True)

    level = int(block["occlusion_levels"][0])
    occ = occlusion_level_cfg(cfg, level)
    modes = ",".join(block["modes"])

    cmd = [
        str(isaaclab),
        "-p",
        str(ISAAC_SCRIPT),
        "--experiment-id",
        EXPERIMENT_ID,
        "--task",
        cfg.get("task", "Isaac-Reach-Dual-STAR-IK-Rel-Play-v0"),
        "--num_envs",
        "1",
        "--seeds",
        ",".join(str(s) for s in block["seeds"]),
        "--onset",
        str(cfg.get("onset", 20)),
        "--max-steps",
        str(cfg.get("max_steps", 160)),
        "--shift-m",
        str(cfg["target_shift_m"]),
        "--replan-delay",
        str(cfg["replan_delay_steps"]),
        "--occlusion-level",
        str(level),
        "--visibility-fraction",
        str(occ["visibility_fraction"]),
        "--reobserve-hold-steps",
        str(next(r["reobserve_hold_steps"] for r in cfg["responses"] if r["id"] == "REOBSERVE")),
        "--modes",
        modes,
        "--body-index",
        str(cfg.get("body_index", 13)),
        "--gain",
        str(cfg.get("gain", 1.0)),
        "--max-delta",
        str(cfg.get("max_delta", 0.08)),
        "--episode-length-s",
        str(cfg.get("episode_length_s", 20)),
        "--out-dir",
        str(out_dir),
        "--headless",
    ]
    print("[isaac]", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def load_isaac_records(artifact_root: Path, smoke: bool = True) -> list[dict[str, Any]]:
    subs = ("isaac_smoke", "isaac_full", ".") if smoke else ("isaac_full", "isaac_smoke", ".")
    for sub in subs:
        js = artifact_root / sub / "isaac_results.json" if sub != "." else artifact_root / "isaac_results.json"
        if js.exists():
            data = json.loads(js.read_text(encoding="utf-8"))
            return list(data.get("records", []))
    raise SystemExit(f"No isaac_results.json under {artifact_root} (smoke={smoke})")


def print_summary(records: list[dict[str, Any]], agg: list[dict[str, Any]]) -> None:
    print(f"\n=== {EXPERIMENT_ID} aggregate ===")
    print(f"{'response':<16} {'class':<22} {'n':>3} {'success':>8} {'viol':>8} {'dist_m':>10}")
    for r in agg:
        print(
            f"{r['response']:<16} {str(r.get('response_class','')):<22} {r['n']:>3} "
            f"{r['successful_resolution_rate']:>8.3f} {r['forbidden_violation_rate']:>8.3f} "
            f"{r['mean_final_distance_m']:>10.4f}"
        )
    ok = all(r.get("branch_replay_ok") for r in records)
    print(f"\nbranch_replay_ok: {ok} ({len(records)} records)")


def write_report(path: Path, records: list[dict[str, Any]], agg: list[dict[str, Any]], manifest: dict[str, Any]) -> None:
    phase = manifest.get("phase", "D0_smoke" if manifest.get("smoke") else "D1_full")
    phase_label = "D0 smoke (3-mode)" if manifest.get("smoke") else "D1 full (5-mode)"
    lines = [
        f"# {EXPERIMENT_ID} Report — Occlusion × multi-mode ({phase_label})",
        "",
        f"> **Phase:** `{phase}` · **Mode:** `{manifest['mode']}` · **Commit:** `{manifest['git_commit']}` · **Proxy:** gain_scale_flag v0.1",
        "",
        "## Design",
        "",
        f"- Shift: **{manifest['target_shift_m']} m** · REPLAN delay **{manifest['replan_delay_steps']}** steps",
        f"- Modes: {', '.join(str(m) for m in manifest.get('modes', []))} · seeds: {manifest.get('seeds', [])}",
        f"- Occlusion proxy: `{manifest['occlusion_proxy_type']}` · contract in docs/study1d_occlusion_proxy_v0.1.md",
        f"- Smoke atlas only — see experiments/.../docs/study1d_phase_gate.md",
        "",
        "## Aggregate",
        "",
        "| Response | Class | n | Success | Violation | Mean dist (m) |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for r in agg:
        lines.append(
            f"| {r['response']} | {r.get('response_class','')} | {r['n']} | "
            f"{r['successful_resolution_rate']:.3f} | {r['forbidden_violation_rate']:.3f} | "
            f"{r['mean_final_distance_m']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Per-branch",
            "",
        ]
    )
    for r in records:
        lines.append(
            f"- seed={r['seed']} {r['response']} success={r['successful_resolution']} "
            f"dist={r['final_distance_m']:.4f} cleared={r.get('visibility_cleared')}"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def analyze_and_write(
    records: list[dict[str, Any]],
    artifact_root: Path,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    agg = aggregate_by_mode(records)
    artifact_root.mkdir(parents=True, exist_ok=True)
    summary = {
        "experiment_id": EXPERIMENT_ID,
        "n_records": len(records),
        "aggregate_by_mode": agg,
        "manifest": manifest,
    }
    write_csv(artifact_root / "results_per_branch.csv", records)
    write_csv(artifact_root / "aggregate_by_mode.csv", agg)
    (artifact_root / "isaac_results.json").write_text(
        json.dumps({"experiment": EXPERIMENT_ID, "records": records, "manifest": manifest}, indent=2) + "\n",
        encoding="utf-8",
    )
    (artifact_root / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (artifact_root / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_report(EXP_ROOT / "study1d_report.md", records, agg, manifest)
    return summary


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="EXP-SURG-001D occlusion × multi-mode")
    p.add_argument("--config", type=Path, default=DEFAULT_CFG)
    p.add_argument("--artifact-root", type=Path, default=ARTIFACT_ROOT)
    p.add_argument("--mock", action="store_true", help="Kinematic mock (default)")
    p.add_argument("--isaac", action="store_true", help="Run Isaac runner")
    p.add_argument("--merge", action="store_true", help="Merge existing Isaac JSON")
    p.add_argument("--smoke", action="store_true", help="D0 smoke grid")
    p.add_argument("--full", action="store_true", help="D1 full grid")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_yaml(args.config)
    artifact_root = args.artifact_root
    smoke = bool(args.smoke or (not args.full and not args.merge))
    commit = git_commit()

    if args.merge:
        records = load_isaac_records(artifact_root, smoke=smoke)
        mode = "isaac_merge"
    elif args.isaac:
        run_isaac(cfg, artifact_root, smoke=smoke)
        records = load_isaac_records(artifact_root)
        mode = "isaac"
    else:
        mock_recs = run_mock_grid(cfg, smoke=smoke)
        records = records_to_dicts(mock_recs)
        mode = "mock"

    manifest = run_manifest(cfg, mode, smoke, commit)
    summary = analyze_and_write(records, artifact_root, manifest)
    print_summary(records, summary["aggregate_by_mode"])
    print(f"\nWrote artifacts under {artifact_root}")


if __name__ == "__main__":
    main()
