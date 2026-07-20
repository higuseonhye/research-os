# EXP-SURG-001D — Phase gate (smoke atlas vs proper run)

> **Status:** active · D0 + **D1 Isaac done** · Phase A smoke atlas **complete**

---

## Phase A — Smoke atlas (current)

| Step | ID | Modes | Seeds | Status |
| --- | --- | --- | --- | --- |
| Shift-only baseline | 001A–C | continue/replan | 0–4 | ✅ Isaac |
| Occlusion 3-mode | **D0** | CONTINUE, REPLAN, REOBSERVE | 0–4 | ✅ Isaac |
| Occlusion 5-mode | **D1** | + RESHAPE, HANDOVER | 0–4 | ✅ Isaac |

**Purpose:** Pipeline + proxy + profile **direction** — not Paper 1 final n.

**Honest label:** smoke / scaffold · n=5 · scripted IK-Rel · gain_scale occlusion v0.1.

---

## Phase B — Whole review (complete · desk)

Deliverable: [`docs/paper1/phase_b_smoke_review.md`](../../../../docs/paper1/phase_b_smoke_review.md)

---

## Phase C — Proper experiment (pre-reg frozen · not run)

Pre-reg v1.0: [`docs/paper1/phase_c_proper_run_prereg_v1.0.md`](../../../../docs/paper1/phase_c_proper_run_prereg_v1.0.md)

- Execute **after** lit + method deep dive + sign-off
- n=20 · promote to `results/study1_proper/`
- Claims labeled **confirmatory** only from Phase C results

---

## Roadmap

[`docs/paper1/roadmap.md`](../../../../docs/paper1/roadmap.md)

---

## D1 RunPod (Phase A finish)

```bash
cd /workspace/research-os && git pull origin master
tmux new -s study1d_d1

# 1) Gate: 1 seed · 5 modes
STUDY1D_FULL=1 STUDY1D_SEEDS=0 bash scripts/run_study1d_runpod.sh

# 2) Atlas: n=5 · 5 modes (25 branches)
STUDY1D_FULL=1 bash scripts/run_study1d_runpod.sh
```

Merge only (if Isaac done):

```bash
/isaac-sim/python.sh scripts/run_study1d.py --merge --full
```

Promote: aggregate → `results/study1d_isaac/` (local commit, D0 pattern).

---

## D0 Isaac (locked reference)

REPLAN **5/5** · CONTINUE **0/5** · REOBSERVE **4/5** @ 6 cm + occlusion L1.
