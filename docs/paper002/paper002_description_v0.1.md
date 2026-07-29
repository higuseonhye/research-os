# Paper 002 — Description v0.1

> **ARCHIVED** · mock→physics direction · superseded **2026-07-29** · **do not cite or extend**
> **Current Paper 002:** [WM expansion](paper002_description_wm_expansion_v0.1.md) · [archive index](archive/mock_to_physics/README.md)

> **Positioning:** mock-to-physics validation · not LLM curriculum · not policy training  
> **Program:** Exception-aware Physical AI · front-end of recoverability pipeline  
> **Pre-reg:** [paper002_prereg_v0.3.md](paper002_prereg_v0.3.md)

---

## Working title

**Can Cheap Proxy Evaluations Identify Informative Physical-AI Failures?
A Same-State Counterfactual Validation Study in Robotic Simulation**

### Alternative

**From Mock Ranking to Physical Informativeness: Validating Rule- and LLM-Generated Occlusion Curricula**

---

## Repository description

Paper 002 evaluates whether a **low-cost mock evaluator** can rank candidate occlusion mismatches according to their informativeness under **high-fidelity Isaac simulation**.

Starting from a fixed robot and world state, each candidate is evaluated through the same **CONTINUE-versus-REPLAN** counterfactual fork used in Paper 001. The study tests whether mock rankings transfer to Isaac-derived informativeness, whether top-ranked candidates enrich for informative failures, and whether an LLM-based goal planner performs at least as well as a deterministic rule-based planner.

This is a **validation and selection study**. It does not claim that generated curricula improve policy learning, autonomous recovery, or real-world surgical performance.

---

## Abstract

Robotic policies are commonly evaluated under researcher-selected perturbations, yet manually chosen failures may be redundant, trivial, or uninformative about the agent's capacity to recover. Automatic curriculum and environment-generation methods expand the space of candidate failures, but evaluating every candidate in high-fidelity physics simulation is computationally expensive.

We study whether a low-cost mock evaluator can identify candidate mismatches that remain informative under high-fidelity robotic simulation. Under a frozen occlusion contract, rule-based and LLM-based planners generate candidate perturbations. Each candidate receives a **continuous mock informativeness score** and is ranked before physics evaluation. A frozen transfer function maps mock occlusion parameters to Isaac simulation parameters. Starting from the same saved world and robot state, we execute paired CONTINUE and REPLAN responses over eight simulation seeds and label a candidate informative when a prespecified majority of valid seeds exhibits a task-relevant counterfactual difference.

The primary analysis measures **rank transfer** between mock and Isaac evaluations on the frozen export set. Secondary analyses test top-tier enrichment and LLM planner adequacy (absolute floor + non-inferiority vs rule). The protocol uses hierarchical hypothesis testing, bootstrap confidence intervals, permutation controls, and prespecified exclusion rules.

---

## One-sentence novelty

> Prior work uses generated environments to **train agents**; we validate whether a low-cost proxy can identify which generated physical mismatches will expose reliable same-state differences between recovery responses **before** expensive physics execution.

---

## Program position

Paper 002 is the **front-end** of the recoverability program — it selects which mismatches are worth measuring, not how to recover from them.

```text
World → Mismatch
           ↑
    Paper 002 — which mismatch to evaluate? (informative selection)
           ↓
    Paper 001 — how do responses compare @ S? (recoverability ruler)
           ↓
    Paper 003 — how to recover better? (policy / agent)
           ↓
    Paper 004 — when to revise world model?
```

| Paper | Question |
| --- | --- |
| **Paper 001** | What should AI do after mismatch? (measure recoverability @ **S**) |
| **Paper 002** | Which mismatch should we evaluate? (proxy validation) |
| **Paper 003** | How can AI learn to recover better? |
| **Paper 004** | When should AI revise its world model? |

---

## Keyword map (all active)

| Keyword | Role in Paper 002 |
| --- | --- |
| **Recoverability** | Select mismatches that **reveal** response differences Paper 001 measures |
| **Counterfactual** | CONTINUE vs REPLAN fork · same **S** |
| **Exception-aware Physical AI** | Find **informative exceptions**, not average-world success |
| **World model** | Mismatches that most **stress** the WM — selection, not update |
| **Active learning / experiment design** | Select **experiments**, not training samples |
| **Evaluation curriculum** | Not training curriculum — **which failures to run in sim** |
| **Decision timing** | Occlusion onset / persistence as perturbation params |
| **Scientific discovery** | Which experiment yields most information per GPU hour? |

---

## Claim boundaries

**May claim:**

- Extreme-export-set rank transfer under tested occlusion contract
- Top-tier enrichment under frozen export procedure
- LLM non-inferiority when all H3 criteria pass
- Feasibility of reducing unnecessary high-fidelity evaluations

**May not claim:**

- Improved robot-policy learning · autonomous curriculum system
- General physical-AI robustness · clinical effectiveness
- Sim-to-real transfer · open-ended learning · recovery-policy improvement

---

## Related docs

| Doc | Content |
| --- | --- |
| [paper002_related_work_v0.1.md](paper002_related_work_v0.1.md) | POET · PLR · GenSim · differentiation |
| [paper002_manuscript_pre_results_v0.1.md](paper002_manuscript_pre_results_v0.1.md) | Full methods · hypotheses · tables · interpretation |
| [paper002_rq_v0.3.md](paper002_rq_v0.3.md) | Operational RQs |
| [paper002_prereg_v0.3.md](paper002_prereg_v0.3.md) | Frozen confirmatory design |
