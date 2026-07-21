"""Agentic curriculum planner — rule-based v0.1 + JSON file hook for LLM output."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scripts.study2_dream_curriculum.perturbation_spec import load_taxonomy


@dataclass(frozen=True)
class CurriculumGoal:
    episode: int
    family: str
    severity: str
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "episode": self.episode,
            "family": self.family,
            "severity": self.severity,
            "rationale": self.rationale,
        }


class AgenticCurriculumPlanner:
    """Plans which perturbation families to elicit — agentic hook via JSON file."""

    def __init__(self, repo_root: Path, cfg: dict[str, Any]) -> None:
        self.repo_root = repo_root
        self.cfg = cfg
        self.taxonomy = load_taxonomy(repo_root, cfg["taxonomy_path"])

    def plan_rule(self, n_episodes: int) -> list[CurriculumGoal]:
        ac = self.cfg["agent"]["rule"]
        families = list(ac["families"])
        severities = list(ac["severity_cycle"])
        goals: list[CurriculumGoal] = []
        for i in range(n_episodes):
            fam = families[i % len(families)]
            sev = severities[i % len(severities)]
            gen = self.taxonomy.get("generator_families", {}).get(fam, {})
            exc = gen.get("exception_type", "unknown")
            goals.append(
                CurriculumGoal(
                    episode=i,
                    family=fam,
                    severity=sev,
                    rationale=f"rule cycle · exception_type={exc} · elicit informative S",
                )
            )
        return goals

    def plan_from_json(self, path: Path) -> list[CurriculumGoal]:
        raw = json.loads(path.read_text(encoding="utf-8"))
        goals: list[CurriculumGoal] = []
        for i, item in enumerate(raw):
            goals.append(
                CurriculumGoal(
                    episode=int(item.get("episode", i)),
                    family=str(item["family"]),
                    severity=str(item["severity"]),
                    rationale=str(item.get("rationale", "agent json")),
                )
            )
        return goals

    def plan(self, n_episodes: int, agent_mode: str, json_path: Path | None) -> list[CurriculumGoal]:
        if agent_mode == "rule":
            return self.plan_rule(n_episodes)
        if agent_mode == "json-file":
            if json_path is None:
                raise ValueError("--agent json-file requires --agent-json PATH")
            return self.plan_from_json(json_path)
        raise ValueError(f"Unknown agent mode: {agent_mode}")


def default_agent_prompt(n_episodes: int, taxonomy_path: str) -> str:
    return f"""Design a failure-eliciting curriculum for surgical reach mock (EXP-SURG-002).

Read generator_families from: {taxonomy_path}

Output JSON array of {n_episodes} objects:
[
  {{"episode": 0, "family": "target_shift", "severity": "mid", "rationale": "..."}},
  ...
]

Prioritize scenarios where CONTINUE likely fails but REPLAN succeeds (informative failures).
Families: target_shift, visual_occlusion, forbidden_region.
"""
