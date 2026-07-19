# research-os

Reproducible evidence for **intervention-conditioned recoverability** in constrained surgical reaching (EXP-SURG-001 · Paper 1).

Platform: Isaac Sim · ORBIT Dual-STAR Reach · scripted 6D IK-Rel proposer.

---

## Scope (Jul 2026)

> We have **not** yet shown a new recoverability method. We established a **same-state counterfactual simulator** that measures how **response choice and timing** affect **successful resolution** after task-relevant mismatch (n=5/cell smoke scale).

---

## Start here

| | Link |
| --- | --- |
| Paper 1 summary | [`docs/paper1/README.md`](docs/paper1/README.md) |
| Experiment hub | [`experiments/surgical_intelligence/exp_surg_001_execute_or_defer/README.md`](experiments/surgical_intelligence/exp_surg_001_execute_or_defer/README.md) |
| Fig 4 · Fig 5 | [counterfactual_grid.png](experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1a_isaac/figures/counterfactual_grid.png) · [recoverability_vs_delay.png](experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1b_isaac/figures/recoverability_vs_delay.png) |
| Repro scripts | [`scripts/README.md`](scripts/README.md) |
| Benchmark schema | [`benchmarks/orbit_recoverability_v0/`](benchmarks/orbit_recoverability_v0/README.md) |

---

## Stage 1 results (Isaac)

| Study | Result | Report |
| --- | --- | --- |
| **001A** @ 3 cm | CONTINUE **0/5** vs REPLAN **4/5** | [study1a_report.md](experiments/surgical_intelligence/exp_surg_001_execute_or_defer/study1a_report.md) |
| **001B** @ 3 cm | REPLAN flat delay 0–20 | [study1b_report.md](experiments/surgical_intelligence/exp_surg_001_execute_or_defer/study1b_report.md) |
| **001C** | No timing cliff in tested grid | [study1c_report.md](experiments/surgical_intelligence/exp_surg_001_execute_or_defer/study1c_report.md) |

Evidence status: [`docs/paper1/status.md`](docs/paper1/status.md)

---

## Quick repro

```bash
python scripts/run_study1a.py --mock
bash scripts/run_study1a_counterfactual_runpod.sh
bash scripts/run_study1c_severity_runpod.sh
```

Bootstrap: [`scripts/bootstrap_orbit_surgical_runpod.sh`](scripts/bootstrap_orbit_surgical_runpod.sh)

---

## Repository layout

| Path | Contents |
| --- | --- |
| `experiments/surgical_intelligence/exp_surg_001_execute_or_defer/` | Configs · reports · committed Isaac aggregates |
| `docs/paper1/` | Research question · status · figure captions |
| `scripts/` | Local mock and RunPod repro entry points |
| `benchmarks/orbit_recoverability_v0/` | JSON schema for recoverability profiles |
| `datasets/` | Manifest pointers used by ORBIT Reach smokes |

---

## Security

Do not commit API keys, credentials, PHI, or embargoed co-author material.
