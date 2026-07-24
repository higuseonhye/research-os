#!/usr/bin/env python3
"""Export top-k informative specs from Study2 mock run for Isaac Phase 1."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _load_records(path: Path) -> dict[str, list[dict]]:
    return json.loads(path.read_text(encoding="utf-8"))


def _spec_key(record: dict) -> tuple:
    spec = record["spec"]
    return (round(spec["shift_m"], 4), spec["onset_step"])


def _score(record: dict) -> tuple:
    informative = int(record.get("informative", False))
    spec = record["spec"]
    return (
        informative,
        spec["shift_m"],
        spec["onset_step"],
    )


def _dedupe_ranked(ranked: list[dict]) -> list[dict]:
    seen: set[tuple] = set()
    out: list[dict] = []
    for r in ranked:
        key = _spec_key(r)
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def select_top_k(records: list[dict], k: int) -> list[dict]:
    informative = [r for r in records if r.get("informative")]
    pool = informative if informative else records
    ranked = sorted(pool, key=_score, reverse=True)
    return _dedupe_ranked(ranked)[:k]


def select_top_bottom(records: list[dict], k: int) -> list[tuple[dict, str]]:
    """Top-k and bottom-k by mock informative rank (deduped by shift/onset)."""
    ranked = sorted(records, key=_score, reverse=True)
    deduped = _dedupe_ranked(ranked)
    top = deduped[:k]
    top_keys = {_spec_key(r) for r in top}
    bottom: list[dict] = []
    for r in reversed(deduped):
        if _spec_key(r) in top_keys:
            continue
        bottom.append(r)
        if len(bottom) >= k:
            break
    return [(r, "top") for r in top] + [(r, "bottom") for r in bottom]


def main() -> None:
    parser = argparse.ArgumentParser(description="Export Study2 Isaac spec pack")
    parser.add_argument("--records", type=Path, required=True, help="mock records.json")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--strategy",
        choices=("top_k", "top_bottom"),
        default="top_k",
        help="top_k=informative pool only (Phase 1); top_bottom=top-k + bottom-k per dreamer (selection ablation)",
    )
    parser.add_argument("--mock-run-id", type=str, default="")
    parser.add_argument(
        "--prereg",
        type=str,
        default="docs/stage2/study2_phase1_design_v0.1.md",
    )
    args = parser.parse_args()

    raw = _load_records(args.records)
    export: list[dict] = []
    spec_id = 0
    for dreamer, records in raw.items():
        if args.strategy == "top_bottom":
            selected = select_top_bottom(records, args.top_k)
        else:
            selected = [(rec, "top") for rec in select_top_k(records, args.top_k)]
        for rec, tier in selected:
            spec = rec["spec"]
            export.append(
                {
                    "spec_id": f"{dreamer}_{spec_id:03d}",
                    "dreamer": dreamer,
                    "selection_tier": tier,
                    "family": spec.get("family", "target_shift"),
                    "severity": spec.get("severity", "mid"),
                    "shift_m": spec["shift_m"],
                    "onset_step": spec["onset_step"],
                    "occlusion_gain": spec.get("occlusion_gain", 0.0),
                    "visibility_fraction": max(
                        0.05, 1.0 - float(spec.get("occlusion_gain", 0.0))
                    ),
                    "mock_seed": spec.get("seed", 0),
                    "mock_informative": bool(rec.get("informative", False)),
                    "goal": rec.get("goal", {}),
                }
            )
            spec_id += 1

    payload = {
        "prereg": args.prereg,
        "mock_run_id": args.mock_run_id,
        "export_strategy": args.strategy,
        "top_k": args.top_k,
        "specs": export,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {len(export)} specs → {args.out}")


if __name__ == "__main__":
    main()
