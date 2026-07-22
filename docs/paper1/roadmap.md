# Paper 1 — roadmap (post-smoke)

> **Updated:** 2026-07-22 · Phase A complete · Phase B/C = planning (no GPU)

---

## Where we are

```text
Phase A  Smoke atlas (001A–C + D0 + D1)     ✅ DONE
Phase B  Desk review → decisions             ✅ DONE
Phase C  Pre-reg v1.0 (frozen · not run)     ✅ PLANNED
Lit v2   Positioning + baseline spec         ✅ DONE
         ↓
Stage 2b PDF deep read (Batch B + A)       ← private queue
         ↓
Stage 3  Sign-off · runner proper n=20
         ↓
Stage 4  Execute Phase C proper run (GPU)
         ↓
Stage 5  Paper 1 draft · lab talk evidence
```

---

## Stage 2 — Prior work & method ✅ (Lit sprint v2)

| Work block | Status | Location |
| --- | --- | --- |
| **Lit sprint v2** | ✅ | [`lit_positioning_v1.md`](lit_positioning_v1.md) · private `lit_sprint_v2_smoke_synthesis.md` |
| **Research framing v1** | ✅ | [`research_framing_v1.md`](research_framing_v1.md) |
| **Evaluation landscape** | ✅ v0.2 | [`evaluation_landscape_2024_2026_v0.2.md`](evaluation_landscape_2024_2026_v0.2.md) |
| **RQ refinement** | ✅ v1.0 | [`research_question.md`](research_question.md) |
| **Baseline spec** | ✅ draft | private `baseline_spec_phase_c_v1.0.md` |
| **PI sign-off** | ⏭ | B2 baseline in v1.0 GPU? · GO for n=20 run |

## Stage 2b — PDF deep read

| Work block | Status | Location |
| --- | --- | --- |
| **Reading queue** | 🔄 | private [`paper_reading_day1`](https://github.com/higuseonhye/builder-os-private/blob/master/working/research/paper_reading_day1_2026-07-22.md) · Obsidian vault |
| **Batch A (6 PDFs)** | ⏭ | Surgical UQ · SuFIA · Guardian · FailSafe · RoboFAC · ResponsibleRobotBench |
| **Batch B (4 PDFs)** | ⏭ | ReSYNC · IVNTR · RecoveryChaining · VAP-TAMP |

**Exit criterion:** Batch A capture notes · kill matrix updated · PI baseline decision.

---

## Stage 3 — Prep (before GPU)

1. PI decision: include **B2 UQ-inspired baseline** in first proper run? (+20 branches)
2. Implement `proper` block in yaml + runner (n=20 seeds)
3. Pre-reg hash ≥7 days on manifest (or waiver)

---

## Stage 4 — Main experiment (Phase C execution)

1. `git pull` · verify pre-reg hash on manifest
2. RunPod: primary cell n=20 × 5 modes
3. Optional: no-occlusion control arm
4. Promote → `results/study1_proper/`
5. Update [`status.md`](status.md) with **confirmatory** label

---

## Stage 4 — Paper / lab (6mo scope)

| Asset | Source |
| --- | --- |
| Fig 4 / 5 | 001A/B (smoke) + optional proper-run overlay |
| Table 1 | Mode profiles @ 6 cm occlusion (proper n) |
| Method | Same-state CF protocol |
| Limitations | Scripted proposer · proxy occlusion · sim-only |

**Stage 2+ (not Paper 1):** learned selector · timing regret paper · sim2real.

---

## Repo map

| Phase | Public (research-os) | Private (builder-os-private) |
| --- | --- | --- |
| A | `results/study1*_isaac/` · reports | pre-reg history |
| B | `docs/paper1/phase_b_smoke_review.md` | extended KR notes |
| C plan | `docs/paper1/phase_c_proper_run_prereg_v1.0.md` | GPU checklist · baseline impl |
| Lit v2 | `docs/paper1/lit_positioning_v1.md` | `lit_sprint_v2_smoke_synthesis.md` |
| C results | `results/study1_proper/` (future) | analysis notebook |
