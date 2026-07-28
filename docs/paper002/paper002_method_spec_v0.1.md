# Paper 002 — Method specification v0.1

> **Pre-reg:** [paper002_prereg_v0.2.md](paper002_prereg_v0.2.md)  
> **RQ:** [paper002_rq_v0.2.md](paper002_rq_v0.2.md)  
> **Analysis:** [paper002_analysis_plan_v0.1.md](paper002_analysis_plan_v0.1.md)  
> **Config:** [`sandbox_v0.3.yaml`](../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/config/sandbox_v0.3.yaml)  
> **Date:** 2026-07-28

---

## 1. Scientific object

**Curriculum validation function** \(V\): given a cheap mock rank of perturbation specs, does it predict **same-state counterfactual informativeness** on Isaac @ mismatch onset **S**?

| Term | Definition (frozen · Paper 001 aligned) |
| --- | --- |
| **State S** | Post-mismatch execution state at perturbation onset (shift + optional occlusion active) |
| **Informative @ spec** | CONTINUE unsuccessful ∧ REPLAN@0 successful under matched **S** fork |
| **Mock** | 1D reach surrogate · same gain/occlusion map as study1d |
| **Isaac** | ORBIT Reach IK-Rel · study1d runner · gain_scale_flag v0.1 |

Paper 002 **does not** re-measure Paper 001 profiles. It tests whether **generated specs** survive Paper 001's CF gate when transferred mock→Isaac.

---

## 2. Experimental factors

```text
                    ┌── Dreamer: gaussian │ diffusion (within pack)
Agent: rule │ llm ──┤
                    └── Selection tier: top-10 │ bottom-10 (within dreamer)
```

| Factor | Levels | Role |
| --- | --- | --- |
| **Agent** (between) | `rule` · `llm-json` | Who plans perturbation **families/severities** |
| **Dreamer** (within) | `gaussian` · `diffusion` | Who proposes **(shift, onset, occlusion_gain)** |
| **Selection tier** (within) | `top` · `bottom` | Mock rank stratum exported to Isaac |

**Not crossed with Paper 001 arms:** only {CONTINUE, REPLAN@0} — the minimal fork for informativeness.

---

## 3. Mock–Isaac transfer contract (mandatory)

Pilot root cause (Study 002 Phase 1): Isaac ignored mock `occlusion_gain`. **Frozen for confirmatory:**

| Mock field | Isaac field | Map |
| --- | --- | --- |
| `occlusion_gain` ∈ [0, 0.85] | `visibility_fraction` | `max(0.05, 1.0 − occlusion_gain)` |
| `shift_m` | target shift (Y+) | direct |
| `onset_step` | perturbation onset step | direct |
| `proxy` | — | `gain_scale_flag_v0.1` · level 1 |
| `runner` | — | `study1d` |

Reference: [study1d_occlusion_proxy_v0.1.md](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/docs/study1d_occlusion_proxy_v0.1.md)

**Gate:** zero_agent smoke + one occlusion spec smoke before full ablation.

---

## 4. Agent conditions

### 4.1 Rule baseline (`rule`)

Cycles taxonomy families `[target_shift, visual_occlusion, forbidden_region]` × severities `[small, mid, unreachable]`.  
Dreamer draws params conditional on `(family, severity)`.

### 4.2 LLM curriculum (`json-file`)

- Frozen prompt v0.1 · schema v0.1 · one JSON per mock seed (42–46)
- LLM outputs **goals only** (family, severity); dreamer still draws continuous params
- **Fair comparison:** same dreamers · same export · same Isaac protocol — only goal sequence differs

See [llm_curriculum_protocol_v0.1.md](llm_curriculum_protocol_v0.1.md).

---

## 5. Dreamer protocol (frozen)

| Step | Gaussian | Diffusion |
| --- | --- | --- |
| Param source | Fixed moments from config | DDPM sample after bootstrap |
| Bootstrap | — | First 16 goals · 4 samples/goal · keep informative · `n_train_seeds=64` |
| Training | — | 200 steps · 50 sample steps · β 1e-4→0.02 |
| Dream space | shift ∈ [0.015, 0.10] · onset ∈ [10, 40] · occ ∈ [0, 0.85] | same |

**Per mock episode:** one spec evaluated · informative flag from single mock CF (deterministic given spec.seed).

---

## 6. Spec export (selection ablation)

**Algorithm (frozen):**

1. Rank mock records per dreamer by `(informative, shift_m, onset_step)` descending
2. Dedupe by `(round(shift_m, 4), onset_step)` — first in rank retained
3. **Top-k:** first k deduped · **Bottom-k:** last k deduped excluding top keys
4. k = **10** per dreamer → **20/dreamer · 40 pooled**

**Primary export:** mock seed **43** (Study 002 convention).  
**Sensitivity (Tier B):** seeds 42, 44, 45, 46 — median ρ reported · not registry pass/fail.

**Negative control (sanity):** shuffle mock informative labels within dreamer → expect ρ ≈ 0 (analysis plan).

---

## 7. Isaac evaluation

| Parameter | Value |
| --- | --- |
| Specs / agent condition | 40 |
| Isaac seeds / spec | 8 (0–7) |
| Branches / spec / seed | CONTINUE · REPLAN_d0 |
| **Isaac informative @ spec** | Majority over seeds: informative on ≥ ⌈8/2⌉ = **5** of 8 seed-level CF outcomes |

Seed-level CF matches mock logic: CONTINUE fail ∧ REPLAN ok on that seed.

**Exclusions:** specs with < 4 valid seed pairs → drop · report `n_excluded` · do not impute.

---

## 8. Scale rationale

| Choice | Pilot | Confirmatory | Rationale |
| --- | --- | --- | --- |
| Specs | 20 | **40** | 2× pilot · more tie-breaking for Spearman |
| Mock episodes | 48 | **128** | Fill top/bottom-10 after dedupe (pilot exhausted at k=5) |
| Mock seeds | 3 | **5** | Export stability · sensitivity |
| Isaac seeds | 5 | **8** | Per-spec binomial majority · tighter than single-seed |

**Power (descriptive):** pilot pooled ρ=0.899 @ n=20. Confirmatory targets ρ≥0.5 (pre-spec). n=40 yields ~80% power vs ρ=0.3 null at α=0.05 (one-sided) for Spearman — adequate for replication study.

---

## 9. Execution gates (unchanged order)

Mock CPU (rule → llm) → export → Isaac rule → **operational gate** → Isaac llm → **H1→H2→H3 analysis**.

See [paper002_run_protocol_v0.1.md](paper002_run_protocol_v0.1.md).

---

## 10. Claim boundaries

| Claim | Requires |
| --- | --- |
| Mock rank predicts Isaac | H1 PASS @ rule |
| Mock tier is usable filter | H2 PASS @ rule |
| LLM curriculum adds value | H3 PASS (both non-inferiority + floor) |
| Diffusion beats Gaussian on yield | **Not claimed** (pilot closed) |
| Clinical / SOTA reach | **Out of scope** |
