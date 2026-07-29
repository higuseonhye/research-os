# Paper 002 — Analysis plan v0.1

> **ARCHIVED** · mock→physics direction · superseded **2026-07-29** · **do not cite or extend**
> **Current Paper 002:** [WM expansion](paper002_description_wm_expansion_v0.1.md) · [archive index](archive/mock_to_physics/README.md)

> **Pre-reg:** [paper002_prereg_v0.2.md](paper002_prereg_v0.2.md)  
> **Method:** [paper002_method_spec_v0.1.md](paper002_method_spec_v0.1.md)  
> **Date:** 2026-07-28

---

## 1. Primary endpoints (hierarchical testing)

Test in order · stop interpretation chain on failure:

```text
H1 (ρ rank)  →  H2 (tier IR)  →  H3 (LLM vs rule)
     │                │
     └─ FAIL → no confirmatory claim · optional exploratory report
```

**Multiplicity:** no Bonferroni across H1–H3 (hierarchical gate). Secondary/exploratory: uncorrected · labeled Tier B.

---

## 2. H1 — Mock–Isaac Spearman ρ (rule agent)

**Unit:** one of 40 specs (pooled across dreamers).

| Variable | Source |
| --- | --- |
| Mock score | Binary `mock_informative` ∈ {0, 1} |
| Isaac score | Binary `isaac_informative` ∈ {0, 1} (majority over 8 seeds) |

**Statistic:** Spearman ρ (tie-aware rank correlation · implementation in `compute_study2_h3_mock_isaac.py`).

**Pass criteria (confirmatory):**

1. Pooled ρ ≥ **0.5** · `reason: ok` · n ≥ **36** (after exclusions)
2. One-sided bootstrap 95% CI lower bound > **0.25** (B=2000 · resample specs with replacement)

**Sanity (negative control · Tier B):**

- Permute mock labels within each dreamer × 1000 shuffles → pooled ρ_null median ≈ 0 · report p_empirical = P(ρ_null ≥ ρ_observed)

**Per-dreamer (secondary):** report Gaussian ρ · diffusion ρ · not registry pass/fail.

---

## 3. H2 — Tier separation (rule agent)

**Strata:** `selection_tier` ∈ {top, bottom} · pooled across dreamers (n=20 each).

| Metric | Definition |
| --- | --- |
| `IR_top` | #isaac_informative / n_top |
| `IR_bottom` | #isaac_informative / n_bottom |
| `tier_gap` | IR_top − IR_bottom |

**Pass criteria (both required):**

1. `IR_bottom` ≤ **0.5**
2. `tier_gap` ≥ **0.4**
3. One-sided binomial: `IR_top` > 0.7 with n=20 · p < 0.05 (H₀: p_top ≤ 0.7)

**Secondary:** per-dreamer tier IR · Fisher exact top vs bottom 2×2.

---

## 4. H3 — LLM agent (runs only if H1+H2 PASS @ rule)

**Comparison:** same metrics on LLM mock export + LLM Isaac ablation.

**Pass criteria (both required for LLM claim):**

1. **H3a — Floor:** LLM pooled ρ ≥ **0.5** · `reason: ok`
2. **H3b — Non-inferiority:** LLM ρ ≥ rule ρ − **0.15**

**Descriptive (not pass/fail):**

- `tier_gap_llm` vs `tier_gap_rule`
- `IR_bottom_llm` vs `IR_bottom_rule`

**Kill (no LLM body claim):** H3a FAIL · or H3b FAIL with LLM ρ < 0.3

---

## 5. Secondary / exploratory

| ID | Analysis |
| --- | --- |
| **S1** | Export seed sensitivity: ρ for seeds 42–46 · report median · IQR |
| **S2** | Gaussian vs diffusion ρ · tier_gap · param_diversity (mock) |
| **S3** | Mock yield (informative_rate) by agent · descriptive |
| **S4** | Hybrid dreamer — **post-hoc only** · not in confirmatory run |

---

## 6. Reporting table (pre-specified)

| Table | Content |
| --- | --- |
| T1 | Design factors · n · pre-reg version |
| T2 | Per-spec mock vs Isaac flags (40 rows · rule) |
| T3 | H1 ρ · bootstrap CI · permutation p |
| T4 | H2 tier IR · binomial CI |
| T5 | Rule vs LLM summary (if Leg 6 run) |
| T6 | Pilot vs confirmatory comparison (Study 002 v0.4 · n=20) |

---

## 7. Software

| Step | Script |
| --- | --- |
| Export | `scripts/export_study2_isaac_specs.py` |
| ρ + per-spec | `scripts/compute_study2_h3_mock_isaac.py` |
| Bootstrap CI | extend compute script or notebook · seed=20260728 |

All promoted JSON must include: `prereg_version`, `git_sha`, `run_id`, `n_excluded`.
