# Paper 1 — evidence status (public)

> **Updated:** 2026-07-22 · **Phase C proper executed** (n=20 · Tier C summary committed)  
> **Lab:** 2026-07-21 GO · detail phase → **runner proper → proper run**

---

## Honest one-liner

> We have **not** yet shown a new recoverability **method**. We **have** confirmatory (n=20) evidence that **response choice at fixed mismatch S** yields **separable intervention profiles** — REPLAN_d20 **19/20** vs CONTINUE **0/20** @ 6 cm + occlusion L1.

---

## Phase status

| Phase | Content | Status |
| --- | --- | --- |
| **A** | Smoke atlas 001A–C + D0 + D1 | ✅ Isaac done |
| **B** | Desk review · decisions | ✅ [`phase_b_smoke_review.md`](phase_b_smoke_review.md) |
| **C** | Proper-run pre-reg v1.0 | ✅ **Executed 2026-07-22** · [`phase_c_proper_run_prereg_v1.0.md`](phase_c_proper_run_prereg_v1.0.md) |
| **Lit v2** | Positioning · industry · baseline spec | ✅ [`lit_positioning_v1.md`](lit_positioning_v1.md) |
| **Next** | Promote full JSON · paper draft intro/method | ⏭ |
| **Then** | B2 UQ baseline (optional v1.1) | backlog |

Roadmap: [`roadmap.md`](roadmap.md) · RQ v1.0: [`research_question.md`](research_question.md)

---

## Secured — Phase C proper (Tier C · n=20)

| Mode | Success (n=20) | Notes |
| --- | ---: | --- |
| **CONTINUE** | **0/20** | Primary baseline |
| **REPLAN_d20** | **19/20 (95%)** | Primary contrast · +95 pp vs CONTINUE |
| **REOBSERVE** | **17/20 (85%)** | Exploratory profile |
| **RESHAPE** | **18/20 (90%)** | Exploratory profile |
| **HANDOVER** | 0/20 | Stub · excluded from primary endpoint |

`branch_replay_ok`: **100/100** · committed summary: [`results/study1_proper/summary.json`](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1_proper/summary.json)

---

## Secured — smoke (Tier B · direction only)

| Item | Result |
| --- | --- |
| Same-state counterfactual branching | Shown (001A) |
| Mode @ 3 cm | CONTINUE **0/5** vs REPLAN **4/5** |
| Delay @ 3 cm | Flat REPLAN band 0–20 (001B) |
| Severity × delay | Mostly 0.8–1.0 · no cliff (001C) |
| Occlusion @ 6 cm D0 | REPLAN **5/5** · REOBSERVE **4/5** |
| Occlusion @ 6 cm D1 | + RESHAPE **4/5** · HANDOVER stub **0/5** |
| Fig 4 / Fig 5 captions | Frozen · [`fig_captions.md`](fig_captions.md) |

---

## Not yet (do not claim publicly)

| Item | Status |
| --- | --- |
| Full `isaac_results.json` in committed `results/study1_proper/` | scp from pod optional |
| Recoverability estimator / learned selector | Stage 2 |
| Beat Surgical UQ / B-VAP baselines | Stretch · not implemented |
| Clinical / OR validation | Out of scope Stage 1 |
| Golden-time headline | Delay sweep deferred |

---

## Reports

| Study | Report |
| --- | --- |
| 001A | [`study1a_report.md`](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/study1a_report.md) |
| 001B | [`study1b_report.md`](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/study1b_report.md) |
| 001C | [`study1c_report.md`](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/study1c_report.md) |
| 001D | [`study1d_report.md`](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/study1d_report.md) |
