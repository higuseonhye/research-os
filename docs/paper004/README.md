# Paper 004 — Experience Disposition

> **Status:** design stage · no confirmatory claims

## Core question

> After an unexpected embodied experience, what should the system do with the experience before deciding how much to change itself?

Paper 004 is the selection layer of the After the Spill program. Papers 001–003 establish evidence about recovery, parameter repair, and structural expansion. Paper 004 studies how those evidence types should be combined into a bounded disposition decision.

## Candidate dispositions

| Disposition | Meaning |
| --- | --- |
| **Preserve** | Record the episode without permanent adaptation. |
| **Recover** | Restore competent behavior without changing the model. |
| **Repair** | Update parameters within the current representation. |
| **Expand** | Invoke a prepared structural operator when repair is insufficient. |
| **Coordinate** | Escalate or recruit capabilities when consequences exceed one controller. |

`Ignore` is not a separate operator in v0.1. An episode may receive low weight, but evidence should remain auditable. `Coordinate` is deferred from the first confirmatory cell unless a multi-relation environment is explicitly introduced.

## First-paper boundary

The first confirmatory study should compare only:

- Preserve
- Repair
- Expand

under sequential experiences drawn from three known families:

1. transient anomaly,
2. parameter-repairable mismatch,
3. persistent structural mismatch.

The study does **not** ask the system to invent arbitrary representations or recovery workflows.

## Proposed contribution

> A recovery-conditioned experience-disposition rule that selects the smallest sufficient change while reducing unnecessary structural revision, missed revision, and nominal regression.

## Dependencies

- [Paper 001](../paper1/README.md): recoverability evidence
- [Paper 002](../paper002/README.md): repair-versus-expansion evidence
- [Paper 003](../paper003/README.md): operator discrimination and capability expansion
- [Program charter](../program/after_the_spill_v2.md)

## Documents

- [Research questions](paper004_rq_v0.1.md)
- [Disposition gate](paper004_experience_disposition_gate_v0.1.md)

*Updated 2026-08-04*