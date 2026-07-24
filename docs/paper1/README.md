# Paper 1 — summary

> **Evidence:** [`../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/README.md`](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/README.md)  
> **Status:** [`status.md`](status.md) · Tier C proper program complete (D0–D3 · 2026-07-24)

---

## Research question (v1.1)

> At fixed mismatch onset **S**, do intervention-conditioned recoverability profiles separate under same-state counterfactual evaluation?

See [`research_question.md`](research_question.md) · [`method_spec_v1.0.md`](method_spec_v1.0.md) · [`roadmap.md`](roadmap.md)

---

## Proper program (Tier C · n=20)

| Block | Result |
| --- | --- |
| **D0** 5-mode + occlusion | REPLAN **19/20** vs CONTINUE **0/20** |
| **D1** no occlusion | REPLAN **19/20** vs CONTINUE **1/20** |
| **D2** B2 UQ rule | HANDOVER **20/20** · success **0/20** |
| **D3** B3 situation rule | REOBSERVE **17/20 (85%)** |

Pre-reg: [`phase_c_proper_run_prereg_v2.0.md`](phase_c_proper_run_prereg_v2.0.md) · Data: [`study1_proper_v2/summary.json`](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1_proper_v2/summary.json)

---

## Figures & tables

**Main text:** [`figures/README.md`](figures/README.md) · Captions: [`fig_captions.md`](fig_captions.md)

| Fig | Asset |
| --- | --- |
| 1 Architecture | [`figures/fig1_architecture_overview.png`](figures/fig1_architecture_overview.png) |
| 2 CF fork | [`figures/fig2_same_state_fork.png`](figures/fig2_same_state_fork.png) |
| 3 D0 profile | [`figures/fig3_profile_d0.png`](figures/fig3_profile_d0.png) |
| 4 Baselines | [`figures/fig4_baseline_overlay.png`](figures/fig4_baseline_overlay.png) |
| 5 Occlusion | [`figures/fig5_occlusion_contrast.png`](figures/fig5_occlusion_contrast.png) |

Regenerate: `python scripts/plot_paper1_figures.py` · Isaac capture: `bash scripts/capture_study1_viewport.sh`

---

## Smoke (Tier B · design input only)

001A–D smoke atlas · see [`phase_b_smoke_review.md`](phase_b_smoke_review.md)

---

## Next

Paper draft (Stage 6) · Isaac viewport capture on GPU for trace-backed sim panels

---

## Not claiming (public)

Learned recoverability estimator · clinical deployment · golden-time law · Study 002 body
