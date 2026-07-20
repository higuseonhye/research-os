# Paper 1 — Phase C proper-run pre-registration v1.0

> **Status:** **FROZEN DESIGN · NOT EXECUTED**  
> **Date frozen:** 2026-07-22 · **Execute only after:** lit review sprint + method lock sign-off  
> **Promote path:** `results/study1_proper/` (confirmatory label)

---

## 0. Scope boundary

This document is **planning only**. No GPU run is authorized until:

1. Phase B review accepted (see [`phase_b_smoke_review.md`](phase_b_smoke_review.md))
2. Prior-work / industry trend review updated (private working notes)
3. PI/lab sign-off on claim tier (smoke vs confirmatory)

**Smoke atlas (Phase A) must not be cited as confirmatory n.**

---

## 1. Primary endpoint

**Successful resolution** — terminal distance to **shifted** target ≤ **0.02 m**, no forbidden violation, within max steps.

**Primary contrast (pre-registered):**

> At fixed mismatch onset **S** (6 cm shift + occlusion L1), recoverability rate of **REPLAN_d20** vs **CONTINUE**.

**Secondary contrasts:**

- REOBSERVE vs CONTINUE
- RESHAPE vs REPLAN_d20 (non-inferiority direction · exploratory)
- Profile separation across all non-stub modes

---

## 2. Design (frozen v1.0)

| Parameter | Value | Rationale (Phase B) |
| --- | --- | --- |
| Task | `Isaac-Reach-Dual-STAR-IK-Rel-Play-v0` | Locked Stage 1 testbed |
| Proposer | Scripted 6D IK-Rel · body 13 | Same as smoke |
| Shift | **+0.06 m Y** @ step 20 | 001C recommend · D0/D1 anchor |
| REPLAN delay | **20 steps** | D0/D1 locked |
| Occlusion | Level 1 · `visibility_fraction=0.35` · **gain_scale_flag v0.1** | Smoke-validated proxy |
| Modes | CONTINUE · REPLAN_d20 · REOBSERVE · RESHAPE · HANDOVER(log) | D1 menu |
| Seeds | **0–19** (n=20 per mode) | Power vs smoke n=5 |
| Branches | **100** (20 × 5 modes) | Single primary cell |
| Horizon | max_steps 160 · episode_length_s 20 | Smoke default |

**Optional extension arm (not required for v1.0 pass):**

- No-occlusion control @ 6 cm (link to 001C cell) — **20 seeds × 2 modes** (CONTINUE, REPLAN_d20)
- Occlusion proxy v0.2 (geometry) — **separate pre-reg bump v1.1**

---

## 3. Baselines (tiered)

| Tier | Baseline | Implementation | Primary metric |
| --- | --- | --- | --- |
| **0** | CONTINUE | Built-in | Success rate @ S |
| **1** | REPLAN_d20 | Built-in | Success rate @ S |
| **2 (stretch)** | Surgical UQ binary | Fail detector → handover/continue rule | Profile AUC vs multi-mode |
| **3 (stretch)** | B-VAP-style rule | Situation → fixed mode map | Same |

**v1.0 minimum:** Tier 0–1 with n=20. Tier 2–3 may slip to v1.1 if implementation not ready — **do not delay mode profile run**.

---

## 4. HANDOVER handling

- **v0.1 stub remains** for collaboration-class logging.
- **Excluded from primary success endpoint.**
- Report: `terminal_category=handover_proxy` rate · time-to-handover · visibility state.
- Real handover semantics → **Stage 2** or pre-reg v1.1.

---

## 5. Analysis plan (pre-registered)

1. Per-mode success rate + Wilson 95% CI (n=20).
2. Mean final distance · completion steps · forbidden violation rate.
3. **Profile table** \( \hat{R}_a(s,t) \) for fixed anchor cell.
4. Seed sensitivity: flag outliers (ep0 pattern) · report with/without sensitivity.
5. **No p-hacking across modes** — primary hypothesis = REPLAN > CONTINUE; others exploratory (FDR noted in text).

---

## 6. Success criteria (confirmatory label)

Phase C run earns **confirmatory** label if:

- [ ] Pre-reg frozen ≥7 days before first GPU branch
- [ ] n=20 per mode completed for primary cell
- [ ] branch_replay_ok = 100%
- [ ] REPLAN success ≥ CONTINUE + **≥15 pp** (directional · not sole publication claim)
- [ ] Results promoted to `results/study1_proper/` with manifest + git commit

---

## 7. GPU budget estimate

| Phase | Branches | Est. time/branch | Total GPU |
| --- | ---: | --- | --- |
| Primary cell (100) | 100 | ~2–3 min | **~3–5 h** |
| Optional no-occlusion (40) | 40 | ~2–3 min | **~1.5 h** |
| Bootstrap (cold pod) | — | 15–25 min | once |
| Merge + figures | — | 15 min | CPU |

**RunPod RTX 4090 · Isaac 4.1.0:** budget **~1 pod-day** including bootstrap + one retry buffer.

---

## 8. Artifacts (on completion)

```
results/study1_proper/
  isaac_aggregate.json
  summary.json
  tables/aggregate_by_mode.csv
  run_manifest.json   # commit · pre-reg hash · timestamp
study1_proper_report.md
```

---

## 9. Explicitly out of scope (Phase C v1.0)

- Learned recoverability selector / meta-policy training
- Clinical OR validation
- Full delay sweep (001C already characterized)
- Beat SOTA VLA on task success
- Golden-time claims in seconds

---

## 10. Version history

| Version | Date | Change |
| --- | --- | --- |
| v1.0 | 2026-07-22 | Initial freeze from Phase B · post D1 smoke |

**Bump to v1.1 only via:** new PR + dated changelog · never retro-edit after GPU start.
