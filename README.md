# research-os

> Public Physical AI research portfolio — Paper 001 recoverability @ fixed S (Tier C) · Paper 002 mock-to-physics validation (pre-reg v0.3 · MS under review)

**Public research portfolio** for a focused question in Physical AI: how embodied systems should respond when reality no longer matches their expectations.

This repository contains **promoted research evidence only**—research questions, reproducible experiments, protocols, figures, and clearly tiered claims. It is not a career diary, lab notebook, or private strategy workspace.

| | |
| --- | --- |
| **Paper 001 (EXP-SURG-001)** | After mismatch @ **S**, how do **intervention choice** and **timing** determine **successful resolution**? |
| **Paper 002 (EXP-SURG-003)** | Can a **cheap mock rank** predict **physics-level counterfactual value** before Isaac evaluation? |
| **Study 002 (EXP-SURG-002)** | Pilot: informative-**S** generation (Tier B · archived) |

**Latest (2026-07-28):** **Paper 001 complete** (D0–D3 · working paper live). **Paper 002** pre-reg frozen · pre-results PDF v1.2 **under review** · confirmatory GPU not started.

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
| C | Confirmatory | **Paper 001 D0–D3 executed** (n=20) · **Paper 002** pre-reg frozen · GPU pending |
| — | Pre-results MS | **Paper 002 PDF v1.2 under review** (no confirmatory outcomes) |

We have **not** shown a new recoverability **estimator** or clinical deployment.

---

## Confirmatory highlights (Tier C)

| Track | Result | Summary |
| --- | --- | --- |
| **Paper 001 D0** | REPLAN **19/20** vs CONTINUE **0/20** @ 6 cm + occlusion | [`study1_proper/summary.json`](experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1_proper/summary.json) |
| **Paper 001 D1–D3** | B2 **0%** · B3 **85%** · D1 control descriptive | [`study1_proper_v2/summary.json`](experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1_proper_v2/summary.json) |
| **Paper 001 figures** | Profile · baseline overlay · Isaac EE traces | [`docs/paper1/figures/`](docs/paper1/figures/) |
| **Study 002** | Pilot · mock–Isaac alignment (Tier B) | [`h3_mock_isaac_v0.4`](experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/h3_mock_isaac_v0.4/summary.json) |
| **Paper 002** | Pre-reg frozen · manuscript under review | [`docs/paper002/`](docs/paper002/) · [`status.md`](docs/paper002/status.md) |

Full status: Paper 001 [`docs/paper1/status.md`](docs/paper1/status.md) · Paper 002 [`docs/paper002/status.md`](docs/paper002/status.md)

---

## Start here

| | Link |
| --- | --- |
| Portfolio landing | **[higuseonhye.github.io/research-os](https://higuseonhye.github.io/research-os/)** · [`docs/index.md`](docs/index.md) |
| Paper 1 hub | [`docs/paper1/README.md`](docs/paper1/README.md) |
| Paper 2 hub | [`docs/paper002/README.md`](docs/paper002/README.md) |
| Pre-results PDF (002) | [`docs/paper002/paper002_pre_results_v1.2.pdf`](docs/paper002/paper002_pre_results_v1.2.pdf) · *under review* |
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
| `docs/paper1/` | Paper 001 RQ · status · working paper |
| `docs/paper002/` | Paper 002 pre-reg · pre-results PDF · protocols |
| `docs/stage2/` | Study 002 pilot · archived |
| `scripts/` | Mock + RunPod entry points |

---

## Security

Do **not** commit API keys, credentials, PHI, or collaborator-embargoed material without consent. See [`.gitignore`](.gitignore) and [`docs/PUBLIC_BOUNDARY.md`](docs/PUBLIC_BOUNDARY.md).

**Private by design:** internal reading queues, career and relocation planning, people notes, internal meeting notes, and unpublished strategy are excluded from this repository.