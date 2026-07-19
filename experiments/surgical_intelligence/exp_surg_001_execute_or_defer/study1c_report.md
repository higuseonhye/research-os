# EXP-SURG-001C Report — Severity × Delay Surface

> **Status:** full grid complete · **Mode:** `isaac` · **Date:** 2026-07-16  
> **RunPod:** full grid · merge OK · Artifacts on pod volume (gitignored)  
> **Committed aggregate:** [`results/study1c_isaac/`](results/study1c_isaac/)

## Core question

How do mismatch severity and intervention delay jointly affect successful resolution under replanning?

## Design

- Severities (m): 0.01, 0.03, 0.06, 0.09 (1, 3, 6, 9 cm)
- Delays: 0, 5, 10, 20, 40, 60 steps after onset
- Seeds: 0, 1, 2, 3, 4 (n=5 per cell)
- CONTINUE: once per severity × seed; REPLAN: each severity × delay × seed
- Same-state branch replay · onset 20 · tol 0.02 m · scripted 6D IK-Rel · body 13

## Observed results (Isaac full grid)

- Branch records: **140** REPLAN + 20 CONTINUE = **160** total (all branch_replay_ok=True on pod)
- Task: `Isaac-Reach-Dual-STAR-IK-Rel-Play-v0`

### Aggregate REPLAN success (severity × delay)

| shift (cm) | delay | n | success rate | mean final dist (m) | violation rate |
| --- | --- | --- | --- | --- | --- |
| 1 | 0 | 5 | 1.000 | 0.0000 | 0.000 |
| 1 | 5 | 5 | 1.000 | 0.0000 | 0.000 |
| 1 | 10 | 5 | 1.000 | 0.0000 | 0.000 |
| 1 | 20 | 5 | 1.000 | 0.0000 | 0.000 |
| 1 | 40 | 5 | 1.000 | 0.0000 | 0.000 |
| 1 | 60 | 5 | 1.000 | 0.0198 | 0.000 |
| 3 | 0 | 5 | **0.800** | 0.1376 | 0.000 |
| 3 | 5 | 5 | **0.800** | 0.1099 | 0.000 |
| 3 | 10 | 5 | 1.000 | 0.0192 | 0.000 |
| 3 | 20 | 5 | **0.800** | 0.1403 | 0.000 |
| 3 | 40 | 5 | 1.000 | 0.0190 | 0.000 |
| 3 | 60 | 5 | 1.000 | 0.0189 | 0.000 |
| 6 | 0 | 5 | 1.000 | 0.0196 | 0.000 |
| 6 | 5 | 5 | **0.800** | 0.0190 | **0.200** |
| 6 | 10 | 5 | 1.000 | 0.0191 | 0.000 |
| 6 | 20 | 5 | **0.800** | 0.1417 | 0.000 |
| 6 | 40 | 5 | 1.000 | 0.0190 | 0.000 |
| 6 | 60 | 5 | 1.000 | 0.0191 | 0.000 |
| 9 | 0 | 5 | **0.800** | 0.1319 | 0.000 |
| 9 | 5 | 5 | 1.000 | 0.0194 | 0.000 |
| 9 | 10 | 5 | **0.800** | 0.1783 | 0.000 |
| 9 | 20 | 5 | 1.000 | 0.0190 | 0.000 |
| 9 | 40 | 5 | **0.800** | 0.1287 | 0.000 |
| 9 | 60 | 5 | 1.000 | 0.0190 | 0.000 |

### Empirical latest viable delay (success ≥ 0.8, tested grid only)

| shift (cm) | latest viable delay (steps) |
| --- | --- |
| 1 | 60 |
| 3 | 60 |
| 6 | 60 |
| 9 | 60 |

Not a universal golden time — maximum delay **within this tested grid** where aggregate rate still ≥ 0.8.

### 3 cm flat band (vs 001B)

- **001B (n=3):** REPLAN 3/3 at delays 0–20 — flat high-recoverability band.
- **001C full @ 3 cm (n=5):** success **0.8–1.0** depending on delay; failures show **~0.11–0.14 m** residual (not tol), not a monotonic delay cliff.
- **Finding:** Strict 001B flat band **narrows** under expanded grid; **no severity-driven delay cliff** up to 60 steps in this scripted setting.

### Severity × delay interaction

- **Not observed** (no monotonic increase in delay sensitivity across 1–9 cm).
- Pattern is **cell-wise seed variance** (4/5 success) more than systematic delay degradation.

## Interpretations (not claims)

- Under scripted IK-Rel on ORBIT Reach PLAY, **REPLAN remains broadly recoverable** across 1–9 cm and delays 0–60 at ≥80% aggregate success.
- **Whether to replan** (001A) still dominates **small delay** in expectation; **timing cliff not shown** in this surface.
- 6 cm @ delay 5 shows **forbidden violation** in 1/5 seeds — environment/safety coupling worth tracking in 001D.
- Results do **not** support clinical replan windows or universal golden time.

## Unsupported claims

- Universal golden time for replanning
- Clinical OR performance
- Learned meta-policy superiority
- Severity × delay interaction as paper headline (not supported here)

## Simulator / controller limitations

- Scripted 6D IK-Rel proposer (not learned policy)
- n=5 per cell; 4/5 vs 5/5 drives many 0.800 rates
- Forbidden region is axis-aligned proxy
- PhysX mass/inertia warnings on robot USD (benign for this reach task)

## Recommendation for EXP-SURG-001D

- **Condition:** 6 cm shift, replan delay 20 steps
- **Rationale:** Mid-grid baseline on a mostly flat surface; some cells at 0.8 with large residual distance — useful before adding **occlusion / environment** interventions

## Artifacts

**Pod (full):** `artifacts/study1c_severity_delay_surface/` — json, csv, figures, videos  
**Committed:** `results/study1c_isaac/summary.json`, `tables/aggregate_by_severity_delay.csv`  
**Copy figures from pod:** `artifacts/.../figures/*.png` → scp before Stop if needed
