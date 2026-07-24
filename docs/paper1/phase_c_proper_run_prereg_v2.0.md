# Paper 1 — Phase C proper-run pre-registration v2.0

> **Status:** **FROZEN · 2026-07-24** · GPU target **2026-07-25** (accelerated)  
> **Note:** 7-day pre-reg wait **waived** — design locked on CPU same day; disclose in Methods.  
> **v1.0 (D0 executed):** [`phase_c_proper_run_prereg_v1.0.md`](phase_c_proper_run_prereg_v1.0.md) · immutable  
> **RQ · method:** [`research_question.md`](research_question.md) v1.1 · [`method_spec_v1.0.md`](method_spec_v1.0.md)

---

## 0. Scope

**Publication-grade Paper 001** = v1.0 **D0** (done) + v2.0 **D1–D3** (this document).

| Block | Content | Status |
| --- | --- | --- |
| **D0** | 5-mode menu @ 6 cm + occlusion L1 | ✅ EXECUTED 2026-07-22 · do not re-run |
| **D1** | No-occlusion control @ 6 cm | scheduled post-freeze |
| **D2** | B2 UQ-inspired binary | scheduled post-freeze |
| **D3** | B3 situation rule | scheduled post-freeze |

---

## 1. Research questions (v1.1)

| ID | Hypothesis | Block |
| --- | --- | --- |
| **RQ-M** | REPLAN_d20 ≫ CONTINUE @ anchor | D0 ✅ |
| **RQ-P** | Occlusion changes CONTINUE/REPLAN vs shift-only @ 6 cm | D1 vs D0 |
| **RQ-B** | Multi-mode best ≥ B2 **or** B3 on success or burden | D0 + D2 + D3 |
| **RQ-C** | REOBSERVE/RESHAPE viable | D0 exploratory |

---

## 2. Primary endpoint

**Successful resolution:** shifted target ≤ **0.02 m** · no forbidden violation · not handover stub.

**D0 (reported):** REPLAN **19/20** vs CONTINUE **0/20**.

**v2.0 contrasts:** RQ-P (D1 directional) · RQ-B (D2/D3 vs D0 menu).

---

## 3. Shared anchor

Task IK-Rel · onset 20 · shift +0.06 m Y · replan delay 20 · n=20 seeds 0–19 · Isaac 4.1.

---

## 4. Blocks D1–D3

| Block | Runner | Branches |
| --- | --- | --- |
| **D1** | `orbit_reach_study1a_counterfactual.py` · no occlusion | 40 |
| **D2** | study1d `--baseline b2` | 20 |
| **D3** | study1d `--baseline b3` | 20 |

Launcher: `scripts/run_study1_proper_v2.sh` · `STUDY1_PROPER_BLOCK=d1|d2|d3`.

B2 constants: `VIS_THRESH=0.5` · `DIST_THRESH=0.15` m · check @ t0+10.  
B3: occluded_shift → REOBSERVE · shift_only → REPLAN_d20 · else CONTINUE.

---

## 5. Analysis (frozen)

**RQ-B primary metric (Option A):** success rate — D0 best-of-menu (REPLAN, REOBSERVE, RESHAPE) vs B2 and vs B3.

Secondary: HANDOVER burden · Wilson CI · violation rate · RQ-P descriptive D0 vs D1.

---

## 6. Success criteria

- [x] Pre-reg frozen 2026-07-24
- [x] 7-day wait **waived** · GPU **2026-07-25** (accelerated)
- [ ] D1–D3 · `branch_replay_ok` 100% · promote `results/study1_proper_v2/`

---

## 7. GPU budget

**80 branches** · ~0.5–0.75 pod-day · VESSL or RunPod.

---

## 8. Out of scope

D0 re-run · Study 002 · delay grid · learned UQ · clinical.

---

## Version

| Version | Date | Note |
| --- | --- | --- |
| v2.0-draft | 2026-07-24 | Initial draft |
| **v2.0** | **2026-07-24** | Frozen · GPU accelerated **2026-07-25** · 7d wait waived |
