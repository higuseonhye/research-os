# Paper 002 — Pre-registration v0.2 (superseded)

> **Superseded by [paper002_prereg_v0.3.md](paper002_prereg_v0.3.md)** · not executed  
> **Experiment:** EXP-SURG-003 · confirmatory generative curriculum  
> **Method:** [paper002_method_spec_v0.1.md](paper002_method_spec_v0.1.md)  
> **Analysis:** [paper002_analysis_plan_v0.1.md](paper002_analysis_plan_v0.1.md)  
> **RQ:** [paper002_rq_v0.2.md](paper002_rq_v0.2.md)  
> **Config:** [`sandbox_v0.3.yaml`](../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/config/sandbox_v0.3.yaml)  
> **Pilot:** Study 002 Phase 1–2 · Tier B · [`../stage2/`](../stage2/)  
> **Date frozen:** 2026-07-28

---

## 1. Design summary

| Parameter | Study 002 Phase 2 (pilot) | **Paper 002 confirmatory** |
| --- | --- | --- |
| Mock episodes / dreamer | 48 | **128** |
| Mock seeds | 3 (42–44) | **5 (42–46)** |
| Export | top-5 + bottom-5 | **top-10 + bottom-10** |
| Specs / dreamer | 10 | **20** |
| **Total Isaac specs / agent** | 20 | **40** |
| Isaac seeds / spec | 5 | **8 (0–7)** |
| Isaac informative @ spec | single-seed impl. | **majority ≥ 5/8 seeds** |
| Agents | rule only | **rule · llm-json** |
| Isaac runner | study1d | **study1d** · gain_scale_flag v0.1 |
| Primary export seed | 43 | **43** (sensitivity: 42, 44, 45, 46) |

---

## 2. Primary hypotheses (hierarchical)

Test **H1 → H2 → H3** in order. Leg 6 (LLM Isaac) runs **only if H1 and H2 PASS** @ rule.

### H1 — Mock–Isaac rank correlation (rule agent)

> Pooled Spearman ρ(mock_informative, isaac_informative) ≥ **0.5** on the **40-spec** top+bottom pack from `mock_confirmatory_v0.1/records_seed43.json`.

**Pass (all):**

- ρ ≥ 0.5 · `reason: ok` · n ≥ **36** after exclusions
- Bootstrap 95% CI lower bound (B=2000) > **0.25**

**Pilot anchor:** Study 002 H3′ ρ=0.899 @ n=20 · confirmatory threshold **lowered** for replication conservatism.

### H2 — Tier separation (rule agent)

> On Isaac @ rule: `IR_bottom` ≤ **0.5** AND `tier_gap` ≥ **0.4** (pooled tiers · n=20 each).

**Pass (all):**

- Both inequalities
- One-sided binomial: `IR_top` > 0.7 @ n=20 · p < 0.05

**Pilot anchor:** H4′ top 1.0 · bottom 0.3 @ n=20.

### H3 — LLM agent @ Isaac (extension · gated)

> LLM curriculum (prompt v0.1 · [llm_curriculum_protocol_v0.1.md](llm_curriculum_protocol_v0.1.md)) satisfies **both**:

- **H3a (floor):** LLM pooled ρ ≥ **0.5**
- **H3b (non-inferiority):** LLM ρ ≥ rule ρ − **0.15**

**Kill (no LLM claim):** H3a FAIL · or LLM ρ < **0.3**

---

## 3. Secondary / exploratory (not registry failure)

| ID | Analysis | Tier |
| --- | --- | --- |
| **S1** | Export seed sensitivity · ρ for seeds 42–46 · median · IQR | B |
| **S2** | Gaussian vs diffusion · ρ · tier_gap · mock diversity | B |
| **S3** | Permutation null for H1 · shuffle mock labels · 1000 draws | B |
| **S4** | LLM mock yield vs rule · descriptive | B |

---

## 4. Agents (frozen)

| Agent | Mode | Outputs |
| --- | --- | --- |
| **Rule** | `rule` | Taxonomy cycle goals |
| **LLM** | `json-file` | Goal JSON per seed · dreamer draws params |

**LLM model ID:** recorded once in `artifacts/llm_run_log_v0.1.json` before mock Leg 3 · no mid-study swap.

---

## 5. Metrics (frozen)

| Metric | Definition |
| --- | --- |
| **mock_informative** | CONTINUE fail ∧ REPLAN ok · mock CF · deterministic per spec |
| **isaac_informative** | Majority ≥ 5/8 seeds: CONTINUE fail ∧ REPLAN_d0 ok |
| **informative_rate (IR)** | #informative / #specs in stratum |
| **tier_gap** | IR_top − IR_bottom |
| **ρ** | Spearman on per-spec binary flags |

---

## 6. Exclusions

| Case | Action |
| --- | --- |
| Isaac spec run error | Exclude spec · log in aggregate |
| < 4 valid seed pairs | Exclude spec |
| Dedupe collision at export | First in rank wins (frozen algorithm) |

Report `n_analyzed` · `n_excluded` in all summaries.

---

## 7. Execution legs

| Leg | Work | Gate |
| ---: | --- | --- |
| 0 | Commit v0.2 pre-reg + method + analysis | — |
| 1 | LLM curricula · 5 seeds · schema valid | — |
| 2 | Mock rule · 5 seeds · `mock_confirmatory_v0.1` | CPU |
| 3 | Mock LLM · 5 seeds · `mock_confirmatory_llm_v0.1` | CPU |
| 4 | Export · seed 43 · 40 specs / agent | CPU |
| 5 | Isaac rule ablation | GPU · zero_agent smoke |
| 6 | Isaac LLM ablation | GPU · **H1∧H2 pass** |
| 7 | Analysis per [paper002_analysis_plan_v0.1.md](paper002_analysis_plan_v0.1.md) | CPU |

---

## 8. Stop rules

| Outcome | Action |
| --- | --- |
| H1∧H2∧H3 pass | Tier A paper |
| H1∧H2 pass · H3 fail | Tier B · no LLM claim |
| H1 pass · H2 fail | Stop · tier filter unreliable |
| H1 fail | Stop · skip Leg 6 · negative doc |

**One Isaac ablation per agent per frozen design.** No retry on same cell without v0.3 pre-reg.

---

## Version history

| Version | Date | Note |
| --- | --- | --- |
| v0.1 | 2026-07-28 | Desk draft · superseded |
| **v0.2** | 2026-07-28 | Method spec · hierarchical tests · Isaac majority · H3 non-inferiority |
