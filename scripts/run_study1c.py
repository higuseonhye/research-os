#!/usr/bin/env python3
"""EXP-SURG-001C — Severity × Delay counterfactual surface orchestration + analysis.

Modes:
  --mock     Kinematic mock (local smoke / pipeline validation).
  --isaac    Launch Isaac runner per severity (RunPod / GPU host).
  --merge    Re-analyze existing per-shift isaac_results.json files only.

Artifacts:
  experiments/.../artifacts/study1c_severity_delay_surface/
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[1]
EXP_ROOT = REPO / "experiments/surgical_intelligence/exp_surg_001_execute_or_defer"
DEFAULT_CFG = EXP_ROOT / "config/study1c_severity_delay_surface.yaml"
ARTIFACT_ROOT = EXP_ROOT / "artifacts/study1c_severity_delay_surface"
ISAAC_SCRIPT = REPO / "scripts/orbit_reach_study1a_counterfactual.py"
RUNPOD_SCRIPT = REPO / "scripts/run_study1c_severity_runpod.sh"

SUCCESS_THRESHOLD = 0.8
TOL_M = 0.02


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


@dataclass
class BranchRecord:
    seed: int
    episode: int
    response: str
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
    mode: str
    experiment_id: str = "EXP-SURG-001C"


def terminal_category(success: bool, violation: bool, timed_out: bool) -> str:
    if violation:
        return "unsafe_failure"
    if success:
        return "successful_resolution"
    if timed_out:
        return "timeout_failure"
    return "safe_unresolved"


def mock_branch(
    seed: int,
    shift_m: float,
    response: str,
    replan_delay: int | None,
    onset: int,
    max_steps: int,
    tol: float,
    step_size: float = 0.012,
) -> BranchRecord:
    """2D Y-axis reach mock: same-state replay implied; deterministic per seed."""
    rng = np.random.default_rng(seed * 1009 + int(round(shift_m * 10000)) * 17)
    ee_y = float(rng.uniform(-0.005, 0.005))
    target0_y = 0.10 + float(rng.uniform(-0.01, 0.01))
    frozen = target0_y
    shifted = target0_y + shift_m
    path = 0.0
    violation = False
    forbidden_y = target0_y + shift_m * 0.45

    for _ in range(onset):
        prev = ee_y
        ee_y += step_size * float(np.sign(target0_y - ee_y))
        if abs(target0_y - ee_y) < step_size:
            ee_y = target0_y
        path += abs(ee_y - prev)

    is_continue = response == "CONTINUE"
    delay = 0 if replan_delay is None else int(replan_delay)
    switch_step = onset if is_continue else onset + delay
    chase = frozen
    response_start = switch_step

    for t in range(onset, max_steps):
        if is_continue:
            chase = frozen
        elif t < switch_step:
            chase = frozen
        else:
            chase = shifted

        prev = ee_y
        ee_y += step_size * float(np.sign(chase - ee_y))
        if abs(chase - ee_y) < step_size:
            ee_y = chase
        path += abs(ee_y - prev)

        if not is_continue and shift_m > 0.015:
            if min(prev, ee_y) <= forbidden_y <= max(prev, ee_y) and t < switch_step:
                violation = True

        final_dist = abs(ee_y - shifted)
        if t + 1 >= max_steps:
            break

    remaining = max_steps - switch_step
    base_steps = shift_m / step_size
    delay_penalty = 0.04 * delay * (shift_m / 0.01)
    steps_needed = math.ceil(base_steps * (1.0 + delay_penalty)) + int(rng.integers(0, 3))
    timed_out = remaining < steps_needed
    final_dist = abs(ee_y - shifted)

    if is_continue:
        success = shift_m <= tol and final_dist <= tol and not violation
    else:
        success = (
            not timed_out
            and not violation
            and final_dist <= tol
            and remaining >= steps_needed
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
        replan_delay=replan_delay,
        shift_distance_m=shift_m,
        onset_step=onset,
        response_start_step=response_start,
        final_distance_m=final_dist if success else max(final_dist, shift_m * 0.5),
        path_length_m=path,
        completion_steps=completion,
        recovery_duration=max(0, completion - response_start),
        forbidden_violation=violation,
        successful_resolution=bool(success),
        terminal_category=terminal_category(bool(success), violation, timed_out),
        branch_replay_ok=True,
        mode="mock",
    )


def run_mock_grid(
    severities: list[float],
    delays: list[int],
    seeds: list[int],
    onset: int,
    max_steps: int,
) -> list[BranchRecord]:
    records: list[BranchRecord] = []
    for shift_m in severities:
        for seed in seeds:
            records.append(
                mock_branch(seed, shift_m, "CONTINUE", None, onset, max_steps, TOL_M)
            )
            for d in delays:
                records.append(
                    mock_branch(
                        seed,
                        shift_m,
                        f"REPLAN_d{d}",
                        d,
                        onset,
                        max_steps,
                        TOL_M,
                    )
                )
    return records


def resolve_shift_dir(artifact_root: Path, shift_m: float) -> Path | None:
    """Find per-shift Isaac output dir (RunPod uses isaac_shift_0.03, not 0.0300)."""
    shift = float(shift_m)
    name_variants = {
        f"isaac_shift_{shift}",
        f"isaac_shift_{shift:.4f}",
        f"isaac_shift_{shift:.3f}",
        f"isaac_shift_{shift:.2f}",
        f"study1c_severity_{shift}",
    }
    for name in name_variants:
        cand = artifact_root / name
        if (cand / "isaac_results.json").exists():
            return cand
    for d in sorted(artifact_root.glob("isaac_shift_*")):
        try:
            parsed = float(d.name.removeprefix("isaac_shift_"))
        except ValueError:
            continue
        if abs(parsed - shift) < 1e-9 and (d / "isaac_results.json").exists():
            return d
    return None


def load_isaac_records(artifact_root: Path, severities: list[float]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for shift_m in severities:
        cand = resolve_shift_dir(artifact_root, shift_m)
        if cand is None:
            continue
        data = json.loads((cand / "isaac_results.json").read_text(encoding="utf-8"))
        records.extend(data.get("records", []))
    if not records:
        # Fallback: ingest any isaac_shift_* with results (smoke/full mismatch)
        for js in sorted(artifact_root.glob("isaac_shift_*/isaac_results.json")):
            data = json.loads(js.read_text(encoding="utf-8"))
            records.extend(data.get("records", []))
    return records


def records_to_dicts(records: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for r in records:
        if isinstance(r, dict):
            out.append(r)
        else:
            out.append(asdict(r))
    return out


def aggregate_by_severity_delay(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[float, int | None, str], list[dict[str, Any]]] = {}
    for r in records:
        delay = r.get("replan_delay")
        if r["response"] == "CONTINUE":
            delay = None
        key = (float(r["shift_distance_m"]), delay, str(r["response"]))
        groups.setdefault(key, []).append(r)

    rows: list[dict[str, Any]] = []
    def sort_key(item: tuple[tuple[float, int | None, str], list]) -> tuple:
        (shift_m, delay, response), _ = item
        return (shift_m, -1 if delay is None else delay, response)

    for (shift_m, delay, response), xs in sorted(groups.items(), key=sort_key):
        n = len(xs)
        rows.append(
            {
                "shift_distance_m": shift_m,
                "shift_cm": round(shift_m * 100, 1),
                "replan_delay": delay,
                "response": response,
                "n": n,
                "successful_resolution_rate": sum(1 for x in xs if x.get("successful_resolution")) / n,
                "forbidden_violation_rate": sum(1 for x in xs if x.get("forbidden_violation")) / n,
                "mean_final_distance_m": float(np.mean([float(x["final_distance_m"]) for x in xs])),
                "mean_completion_steps": float(np.mean([float(x["completion_steps"]) for x in xs])),
                "mean_path_length_m": float(np.mean([float(x.get("path_length_m", 0)) for x in xs])),
                "mean_recovery_duration": float(np.mean([float(x.get("recovery_duration", 0)) for x in xs])),
            }
        )
    return rows


def replan_matrix(rows: list[dict[str, Any]]) -> dict[float, dict[int, float]]:
    mat: dict[float, dict[int, float]] = {}
    for r in rows:
        if r["response"] == "CONTINUE" or r["replan_delay"] is None:
            continue
        shift = float(r["shift_distance_m"])
        delay = int(r["replan_delay"])
        mat.setdefault(shift, {})[delay] = float(r["successful_resolution_rate"])
    return mat


def empirical_latest_viable_delay(
    matrix: dict[float, dict[int, float]],
    threshold: float = SUCCESS_THRESHOLD,
) -> dict[float, int | None]:
    """Max delay with success rate >= threshold (tested grid only; not universal golden time)."""
    out: dict[float, int | None] = {}
    for shift in sorted(matrix.keys()):
        viable: int | None = None
        for delay in sorted(matrix[shift].keys()):
            if matrix[shift][delay] >= threshold:
                viable = delay
        out[shift] = viable
    return out


def delay_sensitivity_slope(matrix: dict[float, dict[int, float]]) -> dict[float, float]:
    slopes: dict[float, float] = {}
    for shift, delays in matrix.items():
        if len(delays) < 2:
            slopes[shift] = 0.0
            continue
        xs = sorted(delays.keys())
        ys = [delays[d] for d in xs]
        if xs[-1] == xs[0]:
            slopes[shift] = 0.0
        else:
            slopes[shift] = (ys[-1] - ys[0]) / (xs[-1] - xs[0])
    return slopes


def interaction_observed(slopes: dict[float, float]) -> dict[str, Any]:
    if len(slopes) < 2:
        return {"observed": False, "detail": "insufficient severity levels"}
    ordered = sorted(slopes.items())
    severity_vals = [s for s, _ in ordered]
    slope_vals = [abs(v) for _, v in ordered]
    # More negative slope at higher severity => delay sensitivity increases
    increasing = all(
        slope_vals[i] <= slope_vals[i + 1] + 1e-9 for i in range(len(slope_vals) - 1)
    ) and slope_vals[-1] > slope_vals[0] + 0.01
    return {
        "observed": increasing,
        "slopes_by_severity_m": {str(k): v for k, v in slopes.items()},
        "interpretation": (
            "Delay sensitivity appears to increase with severity"
            if increasing
            else "No monotonic increase in delay sensitivity across tested severities"
        ),
    }


def flat_band_at_3cm(matrix: dict[float, dict[int, float]], ref_shift: float = 0.03) -> dict[str, Any]:
    if ref_shift not in matrix:
        return {"persists": None, "detail": "3 cm level not in matrix"}
    rates = list(matrix[ref_shift].values())
    if not rates:
        return {"persists": None, "detail": "no REPLAN rows at 3 cm"}
    spread = max(rates) - min(rates)
    persists = spread <= 0.05 and min(rates) >= 0.75
    return {
        "persists": persists,
        "rates_by_delay": matrix[ref_shift],
        "spread": spread,
        "detail": (
            "001B flat high-recoverability band persists at 3 cm within tested delays"
            if persists
            else "001B flat band breaks or narrows at 3 cm under expanded delay/severity grid"
        ),
    }


def recommend_001d_condition(
    matrix: dict[float, dict[int, float]],
    lvd: dict[float, int | None],
) -> dict[str, Any]:
    """Pick severity×delay at pre-cliff boundary when available."""
    if not matrix:
        return {"shift_m": 0.03, "shift_cm": 3, "replan_delay": 10, "rationale": "default mild shift"}

    max_delay = max(d for row in matrix.values() for d in row.keys())
    for shift in sorted(matrix.keys(), reverse=True):
        lv = lvd.get(shift)
        if lv is not None and lv < max_delay:
            return {
                "shift_m": shift,
                "shift_cm": round(shift * 100),
                "replan_delay": lv,
                "rationale": (
                    f"{shift*100:.0f} cm at empirical latest viable delay ({lv} steps) - "
                    "last high-recoverability point before drop in tested grid; "
                    "useful baseline for 001D occlusion interventions"
                ),
            }
    target_shift = 0.06
    target_delay = 20
    if target_shift in matrix and target_delay in matrix[target_shift]:
        return {
            "shift_m": target_shift,
            "shift_cm": 6,
            "replan_delay": target_delay,
            "rationale": "Flat recoverability surface; 6 cm / delay 20 as mid-grid baseline for 001D",
        }
    return {
        "shift_m": 0.03,
        "shift_cm": 3,
        "replan_delay": 10,
        "rationale": "Fallback to 001B-like mild shift if surface remains flat",
    }


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    keys = fieldnames or list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow(row)


def write_figures(
    out_dir: Path,
    records: list[dict[str, Any]],
    agg_rows: list[dict[str, Any]],
    matrix: dict[float, dict[int, float]],
    lvd: dict[float, int | None],
) -> list[str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []

    if matrix:
        shifts = sorted(matrix.keys())
        delays = sorted({d for row in matrix.values() for d in row.keys()})
        grid = np.full((len(shifts), len(delays)), np.nan)
        for i, s in enumerate(shifts):
            for j, d in enumerate(delays):
                if d in matrix[s]:
                    grid[i, j] = matrix[s][d]

        fig, ax = plt.subplots(figsize=(8, 4))
        im = ax.imshow(grid, aspect="auto", cmap="YlGn", vmin=0, vmax=1)
        ax.set_xticks(range(len(delays)), [str(d) for d in delays])
        ax.set_yticks(range(len(shifts)), [f"{s*100:.0f} cm" for s in shifts])
        ax.set_xlabel("Replan delay (steps after onset)")
        ax.set_ylabel("Target shift severity")
        ax.set_title("REPLAN successful resolution rate (severity × delay)")
        for i in range(len(shifts)):
            for j in range(len(delays)):
                if not math.isnan(grid[i, j]):
                    ax.text(j, i, f"{grid[i, j]:.2f}", ha="center", va="center", fontsize=8)
        fig.colorbar(im, ax=ax, label="Success rate")
        fig.tight_layout()
        p = out_dir / "success_rate_heatmap.png"
        fig.savefig(p, dpi=160, bbox_inches="tight")
        plt.close(fig)
        written.append(str(p))

        fig, ax = plt.subplots(figsize=(7, 4))
        for s in shifts:
            xs = sorted(matrix[s].keys())
            ys = [matrix[s][d] for d in xs]
            ax.plot(xs, ys, "o-", label=f"{s*100:.0f} cm")
        ax.axhline(SUCCESS_THRESHOLD, color="gray", ls=":", label=f"threshold {SUCCESS_THRESHOLD}")
        ax.set_xlabel("Replan delay (steps)")
        ax.set_ylabel("Successful resolution rate")
        ax.set_title("Severity-specific delay curves")
        ax.set_ylim(-0.05, 1.05)
        ax.legend(fontsize=8)
        fig.tight_layout()
        p = out_dir / "severity_delay_curves.png"
        fig.savefig(p, dpi=160, bbox_inches="tight")
        plt.close(fig)
        written.append(str(p))

        fig, ax = plt.subplots(figsize=(6, 3.5))
        xs = [s * 100 for s in shifts]
        ys = [lvd[s] if lvd[s] is not None else -5 for s in shifts]
        colors = ["#2f6f4e" if v is not None and v >= 0 else "#b85c38" for v in ys]
        bars = ax.bar([f"{x:.0f} cm" for x in xs], [max(0, y) for y in ys], color=colors)
        ax.axhline(0, color="k", lw=0.5)
        ax.set_ylabel("Empirical latest viable delay (steps)")
        ax.set_title(
            f"Latest delay with success ≥ {SUCCESS_THRESHOLD}\n"
            "(tested condition; not a universal golden time)"
        )
        for bar, shift in zip(bars, shifts):
            val = lvd[shift]
            label = str(val) if val is not None else "none"
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, label, ha="center", fontsize=8)
        fig.tight_layout()
        p = out_dir / "latest_viable_delay.png"
        fig.savefig(p, dpi=160, bbox_inches="tight")
        plt.close(fig)
        written.append(str(p))

    cats: dict[str, int] = {}
    for r in records:
        cats[r["terminal_category"]] = cats.get(r["terminal_category"], 0) + 1
    if cats:
        fig, ax = plt.subplots(figsize=(5, 3.5))
        labels = list(cats.keys())
        vals = [cats[k] for k in labels]
        ax.bar(labels, vals, color="#4a6fa5")
        ax.set_ylabel("Count")
        ax.set_title("Terminal outcome distribution")
        plt.xticks(rotation=20, ha="right")
        fig.tight_layout()
        p = out_dir / "terminal_outcome_distribution.png"
        fig.savefig(p, dpi=160, bbox_inches="tight")
        plt.close(fig)
        written.append(str(p))

    # Same-state comparison grid: one severity, seeds collapsed — REPLAN delays
    if agg_rows:
        ref = 0.03 if any(r["shift_distance_m"] == 0.03 for r in agg_rows) else agg_rows[0]["shift_distance_m"]
        subset = [
            r
            for r in agg_rows
            if r["shift_distance_m"] == ref and r["response"].startswith("REPLAN")
        ]
        subset = sorted(subset, key=lambda r: int(r["replan_delay"] or 0))
        if subset:
            fig, axes = plt.subplots(1, min(4, len(subset)), figsize=(10, 2.8))
            if not isinstance(axes, np.ndarray):
                axes = [axes]
            for ax, row in zip(axes, subset[: len(axes)]):
                ax.bar(["success", "violation"], [row["successful_resolution_rate"], row["forbidden_violation_rate"]])
                ax.set_ylim(0, 1.05)
                ax.set_title(f"d={row['replan_delay']} @ {ref*100:.0f}cm")
            fig.suptitle("Same-state branch comparison (REPLAN delays)", fontsize=10)
            fig.tight_layout()
            p = out_dir / "same_state_comparison_grid.png"
            fig.savefig(p, dpi=160, bbox_inches="tight")
            plt.close(fig)
            written.append(str(p))

    return written


def write_representative_videos(out_dir: Path, records: list[dict[str, Any]]) -> list[str]:
    """Placeholder clips / stub notes when Isaac video capture unavailable."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []

    cases = [
        ("mild_shift_late_replan", 0.03, 40, "REPLAN_d40"),
        ("severe_shift_immediate_replan", 0.09, 0, "REPLAN_d0"),
        ("severe_shift_late_replan", 0.09, 40, "REPLAN_d40"),
    ]
    for tag, shift, delay, resp in cases:
        match = next(
            (
                r
                for r in records
                if abs(float(r["shift_distance_m"]) - shift) < 1e-6
                and r["response"] == resp
                and (r.get("replan_delay") == delay or str(r.get("replan_delay")) == str(delay))
            ),
            None,
        )
        fig, ax = plt.subplots(figsize=(4, 2.5))
        ax.axis("off")
        title = f"{tag}\nshift={shift*100:.0f}cm delay={delay}"
        if match:
            title += (
                f"\nterminal={match['terminal_category']} "
                f"dist={float(match['final_distance_m']):.4f}m"
            )
        ax.text(0.5, 0.5, title + "\n(video stub — Isaac capture on RunPod)", ha="center", va="center")
        p = out_dir / f"{tag}.png"
        fig.savefig(p, dpi=120, bbox_inches="tight")
        plt.close(fig)
        written.append(str(p))
    return written


def write_report(
    path: Path,
    records: list[dict[str, Any]],
    agg_rows: list[dict[str, Any]],
    summary: dict[str, Any],
    manifest: dict[str, Any],
) -> None:
    flat = summary.get("flat_band_3cm", {})
    interaction = summary.get("interaction", {})
    lvd = summary.get("empirical_latest_viable_delay", {})
    rec001d = summary.get("recommend_001d", {})

    lines = [
        "# EXP-SURG-001C Report — Severity × Delay Surface",
        "",
        f"> **Status:** {manifest.get('run_phase', 'completed')} · **Mode:** {manifest.get('mode')} · "
        f"**Commit:** `{manifest.get('git_commit', 'unknown')[:12]}`",
        "",
        (
            "> **Note:** Results below are from **mock** kinematic pipeline validation unless "
            "`mode=isaac`. Re-run on RunPod via `bash scripts/run_study1c_severity_runpod.sh` for Isaac data."
            if manifest.get("mode") == "mock"
            else ""
        ),
        "",
        "## Core question",
        "",
        "How do mismatch severity and intervention delay jointly affect successful resolution under replanning?",
        "",
        "## Design",
        "",
        f"- Severities (m): {manifest.get('severities')}",
        f"- Delays: {manifest.get('delays')}",
        f"- Seeds: {manifest.get('seeds')}",
        "- CONTINUE: once per severity × seed; REPLAN: each severity × delay × seed",
        "- Same-state branch replay to fixed onset (20 steps)",
        "",
        "## Observed results",
        "",
        f"- Branch records: **{len(records)}** (all branch_replay_ok={all(r.get('branch_replay_ok') for r in records)})",
        "",
        "### Aggregate REPLAN success (severity × delay)",
        "",
        "| shift (cm) | delay | n | success rate | mean final dist (m) | violation rate |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in agg_rows:
        if r["response"] != "CONTINUE" and r["replan_delay"] is not None:
            lines.append(
                f"| {r['shift_cm']} | {r['replan_delay']} | {r['n']} | "
                f"{r['successful_resolution_rate']:.3f} | {r['mean_final_distance_m']:.4f} | "
                f"{r['forbidden_violation_rate']:.3f} |"
            )

    lines.extend(
        [
            "",
            "### Empirical latest viable delay (success ≥ 0.8, tested grid)",
            "",
            "| shift (cm) | latest viable delay (steps) |",
            "| --- | --- |",
        ]
    )
    for shift_m, delay in sorted(lvd.items(), key=lambda x: float(x[0])):
        cm = float(shift_m) * 100
        lines.append(f"| {cm:.0f} | {delay if delay is not None else 'none in grid'} |")

    lines.extend(
        [
            "",
            "### 3 cm flat band (vs 001B)",
            "",
            f"- **Finding:** {flat.get('detail', 'n/a')}",
            "",
            "## Interpretations (not claims)",
            "",
            f"- {interaction.get('interpretation', 'n/a')}",
            "- Severity × delay interaction is **empirical under scripted IK-Rel**; not transferred to clinical settings.",
            "",
            "## Unsupported claims",
            "",
            "- Universal \"golden time\" for replanning",
            "- Clinical safety or human OR performance",
            "- Policy optimality of scripted controller",
            "",
            "## Simulator / controller limitations",
            "",
            "- ORBIT Reach PLAY task; 6D IK-Rel proposer (not learned policy)",
            "- Forbidden region is axis-aligned proxy box",
            "- Single env; no contact-rich tissue model",
            "- Video stubs unless Isaac GUI capture enabled on RunPod",
            "",
            "## Run manifest",
            "",
            f"- Command: `{manifest.get('command')}`",
            f"- Timestamp UTC: {manifest.get('timestamp_utc')}",
            f"- Artifact root: `{manifest.get('artifact_root')}`",
            "",
            "## Recommendation for EXP-SURG-001D",
            "",
            f"- **Condition:** shift={rec001d.get('shift_cm')} cm, replan delay={rec001d.get('replan_delay')} steps",
            f"- **Rationale:** {rec001d.get('rationale')}",
            "",
            "## Artifacts",
            "",
            "- `results_per_branch.csv`",
            "- `aggregate_by_severity_delay.csv`",
            "- `summary.json`",
            "- `figures/` — heatmap, delay curves, LVD, terminal distribution, comparison grid",
            "- `videos/` — representative case stubs",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def analyze_and_write(
    records: list[dict[str, Any]],
    artifact_root: Path,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    agg_rows = aggregate_by_severity_delay(records)
    matrix = replan_matrix(agg_rows)
    lvd = empirical_latest_viable_delay(matrix)
    slopes = delay_sensitivity_slope(matrix)
    interaction = interaction_observed(slopes)
    flat = flat_band_at_3cm(matrix)
    rec001d = recommend_001d_condition(matrix, lvd)

    summary = {
        "experiment_id": "EXP-SURG-001C",
        "n_records": len(records),
        "success_threshold_lvd": SUCCESS_THRESHOLD,
        "empirical_latest_viable_delay": {str(k): v for k, v in lvd.items()},
        "flat_band_3cm": flat,
        "interaction": interaction,
        "recommend_001d": rec001d,
        "replan_success_matrix": {str(k): v for k, v in matrix.items()},
        "manifest": manifest,
    }

    artifact_root.mkdir(parents=True, exist_ok=True)
    write_csv(artifact_root / "results_per_branch.csv", records)
    write_csv(artifact_root / "aggregate_by_severity_delay.csv", agg_rows)
    (artifact_root / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (artifact_root / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    figs = write_figures(artifact_root / "figures", records, agg_rows, matrix, lvd)
    vids = write_representative_videos(artifact_root / "videos", records)
    summary["figures"] = figs
    summary["videos"] = vids
    (artifact_root / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    write_report(EXP_ROOT / "study1c_report.md", records, agg_rows, summary, manifest)
    return summary


def print_final_summary(summary: dict[str, Any], agg_rows: list[dict[str, Any]]) -> None:
    print("\n=== EXP-SURG-001C aggregate (REPLAN) ===")
    print(f"{'shift_cm':>8} {'delay':>6} {'n':>4} {'success':>8} {'viol':>8} {'dist_m':>10}")
    for r in agg_rows:
        if r["response"].startswith("REPLAN"):
            print(
                f"{r['shift_cm']:>8.1f} {int(r['replan_delay']):>6} {r['n']:>4} "
                f"{r['successful_resolution_rate']:>8.3f} {r['forbidden_violation_rate']:>8.3f} "
                f"{r['mean_final_distance_m']:>10.4f}"
            )

    lvd = summary.get("empirical_latest_viable_delay", {})
    print("\n=== Empirical latest viable delay (>= 0.8, tested condition) ===")
    for shift, delay in sorted(lvd.items(), key=lambda x: float(x[0])):
        print(f"  {float(shift)*100:.0f} cm -> {delay if delay is not None else 'none'}")

    inter = summary.get("interaction", {})
    print(f"\n=== Severity × delay interaction ===\n  {inter.get('interpretation')}")

    rec = summary.get("recommend_001d", {})
    print(
        f"\n=== EXP-SURG-001D recommended condition ===\n"
        f"  shift={rec.get('shift_cm')} cm, delay={rec.get('replan_delay')} - {rec.get('rationale')}"
    )


def run_isaac_severity(
    shift_m: float,
    delays: list[int],
    seeds: list[int],
    out_dir: Path,
    cfg: dict[str, Any],
) -> None:
    isaaclab = Path(cfg.get("isaaclab_path", "/workspace/IsaacLab/isaaclab.sh"))
    if not isaaclab.exists():
        raise SystemExit(f"Isaac not found at {isaaclab}; use --mock or RunPod")

    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(isaaclab),
        "-p",
        str(ISAAC_SCRIPT),
        "--experiment-id",
        "EXP-SURG-001C",
        "--task",
        cfg.get("task", "Isaac-Reach-Dual-STAR-IK-Rel-Play-v0"),
        "--num_envs",
        "1",
        "--seeds",
        ",".join(str(s) for s in seeds),
        "--onset",
        str(cfg.get("onset", 20)),
        "--max-steps",
        str(cfg.get("max_steps", 160)),
        "--shift-m",
        str(shift_m),
        "--body-index",
        str(cfg.get("body_index", 13)),
        "--gain",
        str(cfg.get("gain", 1.0)),
        "--max-delta",
        str(cfg.get("max_delta", 0.08)),
        "--episode-length-s",
        str(cfg.get("episode_length_s", 20)),
        "--include-continue",
        "--replan-delays",
        ",".join(str(d) for d in delays),
        "--out-dir",
        str(out_dir),
        "--headless",
    ]
    print("[isaac]", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="EXP-SURG-001C severity × delay surface")
    p.add_argument("--config", type=Path, default=DEFAULT_CFG)
    p.add_argument("--artifact-root", type=Path, default=ARTIFACT_ROOT)
    p.add_argument("--mock", action="store_true", help="Kinematic mock (default if no --isaac)")
    p.add_argument("--isaac", action="store_true", help="Run Isaac per severity")
    p.add_argument("--merge", action="store_true", help="Merge existing Isaac JSON only")
    p.add_argument("--smoke", action="store_true", help="Reduced grid smoke test")
    p.add_argument("--full", action="store_true", help="Full grid (default after smoke)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_yaml(args.config)
    artifact_root = args.artifact_root

    if args.smoke:
        severities = cfg.get("smoke_severities_m", [0.03, 0.06, 0.09])
        delays = cfg.get("smoke_delays", [0, 10, 20, 40])
        seeds = cfg.get("smoke_seeds", [0, 1, 2])
        phase = "smoke"
    else:
        severities = cfg.get("severities_m", [0.01, 0.03, 0.06, 0.09])
        delays = cfg.get("replan_delays", [0, 5, 10, 20, 40, 60])
        seeds = cfg.get("seeds", [0, 1, 2, 3, 4])
        phase = "full"

    onset = int(cfg.get("onset", 20))
    max_steps = int(cfg.get("max_steps", 160))
    mode = "merge" if args.merge else ("isaac" if args.isaac else "mock")

    manifest = {
        "experiment_id": "EXP-SURG-001C",
        "mode": mode,
        "run_phase": phase,
        "severities": severities,
        "delays": delays,
        "seeds": seeds,
        "git_commit": git_commit(),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "artifact_root": str(artifact_root),
        "gpu": cfg.get("gpu", "local-or-runpod"),
        "environment": cfg.get("environment", "ORBIT Reach / Isaac Sim 4.1"),
        "command": " ".join(sys.argv),
    }

    records: list[dict[str, Any]] = []

    if mode == "mock":
        raw = run_mock_grid(severities, delays, seeds, onset, max_steps)
        records = records_to_dicts(raw)
    elif mode == "isaac":
        for shift_m in severities:
            out = artifact_root / f"isaac_shift_{shift_m:.4f}"
            run_isaac_severity(shift_m, delays, seeds, out, cfg)
        records = load_isaac_records(artifact_root, severities)
    else:
        records = load_isaac_records(artifact_root, severities)
        if not records:
            raise SystemExit(f"No Isaac results under {artifact_root}; run with --isaac first")

    if not all(r.get("branch_replay_ok", True) for r in records):
        raise SystemExit("branch_replay_ok failed for some records")

    summary = analyze_and_write(records, artifact_root, manifest)
    agg_rows = aggregate_by_severity_delay(records)
    print_final_summary(summary, agg_rows)
    print(f"\nArtifacts: {artifact_root}")


if __name__ == "__main__":
    main()
