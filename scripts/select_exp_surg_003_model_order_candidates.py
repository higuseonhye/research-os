"""Lock static-eligible seeds before EXP-SURG-003 model-order treatments."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _git_commit(repo: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    config: dict[str, Any] = json.loads(args.config.read_text(encoding="utf-8"))
    candidates = [int(seed) for seed in config["candidate_seeds"]]
    required = int(config["required_eligible_seeds"])
    tolerance = float(config["shared"]["success_tolerance_m"])
    evaluations = []
    eligible = []

    for seed in candidates:
        result_path = (
            args.out_dir
            / "eligibility"
            / f"seed_{seed}"
            / "STATIC_CONTROL"
            / "isaac_drift_results.json"
        )
        if not result_path.is_file():
            raise FileNotFoundError(f"missing static eligibility result: {result_path}")
        result = json.loads(result_path.read_text(encoding="utf-8"))
        preconditions = result.get("preconditions", [])
        records = result.get("records", [])
        if len(preconditions) != 1:
            raise ValueError(f"expected one precondition in {result_path}")
        precondition = preconditions[0]
        record = records[0] if records else None
        reasons = []
        if not precondition["prefix_ready"]:
            reasons.append(precondition.get("prefix_failure_reason") or "prefix_not_ready")
        if record is None:
            reasons.append("static_record_missing")
        else:
            if not record["successful_resolution"]:
                reasons.append("static_control_failure")
            if record["max_distance_m"] > tolerance:
                reasons.append("static_control_exceeded_tolerance")
            if record["unexpected_env_reset"]:
                reasons.append("unexpected_env_reset")
        is_eligible = not reasons
        if is_eligible:
            eligible.append(seed)
        evaluations.append(
            {
                "seed": seed,
                "eligible": is_eligible,
                "reasons": reasons,
                "prefix_steps": precondition["prefix_steps"],
                "prefix_final_distance_m": precondition["prefix_final_distance_m"],
                "reset_state_fingerprint": precondition["reset_state_fingerprint"],
                "branch_state_fingerprint": precondition["branch_state_fingerprint"],
                "static_final_distance_m": record["final_distance_m"] if record else None,
                "static_max_distance_m": record["max_distance_m"] if record else None,
            }
        )

    selected = eligible[:required]
    manifest = {
        "protocol": config.get(
            "selection_protocol",
            "static_control_first_fixed_order_quota_model_order_v0.2",
        ),
        "experiment_id": config["experiment_id"],
        "candidate_seeds": candidates,
        "required_eligible_seed_count": required,
        "eligible_seeds": eligible,
        "selected_seeds": selected,
        "selection_quota_met": len(selected) == required,
        "selection_locked_before_treatment": True,
        "eligibility_rate": len(eligible) / len(candidates),
        "eligibility_tolerance_m": tolerance,
        "candidate_evaluations": evaluations,
        "config_path": str(args.config),
        "config_sha256": _sha256(args.config),
        "git_commit": _git_commit(args.repo),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = args.out_dir / "selection_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    if not manifest["selection_quota_met"]:
        raise RuntimeError(
            f"only {len(selected)} eligible seeds found; {required} required"
        )
    print(",".join(str(seed) for seed in selected))


if __name__ == "__main__":
    main()
