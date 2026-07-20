# EXP-SURG-001D Report — Occlusion × multi-mode (D0)

> **Mode:** `mock` · **Commit:** `3a2c99b1ec1520c27a9ed64a4554eff6eb4362ad` · **Proxy:** gain_scale_flag v0.1

## Design

- Shift: **0.06 m** · REPLAN delay **20** steps
- Occlusion proxy: `gain_scale_flag` · contract in docs/study1d_occlusion_proxy_v0.1.md

## Aggregate

| Response | Class | n | Success | Violation | Mean dist (m) |
| --- | --- | ---: | ---: | ---: | ---: |
| CONTINUE | policy | 1 | 0.000 | 0.000 | 0.0600 |
| REOBSERVE | policy_information | 1 | 1.000 | 0.000 | 0.0000 |
| REPLAN_d20 | policy | 1 | 1.000 | 0.000 | 0.0000 |

## Per-branch

- seed=0 CONTINUE success=False dist=0.0600 cleared=False
- seed=0 REPLAN_d20 success=True dist=0.0000 cleared=False
- seed=0 REOBSERVE success=True dist=0.0000 cleared=True
