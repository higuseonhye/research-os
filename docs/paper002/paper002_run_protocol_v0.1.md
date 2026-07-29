# Paper 002 — Run protocol v0.1 (superseded)

> **ARCHIVED** · mock→physics direction · superseded **2026-07-29** · **do not cite or extend**
> **Current Paper 002:** [WM expansion](paper002_description_wm_expansion_v0.1.md) · [archive index](archive/mock_to_physics/README.md)

> **Superseded by [paper002_run_protocol_v0.2.md](paper002_run_protocol_v0.2.md)**  
> **Config:** [`sandbox_v0.3.yaml`](../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/config/sandbox_v0.3.yaml)  
> **Platform:** VESSL A100 (Isaac) · CPU local/Jupyter (mock)  
> **Date:** 2026-07-28

---

## Goal

Execute **confirmatory** generative curriculum (Paper 002) at 2× spec count and 1.6× Isaac seeds vs Study 002 Phase 2 pilot, with **rule + LLM** agents.

| Export | Value |
| --- | --- |
| Config | `sandbox_v0.3.yaml` |
| Mock episodes / dreamer | **128** |
| Mock seeds | 42, 43, 44, 45, 46 |
| Primary export | `records_seed43.json` |
| Strategy | `top_bottom` · **top-10 + bottom-10** / dreamer |
| Total specs / agent | **40** |
| Isaac seeds / spec | **0–7** (n=8) |
| Isaac runner | **study1d** · `visibility_fraction = max(0.05, 1.0 − occlusion_gain)` |

---

## Leg 0 — Freeze (local)

```bash
cd C:\projects\research-os
git status   # paper002_prereg_v0.1.md + sandbox_v0.3.yaml committed
```

---

## Leg 1 — LLM curricula (local · before mock)

See [llm_curriculum_protocol_v0.1.md](llm_curriculum_protocol_v0.1.md).

```bash
# Generate prompt (inspect only)
python scripts/run_study2_dream_curriculum_mock.py \
  --config experiments/surgical_intelligence/exp_surg_002_dream_curriculum/config/sandbox_v0.3.yaml \
  --print-agent-prompt --episodes 128

# After LLM fills JSON → validate + store:
# experiments/.../artifacts/llm_curriculum_seed{42,43,44,45,46}_v0.1.json
```

---

## Leg 2 — Mock rule (CPU)

```bash
CFG=experiments/surgical_intelligence/exp_surg_002_dream_curriculum/config/sandbox_v0.3.yaml

for SEED in 42 43 44 45 46; do
  python scripts/run_study2_dream_curriculum_mock.py \
    --config "$CFG" \
    --compare --episodes 128 --seed "$SEED" \
    --agent rule --promote-label mock_confirmatory_v0.1
done
```

**Promote path:** `results/mock_confirmatory_v0.1/records_seed*.json`

---

## Leg 3 — Mock LLM (CPU)

```bash
CFG=experiments/surgical_intelligence/exp_surg_002_dream_curriculum/config/sandbox_v0.3.yaml

for SEED in 42 43 44 45 46; do
  python scripts/run_study2_dream_curriculum_mock.py \
    --config "$CFG" \
    --compare --episodes 128 --seed "$SEED" \
    --agent json-file \
    --agent-json experiments/surgical_intelligence/exp_surg_002_dream_curriculum/artifacts/llm_curriculum_seed${SEED}_v0.1.json \
    --promote-label mock_confirmatory_llm_v0.1
done
```

---

## Leg 4 — Export Isaac specs (CPU)

```bash
python scripts/export_study2_isaac_specs.py \
  --records experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/mock_confirmatory_v0.1/records_seed43.json \
  --strategy top_bottom --top-k 10 \
  --prereg docs/paper002/paper002_prereg_v0.2.md \
  --out experiments/surgical_intelligence/exp_surg_002_dream_curriculum/artifacts/isaac_specs_v0.3_rule.json

python scripts/export_study2_isaac_specs.py \
  --records experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/mock_confirmatory_llm_v0.1/records_seed43.json \
  --strategy top_bottom --top-k 10 \
  --prereg docs/paper002/paper002_prereg_v0.2.md \
  --out experiments/surgical_intelligence/exp_surg_002_dream_curriculum/artifacts/isaac_specs_v0.3_llm.json
```

Expect **40 specs** each.

---

## Leg 5 — Isaac rule ablation (VESSL GPU)

```bash
cd /workspace/research-os && git pull origin master
tmux new -s paper002

# Bootstrap (cold only)
STUDY2_PREP_BOOTSTRAP=1 bash scripts/prep_study2_selection_ablation_vessl.sh

# zero_agent smoke — MUST PASS
cd /workspace/orbit-surgical
export OMNI_KIT_ALLOW_ROOT=1
export IsaacLab_PATH=/workspace/IsaacLab
/workspace/IsaacLab/isaaclab.sh -p source/standalone/environments/zero_agent.py \
  --task Isaac-Reach-Dual-STAR-IK-Rel-Play-v0 --num_envs 1 --headless

# Confirmatory ablation — rule
cd /workspace/research-os
export STUDY2_SKIP_BOOTSTRAP=1
export STUDY2_CONFIG=experiments/surgical_intelligence/exp_surg_002_dream_curriculum/config/sandbox_v0.3.yaml
export STUDY2_RUNNER=study1d
export STUDY2_TOP_K=10
export STUDY2_ISAAC_SEEDS=0,1,2,3,4,5,6,7
export STUDY2_RECORDS=experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/mock_confirmatory_v0.1/records_seed43.json
export STUDY2_SPECS=experiments/surgical_intelligence/exp_surg_002_dream_curriculum/artifacts/isaac_specs_v0.3_rule.json
bash scripts/run_study2_selection_ablation_vessl.sh
```

Note: if `STUDY2_SPECS` is not supported yet, export step embeds specs via records path (existing script behavior). Override env only when script supports explicit specs file.

---

## Leg 6 — Isaac LLM ablation (VESSL GPU)

Same as Leg 5 with:

```bash
export STUDY2_RECORDS=experiments/.../results/mock_confirmatory_llm_v0.1/records_seed43.json
export STUDY2_SPECS=experiments/.../artifacts/isaac_specs_v0.3_llm.json
bash scripts/run_study2_selection_ablation_vessl.sh
```

Promote to `results/selection_ablation_v0.3/` (rule) and `results/selection_ablation_llm_v0.3/` (llm).

---

## Leg 7 — H1–H3 compute (CPU)

```bash
python scripts/compute_study2_h3_mock_isaac.py \
  --records experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/mock_confirmatory_v0.1/records_seed43.json \
  --strategy top_bottom --top-k 10 \
  --isaac-aggregate experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/selection_ablation_v0.3/isaac_aggregate.json \
  --out experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/h3_mock_isaac_v0.3/summary.json

python scripts/compute_study2_h3_mock_isaac.py \
  --records experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/mock_confirmatory_llm_v0.1/records_seed43.json \
  --strategy top_bottom --top-k 10 \
  --isaac-aggregate experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/selection_ablation_llm_v0.3/isaac_aggregate.json \
  --out experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/h3_mock_isaac_llm_v0.3/summary.json
```

Map outputs to H1 (rule ρ), H2 (tier IR), H3 (llm vs rule).

---

## GPU budget (estimate)

| Leg | Est. |
| --- | --- |
| Mock rule + llm (CPU) | ~1 h total |
| Isaac 40 specs × 8 seeds × 2 branches × 2 agents | **~12–16 h** |
| H3 compute | < 10 min |
| **Total** | **~2 workspace-days** |

---

## Promote checklist

- [ ] `mock_confirmatory_v0.1/` · 5 seeds  
- [ ] `mock_confirmatory_llm_v0.1/` · 5 seeds  
- [ ] `selection_ablation_v0.3/isaac_aggregate.json`  
- [ ] `selection_ablation_llm_v0.3/isaac_aggregate.json`  
- [ ] `h3_mock_isaac_v0.3/summary.json`  
- [ ] `h3_mock_isaac_llm_v0.3/summary.json`  
- [ ] Run log: LLM model ID · VESSL RUN_ID · git SHA

---

## Do not

- ❌ Re-run Study 002 Phase 2 cell as confirmatory (different pre-reg)  
- ❌ Change top_k / seeds / runner after Leg 5 starts  
- ❌ Terminate VESSL workspace before promote  
- ❌ Label pilot results (v0.4) as confirmatory

---

## Related

- Pilot: [../stage2/study2_phase2_design_v0.1.md](../stage2/study2_phase2_design_v0.1.md)  
- Kill matrix: [paper002_kill_matrix_v0.1.md](paper002_kill_matrix_v0.1.md)  
- VESSL ops: [../stage2/vessl_isaac_setup_v0.1.md](../stage2/vessl_isaac_setup_v0.1.md)
