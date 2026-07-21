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


def _score(record: dict) -> tuple:
    informative = int(record.get("informative", False))
    spec = record["spec"]
    return (
        informative,
        spec["shift_m"],
        spec["onset_step"],
    )


def select_top_k(records: list[dict], k: int) -> list[dict]:
    informative = [r for r in records if r.get("informative")]
    pool = informative if informative else records
    ranked = sorted(pool, key=_score, reverse=True)
    seen: set[tuple] = set()
    out: list[dict] = []
    for r in ranked:
        spec = r["spec"]
        key = (round(spec["shift_m"], 4), spec["onset_step"])
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
        if len(out) >= k:
            break
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Export Study2 Isaac spec pack")
    parser.add_argument("--records", type=Path, required=True, help="mock records.json")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--mock-run-id", type=str, default="")
    args = parser.parse_args()

    raw = _load_records(args.records)
    export: list[dict] = []
    spec_id = 0
    for dreamer, records in raw.items():
        for rec in select_top_k(records, args.top_k):
            spec = rec["spec"]
            export.append(
                {
                    "spec_id": f"{dreamer}_{spec_id:03d}",
                    "dreamer": dreamer,
                    "family": spec.get("family", "target_shift"),
                    "severity": spec.get("severity", "mid"),
                    "shift_m": spec["shift_m"],
                    "onset_step": spec["onset_step"],
                    "occlusion_gain": spec.get("occlusion_gain", 0.0),
                    "mock_seed": spec.get("seed", 0),
                    "mock_informative": bool(rec.get("informative", False)),
                    "goal": rec.get("goal", {}),
                }
            )
            spec_id += 1

    payload = {
        "prereg": "docs/stage2/study2_prereg_v0.1.md",
        "mock_run_id": args.mock_run_id,
        "top_k": args.top_k,
        "specs": export,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {len(export)} specs → {args.out}")


if __name__ == "__main__":
    main()
