# Paper 1 — evidence status (public)

> **Updated:** 2026-07-24 · **Pre-reg v2.0 complete** (D0 + D1–D3 · Tier C)  
> **Program:** publication-grade proper run · [`phase_c_proper_run_prereg_v2.0.md`](phase_c_proper_run_prereg_v2.0.md)

---

## Honest one-liner

> Same-state counterfactual profiles @ fixed mismatch **S** separate intervention classes — REPLAN **19/20** vs CONTINUE **0/20** @ 6 cm + occlusion (D0). Multi-mode best (**95%**) beats UQ-inspired binary rule (**0%** success · 20/20 handover) and situation rule REOBSERVE path (**85%**) on pre-registered success metric (D2–D3).

---

## Phase status

| Phase | Content | Status |
| --- | --- | --- |
| **A** | Smoke atlas 001A–D | ✅ Tier B |
| **B** | Desk review | ✅ |
| **C v1.0** | D0 primary cell | ✅ 2026-07-22 |
| **C v2.0** | D1–D3 baselines + control | ✅ **2026-07-24** VESSL |
| **Lit v2** | Positioning | ✅ |
| **Next** | Paper draft · Fig 4 baseline overlay | ⏭ |

---

## Proper program — D0 (anchor · occlusion L1)

| Mode | Success (n=20) | Notes |
| --- | ---: | --- |
| **CONTINUE** | **0/20** | |
| **REPLAN_d20** | **19/20 (95%)** | Primary contrast |
| **REOBSERVE** | **17/20 (85%)** | Exploratory |
| **RESHAPE** | **18/20 (90%)** | Exploratory |
| **HANDOVER** | 0/20 | Stub |

[`study1_proper/summary.json`](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1_proper/summary.json)

---

## Proper program — v2.0 (D1–D3 · 2026-07-24)

| Block | Sub-RQ | Result (n=20 unless noted) |
| --- | --- | --- |
| **D1** no occlusion | RQ-P | CONTINUE **1/20** · REPLAN **19/20** — REPLAN unchanged vs D0; CONTINUE 0→1 descriptive |
| **D2** B2 UQ rule | RQ-B | **HANDOVER 20/20** · success **0/20** (vis rule always fires @ L1) |
| **D3** B3 situation rule | RQ-B | **REOBSERVE 17/20 (85%)** — matches D0 REOBSERVE arm |

**RQ-B (pre-reg Option A):** best-of-menu **95%** > B2 **0%** · **95%** > B3 **85%** · direction met.

`branch_replay_ok`: **80/80** · [`study1_proper_v2/summary.json`](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1_proper_v2/summary.json)

---

## Claim tier

| Tier | Evidence |
| --- | --- |
| **C confirmatory** | D0 + D1–D3 · n=20 per branch · pre-reg v2.0 |
| **B smoke** | 001A–D design input only |

---

## Not claimed

- Learned UQ ensemble · clinical deployment · golden-time law · Study 002 body

---

## Reports

| Study | Report |
| --- | --- |
| 001A–D | [`exp_surg_001_execute_or_defer/`](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/) |
