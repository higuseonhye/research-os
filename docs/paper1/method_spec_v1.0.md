# Paper 1 — Method spec v1.0 (public)

> **Status:** v1.0 · aligns with RQ [v1.1](research_question.md) · pre-reg v2.0 in design  
> **Private draft:** builder-os-private `paper1_method_spec_v1.0.md`

---

## Pipeline

```text
Nominal rollout (0 … onset−1) → record actions → mismatch @ S → replay → fork(response) → judge → profile
```

**Same-state counterfactual evaluation:** all branches share identical trajectory through mismatch onset **S**; only post-onset intervention differs. CF is **method**, not a learned recoverability estimator.

---

## Mismatch onset **S**

| Parameter | Anchor (D0–D3) | D1 control |
| --- | --- | --- |
| Task | `Isaac-Reach-Dual-STAR-IK-Rel-Play-v0` | same |
| Onset step | 20 | 20 |
| Target shift (P2) | +0.06 m Y | same |
| Occlusion (P3) | L1 · visibility 0.35 · gain_scale v0.1 | **none** |
| REPLAN delay | 20 steps | 20 |
| Horizon | 160 steps | 160 |
| Proposer | Scripted 6D IK-Rel · body 13 | same |

Proxy contract: [`study1d_occlusion_proxy_v0.1.md`](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/docs/study1d_occlusion_proxy_v0.1.md).

---

## Replay contract

1. Fix seed · reset · run steps `[0, onset)` · store `pre_actions`.
2. Capture `frozen_xyz` · apply shift → `shifted_xyz`.
3. Per branch: reset(same seed) · replay `pre_actions` · diverge response from step `onset`.

**Invariant:** `branch_replay_ok = true` on all branches.

Forbidden AABB (EE proxy): center `[0.45, 0, 0.15]` · half-extent `0.04` m.

---

## Response menu (D0)

| Mode | Behavior after S |
| --- | --- |
| CONTINUE | Chase frozen target · occluded gain scale |
| REPLAN_d20 | Frozen until t+20 · then shifted target |
| REOBSERVE | 10-step hold · clear visibility · replan shifted |
| RESHAPE | 20-step reshape proxy · clear · replan |
| HANDOVER | Zero-action stub · early terminal |

Runners: [`orbit_reach_study1a_counterfactual.py`](../../scripts/orbit_reach_study1a_counterfactual.py) · [`orbit_reach_study1d_counterfactual.py`](../../scripts/orbit_reach_study1d_counterfactual.py).

---

## Rule baselines (D2 · D3 · v2.0)

**B2 — UQ-inspired binary:** visibility & distance thresholds → HANDOVER_stub vs CONTINUE (rule proxy · not learned UQ).

**B3 — Situation rule:** occluded_shift → REOBSERVE path · shift_only → REPLAN_d20 · else CONTINUE.

Constants frozen in pre-reg v2.0. Desk spec: private `baseline_spec_phase_c_v1.0.md`.

---

## Terminal judge

**Primary — successful resolution:**

- Distance to **shifted** target ≤ **0.02 m**
- No forbidden violation
- Not handover stub exit
- Within max steps

**Categories:** `successful_resolution` · `unsafe_failure` · `timeout_failure` · `safe_unresolved` · `handover_proxy`.

HANDOVER excluded from primary endpoint · reported as burden proxy.

---

## Claim tiers

| Tier | Label |
| --- | --- |
| A | Scaffold / protocol |
| B | Smoke n≤5 (001A–D) |
| C | Pre-reg n=20 · D0–D3 executed · v2.0 complete 2026-07-24 |

---

## Limitations

Scripted proposer · single sim task · occlusion proxy v0.1 · HANDOVER stub · B2 rule proxy · offline CF (not closed-loop deployment).

---

## Links

- RQ v1.1: [`research_question.md`](research_question.md)
- Phase C v1.0 (D0): [`phase_c_proper_run_prereg_v1.0.md`](phase_c_proper_run_prereg_v1.0.md)
- Results D0: [`study1_proper/summary.json`](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1_proper/summary.json)
