#!/usr/bin/env python3
"""Merge per-spec Isaac 001A runs into Study2 Phase 1 aggregate."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def load_isaac_results(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "records" in data:
        return list(data["records"])
    if isinstance(data, list):
        return data
    raise ValueError(f"Unexpected format: {path}")


def informative_from_records(records: list[dict]) -> bool | None:
    by_resp: dict[str, list[dict]] = {}
    for r in records:
        if "response" not in r:
            continue
        by_resp.setdefault(r["response"], []).append(r)

    def _one_seed(cont: dict, repl: dict) -> bool:
        return (not cont.get("successful_resolution", False)) and repl.get(
            "successful_resolution", False
        )

    cont_list = by_resp.get("CONTINUE", [])
    repl_list = by_resp.get("REPLAN_d0") or by_resp.get("REPLAN") or []
    if not cont_list or not repl_list:
        return None

    if len(cont_list) == len(repl_list) == 1:
        return _one_seed(cont_list[0], repl_list[0])

    cont_by_seed = {r["seed"]: r for r in cont_list}
    repl_by_seed = {r["seed"]: r for r in repl_list}
    flags = [
        _one_seed(cont_by_seed[s], repl_by_seed[s])
        for s in cont_by_seed
        if s in repl_by_seed
    ]
    if not flags:
        return None
    return sum(flags) >= (len(flags) + 1) // 2


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge Study2 Isaac results")
    parser.add_argument("--specs", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--git-commit", type=str, default="unknown")
    args = parser.parse_args()

    spec_pack = json.loads(args.specs.read_text(encoding="utf-8"))
    merged: list[dict] = []
    by_dreamer: dict[str, list[bool]] = {}

    for spec in spec_pack["specs"]:
        spec_id = spec["spec_id"]
        result_path = args.results_dir / spec_id / "isaac_results.json"
        if not result_path.exists():
            merged.append({**spec, "isaac_missing": True})
            continue
        records = load_isaac_results(result_path)
        info = informative_from_records(records)
        dreamer = spec["dreamer"]
        by_dreamer.setdefault(dreamer, [])
        if info is not None:
            by_dreamer[dreamer].append(info)
        merged.append(
            {
                **spec,
                "isaac_informative": info,
                "isaac_records": records,
                "result_path": str(result_path),
            }
        )

    summary = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": args.git_commit,
        "prereg": spec_pack.get("prereg"),
        "mock_run_id": spec_pack.get("mock_run_id"),
        "by_dreamer": {
            d: {
                "n": len(flags),
                "informative_count": sum(1 for f in flags if f),
                "informative_rate": sum(1 for f in flags if f) / max(len(flags), 1),
            }
            for d, flags in by_dreamer.items()
        },
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "isaac_aggregate.json").write_text(
        json.dumps({"summary": summary, "specs": merged}, indent=2),
        encoding="utf-8",
    )
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (args.out_dir / "run_manifest.json").write_text(
        json.dumps(
            {
                **summary,
                "specs_file": str(args.specs),
                "results_dir": str(args.results_dir),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps(summary["by_dreamer"], indent=2))


if __name__ == "__main__":
    main()
