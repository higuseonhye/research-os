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

| Stage | Role in the program | Current artifact |
| --- | --- | --- |
| **Paper 001** | Establish recoverability as a measurable post-mismatch window | Same-state intervention and timing study |
| **Paper 002** | Test whether an adequacy decision can distinguish repair from structural expansion | EXP-SURG-003 |
| **Mismatch Lab** | Turn rollout comparison and adequacy analysis into public research infrastructure | Robot Diff · Replay · Explain |

## Application policy

New applications are included only when they sharpen the central question. Candidate domains include robotics, autonomous systems, adaptive agents, healthcare AI, and human–AI collaboration. A domain trend alone is not sufficient reason to enter it.

## Claim boundary

The program currently provides controlled simulation evidence, protocols, and early mechanisms. It does not yet claim a general theory of world-model revision, autonomous structural self-improvement, clinical deployment, or cross-domain generalization.

## Decision rule

Before starting a new paper, benchmark, product surface, or application, ask:

> Does this work help determine when the current model is inadequate, what evidence justifies revision, or how a better model should be constructed?

If not, it belongs outside the core program or should remain an exploratory note in the private workspace.
