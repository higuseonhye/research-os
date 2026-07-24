#!/usr/bin/env python3
"""Compute Study 2 H3: Spearman rho between mock and Isaac per-spec informative flags."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _repo_rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO.resolve()))
    except ValueError:
        return str(path.resolve())
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.export_study2_isaac_specs import select_top_bottom, select_top_k  # noqa: E402


def _spearman(x: list[float], y: list[float]) -> tuple[float | None, str]:
    n = len(x)
    if n < 2:
        return None, "n<2"
    if len(set(x)) <= 1 or len(set(y)) <= 1:
        return None, "zero_variance"

    def ranks(vals: list[float]) -> list[float]:
        order = sorted(range(n), key=lambda i: vals[i])
        r = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and vals[order[j + 1]] == vals[order[i]]:
                j += 1
            avg = (i + j + 2) / 2.0
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r

    rx, ry = ranks(x), ranks(y)
    mx = sum(rx) / n
    my = sum(ry) / n
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    den_x = math.sqrt(sum((rx[i] - mx) ** 2 for i in range(n)))
    den_y = math.sqrt(sum((ry[i] - my) ** 2 for i in range(n)))
    if den_x == 0 or den_y == 0:
        return None, "zero_variance"
    return num / (den_x * den_y), "ok"


def informative_from_isaac_records(records: list[dict]) -> bool | None:
    by_resp: dict[str, list[dict]] = {}
    for r in records:
        if "response" not in r:
            continue
        by_resp.setdefault(r["response"], []).append(r)

    cont = by_resp.get("CONTINUE", [])
    repl = by_resp.get("REPLAN_d0") or by_resp.get("REPLAN") or []
    if not cont or not repl:
        return None

    if len(cont) == len(repl) == 1:
        return (not cont[0].get("successful_resolution", False)) and repl[0].get(
            "successful_resolution", False
        )

    cont_by = {r["seed"]: r for r in cont}
    repl_by = {r["seed"]: r for r in repl}
    flags = [
        (not cont_by[s].get("successful_resolution", False))
        and repl_by[s].get("successful_resolution", False)
        for s in cont_by
        if s in repl_by
    ]
    if not flags:
        return None
    return sum(flags) >= (len(flags) + 1) // 2


def load_specs(
    records_path: Path,
    top_k: int,
    strategy: str = "top_k",
    specs_file: Path | None = None,
) -> list[dict]:
    if specs_file and specs_file.exists():
        pack = json.loads(specs_file.read_text(encoding="utf-8"))
        return [
            {
                "spec_id": s["spec_id"],
                "dreamer": s["dreamer"],
                "selection_tier": s.get("selection_tier", "top"),
                "shift_m": s["shift_m"],
                "onset_step": s["onset_step"],
                "mock_informative": int(bool(s.get("mock_informative", False))),
            }
            for s in pack["specs"]
        ]

    raw = json.loads(records_path.read_text(encoding="utf-8"))
    specs: list[dict] = []
    sid = 0
    for dreamer in ("gaussian", "diffusion"):
        if strategy == "top_bottom":
            selected = select_top_bottom(raw[dreamer], top_k)
        else:
            selected = [(rec, "top") for rec in select_top_k(raw[dreamer], top_k)]
        for rec, tier in selected:
            spec = rec["spec"]
            specs.append(
                {
                    "spec_id": f"{dreamer}_{sid:03d}",
                    "dreamer": dreamer,
                    "selection_tier": tier,
                    "shift_m": spec["shift_m"],
                    "onset_step": spec["onset_step"],
                    "mock_informative": int(bool(rec.get("informative", False))),
                }
            )
            sid += 1
    return specs


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute Study2 H3 mock–Isaac Spearman rho")
    parser.add_argument(
        "--records",
        type=Path,
        default=REPO
        / "experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/mock_smoke_v0.2/records_seed43.json",
    )
    parser.add_argument(
        "--isaac-aggregate",
        type=Path,
        default=None,
        help="isaac_aggregate.json from pod (optional)",
    )
    parser.add_argument(
        "--isaac-all-informative",
        action="store_true",
        help="Use Isaac=1 for all top-k when aggregate missing (ceiling from isaac_full_v0.1 summary)",
    )
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--strategy",
        choices=("top_k", "top_bottom"),
        default="top_k",
    )
    parser.add_argument(
        "--specs",
        type=Path,
        default=None,
        help="isaac_specs.json from export (preferred after ablation run)",
    )
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    specs = load_specs(args.records, args.top_k, args.strategy, args.specs)
    isaac_by_id: dict[str, int | None] = {}

    if args.isaac_aggregate and args.isaac_aggregate.exists():
        agg = json.loads(args.isaac_aggregate.read_text(encoding="utf-8"))
        for row in agg.get("specs", []):
            val = row.get("isaac_informative")
            if val is None and "isaac_records" in row:
                val = informative_from_isaac_records(row["isaac_records"])
            isaac_by_id[row["spec_id"]] = None if val is None else int(bool(val))
    elif args.isaac_all_informative:
        for s in specs:
            isaac_by_id[s["spec_id"]] = 1
    else:
        parser.error("Provide --isaac-aggregate or --isaac-all-informative")

    rows: list[dict] = []
    for s in specs:
        isaac_val = isaac_by_id.get(s["spec_id"])
        rows.append({**s, "isaac_informative": isaac_val})

    mock_vals = [r["mock_informative"] for r in rows if r["isaac_informative"] is not None]
    isaac_vals = [r["isaac_informative"] for r in rows if r["isaac_informative"] is not None]

    rho, reason = _spearman([float(v) for v in mock_vals], [float(v) for v in isaac_vals])

    by_dreamer: dict[str, dict] = {}
    for dreamer in ("gaussian", "diffusion"):
        sub = [r for r in rows if r["dreamer"] == dreamer and r["isaac_informative"] is not None]
        m = [float(r["mock_informative"]) for r in sub]
        i = [float(r["isaac_informative"]) for r in sub]
        drho, dreason = _spearman(m, i)
        by_dreamer[dreamer] = {
            "n": len(sub),
            "mock_informative": m,
            "isaac_informative": i,
            "spearman_rho": drho,
            "reason": dreason,
        }

    h3_pass = rho is not None and rho >= args.threshold
    payload = {
        "tier": "B",
        "label": "h3_mock_isaac_spearman_v0.1",
        "date": "2026-07-23",
        "hypothesis": "H3: mock per-spec informative rank correlates with Isaac (rho >= 0.5)",
        "mock_records": str(args.records.relative_to(REPO)),
        "isaac_source": str(args.isaac_aggregate) if args.isaac_aggregate else "isaac_full_v0.1_ceiling_all_informative",
        "export_strategy": args.strategy if not args.specs else "from_specs_file",
        "top_k_per_dreamer": args.top_k,
        "n_specs_pooled": len(mock_vals),
        "spearman_rho": rho,
        "spearman_reason": reason,
        "h3_pass": h3_pass,
        "threshold": args.threshold,
        "by_dreamer": by_dreamer,
        "per_spec": rows,
        "interpretation": (
            "Top-k selection filters mock-informative specs; Isaac top-k ran at ceiling (5/5). "
            "Constant series → rho undefined → H3 not supported by current protocol."
            if reason == "zero_variance"
            else ""
        ),
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"spearman_rho": rho, "h3_pass": h3_pass, "reason": reason}, indent=2))


if __name__ == "__main__":
    main()
