# After the Spill Research Program

> Live: **[higuseonhye.github.io/research-os](https://higuseonhye.github.io/research-os/)**
> Source: [`docs/index.md`](../index.md)

---

## Core question

**How should unexpected experience change an embodied system?**

Most AI research asks how systems should learn. This program asks how far a
system should change after reality contradicts its current model.

The working decision loop is:

```text
Experience -> Evidence -> Operator -> Closure
```

The governing principle is:

> Intelligence is the ability to determine the smallest sufficient change after
> unexpected experience.

## Research program

This is no longer presented as a single-paper portfolio. The stable object is a
research program with foundation documents, papers, and products that all serve
one question.

| Layer | Portfolio role |
| --- | --- |
| **Foundation documents** | D000-D006 define the language, novelty audit, literature matrix, formal objects, evaluation protocol, and roadmap |
| **Research papers** | Paper 001-005 test specific change operators |
| **Research products** | Robot Diff and Mismatch Lab expose the hypotheses to real rollout-comparison workflows |

[Program charter v2](https://github.com/higuseonhye/research-os/blob/master/docs/program/after_the_spill_v2.md)

[D001 Claim & Novelty Audit](https://github.com/higuseonhye/research-os/blob/master/docs/program/D001_claim_novelty_audit.md)

## Paper 001-005

| Paper | Question | Current status |
| --- | --- | --- |
| **Paper 001: Recoverability** | Can the system still recover from here? | Tier C complete - [working paper](https://github.com/higuseonhye/research-os/blob/master/docs/paper1/paper001_recoverability_complete.pdf) |
| **Paper 002: Model Adequacy** | Should it repair or expand the model class? | Tier C complete - [manuscript v1.1](https://github.com/higuseonhye/research-os/blob/master/docs/paper002/paper002_manuscript_model_order_v1.1.pdf) |
| **Paper 003: Representation Expansion** | Does expansion open capability that repair cannot reach? | Design/calibration - [hub](https://github.com/higuseonhye/research-os/tree/master/docs/paper003) |
| **Paper 004: Experience Disposition** | What should be done with the experience itself? | Program-defined |
| **Paper 005: Recovery Orchestration** | How should recovery operators be sequenced? | Program-defined |

Each paper changes the operator under test, not the core question.

## Research products

| Product | What it tests |
| --- | --- |
| **Robot Diff** | Whether rollout differences can surface evidence for repair, expansion, or refusal |
| **Mismatch Lab** | Whether diff, replay, explanation, and benchmark workflows can become shared evaluation infrastructure |
| **Evaluation Toolkit** | Whether evidence, operator choice, and closure can be compared across tasks |
| **Benchmark** | Whether unexpected experience forces repeatable change decisions |

[Mismatch Lab hub](https://github.com/higuseonhye/research-os/tree/master/docs/mismatch_lab)

[Robot Diff demo](https://higuseonhye.github.io/research-os/mismatch_lab/diff_explorer_v0.1.html)

## Current evidence boundary

Supported today: controlled simulation evidence for recoverability windows and
failure-conditioned model adequacy in specific embodied task families.

Not claimed: clinical deployment, hardware transfer, autonomous structural
self-improvement, universal resilience, arbitrary causal discovery, or a
complete theory of intelligence.

## More

[Research OS](https://github.com/higuseonhye/research-os)

[Program landing](https://higuseonhye.github.io/research-os/)

[Public boundary](https://github.com/higuseonhye/research-os/blob/master/docs/PUBLIC_BOUNDARY.md)

---

*Updated 2026-08-04*
