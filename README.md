# research-os

**Open portfolio** for two linked research questions on **non-average embodied failure** — measure recoverability @ fixed state **S**, and generate **informative** failure scenarios for validation.

| | |
| --- | --- |
| **Paper 001 (EXP-SURG-001)** | After mismatch @ **S**, how do **intervention choice** and **timing** determine **successful resolution**? |
| **Study 002 (EXP-SURG-002)** | Which dreamed scenarios are **informative** (CONTINUE fail ∧ REPLAN success)? Gaussian vs diffusion · agentic curriculum |

**Platform:** Isaac Sim 4.1 · ORBIT Dual-STAR Reach · same-state counterfactual fork.

---

## Claim tier (honest)

| Tier | Label | Status |
| --- | --- | --- |
| A | Scaffold / protocol | Same-state CF pipeline · replay OK |
| B | Smoke / direction | 001A–D · Study2 mock · n=5 / desk pilot |
| C | Confirmatory | Phase C + Study2 Isaac pre-regs **frozen · not executed** |

We have **not** shown a new recoverability estimator or clinical deployment.

---

## Start here

| | Link |
| --- | --- |
| Paper 1 hub | [`docs/paper1/README.md`](docs/paper1/README.md) |
| Research question v1.0 | [`docs/paper1/research_question.md`](docs/paper1/research_question.md) |
| EXP-SURG-001 | [`experiments/.../exp_surg_001_execute_or_defer/README.md`](experiments/surgical_intelligence/exp_surg_001_execute_or_defer/README.md) |
| EXP-SURG-002 | [`experiments/.../exp_surg_002_dream_curriculum/README.md`](experiments/surgical_intelligence/exp_surg_002_dream_curriculum/README.md) |
| Fig · mode separation | [counterfactual_grid.png](experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1a_isaac/figures/counterfactual_grid.png) |
| Fig · delay band | [recoverability_vs_delay.png](experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1b_isaac/figures/recoverability_vs_delay.png) |
| Repro scripts | [`scripts/README.md`](scripts/README.md) |
| Public boundary | [`docs/PUBLIC_BOUNDARY.md`](docs/PUBLIC_BOUNDARY.md) |

---

## Smoke results (Isaac · Tier B)

| Study | Finding | Report |
| --- | --- | --- |
| **001A** @ 3 cm | CONTINUE **0/5** vs REPLAN **4/5** | [study1a_report.md](experiments/surgical_intelligence/exp_surg_001_execute_or_defer/study1a_report.md) |
| **001B** | REPLAN flat delay 0–20 | [study1b_report.md](experiments/surgical_intelligence/exp_surg_001_execute_or_defer/study1b_report.md) |
| **001C** | No timing cliff in tested grid | [study1c_report.md](experiments/surgical_intelligence/exp_surg_001_execute_or_defer/study1c_report.md) |
| **001D** | Multi-mode smoke (REOBSERVE / RESHAPE) | [study1d_report.md](experiments/surgical_intelligence/exp_surg_001_execute_or_defer/study1d_report.md) |
| **Study2 mock** | Informative yield · Gaussian vs diffusion pilot | [mock_smoke summary](experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/mock_smoke_v0.1/summary.json) |

Evidence status: [`docs/paper1/status.md`](docs/paper1/status.md)

---

## Quick repro

```bash
# Paper 001
python scripts/run_study1a.py --mock
bash scripts/run_study1a_counterfactual_runpod.sh

# Study 002 (CPU)
python scripts/run_study2_dream_curriculum_mock.py --compare --episodes 48
```

Bootstrap: [`scripts/bootstrap_orbit_surgical_runpod.sh`](scripts/bootstrap_orbit_surgical_runpod.sh)

---

## Repository layout

| Path | Contents |
| --- | --- |
| `experiments/surgical_intelligence/exp_surg_001_*` | Paper 1 configs · reports · Isaac aggregates |
| `experiments/surgical_intelligence/exp_surg_002_*` | Study 2 dream curriculum · mock smoke |
| `docs/paper1/` | Locked RQ · smoke review · eval landscape · Phase C summary |
| `docs/stage2/` | Stub only — design docs live in **private** repo |
| `scripts/` | Mock + RunPod entry points |
| `benchmarks/orbit_recoverability_v0/` | Profile JSON schema |

---

## Security

Do **not** commit API keys, credentials, PHI, or embargoed co-author material. See [`.gitignore`](.gitignore) and [`docs/PUBLIC_BOUNDARY.md`](docs/PUBLIC_BOUNDARY.md).

**Private by design:** Stage 2 L1 / Study2 narrative · internal reading workflows · career planning · lab meeting notes → not in this repo.
