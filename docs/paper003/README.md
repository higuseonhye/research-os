# Paper 003 — Missing relation & capability expansion

> **Status:** design v0.1 · Isaac calibration pilot run (10 seeds, excluded from evidence) · not preregistered · Experiment ID TBD
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
- [x] Related work — relational/graph world models, capability-boundary framing precedent
- [x] Environment / simulator choice locked — Isaac Sim/ORBIT Reach continuation, physical-coupling relation
- [x] Relation module + gate implemented and separated on a CPU proxy ([`relation_dynamics.py`](../../scripts/wm_expansion/relation_dynamics.py), 10 tests)
- [x] **Capability threshold crossing — constructed.** A continuous reach-and-hold task produced no gap; a [commitment-point task](paper003_commitment_task_v0.1.md) does, with arm B's lockout speed predicted exactly from task geometry.
- [x] **Arm D estimates the reference pattern online** — no longer handed it. Under 20% observation noise at the speed where B is locked out: B 0.00, C 0.29, **D 0.69**, oracle 1.00. The crossing survives; estimating costs ~0.31.
- [x] **Robustness to irregular timing measured.** The estimator does exploit periodicity — it loses ~0.4 from a strict cycle to ±3 steps of jitter — but the gap holds in the worst case tested (jitter + noise: B 0.08, **D 0.52**).
- [x] **Preregistration drafted** — [draft v0.1](paper003_prereg_draft_v0.1.md). Arms, task, primary endpoint, and hypotheses H1–H4 locked; **six parameters left open** because they need real physics, not a 1-D proxy.
- [x] **Episode driver** — all decision logic in [`commitment_episode.py`](../../scripts/wm_expansion/commitment_episode.py), CPU-tested, so the Isaac script is a shell over scene setup
- [x] **Isaac pilot runner** — [`orbit_reach_relation_pilot.py`](../../scripts/orbit_reach_relation_pilot.py) + [runbook](paper003_pilot_runbook_v0.1.md). Ran in Isaac after eight defects a GPU-less environment could not catch
- [x] **Calibration pilot run in Isaac** (10 seeds, excluded from evidence) — [RESULTS](../../experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/isaac_relation_pilot_v0.1/RESULTS.md). The operators dissociate: arm C lands the mode cell (0.0 mm, 1.00) and arm D declines there; arm D leads on the relational cell. No regression where the relation is absent.
- [x] **Commit policy locked** — uniform over eligible steps, with its expected directional effect declared before the run
- [x] **Arm D estimates the coupling** rather than being handed it — radius and gain fitted from observed contacts
- [ ] **Sample size** — nine committed treatment cells; arm D's 0.67 vs 0.56 lead is one cell and cannot support a rate comparison
- [ ] Measure observation noise and timing irregularity — **still unmet**: the coupling is injected through the target command rather than emerging from contact, so there is no physical jitter to measure
- [ ] Speed sweep to locate arm B's near-zero band
- [ ] Freeze the preregistration, then run confirmatory

---

## Not claiming (public, draft)

General causal discovery · relation invention outside the prepared operator · capability emergence outside the tested task family · clinical or hardware deployment.

---

## Links

| Doc | Purpose |
| --- | --- |
| [paper003_rq_v0.1.md](paper003_rq_v0.1.md) | Central question, sub-questions, framing note |
| [paper003_description_v0.1.md](paper003_description_v0.1.md) | Method draft, protocol, capability-threshold metric definition |
| [paper003_prereg_draft_v0.1.md](paper003_prereg_draft_v0.1.md) | **Draft preregistration** — locked arms/endpoint/hypotheses, and the six parameters the calibration pilot must set |
| [paper003_pilot_runbook_v0.1.md](paper003_pilot_runbook_v0.1.md) | How to run the calibration pilot, what it must produce, and the runner's known limits |
| [paper003_commitment_task_v0.1.md](paper003_commitment_task_v0.1.md) | The task shape that makes capability threshold crossing measurable, and the breakfast-domain scope boundary |
| [paper003_related_work_v0.1.md](paper003_related_work_v0.1.md) | Core novelty comparison — relational/graph world models, capability-boundary framing precedent |
| [paper003_lit_positioning_v0.1.md](paper003_lit_positioning_v0.1.md) | Execution-horizon literature (Garg/Shkurti) — narrower, entry-framing only |
| [Paper 002](../paper002/README.md) | Parent method this reuses (two-encounter protocol, expansion gate) |
| [NAMING.md](../NAMING.md) | Program-level roadmap (Paper 003 row) |
