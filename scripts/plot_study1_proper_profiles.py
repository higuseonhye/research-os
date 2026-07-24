"""Fig 3 — Paper 001 D0 profile table/bar chart from study1_proper summary.

Usage:
  python scripts/plot_study1_proper_profiles.py
  python scripts/plot_study1_proper_profiles.py --summary path/to/summary.json
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = (
    ROOT
    / "experiments/surgical_intelligence/exp_surg_001_execute_or_defer"
    / "results/study1_proper/summary.json"
)
DEFAULT_OUT = DEFAULT_SUMMARY.parent / "figures"


def wilson_ci(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return 0.0, 0.0
    p = successes / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = (z / denom) * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return max(0.0, center - margin), min(1.0, center + margin)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    data = json.loads(args.summary.read_text(encoding="utf-8"))
    rows = data["aggregate_by_mode"]
    args.out_dir.mkdir(parents=True, exist_ok=True)

    table_path = args.out_dir / "profile_table_d0.csv"
    with table_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["response", "class", "n", "successes", "success_rate", "wilson_lo", "wilson_hi"])
        for r in rows:
            n = int(r["n"])
            sr = float(r["success_rate"])
            k = int(round(sr * n))
            lo, hi = wilson_ci(k, n)
            w.writerow([r["response"], r.get("class", ""), n, k, f"{sr:.3f}", f"{lo:.3f}", f"{hi:.3f}"])

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print(f"[INFO] matplotlib missing; wrote CSV only: {table_path}")
        return

    labels = [r["response"] for r in rows]
    rates = [float(r["success_rate"]) for r in rows]
    ns = [int(r["n"]) for r in rows]
    yerr_lo = []
    yerr_hi = []
    for r, n in zip(rates, ns):
        k = int(round(r * n))
        lo, hi = wilson_ci(k, n)
        yerr_lo.append(r - lo)
        yerr_hi.append(hi - r)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = range(len(labels))
    colors = ["#c0392b" if lb == "CONTINUE" else "#2980b9" for lb in labels]
    ax.bar(x, rates, color=colors, alpha=0.85)
    ax.errorbar(x, rates, yerr=[yerr_lo, yerr_hi], fmt="none", color="black", capsize=4)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Successful resolution rate")
    ax.set_title("Paper 001 D0 — recoverability profile @ fixed S (n=20)")
    ax.axhline(0.95, color="gray", ls="--", lw=0.8, alpha=0.5)
    fig.tight_layout()
    png = args.out_dir / "profile_bar_d0.png"
    fig.savefig(png, dpi=150)
    plt.close(fig)
    print(f"[INFO] wrote {table_path}")
    print(f"[INFO] wrote {png}")


if __name__ == "__main__":
    main()
