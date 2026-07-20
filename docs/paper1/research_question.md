# Paper 1 — research question (public lock)

> **Status:** **v1.0** · Phase A smoke complete · Phase C pre-reg frozen (not run)  
> **Scope:** 6 months · Stage 1 measurement · surgical reach proxy

---

## Primary research question

> **After a task-relevant mismatch at a fixed execution state, how do intervention choice and start time jointly determine the probability of successful resolution?**

한국어: 과업 관련 불일치가 고정된 실행 상태에서 발생했을 때, **개입의 종류(response)** 와 **시작 시점(timing)** 은 **successful resolution** 가능성을 어떻게 함께 결정하는가?

---

## Measured object

**Intervention-conditioned recoverability profile** \(R_a(s,t)\):

- fixed onset state **S** (same-state counterfactual fork)
- intervention **a** ∈ {continue, replan, reobserve, reshape, handover, …}
- start time **t** (steps after mismatch)
- outcome: **successful resolution** (terminal distance · safety · category)

Counterfactual evaluation is **method**, not a claim of a new learned recoverability estimator.

---

## Sub-questions (Paper 1 · scoped)

| ID | Sub-RQ | Smoke (Phase A) | Confirmatory (Phase C) |
| --- | --- | --- | --- |
| **RQ-M** | At fixed **S**, do response classes yield **separable** success profiles? | **Direction yes** — CONTINUE ≪ REPLAN @ 3 cm & 6 cm+occlusion | n=20 · primary cell |
| **RQ-T** | Does **delaying REPLAN** materially reduce recoverability in the tested band? | **Mostly flat** @ 3 cm grid (001B/C) | Fixed d20 for P1; delay sweep deferred |
| **RQ-P** | Does **occlusion** change profiles vs shift-only at matched severity? | REPLAN **5/5** persists; REOBSERVE **4/5** | Optional no-occlusion control arm |
| **RQ-C** | Do **information / environment** modes (REOBSERVE, RESHAPE) add viable paths beyond REPLAN? | RESHAPE **4/5** · REOBSERVE **4/5** (smoke) | n↑ · path metrics |
| **RQ-B** | Do multi-mode profiles beat **binary UQ-handover** rules on profile metrics? | **Not tested** | Stretch baseline in Phase C |

---

## VAP-separating form (preferred framing)

> Given an execution-time mismatch, can **counterfactual intervention profiles** identify when replanning, re-observation, environment shaping, or human assistance is most likely to preserve successful task resolution — compared to continuing or a fixed situation-handler rule?

We **evaluate** profiles; we do not claim a new VAP-TAMP-style architecture.

---

## Claim tiers (honest labeling)

| Tier | Label | Evidence |
| --- | --- | --- |
| **A** | Scaffold / protocol | Same-state CF pipeline · ORBIT Isaac · replay OK |
| **B** | Smoke / direction | 001A–C + D0/D1 · n=5 · scripted IK-Rel |
| **C** | Confirmatory | Phase C pre-reg v1.0 · n=20 · frozen before GPU |

**Public stance today:** Tier A + B only. Tier C after proper run.

---

## Method (Stage 1)

```text
Shared rollout → mismatch @ S → replay → fork(response, delay) → terminal judge → profile table
```

Platform: Isaac Sim 4.1 · ORBIT Dual-STAR Reach · scripted 6D IK-Rel.

---

## Paper 1 contributions (scoped public)

| # | Contribution |
| --- | --- |
| 1 | **Same-state counterfactual evaluation** — fair intervention comparison at mismatch onset |
| 2 | **Intervention-conditioned recoverability profiles** — empirical slices 001A/B/C/D |

---

## What Paper 1 is not

- Learned meta-policy / recoverability estimator (Stage 2)
- Clinical autonomous surgery
- Universal golden-time law
- “No prior work on recovery” (pieces exist; wedge = **multi-mode CF eval**)

---

## Links

- Phase B review: [`phase_b_smoke_review.md`](phase_b_smoke_review.md)
- Lit positioning v1: [`lit_positioning_v1.md`](lit_positioning_v1.md)
- Phase C pre-reg: [`phase_c_proper_run_prereg_v1.0.md`](phase_c_proper_run_prereg_v1.0.md)
- Roadmap: [`roadmap.md`](roadmap.md)
- Status: [`status.md`](status.md)

---

## Version history

| Version | Date | Note |
| --- | --- | --- |
| v0.9 | 2026-07-16 | Central Q + Stage 1 method |
| **v1.0** | 2026-07-22 | Sub-RQs · claim tiers · post-smoke lock |
