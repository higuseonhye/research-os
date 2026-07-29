# Paper 002 — Pre-registration v0.3 (frozen)

> **ARCHIVED** · mock→physics pre-reg · confirmatory GPU **cancelled** · tag paper002-prereg-v0.3 history only
> **Current:** [paper002_prereg_wm_expansion_v0.1.md](paper002_prereg_wm_expansion_v0.1.md) · [archive index](archive/mock_to_physics/README.md)

> **Status:** **FROZEN** · GPU only after commit  
> **Supersedes:** v0.2 (desk draft · not executed)  
> **Positioning:** [paper002_description_v0.1.md](paper002_description_v0.1.md)  
> **Method:** [paper002_method_spec_v0.2.md](paper002_method_spec_v0.2.md)  
> **Analysis:** [paper002_analysis_plan_v0.2.md](paper002_analysis_plan_v0.2.md)  
> **Config:** [`sandbox_v0.4.yaml`](../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/config/sandbox_v0.4.yaml)  
> **Date frozen:** 2026-07-28

---

## 0. Confirmatory claim (exact wording)

> **Extreme-export-set rank transfer:** On the frozen within-planner top/bottom export set (40 candidates), continuous mock scores (five-seed median) predict continuous Isaac counterfactual scores with prespecified rank association and top-tier enrichment.

Not claimed: global proxy validity over all generated candidates (unless middle-tier leg executed · Tier B).

---

## 1. Design summary

| Parameter | v0.2 | **v0.3** |
| --- | --- | --- |
| Mock score | binary informative | **continuous `cf_margin`** |
| Export ranking | binary / seed 43 | **median seeds 42–46** |
| Export scope | per dreamer 10+10 | **per planner 10+10** (dreamers pooled) |
| Specs / planner | 40 total (20/dreamer×2) | **20/planner · 40 total** |
| H2 IR_top | gap only | **≥ 0.80 (8/10)** · binomial **reported only** |
| H3b | point Δρ ≥ −0.15 | **bootstrap CI lower > −0.15** |
| Isaac score | binary only | **continuous median + binary** |
| Manifest | none | **checksum before Isaac** |

---

## 2. Hypotheses (hierarchical · evaluated post-hoc)

**Important:** H1 → H2 → H3 are tested **only after both planner Isaac legs complete**. They are **not** used to gate the LLM Isaac leg (see §8 operational gate).

**Analysis populations:**

| Hyp | Population |
| --- | --- |
| H1 · H2 | **Rule planner** export set (n=20) |
| H3 | Rule (n=20) vs LLM (n=20) |

### H1 — Rank transfer (rule planner · n=20)
Spearman ρ(\(\bar M_i\), \(I_i\)) ≥ **0.50** on rule export set where:

- \(\bar M_i\) = median mock `cf_margin` over seeds 42–46  
- \(I_i\) = median seed-level CF margin on Isaac (valid seeds only)

**Pass (all):**

1. ρ ≥ 0.50 · `reason: ok` · n ≥ 18 after exclusions  
2. Bootstrap 95% CI lower bound (B=2000) > **0.25**  
3. Permutation empirical p reported (1000 shuffles · **supporting · not pass criterion**)

### H2 — Top-tier enrichment (rule planner)

On rule export top-10 / bottom-10 (pooled dreamers).

**Primary enrichment decision (all required for H2 pass):**

| ID | Criterion |
| --- | --- |
| H2a | \(IR_{top} \geq 0.80\) (≥ **8/10** informative) |
| H2b | \(IR_{bottom} \leq 0.50\) |
| H2c | \(IR_{top} - IR_{bottom} \geq 0.40\) |

**Supporting inference (reported · not an additional pass requirement):**

One-sided exact binomial test \(H_0: p_{top} \leq 0.50\) at α=0.05.

| k / n=10 | One-sided exact p |
| ---: | ---: |
| 8 | **0.0547** |
| 9 | 0.0107 |
| 10 | 0.0010 |

Because 8/10 yields p = 0.0547 > 0.05, the **rate thresholds (H2a–c) are the confirmatory pass criteria**. The binomial p-value is supporting evidence only. If k = 8 and H2a–c pass, H2 **passes**; report p = 0.0547 as borderline support.

### H3 — LLM planner (n=20 · evaluated after both legs)

| ID | Criterion |
| --- | --- |
| H3a | ρ_LLM ≥ 0.50 |
| H3b | Lower bound of 95% bootstrap CI for Δρ = ρ_LLM − ρ_rule **> −0.15** |

Both required. Kill: ρ_LLM < 0.30.

---

## 3. Mock score (frozen)

\[
M_i = (\mathbb{1}[REPLAN\ ok] - \mathbb{1}[CONTINUE\ ok]) + \mathrm{clip}\left(\frac{d_C - d_R}{4\tau}, 0, 1\right) + 0.25 \cdot \mathbb{1}[\text{violation lift}]
\]

τ = 0.02 m · code: `mock_reach.cf_margin()`.

Binary label secondary: \(\mathbb{1}[M_i \geq 0.5]\).

---

## 4. Export procedure (frozen)

1. Mock rule · seeds 42–46 → `merge_study2_mock_consensus.py`  
2. Mock LLM · seeds 42–46 → consensus  
3. `export_study2_isaac_specs.py --scope planner --top-k 10 --strategy top_bottom`  
4. Record manifest SHA256 → `--manifest-checksum`  
5. Isaac on frozen manifest · no post-hoc spec changes  

**Sensitivity (Tier B):** seed-43-only export · binary mock rank.

---

## 5. Isaac (unchanged from v0.2 + continuous)

- study1d · 8 seeds · majority ≥5/8 for binary informative  
- Continuous \(I_i\) = median seed CF margin  
- Exclude specs with <4 valid seed pairs  

---

## 6. Optional middle-tier leg (Tier B · not registry)

If GPU budget allows: +5 middle-ranked per planner → 50 specs. Enables descriptive global validity. **Not required for confirmatory pass.**

---

## 7. Execution legs

| Leg | Work | Gate type |
| ---: | --- | --- |
| 0 | Commit v0.3 docs + code + tag | — |
| 0b | **Seed-43 smoke** (optional · engineering only) | [smoke protocol](paper002_smoke_protocol_v0.1.md) |
| 1 | LLM curricula · 5 seeds | schema |
| 2 | Mock rule · 5 seeds | CPU |
| 3 | Mock LLM · 5 seeds | CPU |
| 4 | Consensus merge + export + **checksum freeze** | CPU |
| 5 | **Isaac rule** engineering leg | GPU |
| 6 | **Operational go/no-go** (§8) | engineering |
| 7 | **Isaac LLM** leg (if go) | GPU |
| 8 | **H1 → H2 → H3** confirmatory analysis | CPU |

**Do not** use H1/H2 results from Leg 5 to skip Leg 7. Skipping Leg 7 for confirmatory reasons converts the study to a **feasibility-only** report (H3 not evaluable).

---

## 8. Operational gate (LLM leg continuation)

Applied **after Leg 5 (rule Isaac)** · **before Leg 7 (LLM Isaac)**.  
This is an **engineering feasibility gate**, not a confirmatory hypothesis gate.

**Continue to LLM Isaac leg when all hold:**

| Criterion | Threshold |
| --- | --- |
| State-restore / run completion | ≥ **90%** of rule export specs start both branches |
| Valid-seed rate | ≥ **80%** of rule export specs have ≥ 4 valid seed pairs |
| Transfer contract | No systematic occlusion-map or study1d runner failure pattern |
| Metric non-degeneracy | CONTINUE/REPLAN informative rate not constant 0 or 1 across all 20 rule specs |

**If gate fails:** document as feasibility study · H3 not evaluated · do not tune export/manifest from rule outcomes.

Full detail: [paper002_operational_gate_v0.1.md](paper002_operational_gate_v0.1.md)

---

## 9. Seed-43 smoke (pre-confirmatory)

Permitted **before** Legs 1–4 for pipeline validation only.

**Must not:**

- enter confirmatory candidate ranking or consensus export (Leg 4 uses seeds 42–46 only)
- change thresholds, mapping, weights, or exclusion rules based on smoke outcomes
- reuse smoke specs in the frozen export manifest

**Must:**

- record separate smoke manifest + run log
- label all smoke artifacts `smoke_seed43_*` · Tier B / engineering

See [paper002_smoke_protocol_v0.1.md](paper002_smoke_protocol_v0.1.md)

---

## Version

| Version | Note |
| --- | --- |
| v0.1 | Desk draft |
| v0.2 | Method + binary scale-up |
| v0.3 | Continuous score · consensus export · planner scope |
| **v0.3-amend** | H2 binomial supporting-only · operational vs hypothesis gate split · smoke rules |
