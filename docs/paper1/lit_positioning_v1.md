# Paper 1 — Literature positioning v1 (public)

> **Date:** 2026-07-22 · **Status:** post Lit Sprint v2 · smoke-informed · not a survey  
> **Private extended:** [builder-os-private lit_sprint_v2](https://github.com/higuseonhye/builder-os-private/blob/master/working/research/lit_sprint_v2_smoke_synthesis.md)

---

## Positioning (one paragraph)

Prior work strong on **separate axes**: uncertainty-gated handover in surgery, binary task–recovery switching, autonomous exploration recovery, tissue reshaping for exposure (MEDiC), and situation-driven replanning stacks (VAP-TAMP). None standardize **same-state counterfactual comparison** of a **multi-mode intervention menu** toward **successful resolution** with explicit timing. Our Stage 1 contribution is an **evaluation protocol** and **empirical profiles** \( \hat{R}_a(s,t) \) on an ORBIT-Surgical reach proxy — smoke evidence (n=5) shows mode separation under shift and an occlusion proxy; confirmatory runs are pre-registered separately (Phase C).

---

## Closest prior art (honest)

| Line | They optimize | Our wedge |
| --- | --- | --- |
| Surgical UQ | continue vs handover | Multi-mode profile @ same onset |
| Recovery RL / RTA | task ↔ backup policy | Menu + reshape + reobserve |
| MEDiC | tissue reshape for exposure | Reshape as one timed mode among many |
| VAP-TAMP | situation → perceive → replan | **Eval** not new stack |
| VLA / FM | task success | No public multi-mode recovery profile tables |

**Kill test (Day-1 + smoke):** full combination → **0 Kill** · refine positioning, do not claim empty field.

---

## What smoke supports (Tier B only)

- CONTINUE ≪ REPLAN @ 3 cm and @ 6 cm + occlusion
- Delay band flat @ tested 3 cm grid — timing not headline
- REOBSERVE / RESHAPE viable in smoke (4/5) — confirmatory n pending

---

## What we do not claim

- Beat SOTA VLA · clinical deployment · learned recoverability estimator
- Geometric occlusion (gain_scale v0.1 is documented proxy)
- HANDOVER success (collaboration stub in v0.1)

---

## Links

- RQ v1.0: [`research_question.md`](research_question.md)
- Phase B: [`phase_b_smoke_review.md`](phase_b_smoke_review.md)
- Phase C pre-reg: [`phase_c_proper_run_prereg_v1.0.md`](phase_c_proper_run_prereg_v1.0.md)
- Roadmap: [`roadmap.md`](roadmap.md)
