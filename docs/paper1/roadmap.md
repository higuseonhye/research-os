# Paper 1 — roadmap (post-smoke)

> **Updated:** 2026-07-23 · Phase A complete · Phase C executed (Tier C)

---

## Where we are

```text
Phase A  Smoke atlas (001A–C + D0 + D1)     ✅ DONE
Phase B  Desk review → decisions             ✅ DONE
Phase C  Pre-reg v1.0 + proper n=20          ✅ DONE (2026-07-22)
Lit v2   Positioning + baseline spec         ✅ DONE
         ↓
Stage 5  Paper 1 draft · lab talk evidence   ← current
         ↓
Stage 2+ Learned selector · timing regret    (not Paper 1)
```

---

## Stage 2 — Prior work & method ✅ (Lit sprint v2)

| Work block | Status | Location |
| --- | --- | --- |
| **Lit sprint v2** | ✅ | [`lit_positioning_v1.md`](lit_positioning_v1.md) |
| **Research framing v1** | ✅ | [`research_framing_v1.md`](research_framing_v1.md) |
| **Evaluation landscape** | ✅ v0.2 | [`evaluation_landscape_2024_2026_v0.2.md`](evaluation_landscape_2024_2026_v0.2.md) |
| **RQ refinement** | ✅ v1.0 | [`research_question.md`](research_question.md) |
| **Phase C proper** | ✅ | [`results/study1_proper/`](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1_proper/) |

---

## Stage 3–4 — Phase C ✅ (executed)

1. Pre-reg frozen · [`phase_c_proper_run_prereg_v1.0.md`](phase_c_proper_run_prereg_v1.0.md)
2. RunPod primary cell n=20 × 5 modes
3. Promoted → `results/study1_proper/summary.json`
4. [`status.md`](status.md) updated · Tier **C**

**Primary result:** REPLAN_d20 **19/20** vs CONTINUE **0/20** @ 6 cm + occlusion.

---

## Stage 5 — Paper / lab (6mo scope)

> **Next:** RQ v1.1 + pre-reg v2.0 (confirmatory blocks D1–D3) before further GPU · see private program doc

| Asset | Source |
| --- | --- |
| Fig 4 / 5 | 001A/B smoke + Phase C narrative |
| Table 1 | Mode profiles @ 6 cm occlusion (proper n) |
| Method | Same-state CF protocol |
| Limitations | Scripted proposer · proxy occlusion · sim-only |

**Stage 2+ (not Paper 1):** learned selector · timing regret paper · sim2real.

---

## Repo map (public only)

| Phase | Location in research-os |
| --- | --- |
| A smoke | `results/study1*_isaac/` · reports |
| B review | `docs/paper1/phase_b_smoke_review.md` |
| C design | `docs/paper1/phase_c_proper_run_prereg_v1.0.md` |
| C results | `results/study1_proper/` |
| Lit v2 | `docs/paper1/lit_positioning_v1.md` |
