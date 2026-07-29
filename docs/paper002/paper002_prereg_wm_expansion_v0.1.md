# Paper 002 — Pre-registration · WM structural expansion v0.1 (DRAFT)

> **Status:** design · **not frozen** · supersedes mock→physics pre-reg v0.3  
> **Description:** [paper002_description_wm_expansion_v0.1.md](paper002_description_wm_expansion_v0.1.md)

---

## 1. Hypotheses

### H1 — Structural gap detectable

Persistent structured residual after ≥ *K* parameter-update attempts on Ep1 clusters by true latent mode (drift vs static mis-specification).

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

## 3. Expansion gate (pre-specified)

Expand only if all hold on Ep1:

1. Residual norm > τ for ≥ *M* steps after parameter update  
2. ≥ *K* parameter updates attempted  
3. Residual variance explained by provisional mode cluster > baseline (exploratory threshold TBD)

---

## 4. Ep2 novelty constraints

Must differ from Ep1 on ≥2 of: start pose · drift vector · drift speed · mismatch onset step.

Same hidden structure: **drifting mode** family.

---

## 5. Outcomes

| ID | Metric | Analysis |
| --- | --- | --- |
| O1 | Next-state prediction error (Ep2) | Primary · arm comparison |
| O2 | Mismatch detection latency | Secondary |
| O3 | Response selection accuracy | Secondary |
| O4 | Recoverability / success (Ep2) | Primary co-endpoint |
| O5 | Repeated failure rate | Secondary |
| O6 | Static-condition success (guardrail) | H3 |

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

---

## 9. Tags

Freeze → `paper002-prereg-wm-v0.1` · new config path TBD (`exp_surg_003_wm_expansion/` or extend exp_surg_002 with new sandbox)
