# EXP-SURG-001A Report — Counterfactual Recovery Smoke

> **Mode:** `isaac` (primary) · scripted IK-Rel proposer · **Date:** 2026-07-16  
> Earlier `mock` table below is pipeline-only; do **not** cite mock as physics evidence.

## Question

Same target-shift branch point → do **CONTINUE** vs **REPLAN** yield different terminal outcomes?
Preferred response is **not** taken from taxonomy labels.

## Isaac results (n=5 episodes × 2 branches)

Task: `Isaac-Reach-Dual-STAR-IK-Rel-Play-v0`  
Proposer: body-frame 6D pose_rel P-control on `robot_1` / `endo360_needle` (body 13)  
Shift: +0.03 m in Y at onset step 20 · success tol 0.02 m · max-steps 160 · episode_length_s 20

| Response | Success | Unsafe | Timeout | Mean final dist (m) |
| --- | ---: | ---: | ---: | ---: |
| CONTINUE | **0 / 5** | 0 | 5 | 0.1415 |
| REPLAN | **4 / 5** | 1 | 0 | 0.0194 |

### Per-episode

| Ep | CONTINUE | REPLAN |
| --- | --- | --- |
| 0 | timeout 0.591 m @160 | success 0.019 m @124 |
| 1 | timeout 0.030 m @160 | success 0.019 m @101 |
| 2 | timeout 0.029 m @160 | **unsafe** 0.020 m @64 |
| 3 | timeout 0.030 m @160 | success 0.020 m @50 |
| 4 | timeout 0.027 m @160 | success 0.019 m @39 |

### Reading

- **H1 direction (replan ≻ continue on success):** supported in this smoke (0/5 vs 4/5).
- CONTINUE ep1–4 land ~2.7–3.0 cm from the **shifted** target — consistent with successfully tracking the **frozen** target after a 3 cm shift (geometry, not random failure).
- CONTINUE ep0 is a true miss (59 cm); treat as hard failure under the same proposer.
- REPLAN ep2 reached tol but `unsafe_failure` (forbidden proxy) — success≠safe; keep for 001B / safety notes.
- This is **scripted** reach, n=5, one seed family — **not** a learned meta-policy result and **not** Paper 1 claim-ready alone.

## What we fixed to make Isaac informative

1. Action contract: 12D = arm1(6)+arm2(6) IK-Rel `pose_rel` (xyz + axis-angle).
2. Track body: `endo360_needle` (13), not `star_link_ee` (9).
3. Episode horizon: default ~5 s (~150 steps) was truncating long control; use `episode_length_s=20`.
4. Judge **min/terminal distance to shifted target**, not post-timeout end distance after env reset.

## What we did **not** verify

- Camera reshape / handover / LLM / learned meta-policy
- Full golden-time curve (EXP-SURG-001B)
- Physics-faithful forbidden collider (proxy AABB)
- Clinical or surgical autonomy claims

## Mock (pipeline only — superseded for empirics)

| Response | Success rate | Mean final dist (m) |
| --- | ---: | ---: |
| CONTINUE | 0.000 | 0.0300 |
| REPLAN | 1.000 | 0.0140 |

## Artifacts

Committed (this repo):

- `results/study1a_isaac/isaac_aggregate.json`
- `results/study1a_isaac/tables/quantitative_results.csv`
- `results/study1a_isaac/figures/result_table.png`
- `results/study1a_isaac/figures/counterfactual_grid.png`
- `results/study1a_isaac/figures/final_distance_by_episode.png`

RunPod (often gitignored under `artifacts/`): full `isaac_results.json` — copy locally before pod stop.

### Visualization decision (now)

- **Do:** offline PNG/CSV from Isaac numbers (above) — Paper Fig 4 draft.
- **Defer:** W&B live logging; Isaac GUI / stream on RunPod.
- **Later:** one short camera capture run for A3 video/GIF after 001B timing curve is designed.

Regenerate figures:

```bash
python scripts/plot_study1a_isaac_results.py
```

## Next smallest experiment

**EXP-SURG-001B** — Replan at t+0 / t+5 / t+10 / t+20 → empirical recoverability vs delay (Fig 5).  
See [`study1b_report.md`](study1b_report.md).

### Backup (001A JSON)

- Same pod + **Stop** only: file stays on `/workspace` — optional to scp before 001B.
- **Terminate** / new volume: scp `isaac_results.json` first.

Optional desk: pull `isaac_results.json`, freeze this table into the Paper-First artifact package, stop RunPod.
