# Stage 2 sandbox — Diffusion dreaming + agentic curriculum v0.1

> **Date:** 2026-07-22  
> **Status:** desk mock scaffold · parallel to Paper 1 RQ exploration  
> **Code:** `experiments/surgical_intelligence/exp_surg_002_dream_curriculum/` · `scripts/run_study2_dream_curriculum_mock.py`

---

## Why this exists

L0 vision (*Physical AI for the Non-Average World*) is still being concretized. ReSYNC future work points at:

1. **Diffusion dreaming** — replace Gaussian state sampling with generative models
2. **Agentic curriculum** — automate failure-eliciting scenario design

This sandbox is a **fun, low-risk probe**: can we generate *informative* failure scenarios (CONTINUE fails, REPLAN succeeds) better than Gaussian?

**Not Paper 1.** Paper 1 = measure profiles @ fixed **S**. This = generate **S** candidates.

---

## v0.1 scope (desk only)

| Component | v0.1 | Later |
| --- | --- | --- |
| **Dream space** | 3D params: `shift_m`, `onset_step`, `occlusion_gain` | Full scene layout · PCD · IVNTR |
| **Dreamers** | Gaussian · toy DDPM (numpy) | Classifier-guided diffusion |
| **Agent** | Rule-based curriculum from `exception_taxonomy.yaml` | LLM coding agent (FLARE-style) |
| **Env** | 001A 1D mock reach | Isaac ORBIT injection |
| **Metric** | % informative · mode separation · diversity | Predicate invention yield |

---

## Loop

```text
Agentic planner → curriculum goals (family + severity)
       ↓
Dreamer (Gaussian | Diffusion) → PerturbationSpec samples
       ↓
Mock reach → CONTINUE vs REPLAN @ S
       ↓
Filter: informative = CONTINUE fail ∧ REPLAN success
       ↓
Compare dreamers · log curriculum.json
```

---

## Week 1 playbook

1. **Run compare:** `--dreamer diffusion --compare` vs gaussian (same seeds)
2. **Inspect** `informative_rate` + param diversity in `summary.json`
3. **Agent hook:** paste `curriculum_prompt.txt` into Cursor / NotebookLM · JSON back → `--agent json-file`
4. **If diffusion wins on mock:** wire top specs into Isaac 001A runner (one cell)

---

## Honest boundary

- Does **not** implement ReSYNC dreaming over object poses
- Does **not** replace Phase C pre-reg
- **Does** give a concrete artifact for L1 RQ (“discovery pipeline vs measure-only”)

---

## Links

- Pre-reg Phase 1: [`study2_prereg_v0.1.md`](study2_prereg_v0.1.md)
- L1 RQ: [`l1_research_question_v0.1.md`](l1_research_question_v0.1.md)
- Taxonomy: [`exception_taxonomy.yaml`](../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/config/exception_taxonomy.yaml)
