"""Render simulation panels from Isaac EE trace JSON (post-GPU capture).

Usage:
  python scripts/plot_paper1_from_ee_traces.py --trace-dir docs/paper1/figures/isaac_captures
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRACE_DIR = ROOT / "docs/paper1/figures/isaac_captures"
DEFAULT_OUT = ROOT / "docs/paper1/figures"


def load_traces(trace_dir: Path) -> list[dict]:
    traces = []
    for p in sorted(trace_dir.glob("*_ee_trace.json")):
        traces.append(json.loads(p.read_text(encoding="utf-8")))
    return traces


def plot_traces(traces: list[dict], out: Path) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    fig, axes = plt.subplots(1, len(traces), figsize=(4.5 * len(traces), 4), squeeze=False)
    for ax, tr in zip(axes[0], traces):
        ee = [t["ee"] for t in tr["trace"]]
        xs = [e[0] for e in ee]
        ys = [e[1] for e in ee]
        fc = tr["forbidden_center"]
        fh = tr["forbidden_half"][0]
        frozen = tr["frozen_xyz"]
        shifted = tr["shifted_xyz"]
        ax.add_patch(Rectangle((fc[0] - fh, fc[1] - fh), 2 * fh, 2 * fh, fc="#ffcccc", ec="#c0392b", alpha=0.5))
        ax.plot(xs, ys, lw=2, label="EE trace")
        ax.plot(frozen[0], frozen[1], "go", ms=8, label="frozen target")
        ax.plot(shifted[0], shifted[1], "b^", ms=8, label="shifted target")
        onset = tr["onset_step"]
        if onset < len(xs):
            ax.plot(xs[onset], ys[onset], "ko", ms=6)
        ax.set_aspect("equal")
        ax.set_xlabel("X (m)")
        ax.set_ylabel("Y (m)")
        ok = tr["terminal"]["successful_resolution"]
        ax.set_title(f"{tr['mode']} · seed {tr['seed']}\n{'success' if ok else 'fail'}")
        ax.legend(fontsize=7)

    fig.suptitle("Isaac EE traces — top-down (from capture script)", fontsize=10)
    fig.tight_layout()
    path = out / "sim_panel_isaac_traces.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace-dir", type=Path, default=DEFAULT_TRACE_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    traces = load_traces(args.trace_dir)
    if not traces:
        print(f"[WARN] no traces in {args.trace_dir}; run scripts/capture_study1_viewport.sh on GPU first")
        return
    args.out_dir.mkdir(parents=True, exist_ok=True)
    p = plot_traces(traces, args.out_dir)
    print(f"[INFO] wrote {p}")


if __name__ == "__main__":
    main()
