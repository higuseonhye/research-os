# research-os

**Public research portfolio** for a focused question in Physical AI: how embodied systems should respond when reality no longer matches their expectations.

This repository contains **promoted research evidence only**—research questions, reproducible experiments, protocols, figures, and clearly tiered claims. It is not a career diary, lab notebook, or private strategy workspace.

| | |
| --- | --- |
| **Paper 001 (EXP-SURG-001)** | After mismatch @ **S**, how do **intervention choice** and **timing** determine **successful resolution**? |
| **Study 002 (EXP-SURG-002)** | Which dreamed scenarios are **informative** (CONTINUE fail ∧ REPLAN success)? Gaussian vs diffusion dreaming. |

**Platform:** Isaac Sim 4.1 · ORBIT Dual-STAR Reach · same-state counterfactual fork.

**Latest (2026-07-24):** **Paper 001 proper program complete** (D0–D3 · pre-reg v2.0 · VESSL) — REPLAN **19/20** vs CONTINUE **0/20** @ fixed **S**; RQ-B menu **95%** > B2 **0%** > B3 **85%**. Figures + Isaac EE traces in [`docs/paper1/figures/`](docs/paper1/figures/). Study 2 selection ablation executed on VESSL.

---

## Research direction

**Long-term vision:** Physical AI for the Non-Average World.

**Near-term program:** build measurable protocols for recognizing and resolving task-relevant mismatch, with emphasis on recoverability, intervention choice, timing, and human–AI collaboration.

**Current scope:** controlled simulation studies. This repository does not claim clinical deployment, a complete theory of exception-aware intelligence, or a general recoverability estimator.

---

## Claim tier (honest)

| Tier | Label | Status |
| --- | --- | --- |
| A | Scaffold / protocol | Same-state CF pipeline · replay OK |
| B | Smoke / direction | 001A–D smoke atlas · Study2 desk mock |
| C | Confirmatory | **Paper 001 D0–D3 executed** (n=20) · **Study 2** Phase 1 + ablation |

We have **not** shown a new recoverability **estimator** or clinical deployment.

---

## Confirmatory highlights (Tier C)

| Track | Result | Summary |
| --- | --- | --- |
| **Paper 001 D0** | REPLAN **19/20** vs CONTINUE **0/20** @ 6 cm + occlusion | [`study1_proper/summary.json`](experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1_proper/summary.json) |
| **Paper 001 D1–D3** | B2 **0%** · B3 **85%** · D1 control descriptive | [`study1_proper_v2/summary.json`](experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1_proper_v2/summary.json) |
| **Paper 001 figures** | Profile · baseline overlay · Isaac EE traces | [`docs/paper1/figures/`](docs/paper1/figures/) |
| **Study 002** | Mock yield vs diversity · Isaac ablation on VESSL | [`isaac_full_v0.1`](experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/isaac_full_v0.1/summary.json) · [`mock_smoke_v0.2`](experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/mock_smoke_v0.2/summary.json) |

Full status: [`docs/paper1/status.md`](docs/paper1/status.md)

---

## Start here

| | Link |
| --- | --- |
| Portfolio landing | **[higuseonhye.github.io/research-os](https://higuseonhye.github.io/research-os/)** · [`docs/index.md`](docs/index.md) |
| Paper 1 hub | [`docs/paper1/README.md`](docs/paper1/README.md) |
| Research question v1.0 | [`docs/paper1/research_question.md`](docs/paper1/research_question.md) |
| EXP-SURG-001 | [`experiments/.../exp_surg_001_execute_or_defer/README.md`](experiments/surgical_intelligence/exp_surg_001_execute_or_defer/README.md) |
| EXP-SURG-002 | [`experiments/.../exp_surg_002_dream_curriculum/README.md`](experiments/surgical_intelligence/exp_surg_002_dream_curriculum/README.md) |
| Fig · D0 profile (Tier C) | [fig3_profile_d0.png](docs/paper1/figures/fig3_profile_d0.png) |
| Fig · baseline overlay | [fig4_baseline_overlay.png](docs/paper1/figures/fig4_baseline_overlay.png) |
| Fig · Isaac EE traces | [sim_panel_isaac_traces.png](docs/paper1/figures/sim_panel_isaac_traces.png) |
| Fig · smoke (Tier B) | [counterfactual_grid.png](experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1a_isaac/figures/counterfactual_grid.png) |
| Experiment loop | [`docs/EXPERIMENT_LOOP.md`](docs/EXPERIMENT_LOOP.md) |
| Repro scripts | [`scripts/README.md`](scripts/README.md) |
| Public boundary | [`docs/PUBLIC_BOUNDARY.md`](docs/PUBLIC_BOUNDARY.md) |

---

## Smoke atlas (Tier B · direction)

| Study | Finding | Report |
| --- | --- | --- |
| **001A** @ 3 cm | CONTINUE **0/5** vs REPLAN **4/5** | [study1a_report.md](experiments/surgical_intelligence/exp_surg_001_execute_or_defer/study1a_report.md) |
| **001B** | REPLAN flat delay 0–20 | [study1b_report.md](experiments/surgical_intelligence/exp_surg_001_execute_or_defer/study1b_report.md) |
| **001C** | No timing cliff in tested grid | [study1c_report.md](experiments/surgical_intelligence/exp_surg_001_execute_or_defer/study1c_report.md) |
| **001D** | Multi-mode smoke → Phase C cell | [study1d_report.md](experiments/surgical_intelligence/exp_surg_001_execute_or_defer/study1d_report.md) |

---

## Quick repro

```bash
# Paper 001
python scripts/run_study1a.py --mock
export STUDY1D_FULL=1
export STUDY1D_SEEDS=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19
bash scripts/run_study1d_runpod.sh

# Study 002 (CPU mock · Isaac RunPod)
python scripts/run_study2_dream_curriculum_mock.py --compare --episodes 48
bash scripts/run_study2_dream_curriculum_smoke_runpod.sh
```

Bootstrap: [`scripts/bootstrap_orbit_surgical_runpod.sh`](scripts/bootstrap_orbit_surgical_runpod.sh)

---

## Repository layout

| Path | Contents |
| --- | --- |
| `experiments/surgical_intelligence/exp_surg_001_*` | Paper 1 configs · reports · Tier B/C results |
| `experiments/surgical_intelligence/exp_surg_002_*` | Study 2 dream curriculum · mock + Isaac summaries |
| `docs/paper1/` | Locked RQ · status · Phase C pre-reg |
| `docs/portfolio/` | Landing page copy |
| `docs/stage2/` | Study 2 frozen design · public index |
| `scripts/` | Mock + RunPod entry points |

---

## Security

Do **not** commit API keys, credentials, PHI, or embargoed co-author material. See [`.gitignore`](.gitignore) and [`docs/PUBLIC_BOUNDARY.md`](docs/PUBLIC_BOUNDARY.md).

**Private by design:** internal reading queues, career and relocation planning, people notes, lab feedback, and unpublished strategy are excluded from this repository.