# Paper 002 — Related work v0.1

> **Positioning doc** · cite in Introduction §4 · not a lit review draft  
> **Core wedge:** proxy validation before physics · not policy-training curriculum

---

## 1. Automatic curriculum learning

Curriculum learning organizes training examples or tasks so the learner encounters a useful progression. In RL, the most useful task depends on the agent's current capabilities — static difficulty is insufficient.

**Prioritized Level Replay (PLR)** assigns priority to environment levels by estimated future learning potential. Not all valid levels are equally informative for the current agent.

**Paper 002 difference:** adopts the distinction between *available* and *useful* candidates, but does **not** optimize policy updates or replay frequency. It asks whether a low-cost evaluator predicts a **physics-derived informativeness label** before expensive execution.

Self-paced and prioritized methods emphasize intermediate difficulty (not always solved / always failed). Paper 002 defines informativeness differently: a candidate is informative only when it produces a prespecified **difference between paired response modes from the same state** — not intermediate success probability.

---

## 2. Unsupervised environment design

**POET** jointly generates environmental challenges and optimizes agents, enabling open-ended skill discovery across a population of tasks.

**PAIRED / minimax-regret** formalize environment generation adversarially — environments are valuable when they expose a performance gap between agents ("just-right" challenges). **ACCEL** edits previously high-regret levels near the capability frontier.

**Paper 002 difference:** related because it searches over perturbation specifications, but narrower:

- generator is **not** trained adversarially
- response policies are **frozen**
- no policy update from selected candidates
- objective = **proxy validation**, not robust agent training

Not an unsupervised environment-design algorithm — a **validation study for an environment-selection proxy**.

---

## 3. Generative models for environment design

Diffusion-based adversarial environment design conditions generation on agent regret to produce diverse challenging levels. Expressive generation does not guarantee that a cheap score remains valid after transfer to higher-fidelity simulation.

**Paper 002 difference:** focuses on the **missing validation layer**. Generator may be rule-based or LLM-based; the central object is **mock ranking → Isaac informativeness**.

---

## 4. LLM-generated robotic tasks and curricula

**GenSim** uses LLMs to generate executable simulation tasks and demonstrations; outcomes are task generation, policy learning, and generalization.

**CurricuLLM** decomposes complex skills into subtasks, translates to code, and evaluates policies trained on the resulting curriculum.

**Paper 002 difference:** LLM proposes parameters within a **frozen perturbation schema**. It cannot modify evaluator, simulator mapping, response policies, or analysis. The LLM is a **constrained candidate proposer**, not an autonomous experiment designer. Primary outcome is **physics-level experimental value prediction**, not downstream training gain.

> GenSim and CurricuLLM ask whether LLM-generated tasks improve learning. Paper 002 asks whether a cheap proxy predicts **physics-level counterfactual value** of generated mismatches.

---

## 5. Simulation validation and fidelity transfer

Sim-to-real work studies whether policies or dynamics transfer across domains. Paper 002 studies whether the **ordering of candidate experiments** transfers.

The mock evaluator need not reproduce exact Isaac trajectories — it is useful when it preserves enough **relative information** to prioritize candidates. Rank association and top-vs-bottom enrichment matter more than absolute agreement.

---

## 6. Counterfactual evaluation and recoverability

Robotic robustness metrics (task success under perturbation, recovery, replanning) can be confounded when trajectories arrive at different pre-mismatch states.

Paper 001 holds the pre-mismatch state fixed and evaluates multiple responses after the same mismatch. Paper 002 validates **upstream selection** of mismatches that reveal those response differences — it does not claim to solve recovery.

---

## Positioning table

| Research line | Candidate source | Selection signal | Main outcome | vs Paper 002 |
| --- | --- | --- | --- | --- |
| POET | Evolutionary mutation | Minimal + transfer | Open-ended skill discovery | No same-state proxy validation |
| PAIRED | Learned adversarial gen. | Relative regret | Robust agent training | Generator + agent co-trained |
| PLR | Procedural levels | Learning potential | Sample efficiency | Prioritizes training, not CF experiments |
| ACCEL | Frontier level edits | Regret | Curriculum complexity | No mock-to-physics contract |
| GenSim | LLM simulation code | Task validity + training | Policy generalization | Evaluates via training |
| CurricuLLM | LLM subtasks + code | Rollout curriculum eval | Complex-skill learning | Curriculum trains policy |
| **Paper 002** | Rule or LLM planner | **Frozen continuous mock score** | **Isaac CF informativeness** | **Validates ranking before physics** |

---

## References (anchor papers)

| ID | Work | URL |
| --- | --- | --- |
| POET | Paired Open-Ended Trailblazer | [arXiv:1901.01753](https://arxiv.org/abs/1901.01753) |
| GenSim | LLM robotic simulation tasks | [ICLR 2024](https://proceedings.iclr.cc/paper_files/paper/2024/hash/143ea4a156ef64f32d4d905206cf32e1-Abstract-Conference.html) |
| Paper 001 | Same-state recoverability @ **S** | [research-os paper1](../paper1/status.md) |

CurricuLLM · PLR · ACCEL · PAIRED — cite from manuscript bib at submission time.
