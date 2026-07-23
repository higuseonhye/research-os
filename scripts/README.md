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
| `run_study1d_runpod.sh` | Isaac 001D D0 smoke / D1 full on RunPod |
| `orbit_reach_study1d_counterfactual.py` | 001D Isaac runner |
| `copy_study1c_figures_to_results.sh` | Commit figures from pod |
| `copy_study1d_results_from_pod.sh` | scp full 001D JSON to results/ |
| `copy_study1_proper_from_pod.sh` | scp Phase C n=20 JSON to study1_proper/ |
| `bootstrap_orbit_surgical_runpod.sh` | ORBIT/Isaac bootstrap |
| `orbit_reach_scripted_smoke.py` | Scripted controller smoke |
| `cloud_preflight.sh` | GPU preflight |

### EXP-SURG-002 (Stage 1 · dream curriculum)

| Script | Purpose |
| --- | --- |
| `run_study2_dream_curriculum_mock.py` | CPU mock · gaussian vs diffusion |
| `run_study2_dream_curriculum_runpod.sh` | Phase 1 mock → Isaac loop |
| `run_study2_dream_curriculum_smoke_runpod.sh` | Isaac smoke only (skip mock, TOP_K=2) |
| `export_study2_isaac_specs.py` | Top-k specs from mock records |
| `run_study2_selection_ablation_runpod.sh` | Top-k + bottom-k selection ablation on RunPod |
| `prep_study2_selection_ablation_runpod.sh` | Pod prep: pull repo, export preview, optional bootstrap |
| `merge_study2_isaac_results.py` | Aggregate per-spec Isaac JSON |
| `compute_study2_h3_mock_isaac.py` | H3 Spearman ρ mock vs Isaac top-k |
| `copy_study2_results_from_pod.sh` | scp Study2 Isaac aggregate from pod |

Pre-reg: `builder-os-private/working/research/stage2/study2_prereg_v0.1.md` (private)

---

## Artifacts

- Committed: `experiments/.../results/study1a_isaac/`, `study1b_isaac/`, `study1c_isaac/`, `study1d_isaac/`
- Pod-only (gitignored): `experiments/.../artifacts/`
