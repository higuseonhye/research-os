# EXP-SURG-001D Report — Occlusion × multi-mode (Isaac D0)

> **Mode:** `isaac` · **Commit:** `992141a` · **Date:** 2026-07-20  
> **Proxy:** gain_scale_flag v0.1 · **RunPod:** `run_study1d_runpod.sh` · seeds 0–4

## Question

Under **P3 occlusion** (gain-scale proxy) with **6 cm target shift**, which responses remain outcome-feasible at the same onset state — and do profiles differ from shift-only 001A–C?

## Design

- Task: `Isaac-Reach-Dual-STAR-IK-Rel-Play-v0` · scripted IK-Rel · body 13
- Shift: **+0.06 m Y** @ onset step 20 · REPLAN delay **20** steps
- Occlusion: level 1 · `visibility_fraction=0.35` · contract in [`docs/study1d_occlusion_proxy_v0.1.md`](docs/study1d_occlusion_proxy_v0.1.md)
- Seeds: **0–4** (n=5 per mode)

## Isaac results (aggregate)

| Response | Class | n | Success | Violation | Mean dist (m) |
| --- | --- | ---: | ---: | ---: | ---: |
| CONTINUE | policy | 5 | **0 / 5** | 0 / 5 | 0.1669 |
| REPLAN_d20 | policy | 5 | **5 / 5** | 0 / 5 | 0.0194 |
| REOBSERVE | policy_information | 5 | **4 / 5** | 0 / 5 | 0.1749 |

Mean dist for REOBSERVE is inflated by **seed 0 outlier** (0.80 m timeout); seeds 1–4 ≈ 0.017–0.020 m.

## Per-seed

| Seed | CONTINUE | REPLAN_d20 | REOBSERVE |
| ---: | --- | --- | --- |
| 0 | fail 0.606 m | success 0.019 m | **fail** 0.799 m (timeout, cleared) |
| 1 | fail 0.059 m | success 0.019 m | success 0.020 m |
| 2 | fail 0.060 m | success 0.020 m | success 0.017 m |
| 3 | fail 0.060 m | success 0.019 m | success 0.019 m |
| 4 | fail 0.050 m | success 0.020 m | success 0.019 m |

## Reading (not claims)

- **Mode separation:** REPLAN **5/5** vs CONTINUE **0/5** — same direction as 001A under occlusion + 6 cm anchor.
- **001C anchor holds:** REPLAN @ 6 cm · d20 remains fully recoverable with P3 proxy active.
- **REOBSERVE 4/5:** supported vs CONTINUE; **seed 0** hard miss (cf. 001A ep0) — do not over-read mean dist.
- **Not claim-ready alone:** RESHAPE/HANDOVER (D1) · clinical · learned selector.

## Artifacts

- Committed: [`results/study1d_isaac/`](results/study1d_isaac/)
- Pod full JSON (gitignored): `artifacts/study1d_occlusion_multimode/isaac_smoke/isaac_results.json`

## Next

- **D1:** `STUDY1D_FULL=1` — RESHAPE + HANDOVER
- Optional: replace `isaac_aggregate.json` with full pod JSON after scp
