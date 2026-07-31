# Research Program — Revising an Inadequate World Model

> **Core question:** When should an intelligent system decide that its current understanding of the world is no longer sufficient—and how should it construct a better one?

This is the long-lived research question behind the papers, experiments, and public tools in this repository.

## Program thesis

Most intelligent systems are optimized to improve predictions, policies, or parameters inside a fixed model class. The harder problem begins when repeated repair no longer explains the world.

This program studies three decisions:

1. **Mismatch detection** — when has reality diverged in a task-relevant way?
2. **Model adequacy** — can the current representation and model class still explain and recover from the mismatch?
3. **World-model revision** — when should the system change structure, composition, memory, abstraction, or representation rather than continue parameter repair?

## Research stack

```text
Core question
  ↓
Theory: mismatch · adequacy · revision · informative experience
  ↓
Measurement: recoverability · counterfactual comparison · intervention timing
  ↓
Testbeds: Physical AI first; surgical and general embodied simulation now
  ↓
Artifacts: papers · protocols · benchmarks · Mismatch Lab
```

Physical AI is the first experimental domain because embodiment exposes consequential mismatch, partial observability, timing, intervention, and recovery. It is a testbed for the question—not the boundary of the question.

## Current sequence

| Stage | Role in the program | Status |
| --- | --- | --- |
| **Paper 001** | Establish recoverability as a measurable post-mismatch window | Tier C complete · [hub](../paper1/README.md) |
| **Paper 002** | Test whether an adequacy decision can distinguish repair from structural expansion | Tier C complete · [hub](../paper002/README.md) · [project page](../paper002/project_page.html) |
| **Paper 003** | Ask whether expansion opens *capability* a repair cannot reach, when the gap is a missing relation | Design v0.1 · [hub](../paper003/README.md) |
| **Mismatch Lab** | Turn rollout comparison and adequacy analysis into public research infrastructure | Spec v0.1 · [hub](../mismatch_lab/README.md) |

Each paper changes the decision under test, not the question:

```text
001  Is the failure recoverable at all?        (measurement window)
002  Repair, or change the model class?        (mode gap)
003  Does changing it open new capability?     (relation gap)
```

## Application policy

New applications are included only when they sharpen the central question. Candidate domains include robotics, autonomous systems, adaptive agents, healthcare AI, and human–AI collaboration. A domain trend alone is not sufficient reason to enter it.

A worked example of the rule refusing something appealing: an everyday-assembly setting was admitted for Paper 003 because irreversible assembly steps supply the commitment structure the capability endpoint needs, while **preference learning and companion interaction in the same setting were excluded** — they are a different question (personalisation), and they offer no ground truth against which a capability threshold could be defined. See [the scope table](../paper003/paper003_commitment_task_v0.1.md#domain-note-breakfast-assembly).

## Claim boundary

The program currently provides controlled simulation evidence, protocols, and early mechanisms. It does not yet claim a general theory of world-model revision, autonomous structural self-improvement, clinical deployment, or cross-domain generalization.

Tier discipline is enforced per artifact: preregistration is frozen before a confirmatory run, and design-stage results are labelled as such. Paper 003's current results are **design-stage** — a construction showing the endpoint is measurable, not evidence that it holds.

## Decision rule

Before starting a new paper, benchmark, product surface, or application, ask:

> Does this work help determine when the current model is inadequate, what evidence justifies revision, or how a better model should be constructed?

If not, it belongs outside the core program or should remain an exploratory note in the private workspace.
