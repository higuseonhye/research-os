"""Aggregate Paper 003 pilot records into a per-condition summary.

CPU only - reads the JSON the Isaac runner writes and reports per-arm landing
rates, miss distances, and gate fire rates. No Isaac import, so this is
testable and runnable anywhere.

CALIBRATION ONLY. The inputs are engineering-pilot records explicitly excluded
from confirmatory evidence; this script summarises them and does not promote
them.

Usage:
    python scripts/aggregate_paper003_pilot.py results/paper003_sweep_seeds
    python scripts/aggregate_paper003_pilot.py results/* --tolerance 0.020
"""

from __future__ import annotations

import argparse
import json
import math

import numpy as np
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

ARMS = ("A", "B", "C", "D", "D_oracle")


def load_records(paths: Iterable[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in paths:
        root = Path(path)
        files = sorted(root.rglob("*.json")) if root.is_dir() else [root]
        for file in files:
            try:
                records.append(json.loads(file.read_text()))
            except (json.JSONDecodeError, OSError) as exc:  # keep going, say what broke
                print(f"  ! skipped {file}: {exc}")
    return records


def miss_distances(record: dict[str, Any]) -> dict[str, float] | None:
    """Metres from each arm's aim to the true landing point."""
    aims = record.get("aims") or {}
    landing = aims.get("D_oracle")
    if landing is None or record.get("committed_at") is None:
        return None
    return {
        arm: math.dist(aims[arm], landing) for arm in ARMS if arm in aims
    }


def bootstrap_rate_interval(
    outcomes: list[bool], draws: int = 10000, seed: int = 20260804
) -> tuple[float, float]:
    """Percentile 95% interval for a landing rate, resampling cells.

    The preregistration requires intervals rather than point estimates, and
    with nine cells they are wide enough that quoting a bare rate would be
    misleading on its own.
    """

    if not outcomes:
        return (0.0, 0.0)
    rng = np.random.default_rng(seed)
    data = np.asarray(outcomes, dtype=float)
    resampled = rng.choice(data, size=(draws, len(data)), replace=True).mean(axis=1)
    return (float(np.percentile(resampled, 2.5)), float(np.percentile(resampled, 97.5)))


def bootstrap_difference_interval(
    left: list[bool], right: list[bool], draws: int = 10000, seed: int = 20260804
) -> tuple[float, float]:
    """Paired interval for (left - right) landing rate, resampling cells together.

    Paired because both arms are scored on the same cells; resampling them
    independently would discard that and overstate the uncertainty.
    """

    if not left or len(left) != len(right):
        return (0.0, 0.0)
    rng = np.random.default_rng(seed)
    a, b = np.asarray(left, dtype=float), np.asarray(right, dtype=float)
    idx = rng.integers(0, len(a), size=(draws, len(a)))
    diffs = a[idx].mean(axis=1) - b[idx].mean(axis=1)
    return (float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5)))


def summarise(records: list[dict[str, Any]], tolerance: float) -> dict[str, dict[str, Any]]:
    by_condition: dict[str, dict[str, Any]] = {}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[record.get("condition", "?")].append(record)

    for condition, group in sorted(grouped.items()):
        committed = [r for r in group if r.get("committed_at") is not None]
        misses: dict[str, list[float]] = defaultdict(list)
        lands: dict[str, int] = defaultdict(int)
        outcomes: dict[str, list[bool]] = defaultdict(list)
        for record in committed:
            distances = miss_distances(record)
            if distances is None:
                continue
            for arm, distance in distances.items():
                misses[arm].append(distance)
                landed = distance <= tolerance
                lands[arm] += int(landed)
                outcomes[arm].append(bool(landed))

        by_condition[condition] = {
            "cells": len(group),
            "committed": len(committed),
            "invalid": sum(1 for r in group if not r.get("valid", False)),
            "gate_fire_rate": (
                sum(r.get("gate_fire_rate", 0.0) for r in group) / len(group) if group else 0.0
            ),
            "d_estimated_rate": (
                sum(1 for r in committed if r.get("d_estimated")) / len(committed)
                if committed
                else 0.0
            ),
            "median_miss_mm": {
                arm: sorted(values)[len(values) // 2] * 1000.0
                for arm, values in misses.items()
                if values
            },
            "land_rate": {
                arm: lands[arm] / len(misses[arm]) for arm in misses if misses[arm]
            },
            "land_rate_ci": {
                arm: bootstrap_rate_interval(outcomes[arm]) for arm in outcomes if outcomes[arm]
            },
            "d_minus_b_ci": (
                bootstrap_difference_interval(outcomes["D"], outcomes["B"])
                if outcomes.get("D") and outcomes.get("B")
                else None
            ),
        }

        # Conditional on arm D having engaged. Preregistered as a secondary
        # estimate so it cannot be introduced after seeing the marginal one;
        # where arm D declines it is identical to arm B by construction, which
        # dilutes the marginal figure without saying anything about the model.
        engaged = [r for r in committed if r.get("d_estimated")]
        cond_misses: dict[str, list[float]] = defaultdict(list)
        cond_lands: dict[str, int] = defaultdict(int)
        for record in engaged:
            distances = miss_distances(record)
            if distances is None:
                continue
            for arm, distance in distances.items():
                cond_misses[arm].append(distance)
                cond_lands[arm] += int(distance <= tolerance)
        by_condition[condition]["engaged_cells"] = len(engaged)
        by_condition[condition]["land_rate_engaged"] = {
            arm: cond_lands[arm] / len(cond_misses[arm])
            for arm in cond_misses
            if cond_misses[arm]
        }
    return by_condition


def render(summary: dict[str, dict[str, Any]], tolerance: float) -> str:
    lines = [
        f"Paper 003 pilot summary - CALIBRATION ONLY, excluded from confirmatory evidence",
        f"tolerance {tolerance * 1000:.0f} mm",
        "",
        f"{'condition':<10}{'cells':>6}{'commit':>7}{'gate':>7}{'estD':>6}"
        f"{'  median miss (mm)':<34}{'  land rate':<28}",
        "-" * 98,
    ]
    for condition, stats in summary.items():
        miss = stats["median_miss_mm"]
        land = stats["land_rate"]
        miss_text = " ".join(f"{a}={miss[a]:6.1f}" for a in ("B", "C", "D") if a in miss)
        land_text = " ".join(f"{a}={land[a]:.2f}" for a in ("B", "C", "D", "D_oracle") if a in land)
        lines.append(
            f"{condition:<10}{stats['cells']:>6}{stats['committed']:>7}"
            f"{stats['gate_fire_rate']:>7.2f}{stats['d_estimated_rate']:>6.2f}"
            f"  {miss_text:<32}  {land_text:<26}"
        )
        if stats["invalid"]:
            lines.append(f"{'':<10}  ! {stats['invalid']} invalid cell(s)")

    # Preregistered as a secondary estimate, so it is printed every time rather
    # than computed by hand once the marginal figure looks disappointing. Where
    # arm D declines it is identical to arm B by construction, which dilutes the
    # marginal rate without saying anything about the model.
    # Point estimates alone invite over-reading, especially at pilot sample
    # sizes. The preregistration requires intervals, so they are printed here
    # rather than computed only when someone asks.
    lines += ["", "95% bootstrap intervals (10,000 draws, cells resampled)", "-" * 98]
    for condition, stats in summary.items():
        ci = stats.get("land_rate_ci", {})
        if not ci:
            continue
        text = " ".join(
            f"{a}=[{ci[a][0]:.2f},{ci[a][1]:.2f}]" for a in ("B", "C", "D") if a in ci
        )
        lines.append(f"{condition:<10}{text}")
        diff = stats.get("d_minus_b_ci")
        if diff:
            crosses = diff[0] <= 0.0 <= diff[1]
            note = "includes zero" if crosses else "excludes zero"
            lines.append(
                f"{'':<10}D-B paired = [{diff[0]:+.2f}, {diff[1]:+.2f}]   {note}"
            )

    lines += ["", "conditional on arm D engaging (secondary, preregistered)", "-" * 98]
    for condition, stats in summary.items():
        engaged = stats.get("engaged_cells", 0)
        if not engaged:
            lines.append(f"{condition:<10}  arm D never engaged")
            continue
        land = stats.get("land_rate_engaged", {})
        text = " ".join(f"{a}={land[a]:.2f}" for a in ("B", "C", "D") if a in land)
        lines.append(
            f"{condition:<10}{engaged:>4}/{stats['committed']} committed   {text}"
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="result directories or JSON files")
    parser.add_argument("--tolerance", type=float, default=0.020,
                        help="metres; the task family's established 20 mm criterion")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    args = parser.parse_args()

    records = load_records(args.paths)
    if not records:
        raise SystemExit("no pilot records found")

    summary = summarise(records, args.tolerance)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(render(summary, args.tolerance))
        print(f"\n{len(records)} record(s) read")


if __name__ == "__main__":
    main()
