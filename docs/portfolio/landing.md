# Informative failures @ fixed S — measurement + selection

> Portfolio · **[higuseonhye.github.io/research-os](https://higuseonhye.github.io/research-os/)** · source [`docs/index.md`](../index.md)

---

## Two questions

1. **Paper 1 (measure):** At fixed mismatch onset **S**, do **intervention-conditioned recoverability profiles** separate under same-state counterfactual evaluation?

2. **Paper 2 (select):** Can a **cheap mock rank** predict **physics-level counterfactual value** on a frozen export set?

**Platform:** Isaac Sim 4.1 · ORBIT Dual-STAR Reach · same-state CF replay.

**Latest:** Paper 001 Tier C complete · **Paper 002** PDF v1.2 **under review** · GPU not started.

---

## What is verified

### Tier C — Paper 001 proper program (2026-07-24)

| Block | Result |
| --- | --- |
| **D0** @ 6 cm + occlusion | REPLAN **19/20** vs CONTINUE **0/20** |
| **D1** no occlusion | REPLAN **19/20** vs CONTINUE **1/20** |
| **D2** B2 UQ rule | success **0/20** (HANDOVER 20/20) |
| **D3** B3 situation rule | REOBSERVE **17/20 (85%)** |

RQ-B direction met: menu best **95%** > B2 **0%** > B3 **85%**.

Links: [D0 summary](https://github.com/higuseonhye/research-os/blob/master/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1_proper/summary.json) · [D1–D3 summary](https://github.com/higuseonhye/research-os/blob/master/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1_proper_v2/summary.json) · [Paper 1 status](https://github.com/higuseonhye/research-os/blob/master/docs/paper1/status.md)

### Figures (Tier C)

| Fig | Asset |
| --- | --- |
| D0 profile | [fig3_profile_d0.png](https://github.com/higuseonhye/research-os/blob/master/docs/paper1/figures/fig3_profile_d0.png) |
| Baseline overlay | [fig4_baseline_overlay.png](https://github.com/higuseonhye/research-os/blob/master/docs/paper1/figures/fig4_baseline_overlay.png) |
| Isaac EE traces | [sim_panel_isaac_traces.png](https://github.com/higuseonhye/research-os/blob/master/docs/paper1/figures/sim_panel_isaac_traces.png) |
| Full set | [docs/paper1/figures/](https://github.com/higuseonhye/research-os/tree/master/docs/paper1/figures) |

### Study 2 · Tier B/C probe

Phase 1 mock + Isaac · selection ablation VESSL 2026-07-24 · [isaac_full_v0.1 summary](https://github.com/higuseonhye/research-os/blob/master/experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/isaac_full_v0.1/summary.json)

### Paper 002 · pre-results (under review)

Pre-reg frozen · tag `paper002-prereg-v0.3` · [PDF v1.2](https://github.com/higuseonhye/research-os/blob/master/docs/paper002/paper002_pre_results_v1.2.pdf) · [status](https://github.com/higuseonhye/research-os/blob/master/docs/paper002/status.md) · confirmatory GPU not started

### Tier B smoke (superseded for claims)

[counterfactual_grid.png](https://github.com/higuseonhye/research-os/blob/master/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1a_isaac/figures/counterfactual_grid.png) · [recoverability_vs_delay.png](https://github.com/higuseonhye/research-os/blob/master/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1b_isaac/figures/recoverability_vs_delay.png)

---

## What we do not claim

- Learned recoverability estimator · clinical deployment · WM extension in Paper 001 body

---

## Artifacts

- **Working paper (EN):** [paper001_recoverability_complete.pdf](https://github.com/higuseonhye/research-os/blob/master/docs/paper1/paper001_recoverability_complete.pdf) · *not peer-reviewed*
- **Pre-results 002 (under review):** [paper002_pre_results_v1.2.pdf](https://github.com/higuseonhye/research-os/blob/master/docs/paper002/paper002_pre_results_v1.2.pdf)
- [research-os](https://github.com/higuseonhye/research-os) · [EXPERIMENT_LOOP.md](https://github.com/higuseonhye/research-os/blob/master/docs/EXPERIMENT_LOOP.md)

---

## Contact

Open to research and evaluation roles where **failure is data**. Korea · Toronto / remote Canada welcome.

**GitHub:** [higuseonhye/research-os](https://github.com/higuseonhye/research-os)

---

*Updated 2026-07-28 · sync with [`docs/index.md`](../index.md)*
