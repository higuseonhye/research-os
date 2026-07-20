# EXP-SURG-001D — Phase gate (smoke atlas vs proper run)

> **Status:** active · D0 Isaac done · **D1 = smoke atlas completion**

---

## Phase A — Smoke atlas (current)

| Step | ID | Modes | Seeds | Status |
| --- | --- | --- | --- | --- |
| Shift-only baseline | 001A–C | continue/replan | 0–4 | ✅ Isaac |
| Occlusion 3-mode | **D0** | CONTINUE, REPLAN, REOBSERVE | 0–4 | ✅ Isaac |
| Occlusion 5-mode | **D1** | + RESHAPE, HANDOVER | 0–4 | ⏭ RunPod |

**Purpose:** Pipeline + proxy + profile **direction** — not Paper 1 final n.

**Honest label:** smoke / scaffold · n=5 · scripted IK-Rel · gain_scale occlusion v0.1.

---

## Phase B — Whole review (after D1)

Desk checklist before proper run pre-reg v1.0:

1. Smoke summary table (001A–C + D0 + D1)
2. What we know / don't know (timing, REOBSERVE seed 0, RESHAPE vs REPLAN)
3. Baseline list (Surgical UQ binary, B-VAP rule)
4. Proxy upgrade (v0.2 geometry?) vs keep gain_scale
5. n and power target for proper run
6. GPU budget estimate

---

## Phase C — Proper experiment (later)

- Pre-reg **v1.0** frozen before GPU
- n↑ · optional baseline implementation · promote to `results/study1d_proper/`
- Claims for lab/paper from Phase C only (or clearly labeled “smoke” vs “confirmatory”)

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
