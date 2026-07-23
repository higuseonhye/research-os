# Study 2 — Selection ablation run protocol v0.1

> **Design:** [study2_phase1_design_v0.1.md](study2_phase1_design_v0.1.md) · **Date:** 2026-07-23  
> **Tier target:** B (direction + H3 re-test on 20-spec pack)

---

## Goal

Test whether **mock informative rank** predicts Isaac informativeness when **bottom mock** specs are included (not top-k only).

| Export | Value |
| --- | --- |
| Strategy | `top_bottom` |
| Specs / dreamer | top-5 + bottom-5 (deduped) |
| Total specs | 20 |
| Seeds / spec | 0–4 |
| Mock records | `mock_smoke_v0.2/records_seed43.json` |

---

## Pass criteria (Tier B)

1. `bottom.informative_rate` **<** `top.informative_rate` on ≥1 dreamer, **or**
2. Pooled mock–Isaac Spearman **ρ ≥ 0.5** on 20-spec pack

**Ceiling again:** document blocker · defer harder perturbation cell · no extra mock yield runs.

---

## Pod prerequisites

- Image: `nvcr.io/nvidia/isaac-sim:4.1.0` · RTX 4090 · **On-Demand** preferred
- Access: SSH + tmux (not Web Terminal for long runs)
- **Never** `pkill -9 -f '/isaac-sim/kit/kit'` (kills RunPod sidecar)
- `git pull` → need commit **`21c95ec+`**

---

## Commands (on pod)

```bash
cd /workspace/research-os && git pull origin master
tmux new -s study2

# 1) Bootstrap (cold pod only · ~15–25 min)
STUDY2_PREP_BOOTSTRAP=1 bash scripts/prep_study2_selection_ablation_runpod.sh
# Ctrl+B D — wait for bootstrap in tmux

# 2) zero_agent smoke — MUST PASS before full ablation
cd /workspace/orbit-surgical
export OMNI_KIT_ALLOW_ROOT=1
export IsaacLab_PATH=/workspace/IsaacLab
/workspace/IsaacLab/isaaclab.sh -p source/standalone/environments/zero_agent.py \
  --task Isaac-Reach-Dual-STAR-IK-Rel-Play-v0 --num_envs 1 --headless

# 3) Full ablation (after smoke PASS)
cd /workspace/research-os
export STUDY2_SKIP_BOOTSTRAP=1
bash scripts/run_study2_selection_ablation_runpod.sh
# note RUN_ID from output: results/study2_dream_curriculum/isaac/<RUN_ID>/
```

**Retry failed specs only:**

```bash
export STUDY2_RUN_ID=<RUN_ID>
export STUDY2_SKIP_BOOTSTRAP=1
bash scripts/retry_study2_isaac_failed_runpod.sh
```

---

## Promote (local PC after pod)

```bash
# Replace RUN_ID · POD_IP · PORT
RUN_ID=20260723TxxxxxxZ
scp -P <PORT> -i ~/.ssh/id_ed25519 \
  root@<POD_IP>:/workspace/research-os/results/study2_dream_curriculum/isaac/$RUN_ID/isaac_aggregate.json \
  experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/selection_ablation_v0.1/isaac_aggregate.json
```

Add `summary.json` with tier **B** · `prereg`: `docs/stage2/study2_phase1_design_v0.1.md`.

---

## H3 recompute (CPU · local or pod)

```bash
python scripts/compute_study2_h3_mock_isaac.py \
  --records experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/mock_smoke_v0.2/records_seed43.json \
  --strategy top_bottom \
  --specs experiments/surgical_intelligence/exp_surg_002_dream_curriculum/artifacts/isaac_specs.json \
  --isaac-aggregate experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/selection_ablation_v0.1/isaac_aggregate.json \
  --out experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/h3_mock_isaac_v0.2/summary.json
```

---

## Related work anchor (why this run)

| Line | Role |
| --- | --- |
| ReSYNC | Which failures to validate — **selection** not yield |
| Dream2Fix | CF recovery eval — same fork, different metric |
| Surgical UQ | Binary baseline — separate leg (Paper 001 B2) |
