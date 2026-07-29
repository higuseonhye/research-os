# Paper 002 — Kill matrix v0.1

> **ARCHIVED** · mock→physics direction · superseded **2026-07-29** · **do not cite or extend**
> **Current Paper 002:** [WM expansion](paper002_description_wm_expansion_v0.1.md) · [archive index](archive/mock_to_physics/README.md)

> **Pre-reg:** [paper002_prereg_v0.2.md](paper002_prereg_v0.2.md)  
> **Date:** 2026-07-28

---

## Decision tree (after Isaac rule leg)

```text
                    Leg 5 complete (rule @ Isaac)
                              │
              ┌───────────────┴───────────────┐
              │                               │
    Operational gate (§8)              Gate FAIL
              │                               │
         GO → Leg 7 LLM Isaac          Feasibility study
              │                         · H3 N/A
              ▼
    Leg 7 complete (both planners)
              │
    Confirmatory H1 → H2 → H3 (analysis only)
```

---

## Hard stops (no retry on same cell)

| Trigger | Action |
| --- | --- |
| **Operational gate FAIL** | Skip LLM Isaac · feasibility report · H3 N/A |
| H1 FAIL (post-hoc) | Confirmatory proxy claim fails · LLM data exploratory |
| H2 FAIL (post-hoc) | Tier filter not supported · report H1 if passed |
| zero_agent smoke FAIL | Fix infra · do not proceed to confirmatory ablation |
| Occlusion map drift | Stop · realign to Paper 001 study1d contract |

---

## Soft outcomes (publishable)

| Outcome | Tier | Paper framing |
| --- | --- | --- |
| Operational gate pass · H1+H2+H3 pass | **A** | Full confirmatory story |
| Operational gate pass · H1+H2 pass · H3 fail | **B** | Proxy + enrichment · no LLM claim |
| Operational gate **fail** (LLM skipped) | **C-feas** | Engineering / feasibility only |
| H1 PASS · H2 FAIL | **B−** | Rank correlation without reliable tier separation |
| H1 FAIL | **C** | Honest negative · pilot H3′ did not replicate at scale |

---

## LLM-specific kills

| Signal | Interpretation |
| --- | --- |
| LLM mock yield = rule · LLM ρ < 0.3 | LLM adds no Isaac signal · appendix only |
| LLM ρ ≥ 0.5 but < rule − 0.15 | Floor pass · non-inferiority fail · cautious LLM wording |
| LLM JSON schema invalid | Regenerate once · if repeat → rule-only study |

---

## Pilot vs confirmatory (do not conflate)

| Label | n specs | Pre-reg | Use in paper |
| --- | --- | --- | --- |
| Study 002 v0.4 | 20 | Phase 2 | **Methods background** · alignment discovery |
| **Paper 002 v0.3** | 40 | This matrix | **Primary confirmatory** |

---

## Escalation (requires new pre-reg)

- Third ablation on identical cell  
- Change dream space bounds  
- Change informative definition  
- Add dreamer type (hybrid) as confirmatory — register as H6 exploratory first
