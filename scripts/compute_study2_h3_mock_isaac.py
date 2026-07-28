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

try:
    from scripts.study2_dream_curriculum.mock_reach import MockOutcome, cf_margin  # noqa: E402
except ImportError:
    cf_margin = None  # type: ignore
    MockOutcome = None  # type: ignore


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


def _seed_cf_margin(cont: dict, repl: dict, tol: float = 0.02) -> float:
    if cf_margin is None or MockOutcome is None:
        informative = (not cont.get("successful_resolution", False)) and repl.get(
            "successful_resolution", False
        )
        return 1.0 if informative else 0.0
    outcomes = {
        "CONTINUE": MockOutcome(
            response="CONTINUE",
            successful_resolution=bool(cont.get("successful_resolution", False)),
            final_distance_m=float(cont.get("final_distance_m", cont.get("final_dist_m", 1.0))),
            forbidden_violation=bool(cont.get("forbidden_violation", False)),
        ),
        "REPLAN": MockOutcome(
            response="REPLAN",
            successful_resolution=bool(repl.get("successful_resolution", False)),
            final_distance_m=float(repl.get("final_distance_m", repl.get("final_dist_m", 1.0))),
            forbidden_violation=bool(repl.get("forbidden_violation", False)),
        ),
    }
    return cf_margin(outcomes, tol=tol)


def isaac_scores_from_records(records: list[dict], tol: float = 0.02) -> tuple[float | None, bool | None]:
    """Return (continuous median margin, binary majority informative)."""
    by_resp: dict[str, list[dict]] = {}
    for r in records:
        if "response" not in r:
            continue
        by_resp.setdefault(r["response"], []).append(r)

    cont = by_resp.get("CONTINUE", [])
    repl = by_resp.get("REPLAN_d0") or by_resp.get("REPLAN") or []
    if not cont or not repl:
        return None, None

    cont_by = {r["seed"]: r for r in cont}
    repl_by = {r["seed"]: r for r in repl}
    margins: list[float] = []
    flags: list[bool] = []
    for s in cont_by:
        if s not in repl_by:
            continue
        m = _seed_cf_margin(cont_by[s], repl_by[s], tol=tol)
        margins.append(m)
        flags.append(m >= 0.5)

    if not margins:
        return None, None
    margins.sort()
    mid = len(margins) // 2
    median_margin = (
        margins[mid]
        if len(margins) % 2 == 1
        else (margins[mid - 1] + margins[mid]) / 2.0
    )
    binary = sum(flags) >= (len(flags) + 1) // 2
    return float(median_margin), bool(binary)


def _bootstrap_spearman_ci(
    x: list[float], y: list[float], n_boot: int = 2000, seed: int = 20260728
) -> tuple[float | None, float | None]:
    if len(x) < 3:
        return None, None
    rng = __import__("random").Random(seed)
    n = len(x)
    rhos: list[float] = []
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        bx = [x[i] for i in idx]
        by = [y[i] for i in idx]
        r, reason = _spearman(bx, by)
        if r is not None and reason == "ok":
            rhos.append(r)
    if len(rhos) < 100:
        return None, None
    rhos.sort()
    return rhos[int(0.025 * len(rhos))], rhos[int(0.975 * len(rhos)) - 1]


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
                "mock_score": float(s.get("mock_score", 0.0)),
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
                    "mock_score": float(rec.get("mock_score", rec.get("mock_score_median", 0.0))),
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
    parser.add_argument(
        "--continuous",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use continuous mock_score and Isaac CF margin (Paper 002 v0.3)",
    )
    parser.add_argument("--bootstrap-n", type=int, default=2000)
    parser.add_argument("--prereg-version", type=str, default="v0.3")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--label", type=str, default="h3_mock_isaac_spearman")
    parser.add_argument("--date", type=str, default="")
    args = parser.parse_args()

    records_path = args.records.resolve()
    isaac_agg = args.isaac_aggregate.resolve() if args.isaac_aggregate else None
    out_path = args.out.resolve()
    specs_path = args.specs.resolve() if args.specs else None

    specs = load_specs(records_path, args.top_k, args.strategy, specs_path)
    isaac_by_id: dict[str, dict] = {}

    if isaac_agg and isaac_agg.exists():
        agg = json.loads(isaac_agg.read_text(encoding="utf-8"))
        for row in agg.get("specs", []):
            val = row.get("isaac_informative")
            cont_score = row.get("isaac_score")
            if val is None and "isaac_records" in row:
                cont_score, val = isaac_scores_from_records(row["isaac_records"])
            isaac_by_id[row["spec_id"]] = {
                "binary": None if val is None else int(bool(val)),
                "continuous": None if cont_score is None else float(cont_score),
            }
    elif args.isaac_all_informative:
        for s in specs:
            isaac_by_id[s["spec_id"]] = {"binary": 1, "continuous": 1.0}
    else:
        parser.error("Provide --isaac-aggregate or --isaac-all-informative")

    rows: list[dict] = []
    for s in specs:
        isaac_entry = isaac_by_id.get(s["spec_id"], {})
        rows.append(
            {
                **s,
                "isaac_informative": isaac_entry.get("binary"),
                "isaac_score": isaac_entry.get("continuous"),
            }
        )

    analyzed = [r for r in rows if r["isaac_informative"] is not None]
    if args.continuous:
        mock_vals = [
            float(r.get("mock_score", r["mock_informative"])) for r in analyzed
        ]
        isaac_vals = [
            float(r["isaac_score"] if r["isaac_score"] is not None else r["isaac_informative"])
            for r in analyzed
        ]
    else:
        mock_vals = [float(r["mock_informative"]) for r in analyzed]
        isaac_vals = [float(r["isaac_informative"]) for r in analyzed]

    rho, reason = _spearman(mock_vals, isaac_vals)
    ci_lo, ci_hi = _bootstrap_spearman_ci(
        mock_vals, isaac_vals, n_boot=args.bootstrap_n
    )
    h1_pass = (
        rho is not None
        and rho >= args.threshold
        and ci_lo is not None
        and ci_lo > 0.25
    )

    # H2 tier enrichment
    tier_stats: dict[str, dict] = {}
    for tier in ("top", "bottom"):
        sub = [r for r in analyzed if r.get("selection_tier") == tier]
        if not sub:
            continue
        informative = sum(int(r["isaac_informative"]) for r in sub)
        n = len(sub)
        tier_stats[tier] = {
            "n": n,
            "informative": informative,
            "ir": informative / n if n else 0.0,
        }
    h2_pass = False
    binomial_p_top: float | None = None
    if "top" in tier_stats and "bottom" in tier_stats:
        top = tier_stats["top"]
        bottom = tier_stats["bottom"]
        h2_pass = (
            top["ir"] >= 0.80
            and bottom["ir"] <= 0.50
            and (top["ir"] - bottom["ir"]) >= 0.40
        )
        # Supporting exact binomial (one-sided H0: p <= 0.5) — not a pass criterion
        k = top["informative"]
        n = top["n"]
        if n > 0:
            from math import comb

            binomial_p_top = sum(
                comb(n, i) * (0.5**n) for i in range(k, n + 1)
            )

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

    from datetime import date

    h3_pass = h1_pass  # legacy field name
    payload = {
        "tier": "confirmatory",
        "prereg_version": args.prereg_version,
        "label": args.label,
        "date": args.date or date.today().isoformat(),
        "hypothesis": "H1: continuous mock rank vs Isaac CF margin (rho >= 0.5, CI_lo > 0.25)",
        "score_type": "continuous" if args.continuous else "binary",
        "mock_records": _repo_rel(records_path),
        "isaac_source": _repo_rel(isaac_agg) if isaac_agg else "isaac_full_v0.1_ceiling_all_informative",
        "export_strategy": args.strategy if not specs_path else "from_specs_file",
        "top_k_per_dreamer": args.top_k,
        "n_specs_pooled": len(mock_vals),
        "spearman_rho": rho,
        "spearman_reason": reason,
        "bootstrap_ci_95": [ci_lo, ci_hi],
        "h1_pass": h1_pass,
        "h2_pass": h2_pass,
        "h2_binomial_p_top_one_sided": binomial_p_top,
        "h2_binomial_supporting_only": True,
        "tier_stats": tier_stats,
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

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "spearman_rho": rho,
                "bootstrap_ci_95": [ci_lo, ci_hi],
                "h1_pass": h1_pass,
                "h2_pass": h2_pass,
                "reason": reason,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
