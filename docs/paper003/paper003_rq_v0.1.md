# Paper 003 — Research question v0.1

> **Status:** design · not yet run · Experiment ID TBD
> **Program L0:** When reality cannot be explained by the agent's **model class**, how should an embodied system revise **parameters and the architecture/composition** of its world-modeling system?
> **Builds on:** [Paper 002 description](../paper002/paper002_description_wm_expansion_v0.1.md) · [expansion taxonomy](../paper002/paper002_wm_system_expansion_v0.1.md)

---

## Central question (v0.1)

> When repeated failures reveal that the agent's world model is missing not a **mode** but a **relation** between entities, does adding a prepared relation-module expansion open **task capability** that neither parameter repair nor a single mode-expert reaches — measured as growth of the achievable-task space, not only reduced prediction error?

Paper 002 asked whether a missing **dynamic mode** (drift vs static) justifies structural expansion. Paper 003 asks the next taxonomy cell — a missing **causal relation** (line 84/100 of the expansion taxonomy: `add_relation_module`) — and adds a stronger success criterion: does expansion cross **capability thresholds** (task variants that go from unachievable to achievable), not merely shrink error on already-partially-solvable variants.

---

## Framing note (external vs internal — keep separate)

Two audiences read this RQ differently; do not collapse them into one sentence:

| Audience | Framing | Use |
| --- | --- | --- |
| Lab intro / advisor conversation (e.g. execution-horizon, replanning-trigger language) | "When should an autonomous system revise its model class rather than repair within it?" | Entry point — familiar engineering vocabulary, useful for first contact |
| Actual RQ this paper answers | "After a structural gap is filled, does the system do something qualitatively new — not just fail less?" | What gets measured and written up |

The entry framing is not wrong, it is just narrower than the question being asked. See [vision_narrative_v0.2.md § Domain generality](../mismatch_lab/vision_narrative_v0.2.md) for the same distinction applied to the program's long-term framing, and [paper003_lit_positioning_v0.1.md](paper003_lit_positioning_v0.1.md) for the papers behind the entry framing and exactly where they stop short of this RQ.

---

## Sub-questions

| ID | Question | Role |
| --- | --- | --- |
| **RQ-1** | After L1 (parameter) and L3-mode repair both fail to absorb structured residual, does the residual signature specifically implicate a **missing relation** (correlates with a second entity's state) rather than a missing mode (correlates with time/regime only)? | Detection / diagnosis |
| **RQ-2** | Does invoking a prepared **relation-module** expansion reduce residual and improve control on the novel relational task beyond L1 and L3-mode arms? | Expansion validity |
| **RQ-3** | Does expansion convert task variants with **~0% baseline success** into **>0% success** — i.e. cross a capability threshold — rather than only lowering error on variants that were already partially solvable? | **Core novel contribution** |
| **RQ-4** | Does relation expansion avoid regression on Paper-002-style nominal and single-mode-drift tasks that do not require the relation? | Guardrail |

---

## Program position

```text
L0         Representation reconstruction under model-inadequate reality
Paper 001  Recoverability @ S (optional credential)
Paper 002  Missing dynamic mode — detect · expand · validate
Paper 003  Missing causal relation — detect · expand · validate CAPABILITY (this doc)
Later      Human-provided representation · surgical exceptions
```

Paper 003 is **not** required to follow Paper 002 sequentially in execution, but reuses its two-encounter protocol and expansion-gate logic (see [method draft](paper003_description_v0.1.md)).

---

## What Paper 003 is not (draft)

- Not a claim that relation modules solve arbitrary causal discovery — the relation is a **prepared** operator, not free structure search (same constraint as Paper 002's `add_dynamics_expert`).
- Not a general "capability emergence" claim outside the tested task family.
- Not the execution-horizon / replanning-trigger paper implied by the entry framing above — that framing is for lab conversations, not this RQ.

---

## Links

| Doc | Path |
| --- | --- |
| Description / method draft | [paper003_description_v0.1.md](paper003_description_v0.1.md) |
| Paper 002 description (parent method) | [paper002_description_wm_expansion_v0.1.md](../paper002/paper002_description_wm_expansion_v0.1.md) |
| Expansion taxonomy | [paper002_wm_system_expansion_v0.1.md](../paper002/paper002_wm_system_expansion_v0.1.md) |
| Naming / program roadmap | [NAMING.md](../NAMING.md) |

---

## Version history

| Version | Date | Note |
| --- | --- | --- |
| v0.1 | 2026-07-31 | Initial RQ draft — missing relation + capability-threshold framing |
