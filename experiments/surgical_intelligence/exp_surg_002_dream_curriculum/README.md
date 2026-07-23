# EXP-SURG-002 — Dream curriculum sandbox (Stage 2 probe)

> **Status:** Phase 1 complete · H3 computed (FAIL) · selection ablation Isaac pending  
> **Design (public):** [`docs/stage2/study2_phase1_design_v0.1.md`](../../../docs/stage2/study2_phase1_design_v0.1.md)  
> **Parent:** EXP-SURG-001 perturbation taxonomy + mock reach

## Quick start (no GPU)

```bash
python scripts/run_study2_dream_curriculum_mock.py --dreamer diffusion --agent rule --episodes 32
python scripts/run_study2_dream_curriculum_mock.py --compare --episodes 48
```

## Phase 1 (RunPod)

Frozen design: [`study2_phase1_design_v0.1.md`](../../../docs/stage2/study2_phase1_design_v0.1.md)

```bash
# Smoke (~$1)
bash scripts/run_study2_dream_curriculum_smoke_runpod.sh

# Full confirmatory (bootstrap required on new pod)
export STUDY2_SKIP_MOCK=1
bash scripts/run_study2_dream_curriculum_runpod.sh

# Selection ablation — top-5 + bottom-5 mock rank → Isaac (20 specs · seeds 0–4)
bash scripts/run_study2_selection_ablation_runpod.sh
```

**Pod prep (bootstrap in tmux):**

```bash
STUDY2_PREP_BOOTSTRAP=1 bash scripts/prep_study2_selection_ablation_runpod.sh
```

Promote full `isaac_aggregate.json` from pod: [`scripts/copy_study2_results_from_pod.sh`](../../../scripts/copy_study2_results_from_pod.sh)

## Committed results

| Label | Tier | Content |
| --- | --- | --- |
| [`mock_smoke_v0.2/`](results/mock_smoke_v0.2/) | B | 3-seed mock · rule agent · G vs D |
| [`mock_smoke_v0.3/`](results/mock_smoke_v0.3/) | B | Replicate of v0.2 (deterministic) |
| [`h3_mock_isaac_v0.1/`](results/h3_mock_isaac_v0.1/) | B | H3 Spearman · ρ=null · zero variance |
| [`isaac_smoke_v0.1/`](results/isaac_smoke_v0.1/) | C | Pipeline smoke · top-2 × seeds 0,1 |
| [`isaac_full_v0.1/`](results/isaac_full_v0.1/) | C | Confirmatory summary · top-5 × seeds 0–4 |

**Honest read (2026-07-23):** mock — Gaussian higher informative yield, diffusion higher param diversity. Isaac top-k — both dreamers 5/5 informative (ceiling); primary yield hypothesis not supported. H3 — mock rank does not discriminate Isaac informativeness at top-k protocol (ρ undefined). Selection ablation (top+bottom mock rank) **pending** Isaac retry.

## Boundary

- **Not** Paper 1 confirmatory · parallel probe (discovery voice)
- **Not** full ReSYNC / IVNTR — perturbation-param dreaming only (v0.1)
- Public repo: frozen design + tier-labeled results only (see [`PUBLIC_BOUNDARY.md`](../../../docs/PUBLIC_BOUNDARY.md))

## Next (Paper program)

Paper 001 Phase C proper run (n=20) complete — see [`docs/paper1/status.md`](../../../docs/paper1/status.md).
