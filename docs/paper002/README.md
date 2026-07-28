# Paper 002 — Recoverable agentic loop (design v0.1)

> **Status:** design · pre-reg pending · **Gate:** Paper 001 ruler frozen ✅  
> **Experiment:** EXP-SURG-003 (+ EXP-WM-MISMATCH-001 sub-arm)  
> **Study 002:** closed — lessons feed in; not extended as “Phase 3”

---

## Why Paper 002 (not “Study 001”)

| Done | Label |
| --- | --- |
| Measurement @ fixed **S** | **Paper 001** / EXP-SURG-001 |
| Generation probe | **Study 002** / EXP-SURG-002 (closed) |
| **Next paper** | **Paper 002** — agent · diffusion · LLM · RL on the same ruler |

See [`../NAMING.md`](../NAMING.md).

---

## Central question (draft)

> After Paper 001 showed intervention profiles separate @ fixed **S**, can a **recoverable agentic loop**—(1) mismatch signal, (2) **LLM- or diffusion-generated** informative scenarios validated by same-state CF, and (3) an **agent or RL policy** over the response menu—beat rule baselines on recovery and curriculum yield?

**Uses Paper 001 as:** matched-**S** fork · terminal resolution metric · B2/B3 comparators.

**Does not claim:** clinical deployment · new surgical foundation model · SOTA reach policy.

---

## Three arms (one paper · tier-labeled)

| Arm | ID | Hypothesis (directional) | Builds on |
| --- | --- | --- | --- |
| **A · Mismatch** | EXP-WM-MISMATCH-001 | WM residual / learned signal triggers recovery earlier than geometry-only rules | Agentic WM L1 · EXP-DAILY-001 scout |
| **B · Generate S** | EXP-SURG-003 · dream | **LLM agent** + **diffusion** propose specs; mock rank predicts Isaac informative rate when occlusion contract aligned (Study 002 H3′) | Study 002 Phase 2 · LLM JSON mock-only today |
| **C · Select response** | EXP-SURG-003 · policy | Agent or **RL** over {CONTINUE, REPLAN, …} beats B2/B3 @ **S** | Paper 001 D0–D3 profiles as labels / baselines |

**Paper body strategy:** one primary confirmatory arm (pick after desk week) · others exploratory Tier B.

---

## Honest carryover from Study 002

| Finding | Paper 002 use |
| --- | --- |
| Gaussian ↑ yield · diffusion ↑ diversity | Hybrid curriculum design |
| H3 FAIL → H3′ PASS after occlusion align | **Mandatory** Paper 001 occlusion contract in all Isaac arms |
| LLM JSON = rule on mock | **Isaac arm required** before LLM claim |
| Phase 3 GPU deferred | Scope as Paper 002 pre-reg, not Study 002 Phase 3 |

---

## Phase plan

| Phase | Work | Tier |
| --- | --- | --- |
| **0 · Desk** | Pick primary arm · related work · kill matrix | — |
| **1 · Pre-reg** | Frozen hypotheses · promote to `docs/paper002/` | A |
| **2 · Mock smoke** | LLM agent · diffusion · optional L1 mismatch | B |
| **3 · Isaac GPU** | Same-state CF validation @ **S** | B/C |
| **4 · Paper** | Draft · figures · public promote slice | — |

---

## Public boundary

Design + pre-reg + tier-labeled results only. No private career material · no unlabeled mock as confirmatory.

---

## Links

| Resource | Path |
| --- | --- |
| Paper 001 ruler | [`../paper1/status.md`](../paper1/status.md) |
| Study 002 index | [`../stage2/README.md`](../stage2/README.md) |
| Naming | [`../NAMING.md`](../NAMING.md) |
| EXP-SURG-002 code | [`../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/`](../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/) |
