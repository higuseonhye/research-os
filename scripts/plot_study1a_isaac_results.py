"""Mint EXP-SURG-001A paper figures from Isaac aggregate (no W&B / no live GUI).

Reads a small committed JSON summary (or full isaac_results.json) and writes:
  figures/result_table.png
  figures/counterfactual_grid.png
  figures/final_distance_by_episode.png
  tables/quantitative_results.csv

Usage (local):
  python scripts/plot_study1a_isaac_results.py
  python scripts/plot_study1a_isaac_results.py --results path/to/isaac_results.json
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = (
    ROOT
    / "experiments/surgical_intelligence/exp_surg_001_execute_or_defer"
    / "results/study1a_isaac/isaac_aggregate.json"
)
DEFAULT_OUT = (
    ROOT
    / "experiments/surgical_intelligence/exp_surg_001_execute_or_defer"
    / "results/study1a_isaac"
)


def load_records(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if "records" in data:
        return list(data["records"])
    if "episodes" in data:
        # compact aggregate format
        rows: list[dict[str, Any]] = []
        for ep in data["episodes"]:
            for resp in ("CONTINUE", "REPLAN"):
                cell = ep[resp]
                rows.append(
                    {
                        "episode": ep["episode"],
                        "response": resp,
                        "final_distance_m": cell["final_distance_m"],
                        "completion_steps": cell["completion_steps"],
                        "successful_resolution": cell.get("terminal_category")
                        == "successful_resolution",
                        "forbidden_violation": cell.get("terminal_category") == "unsafe_failure",
                        "terminal_category": cell["terminal_category"],
                    }
                )
        return rows
    raise ValueError(f"Unrecognized results schema: {path}")


def aggregate(records: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for resp in ("CONTINUE", "REPLAN"):
        xs = [r for r in records if r.get("response") == resp]
        n = max(1, len(xs))
        out[resp] = {
            "n": float(len(xs)),
            "successful_resolution_rate": sum(1 for r in xs if r.get("successful_resolution")) / n,
            "forbidden_violation_rate": sum(1 for r in xs if r.get("forbidden_violation")) / n,
            "mean_final_distance_m": sum(float(r["final_distance_m"]) for r in xs) / n,
            "mean_completion_steps": sum(float(r["completion_steps"]) for r in xs) / n,
        }
    return out


def write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = [
        "episode",
        "response",
        "terminal_category",
        "final_distance_m",
        "completion_steps",
        "successful_resolution",
        "forbidden_violation",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for r in records:
            w.writerow({k: r.get(k) for k in keys})


def write_figures(out: Path, table: dict[str, dict[str, float]], records: list[dict[str, Any]]) -> list[str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out.mkdir(parents=True, exist_ok=True)
    written: list[str] = []

    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    ax.axis("off")
    cell = [["Response", "Success", "Unsafe", "Mean dist (m)", "Mean steps"]]
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
    tbl = ax.table(cellText=cell, loc="center", cellLoc="center")
    tbl.scale(1.2, 1.5)
    ax.set_title("EXP-SURG-001A Isaac — CONTINUE vs REPLAN")
    p = out / "result_table.png"
    fig.savefig(p, dpi=160, bbox_inches="tight")
    plt.close(fig)
    written.append(str(p))

    # Fig 4 style: success bars + distance bars
    fig, axes = plt.subplots(1, 2, figsize=(8.5, 3.2))
    resps = ["CONTINUE", "REPLAN"]
    succ = [table[r]["successful_resolution_rate"] for r in resps]
    dist = [table[r]["mean_final_distance_m"] for r in resps]
    colors = ["#b85c38", "#2f6f4e"]
    axes[0].bar(resps, succ, color=colors)
    axes[0].set_ylim(0, 1.05)
    axes[0].set_ylabel("Successful resolution rate")
    axes[0].set_title("Same-state counterfactual")
    axes[1].bar(resps, dist, color=colors)
    axes[1].axhline(0.02, color="gray", ls="--", lw=1, label="tol 0.02 m")
    axes[1].set_ylabel("Mean final distance (m)")
    axes[1].set_title("Distance to shifted target")
    axes[1].legend(fontsize=8)
    fig.suptitle("Fig 4 draft — target shift @ onset → two responses", fontsize=11)
    fig.tight_layout()
    p = out / "counterfactual_grid.png"
    fig.savefig(p, dpi=160, bbox_inches="tight")
    plt.close(fig)
    written.append(str(p))

    # Per-episode final distance
    eps = sorted({int(r["episode"]) for r in records})
    fig, ax = plt.subplots(figsize=(7.5, 3.2))
    x = list(range(len(eps)))
    cont = [
        next(float(r["final_distance_m"]) for r in records if int(r["episode"]) == e and r["response"] == "CONTINUE")
        for e in eps
    ]
    rep = [
        next(float(r["final_distance_m"]) for r in records if int(r["episode"]) == e and r["response"] == "REPLAN")
        for e in eps
    ]
    width = 0.38
    ax.bar([i - width / 2 for i in x], cont, width=width, label="CONTINUE", color="#b85c38")
    ax.bar([i + width / 2 for i in x], rep, width=width, label="REPLAN", color="#2f6f4e")
    ax.axhline(0.02, color="gray", ls="--", lw=1, label="tol 0.02 m")
    ax.set_xticks(x)
    ax.set_xticklabels([f"ep{e}" for e in eps])
    ax.set_ylabel("Final distance (m)")
    ax.set_title("Per-episode terminal distance (Isaac smoke)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    p = out / "final_distance_by_episode.png"
    fig.savefig(p, dpi=160, bbox_inches="tight")
    plt.close(fig)
    written.append(str(p))

    return written


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    records = load_records(args.results)
    table = aggregate(records)
    write_csv(args.out / "tables" / "quantitative_results.csv", records)
    figs = write_figures(args.out / "figures", table, records)
    meta = {
        "experiment": "EXP-SURG-001A",
        "mode": "isaac",
        "source": str(args.results),
        "aggregate": table,
        "figures": figs,
    }
    (args.out / "plot_summary.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(table, indent=2))
    for f in figs:
        print("wrote", f)


if __name__ == "__main__":
    main()
