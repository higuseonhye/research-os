# Naming guide — research program

> **Updated:** 2026-07-28 · Independent personal research

---

## Frozen (do not renumber)

| Label | Experiment ID | Role | Status |
| --- | --- | --- | --- |
| **Paper 001** | **EXP-SURG-001** | Measure recoverability profiles @ fixed **S** | ✅ Tier C complete · working paper live |
| **Study 002** | **EXP-SURG-002** | Dream curriculum / informative-**S** generation probe | ✅ Phase 1–2 executed · **closed** (appendix only for Paper 001) |

**Do not call Paper 001 “Study 001”.** Config paths use legacy `study1_*`; public brand = **Paper 001 / EXP-SURG-001**.

---

## Active (now)

| Label | Experiment ID(s) | Role | Status |
| --- | --- | --- | --- |
| **Paper 002** | **EXP-SURG-003** (+ sub-arms) | Recoverable agentic loop: mismatch · generative **S** · response agent/RL | 🔄 design · pre-reg next |
| **Program alias** | Study 003 (optional) | Same as Paper 002 — use **Paper 002** in outreach |

---

## Sub-arms (Paper 002)

| Arm | ID | Interest |
| --- | --- | --- |
| Mismatch trigger | **EXP-WM-MISMATCH-001** | WM / residual signal · agentic L1 |
| Generative curriculum | **EXP-SURG-003 · dream** | Diffusion + **LLM agent** @ Isaac (Study 002 lesson: occlusion contract) |
| Response selection | **EXP-SURG-003 · policy** | Agent / **RL** over Paper 001 menu |

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

> Paper 001 measures @ **S** · Study 002 probed generation (closed) · **Paper 002** closes the loop with mismatch detection, LLM/diffusion curriculum, and agent/RL response selection on the same ruler.
