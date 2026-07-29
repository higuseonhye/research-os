# Model Adequacy Benchmark v0.1

> Public benchmark spec for Mismatch Lab · aligned with Paper 002 H4

---

## Purpose

Evaluate whether a system can distinguish:

1. **Transient noise** vs **persistent structural mismatch**
2. **Parameter error** vs **missing dynamics mode**
3. **Recoverable via repair** vs **expansion warranted**

This is a **classification + ranking** benchmark — not end-task success alone.

---

## Tasks

| Task ID | Condition | Expected adequacy hint | Gate should fire |
| --- | --- | --- | --- |
| **M0-static** | No drift · static target | `none` | No |
| **N1-noise** | Observation noise · static dynamics | `none` or `watch` | No |
| **N2-impulse** | Single target impulse | `replan` | No / low |
| **M1-drift-x** | Persistent drift +x | `structural_review` | Yes |
| **M1-drift-y** | Persistent drift +y (held-out dir) | `structural_review` | Yes |
| **M1-drift-diag** | Diagonal drift (Ep2 novelty) | `structural_review` | Yes |

---

## Inputs (per episode)

Required fields in RunBundle:

```json
{
  "trajectory": {"obs": "T×D float", "actions": "T×A float"},
  "predictions": {"one_step": "T×D float", "optional_multi_step": "..."},
  "recovery_attempts": [{"step": "int", "residual_after": "float"}],
  "metadata": {"task": "string", "seed": "int", "condition_id": "string"}
}
```

---

## Scoring

### Primary metrics

| Metric | Definition |
| --- | --- |
| **H4 accuracy** | Fraction of episodes where `adequacy_hint` matches gold label |
| **False expansion rate** | P(`structural_review` \| N1 or N2 or M0) |
| **Miss rate** | P(`none` or `watch` \| M1) |

### Secondary metrics

| Metric | Definition |
| --- | --- |
| **Onset error** | \|predicted_onset − true_onset\| steps |
| **Repair sufficiency AUC** | Predict `repair_likely_sufficient` vs gold from repair curve |
| **Calibration** | Brier score on adequacy_score (when labeled) |

---

## Gold labels (v0.1)

Derived from EXP-SURG-003 protocol:

- **Gold adequacy hint** from gate + repair residuals on Ep1 adaptation window
- **Gold classification** from `DriftSpec.mode` + velocity direction
- **Gold repair_sufficient** = final repair residual ≤ τ_error after K attempts

Confirmatory tier adds Isaac traces with independent human review sample (n≥20).

---

## Baselines

| Baseline | Description |
| --- | --- |
| **Threshold-only** | Fire if mean prediction error > τ |
| **Repair-count** | Fire if K repairs fail (no autocorr · no ΔNLL) |
| **Paper 002 gate** | Full rule-based gate (pre-registered) |
| **Oracle** | Privileged mode label (upper bound · not deployable) |

---

## Leaderboard rules (public)

1. Submit JSON predictions on frozen seed list · no training on confirmatory seeds
2. Report H4 accuracy + FP rate on negatives + miss rate on M1
3. Disclose: mock-only vs Isaac · scripted vs MPC behavior
4. Preliminary mock results labeled **Tier P** · Isaac **Tier I** · hardware **Tier H**

---

## Data release (v0.1)

| Asset | Format | Source |
| --- | --- | --- |
| 4 explorer cases | JSON | Mock pilot export |
| 5-seed pilot bundle | JSON | `exp_surg_003` results |
| Gate control episodes | JSON | H4 negative controls |

Full confirmatory bundle after prereg lock.

---

## Connection to Robot Diff

Benchmark tasks map 1:1 to Diff Explorer cases:

- Case 1 → policy comparison (no benchmark label)
- Case 2 → M1-drift-x onset visualization
- Case 3 → repair plateau · gold `structural_review`
- Case 4 → N1 vs M1 side-by-side

---

*Updated 2026-07-29*
