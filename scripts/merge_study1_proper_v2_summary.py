#!/usr/bin/env python3
"""Merge Paper 001 proper v2.0 D1–D3 isaac_results → results/study1_proper_v2/summary.json."""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "experiments/surgical_intelligence/exp_surg_001_execute_or_defer/artifacts/study1_proper_v2"
OUT = ROOT / "experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1_proper_v2"

BLOCKS = {
    "d1": {"label": "no_occlusion_control", "rq": "RQ-P"},
    "d2": {"label": "b2_uq_inspired", "rq": "RQ-B"},
    "d3": {"label": "b3_situation_rule", "rq": "RQ-B"},
}


def load_records(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("records") or data.get("episodes") or [])


def aggregate(records: list[dict]) -> list[dict]:
    by_key: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in records:
        resp = str(r.get("response") or r.get("mode") or "UNKNOWN")
        cls = str(r.get("response_class") or r.get("class") or "")
        by_key[(resp, cls)].append(r)
    rows = []
    for (resp, cls), xs in sorted(by_key.items()):
        n = len(xs)
        succ = sum(1 for x in xs if x.get("successful_resolution"))
        viol = sum(1 for x in xs if x.get("forbidden_violation"))
        dists = [float(x["final_distance_m"]) for x in xs if "final_distance_m" in x]
        rows.append(
            {
                "response": resp,
                "class": cls or None,
                "n": n,
                "success_rate": succ / n if n else 0.0,
                "forbidden_violation_rate": viol / n if n else 0.0,
                "mean_final_distance_m": sum(dists) / len(dists) if dists else None,
            }
        )
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    block_summaries: dict[str, dict] = {}
    all_replay_ok = True

    for block, meta in BLOCKS.items():
        src = ART / block / "isaac_results.json"
        if not src.is_file():
            raise SystemExit(f"Missing {src}")
        records = load_records(src)
        replay_ok = all(r.get("branch_replay_ok", True) for r in records)
        all_replay_ok = all_replay_ok and replay_ok
        agg = aggregate(records)
        block_summaries[block] = {
            "block": block,
            "label": meta["label"],
            "sub_rq": meta["rq"],
            "n_records": len(records),
            "branch_replay_ok": replay_ok,
            "aggregate_by_mode": agg,
            "source": str(src.relative_to(ROOT)).replace("\\", "/"),
        }
        dest = OUT / block
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "isaac_results.json").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    d0_path = ROOT / "experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1_proper/summary.json"
    d0_ref = json.loads(d0_path.read_text(encoding="utf-8")) if d0_path.is_file() else None

    summary = {
        "tier": "C",
        "label": "study1_proper_v2.0",
        "experiment": "EXP-SURG-001 Phase C pre-reg v2.0 D1-D3",
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "prereg": "docs/paper1/phase_c_proper_run_prereg_v2.0.md",
        "d0_reference": "results/study1_proper/summary.json",
        "d0_primary_contrast": d0_ref.get("primary_contrast") if d0_ref else None,
        "blocks": block_summaries,
        "branch_replay_ok": all_replay_ok,
        "n_records_total": sum(b["n_records"] for b in block_summaries.values()),
    }
    out_path = OUT / "summary.json"
    out_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"[OK] wrote {out_path}")
    for block, bs in block_summaries.items():
        print(f"  {block}: n={bs['n_records']} replay_ok={bs['branch_replay_ok']}")


if __name__ == "__main__":
    main()
