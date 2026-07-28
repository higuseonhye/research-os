# Paper 002 — LLM curriculum protocol v0.1

> **Pre-reg:** [paper002_prereg_v0.1.md](paper002_prereg_v0.1.md)  
> **Prompt version:** v0.1 · **Schema:** [`llm_curriculum_schema_v0.1.json`](../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/artifacts/llm_curriculum_schema_v0.1.json)

---

## Purpose

Produce **frozen** LLM curriculum JSON files for Paper 002 confirmatory mock runs. Study 002 tested LLM only as exploratory mock — **never @ Isaac**. This protocol closes that gap.

---

## Workflow

1. **Print prompt** (128 episodes · taxonomy from Paper 001):

```bash
python scripts/run_study2_dream_curriculum_mock.py \
  --config experiments/surgical_intelligence/exp_surg_002_dream_curriculum/config/sandbox_v0.3.yaml \
  --print-agent-prompt --episodes 128
```

2. **Call LLM** with:
   - System: output JSON array only · no markdown fences
   - User: printed prompt + instruction to vary families across episodes
   - **Record:** model ID · temperature · date in `artifacts/llm_run_log_v0.1.json`

3. **Validate** each file against schema (128 items · valid families/severities)

4. **Save** per seed (mock RNG seed = curriculum file seed):

```
experiments/surgical_intelligence/exp_surg_002_dream_curriculum/artifacts/
  llm_curriculum_seed42_v0.1.json
  llm_curriculum_seed43_v0.1.json
  ...
  llm_curriculum_seed46_v0.1.json
```

5. **Run mock** with `--agent json-file --agent-json <path>` (see run protocol Leg 3)

---

## Frozen prompt v0.1 (canonical)

```
Design a failure-eliciting curriculum for surgical reach mock (EXP-SURG-003 / Paper 002).

Read generator_families from:
experiments/surgical_intelligence/exp_surg_001_execute_or_defer/config/exception_taxonomy.yaml

Output JSON array of 128 objects:
[
  {"episode": 0, "family": "target_shift", "severity": "mid", "rationale": "..."},
  ...
]

Rules:
- Prioritize scenarios where CONTINUE likely fails but REPLAN succeeds (informative failures).
- Families (only these): target_shift, visual_occlusion, forbidden_region.
- Severities: small, mid, unreachable.
- Cycle all three families across the curriculum.
- Do not repeat the same (family, severity) more than 8 times in a row.
- Output JSON only.
```

---

## Schema constraints

| Field | Type | Allowed |
| --- | --- | --- |
| `episode` | int | 0 … 127 |
| `family` | str | `target_shift` · `visual_occlusion` · `forbidden_region` |
| `severity` | str | `small` · `mid` · `unreachable` |
| `rationale` | str | free text |

**Length:** exactly **128** objects per file.

---

## Model policy

- **One model** for all 5 seeds (record ID in run log)  
- **Temperature:** ≤ 0.7 (reproducibility)  
- **No mid-study model swap** without new pre-reg  
- Acceptable models: any instruction-tuned LLM that outputs valid JSON · record which was used

---

## Pass/fail before GPU

| Check | Pass |
| --- | --- |
| Schema valid | 5/5 files |
| Family coverage | each family ≥ 20% of episodes |
| Mock smoke (seed 43) | runs without error · informative_rate > 0 |

If mock smoke informative_rate = rule ± 5% on seed 43 → **descriptive only** · H3 still runs on Isaac

---

## Honest expectation (from Study 002 pilot)

LLM JSON on mock was **≈ rule** on yield. Paper 002 value is **Isaac validation**, not mock yield claim. Kill matrix applies if LLM adds no Isaac signal.
