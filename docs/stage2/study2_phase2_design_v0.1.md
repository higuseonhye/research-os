# Study 2 — Phase 2 design v0.1 (public · frozen)

> **Experiment:** EXP-SURG-002 · Dream curriculum sandbox  
> **Date frozen:** 2026-07-24 · **Phase 1 closed:** 2026-07-24  
> **Prerequisite:** Phase 1 + selection ablation `selection_ablation_v0.1` · H3 v0.2 ρ=0.145 FAIL  
> **Code:** [`exp_surg_002_dream_curriculum`](../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/) · **Config:** [`sandbox_v0.2.yaml`](../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/config/sandbox_v0.2.yaml)  
> **Run protocol:** [`study2_phase2_run_protocol_v0.1.md`](study2_phase2_run_protocol_v0.1.md)

---

## Why Phase 2 exists (Phase 1 diagnosis)

| Finding | Implication |
| --- | --- |
| Primary yield FAIL (both dreamers 5/5 top-k) | **Do not** re-run top-k yield comparison |
| Selection ablation **Tier B PASS** (top 1.0 · bottom 0.8) | Mock **tier** has signal; per-spec rank weak |
| H3 v0.2 ρ=**0.145** FAIL | Mock rank is not a strong continuous predictor |
| Diffusion bottom: mock **0/5** informative · Isaac **5/5** | **Root cause:** Phase 1 Isaac arm used **shift+onset only**; mock used **occlusion_gain** |
| Gaussian per-dreamer ρ=**0.67** · diffusion ρ=**null** (zero variance) | Alignment may recover H3 for shift-sensitive dreamer first |

**Phase 2 question (pivot):**

> After **mock–Isaac perturbation alignment**, does mock informative rank predict Isaac informative rank on a **top+bottom** spec pack (Spearman ρ ≥ 0.5)?

**Not asking again:** diffusion beats Gaussian on yield (Phase 1 closed · coverage vs diversity).

---

## Scope boundary

| In scope | Out of scope |
| --- | --- |
| Mock–Isaac **occlusion alignment** (study1d proxy) | Classifier-guided diffusion (stretch · Phase 2b backlog) |
| Selection ablation **rerun** on new mock records | Phase 1 top-k confirmatory rerun |
| Harder perturbation cell (wider shift range) | ManiSkill / new sim |
| Tier + ρ pass criteria (Tier B/C) | Predicate invention / IVNTR |
| CPU mock `mock_smoke_v0.4` before GPU | Extra mock yield episodes at v0.1 config |

**Paper 1 (001 Phase C) remains separate.**

---

## Primary hypothesis (Phase 2 · H3′)

> On a **20-spec top+bottom pack** exported from fresh mock records, **mock per-spec informative rank correlates** with Isaac informative rank with **Spearman ρ ≥ 0.5** (pooled or both dreamers individually).

**Informative @ spec (unchanged):** CONTINUE unsuccessful ∧ REPLAN successful (same-state CF @ **S**).

---

## Secondary hypotheses

| ID | Hypothesis | Pass |
| --- | --- | --- |
| **H4′** | **Tier separation** on Isaac: `bottom.informative_rate` ≤ **0.6** and `< top` | Tier B direction (stricter floor than Phase 1) |
| **H5′** | **Alignment lift:** ρ(v0.4 aligned) **>** ρ(v0.2 unaligned) by ≥ **0.25** | Descriptive · not registry if H3′ fails |
| **H6 (exploratory)** | Gaussian vs diffusion **tier gap** (top−bottom IR) differs | Coverage vs diversity · secondary narrative |

---

## Design changes from Phase 1 (frozen v0.2)

| Parameter | Phase 1 (v0.1) | Phase 2 (v0.2) |
| --- | --- | --- |
| **Isaac runner** | `orbit_reach_study1a` · shift + onset | **`orbit_reach_study1d`** · shift + onset + **visibility_fraction** |
| **Occlusion map** | ignored on Isaac | `visibility_fraction = max(0.05, 1.0 − occlusion_gain)` |
| **Occlusion level** | — | **L1** · `gain_scale_flag_v0.1` (Paper 001 contract) |
| **Dream space shift** | [0.02, 0.08] | **[0.015, 0.10]** (harder negatives) |
| **Mock records** | `mock_smoke_v0.2` (reuse) | **`mock_smoke_v0.4`** (new · 3 seeds · same episodes) |
| **Isaac export** | top_bottom · 20 specs | **same strategy** · new records |
| **Seeds / spec** | 0–4 (n=5) | **unchanged** |
| **Branches** | CONTINUE · REPLAN_d0 | **unchanged** |
| **Platform** | RunPod 4090 · VESSL A100 | **VESSL preferred** (workspace kept · Jupyter) |

**Dream space (v0.2):** `shift_m` ∈ [0.015, 0.10] · `onset_step` ∈ [10, 40] · `occlusion_gain` ∈ [0, 0.85]

---

## Execution legs (order)

| Leg | Label | Where | Gate |
| ---: | --- | --- | --- |
| 0 | **Code align** | PR: study2 Isaac loop → study1d + occlusion map | unit smoke |
| 1 | **Mock v0.4** | CPU · `--compare` × seeds 42,43,44 | records committed |
| 2 | **Export** | top-5 + bottom-5 / dreamer → 20 specs | `isaac_specs_v0.4.json` |
| 3 | **Isaac ablation** | VESSL · zero_agent smoke → full 20 spec | `selection_ablation_v0.2/` |
| 4 | **H3′** | CPU · `compute_study2_h3_mock_isaac.py` | `h3_mock_isaac_v0.4/` |

**Do not** run Leg 3 before Leg 0–2 complete.

---

## Pass criteria (Tier B/C)

**Phase 2 GO (publishable H3′ story):**

1. H3′ **PASS** — pooled ρ ≥ 0.5 **or** both dreamers ρ ≥ 0.5 individually (`reason: ok`), **and**
2. H4′ **PASS** — bottom IR ≤ 0.6 and bottom < top on pooled tiers

**Partial (Tier B only):**

- H4′ PASS but H3′ FAIL → mock useful as **binary tier filter** · not rank predictor · document for Paper 002 discussion

**FAIL (stop Phase 2 GPU spiral):**

- H4′ FAIL again (bottom IR > 0.6) → defer to **Isaac-first curriculum** (Phase 3) · no third ablation on same cell

---

## Metrics (unchanged definitions)

| Metric | Definition |
| --- | --- |
| **informative_rate** | #(CONTINUE fail ∧ REPLAN ok) / #specs |
| **mock–isaac agree** | Spearman ρ on per-spec informative (0/1) |
| **param_diversity** | mean std(shift, onset, occlusion) across specs |
| **alignment_lift** | ρ(v0.4) − ρ(v0.2) = 0.145 baseline |

---

## GPU budget (estimate)

| Phase | Est. |
| --- | --- |
| Mock v0.4 (CPU) | < 15 min |
| Bootstrap (cold VESSL) | 15–25 min once |
| Isaac 20 specs × 5 seeds × 2 branches | ~2–3 h |
| H3′ recompute | < 5 min CPU |
| **Total** | **~0.5 workspace-day** |

---

## Version

| Version | Date | Note |
| --- | --- | --- |
| v0.1 | 2026-07-24 | Design freeze · mock–Isaac alignment + ablation rerun |
| | | Phase 1 frozen in [`study2_phase1_design_v0.1.md`](study2_phase1_design_v0.1.md) |

---

## Related

- Phase 1 outcomes: [`study2_phase1_design_v0.1.md`](study2_phase1_design_v0.1.md)  
- Ablation protocol (Phase 1): [`selection_ablation_run_protocol_v0.1.md`](selection_ablation_run_protocol_v0.1.md)  
- VESSL ops: [`vessl_isaac_setup_v0.1.md`](vessl_isaac_setup_v0.1.md)  
- Paper 001 occlusion contract: [`study1d_occlusion_proxy_v0.1.md`](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/docs/study1d_occlusion_proxy_v0.1.md)
