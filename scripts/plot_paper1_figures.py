"""Generate Paper 001 main-text figures, tables, and simulation panels (CPU · reproducible).

Outputs under docs/paper1/figures/:
  fig1_architecture_overview.png   — evaluation protocol + system stack
  fig2_same_state_fork.png         — CF branching at onset S
  fig3_profile_d0.png              — D0 recoverability profile (n=20)
  fig4_baseline_overlay.png        — menu vs B2 vs B3
  fig5_occlusion_contrast.png      — D0 vs D1 CONTINUE/REPLAN
  table1_d0_results.png            — formatted results table
  table2_proper_program.png        — full program summary
  sim_panel_continue_replan.png    — top-down schematic @ seed 0
  sim_panel_multimode.png          — five-mode divergence schematic
  tables/*.csv

Usage:
  python scripts/plot_paper1_figures.py
  python scripts/plot_paper1_figures.py --out-dir docs/paper1/figures
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments/surgical_intelligence/exp_surg_001_execute_or_defer"
DEFAULT_D0 = EXP / "results/study1_proper/summary.json"
DEFAULT_V2 = EXP / "results/study1_proper_v2/summary.json"
DEFAULT_OUT = ROOT / "docs/paper1/figures"


def wilson_ci(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return 0.0, 0.0
    p = successes / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = (z / denom) * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return max(0.0, center - margin), min(1.0, center + margin)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def setup_matplotlib():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "figure.dpi": 150,
            "savefig.dpi": 150,
            "savefig.bbox": "tight",
        }
    )
    return plt


def draw_fig1_architecture(out: Path, plt) -> Path:
    """Fig 1 — system stack + evaluation pipeline."""
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.5)
    ax.axis("off")

    def box(x, y, w, h, text, fc="#eef4fb", ec="#2c5282"):
        p = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            facecolor=fc,
            edgecolor=ec,
            linewidth=1.2,
        )
        ax.add_patch(p)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=9, wrap=True)

    def arrow(x1, y1, x2, y2):
        ax.add_patch(
            FancyArrowPatch(
                (x1, y1),
                (x2, y2),
                arrowstyle="-|>",
                mutation_scale=12,
                color="#444",
                linewidth=1.1,
            )
        )

    # Top row — deployment context (Stage 2+; not measured here)
    box(0.3, 4.0, 2.0, 0.9, "Observation\n(proprio + proxy vis)", fc="#f7f7f7", ec="#888")
    box(2.6, 4.0, 2.0, 0.9, "Frozen proposer\n(scripted IK-Rel)", fc="#fff3e0", ec="#e65100")
    box(4.9, 4.0, 2.0, 0.9, "Risk / UQ\n(future selector)", fc="#f7f7f7", ec="#888")
    box(7.2, 4.0, 2.3, 0.9, "Response policy\n{Execute, Reobserve,\nReplan, Defer}", fc="#f7f7f7", ec="#888")
    ax.text(5.0, 5.15, "Surgical agent stack (context · Stage 2+)", ha="center", fontsize=10, fontweight="bold")

    # Bottom row — Paper 001 measurement layer
    ax.plot([0.2, 9.8], [3.55, 3.55], color="#c0392b", lw=1.5, ls="--", alpha=0.6)
    ax.text(5.0, 3.72, "Paper 001 — same-state counterfactual evaluation @ fixed S", ha="center", fontsize=10, fontweight="bold", color="#c0392b")

    box(0.3, 2.0, 1.6, 1.1, "Nominal rollout\nsteps 0 … 19\n(record actions)")
    box(2.2, 2.0, 1.8, 1.1, "Mismatch onset S\n+6 cm Y shift\nocclusion L1 (D0)")
    box(4.3, 2.0, 1.5, 1.1, "Action replay\n(same seed)")
    box(6.1, 2.0, 1.6, 1.1, "Fork response\nCONTINUE · REPLAN\nREOBSERVE · …")
    box(7.9, 2.0, 1.5, 1.1, "Terminal judge\n≤ 2 cm · no AABB\nviolation")
    box(0.3, 0.35, 9.1, 1.2, "Profile table — intervention-conditioned recoverability @ fixed S\n(not a learned WM · CF is the method)", fc="#e8f5e9", ec="#2e7d32")

    for x1, x2 in [(1.9, 2.2), (4.0, 4.3), (5.8, 6.1), (7.7, 7.9)]:
        arrow(x1, 2.55, x2, 2.55)
    arrow(8.65, 2.0, 4.75, 1.55)

    ax.text(5.0, 0.08, "Task: Isaac-Reach-Dual-STAR-IK-Rel · ORBIT · Isaac Sim 4.1", ha="center", fontsize=8, color="#666")

    path = out / "fig1_architecture_overview.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def draw_fig2_fork(out: Path, plt) -> Path:
    """Fig 2 — same-state counterfactual fork at S."""
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 6)
    ax.axis("off")

    def node(x, y, text, fc="#eef4fb"):
        p = FancyBboxPatch(
            (x - 0.55, y - 0.28),
            1.1,
            0.56,
            boxstyle="round,pad=0.02",
            facecolor=fc,
            edgecolor="#333",
        )
        ax.add_patch(p)
        ax.text(x, y, text, ha="center", va="center", fontsize=9)

    def arr(x1, y1, x2, y2):
        ax.add_patch(
            FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=10, color="#444")
        )

    node(1.2, 5.0, "reset(seed)")
    node(3.0, 5.0, "rollout\n0…19")
    node(5.0, 5.0, "apply shift\n@ step 20")
    node(7.0, 5.0, "state S\n(shared)")
    for x1, x2 in [(1.75, 2.45), (3.55, 4.45), (5.55, 6.45)]:
        arr(x1, 5.0, x2, 5.0)

    ax.text(7.0, 5.55, "identical through S", ha="center", fontsize=8, color="#c0392b", fontweight="bold")

    branches = [
        (1.5, 3.2, "CONTINUE\nchase frozen", "#fdecea", "0/20"),
        (3.3, 2.2, "REPLAN_d20\nshift @ t+20", "#e8f4fd", "19/20"),
        (5.1, 2.2, "REOBSERVE\nhold→clear", "#f3e5f5", "17/20"),
        (6.9, 2.2, "RESHAPE\nproxy→clear", "#e8f5e9", "18/20"),
        (8.5, 3.2, "HANDOVER\nstub", "#f5f5f5", "0/20"),
    ]
    for x, y, lab, fc, rate in branches:
        node(x, y, lab, fc)
        arr(7.0, 4.72, x, y + 0.28)
        ax.text(x, y - 0.55, f"D0: {rate}", ha="center", fontsize=8, color="#555")

    node(4.5, 0.6, "terminal judge → profile", fc="#fff9c4")
    for x, y, *_ in branches:
        arr(x, y - 0.28, 4.5, 0.88)

    ax.set_title("Same-state counterfactual fork @ mismatch onset S (D0 · n=20)", fontsize=11)
    path = out / "fig2_same_state_fork.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def draw_profile_bar(rows: list[dict], title: str, out_path: Path, plt, highlight: str | None = None) -> None:
    labels = [r["response"] for r in rows]
    rates = [float(r["success_rate"]) for r in rows]
    ns = [int(r["n"]) for r in rows]
    yerr_lo, yerr_hi = [], []
    for r, n in zip(rates, ns):
        k = int(round(r * n))
        lo, hi = wilson_ci(k, n)
        yerr_lo.append(r - lo)
        yerr_hi.append(hi - r)

    fig, ax = plt.subplots(figsize=(8, 4.2))
    colors = []
    for lb in labels:
        if lb == "CONTINUE":
            colors.append("#c0392b")
        elif highlight and lb == highlight:
            colors.append("#27ae60")
        else:
            colors.append("#2980b9")
    x = list(range(len(labels)))
    ax.bar(x, rates, color=colors, alpha=0.88)
    ax.errorbar(x, rates, yerr=[yerr_lo, yerr_hi], fmt="none", color="black", capsize=4)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=18, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Successful resolution rate")
    ax.set_title(title)
    ax.axhline(0.02, color="gray", ls=":", lw=0.8, alpha=0.4)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def draw_fig4_baseline(d0: dict, v2: dict, out: Path, plt) -> Path:
    """Baseline overlay — best menu vs REPLAN vs B2 vs B3 vs CONTINUE."""
    d0_rows = {r["response"]: r for r in d0["aggregate_by_mode"]}
    best = max(
        float(d0_rows[m]["success_rate"])
        for m in ("REPLAN_d20", "REOBSERVE", "RESHAPE")
    )
    series = [
        ("Best-of-menu", best, "D0"),
        ("REPLAN_d20", float(d0_rows["REPLAN_d20"]["success_rate"]), "D0"),
        ("CONTINUE", float(d0_rows["CONTINUE"]["success_rate"]), "D0"),
        ("B3 situation", float(v2["blocks"]["d3"]["aggregate_by_mode"][0]["success_rate"]), "D3"),
        ("B2 UQ rule", float(v2["blocks"]["d2"]["aggregate_by_mode"][0]["success_rate"]), "D2"),
    ]
    labels = [s[0] for s in series]
    rates = [s[1] for s in series]
    colors = ["#27ae60", "#2980b9", "#c0392b", "#8e44ad", "#e67e22"]

    fig, ax = plt.subplots(figsize=(8, 4.2))
    x = range(len(labels))
    bars = ax.bar(x, rates, color=colors, alpha=0.88)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=15, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Successful resolution rate @ fixed S")
    ax.set_title("Fig 4 — Response menu vs rule baselines (Tier C · n=20)")
    for i, (bar, (_, rate, block)) in enumerate(zip(bars, series)):
        ax.text(bar.get_x() + bar.get_width() / 2, rate + 0.03, f"{rate:.0%}", ha="center", fontsize=9)
        ax.text(bar.get_x() + bar.get_width() / 2, -0.08, block, ha="center", fontsize=7, color="#666")
    fig.tight_layout()
    path = out / "fig4_baseline_overlay.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def draw_fig5_occlusion(d0: dict, v2: dict, out: Path, plt) -> Path:
    d0_rows = {r["response"]: r for r in d0["aggregate_by_mode"]}
    d1_rows = {r["response"]: r for r in v2["blocks"]["d1"]["aggregate_by_mode"]}
    groups = ["D0 occluded", "D1 no occlusion"]
    cont = [float(d0_rows["CONTINUE"]["success_rate"]), float(d1_rows["CONTINUE"]["success_rate"])]
    repl = [float(d0_rows["REPLAN_d20"]["success_rate"]), float(d1_rows["REPLAN_d20"]["success_rate"])]

    fig, ax = plt.subplots(figsize=(6.5, 4))
    x = [0, 1]
    w = 0.35
    ax.bar([i - w / 2 for i in x], cont, width=w, label="CONTINUE", color="#c0392b")
    ax.bar([i + w / 2 for i in x], repl, width=w, label="REPLAN_d20", color="#2980b9")
    ax.set_xticks(x)
    ax.set_xticklabels(groups)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Successful resolution rate")
    ax.set_title("Fig 5 — Occlusion contrast (descriptive · RQ-P)")
    ax.legend()
    for i, (c, r) in enumerate(zip(cont, repl)):
        ax.text(i - w / 2, c + 0.02, f"{c:.0%}", ha="center", fontsize=9)
        ax.text(i + w / 2, r + 0.02, f"{r:.0%}", ha="center", fontsize=9)
    fig.tight_layout()
    path = out / "fig5_occlusion_contrast.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def write_table_png(rows: list[list[str]], title: str, out_path: Path, plt, col_widths: list[float] | None = None) -> None:
    fig, ax = plt.subplots(figsize=(10, 0.45 * len(rows) + 0.8))
    ax.axis("off")
    tbl = ax.table(cellText=rows, loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1.1, 1.45)
    if col_widths:
        for i, w in enumerate(col_widths):
            for j in range(len(rows)):
                tbl[(j, i)].set_width(w)
    # header row styling
    for j in range(len(rows[0])):
        tbl[(0, j)].set_facecolor("#eef4fb")
        tbl[(0, j)].set_text_props(fontweight="bold")
    ax.set_title(title, fontsize=11, pad=12)
    fig.savefig(out_path)
    plt.close(fig)


def draw_tables(d0: dict, v2: dict, out: Path, plt) -> list[Path]:
    table_dir = out / "tables"
    table_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    # Table 1 — D0
    rows = [["Mode", "Class", "Success", "Rate", "Wilson 95% CI", "Mean dist (m)"]]
    csv_rows = [["mode", "class", "successes", "n", "rate", "wilson_lo", "wilson_hi", "mean_final_distance_m"]]
    for r in d0["aggregate_by_mode"]:
        n = int(r["n"])
        rate = float(r["success_rate"])
        k = int(round(rate * n))
        lo, hi = wilson_ci(k, n)
        ci = f"[{lo:.2f}, {hi:.2f}]" if n else "—"
        rows.append([
            r["response"],
            r.get("class", ""),
            f"{k}/{n}",
            f"{rate:.0%}",
            ci,
            f"{r.get('mean_final_distance_m', 0):.3f}",
        ])
        csv_rows.append([r["response"], r.get("class", ""), k, n, f"{rate:.3f}", f"{lo:.3f}", f"{hi:.3f}", r.get("mean_final_distance_m", "")])

    p1 = out / "table1_d0_results.png"
    write_table_png(rows, "Table 1 — D0 recoverability profile @ fixed S (n=20)", p1, plt)
    paths.append(p1)
    with (table_dir / "table1_d0.csv").open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(csv_rows)

    # Table 2 — full program
    rows2 = [["Block", "Sub-RQ", "Condition", "Primary outcome", "Success rate"]]
    csv2 = [["block", "sub_rq", "condition", "outcome", "success_rate", "n"]]
    d0_rows = {r["response"]: r for r in d0["aggregate_by_mode"]}
    program = [
        ("D0", "RQ-M", "5-mode + occlusion L1", "REPLAN vs CONTINUE", "19/20 vs 0/20"),
        ("D1", "RQ-P", "no occlusion control", "REPLAN vs CONTINUE", "19/20 vs 1/20"),
        ("D2", "RQ-B", "B2 UQ-inspired rule", "HANDOVER burden", "20/20 handover · 0/20 success"),
        ("D3", "RQ-B", "B3 situation rule", "REOBSERVE path", "17/20 (85%)"),
    ]
    for block, rq, cond, outcome, rate in program:
        rows2.append([block, rq, cond, outcome, rate])
        csv2.append([block, rq, cond, outcome, rate, "20"])

    p2 = out / "table2_proper_program.png"
    write_table_png(rows2, "Table 2 — Paper 001 proper program summary (Tier C)", p2, plt)
    paths.append(p2)
    with (table_dir / "table2_program.csv").open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(csv2)

    return paths


def draw_sim_panel_continue_replan(d0_json: Path, out: Path, plt) -> Path:
    """Top-down schematic simulation panel — seed 0 CONTINUE vs REPLAN."""
    from matplotlib.patches import Circle, Rectangle

    # Representative geometry from method spec (meters, top-down X-Y)
    frozen = (0.42, 0.02)
    shifted = (0.42, 0.08)
    forbidden_c = (0.45, 0.0)
    forbidden_h = 0.04
    base = (0.15, 0.0)

    fig, axes = plt.subplots(1, 3, figsize=(11, 3.8))
    panels = [
        ("t = 0–19 · nominal reach", "nominal", None),
        ("t = 20 · mismatch S (shared state)", "onset", None),
        ("t > 20 · forked responses", "fork", None),
    ]

    for ax, (title, phase, _) in zip(axes, panels):
        ax.set_aspect("equal")
        ax.set_xlim(0.0, 0.65)
        ax.set_ylim(-0.15, 0.22)
        ax.set_xlabel("X (m)")
        ax.set_ylabel("Y (m)")
        ax.set_title(title, fontsize=9)
        ax.add_patch(Rectangle(
            (forbidden_c[0] - forbidden_h, forbidden_c[1] - forbidden_h),
            2 * forbidden_h,
            2 * forbidden_h,
            facecolor="#ffcccc",
            edgecolor="#c0392b",
            alpha=0.5,
            label="forbidden AABB",
        ))
        ax.plot(*base, "ks", ms=8)
        ax.text(base[0] - 0.02, base[1] - 0.06, "robot base", fontsize=7)
        ax.plot(*frozen, "go", ms=10, label="frozen target")
        ax.plot(*shifted, "b^", ms=10, label="shifted target")

        if phase == "nominal":
            xs = [base[0], 0.28, 0.36, frozen[0]]
            ys = [base[1], 0.01, 0.015, frozen[1]]
            ax.plot(xs, ys, "k-", lw=2, label="EE path")
        elif phase == "onset":
            ax.annotate("", xy=shifted, xytext=frozen, arrowprops=dict(arrowstyle="->", color="#e67e22", lw=2))
            ax.text(0.44, 0.05, "+6 cm Y", fontsize=8, color="#e67e22")
            ax.plot(frozen[0], frozen[1], "ko", ms=6)
            ax.text(0.46, 0.01, "occlusion L1\nvis=0.35", fontsize=7, color="#8e44ad")
        else:
            # CONTINUE: stays near frozen; REPLAN: curves to shifted
            cx = [frozen[0], 0.40, 0.38, 0.40, frozen[0]]
            cy = [frozen[1], 0.03, 0.01, -0.02, frozen[1]]
            rx = [frozen[0], 0.39, 0.41, shifted[0]]
            ry = [frozen[1], 0.05, 0.07, shifted[1]]
            ax.plot(cx, cy, color="#c0392b", lw=2, ls="--", label="CONTINUE (fail)")
            ax.plot(rx, ry, color="#2980b9", lw=2, label="REPLAN_d20 (success)")
            ax.text(0.48, -0.10, "seed 0 · D0", fontsize=7, color="#666")

        ax.legend(fontsize=6, loc="upper left")

    fig.suptitle("Simulation panel — ORBIT Dual-STAR Reach (top-down schematic · reproducible via capture script)", fontsize=10)
    fig.tight_layout()
    path = out / "sim_panel_continue_replan.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def draw_sim_panel_multimode(out: Path, plt) -> Path:
    """Five-mode divergence schematic at S."""
    from matplotlib.patches import FancyBboxPatch

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    ax.text(5, 4.7, "Multi-mode response menu @ fixed S (D0 · schematic)", ha="center", fontsize=11, fontweight="bold")

    modes = [
        (1, 2.5, "CONTINUE", "Chase frozen target\n0% success", "#fdecea"),
        (3, 2.5, "REPLAN_d20", "Delay 20 → shifted\n95% success", "#e8f4fd"),
        (5, 2.5, "REOBSERVE", "Hold 10 · clear vis\n85% success", "#f3e5f5"),
        (7, 2.5, "RESHAPE", "Proxy reshape 20\n90% success", "#e8f5e9"),
        (9, 2.5, "HANDOVER", "Zero-action stub\n0% (burden proxy)", "#f5f5f5"),
    ]
    ax.add_patch(FancyBboxPatch((3.5, 3.6), 3, 0.7, boxstyle="round", facecolor="#fff9c4", edgecolor="#333"))
    ax.text(5, 3.95, "Shared state S @ step 20", ha="center", va="center", fontsize=10)

    for x, y, name, desc, fc in modes:
        ax.add_patch(FancyBboxPatch((x - 0.7, y - 0.55), 1.4, 1.1, boxstyle="round", facecolor=fc, edgecolor="#555"))
        ax.text(x, y + 0.15, name, ha="center", va="center", fontsize=9, fontweight="bold")
        ax.text(x, y - 0.25, desc, ha="center", va="center", fontsize=7)
        ax.plot([5, x], [3.6, y + 0.55], "k-", lw=0.8, alpha=0.5)

    ax.text(5, 0.4, "Isaac viewport capture: scripts/capture_study1_viewport.sh (GPU · seed 0)", ha="center", fontsize=8, color="#666")
    path = out / "sim_panel_multimode.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--d0-summary", type=Path, default=DEFAULT_D0)
    parser.add_argument("--v2-summary", type=Path, default=DEFAULT_V2)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    plt = setup_matplotlib()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    d0 = load_json(args.d0_summary)
    v2 = load_json(args.v2_summary)

    written: list[str] = []

    for fn in (
        lambda: draw_fig1_architecture(args.out_dir, plt),
        lambda: draw_fig2_fork(args.out_dir, plt),
        lambda: draw_fig4_baseline(d0, v2, args.out_dir, plt),
        lambda: draw_fig5_occlusion(d0, v2, args.out_dir, plt),
        lambda: draw_sim_panel_continue_replan(args.d0_summary, args.out_dir, plt),
        lambda: draw_sim_panel_multimode(args.out_dir, plt),
    ):
        p = fn()
        written.append(str(p))
        print(f"[INFO] wrote {p}")

    draw_profile_bar(
        d0["aggregate_by_mode"],
        "Fig 3 — D0 recoverability profile @ fixed S (n=20 · Wilson 95% CI)",
        args.out_dir / "fig3_profile_d0.png",
        plt,
    )
    written.append(str(args.out_dir / "fig3_profile_d0.png"))
    print(f"[INFO] wrote {args.out_dir / 'fig3_profile_d0.png'}")

    for p in draw_tables(d0, v2, args.out_dir, plt):
        written.append(str(p))
        print(f"[INFO] wrote {p}")

    manifest = {
        "generator": "scripts/plot_paper1_figures.py",
        "d0_summary": str(args.d0_summary.relative_to(ROOT)),
        "v2_summary": str(args.v2_summary.relative_to(ROOT)),
        "figures": [str(Path(w).relative_to(ROOT)) for w in written],
    }
    manifest_path = args.out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"[INFO] wrote {manifest_path}")


if __name__ == "__main__":
    main()
