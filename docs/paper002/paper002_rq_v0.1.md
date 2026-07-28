# Paper 002 — Research questions v0.1 (superseded)

> **Superseded by [paper002_rq_v0.2.md](paper002_rq_v0.2.md)**

> **Paper:** CF-validated generative curriculum for informative failure scenarios  
> **Experiment:** EXP-SURG-003 · **Codebase:** [`exp_surg_002_dream_curriculum`](../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/)  
> **Pilot:** Study 002 / EXP-SURG-002 (Tier B · archived)  
> **Ruler:** Paper 001 same-state CF @ fixed **S** · study1d occlusion contract  
> **Date:** 2026-07-28

---

## Position in program

| Layer | Artifact | Status |
| --- | --- | --- |
| **Measure @ S** | Paper 001 | ✅ complete |
| **Generate probe** | Study 002 | ✅ pilot · informs design |
| **Generate confirmatory** | **Paper 002** | 🔄 this document |

Paper 003 (deferred): latent mismatch + response selection — not in scope here.

---

## Central question

> Can a **mock–Isaac aligned** generative curriculum—using **Gaussian and diffusion dreamers** under an **agentic planner** (rule or LLM)—produce **informative failure scenarios** whose mock rank **predicts** Isaac same-state counterfactual outcomes @ **S**?

**Informative @ spec (frozen):** CONTINUE unsuccessful ∧ REPLAN successful (Paper 001 definition).

---

## Sub-questions

| ID | Question | Role |
| --- | --- | --- |
| **RQ-B1** | Does mock per-spec informative rank correlate with Isaac rank at **confirmatory scale** (40-spec pack · study1d)? | **Primary** |
| **RQ-B2** | Does **tier separation** (top vs bottom mock rank) hold on Isaac with stricter floors? | **Primary** |
| **RQ-B3** | Does an **LLM JSON curriculum** validate on Isaac—not only mock—vs the rule planner? | **Primary confirmatory extension** |
| **RQ-B4** | Gaussian vs diffusion: yield vs param diversity tradeoff? | Exploratory |
| **RQ-B5** | Hybrid dreamer (mixed proposals) improve tier gap or ρ? | Exploratory |

---

## What Study 002 established (pilot · not re-tested as primary)

| Pilot finding | Paper 002 use |
| --- | --- |
| Diffusion > Gaussian on yield | **Not primary** — closed at Phase 1 |
| Occlusion misalignment broke H3 | **Mandatory** study1d + visibility map |
| H3′ ρ=0.899 @ n=20 | **Power basis** for n=40 confirmatory |
| LLM JSON mock-only | **RQ-B3** — Isaac leg required |

---

## Success definition (paper-level)

**Tier A candidate (primary story):**

1. H1 + H2 PASS @ rule agent (replication at scale), **and**
2. H3 PASS @ LLM agent (Isaac validation), **or** honest Tier B: “mock filter works · LLM = rule on Isaac”

**Tier B (still publishable):**

- H1 + H2 PASS · H3 FAIL → CF-gated curriculum without LLM claim

**Stop (no GPU spiral):**

- H2 FAIL @ rule → mock tier filter unreliable at scale · redesign before LLM leg

---

## Non-claims

- Clinical deployment · surgical foundation model · SOTA reach policy  
- Latent mismatch trigger (Paper 003) · RL response selection (Paper 003)  
- Classifier-guided image diffusion · full ReSYNC / IVNTR
