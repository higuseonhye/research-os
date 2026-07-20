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
| **001D** @ 6 cm + occlusion | REPLAN **5/5** · CONTINUE **0/5** · REOBSERVE **4/5** |

**Interpretation (not claim):** Mode may dominate small delay at mild shift. Not a golden-time result.

**Figures:** [Fig 4](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1a_isaac/figures/counterfactual_grid.png) · [Fig 5](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1b_isaac/figures/recoverability_vs_delay.png)

Captions: [`fig_captions.md`](fig_captions.md)

---

## 001D (Isaac D0 · promoted)

**001D** — [`study1d_report.md`](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/study1d_report.md) · [`results/study1d_isaac/`](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1d_isaac/)

RunPod: `STUDY1D_SEEDS=0,1,2,3,4 bash scripts/run_study1d_runpod.sh` · **D1 next:** `STUDY1D_FULL=1`

---

## Not claiming (public)

- Learned recoverability method · clinical deployment · golden time in seconds
- Severity×delay as Paper 1 headline
- Full novelty verdict vs recovery literature (in progress)
- “No prior work on recovery” (pieces exist; wedge = same-state multi-mode CF profiles)
