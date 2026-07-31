# Paper 003 — Missing relation & capability expansion

> **Status:** design v0.1 · not yet run · Experiment ID TBD
> **Program context:** builds on [Paper 002](../paper002/README.md) (missing dynamic mode) · next taxonomy cell = missing causal relation

---

## Working title

**Beyond Error Reduction: Does Structural Expansion Enable Task Capability That Repair Cannot?**

---

## Research question (v0.1)

> When repeated failures reveal that the agent's world model is missing not a mode but a **relation** between entities, does adding a prepared relation-module expansion open task capability that neither parameter repair nor a single mode-expert reaches — measured as growth of the achievable-task space, not only reduced prediction error?

See [`paper003_rq_v0.1.md`](paper003_rq_v0.1.md) · [`paper003_description_v0.1.md`](paper003_description_v0.1.md)

---

## What's new vs Paper 002

| | Paper 002 | Paper 003 |
| --- | --- | --- |
| Missing thing | Dynamic mode (static vs drift) | Causal relation (dependency between two entities) |
| Expansion operator | `add_dynamics_expert` | `add_relation_module` |
| Primary success metric | Prediction error, recoverability | **+ capability threshold crossing** (0% → achievable) |

---

## Status

- [x] RQ drafted (v0.1)
- [x] Method / protocol drafted (v0.1)
- [x] NAMING.md program roadmap updated
- [x] Lit review — execution-horizon framing vs internal RQ
- [ ] Environment / simulator choice locked
- [ ] Prereg

---

## Not claiming (public, draft)

General causal discovery · relation invention outside the prepared operator · capability emergence outside the tested task family · clinical or hardware deployment.

---

## Links

| Doc | Purpose |
| --- | --- |
| [paper003_rq_v0.1.md](paper003_rq_v0.1.md) | Central question, sub-questions, framing note |
| [paper003_description_v0.1.md](paper003_description_v0.1.md) | Method draft, protocol, capability-threshold metric definition |
| [paper003_lit_positioning_v0.1.md](paper003_lit_positioning_v0.1.md) | Execution-horizon literature (Garg/Shkurti) vs this RQ, with citations |
| [Paper 002](../paper002/README.md) | Parent method this reuses (two-encounter protocol, expansion gate) |
| [NAMING.md](../NAMING.md) | Program-level roadmap (Paper 003 row) |
