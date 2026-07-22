# Paper 1 — summary

> **Evidence:** [`../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/README.md`](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/README.md)  
> **Public boundary:** [`../PUBLIC_BOUNDARY.md`](../PUBLIC_BOUNDARY.md)

---

## Research question (v1.0)

> After a task-relevant mismatch at fixed state **S**, how do **intervention choice** and **start time** jointly determine **successful resolution**?

See [`research_question.md`](research_question.md) · [`status.md`](status.md) · [`roadmap.md`](roadmap.md)

---

## Stage 1 smoke results (Isaac · n=5 · Tier B)

| Study | Finding |
| --- | --- |
| **001A** @ 3 cm | CONTINUE **0/5** vs REPLAN **4/5** |
| **001B** @ 3 cm | REPLAN **3/3** for delays 0–20; flat band |
| **001C** grid | Mostly 0.8–1.0; **no timing cliff** |
| **001D D0** @ 6 cm + occlusion | REPLAN **5/5** · REOBSERVE **4/5** |
| **001D D1** 5-mode | RESHAPE **4/5** · HANDOVER stub **0/5** |

**Framing:** [`research_framing_v1.md`](research_framing_v1.md)  
**Evaluation landscape:** [`evaluation_landscape_2024_2026_v0.2.md`](evaluation_landscape_2024_2026_v0.2.md)  
**Phase B review:** [`phase_b_smoke_review.md`](phase_b_smoke_review.md)  
**Lit positioning:** [`lit_positioning_v1.md`](lit_positioning_v1.md)  
**Related work index:** [`related_work_index.md`](related_work_index.md)  
**Phase C plan (frozen · not run):** [`phase_c_proper_run_prereg_v1.0.md`](phase_c_proper_run_prereg_v1.0.md)

**Figures:** [Fig 4](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1a_isaac/figures/counterfactual_grid.png) · [Fig 5](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1b_isaac/figures/recoverability_vs_delay.png)

---

## Next

1. Phase C confirmatory run (n=20) after sign-off · pre-reg frozen  
2. Study 002 pilot — see [`../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/README.md`](../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/README.md)

---

## Not claiming (public)

- Confirmatory statistics · learned recoverability method · clinical deployment  
- Golden time · severity×delay as headline  
- Full novelty verdict without PDF-complete related work
