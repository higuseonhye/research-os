# Study 2 — Phase 2 run protocol v0.1

> **Design:** [study2_phase2_design_v0.1.md](study2_phase2_design_v0.1.md) · **Date:** 2026-07-24  
> **Platform:** VESSL Cloud (workspace **kept running** · do not terminate before Leg 3)  
> **Tier target:** B/C (H3′ + tier separation)

---

## Goal

Re-run **selection ablation** on **mock_smoke_v0.4** with **Isaac occlusion aligned** to mock `occlusion_gain`.

| Export | Value |
| --- | --- |
| Mock records | `mock_smoke_v0.4/records_seed{42,43,44}.json` |
| Strategy | `top_bottom` |
| Specs / dreamer | top-5 + bottom-5 |
| Total specs | 20 |
| Seeds / spec | 0–4 |
| Isaac runner | **study1d** · `visibility_fraction = max(0.05, 1.0 − occlusion_gain)` |

---

## Prerequisites

### Leg 0 — Code (merged in research-os)

- [x] `run_study2_isaac_loop.py` supports `--runner study1d` + visibility map
- [x] `sandbox_v0.2.yaml` committed
- [ ] Desk smoke: one spec with occlusion_gain > 0 on VESSL

### Leg 1 — Mock v0.4 (CPU · local or VESSL Jupyter)

```bash
cd /workspace/research-os   # or local repo root
git pull origin master

# Per seed (or loop)
python scripts/run_study2_dream_curriculum_mock.py \
  --config experiments/surgical_intelligence/exp_surg_002_dream_curriculum/config/sandbox_v0.2.yaml \
  --compare --episodes 48 --seed 42 --promote-label mock_smoke_v0.4

python scripts/run_study2_dream_curriculum_mock.py \
  --config experiments/surgical_intelligence/exp_surg_002_dream_curriculum/config/sandbox_v0.2.yaml \
  --compare --episodes 48 --seed 43 --promote-label mock_smoke_v0.4

python scripts/run_study2_dream_curriculum_mock.py \
  --config experiments/surgical_intelligence/exp_surg_002_dream_curriculum/config/sandbox_v0.2.yaml \
  --compare --episodes 48 --seed 44 --promote-label mock_smoke_v0.4
```

Primary export seed for Isaac: **`records_seed43.json`** (same as Phase 1 ablation convention).

---

## VESSL commands (Leg 3)

**Workspace:** keep **Running** or **Paused** (not Terminated) · mount `/workspace` persists while workspace exists.

```bash
cd /workspace/research-os && git pull origin master
tmux new -s study2p2

# Bootstrap (cold only)
STUDY2_PREP_BOOTSTRAP=1 bash scripts/prep_study2_selection_ablation_vessl.sh
# Ctrl+B D

# zero_agent smoke — MUST PASS
cd /workspace/orbit-surgical
export OMNI_KIT_ALLOW_ROOT=1
export IsaacLab_PATH=/workspace/IsaacLab
/workspace/IsaacLab/isaaclab.sh -p source/standalone/environments/zero_agent.py \
  --task Isaac-Reach-Dual-STAR-IK-Rel-Play-v0 --num_envs 1 --headless

# Phase 2 ablation (mock v0.4 + study1d runner)
cd /workspace/research-os
export STUDY2_SKIP_BOOTSTRAP=1
export STUDY2_CONFIG=experiments/surgical_intelligence/exp_surg_002_dream_curriculum/config/sandbox_v0.2.yaml
export STUDY2_RUNNER=study1d
export STUDY2_RECORDS=experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/mock_smoke_v0.4/records_seed43.json
bash scripts/run_study2_selection_ablation_vessl.sh

---

## Pass criteria

| ID | Criterion |
| --- | --- |
| **H3′** | Pooled Spearman ρ ≥ **0.5** on 20-spec pack (`h3_mock_isaac_v0.4/`) |
| **H4′** | `bottom.informative_rate` ≤ **0.6** and `< top` |
| **H5′** | ρ(v0.4) − 0.145 ≥ **0.25** (descriptive lift) |

**FAIL spiral lock:** one ablation run per frozen design · if H4′ FAIL → Phase 3 design (Isaac-first) · no retry on same cell.

---

## Promote (local after run)

```bash
RUN_ID=<from output>
# scp or Jupyter download →
experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/selection_ablation_v0.2/isaac_aggregate.json
```

### H3′ recompute (CPU)

```bash
python scripts/compute_study2_h3_mock_isaac.py \
  --records experiments/.../results/mock_smoke_v0.4/records_seed43.json \
  --strategy top_bottom \
  --isaac-aggregate experiments/.../results/selection_ablation_v0.2/isaac_aggregate.json \
  --out experiments/.../results/h3_mock_isaac_v0.4/summary.json
```

---

## Ops (do not)

- ❌ Terminate VESSL workspace before promote (Pause OK)
- ❌ Re-run Phase 1 top-k confirmatory
- ❌ Extra mock yield at v0.1 config
- ❌ `pkill kit`

---

## Related

- Phase 1 ablation: [selection_ablation_run_protocol_v0.1.md](selection_ablation_run_protocol_v0.1.md)  
- VESSL image: [vessl_isaac_setup_v0.1.md](vessl_isaac_setup_v0.1.md)
