# Paper 002 — Operational gate v0.1

> **ARCHIVED** · mock→physics direction · superseded **2026-07-29** · **do not cite or extend**
> **Current Paper 002:** [WM expansion](paper002_description_wm_expansion_v0.1.md) · [archive index](archive/mock_to_physics/README.md)

> **Type:** engineering feasibility · **not** confirmatory hypothesis gate  
> **When:** after rule-planner Isaac leg · before LLM-planner Isaac leg  
> **Pre-reg:** [paper002_prereg_v0.3.md](paper002_prereg_v0.3.md) §8

---

## Purpose

Rule Isaac runs first for **pipeline validation** and cost ordering. Whether to continue to the LLM Isaac leg is governed by **prespecified engineering criteria** — not by H1/H2 pass/fail on rule data.

Confirmatory hypotheses **H1 → H2 → H3** are evaluated **only after both planner legs complete** (or after rule-only leg if operational gate fails and LLM leg is skipped).

---

## Continue to LLM Isaac when ALL true

| # | Criterion | Measurement | Pass |
| ---: | --- | --- | --- |
| 1 | **Run completion** | Rule export specs where both CONTINUE and REPLAN branches started | ≥ **90%** (≥ 18/20) |
| 2 | **Valid-seed rate** | Rule export specs with ≥ 4 valid seed pairs | ≥ **80%** (≥ 16/20) |
| 3 | **Transfer contract** | Failures tagged occlusion-map / study1d / visibility | No **systematic** pattern (>50% failures same category) |
| 4 | **Metric non-degeneracy** | Binary informative across 20 rule specs | Not all 0 · not all 1 |

---

## If gate fails

| Action | Rationale |
| --- | --- |
| **Do not** run LLM Isaac leg | Physics pipeline not validated |
| **Do not** revise export manifest from rule outcomes | Pre-reg integrity |
| Report as **feasibility / engineering study** | H3 not evaluable |
| H1/H2 on rule data may be reported **exploratory Tier B** only | Not confirmatory |

---

## If gate passes but H1/H2 later fail

LLM leg still ran under valid engineering assumptions. Confirmatory analysis proceeds hierarchically on prespecified populations:

1. H1 · H2 @ rule export set (n=20)  
2. H3 @ rule vs LLM (if LLM leg completed)

Rule H1/H2 failure does **not** retroactively invalidate LLM leg — but manuscript framing follows [kill matrix](paper002_kill_matrix_v0.1.md).

---

## Log fields (required)

```json
{
  "operational_gate": {
    "rule_export_n": 20,
    "run_completion_rate": 0.0,
    "valid_seed_rate": 0.0,
    "transfer_failures_by_category": {},
    "informative_rate_rule_set": 0.0,
    "go_llm_leg": true,
    "timestamp_utc": ""
  }
}
```
