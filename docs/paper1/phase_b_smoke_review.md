# Paper 1 — Phase B smoke review (desk · complete)

> **Date:** 2026-07-22 · **Input:** Phase A Isaac smokes (001A–C + 001D D0/D1)  
> **Output:** decisions for [`phase_c_proper_run_prereg_v1.0.md`](phase_c_proper_run_prereg_v1.0.md)  
> **Label:** smoke / scaffold only — not confirmatory evidence

---

## 1. Smoke summary table

| Study | Perturbation | Modes / axis | n | Key result (success) | Role |
| --- | --- | --- | ---: | --- | --- |
| **001A** | Target shift **3 cm** | CONTINUE vs REPLAN | 5 ep | CONTINUE **0/5** · REPLAN **4/5** (1 unsafe) | Mode separation @ mild shift |
| **001B** | Shift **3 cm** | REPLAN delay 0–20 | 3 ep | REPLAN **3/3** all delays · flat band | Timing insensitive @ 3 cm |
| **001C** | Shift 1–9 cm × delay 0–60 | REPLAN grid + CONTINUE | 5/cell | Mostly **0.8–1.0** · no monotonic cliff | Severity×delay surface mostly flat |
| **001D D0** | Shift **6 cm** + occlusion L1 | CONTINUE · REPLAN · REOBSERVE | 5 | REPLAN **5/5** · CONTINUE **0/5** · REOBSERVE **4/5** | Occlusion anchor @ 6 cm |
| **001D D1** | Same + 5-mode | + RESHAPE · HANDOVER | 5 | REPLAN **5/5** · RESHAPE **4/5** · REOBSERVE **4/5** · HANDOVER **0/5** | Multi-class menu smoke |

**Cross-cutting:** scripted IK-Rel · same-state CF fork · tol 2 cm · n=5 smoke scale.

---

## 2. What we know (smoke)

1. **Mode dominates at fixed S** — CONTINUE ≪ REPLAN repeats across shift-only (001A) and occlusion (D0/D1).
2. **Timing cliff absent @ tested grid** — 001B flat @ 3 cm; 001C no monotonic delay sensitivity; 6 cm @ d20 remains viable (001C recommend cell).
3. **Occlusion does not collapse REPLAN** — D0/D1 REPLAN **5/5** @ 6 cm + gain_scale proxy.
4. **REOBSERVE viable but seed-sensitive** — **4/5** both D0 and D1; seed 0 outlier (~0.80 m) matches 001A ep0 pattern.
5. **RESHAPE competitive with REPLAN** — **4/5** (seed 2 timeout); environment-class path is **plausible**, not proven at scale.
6. **HANDOVER stub fails by design** — **0/5** · `handover_proxy` terminal · not a recovery endpoint in v0.1.
7. **CF scaffold works** — branch_replay_ok True on all promoted runs · pipeline RunPod-reproducible.

---

## 3. What we do not know (honest gaps)

| Gap | Why it matters | Phase C action |
| --- | --- | --- |
| **Statistical power** | n=5 · seed outliers drive rates | n↑ pre-registered |
| **Timing headline** | Flat bands may be true or under-powered | Keep delay **fixed @ d20** for P1; optional extended delay arm |
| **Occlusion realism** | gain_scale v0.1 ≠ geometric occlusion | Decide v0.1 vs v0.2 before GPU |
| **RESHAPE vs REPLAN mechanism** | One seed failure · no path metrics | Report path length · violation · n↑ |
| **HANDOVER semantics** | Stub only | Separate **collaboration log** metric or defer to Stage 2 |
| **Baselines** | Surgical UQ · B-VAP not implemented | Pre-reg optional baseline arm |
| **Learned selector** | Not tested | **Out of Phase C** — Stage 2 |

---

## 4. Open questions → Phase C decisions

| # | Question | Phase B decision |
| ---: | --- | --- |
| 1 | Paper 1 headline axis? | **Intervention mode** under **6 cm + occlusion** — not golden-time |
| 2 | Keep gain_scale occlusion? | **Yes for Phase C v1.0** · document as proxy · v0.2 geometry = optional arm |
| 3 | Include HANDOVER in success table? | **Log only** · primary endpoint = policy/info/environment modes that target resolution |
| 4 | Primary comparison cell? | **6 cm · delay 20 · occlusion L1** (001C recommend · D0/D1 validated) |
| 5 | Baselines in first proper run? | **Tier 1:** CONTINUE + REPLAN only profile · **Tier 2 (stretch):** binary UQ-handover rule |
| 6 | Claim label? | Smoke = **direction** · Phase C = **confirmatory** only after pre-reg freeze |

---

## 5. Hypothesis status (from method doc)

| ID | Hypothesis | Smoke verdict | Proper run needed? |
| --- | --- | --- | --- |
| H1 | Mode matters @ fixed S | **Supported (direction)** | n↑ to confirm rates |
| H2 | Delay matters | **Weak / flat @ 3 cm** | Not P1 headline; optional arm |
| H3 | Occlusion ≠ shift-only | **Partial** — REPLAN still 5/5; profile shape differs (REOBSERVE role) | Compare D1 vs 001C @ 6 cm no-occlusion cell |
| H4 | RESHAPE adds path | **Plausible 4/5** | n↑ + ablation |
| H5 | Beats binary baseline | **Not tested** | Implement in Phase C stretch |
| H6 | Not replay artifact | **Not tested** | n≥20 · second seed block |

---

## 6. Phase B deliverable checklist

- [x] Smoke summary table (001A–C + D0 + D1)
- [x] Know / don't know documented
- [x] Baseline list for Phase C
- [x] Proxy decision (gain_scale v0.1 for v1.0)
- [x] n / power target drafted → see Phase C pre-reg
- [x] GPU budget estimate → see Phase C pre-reg

**Phase B status:** complete (desk). **Next:** freeze Phase C pre-reg → lit deep dive → execute proper run.

---

## Links

- Phase C pre-reg: [`phase_c_proper_run_prereg_v1.0.md`](phase_c_proper_run_prereg_v1.0.md)
- RQ v1.0: [`research_question.md`](research_question.md)
- Roadmap: [`roadmap.md`](roadmap.md)
- Evidence: [`status.md`](status.md)
