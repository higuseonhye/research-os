# Paper 1 — research question (public lock)

> **Status:** **v1.1** · D0 Tier C executed · pre-reg v2.0 (D1–D3) in design  
> **Scope:** Stage 1 measurement · surgical reach proxy · EXP-SURG-001 unified with study1A–D  
> **Program context:** Non-Average World ruler @ fixed **S** — not WM extension · Study 002 separate

---

## Central research question (v1.1)

**EN:**

> At a fixed post-mismatch execution state **S**, do intervention classes yield **separable recoverability profiles** — and does a **multi-mode menu** outperform **continue**, a **UQ-inspired binary rule**, and a **situation rule** on resolution and burden metrics?

**KR:**

> 과업 관련 mismatch 직후 **고정 상태 S**에서, response class별 recoverability profile이 분리되는가 — multi-mode menu가 continue·UQ binary rule·situation rule보다 resolution/burden에서 나은가?

*(v1.0 timing joint form retained as secondary object — delay confirmatory deferred; see RQ-T.)*

---

## Measured object

**Intervention-conditioned recoverability profile** \(R_a(s,t)\):

- fixed onset state **S** (same-state counterfactual fork)
- intervention **a** ∈ {continue, replan, reobserve, reshape, handover, …}
- start time **t** (steps after mismatch) — fixed d20 for confirmatory primary cell
- outcome: **successful resolution** (terminal distance · safety · category)

Counterfactual evaluation is **method**, not a claim of a new learned recoverability estimator.

---

## Sub-questions (Paper 1 · v1.1 priority)

| ID | Sub-RQ | Smoke (Tier B) | Confirmatory (pre-reg v2.0) |
| --- | --- | --- | --- |
| **RQ-M** | At fixed **S**, do response classes yield **separable** success profiles? (REPLAN ≫ CONTINUE) | **Direction yes** — 001A · 001D | ✅ **D0** n=20 · REPLAN **19/20** vs CONTINUE **0/20** |
| **RQ-B** | Do multi-mode profiles beat **B2 UQ rule** and **B3 situation rule**? | Not tested | **Required** · **D2** · **D3** |
| **RQ-P** | Does **occlusion** change profiles vs shift-only @ matched 6 cm? | 001D direction | **Required** · **D1** |
| **RQ-C** | Do REOBSERVE / RESHAPE add viable paths beyond REPLAN? | 001D smoke 4/5 | Exploratory · **D0** profile (17/20 · 18/20) |
| **RQ-T** | Does **delaying REPLAN** materially reduce recoverability? | **Mostly flat** · 001B/C | **Deferred** — not confirmatory headline |

---

## Experimental arm map (EXP-SURG-001)

| Arm | Study | Sub-RQ | Tier | Role |
| --- | --- | --- | --- | --- |
| Mode @ 3 cm | 001A | RQ-M | B | Design · counterfactual grid |
| Delay grid | 001B | RQ-T | B | Defer confirmatory |
| Severity × delay | 001C | RQ-T · anchor | B | 6 cm · d20 lock |
| Occlusion + 5-mode smoke | 001D | RQ-M · RQ-C · RQ-P | B | Proxy validation |
| Primary cell | **D0** (Phase C) | RQ-M · RQ-C | **C** | Executed 2026-07-22 |
| No-occlusion control | **D1** | RQ-P | C target | pre-reg v2.0 |
| B2 UQ-inspired binary | **D2** | RQ-B | C target | pre-reg v2.0 |
| B3 situation rule | **D3** | RQ-B | C target | pre-reg v2.0 |

**Study 002 (EXP-SURG-002):** informative scenario **generation** — separate program · optional appendix only · not Paper 1 body.

---

## VAP-separating form (preferred framing)

> Given an execution-time mismatch, can **counterfactual intervention profiles** identify when replanning, re-observation, environment shaping, or human assistance is most likely to preserve successful task resolution — compared to continuing or a fixed situation-handler rule?

We **evaluate** profiles; we do not claim a new VAP-TAMP-style architecture.

---

## Claim tiers (honest labeling)

| Tier | Label | Evidence |
| --- | --- | --- |
| **A** | Scaffold / protocol | Same-state CF pipeline · ORBIT Isaac · replay OK |
| **B** | Smoke / direction | 001A–D · n=5 · scripted IK-Rel |
| **C** | Confirmatory | **D0** Phase C n=20 · D1–D3 pending pre-reg v2.0 |

**Public stance today:** Tier A + B + **one Tier C cell (D0)**. Full publication-grade program after D1–D3.

---

## Method (Stage 1)

```text
Shared rollout → mismatch @ S → replay → fork(response [, baseline rule]) → terminal judge → profile table
```

Platform: Isaac Sim 4.1 · ORBIT Dual-STAR Reach · scripted 6D IK-Rel.

Anchor cell: +6 cm Y @ step 20 · occlusion L1 (visibility 0.35) · REPLAN_d20 · n=20.

---

## Paper 1 contributions (scoped public)

| # | Contribution |
| --- | --- |
| 1 | **Same-state counterfactual evaluation** — fair intervention comparison at mismatch onset |
| 2 | **Intervention-conditioned recoverability profiles** — empirical slices 001A–D + D0 proper |
| 3 | *(v2.0)* **Rule baseline comparison** — UQ-inspired binary · situation rule @ same **S** |

---

## What Paper 1 is not

- Learned meta-policy / recoverability estimator (Stage 2+)
- World model extension · diffusion dreaming · agent curriculum (Study 002 · separate)
- Clinical autonomous surgery
- Universal golden-time law (RQ-T deferred)
- “No prior work on recovery” (wedge = **multi-mode CF eval**)

---

## Links

- Proper program: private `paper1_proper_program_v0.1.md` · public [`roadmap.md`](roadmap.md)
- Method spec v1.0: [`method_spec_v1.0.md`](method_spec_v1.0.md)
- Pre-reg v2.0 (draft): [`phase_c_proper_run_prereg_v2.0.md`](phase_c_proper_run_prereg_v2.0.md)
- Phase C v1.0 (D0): [`phase_c_proper_run_prereg_v1.0.md`](phase_c_proper_run_prereg_v1.0.md)
- Results D0: [`study1_proper/summary.json`](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1_proper/summary.json)
- Phase B review: [`phase_b_smoke_review.md`](phase_b_smoke_review.md)
- Lit positioning: [`lit_positioning_v1.md`](lit_positioning_v1.md)
- Status: [`status.md`](status.md)

---

## Version history

| Version | Date | Note |
| --- | --- | --- |
| v0.9 | 2026-07-16 | Central Q + Stage 1 method |
| v1.0 | 2026-07-22 | Sub-RQs · claim tiers · post-smoke lock |
| **v1.1** | 2026-07-24 | Unified EXP-SURG-001 arms · RQ-B/P promoted · RQ-T deferred · D0–D3 matrix · Study 002 boundary |
