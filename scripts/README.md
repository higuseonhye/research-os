# Scripts — EXP-SURG-001 repro

| Script | Purpose |
| --- | --- |
| `run_study1a.py` | Local mock pipeline |
| `run_study1a_counterfactual_runpod.sh` | Isaac 001A on RunPod |
| `orbit_reach_study1a_counterfactual.py` | 001A counterfactual runner |
| `plot_study1a_isaac_results.py` | Fig 4 from aggregate |
| `run_study1b_timing_runpod.sh` | Isaac 001B |
| `plot_study1b_timing_curve.py` | Fig 5 from aggregate |
| `run_study1c.py` | 001C orchestrator / merge |
| `run_study1c_severity_runpod.sh` | Isaac 001C grid on RunPod |
| `run_study1d.py` | 001D orchestrator / merge |
| `run_study1d_runpod.sh` | Isaac 001D D0 smoke on RunPod |
| `orbit_reach_study1d_counterfactual.py` | 001D Isaac runner |
| `copy_study1c_figures_to_results.sh` | Commit figures from pod |
| `bootstrap_orbit_surgical_runpod.sh` | ORBIT/Isaac bootstrap |
| `orbit_reach_scripted_smoke.py` | Scripted controller smoke |
| `cloud_preflight.sh` | GPU preflight |

---

## Artifacts

- Committed: `experiments/.../results/study1a_isaac/`, `study1b_isaac/`, `study1c_isaac/`
- Pod-only (gitignored): `experiments/.../artifacts/`
