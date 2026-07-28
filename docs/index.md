# Informative failures @ fixed S — measurement + selection

Research portfolio · [GitHub repo](https://github.com/higuseonhye/research-os)

---

## Two questions

1. **Paper 1 (measure):** At fixed mismatch onset **S**, do **intervention-conditioned recoverability profiles** separate under same-state counterfactual evaluation?

2. **Paper 2 (select):** Can a **cheap mock rank** predict **physics-level counterfactual value** on a frozen export set — before full Isaac evaluation?

**Platform:** Isaac Sim 4.1 · ORBIT Dual-STAR Reach · same-state CF replay.

**Latest:** Paper 001 Tier C complete · **Paper 002** pre-reg frozen · pre-results PDF v1.2 **under review** · GPU not started.

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

### Study 2 (Tier B/C probe · closed)

| Claim | Evidence |
| --- | --- |
| Dream curriculum pipeline | Phase 1–2 executed · H3′ ρ=0.899 after occlusion align |
| Mock tradeoff | Gaussian higher informative yield · diffusion higher param diversity |

[Study 2 index](stage2/README.md) · **Active:** [Paper 002 — mock-to-physics validation](paper002/README.md) · **Status:** [under review](paper002/status.md)

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

- **Working paper (EN · July 2026):** [paper001_recoverability_complete.pdf](paper1/paper001_recoverability_complete.pdf) — same-state CF · Tier C D0–D3 · *not peer-reviewed* · *independent research*
- **Pre-results (002 · under review):** [paper002_pre_results_v1.2.pdf](paper002/paper002_pre_results_v1.2.pdf) · [status](paper002/status.md)
- **Code & results:** [research-os](https://github.com/higuseonhye/research-os)
- **Paper 1 hub:** [docs/paper1/](https://github.com/higuseonhye/research-os/tree/master/docs/paper1)
- **Paper 002 hub:** [docs/paper002/](https://github.com/higuseonhye/research-os/tree/master/docs/paper002) · tag `paper002-prereg-v0.3`
- **Naming guide:** [NAMING.md](https://github.com/higuseonhye/research-os/blob/master/docs/NAMING.md)
- **Experiment loop:** [EXPERIMENT_LOOP.md](https://github.com/higuseonhye/research-os/blob/master/docs/EXPERIMENT_LOOP.md)

---

## Contact

Open to research and evaluation roles where **failure is data** and hypotheses are tested explicitly. Based in Korea · open to **Toronto / remote Canada**.

**GitHub:** [@higuseonhye](https://github.com/higuseonhye) · **Repo:** [research-os](https://github.com/higuseonhye/research-os)

---

*Updated 2026-07-28 · [Edit this page](https://github.com/higuseonhye/research-os/blob/master/docs/index.md)*
