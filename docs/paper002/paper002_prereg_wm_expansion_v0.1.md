# Paper 002 — Pre-registration · WM structural expansion v0.1 (DRAFT)

> Superseded before confirmatory data by
> [model-order confirmatory preregistration v1.0](paper002_model_order_confirmatory_prereg_v1.0.md).

> **Status:** design · **not frozen** · supersedes mock→physics pre-reg v0.3  
> **Confirmatory spec:** [paper002_confirmatory_spec_v0.1.md](paper002_confirmatory_spec_v0.1.md)  
> **Analysis:** [paper002_analysis_plan_v0.3.md](paper002_analysis_plan_v0.3.md)

---

## 0. Primary RQ

> When a fixed dynamics model cannot explain **persistent drift failure** with parameter update alone, does adding a **drift dynamics expert** (L3) improve **held-out drift prediction** and **Ep2 control**, without **nominal static regression**?

---

## 1. Hypotheses

### H1 — Prediction

L3 modular expansion shows **lower held-out drift trajectory prediction error** than L1 parameter update on Ep2 (multi-step horizon **H=10**).

### H2 — Behavior

L3 shows **higher Ep2 task success** (or recoverability) than L1 on held-out drift conditions.

### H3 — Retention

L3 does **not** degrade nominal static success beyond pre-specified margin **δ** (non-inferiority).

### H4 — Gate validity

Rule-based expansion gate activates on **persistent drift (M1)** · rarely on **observation noise (N1)** · **single impulse (N2)** · **nominal static (M0)**.

---

## 2. Design

| Factor | Levels |
| --- | --- |
| Update arm | A No update · B Parameter (L1) · C Modular expansion (L3) · D Oracle (diagnostic) |
| True mode | M0 static · M1 drift |
| Protocol | Phase 0 pretrain → Ep1 → K repairs → gate → intervention → Ep2 → static retention |

**Hidden from initial WM:** `target_mode` · drift velocity  
**L3 adds:** F1 drift expert + gate G (not latent scalar alone)

**Controller:** MPC / model-based trajectory selection (v0.1).

---

## 3. Arms

| Arm | Intervention |
| --- | --- |
| A | `W_after = W0` |
| B | Fine-tune F0 only · `θ0 → θ0'` |
| C | Add F1 + G · F0 frozen or low LR |
| D | Oracle mode label to gate · upper bound only |

**Primary contrast:** C vs B · equal **data budget** across arms.

---

## 4. Protocol phases

| Phase | Content |
| --- | --- |
| 0 | Pretrain W0 on M0 static only |
| 1 | Ep1 drift exposure · log full trajectory |
| 2 | K parameter repair attempts on F0 |
| 3 | Rule-based expansion gate |
| 4 | Arm intervention |
| 5 | Ep2 novel drift (≥2 params differ from Ep1) |
| 6 | Static retention (M0) |

Ep1 evidence identical across arms before split.

---

## 5. Expansion gate (rule-based · pre-specified)

```text
Gate = 1 iff ALL:
  mean(residual_after_repair) > τ_error
  K repair attempts completed without absorbing residual
  residual_autocorrelation > τ_a
  ΔNLL = NLL(F0_repaired) - NLL(F1_candidate) > τ_nll   [held-out Ep1 slice]
```

Structural inadequacy · not distribution shift or epistemic uncertainty alone.

Latent cluster metrics **do not** trigger gate (Appendix A).

---

## 6. Ep2 novelty

≥2 differ from Ep1 among: initial target · drift direction · drift speed · drift onset · robot initial joints.  
Same regime: **M1 drift**.

---

## 7. Gate negative controls (H4)

| ID | Condition |
| --- | --- |
| N1 | ↑ target observation noise · M0 static |
| N2 | Single target impulse then stop |
| — | Nominal M0 · persistent M1 |

---

## 8. Outcomes

**Presentation:** Ep1 L1 failure → Ep2 O1/O2 → static retention → H4 → latent (supporting).

| ID | Metric | Role |
| --- | --- | --- |
| O1 | Multi-step prediction error Ep2 · **H=10** | **Primary** |
| O2 | Ep2 task success | **Primary** |
| O6 | Static retention success | H3 · non-inferiority |
| O9 | Gate activation rate by condition | H4 |
| O7 | Ep1 residual after K L1 repairs | H1 diagnostic |
| O2b | Recoverability composite | Secondary (optional) |
| O3–O5 | Latency · tracking · safety · effort | Secondary |
| O8 | Latent / expert / residual mechanistic | Exploratory |

---

## 9. Sample size

| Tier | Design | In confirmatory? |
| --- | --- | --- |
| Engineering pilot | 3 arms × 5 seeds × 10 Ep2 | No |
| Confirmatory | 3 arms × 10 seeds × 30 Ep2 | Yes |
| Minimum start | 10 seeds × 20 Ep2 conditions | Yes |

Paired: same (seed, condition) across arms.

---

## 10. Analysis

See [paper002_analysis_plan_v0.3.md](paper002_analysis_plan_v0.3.md).

- Primary: C vs B on O1 · O2  
- H3: one-sided non-inferiority · margin **δ** (candidate 5 pp)  
- H4: gate rates by control condition  

---

## 11. Environment

- Isaac Sim 4.1 · ORBIT Reach  
- Config: [`confirmatory_v0.1.yaml`](../../experiments/surgical_intelligence/exp_surg_003_wm_expansion/config/confirmatory_v0.1.yaml)  
- Drift via env: `target_mode · drift_velocity · drift_onset · drift_duration`

---

## 12. Open before freeze

- [ ] τ_error · K · τ_a · τ_nll (from pilot seeds only)  
- [ ] Pretrain success floor · ε · N consecutive steps  
- [ ] F0 parameter update algorithm · step budget  
- [ ] F1 + G training budget · F0 freeze policy  
- [ ] δ non-inferiority margin  
- [ ] MPC horizon · cost weights  
- [ ] Exclusion rules  
- [ ] Confirmatory seed list (generated post-pilot)

---

## Appendix A — Latent logging (mechanistic · exploratory)

| Field | Spec |
| --- | --- |
| **When** | Every step Ep1/Ep2 · snapshots pre/post expansion |
| **Log** | `z_t` · predicted z rollouts · residual · uncertainty · gate p · selected expert · action · success |
| **Analysis** | static/drift probe · silhouette · expert entropy · CKA before/after |
| **Rule** | **Not** primary endpoint · **not** gate trigger |
| **Claim text** | Must link to O1/O2: separation **associated with** lower error and higher success |

Diffusion WM: extension only · not confirmatory v0.1.

---

## 13. Tags

Freeze → `paper002-prereg-wm-v0.1` · experiment `exp_surg_003_wm_expansion`

**First milestone (engineering):** L1 repair fails · L3 explains held-out drift on pilot seeds.
