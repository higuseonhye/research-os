#!/usr/bin/env python3
"""Run Isaac counterfactual for each Study2 spec (with kit cleanup between runs)."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def visibility_from_occlusion_gain(occlusion_gain: float) -> float:
    """Phase 2 alignment: mock gain_scale ↔ study1d visibility_fraction."""
    return max(0.05, 1.0 - float(occlusion_gain))


def cleanup_hung_runner(runner: str) -> None:
    """Kill hung counterfactual python only.

    Do NOT pkill /isaac-sim/kit/kit — on Isaac Sim pods that kills the container
    base kit process and drops Web Terminal (RunPod sidecar).
    """
    pattern = (
        "orbit_reach_study1d_counterfactual"
        if runner == "study1d"
        else "orbit_reach_study1a_counterfactual"
    )
    subprocess.run(["pkill", "-9", "-f", pattern], check=False)
    time.sleep(2)


def build_cmd(
    *,
    runner: str,
    spec: dict,
    spec_id: str,
    isaaclab: Path,
    orbit: Path,
    task: str,
    seeds: str,
    max_steps: str,
    onset_default: str,
    body_index: int,
    out: Path,
    replan_delay: int,
    occlusion_level: int,
) -> list[str]:
    shift = spec["shift_m"]
    onset = int(spec.get("onset_step", onset_default))
    base = [
        str(isaaclab / "isaaclab.sh"),
        "-p",
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
        "--out-dir",
        str(out),
        "--headless",
    ]
    if runner == "study1d":
        vis = spec.get("visibility_fraction")
        if vis is None:
            vis = visibility_from_occlusion_gain(spec.get("occlusion_gain", 0.0))
        script = REPO / "scripts/orbit_reach_study1d_counterfactual.py"
        return [
            base[0],
            base[1],
            str(script),
            *base[2:],
            "--replan-delay",
            str(replan_delay),
            "--occlusion-level",
            str(occlusion_level),
            "--visibility-fraction",
            str(vis),
            "--modes",
            "CONTINUE,REPLAN",
        ]
    script = REPO / "scripts/orbit_reach_study1a_counterfactual.py"
    return [
        base[0],
        base[1],
        str(script),
        *base[2:],
        "--include-continue",
        "--replan-delays",
        str(replan_delay),
    ]


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
    runner: str,
    replan_delay: int,
    occlusion_level: int,
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

        cmd = build_cmd(
            runner=runner,
            spec=spec,
            spec_id=spec_id,
            isaaclab=isaaclab,
            orbit=orbit,
            task=task,
            seeds=seeds,
            max_steps=max_steps,
            onset_default=onset_default,
            body_index=body_index,
            out=out,
            replan_delay=replan_delay,
            occlusion_level=occlusion_level,
        )
        if runner == "study1d":
            vis = spec.get("visibility_fraction")
            if vis is None:
                vis = visibility_from_occlusion_gain(spec.get("occlusion_gain", 0.0))
            print(
                f"[Isaac/study1d] {spec_id} shift={shift} onset={onset} vis={vis:.3f}",
                flush=True,
            )
        else:
            print(f"[Isaac/study1a] {spec_id} shift={shift} onset={onset}", flush=True)
        env = os.environ.copy()
        env.setdefault("OMNI_KIT_ALLOW_ROOT", "1")
        env.setdefault("IsaacLab_PATH", str(isaaclab))
        rc = subprocess.run(cmd, cwd=str(orbit), env=env).returncode
        if rc != 0 or not result_path.exists():
            failures.append(spec_id)
            print(f"[WARN] Isaac failed for {spec_id} rc={rc}", flush=True)
            cleanup_hung_runner(runner)
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
    parser.add_argument(
        "--runner",
        choices=("study1a", "study1d"),
        default=os.environ.get("STUDY2_RUNNER", "study1a"),
        help="study1a=Phase 1 shift-only; study1d=Phase 2 occlusion-aligned",
    )
    parser.add_argument("--replan-delay", type=int, default=0)
    parser.add_argument("--occlusion-level", type=int, default=1)
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
        runner=args.runner,
        replan_delay=args.replan_delay,
        occlusion_level=args.occlusion_level,
    )
    if failures:
        print(f"[WARN] Failed specs ({len(failures)}): {failures}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
