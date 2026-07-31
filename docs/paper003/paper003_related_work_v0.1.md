# Paper 003 — Related work v0.1 (missing relation & capability expansion)

> **Positioning doc** · cite in Introduction · complements [paper003_lit_positioning_v0.1.md](paper003_lit_positioning_v0.1.md) (execution-horizon entry framing — a different, narrower comparison)
> **Core wedge:** failure-triggered **relational** expansion, validated by **capability threshold crossing** — not "learn a relational world model" alone, and not "mean error went down" alone.

---

## Novelty (defensible)

**Avoid:** "we add a graph/relational module to a world model" (not novel by itself — see §1) · "relational reasoning improves generalization" (not novel by itself — see §2) · "capability emerges from scale" (different mechanism, different literature — see §3).

**Use:**

> **Failure-triggered relational-adequacy testing, validated by achievable-task-space growth:** determining when parameter repair and mode-level expansion are both insufficient because the model class is missing a *relation* between entities, and testing whether the resulting expansion converts previously unachievable task variants into achievable ones — not only whether it lowers prediction error.

**Scope defense:**

> Paper 003 does not perform open-ended relational/causal discovery. It reuses Paper 002's restricted setting: a **prepared** relation-module operator, invoked only after a **prespecified gate** (residual survives parameter repair *and* mode expansion, and correlates with a second entity's state). The novel measurement is **capability threshold crossing**, not the expansion mechanism itself.

---

## 1. Relational / graph-based world models (how to represent relations — not our contribution)

These lines establish **how** to build relational structure into a dynamics model. Paper 003 does not compete on this axis — it assumes a prepared relation-module operator exists (same posture as Paper 002 toward its dynamics expert).

| Work | Focus | Relation to Paper 003 |
| --- | --- | --- |
| [Neural Relational Inference (NRI)](https://arxiv.org/abs/1802.04687) — Kipf et al. | Unsupervised discovery of an interaction graph + dynamics, jointly, from observational data | Learns relations **from scratch across many examples**; Paper 003 tests whether **one failure-triggered switch** to a prepared relation module beats parameter/mode repair — not open discovery |
| Interaction Networks / Neural Physics Engines / [Graph Networks as Learnable Physics Engines](https://www.science.org/doi/10.1126/scirobotics.adt1497) (survey coverage) | Graph-based reasoning over objects and pairwise relations for physical prediction | Foundational relational-dynamics architecture; **assumes the graph is relevant from step 1**, not "detected as missing after failure" |
| [Factored World Models for Zero-Shot Generalization in Robotic Manipulation](https://arxiv.org/pdf/2202.05333) | Decomposes scenes into objects, models pairwise interactions, zero-shot generalizes to novel object combinations | Closest prior on "relations → generalization to new task configurations"; does not test a **repair-vs-expansion gate**, and measures generalization accuracy broadly, not a preregistered 0%→achievable threshold |
| [TriRelVLA](https://arxiv.org/pdf/2605.05714) | Triadic (object-hand-task) relational structure for compositional generalization across unseen scenes/objects/tasks | Relational structure is designed in from the start for a VLA policy; no failure-triggered adequacy test |
| FOCUS-style object-centric world models (see [WM robot-learning survey](https://arxiv.org/abs/2605.00080)) | Explicit object representations for efficient exploration of object dynamics | Object-centricity as a design choice, not a response to detected model-class inadequacy |

**Gap these leave open:** none of these ask *when* a relational representation becomes necessary — they either assume it from the start or learn it from broad multi-scenario data. Paper 003's question is narrower and prior-conditioned: **given a system that already believes entities are independent, and has already tried parameter repair and mode expansion, is the next failure signature specifically diagnostic of a missing relation?**

---

## 2. Compositional / relational generalization (measuring success — partial overlap)

| Work | What it measures | vs Paper 003 |
| --- | --- | --- |
| Compositional generalization surveys (e.g. [survey](https://arxiv.org/pdf/2302.01067)) | Whether a system generalizes to novel combinations of known parts | Closest **framing** neighbor to "achievable task space," but typically reported as aggregate accuracy on a held-out combination set, not as **threshold crossing** on individually preregistered variants |
| [Relational Structural Causal Models](https://arxiv.org/pdf/2606.14892) | Causal structure over relational (multi-entity) data | Causal-discovery framing, broader than Paper 003's single prepared operator |

**Differentiation:** Paper 003 borrows the *intuition* that relational structure is what unlocks compositional/OOD task success, but narrows the **claim** to a controlled repair-vs-expansion comparison with a **prespecified capability-crossing threshold**, matching Paper 002's confirmatory discipline rather than a broad generalization benchmark.

---

## 3. Capability-boundary framing (methodological precedent, different domain)

This is where the **"beyond error reduction"** measurement idea has precedent — in LLM-agent RL, not embodied world models. Cite as methodological precedent, not as competing work.

| Work | Framing | Precedent value |
| --- | --- | --- |
| [ProRL: Prolonged RL Expands Reasoning Boundaries in LLMs](https://arxiv.org/html/2505.24864v1) | Extended RL training solves problems the base model could not solve **at all**, not just faster/more accurately | Direct precedent for "does the intervention cross a **solve-at-all** boundary," the same shape as capability threshold crossing |
| [Does RL Expand the Capability Boundary of LLM Agents? A Pass@(k,T) Analysis](https://arxiv.org/html/2604.14877v1) | Explicit metric distinguishing capability-boundary expansion from within-boundary performance gain | Closest **metric-design** precedent for capability threshold crossing — worth citing directly when defining the metric in [paper003_description_v0.1.md](paper003_description_v0.1.md) |

**Boundary:** these papers study LLM reasoning/agents under RL scaling, not embodied structural world-model expansion. Paper 003 imports the **measurement logic** (solved-at-all vs solved-better), not the mechanism.

---

## Positioning matrix

| Line | What changes | Trigger | Failure-gated? | Success metric | vs Paper 003 |
| --- | --- | --- | :---: | --- | --- |
| NRI / Interaction Networks | learn relation graph | training data | no | prediction accuracy | assumes relation relevant from start |
| Factored World Models | object decomposition | design choice | no | zero-shot generalization (aggregate) | no repair-vs-expansion gate |
| TriRelVLA | relational policy structure | design choice | no | task success (aggregate) | no failure-triggered test |
| Compositional generalization (general) | combinatorial reuse | design / data diversity | no | held-out combination accuracy | not threshold-crossing framed |
| ProRL / Pass@(k,T) | RL training regime | scale / compute | no | **capability-boundary crossing** (LLM) | same metric shape, different domain/mechanism |
| **Paper 002** | mode expert | task failure after L1 repair | **yes** | prediction, recoverability | missing **mode**, not relation |
| **Paper 003** | relation module | task failure after L1 **and** L3-mode repair | **yes** | prediction, recoverability, **+ capability threshold crossing** | this paper |

---

## Manuscript paragraph (draft)

Relational and graph-based world models represent entities and their pairwise interactions explicitly, supporting generalization across novel object counts and configurations. Neural relational inference methods learn the interaction graph and dynamics jointly from observational data, and object-centric or factored world models decompose a scene to model relative interactions, showing that relational structure supports zero-shot generalization to new task configurations. Task-specific relational representations further extend this to compositional manipulation policies. These approaches establish that relational structure is *useful*, but they generally assume relational structure is warranted from the outset, or infer it from broad multi-scenario training data, rather than asking whether a specific pattern of task failure — one that already survives parameter repair and mode-level expansion — provides evidence that a relation is specifically missing.

A separate line of work, in LLM-agent reinforcement learning, distinguishes capability-boundary expansion (solving problems previously unsolvable at all) from within-boundary performance improvement, and designs explicit metrics for this distinction. We import this measurement logic into embodied structural world-model expansion: rather than reporting only mean prediction-error reduction, we test whether a prepared relation-module expansion converts task variants with near-zero baseline success into achievable ones, under a preregistered threshold.

We therefore study a restricted, failure-gated relational-adequacy decision: given a task failure that survives both parameter repair and mode-level structural expansion, does invoking a prepared relation-module operator expand the achievable-task space beyond what either prior arm reaches, without regressing performance on relation-independent tasks.

---

## References (anchor · verify at submission)

| ID | Work | URL |
| --- | --- | --- |
| NRI | Neural Relational Inference for Interacting Systems | [arXiv:1802.04687](https://arxiv.org/abs/1802.04687) |
| Dynamics review | Learning-based dynamics models for robotic manipulation | [Science Robotics](https://www.science.org/doi/10.1126/scirobotics.adt1497) |
| Factored WM | Factored World Models for Zero-Shot Generalization in Robotic Manipulation | [arXiv:2202.05333](https://arxiv.org/pdf/2202.05333) |
| TriRelVLA | Triadic Relational Structure for Generalizable Embodied Manipulation | [arXiv:2605.05714](https://arxiv.org/pdf/2605.05714) |
| RSCM | Relational Structural Causal Models | [arXiv:2606.14892](https://arxiv.org/pdf/2606.14892) |
| WM survey | World Model for Robot Learning: A Comprehensive Survey | [arXiv:2605.00080](https://arxiv.org/abs/2605.00080) |
| Compositional survey | A Survey on Compositional Generalization in Applications | [arXiv:2302.01067](https://arxiv.org/pdf/2302.01067) |
| ProRL | Prolonged RL Expands Reasoning Boundaries in LLMs | [arXiv:2505.24864](https://arxiv.org/html/2505.24864v1) |
| Pass@(k,T) | Does RL Expand the Capability Boundary of LLM Agents? | [arXiv:2604.14877](https://arxiv.org/html/2604.14877v1) |
| Paper 002 | Missing dynamic mode — detect · expand · validate | [paper002_related_work_v0.2.md](../paper002/paper002_related_work_v0.2.md) |

---

## Open item

- [ ] These are desk-search hits (2026-07-31), not a systematic review — verify coverage isn't missing a closer relational-expansion neighbor before prereg, same caveat as [lit positioning](paper003_lit_positioning_v0.1.md).

---

## Links

| Doc | Path |
| --- | --- |
| RQ | [paper003_rq_v0.1.md](paper003_rq_v0.1.md) |
| Method draft | [paper003_description_v0.1.md](paper003_description_v0.1.md) |
| Lit positioning (entry framing, narrower) | [paper003_lit_positioning_v0.1.md](paper003_lit_positioning_v0.1.md) |
