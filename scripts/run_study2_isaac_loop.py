#!/usr/bin/env python3
"""Run Isaac 001A counterfactual for each Study2 spec (with kit cleanup between runs)."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def cleanup_hung_runner() -> None:
    """Kill hung counterfactual python only.

    Do NOT pkill /isaac-sim/kit/kit — on Isaac Sim pods that kills the container
    base kit process and drops Web Terminal (RunPod sidecar).
    """
    subprocess.run(["pkill", "-9", "-f", "orbit_reach_study1a_counterfactual"], check=False)
    time.sleep(2)


def run_specs(
    *,
    specs_path: Path,
    per_spec_dir: Path,
    isaaclab: Path,
    orbit: Path,
    task: str,
    seeds: str,
    max_steps: str,
    onset_default: str,
    body_index: int,
    skip_existing: bool,
    sleep_s: float,
) -> list[str]:
    pack = json.loads(specs_path.read_text(encoding="utf-8"))
    failures: list[str] = []

    for spec in pack["specs"]:
        spec_id = spec["spec_id"]
        out = per_spec_dir / spec_id
        out.mkdir(parents=True, exist_ok=True)
        result_path = out / "isaac_results.json"
        if skip_existing and result_path.exists():
            print(f"[skip] {spec_id} (isaac_results.json exists)", flush=True)
            continue

        shift = spec["shift_m"]
        onset = int(spec.get("onset_step", onset_default))
        (out / "spec.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")

        cmd = [
            str(isaaclab / "isaaclab.sh"),
            "-p",
            str(REPO / "scripts/orbit_reach_study1a_counterfactual.py"),
            "--experiment-id",
            f"EXP-SURG-002-{spec_id}",
            "--task",
            task,
            "--num_envs",
            "1",
            "--seeds",
            seeds,
            "--onset",
            str(onset),
            "--max-steps",
            max_steps,
            "--shift-m",
            str(shift),
            "--body-index",
            str(body_index),
            "--include-continue",
            "--replan-delays",
            "0",
            "--out-dir",
            str(out),
            "--headless",
        ]
        print(f"[Isaac] {spec_id} shift={shift} onset={onset}", flush=True)
        env = os.environ.copy()
        env.setdefault("OMNI_KIT_ALLOW_ROOT", "1")
        env.setdefault("IsaacLab_PATH", str(isaaclab))
        rc = subprocess.run(cmd, cwd=str(orbit), env=env).returncode
        if rc != 0 or not result_path.exists():
            failures.append(spec_id)
            print(f"[WARN] Isaac failed for {spec_id} rc={rc}", flush=True)
            cleanup_hung_runner()
        if sleep_s > 0:
            time.sleep(sleep_s)

    return failures


def main() -> None:
    parser = argparse.ArgumentParser(description="Study2 Isaac per-spec loop")
    parser.add_argument("--specs", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--isaaclab", type=Path, default=Path("/workspace/IsaacLab"))
    parser.add_argument("--orbit", type=Path, default=Path("/workspace/orbit-surgical"))
    parser.add_argument("--task", default="Isaac-Reach-Dual-STAR-IK-Rel-Play-v0")
    parser.add_argument("--seeds", default="0,1,2,3,4")
    parser.add_argument("--max-steps", default="160")
    parser.add_argument("--onset-default", default="20")
    parser.add_argument("--body-index", type=int, default=13)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--sleep-s", type=float, default=2.0)
    args = parser.parse_args()

    failures = run_specs(
        specs_path=args.specs,
        per_spec_dir=args.results_dir,
        isaaclab=args.isaaclab,
        orbit=args.orbit,
        task=args.task,
        seeds=args.seeds,
        max_steps=args.max_steps,
        onset_default=args.onset_default,
        body_index=args.body_index,
        skip_existing=args.skip_existing,
        sleep_s=args.sleep_s,
    )
    if failures:
        print(f"[WARN] Failed specs ({len(failures)}): {failures}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
