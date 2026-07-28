# EXP-SURG-002 / EXP-SURG-003 — Dream curriculum

> **Study 002 (pilot):** Phase 1–2 complete · Tier B · archived  
> **Paper 002 (confirmatory):** pre-reg frozen · [`docs/paper002/`](../../../docs/paper002/) · config `sandbox_v0.3.yaml`  
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
| [`selection_ablation_v0.1/`](results/selection_ablation_v0.1/) | B | top/bottom IR 1.0 vs 0.8 · study1a |
| [`h3_mock_isaac_v0.2/`](results/h3_mock_isaac_v0.2/) | B | H3 20-spec · ρ=0.15 FAIL |
| [`selection_ablation_v0.2/`](results/selection_ablation_v0.2/) | B | study1d · top 1.0 · bottom **0.3** |
| [`h3_mock_isaac_v0.4/`](results/h3_mock_isaac_v0.4/) | B | H3′ ρ=**0.899** PASS |

**Honest read (2026-07-24):** mock — Gaussian higher informative yield, diffusion higher param diversity. Isaac top-k ceiling (5/5) broken at **bottom tier** (8/10). Tier direction PASS (top 1.0 vs bottom 0.8). H3 per-spec ρ=0.15 — rank correlation **not supported**; mock tier not a strong continuous predictor.

## Phase 2 (executed · 2026-07-24)

**RUN_ID** `20260724T053134Z` · H3′ **ρ=0.899 PASS** · H4′ top 1.0 / bottom **0.3 PASS** · study1d occlusion align.

→ [`study2_phase2_design_v0.1.md`](../../../docs/stage2/study2_phase2_design_v0.1.md) · results [`selection_ablation_v0.2/`](results/selection_ablation_v0.2/) · [`h3_mock_isaac_v0.4/`](results/h3_mock_isaac_v0.4/)

## Boundary

- **Not** Paper 1 confirmatory · parallel probe (discovery voice)
- **Not** full ReSYNC / IVNTR — perturbation-param dreaming only (v0.1)
- Public repo: frozen design + tier-labeled results only (see [`PUBLIC_BOUNDARY.md`](../../../docs/PUBLIC_BOUNDARY.md))

## Paper 002 confirmatory (execute next)

Pre-reg: [`paper002_prereg_v0.1.md`](../../../docs/paper002/paper002_prereg_v0.1.md) · protocol: [`paper002_run_protocol_v0.1.md`](../../../docs/paper002/paper002_run_protocol_v0.1.md)

```bash
# Mock (CPU) — after LLM curricula generated
python scripts/run_study2_dream_curriculum_mock.py \
  --config experiments/surgical_intelligence/exp_surg_002_dream_curriculum/config/sandbox_v0.3.yaml \
  --compare --episodes 128 --seed 43 --agent rule --promote-label mock_confirmatory_v0.1

# Isaac (GPU) — see run protocol Leg 5
export STUDY2_CONFIG=experiments/surgical_intelligence/exp_surg_002_dream_curriculum/config/sandbox_v0.3.yaml
export STUDY2_TOP_K=10
export STUDY2_ISAAC_SEEDS=0,1,2,3,4,5,6,7
```
