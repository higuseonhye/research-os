#!/usr/bin/env python3
"""EXP-SURG-002 — Dream curriculum sandbox (mock · desk-first).

Compare Gaussian vs diffusion dreaming + agentic curriculum on 001A mock reach.

Example:
  python scripts/run_study2_dream_curriculum_mock.py --dreamer diffusion --agent rule --episodes 32
  python scripts/run_study2_dream_curriculum_mock.py --compare --episodes 48
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.study2_dream_curriculum.agentic_planner import (  # noqa: E402
    AgenticCurriculumPlanner,
    default_agent_prompt,
)
from scripts.study2_dream_curriculum.dreamers import make_dreamer  # noqa: E402
from scripts.study2_dream_curriculum.mock_reach import evaluate_spec, is_informative  # noqa: E402
from scripts.study2_dream_curriculum.perturbation_spec import (  # noqa: E402
    PerturbationSpec,
    load_yaml,
)


DEFAULT_CFG = (
    REPO
    / "experiments/surgical_intelligence/exp_surg_002_dream_curriculum/config/sandbox_v0.1.yaml"
)


def _run_single(
    dreamer_name: str,
    agent_mode: str,
    n_episodes: int,
    cfg: dict,
    repo: Path,
    rng: np.random.Generator,
    agent_json: Path | None,
) -> dict:
    planner = AgenticCurriculumPlanner(repo, cfg)
    goals = planner.plan(n_episodes, agent_mode, agent_json)
    dreamer = make_dreamer(dreamer_name)

    # Bootstrap diffusion training data with rule+gaussian informative mining
    bootstrap = make_dreamer("gaussian")
    bootstrap_specs: list[PerturbationSpec] = []
    for g in goals[: min(16, len(goals))]:
        for spec in bootstrap.sample(4, g.family, g.severity, cfg, rng):
            if is_informative(evaluate_spec(spec)):
                bootstrap_specs.append(spec)
    dreamer.fit(bootstrap_specs, cfg)

    records: list[dict] = []
    informative = 0
    for goal in goals:
        spec = dreamer.sample(1, goal.family, goal.severity, cfg, rng)[0]
        outcomes = evaluate_spec(spec)
        info = is_informative(outcomes)
        informative += int(info)
        records.append(
            {
                "goal": goal.to_dict(),
                "spec": spec.to_dict(),
                "continue_success": bool(outcomes["CONTINUE"].successful_resolution),
                "replan_success": bool(outcomes["REPLAN"].successful_resolution),
                "informative": bool(info),
            }
        )

    params = np.array([[r["spec"]["shift_m"], r["spec"]["onset_step"], r["spec"]["occlusion_gain"]] for r in records])
    diversity = float(np.mean(np.std(params, axis=0))) if len(params) else 0.0

    return {
        "dreamer": dreamer_name,
        "agent": agent_mode,
        "n_episodes": n_episodes,
        "informative_count": informative,
        "informative_rate": informative / max(n_episodes, 1),
        "param_diversity": diversity,
        "bootstrap_informative": len(bootstrap_specs),
        "records": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="EXP-SURG-002 dream curriculum mock")
    parser.add_argument("--config", type=Path, default=DEFAULT_CFG)
    parser.add_argument("--dreamer", choices=["gaussian", "diffusion"], default="diffusion")
    parser.add_argument("--agent", choices=["rule", "json-file"], default="rule")
    parser.add_argument("--agent-json", type=Path, default=None)
    parser.add_argument("--episodes", type=int, default=32)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--compare", action="store_true", help="Run gaussian vs diffusion")
    parser.add_argument("--print-agent-prompt", action="store_true")
    parser.add_argument(
        "--promote-label",
        type=str,
        default="",
        help="Copy records.json to results/<label>/records_seed<seed>.json (Tier B promote)",
    )
    args = parser.parse_args()

    cfg = load_yaml(args.config)

    if args.print_agent_prompt:
        print(default_agent_prompt(args.episodes, cfg["taxonomy_path"]))
        return

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = REPO / cfg["output_root"] / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(args.seed)
    results: list[dict] = []

    if args.compare:
        for name in ("gaussian", "diffusion"):
            results.append(
                _run_single(name, args.agent, args.episodes, cfg, REPO, rng, args.agent_json)
            )
    else:
        results.append(
            _run_single(args.dreamer, args.agent, args.episodes, cfg, REPO, rng, args.agent_json)
        )

    summary = {
        "run_id": run_id,
        "config": str(args.config.relative_to(REPO)),
        "seed": args.seed,
        "compare": args.compare,
        "runs": [
            {k: v for k, v in r.items() if k != "records"}
            for r in results
        ],
    }

    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out_dir / "records.json").write_text(
        json.dumps({r["dreamer"]: r["records"] for r in results}, indent=2),
        encoding="utf-8",
    )

    if args.promote_label:
        promote_dir = (
            REPO
            / "experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results"
            / args.promote_label
        )
        promote_dir.mkdir(parents=True, exist_ok=True)
        dest = promote_dir / f"records_seed{args.seed}.json"
        dest.write_text((out_dir / "records.json").read_text(encoding="utf-8"), encoding="utf-8")
        (promote_dir / "summary.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8"
        )
        print(f"Promoted → {dest}")

    print(f"Wrote {out_dir / 'summary.json'}")
    for r in results:
        print(
            f"  [{r['dreamer']}] informative_rate={r['informative_rate']:.2f} "
            f"diversity={r['param_diversity']:.4f} bootstrap={r['bootstrap_informative']}"
        )


if __name__ == "__main__":
    main()
