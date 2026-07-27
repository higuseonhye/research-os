# Informative failures @ fixed S — measurement + generation

Research portfolio · [GitHub repo](https://github.com/higuseonhye/research-os)

---

## Two questions

1. **Paper 1 (measure):** At fixed mismatch onset **S**, do **intervention-conditioned recoverability profiles** separate under same-state counterfactual evaluation?

2. **Study 2 (generate):** Which dreamed perturbation scenarios are **informative** for curriculum design (CONTINUE fails ∧ REPLAN succeeds)—**Gaussian vs diffusion** dreaming?

**Platform:** Isaac Sim 4.1 · ORBIT Dual-STAR Reach · scripted IK-Rel · same-state CF replay.

---

## What is verified

### Tier C — Paper 001 proper program (2026-07-24)

Pre-reg v2.0 executed on VESSL · n=20 per branch · `branch_replay_ok` on all records.

| Block | Result |
| --- | --- |
| **D0** @ 6 cm + occlusion L1 | REPLAN **19/20** vs CONTINUE **0/20** · REOBSERVE **17/20** · RESHAPE **18/20** |
| **D1** no-occlusion control | REPLAN **19/20** vs CONTINUE **1/20** (descriptive) |
| **D2** B2 UQ-inspired rule | HANDOVER **20/20** · success **0/20** |
| **D3** B3 situation rule | REOBSERVE path **17/20 (85%)** |

**RQ-B (pre-reg):** best-of-menu **95%** > B2 **0%** · **95%** > B3 **85%** — direction met.

Summaries: [D0 JSON](https://github.com/higuseonhye/research-os/blob/master/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1_proper/summary.json) · [D1–D3 JSON](https://github.com/higuseonhye/research-os/blob/master/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1_proper_v2/summary.json) · [status](https://github.com/higuseonhye/research-os/blob/master/docs/paper1/status.md)

### Figures (Tier C)

**D0 recoverability profile @ fixed S (n=20):**

![D0 profile](https://raw.githubusercontent.com/higuseonhye/research-os/master/docs/paper1/figures/fig3_profile_d0.png)

**Response menu vs rule baselines (RQ-B):**

![Baseline overlay](https://raw.githubusercontent.com/higuseonhye/research-os/master/docs/paper1/figures/fig4_baseline_overlay.png)

**Isaac EE traces — seed 0 (reproducible capture):**

![Isaac traces](https://raw.githubusercontent.com/higuseonhye/research-os/master/docs/paper1/figures/sim_panel_isaac_traces.png)

More: [figure index](https://github.com/higuseonhye/research-os/tree/master/docs/paper1/figures) · [method spec](https://github.com/higuseonhye/research-os/blob/master/docs/paper1/method_spec_v1.0.md)

### Study 2 (Tier B/C probe)

| Claim | Evidence |
| --- | --- |
| Dream curriculum pipeline | Phase 1 mock + Isaac transfer · selection ablation on VESSL (2026-07-24) |
| Mock tradeoff | Gaussian higher informative yield · diffusion higher param diversity |

[Study 2 Isaac summary](https://github.com/higuseonhye/research-os/blob/master/experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/isaac_full_v0.1/summary.json)

### Tier B (smoke · design input only)

| Claim | Evidence |
| --- | --- |
| Same-state CF fork @ 3 cm | [counterfactual_grid.png](https://github.com/higuseonhye/research-os/blob/master/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1a_isaac/figures/counterfactual_grid.png) |
| Delay band @ 3 cm | [recoverability_vs_delay.png](https://github.com/higuseonhye/research-os/blob/master/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1b_isaac/figures/recoverability_vs_delay.png) |

Superseded for claims by Tier C figures above.

---

## What we do not claim

- A learned recoverability **estimator** or clinical OR deployment
- World-model extension (Study 2 is appendix-scope · not Paper 001 body)
- Registry-style claims beyond committed Tier C summaries

---

## Artifacts

- **Code & results:** [research-os](https://github.com/higuseonhye/research-os)
- **Paper 1 hub:** [docs/paper1/](https://github.com/higuseonhye/research-os/tree/master/docs/paper1)
- **Experiment loop:** [EXPERIMENT_LOOP.md](https://github.com/higuseonhye/research-os/blob/master/docs/EXPERIMENT_LOOP.md)

---

## Contact

Open to research and evaluation roles where **failure is data** and hypotheses are tested explicitly. Based in Korea · open to **Toronto / remote Canada**.

**GitHub:** [@higuseonhye](https://github.com/higuseonhye) · **Repo:** [research-os](https://github.com/higuseonhye/research-os)

---

*Updated 2026-07-24 · [Edit this page](https://github.com/higuseonhye/research-os/blob/master/docs/index.md)*
