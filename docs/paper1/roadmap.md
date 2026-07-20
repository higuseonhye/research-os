# Paper 1 — roadmap (post-smoke)

> **Updated:** 2026-07-22 · Phase A complete · Phase B/C = planning (no GPU)

---

## Where we are

```text
Phase A  Smoke atlas (001A–C + D0 + D1)     ✅ DONE
Phase B  Desk review → decisions             ✅ DONE
Phase C  Pre-reg v1.0 (frozen · not run)     ✅ PLANNED
         ↓
Stage 2  Lit + industry + method deep dive   ← YOU ARE HERE (next work block)
         ↓
Stage 3  Execute Phase C proper run (GPU)
         ↓
Stage 4  Paper 1 draft · lab talk evidence
```

---

## Stage 2 — Prior work & method (before main GPU)

**Goal:** Refine RQ, differentiation, and baselines so Phase C claims are defensible.

| Work block | Deliverable | Location |
| --- | --- | --- |
| **Lit sprint v2** | Update kill matrix · 5–10 new papers · industry scan (VLA, surgical UQ, MEDiC, VAP-TAMP) | private `prior_art_*` · Obsidian [[03_Research/Lit-Sprint-Recoverability-2026-07]] |
| **RQ refinement** | v1.0 lock + sub-RQs + claim tiers | [`research_question.md`](research_question.md) |
| **Method doc** | CF protocol · endpoints · baseline specs | private `research_method_and_differentiation_v1.md` |
| **Industry trends** | What top labs optimize vs our eval wedge | private working note · optional blog slide |
| **PI sign-off** | Phase C go/no-go on baselines + n | meeting notes |

**Exit criterion:** Phase C pre-reg v1.0 signed · no open blocker on proxy/baseline semantics.

---

## Stage 3 — Main experiment (Phase C execution)

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
| C results | `results/study1_proper/` (future) | analysis notebook |
