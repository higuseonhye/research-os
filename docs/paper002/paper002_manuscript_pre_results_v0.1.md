# Paper 002 — Manuscript pre-results v0.1

> **ARCHIVED** · mock→physics direction · superseded 2026-07-29  
> **Use instead:** [paper002_manuscript_wm_expansion_v0.1.md](paper002_manuscript_wm_expansion_v0.1.md)  
> **Archive context:** [archive/mock_to_physics/README.md](archive/mock_to_physics/README.md)

---

# Paper 002 — Manuscript pre-results v0.1 (mock→physics · archived)

> **Draft body** before Isaac confirmatory run · fill T1–T6 after execution  
> **Companion (historical):** [paper002_description_v0.1.md](paper002_description_v0.1.md) · [paper002_prereg_v0.3.md](paper002_prereg_v0.3.md)

---

# 1. Introduction

Physical-AI systems are developed under a limited collection of disturbances selected by researchers. Such disturbances may show that a system can fail, but not whether the failure is **useful** for comparing alternative responses or constructing subsequent experiments.

**Informative mismatch:** produces a reliable, task-relevant difference between two prespecified responses from the same initial state — not merely task difficulty.

Paper 001 established the same-state counterfactual fork @ **S**:

```text
S ──mismatch──► CONTINUE  vs  REPLAN@0
```

Paper 002 addresses the **selection problem**: given many candidate mismatches, can a low-cost approximation identify which are likely informative in physics?

Three questions often conflated:

1. Can a system **generate** valid perturbation specifications?
2. Can a low-cost evaluator **rank** those specifications?
3. Do selected perturbations remain informative under **physics simulation**?

**Primary contribution:** questions 2 and 3. Generation is an experimental factor, not sufficient evidence of curriculum quality.

---

# 2. Research question

> Under a frozen occlusion contract, does **continuous mock-based ranking** predict same-state counterfactual informativeness in Isaac simulation on the frozen export set — and does an LLM goal planner meet prespecified adequacy criteria relative to a rule planner?

### Ordered claims

| # | Claim | Hypothesis |
| --- | --- | --- |
| 1 | Proxy validity | H1 — rank transfer |
| 2 | Selection utility | H2 — top-tier enrichment |
| 3 | Planner adequacy | H3 — LLM floor + non-inferiority |

Does **not** test whether either planner improves a learned policy.

---

# 3. Contributions

1. **Proxy-validation formulation** — cheap proxy predicts physics-based counterfactual criterion, not novelty or text plausibility  
2. **Same-state informativeness target** — paired CONTINUE/REPLAN from common **S**  
3. **Frozen mock-to-physics contract** — params, export, mapping, aggregation, exclusions fixed pre-GPU  
4. **Controlled LLM-vs-rule comparison** — absolute floor + non-inferiority margin vs executable rule baseline  

---

# 4. Hypotheses (hierarchical)

## H1 — Extreme-export-set rank transfer

Spearman ρ between continuous aggregated mock score \(\bar M_i\) and continuous Isaac score \(I_i\) on the **40-candidate export set** (20 rule + 20 LLM):

- Pass: ρ ≥ 0.50 **and** bootstrap 95% CI lower bound > 0.25  
- **Not** framed as global proxy validity over all generated candidates unless middle-tier sample added (see §7)

## H2 — Top-tier enrichment (rule planner · n=20)

**Primary enrichment decision (H2 pass requires all):**

- H2a: \(IR_{top} \geq 0.80\) (≥ 8/10 informative)
- H2b: \(IR_{bottom} \leq 0.50\)
- H2c: \(IR_{top} - IR_{bottom} \geq 0.40\)

**Supporting inference:** one-sided exact binomial \(H_0: p_{top} \leq 0.50\). Report exact p. **Not an additional pass requirement.** For n=10, 8/10 → p = **0.0547** (borderline); 9/10 → p = 0.0107.

## H3 — LLM planner (after **both** Isaac legs)

Evaluated post-hoc · hierarchical after H1 and H2 on rule set.

- **H3a:** ρ_LLM ≥ 0.50  
- **H3b:** lower bound of 95% bootstrap CI for Δρ = ρ_LLM − ρ_rule **> −0.15**  

Both required for LLM claim.

---

# 5. Study design

**Mixed factorial:**

- **Planner:** between (rule · llm)  
- **Dreamer:** within candidate generation (gaussian · diffusion)  
- **Tier:** within export (top · bottom)

**Export scope:** **within-planner** — top 10 + bottom 10 pooled across dreamers per planner → **40 Isaac specs total**.

**Mock aggregation:** median \(\bar M_i\) over mock seeds 42–46 (not seed 43 alone). Seed 43 = sensitivity only.

---

# 6. Mock evaluator

### Continuous mock score (primary)

\[
M_i = \underbrace{\mathbb{1}[REPLAN\ ok] - \mathbb{1}[CONTINUE\ ok]}_{\text{success gap}}
+ \underbrace{\mathrm{clip}\left(\frac{d_{CONTINUE} - d_{REPLAN}}{4\tau}, 0, 1\right)}_{\text{distance gap}}
+ \underbrace{0.25 \cdot \mathbb{1}[\text{violation lift}]}_{\text{optional}}
\]

where \(\tau\) = mock tolerance (0.02 m). Implemented in `mock_reach.cf_margin()`.

Binary informative label = secondary: \( \hat Y^{mock}_i = \mathbb{1}[M_i \geq \theta_M]\) with \(\theta_M = 0.5\) frozen.

**Spearman uses continuous \(\bar M_i\), not binary.**

### Consensus export score

\[
\bar M_i = \mathrm{median}_{s \in \{42,\ldots,46\}} M_{is}
\]

Candidates matched by canonical spec key `(round(shift_m,4), onset_step, round(occlusion_gain,3))`.

---

# 7. Mock-to-Isaac transfer (frozen)

| Mock field | Isaac field | Transfer |
| --- | --- | --- |
| `occlusion_gain` | `visibility_fraction` | clip(1−g, 0.05, 1) |
| `onset_step` | perturbation start | identical |
| `shift_m` | target shift (Y+) | direct |
| `tier` | metadata | no sim effect |

Runner: **study1d** · proxy: **gain_scale_flag_v0.1** · level 1.

---

# 8. Isaac evaluation

- Fixed **S** @ control step 20 (Paper 001 contract)  
- Branches: CONTINUE · REPLAN_d0  
- 8 seeds (0–7) per spec  
- **Valid spec:** ≥ 4 completed seed pairs  
- **Binary informative @ spec:** ≥ 5/8 seeds informative (or majority of valid if 4–7 seeds)  
- **Continuous Isaac score:** \(I_i = \mathrm{median}_{s \in V_i} D_{is}\) where \(D_{is}\) = seed-level CF margin (same formula as mock)

---

# 9. Statistical analysis

See [paper002_analysis_plan_v0.2.md](paper002_analysis_plan_v0.2.md).

- H1: Spearman + bootstrap CI (B=2000, candidate-level) + permutation (1000 shuffles)  
- H2: exact binomial CI · one-sided test on top tier  
- H3: planner-stratified ρ · bootstrap CI on Δρ  
- Multiplicity: hierarchical H1 → H2 → H3  

### Sensitivity (Tier B)

1. Seed-43 export only  
2. Binary mock label instead of continuous  
3. Kendall τ instead of Spearman  
4. Middle 5 candidates per planner (if run)  

---

# 10. Power note

n=40 export set — suitable for detecting ρ ≳ 0.5, not fine-grained interactions. Non-inferiority for LLM is **bounded confirmatory** — failure to establish non-inferiority ≠ proven inferiority.

Without middle-ranked candidates, H1 is **extreme-export-set rank transfer** — manuscript must not claim global proxy validity over full candidate space.

---

# 11. Preregistered tables

## T1 — Candidate accounting

| Planner | Raw | Valid | Unique | Exported | Isaac-valid | Confirmatory |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rule | | | | 20 | | |
| LLM | | | | 20 | | |
| **Total** | | | | **40** | | |

## T3 — Rank transfer

| Population | n | Spearman ρ | Bootstrap 95% CI | Perm p | Pass |
| --- | ---: | ---: | --- | ---: | --- |
| Rule export set | | | | | |
| LLM export set | | | | | |
| Pooled (descriptive) | | | | | |

## T4 — Tier enrichment

| Planner | Group | n | Informative | IR | Exact 95% CI |
| --- | --- | ---: | ---: | ---: | --- |
| Rule | Top | 10 | | | |
| Rule | Bottom | 10 | | | |
| LLM | Top | 10 | | | |
| LLM | Bottom | 10 | | | |

## T5 — Hypothesis decisions

| Hyp | Criterion | Estimate | Pass |
| --- | --- | ---: | --- |
| H1 | ρ≥0.50 ∧ CI_lo>0.25 | | |
| H2a–c | IR_top · IR_bottom · gap | | |
| H2 binomial (support) | exact p one-sided | | — |
| H3a | ρ_LLM≥0.50 | | |
| H3b | CI_lo(Δρ)>−0.15 | | |

---

# 12. Interpretation rules

| Pattern | Statement |
| --- | --- |
| H1+H2 pass | Proxy-guided selection supported on export set |
| H1+H2+H3 pass | + LLM non-inferior proposer |
| H1 pass · H2 fail | Association without usable tier filter |
| H1 fail | No validated rank transfer under tested contract |
| H3a pass · H3b fail | LLM floor ok · non-inferiority not established |

---

# 13. Limitations

1. Single perturbation family (controlled visual occlusion)  
2. Extreme-groups export may inflate ρ — label H1 accordingly  
3. Small n for planner-specific inference  
4. Isaac ≠ real hardware / clinical setting  
5. LLM result tied to frozen model + prompt  
6. Informativeness relative to frozen CONTINUE/REPLAN pair only  

---

# 14. Results template (fill post-run)

## Candidate generation

Rule generated [N] contract-valid candidates; LLM [N] parsed / [N] valid. After five-seed median aggregation and within-planner export, 20 candidates per planner were frozen (checksum: [hash]) before Isaac.

## Primary association

Rule planner: ρ = [X], 95% CI [L, U]. H1 [pass/fail].

## Enrichment

Rule top tier: [k]/10 informative (IR=[X]). Bottom: [k]/10. H2 [pass/fail].

## LLM (if Leg 6)

ρ_LLM = [X], Δρ = [X−Y], 95% CI for Δρ [L, U]. H3 [pass/fail].

---

# 15. Figures (pre-specified)

1. Pipeline diagram  
2. Mock vs Isaac continuous score scatter (planner markers)  
3. Top vs bottom IR with binomial CI  
4. Planner ρ comparison + non-inferiority margin  
5. Disagreement exemplars (mock-high/Isaac-low · etc.)
