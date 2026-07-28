# Paper 002 — Analysis plan v0.2

> **Supersedes:** v0.1 · **Pre-reg:** [paper002_prereg_v0.3.md](paper002_prereg_v0.3.md)

---

## Primary endpoints

| Analysis | Mock | Isaac |
| --- | --- | --- |
| H1 · H3 rank transfer | \(\bar M_i\) continuous median | \(I_i\) continuous median |
| H2 enrichment | — | \(Y_i\) binary majority |

---

## Hierarchical testing (v0.3-amend)

Evaluated **after both planner Isaac legs complete** (or rule-only if operational gate fails):

```text
H1 (rule n=20) → H2 (rule n=20) → H3 (LLM vs rule)
```

**Not** used to gate LLM Isaac execution. Operational continuation: [paper002_operational_gate_v0.1.md](paper002_operational_gate_v0.1.md).

---

## H1 (rule planner · n=20)

```python
rho, reason = spearman(M_bar, I_continuous)
ci_lo, ci_hi = bootstrap_spearman(M_bar, I_continuous, B=2000, seed=20260728)
p_perm = permutation_spearman(M_bar, I_continuous, B=1000, seed=20260728)
```

**Pass:** rho ≥ 0.50 ∧ ci_lo > 0.25.

---

## H2 (rule planner · n=20)

Per tier (top n=10 · bottom n=10):

**Pass (all required):**

- \(IR_{top} \geq 0.80\)
- \(IR_{bottom} \leq 0.50\)
- \(IR_{top} - IR_{bottom} \geq 0.40\)

**Supporting (report · not pass criterion):**

- Clopper-Pearson exact 95% CI on \(IR_{top}\), \(IR_{bottom}\)
- One-sided exact binomial: \(H_0: p_{top} \leq 0.5\)

| k / n=10 | One-sided exact p |
| ---: | ---: |
| 8 | 0.0547 |
| 9 | 0.0107 |

8/10 passes H2 via rate thresholds; binomial p = 0.0547 is reported as borderline supporting evidence.

---

## H3 (LLM · after both Isaac legs)

Evaluated **after** rule + LLM Isaac complete · **not** gated by H1/H2 at rule leg.

Δρ = ρ_LLM − ρ_rule

Bootstrap paired/stratified preserving planner identity (B=2000):

**Pass H3b:** CI_lower(Δρ) > −0.15

---

## Sensitivity (Tier B)

| ID | Variant |
| --- | --- |
| S1 | Seed-43 export only |
| S2 | Binary mock rank |
| S3 | Kendall τ |
| S4 | Pooled 40-candidate ρ (descriptive) |
| S5 | Middle-tier 10 candidates (if run) |

---

## Software

| Script | Role |
| --- | --- |
| `merge_study2_mock_consensus.py` | Five-seed median |
| `export_study2_isaac_specs.py` | Planner-scope export |
| `compute_study2_h3_mock_isaac.py` | ρ · bootstrap · tiers |

Extend compute script with `--continuous` (default in v0.3).

---

## Output fields (promoted JSON)

```json
{
  "prereg_version": "v0.3",
  "mock_score_type": "cf_margin_median",
  "export_scope": "planner",
  "spearman_rho": 0.0,
  "bootstrap_ci_95": [0.0, 0.0],
  "h1_pass": false,
  "h2_pass": false,
  "h3_pass": false
}
```
