# After the Spill Research Program v2.0

> **Core question:** How should unexpected experience control the scope of change in embodied systems?

## Mission

Develop embodied intelligence that selects the **smallest sufficient change** needed to restore competent interaction with reality.

## Change-decision framework

Given experience `e`, evidence `z`, and available operators `C`, select:

```text
c* = argmin_c [task loss + change cost + risk + future cost]
```

Operators:

- **Preserve** — record the episode without permanent adaptation.
- **Recover** — restore behavior without changing the model.
- **Repair** — update parameters within the current representation.
- **Expand** — add a prepared mode, relation, entity, or constraint when repair is insufficient.
- **Coordinate** — recruit capabilities when consequences exceed one controller.

## Program map

| Work | Decision studied | Current role |
| --- | --- | --- |
| Paper 001 | Which response restores execution at the same mismatch state? | Recoverability ruler |
| Paper 002 | When is parameter repair insufficient? | Failure-conditioned model adequacy |
| Paper 003 | Which representational operator is missing? | Mode/relation discrimination and capability expansion |
| Paper 004 | How much should an experience change the system? | Recovery-conditioned experience disposition |
| Paper 005 | How should multi-relation consequences be contained and resolved? | Model-inadequacy-aware recovery orchestration |

Capability recruitment is a Paper 005 mechanism, not a separate paper. Ecosystem adaptation remains a long-term open problem.

## Foundation documents

- D000 — Mathematical foundation
- D001 — Claim and novelty audit
- D002 — Literature matrix
- D003 — Terminology
- D004 — Formal definitions
- D005 — Unified evaluation protocol
- D006 — Research roadmap

## Shared evaluation

Every study should measure not only performance, but whether the **amount of change was justified**:

- recovery closure
- unnecessary and missed revision
- revision latency
- nominal regression
- cumulative task regret
- unresolved relation burden

## Claim boundary

This program does not claim a new field, universal resilience, arbitrary causal discovery, or a solution to continual learning. It proposes a unified decision framework for experience-induced change in embodied systems, initially tested in controlled Physical AI settings.

## Governing principle

> Intelligence is the ability to determine the smallest sufficient change after unexpected experience.

*Living document · 2026-08-04*