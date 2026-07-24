# Study 2 — Phase 1 design v0.1 (public · frozen)

> **Experiment:** EXP-SURG-002 · Dream curriculum sandbox  
> **Date frozen:** 2026-07-22 · **Phase 1 executed:** 2026-07-22  
> **Code:** [`exp_surg_002_dream_curriculum`](../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/) · **Config:** [`sandbox_v0.1.yaml`](../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/config/sandbox_v0.1.yaml)

---

## Scope boundary

**Paper 1 (001 Phase C) is separate.** This study tests **failure scenario generation**, not confirmatory recoverability profiles @ fixed **S**.

| In scope | Out of scope |
| --- | --- |
| Gaussian vs diffusion **dreamer** | Full ReSYNC / IVNTR stack |
| Rule vs JSON **agentic curriculum** | Classifier-guided diffusion on images |
| Isaac ORBIT reach @ dreamed specs | ManiSkill / new sim |
| Informative rate mock ↔ Isaac correlation | Predicate invention metrics |

---

## Primary hypothesis (RQ 1.2)

> **Diffusion dreaming** produces a **higher rate of informative failures** on Isaac ORBIT reach than **Gaussian dreaming**, under matched agentic curricula and seed budget.

**Informative failure @ spec:** CONTINUE unsuccessful ∧ REPLAN successful (same-state CF @ mismatch onset **S**).

---

## Secondary hypotheses

| ID | Hypothesis |
| --- | --- |
| **H2** | Diffusion yields **higher param diversity** than Gaussian at matched informative rate |
| **H3** | Mock informative rate **correlates** with Isaac informative rate (Spearman ρ ≥ 0.5 on top-k specs) |
| **H4 (exploratory)** | LLM JSON curriculum ≥ rule curriculum on informative yield |

---

## Design (frozen v0.1)

| Parameter | Value |
| --- | --- |
| **Dreamers** | `gaussian` · `diffusion` (toy DDPM · desk-trained bootstrap) |
| **Agent default** | `rule` (taxonomy families cycle) |
| **Mock episodes / dreamer** | 48 |
| **Mock seeds** | 42, 43, 44 |
| **Isaac top-k specs / dreamer** | 5 (highest mock informative; tie-break diversity) |
| **Isaac seeds / spec** | 0,1,2,3,4 (n=5) |
| **Perturbation** | P2 target shift (+Y); onset + shift from dream space |
| **Branches** | CONTINUE · REPLAN_d0 |
| **Platform** | Isaac Sim 4.1 · ORBIT Reach IK-Rel · RunPod RTX 4090 |

**Dream space:** `shift_m` ∈ [0.02, 0.08] · `onset_step` ∈ [10, 40] · `occlusion_gain` ∈ [0, 0.85] (mock only v0.1)

---

## Metrics

| Metric | Definition |
| --- | --- |
| **Primary:** informative_rate | #(CONTINUE fail ∧ REPLAN ok) / #specs |
| **param_diversity** | mean std(shift, onset, occlusion) across specs |
| **mock–isaac agree** | Spearman ρ on per-spec informative (0/1) |

---

## Phase 1 outcomes (committed · honest tiers)

| Leg | Label | Outcome |
| --- | --- | --- |
| Mock | `mock_smoke_v0.2` | Gaussian yield ↑ · diffusion diversity ↑ · primary yield **not supported** |
| Isaac | `isaac_full_v0.1` | Top-k 5/5 both dreamers (ceiling) |
| H3 | `h3_mock_isaac_v0.1` | ρ **null** (zero variance) · **not supported** |
| Ablation | `selection_ablation_v0.1` | Tier B direction **PASS** (top 1.0 · bottom 0.8 IR) |
| H3 ablation | `h3_mock_isaac_v0.2` | ρ=**0.145** · **not supported** (variance restored) |

Narrative: **coverage (Gaussian) vs diversity (diffusion)**, not diffusion beats Gaussian on yield. Mock **tier** (top vs bottom) partially predicts Isaac; per-spec rank correlation remains weak.

---

## Selection ablation (executed · 2026-07-24)

Per dreamer: **top-5 + bottom-5** by mock informative rank → **20 Isaac specs** · seeds 0–4 · **RUN_ID** `20260724T041955Z` (VESSL A100).  
Scripts: [`run_study2_selection_ablation_vessl.sh`](../../scripts/run_study2_selection_ablation_vessl.sh) · promote → [`selection_ablation_v0.1/`](../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/selection_ablation_v0.1/)

---

## Version

| Version | Date | Note |
| --- | --- | --- |
| v0.1 | 2026-07-22 | Design freeze · Phase 1 executed |
| v0.1-public | 2026-07-23 | Promoted frozen design to research-os (no private links) |
