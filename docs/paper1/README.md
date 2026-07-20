# Paper 1 — summary

> **Evidence:** [`../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/README.md`](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/README.md)

---

## Research question (v0.9)

> When a task-relevant mismatch occurs, **which response should start when** to maximize **successful resolution**?

See [`research_question.md`](research_question.md) · status [`status.md`](status.md)

---

## Stage 1 results (Isaac · n=5)

| Study | Finding |
| --- | --- |
| **001A** @ 3 cm | CONTINUE **0/5** vs REPLAN **4/5** |
| **001B** @ 3 cm | REPLAN **3/3** for delays 0–20; flat band |
| **001C** grid | Mostly 0.8–1.0; **no timing cliff** in tested grid |

**Interpretation (not claim):** Mode may dominate small delay at mild shift. Not a golden-time result.

**Figures:** [Fig 4](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1a_isaac/figures/counterfactual_grid.png) · [Fig 5](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1b_isaac/figures/recoverability_vs_delay.png)

Captions: [`fig_captions.md`](fig_captions.md)

---

## Next experiment (Go · 2026-07-21 lab)

**001D** — occlusion-induced visibility mismatch @ 6 cm · REPLAN delay 20 · multi-mode (continue / replan / reobserve / reshape).  
Pre-reg and config: private `builder-os-private/working/experiments/` until Isaac smoke promotes public config.

---

## Not claiming (public)

- Learned recoverability method · clinical deployment · golden time in seconds
- Severity×delay as Paper 1 headline
- Full novelty verdict vs recovery literature (in progress)
- “No prior work on recovery” (pieces exist; wedge = same-state multi-mode CF profiles)
