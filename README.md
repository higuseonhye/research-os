# After the Spill

> **How should unexpected experience change an embodied system?**

Most AI research asks how systems should learn. This research program asks a
different question: **how much should a system change after reality contradicts
its current model?**

This repository is the public evidence surface for the **After the Spill
Research Program**: a long-lived program on decision-making after unexpected
experience in embodied systems.

## Core question

Unexpected experience can be noise, a recoverable disturbance, a sign that the
current representation is inadequate, or evidence that multiple recovery
operators must be coordinated. The central problem is deciding which one it is.

```text
Unexpected experience
  -> evidence
  -> change decision
  -> smallest sufficient operator
  -> closure test
```

The governing principle is:

> Intelligence chooses the smallest sufficient change.

That sentence is treated as a claim to audit, not a slogan to protect.

## Program structure

| Layer | Role |
| --- | --- |
| **Foundation documents** | Stable program constitution: definitions, audits, literature matrix, evaluation philosophy, and roadmap |
| **Research papers** | Experiments that test pieces of the foundation |
| **Research products** | Platforms that expose the program's hypotheses to real users, rollouts, and benchmarks |

Start with the program charter: [`docs/program/after_the_spill_v2.md`](docs/program/after_the_spill_v2.md).

## Foundation documents

| Document | Purpose |
| --- | --- |
| **D000 Mathematical Foundation** | Formal objects: experience, evidence, operator, closure, competence |
| **D001 Claim & Novelty Audit** | Why the program could be wrong; overlap with existing fields |
| **D002 Literature Matrix** | A shared reading table, not paper summaries |
| **D003 Terminology** | Recover, repair, restore, resume, replan, adapt, update, expand, revise, modify, transform |
| **D004 Formal Definitions** | Operational definitions used across papers and products |
| **D005 Evaluation Protocol** | Shared evidence standards and closure tests |
| **D006 Research Roadmap** | How Paper 001-005 contribute to the same question |

## Research papers

Each paper answers the same question with a different change operator.

| Paper | Role in the program | Status |
| --- | --- | --- |
| **Paper 001: Recoverability** | When is the post-mismatch state still recoverable? | Tier C complete |
| **Paper 002: Model Adequacy** | When should repair give way to model-order expansion? | Tier C complete |
| **Paper 003: Representation Expansion** | Does expansion open capability that repair cannot reach? | **Negative under real contact, and written up.** Paper 002's mode operator lands 0.957–1.000 of physical cells where the relational arm lands 0.174–0.583. [PDF](docs/paper003/paper003_manuscript_negative_v1.0.pdf) · [manuscript](docs/paper003/paper003_manuscript_negative_v1.0.md) · [prereg, closed](docs/paper003/paper003_prereg_v1.0.md#closure--what-the-pilot-returned-and-what-it-licenses) |
| **Paper 004: Experience Disposition** | Should an experience be ignored, stored, repaired from, or escalated? | Program-defined |
| **Paper 005: Recovery Orchestration** | How should multiple recovery operators be coordinated? | Program-defined |

Paper success is useful; program coherence is mandatory.

## Research products

| Product | Program role |
| --- | --- |
| **Robot Diff** | Compare embodied rollouts and surface differences that may imply model inadequacy |
| **Mismatch Lab** | Public specification for diff, replay, explanation, and benchmark workflows |
| **Evaluation Toolkit** | Shared tests for evidence, closure, and operator choice |
| **Benchmark** | Repeatable tasks where unexpected experience forces a change decision |

Products are not side effects of papers. They are platforms for testing the
program's claims in actual workflows.

## Operating rules

1. New ideas do not automatically become new papers. First ask whether they fit
   D000-D006 or an existing paper.
2. New terms are not introduced until existing terms fail.
3. Novelty is not asserted first. It is tabulated against existing fields.
4. Every paper answers the same core question; only the operator changes.
5. Rejected ideas are recorded, because subtraction is part of the method.

## Start here

| Surface | Link |
| --- | --- |
| Program charter | [`docs/program/after_the_spill_v2.md`](docs/program/after_the_spill_v2.md) |
| Program index | [`docs/program/README.md`](docs/program/README.md) |
| GitHub Pages | [`docs/index.md`](docs/index.md) |
| Mismatch Lab | [`docs/mismatch_lab/README.md`](docs/mismatch_lab/README.md) |
| Paper 001 | [`docs/paper1/README.md`](docs/paper1/README.md) |
| Paper 002 | [`docs/paper002/README.md`](docs/paper002/README.md) |
| Paper 003 | [`docs/paper003/README.md`](docs/paper003/README.md) |

## Boundary

This repository contains promoted public research evidence: program documents,
research questions, protocols, reproducible experiments, figures, and tiered
claims. It is not a private notebook, career diary, or strategy workspace.

Current evidence is controlled simulation evidence. The program does not yet
claim clinical deployment, autonomous structural self-improvement, hardware
transfer, or a complete general theory of intelligence.

All work in this repository is independent personal research. Affiliations, when
listed, are for identification only and do not imply sponsorship or endorsement.
