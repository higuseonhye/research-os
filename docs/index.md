# After the Spill

**How should unexpected experience change an embodied system?**

Most AI research asks how systems should learn.

We ask a different question:

**How much should they change?**

This site documents an ongoing research program on decision-making after
unexpected experience in embodied systems.

[Research program](program/README.md) | [GitHub](https://github.com/higuseonhye/research-os) | [Mismatch Lab](mismatch_lab/README.md)

---

## Core question

Unexpected experience can mean many things: noise, disturbance, recoverable
failure, model inadequacy, missing representation, or the need to coordinate
several recovery operators.

The program studies the decision among those interpretations.

```text
Experience -> Evidence -> Operator -> Closure
```

---

## Research program

| Foundation document | Role |
| --- | --- |
| D000 Mathematical Foundation | Objects and primitives |
| D001 Claim & Novelty Audit | Why the program could be wrong |
| D002 Literature Matrix | Shared reading schema |
| D003 Terminology | Stable language |
| D004 Formal Definitions | Operational definitions |
| D005 Evaluation Protocol | Evidence and closure |
| D006 Research Roadmap | Paper/product sequence |

[Program charter v2](program/after_the_spill_v2.md)

---

## Papers

| Paper | Question | Status |
| --- | --- | --- |
| **001 Recoverability** | Can the system still recover from here? | Tier C complete |
| **002 Model Adequacy** | Should it repair or expand the model class? | Tier C complete |
| **003 Representation Expansion** | Does expansion open capability that repair cannot reach? | Design/calibration |
| **004 Experience Disposition** | What should be done with the experience itself? | Program-defined |
| **005 Recovery Orchestration** | How should recovery operators be sequenced? | Program-defined |

---

## Products

| Product | Program role |
| --- | --- |
| **Robot Diff** | Compare embodied rollouts and expose consequential differences |
| **Mismatch Lab** | Public lab surface for diff, replay, explanation, and benchmark design |
| **Evaluation Toolkit** | Shared tests for evidence, operator choice, and closure |
| **Benchmark** | Repeatable tasks where unexpected experience forces a change decision |

[Mismatch Lab](mismatch_lab/README.md) | [Robot Diff demo](mismatch_lab/diff_explorer_v0.1.html)

---

## Current evidence boundary

The strongest current claims are controlled simulation claims. This program does
not yet claim clinical deployment, hardware transfer, autonomous structural
self-improvement, or a complete theory of intelligence.

Negative and design-stage results are part of the record. A program gets
stronger by rejecting weak claims early.

*Updated 2026-08-04*
