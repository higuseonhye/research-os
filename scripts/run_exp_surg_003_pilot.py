#!/usr/bin/env python3
"""EXP-SURG-003 mock pilot — Paper 002 WM expansion (no Isaac required).

Usage:
  python scripts/run_exp_surg_003_pilot.py --smoke
  python scripts/run_exp_surg_003_pilot.py --seeds 0,1,2,3,4 --arms A,B,C
  python scripts/run_exp_surg_003_pilot.py --config experiments/.../pilot_v0.1.yaml
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
for p in (str(REPO), str(SCRIPTS)):
    if p not in sys.path:
        sys.path.insert(0, p)

from wm_expansion.gate import GateThresholds  # noqa: E402
from wm_expansion.protocol import PilotConfig, run_pilot, write_pilot_artifacts  # noqa: E402

DEFAULT_CFG = (
    REPO
    / "experiments/surgical_intelligence/exp_surg_003_wm_expansion/config/pilot_v0.1.yaml"
)
DEFAULT_OUT = (
    REPO / "experiments/surgical_intelligence/exp_surg_003_wm_expansion/results/pilot_v0.1"
)


def load_yaml(path: Path) -> dict:
    try:
        import yaml
    except ImportError as exc:
        raise SystemExit("pip install pyyaml") from exc
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def cfg_from_yaml(data: dict) -> PilotConfig:
    gate = data.get("gate", {})
    pilot = data.get("pilot", {})
    return PilotConfig(
        max_steps=int(pilot.get("max_steps", 80)),
        pretrain_static_episodes=int(pilot.get("pretrain_static_episodes", 40)),
        pretrain_steps=int(pilot.get("pretrain_steps", 250)),
        repair_steps=int(pilot.get("repair_steps", 120)),
        expansion_steps=int(pilot.get("expansion_steps", 280)),
        K_repairs=int(pilot.get("K_repairs", 3)),
        prediction_horizon=int(pilot.get("prediction_horizon", 10)),
        gate=GateThresholds(
            tau_error=float(gate.get("tau_error", 0.015)),
            tau_autocorr=float(gate.get("tau_autocorr", 0.35)),
            tau_delta_nll=float(gate.get("tau_delta_nll", 0.002)),
            K_repairs=int(gate.get("K_repairs", 3)),
        ),
        device=str(pilot.get("device", "cpu")),
        seed=int(pilot.get("seed", 0)),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="EXP-SURG-003 mock pilot")
    parser.add_argument("--config", type=Path, default=DEFAULT_CFG)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--seeds", type=str, default="0,1,2,3,4")
    parser.add_argument("--arms", type=str, default="A,B,C")
    parser.add_argument("--smoke", action="store_true", help="Fast smoke: 2 seeds, reduced training")
    parser.add_argument("--device", type=str, default="")
    args = parser.parse_args()

    if args.config.exists():
        cfg = cfg_from_yaml(load_yaml(args.config))
    else:
        cfg = PilotConfig()

    if args.device:
        cfg.device = args.device

    if args.smoke:
        cfg.pretrain_static_episodes = 8
        cfg.pretrain_steps = 40
        cfg.repair_steps = 25
        cfg.expansion_steps = 50
        cfg.gate.tau_error = 0.008
        cfg.gate.tau_delta_nll = 0.0005
        seeds = [0, 1]
    else:
        seeds = [int(x.strip()) for x in args.seeds.split(",") if x.strip()]

    arms = [x.strip().upper() for x in args.arms.split(",") if x.strip()]

    print(f"[INFO] EXP-SURG-003 mock pilot arms={arms} seeds={seeds} device={cfg.device}", flush=True)
    payload = run_pilot(cfg, arms=arms, seeds=seeds)
    write_pilot_artifacts(args.out_dir, payload)

    print("[INFO] summary:", flush=True)
    for arm, stats in payload["summary"].items():
        print(f"  {arm}: {stats}", flush=True)
    print(f"[INFO] wrote {args.out_dir / 'summary.json'}", flush=True)


if __name__ == "__main__":
    main()
