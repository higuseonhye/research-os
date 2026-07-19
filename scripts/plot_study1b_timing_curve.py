"""Mint EXP-SURG-001B Fig 5 recoverability-vs-delay from Isaac results."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = (
    ROOT
    / "experiments/surgical_intelligence/exp_surg_001_execute_or_defer"
    / "results/study1b_isaac"
)


def load_records(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    return list(data.get("records", []))


def curve_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by: dict[str, list[dict[str, Any]]] = {}
    for r in records:
        by.setdefault(str(r["response"]), []).append(r)
    rows = []
    for resp, xs in sorted(by.items()):
        n = max(1, len(xs))
        delay = xs[0].get("replan_delay")
        rows.append(
            {
                "response": resp,
                "replan_delay": delay,
                "n": len(xs),
                "success_rate": sum(1 for x in xs if x.get("successful_resolution")) / n,
                "mean_final_distance_m": sum(float(x["final_distance_m"]) for x in xs) / n,
                "mean_completion_steps": sum(float(x["completion_steps"]) for x in xs) / n,
            }
        )
    return rows


def write_figures(out: Path, rows: list[dict[str, Any]]) -> list[str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out.mkdir(parents=True, exist_ok=True)
    written: list[str] = []

    # Prefer delay-ordered replan points + continue as delay=None marker at right/left
    replans = [r for r in rows if r["response"] != "CONTINUE"]
    replans = sorted(replans, key=lambda r: (999 if r["replan_delay"] is None else int(r["replan_delay"])))
    cont = next((r for r in rows if r["response"] == "CONTINUE"), None)

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.4))
    xs = [int(r["replan_delay"]) for r in replans]
    succ = [r["success_rate"] for r in replans]
    dist = [r["mean_final_distance_m"] for r in replans]
    axes[0].plot(xs, succ, "o-", color="#2f6f4e", label="REPLAN@delay")
    if cont is not None:
        axes[0].axhline(cont["success_rate"], color="#b85c38", ls="--", label="CONTINUE")
    axes[0].set_ylim(-0.05, 1.05)
    axes[0].set_xlabel("Replan delay (steps after onset)")
    axes[0].set_ylabel("Successful resolution rate")
    axes[0].set_title("Empirical recoverability vs delay")
    axes[0].legend(fontsize=8)

    axes[1].plot(xs, dist, "o-", color="#2f6f4e", label="REPLAN@delay")
    if cont is not None:
        axes[1].axhline(cont["mean_final_distance_m"], color="#b85c38", ls="--", label="CONTINUE")
    axes[1].axhline(0.02, color="gray", ls=":", lw=1, label="tol 0.02 m")
    axes[1].set_xlabel("Replan delay (steps after onset)")
    axes[1].set_ylabel("Mean final distance (m)")
    axes[1].set_title("Distance to shifted target")
    axes[1].legend(fontsize=8)
    fig.suptitle("Fig 5 draft — EXP-SURG-001B timing curve", fontsize=11)
    fig.tight_layout()
    p = out / "recoverability_vs_delay.png"
    fig.savefig(p, dpi=160, bbox_inches="tight")
    plt.close(fig)
    written.append(str(p))
    return written


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    records = load_records(args.results)
    rows = curve_rows(records)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "tables").mkdir(parents=True, exist_ok=True)
    with (args.out / "tables" / "timing_curve.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["response"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    figs = write_figures(args.out / "figures", rows)
    (args.out / "plot_summary.json").write_text(
        json.dumps({"rows": rows, "figures": figs}, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(rows, indent=2))
    for f in figs:
        print("wrote", f)


if __name__ == "__main__":
    main()
