"""VESSL/RunPod orchestrator for the EXP-SURG-003 model-order experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


EP2_ARMS = (
    "A_ZERO_ORDER_FROZEN",
    "B_L1_ZERO_ORDER",
    "C_L3_CONSTANT_VELOCITY",
    "D_ORACLE_VELOCITY",
)
RETENTION_ARMS = ("B_L1_ZERO_ORDER", "C_L3_CONSTANT_VELOCITY")
EXECUTION_ISOLATION = "fresh_isaac_process_per_seed_arm_condition"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stream_command(command: list[str], cwd: Path, log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[RUN] {' '.join(command)}", flush=True)
    with log_path.open("a", encoding="utf-8") as log:
        log.write(f"\n[RUN] {' '.join(command)}\n")
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=os.environ.copy(),
        )
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="", flush=True)
            log.write(line)
        return_code = process.wait()
    if return_code != 0:
        raise subprocess.CalledProcessError(return_code, command)


def _complete(arm_dir: Path) -> bool:
    result = arm_dir / "isaac_drift_results.json"
    trajectory = arm_dir / "isaac_drift_trajectories.json"
    return result.is_file() and trajectory.is_file()


def _model_args(config: dict[str, Any]) -> list[str]:
    models = config["models"]
    gate = config["gate"]
    return [
        "--prediction-horizon",
        str(config["shared"]["prediction_horizon_steps"]),
        "--a-position-alpha",
        str(models["A_ZERO_ORDER_FROZEN"]["position_alpha"]),
        "--l1-position-alpha",
        str(models["B_L1_ZERO_ORDER"]["position_alpha"]),
        "--l3-position-alpha",
        str(models["C_L3_CONSTANT_VELOCITY"]["position_alpha"]),
        "--l3-velocity-alpha",
        str(models["C_L3_CONSTANT_VELOCITY"]["velocity_alpha"]),
        "--gate-window",
        str(gate["window"]),
        "--gate-min-deltas",
        str(gate["min_deltas"]),
        "--gate-speed-floor",
        str(gate["speed_floor_m_per_step"]),
        "--gate-min-active-fraction",
        str(gate["min_active_fraction"]),
        "--gate-min-directional-consistency",
        str(gate["min_directional_consistency"]),
        "--gate-min-cv-improvement",
        str(gate["min_cv_error_improvement"]),
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=Path("/workspace/research-os"))
    parser.add_argument("--isaaclab-path", type=Path, default=Path("/workspace/IsaacLab"))
    parser.add_argument("--orbit-surgical-path", type=Path, default=Path("/workspace/orbit-surgical"))
    parser.add_argument("--skip-bootstrap", action="store_true")
    parser.add_argument("--skip-zero-agent", action="store_true")
    parser.add_argument("--disable-fabric", action="store_true")
    args = parser.parse_args()

    repo = args.repo.resolve()
    config_path = args.config.resolve()
    out_dir = args.out_dir.resolve()
    isaaclab_sh = (args.isaaclab_path / "isaaclab.sh").resolve()
    if not config_path.is_file():
        raise FileNotFoundError(config_path)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("execution_isolation") != EXECUTION_ISOLATION:
        raise ValueError(
            "model-order runs require fresh process isolation for every "
            "seed-arm-condition cell"
        )
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "orchestrator_stdout.log"

    if not args.skip_bootstrap:
        _stream_command(
            ["bash", str(repo / "scripts" / "bootstrap_orbit_surgical_runpod.sh")],
            repo,
            log_path,
        )
    if not isaaclab_sh.is_file():
        raise FileNotFoundError(f"isaaclab.sh not found: {isaaclab_sh}")

    os.environ["OMNI_KIT_ALLOW_ROOT"] = "1"
    os.environ["IsaacLab_PATH"] = str(args.isaaclab_path)
    if not args.skip_zero_agent:
        _stream_command(
            [
                str(isaaclab_sh),
                "-p",
                "source/standalone/environments/zero_agent.py",
                "--task",
                config["task"],
                "--num_envs",
                "1",
                "--headless",
            ],
            args.orbit_surgical_path,
            log_path,
        )

    _stream_command(
        [
            str(isaaclab_sh),
            "-p",
            str(repo / "scripts" / "test_exp_surg_003_target_dynamics.py"),
        ],
        repo,
        log_path,
    )

    git_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    git_commit = git_result.stdout.strip() if git_result.returncode == 0 else "unknown"
    (out_dir / "git_commit.txt").write_text(git_commit + "\n", encoding="utf-8")
    run_manifest = {
        "experiment_id": config["experiment_id"],
        "config_path": str(config_path),
        "config_sha256": _sha256(config_path),
        "git_commit": git_commit,
        "repo": str(repo),
        "isaaclab_path": str(args.isaaclab_path),
        "orbit_surgical_path": str(args.orbit_surgical_path),
        "execution_isolation": EXECUTION_ISOLATION,
    }
    (out_dir / "orchestration_manifest.json").write_text(
        json.dumps(run_manifest, indent=2), encoding="utf-8"
    )

    shared = config["shared"]
    common = [
        "--headless",
        "--task",
        config["task"],
        "--onset",
        str(shared["onset"]),
        "--tol-m",
        str(shared["success_tolerance_m"]),
        "--prefix-max-steps",
        str(shared["prefix_max_steps"]),
        "--prefix-stable-steps",
        str(shared["prefix_stable_steps"]),
        "--paired-start-tol-m",
        str(shared["paired_start_tolerance_m"]),
        "--gain",
        str(shared["gain"]),
        "--max-delta",
        str(shared["max_delta"]),
        "--experiment-id",
        config["experiment_id"],
    ] + _model_args(config)
    if args.disable_fabric:
        common.append("--disable_fabric")

    def run_arm(
        arm_dir: Path,
        seed: int,
        policy: str,
        target_mode: str,
        condition_id: str,
        vector: list[float],
        delay: int,
        duration: int,
    ) -> None:
        if _complete(arm_dir):
            print(f"[SKIP] complete: {arm_dir}", flush=True)
            return
        arm_dir.mkdir(parents=True, exist_ok=True)
        vector_arg = ",".join(str(value) for value in vector)
        max_steps = int(shared["onset"]) + delay + duration
        command = [
            str(isaaclab_sh),
            "-p",
            str(repo / "scripts" / "orbit_reach_drift.py"),
            *common,
            "--out-dir",
            str(arm_dir),
            "--seeds",
            str(seed),
            "--policy",
            policy,
            "--target-mode",
            target_mode,
            "--condition-id",
            condition_id,
            f"--drift-vector={vector_arg}",
            "--drift-delay",
            str(delay),
            "--drift-duration",
            str(duration),
            "--max-steps",
            str(max_steps),
        ]
        _stream_command(command, args.orbit_surgical_path, log_path)

    def run_ep2_isolated(arm_dir: Path, seed: int, policy: str) -> None:
        for condition in config["conditions"]:
            condition_id = str(condition["id"])
            run_arm(
                arm_dir / f"condition_{condition_id}",
                seed,
                policy,
                "persistent_drift",
                condition_id,
                condition["drift_vector_m_per_step"],
                int(condition["delay_steps"]),
                int(condition["duration_steps"]),
            )

    retention_steps = max(
        int(condition["delay_steps"]) + int(condition["duration_steps"])
        for condition in config["conditions"]
    )
    for seed in config["candidate_seeds"]:
        run_arm(
            out_dir / "eligibility" / f"seed_{seed}" / "STATIC_CONTROL",
            int(seed),
            "STATIC_CONTROL",
            "static",
            "ELIGIBILITY",
            [0.0, 0.0, 0.0],
            0,
            retention_steps,
        )

    selection_path = out_dir / "selection_manifest.json"
    if selection_path.is_file():
        existing = json.loads(selection_path.read_text(encoding="utf-8"))
        if existing.get("config_sha256") != _sha256(config_path):
            raise ValueError("existing selection manifest belongs to a different config")
        selected_seeds = [int(seed) for seed in existing["selected_seeds"]]
    else:
        selection_result = subprocess.run(
            [
                sys.executable,
                str(repo / "scripts" / "select_exp_surg_003_model_order_candidates.py"),
                "--repo",
                str(repo),
                "--config",
                str(config_path),
                "--out-dir",
                str(out_dir),
            ],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        )
        print(selection_result.stdout, end="", flush=True)
        selected_seeds = [
            int(value) for value in selection_result.stdout.strip().split(",") if value
        ]
    print(f"[LOCKED] selected seeds before treatment: {selected_seeds}", flush=True)

    for seed in selected_seeds:
        for arm in EP2_ARMS:
            run_ep2_isolated(out_dir / "ep2" / f"seed_{seed}" / arm, seed, arm)

    for seed in selected_seeds:
        for arm in RETENTION_ARMS:
            run_arm(
                out_dir / "retention" / f"seed_{seed}" / arm,
                seed,
                arm,
                "static",
                "STATIC_RETENTION",
                [0.0, 0.0, 0.0],
                0,
                retention_steps,
            )

    _stream_command(
        [
            str(isaaclab_sh),
            "-p",
            str(repo / "scripts" / "aggregate_exp_surg_003_model_order.py"),
            "--config",
            str(config_path),
            "--out-dir",
            str(out_dir),
        ],
        repo,
        log_path,
    )
    print(f"[OK] results: {out_dir / 'isaac_model_order_results.json'}")


if __name__ == "__main__":
    main()
