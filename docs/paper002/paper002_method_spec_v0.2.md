# Paper 002 — Method specification v0.2

> **Supersedes:** v0.1 · **Pre-reg:** [paper002_prereg_v0.3.md](paper002_prereg_v0.3.md)  
> **Config:** [`sandbox_v0.4.yaml`](../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/config/sandbox_v0.4.yaml)

---

## Changes from v0.1

| Item | v0.1/v0.2 | **v0.3** |
| --- | --- | --- |
| Primary mock outcome | binary | **continuous `cf_margin`** |
| Export input | seed 43 | **median over seeds 42–46** |
| Export unit | per dreamer | **per planner** (dreamers pooled) |
| H1 claim scope | implicit global | **extreme-export-set** (explicit) |
| Isaac primary score | binary | **continuous median + binary** |
| H2 binomial | pass criterion | **supporting report only** |
| LLM leg gate | H1∧H2 @ rule | **operational feasibility gate** |

---

## Staged execution (v0.3-amend)

```text
rule Isaac → operational gate → LLM Isaac → H1 → H2 → H3 (analysis)
```

Confirmatory H1–H3 are **post-hoc** · not used to skip LLM leg. See [operational gate](paper002_operational_gate_v0.1.md).

All other v0.1 content (occlusion contract · dreamers · agents · Isaac majority) unchanged unless noted here.

---

## Continuous mock score

See `mock_reach.cf_margin()` — success gap + normalized distance gap + violation lift.

**Ranking:** Spearman on continuous scores only for H1/H3.

**Consensus:**

```bash
python scripts/merge_study2_mock_consensus.py \
  --results-dir experiments/.../results/mock_confirmatory_v0.1 \
  --seeds 42,43,44,45,46 \
  --planner rule \
  --out experiments/.../artifacts/consensus_rule_v0.3.json
```

---

## Export (within-planner)

```bash
python scripts/export_study2_isaac_specs.py \
  --records experiments/.../artifacts/consensus_rule_v0.3.json \
  --scope planner --planner rule \
  --strategy top_bottom --top-k 10 \
  --out experiments/.../artifacts/isaac_specs_rule_v0.3.json
```

→ **20 specs** (10 top + 10 bottom) per planner · **40 total**.

Tie-break: higher mock_score · then lexicographic spec_id.

---

## Manifest checksum

Before Isaac Leg 5:

```bash
# PowerShell
Get-FileHash experiments/.../artifacts/isaac_specs_rule_v0.3.json -Algorithm SHA256
```

Record in export `--manifest-checksum` and run log.

---

## Full method reference

Sections 1–10 from [paper002_method_spec_v0.1.md](paper002_method_spec_v0.1.md) remain valid except where this v0.2 doc overrides export and scoring.

Manuscript detail: [paper002_manuscript_pre_results_v0.1.md](paper002_manuscript_pre_results_v0.1.md).
