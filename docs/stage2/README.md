# Study 2 — dream curriculum (public)

> **Experiment:** EXP-SURG-002 · parallel to Paper 1 · not Paper 1 confirmatory  
> **Status (2026-07-24):** Phase 1 complete · **Phase 2 executed** (H3′ ρ=0.899 PASS)

---

## Start here

| Doc | Purpose |
| --- | --- |
| [**Phase 1 design v0.1**](study2_phase1_design_v0.1.md) | Frozen hypotheses · Phase 1 outcomes |
| [**Phase 2 design v0.1**](study2_phase2_design_v0.1.md) | Mock–Isaac alignment · H3′ · ablation v0.2 |
| [**Phase 2 run protocol**](study2_phase2_run_protocol_v0.1.md) | VESSL legs · promote · pass criteria |
| [**Selection ablation protocol**](selection_ablation_run_protocol_v0.1.md) | Phase 1 ablation (executed) |
| [**VESSL Isaac setup v0.1**](vessl_isaac_setup_v0.1.md) | Workspace kept · Jupyter |
| [**EXP-SURG-002 README**](../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/README.md) | Quick start · results table |
| [**Sandbox v0.2 config**](../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/config/sandbox_v0.2.yaml) | Phase 2 parameters |

---

## Committed results (Phase 1)

| Label | Tier | Summary |
| --- | --- | --- |
| [`mock_smoke_v0.2/`](../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/mock_smoke_v0.2/) | B | 3-seed mock · G vs D |
| [`h3_mock_isaac_v0.1/`](../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/h3_mock_isaac_v0.1/) | B | H3 top-k · ρ=null |
| [`selection_ablation_v0.1/`](../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/selection_ablation_v0.1/) | B | top/bottom IR 1.0 vs 0.8 |
| [`h3_mock_isaac_v0.2/`](../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/h3_mock_isaac_v0.2/) | B | H3 20-spec · ρ=0.15 FAIL |
| [`isaac_full_v0.1/`](../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/isaac_full_v0.1/) | C | Phase 1 Isaac top-k |

**Phase 2 pending:** `mock_smoke_v0.4` · `selection_ablation_v0.2` · `h3_mock_isaac_v0.4`

| Label | Tier | Summary |
| --- | --- | --- |
| [`mock_smoke_v0.4/`](../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/mock_smoke_v0.4/) | B | v0.2 dream space · seeds 42–44 |
| [`selection_ablation_v0.2/`](../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/selection_ablation_v0.2/) | B | study1d · top 1.0 · bottom 0.3 |
| [`h3_mock_isaac_v0.4/`](../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/h3_mock_isaac_v0.4/) | B | H3′ ρ=**0.899** PASS |

---

## Public boundary

- **In repo:** frozen design · repro code · tier-labeled summaries · honest pass/fail
- **Not in repo:** L1 program narrative · paper outline · internal execution logs · career material

See [`docs/PUBLIC_BOUNDARY.md`](../PUBLIC_BOUNDARY.md).
