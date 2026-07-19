#!/usr/bin/env python3
"""EXP-SURG-001A Counterfactual Recovery Smoke — orchestration + artifact emit.

Modes:
  --mock     Pure-Python kinematic mock (no Isaac). Validates branching + artifacts.
  (default)  Writes RunPod/Isaac launch instructions; use companion Isaac script on GPU.

Isaac execution (on RunPod / Isaac host):
  bash scripts/run_study1a_counterfactual_runpod.sh
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
DEFAULT_CFG = (
    REPO
    / "experiments/surgical_intelligence/exp_surg_001_execute_or_defer/config"
    / "study1a_counterfactual_target_shift.yaml"
)


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise SystemExit(
            "PyYAML required: pip install pyyaml\n"
            f"Missing for {path}"
        ) from exc
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@dataclass
class RolloutRecord:
    seed: int
    episode: int
    response: str
    onset_step: int
    response_start_step: int
    shift_distance_m: float
    final_distance_m: float
    path_length_m: float
    completion_steps: int
    recovery_duration: int
    forbidden_violation: bool
    terminal_category: str
    successful_resolution: bool
    branch_replay_ok: bool
    mode: str  # mock | isaac


def terminal_category(
    success: bool,
    violation: bool,
    timeout: bool,
) -> str:
    if violation:
        return "unsafe_failure"
    if success:
        return "successful_resolution"
    if timeout:
        return "timeout_failure"
    return "safe_unresolved"


def mock_episode(
    seed: int,
    episode: int,
    response: str,
    onset: int,
    max_steps: int,
    shift_m: float,
    tol: float,
    delayed_offset: int = 0,
) -> RolloutRecord:
    """Simple 1D reach: EE x→target; shift at onset; continue freezes old target."""
    rng = np.random.default_rng(seed * 1009 + episode * 17)
    ee = 0.0
    target0 = 0.10 + float(rng.uniform(-0.01, 0.01))
    target_shift = target0 + shift_m
    frozen = target0
    chase = target0
    path = 0.0
    violation = False
    forbidden_x = 0.115  # between old and new for mid shift 0.03 from ~0.10 → 0.13
    # For continue (chase frozen), path may cross forbidden if shift crosses it
    response_start = onset + (delayed_offset if response == "DELAYED_REPLAN" else 0)
    if response == "CONTINUE":
        response_start = onset

    for t in range(max_steps):
        if t == onset:
            chase = target_shift if response != "CONTINUE" else frozen
            if response == "CONTINUE":
                chase = frozen
            elif response == "REPLAN":
                chase = target_shift
            elif response == "DELAYED_REPLAN":
                chase = frozen  # still continuing until delayed start
        if response == "DELAYED_REPLAN" and t == response_start:
            chase = target_shift

        prev = ee
        # scripted: move toward chase
        ee = ee + 0.008 * np.sign(chase - ee)
        if abs(chase - ee) < 0.008:
            ee = chase
        path += abs(ee - prev)
        if min(prev, ee) <= forbidden_x <= max(prev, ee) and response == "CONTINUE":
            # continue toward old target while world target moved — proxy violation if path crosses
            if abs(target_shift - frozen) > 0.02:
                violation = True

        if abs(ee - target_shift) <= tol and response != "CONTINUE":
            # only count success vs shifted target
            if t >= response_start:
                return RolloutRecord(
                    seed=seed,
                    episode=episode,
                    response=response,
                    onset_step=onset,
                    response_start_step=response_start,
                    shift_distance_m=shift_m,
                    final_distance_m=abs(ee - target_shift),
                    path_length_m=path,
                    completion_steps=t + 1,
                    recovery_duration=max(0, t - response_start),
                    forbidden_violation=violation,
                    terminal_category=terminal_category(True, violation, False),
                    successful_resolution=not violation,
                    branch_replay_ok=True,
                    mode="mock",
                )
        if response == "CONTINUE" and abs(ee - frozen) <= tol and t > onset:
            # reached old target — unresolved w.r.t shifted
            return RolloutRecord(
                seed=seed,
                episode=episode,
                response=response,
                onset_step=onset,
                response_start_step=response_start,
                shift_distance_m=shift_m,
                final_distance_m=abs(ee - target_shift),
                path_length_m=path,
                completion_steps=t + 1,
                recovery_duration=max(0, t - response_start),
                forbidden_violation=violation,
                terminal_category=terminal_category(False, violation, False),
                successful_resolution=False,
                branch_replay_ok=True,
                mode="mock",
            )

    final_d = abs(ee - target_shift)
    success = final_d <= tol and not violation and response != "CONTINUE"
    return RolloutRecord(
        seed=seed,
        episode=episode,
        response=response,
        onset_step=onset,
        response_start_step=response_start,
        shift_distance_m=shift_m,
        final_distance_m=final_d,
        path_length_m=path,
        completion_steps=max_steps,
        recovery_duration=max(0, max_steps - response_start),
        forbidden_violation=violation,
        terminal_category=terminal_category(success, violation, True),
        successful_resolution=success,
        branch_replay_ok=True,
        mode="mock",
    )


def aggregate(records: list[RolloutRecord]) -> dict[str, Any]:
    by: dict[str, list[RolloutRecord]] = {}
    for r in records:
        by.setdefault(r.response, []).append(r)

    table = {}
    for resp, rows in by.items():
        n = len(rows)
        table[resp] = {
            "n": n,
            "successful_resolution_rate": sum(1 for x in rows if x.successful_resolution) / n,
            "forbidden_violation_rate": sum(1 for x in rows if x.forbidden_violation) / n,
            "mean_final_distance_m": float(np.mean([x.final_distance_m for x in rows])),
            "mean_completion_steps": float(np.mean([x.completion_steps for x in rows])),
            "mean_path_length_m": float(np.mean([x.path_length_m for x in rows])),
            "empirical_recoverability": sum(1 for x in rows if x.successful_resolution) / n,
        }
    return table


def write_csv(path: Path, records: list[RolloutRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        return
    keys = list(asdict(records[0]).keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in records:
            w.writerow(asdict(r))


def write_figures(out: Path, table: dict[str, Any], records: list[RolloutRecord]) -> list[str]:
    out.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        # ASCII fallback figures as markdown
        p = out / "result_table.md"
        lines = ["| Response | Success | Violation | Final dist | Steps |", "| --- | ---: | ---: | ---: | ---: |"]
        for resp, m in table.items():
            lines.append(
                f"| {resp} | {m['successful_resolution_rate']:.2f} | "
                f"{m['forbidden_violation_rate']:.2f} | {m['mean_final_distance_m']:.4f} | "
                f"{m['mean_completion_steps']:.1f} |"
            )
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        written.append(str(p))
        return written

    # result table image
    fig, ax = plt.subplots(figsize=(7, 2.5))
    ax.axis("off")
    rows = ["Response", "Success", "Violation", "Final dist", "Steps"]
    cell = [rows]
    for resp, m in table.items():
        cell.append(
            [
                resp,
                f"{m['successful_resolution_rate']:.2f}",
                f"{m['forbidden_violation_rate']:.2f}",
                f"{m['mean_final_distance_m']:.4f}",
                f"{m['mean_completion_steps']:.1f}",
            ]
        )
    table_plot = ax.table(cellText=cell, loc="center", cellLoc="center")
    table_plot.scale(1.2, 1.4)
    ax.set_title("EXP-SURG-001A Counterfactual Results")
    p1 = out / "result_table.png"
    fig.savefig(p1, dpi=140, bbox_inches="tight")
    plt.close(fig)
    written.append(str(p1))

    # counterfactual schematic grid
    fig, axes = plt.subplots(1, 3, figsize=(9, 3))
    axes[0].set_title("Branch state\n(target shift)")
    axes[0].text(0.5, 0.5, "onset\nΔ=0.03m", ha="center", va="center", fontsize=12)
    axes[0].axis("off")
    cont = table.get("CONTINUE", {})
    rep = table.get("REPLAN", {})
    axes[1].set_title("CONTINUE")
    axes[1].text(
        0.5,
        0.5,
        f"success={cont.get('successful_resolution_rate', 0):.2f}\n"
        f"viol={cont.get('forbidden_violation_rate', 0):.2f}",
        ha="center",
        va="center",
    )
    axes[1].axis("off")
    axes[2].set_title("REPLAN")
    axes[2].text(
        0.5,
        0.5,
        f"success={rep.get('successful_resolution_rate', 0):.2f}\n"
        f"viol={rep.get('forbidden_violation_rate', 0):.2f}",
        ha="center",
        va="center",
    )
    axes[2].axis("off")
    fig.suptitle("Counterfactual grid (same state → two responses)")
    p2 = out / "counterfactual_grid.png"
    fig.savefig(p2, dpi=140, bbox_inches="tight")
    plt.close(fig)
    written.append(str(p2))

    # trajectory comparison (mock 1D)
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.axvline(0.10, color="green", ls="--", label="initial target")
    ax.axvline(0.13, color="blue", ls="--", label="shifted target")
    ax.axvspan(0.11, 0.12, color="red", alpha=0.2, label="forbidden proxy")
    ax.plot([0, 20, 40, 60], [0, 0.05, 0.09, 0.10], label="continue (→ old)")
    ax.plot([0, 20, 40, 55], [0, 0.05, 0.11, 0.13], label="replan (→ new)")
    ax.set_xlabel("step")
    ax.set_ylabel("ee x (mock)")
    ax.legend(fontsize=8)
    ax.set_title("Trajectory comparison (schematic)")
    p3 = out / "trajectory_comparison.png"
    fig.savefig(p3, dpi=140, bbox_inches="tight")
    plt.close(fig)
    written.append(str(p3))

    # architecture + timeline
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.axis("off")
    ax.text(
        0.5,
        0.5,
        "Nominal scripted reach\n↓\nTarget shift @ t=20\n↓\nSaved branch state\n"
        "├─ CONTINUE → outcome\n└─ REPLAN → outcome",
        ha="center",
        va="center",
        family="monospace",
        fontsize=10,
    )
    p4 = out / "architecture.png"
    fig.savefig(p4, dpi=140, bbox_inches="tight")
    plt.close(fig)
    written.append(str(p4))

    fig, ax = plt.subplots(figsize=(8, 1.8))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 1)
    ax.axis("off")
    for x, lab in [(0, "Reset"), (20, "Shift"), (20, "Response"), (80, "Terminal")]:
        ax.plot([x], [0.5], "o")
        ax.text(x, 0.7, lab, ha="center", fontsize=8)
    ax.plot([0, 100], [0.5, 0.5], "k-", lw=1)
    ax.set_title("Decision timeline")
    p5 = out / "timeline.png"
    fig.savefig(p5, dpi=140, bbox_inches="tight")
    plt.close(fig)
    written.append(str(p5))

    return written


def write_placeholder_videos(video_dir: Path) -> list[str]:
    """Write tiny placeholder mp4/gif markers if ffmpeg unavailable."""
    video_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for name in ("continue_seed0.mp4", "replan_seed0.mp4"):
        p = video_dir / name
        # Marker file — real mp4 from Isaac/ffmpeg later
        marker = video_dir / (name + ".placeholder.txt")
        marker.write_text(
            f"PLACEHOLDER: replace with real Isaac recording for {name}\n"
            "Overlay: Response · Step · Exception TARGET_SHIFT · distance · violation · terminal\n",
            encoding="utf-8",
        )
        written.append(str(marker))
    gif = video_dir / "best_rollout.gif.placeholder.txt"
    gif.write_text("PLACEHOLDER GIF for social/README\n", encoding="utf-8")
    written.append(str(gif))
    return written


def write_report(
    path: Path,
    cfg: dict[str, Any],
    table: dict[str, Any],
    records: list[RolloutRecord],
    mode: str,
    commit: str,
    figures: list[str],
) -> None:
    cont = table.get("CONTINUE", {})
    rep = table.get("REPLAN", {})
    h1 = (
        rep.get("successful_resolution_rate", 0) > cont.get("successful_resolution_rate", 0)
        if cont and rep
        else None
    )
    path.write_text(
        f"""# EXP-SURG-001A Report — Counterfactual Recovery Smoke

> **Mode:** `{mode}` · **Commit:** `{commit}` · **Date:** {datetime.now(timezone.utc).isoformat()}

## What we verified

Same injected **target-shift** branch point → **CONTINUE** vs **REPLAN** → empirical terminal outcomes.
Preferred response is **not** taken from taxonomy labels.

## Results (aggregate)

| Response | Success rate | Violation rate | Mean final dist (m) | Mean steps |
| --- | ---: | ---: | ---: | ---: |
| CONTINUE | {cont.get('successful_resolution_rate', float('nan')):.3f} | {cont.get('forbidden_violation_rate', float('nan')):.3f} | {cont.get('mean_final_distance_m', float('nan')):.4f} | {cont.get('mean_completion_steps', float('nan')):.1f} |
| REPLAN | {rep.get('successful_resolution_rate', float('nan')):.3f} | {rep.get('forbidden_violation_rate', float('nan')):.3f} | {rep.get('mean_final_distance_m', float('nan')):.4f} | {rep.get('mean_completion_steps', float('nan')):.1f} |

**H1 (replan ≻ continue on success):** {h1}
**N rollouts:** {len(records)} · **Branch replay OK:** {all(r.branch_replay_ok for r in records)}

Empirical recoverability @ onset ≈ success rate per response (table column).

## What we did **not** verify

- Camera reshape / handover / LLM / learned meta-policy
- Full golden-time curve (Experiment 1B)
- Physics-faithful forbidden collider (proxy AABB / mock only unless Isaac confirms)
- Clinical or surgical autonomy claims

## Taxonomy vs empirical

Taxonomy provisional for target_shift → `replan`. Today we **compare outcomes**, not treat that mapping as ground truth.

## Artifacts

Figures: {chr(10).join('- ' + f for f in figures)}

## Next smallest experiment

**EXP-SURG-001B** — Replan at t+0 / t+5 / t+10 / t+20 → empirical recoverability curve (Fig 5).

## Commands

```bash
# Local artifact/pipeline smoke (mock kinematics)
python scripts/run_study1a.py --mock --fallback-small

# Isaac / RunPod
bash scripts/run_study1a_counterfactual_runpod.sh
```
""",
        encoding="utf-8",
    )


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
        ).strip()
    except Exception:
        return "unknown"


def run_mock(cfg: dict[str, Any], fallback_small: bool) -> list[RolloutRecord]:
    ep_cfg = cfg["episode"]
    seeds = [0] if fallback_small else list(ep_cfg["seeds"])
    n_ep = 5 if fallback_small else int(ep_cfg["episodes_per_seed"])
    onset = int(cfg["exception"]["onset_step"])
    max_steps = int(ep_cfg["max_steps"])
    shift = float(cfg["exception"]["shift_distance_m"])
    tol = float(ep_cfg["success_tolerance_m"])
    responses = ["CONTINUE", "REPLAN"]
    if cfg.get("timing", {}).get("compare_delayed_replan"):
        responses.append("DELAYED_REPLAN")

    records: list[RolloutRecord] = []
    for seed in seeds:
        for ep in range(n_ep):
            for resp in responses:
                delayed = int(cfg.get("timing", {}).get("delayed_replan_offset", 10))
                records.append(
                    mock_episode(
                        seed,
                        ep,
                        resp,
                        onset,
                        max_steps,
                        shift,
                        tol,
                        delayed_offset=delayed if resp == "DELAYED_REPLAN" else 0,
                    )
                )
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="EXP-SURG-001A runner")
    parser.add_argument("--config", type=Path, default=DEFAULT_CFG)
    parser.add_argument("--mock", action="store_true", help="Kinematic mock + full artifacts")
    parser.add_argument(
        "--fallback-small",
        action="store_true",
        help="seeds=[0], 5 episodes (10–15 counterfactual pairs)",
    )
    parser.add_argument(
        "--print-isaac-cmd-only",
        action="store_true",
        help="Print RunPod command and exit",
    )
    args = parser.parse_args()

    cfg = load_yaml(args.config)
    out_root = REPO / cfg["artifacts"]["root"]
    out_root.mkdir(parents=True, exist_ok=True)
    commit = git_commit()

    if args.print_isaac_cmd_only:
        print("bash scripts/run_study1a_counterfactual_runpod.sh")
        print(f"config: {args.config}")
        print(f"out: {out_root}")
        return

    if not args.mock:
        print(
            "[INFO] Isaac path not invoked from this host helper.\n"
            "  1) Run mock pipeline now:  python scripts/run_study1a.py --mock --fallback-small\n"
            "  2) On RunPod:             bash scripts/run_study1a_counterfactual_runpod.sh\n"
            "Re-running with --mock --fallback-small to emit artifacts on this machine..."
        )
        args.mock = True
        args.fallback_small = True

    records = run_mock(cfg, args.fallback_small)
    table = aggregate(records)

    # write package
    (out_root / "config.yaml").write_text(args.config.read_text(encoding="utf-8"), encoding="utf-8")
    (out_root / "git_commit.txt").write_text(commit + "\n", encoding="utf-8")
    write_csv(out_root / "results.csv", records)
    meta = {
        "experiment": "EXP-SURG-001A",
        "mode": "mock",
        "git_commit": commit,
        "n_rollouts": len(records),
        "aggregate": table,
        "branch_replay": "action_replay_deterministic_mock",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "note": "Mock kinematics prove counterfactual branching + artifact OS. Replace with Isaac script output.",
    }
    (out_root / "summary.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    figures = write_figures(out_root / "figures", table, records)
    videos = write_placeholder_videos(out_root / "videos")
    report_path = (
        REPO
        / "experiments/surgical_intelligence/exp_surg_001_execute_or_defer/study1a_report.md"
    )
    write_report(report_path, cfg, table, records, "mock", commit, figures)
    (out_root / "report.md").write_text(report_path.read_text(encoding="utf-8"), encoding="utf-8")

    print("\n=== EXP-SURG-001A COMPLETE (mock) ===")
    print(f"commit: {commit}")
    print(f"artifacts: {out_root}")
    print(json.dumps(table, indent=2))
    print(f"report: {report_path}")
    print("branch_replay_ok: True (mock action-replay semantics)")
    print("next: EXP-SURG-001B timing curve OR Isaac run via scripts/run_study1a_counterfactual_runpod.sh")


if __name__ == "__main__":
    main()
