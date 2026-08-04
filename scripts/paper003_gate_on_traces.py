"""Run the real relation gate on real contact traces.

CPU only. Reads the JSON written by `orbit_lift_stopping_probe.py` - which
records both the object's pose and the end effector's, every step - and asks the
actual gate whether it would fire, rather than consulting a retention threshold
taken from a toy friction model.

This is the decisive test for Paper 003. The gate requires target motion to be
proximity-conditioned: present while a body is near, absent once it leaves. A
struck block that coasts violates that, and a constant-velocity model - Paper
002's operator - explains the coast. Whether real contact leaves enough
proximity conditioning to fire on is not something a proxy can settle.

Usage:
    python scripts/paper003_gate_on_traces.py results/gate_v0.04
    python scripts/paper003_gate_on_traces.py results/gate_v0.0* --radius 0.012
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from wm_expansion.relation_dynamics import (
    RelationGateThresholds,
    evaluate_relation_gate,
    gate_fired_persistently,
)

MIN_DELTAS = 6


def load_traces(paths: Iterable[str]) -> list[dict[str, Any]]:
    records = []
    for path in paths:
        root = Path(path)
        files = sorted(root.rglob("*.json")) if root.is_dir() else [root]
        for file in files:
            try:
                record = json.loads(file.read_text())
            except (json.JSONDecodeError, OSError) as exc:
                print(f"  ! skipped {file}: {exc}")
                continue
            if record.get("positions") and record.get("ee_positions"):
                record["_source"] = str(file)
                records.append(record)
    return records


def judge(
    record: dict[str, Any],
    thresholds: RelationGateThresholds,
    radius: float,
    horizon: int,
) -> dict[str, Any]:
    """Gate statistics over the whole trace and at every prefix."""

    targets = np.asarray(record["positions"], dtype=np.float64)
    bodies = np.asarray(record["ee_positions"], dtype=np.float64)
    if len(targets) != len(bodies) or len(targets) < MIN_DELTAS + 2:
        return {"source": record.get("_source"), "usable": False}

    fired = []
    contrasts = []
    gains = []
    for end in range(MIN_DELTAS + 1, len(targets) + 1):
        decision = evaluate_relation_gate(
            targets[:end], bodies[:end], thresholds,
            interaction_radius=radius, horizon=horizon,
        )
        contrasts.append(decision.proximity_contrast)
        gains.append(decision.constant_velocity_gain)
        fired.append(
            gate_fired_persistently(
                targets[:end], bodies[:end], thresholds,
                interaction_radius=radius, horizon=horizon,
            )
        )
    stopping = record.get("stopping") or {}
    return {
        "source": record.get("_source"),
        "usable": True,
        "seed": record.get("seed"),
        "struck_at": record.get("struck_at"),
        "retention": stopping.get("retention"),
        "coast_mm": (stopping.get("coast_distance") or 0.0) * 1000.0,
        "step_rate": float(np.mean(fired)),
        "trial": bool(np.any(fired)),
        "median_contrast": float(np.median(contrasts)),
        "median_cv_gain": float(np.median(gains)),
        "max_cv_gain": float(np.max(gains)),
    }


def render(rows: list[dict[str, Any]]) -> str:
    usable = [r for r in rows if r["usable"]]
    lines = [
        "The relation gate on real contact traces",
        "(not the toy model's retention proxy - the gate itself)",
        "",
        f"{'seed':>5}{'struck':>8}{'retain':>8}{'coast':>8}"
        f"{'contrast':>10}{'cv_gain':>9}{'per-step':>10}{'fired?':>8}",
        "-" * 66,
    ]
    for row in sorted(usable, key=lambda r: (r.get("seed") or 0)):
        lines.append(
            f"{row['seed']:>5}{str(row['struck_at']):>8}"
            f"{(row['retention'] if row['retention'] is not None else float('nan')):>8.2f}"
            f"{row['coast_mm']:>8.1f}{row['median_contrast']:>10.3f}"
            f"{row['median_cv_gain']:>9.3f}{row['step_rate']:>10.2f}"
            f"{str(row['trial']):>8}"
        )
    if usable:
        trial = float(np.mean([r["trial"] for r in usable]))
        step = float(np.mean([r["step_rate"] for r in usable]))
        lines += [
            "",
            f"{len(usable)} traces   per-trial {trial:.2f}   per-step {step:.2f}",
            "",
            "H3 asks for >= 0.90 on the treatment condition. A gate that fires on"
            "\nfew of these is reporting that real contact leaves the residual"
            "\nsubstantially constant-velocity, which is Paper 002's operator and"
            "\nnot a missing relation.",
        ]
    skipped = len(rows) - len(usable)
    if skipped:
        lines.append(f"\n{skipped} trace(s) unusable - too short, or no end-effector poses")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--radius", type=float, default=0.012,
                        help="contact radius. 50 mm is the injected design's "
                             "number and was shown to mark non-contact as "
                             "contact in this scene; observed contact is 2-5 mm")
    parser.add_argument("--horizon", type=int, default=6, help="dispense latency")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    records = load_traces(args.paths)
    if not records:
        raise SystemExit("no traces with both object and end-effector poses")
    thresholds = RelationGateThresholds()
    rows = [judge(r, thresholds, args.radius, args.horizon) for r in records]
    print(json.dumps(rows, indent=2) if args.json else render(rows))


if __name__ == "__main__":
    main()
