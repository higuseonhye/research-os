# Paper 002 — Run protocol v0.2

> **ARCHIVED** · mock→physics direction · superseded **2026-07-29** · **do not cite or extend**
> **Current Paper 002:** [WM expansion](paper002_description_wm_expansion_v0.1.md) · [archive index](archive/mock_to_physics/README.md)

> **Supersedes:** v0.1 execution gates · **Pre-reg:** [paper002_prereg_v0.3.md](paper002_prereg_v0.3.md)  
> **Operational gate:** [paper002_operational_gate_v0.1.md](paper002_operational_gate_v0.1.md)  
> **Smoke:** [paper002_smoke_protocol_v0.1.md](paper002_smoke_protocol_v0.1.md)

---

## Final execution order

```text
 1. v0.3-amend commit + tag
 2. seed-43 smoke (engineering · optional · separate manifest)
 3. LLM curricula · 5 seeds
 4. mock rule · seeds 42–46
 5. mock LLM · seeds 42–46
 6. consensus merge (median) · within-planner export · checksum freeze
 7. rule Isaac engineering leg
 8. operational go/no-go (NOT H1∧H2)
 9. LLM Isaac leg (if go)
10. confirmatory H1 → H2 → H3 analysis
```

---

## Leg 0 — Commit

```bash
cd C:\projects\research-os
git add docs/paper002/ experiments/.../config/sandbox_v0.4.yaml scripts/
git commit -m "Paper 002 pre-reg v0.3-amend: proxy validation design"
git tag paper002-prereg-v0.3
```

---

## Leg 0b — Seed-43 smoke (optional)

See [paper002_smoke_protocol_v0.1.md](paper002_smoke_protocol_v0.1.md).  
**Exclude** from `mock_confirmatory_v0.1` and confirmatory export.

---

## Legs 1–4 — Mock + export (unchanged commands · v0.4 config)

Consensus merge:

```bash
python scripts/merge_study2_mock_consensus.py \
  --results-dir experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/mock_confirmatory_v0.1 \
  --seeds 42,43,44,45,46 --planner rule \
  --out experiments/surgical_intelligence/exp_surg_002_dream_curriculum/artifacts/consensus_rule_v0.3.json
```

Export (within-planner · 20 specs):

```bash
python scripts/export_study2_isaac_specs.py \
  --records experiments/surgical_intelligence/exp_surg_002_dream_curriculum/artifacts/consensus_rule_v0.3.json \
  --scope planner --planner rule --strategy top_bottom --top-k 10 \
  --prereg docs/paper002/paper002_prereg_v0.3.md \
  --out experiments/surgical_intelligence/exp_surg_002_dream_curriculum/artifacts/isaac_specs_rule_v0.3.json
```

Repeat for LLM consensus → `isaac_specs_llm_v0.3.json`.  
Record SHA256 checksum on **both** manifests before Isaac.

---

## Leg 5 — Rule Isaac (engineering)

VESSL commands as v0.1 · env `STUDY2_RECORDS` / specs from **rule manifest only**.

Promote → `results/selection_ablation_rule_v0.3/isaac_aggregate.json`

---

## Leg 6 — Operational go/no-go

Compute from rule aggregate:

- run_completion_rate ≥ 0.90  
- valid_seed_rate ≥ 0.80  
- no systematic transfer failure  
- informative rate not degenerate (0 or 1 for all 20)

Log → `results/operational_gate_v0.1.json`

**If NO-GO:** skip Leg 7 · feasibility report · H3 N/A.

---

## Leg 7 — LLM Isaac (if go)

Same protocol · **LLM manifest only** · promote → `selection_ablation_llm_v0.3/`

---

## Leg 8 — Confirmatory analysis

**After both legs** (or rule-only if NO-GO):

```bash
# H1 + H2 @ rule export set
python scripts/compute_study2_h3_mock_isaac.py \
  --specs experiments/.../artifacts/isaac_specs_rule_v0.3.json \
  --isaac-aggregate experiments/.../results/selection_ablation_rule_v0.3/isaac_aggregate.json \
  --continuous --top-k 10 --strategy top_bottom \
  --prereg-version v0.3-amend \
  --out experiments/.../results/h3_rule_v0.3/summary.json

# H3: repeat on LLM + compare Δρ (analysis notebook or second run)
```

Interpret H1 → H2 → H3 hierarchically per [analysis plan v0.2](paper002_analysis_plan_v0.2.md).

---

## Do not

- ❌ Skip LLM leg because rule H1/H2 fail (confirmatory only · post-hoc)
- ❌ Use seed-43 smoke in consensus export
- ❌ Tune manifest from rule Isaac outcomes
