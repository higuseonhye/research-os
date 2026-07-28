# Naming guide — research program

> **Updated:** 2026-07-28 · Independent personal research

---

## Frozen (do not renumber)

| Label | Experiment ID | Role | Status |
| --- | --- | --- | --- |
| **Paper 001** | **EXP-SURG-001** | Measure recoverability profiles @ fixed **S** | ✅ Tier C complete · working paper live |
| **Study 002** | **EXP-SURG-002** | Dream curriculum **pilot** (Tier B) | ✅ Phase 1–2 · **archived** · feeds Paper 002 |

**Do not call Paper 001 “Study 001”.** Config paths use legacy `study1_*`; public brand = **Paper 001 / EXP-SURG-001**.

---

## Active (now)

| Label | Experiment ID | Role | Status |
| --- | --- | --- | --- |
| **Paper 002** | **EXP-SURG-003** | **Mock-to-physics validation** for informative mismatch selection | 🔄 pre-reg v0.3 frozen |
| **Paper 003** | **EXP-WM-MISMATCH-001** (+ policy) | Latent mismatch · response agent/RL | design · after Paper 002 |

---

## Paper 002 scope (confirmatory · not full loop)

| Component | In Paper 002 | Deferred |
| --- | --- | --- |
| Gaussian + diffusion dreamers | ✅ | — |
| Rule + **LLM** planner @ Isaac | ✅ | — |
| Mock→Isaac rank @ n=40 | ✅ | — |
| Latent mismatch trigger | — | Paper 003 |
| RL response selection | — | Paper 003 |

Paper 001 remains the **eval ruler** for all arms.

---

## Disambiguation

| Term | Means | Does **not** mean |
| --- | --- | --- |
| **`docs/stage2/`** | Study 002 public docs | Paper 002 · program Stage 2 |
| **Stage 2 (lit sprint)** | Paper 001 prior-work phase (done) | Study 002 |
| **Paper 2 (timing)** | Deferred timing-regret paper | Paper 002 |
| **L1/L2/L3 (Agentic WM)** | Predictor / simulator / evolver levels | Study phase numbers |

---

## One-line program

> Paper 001 measures @ **S** · **Paper 002** validates mock→Isaac selection · **Paper 003** mismatch + response loop.
