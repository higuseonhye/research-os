# EXP-SURG-001D Report — Occlusion × multi-mode (Isaac D0 + D1)

> **D0:** `992141a` · 2026-07-20 · 3-mode smoke  
> **D1:** `992141a` · 2026-07-20 · 5-mode smoke atlas (25 branches)  
> **Proxy:** gain_scale_flag v0.1 · **RunPod:** `run_study1d_runpod.sh`

## Question

Under **P3 occlusion** (gain-scale proxy) with **6 cm target shift**, which responses remain outcome-feasible at the same onset state — and do profiles differ from shift-only 001A–C?

## Design (shared)

- Task: `Isaac-Reach-Dual-STAR-IK-Rel-Play-v0` · scripted IK-Rel · body 13
- Shift: **+0.06 m Y** @ onset step 20 · REPLAN delay **20** steps
- Occlusion: level 1 · `visibility_fraction=0.35` · contract in [`docs/study1d_occlusion_proxy_v0.1.md`](docs/study1d_occlusion_proxy_v0.1.md)
- Seeds: **0–4** (n=5 per mode) · smoke atlas only

---

## D0 — 3-mode (CONTINUE / REPLAN / REOBSERVE)

| Response | Class | n | Success | Violation | Mean dist (m) |
| --- | --- | ---: | ---: | ---: | ---: |
| CONTINUE | policy | 5 | **0 / 5** | 0 / 5 | 0.1669 |
| REPLAN_d20 | policy | 5 | **5 / 5** | 0 / 5 | 0.0194 |
| REOBSERVE | policy_information | 5 | **4 / 5** | 0 / 5 | 0.1749 |

REOBSERVE mean dist inflated by **seed 0 outlier** (0.80 m timeout); seeds 1–4 ≈ 0.017–0.020 m.

Committed: [`results/study1d_isaac/`](results/study1d_isaac/)

---

## D1 — 5-mode (+ RESHAPE / HANDOVER)

| Response | Class | n | Success | Violation | Mean dist (m) |
| --- | --- | ---: | ---: | ---: | ---: |
| CONTINUE | policy | 5 | **0 / 5** | 0 / 5 | 0.1728 |
| REPLAN_d20 | policy | 5 | **5 / 5** | 0 / 5 | 0.0191 |
| REOBSERVE | policy_information | 5 | **4 / 5** | 0 / 5 | 0.1753 |
| RESHAPE | environment | 5 | **4 / 5** | 0 / 5 | 0.1467 |
| HANDOVER | collaboration | 5 | **0 / 5** | 0 / 5 | 0.3454 |

### Notable branches

| Seed | Mode | Outcome | Notes |
| ---: | --- | --- | --- |
| 0 | REOBSERVE | fail 0.799 m | Same ep0 outlier as D0 |
| 2 | RESHAPE | fail 0.657 m | timeout after visibility cleared |
| all | HANDOVER | fail | `handover_proxy` stub — collaboration class logged, not recoverable endpoint |

### Reading (smoke · not confirmatory)

- **Policy / info / environment:** REPLAN **5/5** · REOBSERVE **4/5** · RESHAPE **4/5** vs CONTINUE **0/5**
- **RESHAPE ≈ REPLAN** on most seeds — environment-class proxy competitive at smoke n
- **HANDOVER 0/5** expected — v0.1 stub terminates early; proper run needs real handover semantics
- **Phase A smoke atlas complete** → Phase B whole review

Committed: [`results/study1d_isaac/d1/`](results/study1d_isaac/d1/)

---

## Lab one-liners

- **D0:** occlusion @ 6 cm · REPLAN d20 **5/5** vs CONTINUE **0/5** · REOBSERVE **4/5**
- **D1:** + RESHAPE **4/5** · HANDOVER stub **0/5** (smoke scaffold)

## Artifacts

- D0 aggregate: `results/study1d_isaac/isaac_aggregate.json`
- D1 aggregate: `results/study1d_isaac/d1/isaac_aggregate.json`
- Pod raw (gitignored): `artifacts/study1d_occlusion_multimode/isaac_full/isaac_results.json`

## Next

- **Phase B:** whole review → proper-run pre-reg v1.0
- Pod merge fix: `git pull` + `run_study1d.py --merge --full` (old commit read D0 smoke JSON first)
