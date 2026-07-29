# Paper 002 — Pre-registration · WM structural expansion v0.1 (DRAFT)

> **Status:** design · **not frozen** · supersedes mock→physics pre-reg v0.3  
> **Description:** [paper002_description_wm_expansion_v0.1.md](paper002_description_wm_expansion_v0.1.md)

---

## 1. Hypotheses

### H1 — Structural inadequacy detectable (not uncertainty alone)

On Ep1, evidence supports **structural inadequacy** (third category — distinct from distribution shift and epistemic uncertainty):

```text
structured residual persists after ≥ K parameter-update attempts
AND clusters by provisional hidden mode (drift vs static mis-specification)
AND is not absorbed by L1 repair
```

Latent cluster separation is **diagnostic / mechanistic**, not the expansion trigger by itself.

### H2 — Expansion beats parameter update (Ep2 · novel drift)

On Ep2 with **novel drift instance** (≠ Ep1 parameters):

| Arm | Expected ordering |
| --- | --- |
| Structural Expansion | Best: prediction error ↓ · mismatch latency ↓ · success ↑ |
| Parameter Update | Intermediate |
| No Update | Worst |

Primary: **recoverability or task success** on Ep2 (TBD exact threshold · n=20 seeds).

### H3 — No nominal regression

Static-target episodes: Structural Expansion ≈ Parameter Update ≈ No Update (guardrail · pre-specified non-inferiority band).

---

## 2. Design

| Factor | Levels |
| --- | --- |
| Update arm | No · Parameter · Structural |
| True mode | static · drifting |
| Encounter | Ep1 (train failure) · Ep2 (test · novel drift params) |

Agent fixed for v0.1 · response menu TBD (CONTINUE / REPLAN minimum).

**Hidden from initial WM:** `target_mode`  
**Expansion adds:** `target_mode` or binary motion-mode latent

---

## 3. Expansion gate (pre-specified · model-adequacy test)

Expand only if **all** hold on Ep1:

1. ≥ *K* parameter-update attempts on M₀ (L1 repair) attempted  
2. Structured residual norm > τ for ≥ *M* consecutive steps **after each** repair attempt  
3. Residual variance explained by provisional mode cluster > baseline (TBD threshold at freeze)  
4. Prepared L3 expert explains held-out Ep1 trajectories better than L1-only (exploratory diagnostic · TBD)

**Not sufficient alone:** single-step high error · epistemic uncertainty spike · input OOD without failed repair.

Three-way taxonomy (method): distribution shift · epistemic uncertainty · **structural inadequacy**.

---

## 4. Ep2 novelty constraints

Must differ from Ep1 on ≥2 of: start pose · drift vector · drift speed · mismatch onset step.

Same hidden structure: **drifting mode** family.

---

## 5. Outcomes

**Primary presentation order:** Ep1 L1 repair failure diagnostics → Ep2 arm comparison (Layer 3) → latent panel (Fig 4 · supporting).

| ID | Metric | Role | Analysis |
| --- | --- | --- | --- |
| O1 | Next-state prediction error (Ep2) | **Primary** | arm comparison |
| O4 | Recoverability / success (Ep2) | **Primary co-endpoint** | arm comparison |
| O2 | Mismatch detection latency | Secondary | arm comparison |
| O3 | Response selection accuracy | Secondary | arm comparison |
| O5 | Repeated failure rate | Secondary | arm comparison |
| O6 | Static-condition success (guardrail) | H3 | non-inferiority |
| O7 | Ep1 L1 residual after *K* repairs | H1 diagnostic | descriptive |
| O8 | Latent cluster separation (before/after) | **Mechanistic secondary · exploratory** | not expansion trigger |

---

## 6. Analysis plan (sketch)

- Ep2 primary: bootstrap CI on arm differences · hierarchical: Expansion vs Parameter first  
- H3: one-sided non-inferiority vs Parameter on static episodes  
- Ep1 diagnostics: descriptive only for gate triggers  

Permutation / seed holdout: TBD at freeze.

---

## 7. Environment

- Isaac Sim 4.1 · ORBIT Reach (3D rigid · target shift / drift injection)  
- Belief panel logged separately from ground truth for figures  

4D temporal variants (drift profile): **deferred** to extension · not confirmatory v0.1.

---

## 8. Open before freeze

- [ ] Exact τ, *K*, *M* for expansion gate  
- [ ] n seeds · Ep1/Ep2 count per seed  
- [ ] Parameter update algorithm (EKF / heuristic / bounded LS)  
- [ ] Structural expansion operator (hand-designed vs search over finite mode set)  
- [ ] Recoverability definition (Paper 001 fork reuse vs binary success)  
- [ ] O8 latent logging spec (see Appendix A)

---

## Appendix A — Latent logging (mechanistic · exploratory)

> **Status:** secondary endpoint · **not** primary claim · **not** expansion trigger

| Field | Spec |
| --- | --- |
| **When logged** | End Ep1 (pre-expansion) · post-expansion · end Ep2 |
| **What** | Encoder embeddings z_t · optional 2D projection (UMAP/t-SNE · fixed seed) |
| **Fig 4 use** | Before: single cluster · After: mode-separated clusters (qualitative + optional silhouette) |
| **Analysis tier** | Exploratory · descriptive · pairs with O1/O4 · never standalone success criterion |
| **Pre-reg rule** | Cluster separation **cannot** gate expansion · gate uses O7 residual diagnostics only |

Diffusion future generator: **extension arm only** · excluded from confirmatory v0.1 (see [related work v0.2](paper002_related_work_v0.2.md)).

---

## 9. Tags

Freeze → `paper002-prereg-wm-v0.1` · new config path TBD (`exp_surg_003_wm_expansion/` or extend exp_surg_002 with new sandbox)
