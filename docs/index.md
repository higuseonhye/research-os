# Informative failures @ fixed S — measurement + generation

Research portfolio · [GitHub repo](https://github.com/higuseonhye/research-os)

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

[Paper 1 summary JSON](https://github.com/higuseonhye/research-os/blob/master/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1_proper/summary.json) · [Study 2 Isaac summary](https://github.com/higuseonhye/research-os/blob/master/experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/isaac_full_v0.1/summary.json)

### Tier B (smoke · direction)

| Claim | Evidence |
| --- | --- |
| Same-state counterfactual fork | Fig 4 below |
| Delay band @ 3 cm | Fig 5 below |
| Dreamer tradeoff (desk) | Gaussian higher informative yield · diffusion higher param diversity |

![Mode separation @ fixed S](https://raw.githubusercontent.com/higuseonhye/research-os/master/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1a_isaac/figures/counterfactual_grid.png)

![Recoverability vs replan delay](https://raw.githubusercontent.com/higuseonhye/research-os/master/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1b_isaac/figures/recoverability_vs_delay.png)

---

## What we do not claim

- A new learned recoverability **method** or clinical OR validation
- Diffusion beats Gaussian on **yield** (Study 2 Phase 1: coverage vs diversity framing)
- Registry-style confirmatory claims beyond committed Tier C summaries

---

## Artifacts

- **Code & results:** [research-os](https://github.com/higuseonhye/research-os)
- **Paper 1 status:** [status.md](https://github.com/higuseonhye/research-os/blob/master/docs/paper1/status.md)
- **Experiment loop:** [EXPERIMENT_LOOP.md](https://github.com/higuseonhye/research-os/blob/master/docs/EXPERIMENT_LOOP.md)

---

## Contact

Open to research and evaluation roles where **failure is data** and hypotheses are tested explicitly. Based in Korea · open to **Toronto / remote Canada**.

**GitHub:** [@higuseonhye](https://github.com/higuseonhye) · **Repo:** [research-os](https://github.com/higuseonhye/research-os)

---

*Updated 2026-07-23 · [Edit this page](https://github.com/higuseonhye/research-os/blob/master/docs/index.md)*
