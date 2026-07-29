# Paper 002 — Manuscript skeleton · WM expansion v0.1

> **Status:** pre-results · fill Results tables after confirmatory run  
> **Supersedes:** [paper002_manuscript_pre_results_v0.1.md](paper002_manuscript_pre_results_v0.1.md) (mock→physics · archived)  
> **Companion:** [description](paper002_description_wm_expansion_v0.1.md) · [confirmatory spec](paper002_confirmatory_spec_v0.1.md) · [pre-reg draft](paper002_prereg_wm_expansion_v0.1.md) · [analysis plan v0.3](paper002_analysis_plan_v0.3.md)

---

## Title (working)

**When Parameter Update Is Not Enough: Structural World-Model Expansion from Unexplained Failures in Embodied Simulation**

---

## Abstract (draft · fill numbers post-confirmatory)

Embodied agents often respond to prediction failure by retuning parameters within a fixed world-model class. We ask when such repair is **structurally inadequate** — when persistent, directionally structured residuals indicate a **missing dynamics mode** rather than wrong values in a known representation.

We introduce a **failure-conditioned model-adequacy test** in ORBIT surgical reach simulation: after Episode 1 persistent target drift and **K** failed L1 parameter repairs, a rule-based gate decides whether to invoke a **prepared** L3 operator (add drift dynamics expert **F₁** + mode gate **G**) versus L1 repair only or no update. Episode 2 varies drift direction, speed, onset, and initial pose while holding the hidden regime fixed.

**Primary contrasts:** L3 vs L1 on multi-step prediction error (H=10) and Ep2 task success; static retention as non-inferiority guardrail; gate validity on noise and impulse negative controls.

**Preliminary mock pilot (Tier B+ · mechanism only · not in confirmatory analysis):** gate fires on drift and not on negative controls; L3 lowers held-out prediction error vs L1. Confirmatory Isaac run pending pre-reg freeze.

**Not claimed:** expert addition alone · general WM expansion · clinical deployment · hardware validation (parallel track).

---

# 1. Introduction

World models compress observations into latent state, predict action-conditioned dynamics, and support model-based control. When prediction error rises, standard practice is to **update parameters** within a fixed architecture — better latents, better friction estimates, better noise models.

Three failure interpretations are often conflated:

1. **Distribution shift** — familiar variables under new statistics  
2. **Epistemic uncertainty** — insufficient data in an otherwise adequate class  
3. **Structural inadequacy** — the current **model class** cannot represent the generating dynamics

Paper 002 targets (3). The operational question is not whether an agent can add capacity, but **whether failure evidence justifies switching** from parameter repair to a **prepared structural expansion operator** — and whether that switch improves **prediction and control on novel related encounters** without nominal regression.

Prior work adds modules, routes mixtures, or integrates new world models at test time (TMoW · MuSix · Worldscape-MoE · LMC). Our wedge is **whether and when** expansion is warranted — validated with an explicit **L1 vs L3 arm comparison**, a **parsimony gate**, and **negative controls**.

**Paper 001 (optional credential):** same-state counterfactual recoverability @ fixed mismatch **S** — REPLAN vs CONTINUE. Recoverability is a **measurement window**, not the program center. Paper 002 does not require Paper 001 as a logical prerequisite.

---

# 2. Research question

> When a fixed dynamics model cannot explain **persistent drift failure** with parameter update alone, does adding a **drift dynamics expert** (L3 structural expansion) improve **held-out drift prediction** and **Ep2 control**, without **nominal static regression**?

### Ordered hypotheses

| ID | Claim | Endpoint |
| --- | --- | --- |
| **H1** | L3 beats L1 on Ep2 prediction | O1 · multi-step PE · H=10 |
| **H2** | L3 beats L1 on Ep2 behavior | O2 · task success |
| **H3** | L3 does not harm static nominal | O6 · non-inferiority · margin δ |
| **H4** | Gate fires on drift · rarely on noise/impulse | O9 · gate rate by condition |

**Primary contrast:** C (modular L3) vs B (parameter L1).  
**Secondary:** C vs A (no update).  
**Diagnostic only:** D (oracle mode label to gate).

Does **not** test unconstrained neural architecture search · diffusion WM as primary cell · real-hardware confirmatory (deferred).

---

# 3. Contributions

1. **Failure-conditioned model-adequacy formulation** — distinguish structural inadequacy from shift and uncertainty; gate expansion on persistent structured residual after **K** failed L1 repairs  
2. **Restricted operator menu** — prepared L3 (F₁ drift expert + G) vs L1 vs none; equal data budget across arms  
3. **Two-encounter protocol** — Ep1 failure evidence shared across arms; Ep2 novel drift with ≥2 changed dimensions; static retention phase  
4. **Negative-control gate validity (H4)** — observation noise · single impulse · nominal static vs persistent drift  
5. **Mechanistic panel (exploratory)** — latent separation · expert selection · residual structure adjacent to O1/O2 — not primary claim  

---

# 4. Method overview

### 4.1 Environment

**Platform:** Isaac Sim 4.1 · ORBIT Surgical Reach (`Isaac-Reach-Dual-STAR-IK-Rel-Play-v0` or documented successor).

**Hidden true modes:**

| Mode | Dynamics |
| --- | --- |
| **M0 static** | `x_target(t+1) = x_target(t)` |
| **M1 drift** | `x_target(t+1) = x_target(t) + v_drift Δt` after onset |

**Initial agent WM W₀:** trained on M0 only · assumes static target dynamics.

**Controller (v0.1):** MPC / model-based trajectory selection over WM rollouts.

Full runnable minimum: [confirmatory spec §Environment](paper002_confirmatory_spec_v0.1.md).

### 4.2 Protocol phases

```text
Phase 0   Pretrain W0 on M0 static only
Phase 1   Ep1 — M1 persistent drift · log full trajectory
Phase 2   K × L1 parameter repair attempts on F0
Phase 3   Rule-based expansion gate (identical evidence · all arms)
Phase 4   Arm intervention (A / B / C / D)
Phase 5   Ep2 — novel M1 drift (≥2 dims changed from Ep1)
Phase 6   Static retention (M0)
```

Ep1 evidence is **identical** across arms before split.

### 4.3 Arms

| Arm | Label | Intervention |
| --- | --- | --- |
| A | No update | frozen W₀ |
| B | Parameter L1 | fine-tune F0 only |
| C | Modular L3 | add F1 drift expert + gate G |
| D | Oracle | true mode label to gate · diagnostic only |

**Primary contrast:** C vs B · equal data budget.

### 4.4 Expansion gate (rule-based · pre-specified)

```text
Gate = 1 iff ALL:
  mean(residual_after_repair) > τ_error
  K repair attempts completed without absorbing residual
  residual_autocorrelation > τ_a
  ΔNLL = NLL(F0_repaired) - NLL(F1_candidate) > τ_nll   [held-out Ep1 slice]
```

Thresholds frozen at pre-reg from **pilot seeds only** — confirmatory seeds never used for tuning.

Latent cluster metrics **do not** trigger the gate (Appendix · mechanistic only).

### 4.5 Gate negative controls (H4)

| ID | Condition |
| --- | --- |
| N1 | ↑ target observation noise · M0 static |
| N2 | Single target impulse then stop |
| — | Nominal M0 · persistent M1 |

### 4.6 Outcomes

| ID | Metric | Role |
| --- | --- | --- |
| O1 | Multi-step prediction error Ep2 · H=10 | **Primary** (H1) |
| O2 | Ep2 task success | **Primary** (H2) |
| O6 | Static retention success | H3 guardrail |
| O9 | Gate activation rate by condition | H4 |
| O7 | Ep1 residual after K L1 repairs | H1 diagnostic |
| O8 | Latent / expert / residual mechanistic | Exploratory |

### 4.7 Sample size

| Tier | Design | In primary analysis? |
| --- | --- | --- |
| Engineering pilot | 3 arms × 5 seeds × 10 Ep2 | **No** |
| Confirmatory | 3 arms × 10 seeds × 30 Ep2 | **Yes** |

See [pre-reg §9](paper002_prereg_wm_expansion_v0.1.md).

---

# 5. Statistical analysis

See [analysis plan v0.3](paper002_analysis_plan_v0.3.md).

- **O1:** paired bootstrap or permutation on (seed, condition) blocks · C vs B  
- **O2:** arm-wise success rate + paired bootstrap  
- **H3:** one-sided non-inferiority · P(static_success_L3 ≥ baseline − δ) > 0.95  
- **H4:** descriptive gate rates + binomial CI by control condition  

**Presentation order:**

```text
1. Ep1 L1 repair failure (O7)
2. Ep2 O1 + O2 by arm
3. Phase 6 static retention (H3)
4. H4 gate controls
5. Mechanism panel (O8) — adjacent to O1/O2
```

---

# 6. Preliminary pilot (Tier B+ · not confirmatory)

> **Fill after mock re-run · label honestly in manuscript**

Engineering mock pilot v0.4 (5 seeds · local CPU · scripted controller · mechanism validation only):

| Metric | Preliminary result |
| --- | --- |
| Ep1 gate fire (drift) | [100% · 5/5] |
| H4 drift_M1 / negatives | [100% / 0%] |
| C vs B ΔPE (H=10) | [+0.122 · ~50% relative] |
| Ep2 success (all arms) | [100% · scripted · not behavior claim] |

Source: [`pilot_v0.1/summary.json`](../../experiments/surgical_intelligence/exp_surg_003_wm_expansion/results/pilot_v0.1/summary.json)

**Manuscript rule:** report in Methods or Supplement as engineering validation · **exclude from confirmatory primary analysis**.

---

# 7. Preregistered results tables (fill post-confirmatory)

## T1 — Protocol accounting

| Phase | Seeds | Ep2 conditions | Arms | Completed | Excluded |
| --- | ---: | ---: | --- | ---: | ---: |
| Confirmatory | | | A/B/C | | |
| H4 controls | | | — | | |

## T2 — Ep1 L1 repair failure (O7 · diagnostic)

| Arm | Mean residual after K repairs | Gate fire rate |
| --- | ---: | ---: |
| B (L1) | | |
| Shared pre-split | | |

## T3 — Primary endpoints (Ep2)

| Arm | O1 PE (H=10) mean ± CI | O2 success rate | Δ vs B (bootstrap CI) |
| --- | --- | ---: | --- |
| A No update | | | |
| B Parameter L1 | | | ref |
| C Modular L3 | | | |
| D Oracle | | | diag |

## T4 — Static retention (H3)

| Arm | Static success rate | vs baseline − δ | H3 pass |
| --- | ---: | ---: | --- |
| B | | | |
| C | | | |

## T5 — Gate validity (H4)

| Condition | P(gate=1) | 95% CI | Expected |
| --- | ---: | --- | --- |
| M1 drift | | | high |
| M0 static | | | low |
| N1 noise | | | low |
| N2 impulse | | | low |

## T6 — Hypothesis decisions

| Hyp | Criterion | Estimate | Pass |
| --- | --- | ---: | --- |
| H1 | C < B on O1 | | |
| H2 | C > B on O2 | | |
| H3 | C non-inferior static · margin δ | | |
| H4 | drift high · controls low | | |

---

# 8. Interpretation rules

| Pattern | Statement |
| --- | --- |
| H1+H2+H3+H4 pass | Prepared structural expansion warranted after failed L1 · improves Ep2 without static harm |
| H1 pass · H2 fail | Better prediction without control transfer — revise MPC / cost / behavior link |
| H1 fail · H2 pass | Behavior gain without PE separation — inspect gate / expert routing |
| H4 fail | Gate not valid — do not claim adequacy-triggered expansion |
| Pilot only · no confirmatory | Mechanism direction only · no venue-grade primary claim |

---

# 9. Limitations

1. Single hidden mode family (static vs drift) — not general ontology invention  
2. Prepared operator menu — not free architecture search  
3. Isaac simulation — not hardware confirmatory (Track B parallel · EXP-REAL-001 after Go gates)  
4. GRU dynamics backbone — RSSM / diffusion deferred  
5. Oracle arm diagnostic — not deployable policy  
6. Pilot thresholds tuned on small seed set — confirmatory uses fresh seeds  

---

# 10. Results template (fill post-run)

## Setup

We pretrained static-only W₀ on [N] M0 episodes. Confirmatory run: [10] seeds × [30] Ep2 conditions × arms A/B/C after pre-reg freeze ([tag · date]). Thresholds τ_error, K, τ_a, τ_nll frozen from pilot only.

## Ep1 failure evidence

After K L1 repairs, mean held-out residual remained [X]. Gate fired on [Y]/[Z] drift episodes. Parameter repair did not absorb structured drift residual (Fig 2).

## Primary Ep2 outcomes

C vs B: ΔPE = [X] (95% CI [L, U]) · success [a]/[n] vs [b]/[n] (Δ = [pp] pp). H1 [pass/fail] · H2 [pass/fail].

## Retention

Static success C vs baseline: [rate] · non-inferiority margin δ = [5] pp. H3 [pass/fail].

## Gate validity

Drift [rate] · noise [rate] · impulse [rate]. H4 [pass/fail].

## Mechanism (exploratory)

[Latent separation · expert entropy · residual autocorrelation — linked to O1/O2 only.]

---

# 11. Figures (pre-specified)

| Fig | Content |
| --- | --- |
| **1** | Protocol diagram · Reality \| Belief · Ep1→gate→arms→Ep2 |
| **2** | Ep1 residual after K L1 repairs · gate inputs |
| **3** | Primary table / bar: O1 + O2 by arm (C vs B highlighted) |
| **4** | Mechanism panel: latent · expert selection · rollout vs actual (supporting) |
| **5** | H4 gate rates by condition |
| **6** | Static retention · non-inferiority margin |

Video (optional): top-down robot · predicted vs actual future · active expert · gate state.

---

# 12. Related work (pointer)

Full positioning: [paper002_related_work_v0.2.md](paper002_related_work_v0.2.md).

Mandatory citations: TMoW · MuSix · Worldscape-MoE · LMC · DRAGO · continual WM lines · sim-to-real (background).

**Wedge sentence:**

> Closest prior work adds experts or routes mixtures; we test **whether failure after failed parameter repair warrants** prepared structural expansion — with gate validity and nominal regression guardrails.

---

# 13. Links

| Resource | Path |
| --- | --- |
| Experiment package | [`exp_surg_003_wm_expansion`](../../experiments/surgical_intelligence/exp_surg_003_wm_expansion/README.md) |
| Status | [status.md](status.md) |
| VESSL runbook | [vessl_runbook_v0.1.md](vessl_runbook_v0.1.md) |
| Physical roadmap | [paper002_physical_validation_roadmap_v0.1.md](paper002_physical_validation_roadmap_v0.1.md) |
| Archived MS (mock→physics) | [paper002_manuscript_pre_results_v0.1.md](paper002_manuscript_pre_results_v0.1.md) |
