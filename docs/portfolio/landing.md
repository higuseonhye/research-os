# Informative failures @ fixed S — measurement + generation

> Portfolio landing v0.1 · copy to Notion / GitHub Pages / personal site  
> Canonical repo: [github.com/higuseonhye/research-os](https://github.com/higuseonhye/research-os)

---

## Two questions

1. **Paper 1 (measure):** After task-relevant mismatch at a fixed execution state **S**, how do **intervention choice** and **timing** determine **successful resolution**?

2. **Study 2 (generate):** Which dreamed perturbation scenarios are **informative** for curriculum design (CONTINUE fails ∧ REPLAN succeeds)—**Gaussian vs diffusion** dreaming?

**Platform:** Isaac Sim 4.1 · ORBIT Dual-STAR Reach · same-state counterfactual evaluation.

---

## What is verified

### Tier C (confirmatory summaries · 2026-07-22)

| Claim | Evidence |
| --- | --- |
| **Mode separation @ S** | Occlusion @ 6 cm · REPLAN d20 **19/20** vs CONTINUE **0/20** (n=20) |
| **Multi-mode profiles** | REOBSERVE **17/20** · RESHAPE **18/20** (same cell) |
| **Dream curriculum pipeline** | Study 2 Phase 1: mock + Isaac transfer complete |

Links: [Paper 1 summary](https://github.com/higuseonhye/research-os/blob/master/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1_proper/summary.json) · [Study 2 Isaac summary](https://github.com/higuseonhye/research-os/blob/master/experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/isaac_full_v0.1/summary.json)

### Tier B (smoke · direction)

| Claim | Evidence |
| --- | --- |
| Same-state counterfactual fork | [counterfactual_grid.png](https://github.com/higuseonhye/research-os/blob/master/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1a_isaac/figures/counterfactual_grid.png) |
| Delay band @ 3 cm | [recoverability_vs_delay.png](https://github.com/higuseonhye/research-os/blob/master/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1b_isaac/figures/recoverability_vs_delay.png) |
| Dreamer tradeoff (desk) | Gaussian higher informative yield · diffusion higher param diversity |

---

## What we do not claim

- A new learned recoverability **method** or clinical OR validation
- Diffusion beats Gaussian on **yield** (Study 2 Phase 1: coverage vs diversity framing)
- Registry-style confirmatory claims beyond committed Tier C summaries

---

## Artifacts

- **Code & results:** [research-os](https://github.com/higuseonhye/research-os)
- **Paper 1 status:** [docs/paper1/status.md](https://github.com/higuseonhye/research-os/blob/master/docs/paper1/status.md)
- **Repro:** RunPod scripts · pre-registered Phase C design

---

## Contact

Open to research and evaluation roles where **failure is data** and hypotheses are tested explicitly. Based in Korea · open to **Toronto / remote Canada** · technical conversations welcome from Bay Area and Pittsburgh.

**Email:** _(add)_ · **GitHub:** [higuseonhye/research-os](https://github.com/higuseonhye/research-os)

---

*Updated 2026-07-22 · smoke → proper → update loop · see [EXPERIMENT_LOOP.md](https://github.com/higuseonhye/research-os/blob/master/docs/EXPERIMENT_LOOP.md)*
