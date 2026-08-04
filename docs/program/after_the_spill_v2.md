# After the Spill Research Program v2.0

> **Core question:** How should unexpected experience change an embodied system?

## Program mission

After the Spill studies decision-making after unexpected experience in embodied
systems. It asks when a system should preserve its current model, recover within
it, repair parameters, expand representation, or coordinate multiple recovery
operators.

The program is built to survive individual paper outcomes. A paper may fail,
but the foundation documents should continue to clarify the question.

## Practical question

> Given an unexpected experience, what is the smallest change that restores
> competent action without hiding the evidence that made change necessary?

One compact decision form is:

```text
c* = argmin_c [task loss + change cost + risk + future cost]
```

where `c` ranges over the available change operators.

## Change decision framework

| Object | Working role |
| --- | --- |
| Experience | A situated event that violates, stresses, or confirms the current model |
| Evidence | Information extracted from experience that bears on adequacy |
| Operator | A change action applied to state, policy, model, representation, or coordination |
| Closure | A test that the chosen change is sufficient for the current task boundary |
| Competence | The ability to act successfully under the relevant post-experience conditions |

The decision is not "learn or do not learn." It is a choice among change
operators with different costs and risks.

## Change operators

| Operator | Meaning | Typical failure if overused |
| --- | --- | --- |
| Preserve | Record the episode without permanent adaptation | Ignores real mismatch |
| Recover | Restore competent behavior without changing the model | Treats inadequacy as disturbance |
| Repair | Update parameters or local policy within the current representation | Overfits inside the wrong model |
| Expand | Add a prepared mode, relation, entity, constraint, or representation | Invents structure too eagerly |
| Coordinate | Select, order, or recruit multiple recovery capabilities | Adds policy complexity without evidence |

## Paper roles

| Paper | Decision studied | Program contribution |
| --- | --- | --- |
| Paper 001: Recoverability | Which response restores execution at the same mismatch state? | Defines the post-mismatch recovery window |
| Paper 002: Model Adequacy | When is parameter repair insufficient? | Tests evidence for moving from repair to model-order expansion |
| Paper 003: Representation Expansion | Which representational operator is missing? | Tests mode/relation discrimination and capability expansion |
| Paper 004: Experience Disposition | How much should an experience change the system? | Classifies ignore, preserve, recover, repair, expand, and escalate decisions |
| Paper 005: Recovery Orchestration | How should multi-relation consequences be contained and resolved? | Studies ordered operator choice under uncertainty |

Capability recruitment is a Paper 005 mechanism, not a separate paper.
Ecosystem adaptation remains a long-term open problem.

## Foundation documents

| ID | Title | Immediate question |
| --- | --- | --- |
| D000 | Mathematical Foundation | What are the program's stable objects? |
| D001 | Claim & Novelty Audit | Is this already Active Inference, Continual Learning, Meta Learning, Recovery Planning, Resilience Engineering, Self-healing Systems, Adaptive Control, or Decision Theory? |
| D002 | Literature Matrix | Can every paper be read through experience, change, decision, evidence, and closure? |
| D003 | Terminology | Which words are allowed, and what do they mean? |
| D004 | Formal Definitions | What must be defined before experiments can claim anything? |
| D005 | Unified Evaluation Protocol | What counts as evidence that an operator was sufficient? |
| D006 | Research Roadmap | How do papers and products accumulate into one program? |

## Shared evaluation philosophy

The program evaluates decisions, not only outcomes. A system that succeeds after
unnecessary expansion may still be making a bad change decision. A system that
fails after refusing expansion may have learned the boundary of repair.

Every study should measure whether the amount of change was justified:

1. recovery closure,
2. unnecessary and missed revision,
3. revision latency,
4. nominal regression,
5. cumulative task regret,
6. unresolved relation burden,
7. claim tier supported by the result.

## Claim boundary

Current evidence supports controlled simulation claims. It does not support
clinical deployment, autonomous self-improvement, general intelligence,
universal resilience, arbitrary causal discovery, unbounded world-model
expansion, or a solution to continual learning.

The line "intelligence chooses the smallest sufficient change" is a governing
principle and an audit target. It becomes a scientific claim only where evidence
and closure tests make it measurable.

## Governing principle

> Intelligence is the ability to determine the smallest sufficient change after
> unexpected experience.

Build less. Break more. Keep what survives.

The program should become harder to fool over time.

*Living document - 2026-08-04*
