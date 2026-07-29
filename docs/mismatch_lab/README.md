# Mismatch Lab

> **Public Lab** · external entry point for Research OS  
> **Status:** v0.1 spec · pilot design · not yet deployed

---

## What is Mismatch Lab?

**Mismatch Lab** is the public-facing layer for understanding robot behavior — starting with **Robot Diff**, not failure analysis.

| Layer | Role |
| --- | --- |
| **Research OS** | Evidence engine — prereg, protocols, Paper 001/002, negative controls |
| **Mismatch Lab** | Community & adoption — demos, benchmark, explorer, SDK pilot |
| **Company** (future) | Customer contracts, integrations, enterprise evaluation |

---

## One-line thesis

> **What changed between these two robot runs — and when does that change mean the model needs more than retuning?**

---

## Documents

| Doc | Purpose |
| --- | --- |
| [**v0.1 spec**](v0.1_spec.md) | Product spec · 4 cases · Diff UI · 4–6 week build plan |
| [**Diff Explorer (live demo)**](diff_explorer_v0.1.html) | Static interactive wireframe · GitHub Pages |
| [**API schema**](api_schema_v0.1.json) | `mismatch.diff` · `mismatch.analyze` · report JSON |
| [**Homepage v0.1**](homepage_v0.1.md) | Hero · CTAs · demo copy · pilot waitlist |
| [**Benchmark spec**](benchmark_spec_v0.1.md) | Adequacy benchmark · negative controls · scoring |
| [**Investor deck v0.1**](investor_deck_v0.1.md) | 6-slide outline · understanding-first framing |
| [**Company narrative v0.2**](company_narrative_v0.2.md) | Vision · wedge · roadmap by trust level |

---

## User-facing verbs (Twelve Labs pattern)

| User sees | Internal engine |
| --- | --- |
| **Replay** | Trajectory visualization |
| **Diff** | Aligned difference map |
| **Explain** | Timeline + salient moments |
| **Discover** | Interesting episodes in corpus |

Premium insight (not front-page): **Adequacy** — persistent mismatch that repair cannot absorb.

---

## Research link

Paper 002 (EXP-SURG-003) provides scientific evidence for the adequacy decision rule.  
See [Paper 002 hub](../paper002/README.md) · [confirmatory spec](../paper002/paper002_confirmatory_spec_v0.1.md).

---

*Updated 2026-07-29*
