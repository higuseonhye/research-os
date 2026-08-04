# Paper 003 — Missing relation & capability expansion

> **Status 2026-08-04.** Design stage. Not preregistered, no confirmatory data.
> The relation was **changed today** after measuring three candidates, and
> several documents in this folder are superseded or carry corrections.
> **Read this file first** — the folder is not safe to read in alphabetical
> order.
>
> **Program context:** builds on [Paper 002](../paper002/README.md) (missing
> dynamic mode); this is the next taxonomy cell, a missing causal relation.

---

## Research question (unchanged)

> When repeated failures reveal that the agent's world model is missing not a
> mode but a **relation** between entities, does adding a prepared
> relation-module expansion open task capability that neither parameter repair
> nor a single mode-expert reaches — measured as growth of the achievable-task
> space, not only reduced prediction error?

[`paper003_rq_v0.1.md`](paper003_rq_v0.1.md) ·
[`paper003_description_v0.1.md`](paper003_description_v0.1.md)

---

## What changed, and why it matters

The question is unchanged. What changed is **what "relation" means in the
implementation**. Three candidates were measured against each other, and the
decision turned on a single-entity control — a model that sees no second body
and learns the burst pattern of the *target's own* trajectory.

| Relation | Relation necessary | Effect exceeds tolerance |
| --- | :---: | :---: |
| **Collision** — struck and released (what the Isaac line ran all day) | yes | **no** |
| **Carriage** — rides the reference throughout | **no** | yes |
| **Capture** — reference arrives at a still target, then carries it | **yes** | **yes** |

**Collision** cannot clear the placement tolerance. The push moves the target
away, which reduces penetration, which reduces the push, so displacement per
contact sits at the order of the interaction radius — below the 20 mm criterion.
Measured five independent ways
([the ceiling](paper003_displacement_ceiling_v0.1.md)).

**Carriage** clears it easily and makes the relation unnecessary: the
single-entity model matched the relational arm exactly, so H2 fails.

**Capture is the design.** Before the arrival the target is perfectly still, so
its own history says nothing; afterwards it rides, so the effect accumulates
without bound.

---

## Read in this order

### Current

| Document | What it settles |
| --- | --- |
| [`paper003_capture_design_v0.1.md`](paper003_capture_design_v0.1.md) | **The relation.** Why capture, and why carriage was recommended and then rejected |
| [`paper003_displacement_ceiling_v0.1.md`](paper003_displacement_ceiling_v0.1.md) | Why collision cannot work |
| [`paper003_branch_b_scene_v0.1.md`](paper003_branch_b_scene_v0.1.md) | The Isaac scene with a rigid object, and where 20 mm comes from |
| [`paper003_related_work_v0.1.md`](paper003_related_work_v0.1.md) · [`paper003_lit_positioning_v0.1.md`](paper003_lit_positioning_v0.1.md) | Positioning |

### Superseded or partly wrong — check the header before citing

| Document | Status |
| --- | --- |
| [`paper003_sliding_problem_v0.1.md`](paper003_sliding_problem_v0.1.md) | **Reversed the same day.** Concluded the gate collapses under real contact; it does not |
| [`paper003_two_body_encounter_v0.1.md`](paper003_two_body_encounter_v0.1.md) | Its tolerance argument is wrong (header says so). The machinery is real; the collision coupling under it is superseded |
| [`paper003_encounter_does_not_scale_v0.1.md`](paper003_encounter_does_not_scale_v0.1.md) | The scaling diagnosis holds; its proposed fix was overtaken by the change of relation |
| [`paper003_real_contact_design_v0.1.md`](paper003_real_contact_design_v0.1.md) | Its Branch A/B question is settled — the scene exists |

### Substantially outdated, not yet rewritten

| Document | Problem |
| --- | --- |
| [`paper003_prereg_draft_v0.1.md`](paper003_prereg_draft_v0.1.md) | Assumes the **collision** coupling throughout, grades variants by reference speed (measured non-functional), and its sample-size section predates the change of relation. **Needs a rewrite, not an edit** |
| [`paper003_commitment_task_v0.1.md`](paper003_commitment_task_v0.1.md) | Describes carriage — "a bread slice carried by a tray" — and its arm-B band came from that rejected model |
| [`paper003_pilot_runbook_v0.1.md`](paper003_pilot_runbook_v0.1.md) | Targets the reach task; the scene is now the lift task |

---

## Settled

- **The scene.** `Isaac-Lift-Block-PSM-IK-Rel-Play-v0` reports
  `rigid_objects: ['object']` and command `object_pose`. The bootstrap used to
  delete it as "incompatible"; the incompatibility was two lines setting a debug
  marker's scale.
- **The placement tolerance: 20 mm**, on two independent grounds — the task
  family's own `mdp/terminations.py` threshold, and the block's half-height.
- ~~**The gate.** Fires on capture at 1.00 using the *same* thresholds as
  collision.~~ **Reversed 2026-08-04.** The gate fires on capture at **0.00**,
  with no post-contact far-field steps in any of 20 rollouts. The 1.00 came from
  an off-by-one in `capture_displacement`, which threw a captured target one
  body-step past its carrier so that the pauses sorted into the far field. The
  capture-specific variant was deleted against that artefact, and its premise
  was right. It still rejects self-moving controls at 0.00.

  **This blocks the paper**: `can_estimate` requires the gate, so arm D cannot
  act under capture and scores exactly arm B.
- **The gate under real contact.** Fires on every Isaac trace containing a
  strike, with `cv_gain` between −0.20 and −0.75 — a constant-velocity model is
  *worse* than zero-order, so Paper 002's operator does not absorb the residual.
- **The cell loop.** `wm_expansion/cell.py` runs the same code the GPU runs with
  the simulator behind one callback. It has caught six defects before GPU time.

## Open, in order

1. ~~Connect capture to the cell loop and the encounter.~~ **Done.**
   `CellSpec(coupling="capture")` drives a cell, paired with the `burst`
   schedule — a body that arrives and carries the target off has no reason to
   withdraw. Under `probe` the carried target is dragged back with it.
2. **The commit window relative to the capture.** Must be fixed on arm-neutral
   grounds — "so that arm B fails" is not one. **This is the next decision, and
   it is a judgement rather than an implementation.**
3. **Score the arms under capture in a cell.** The relation and the loop now
   meet; nothing has been measured through them together.
4. **Rewrite the preregistration**, which assumes collision throughout.
5. **Then** the confirmatory sample.

## Not in this repository

Isaac records from 2026-08-04 were written on the VESSL pod and never pushed —
the sweeps under `results/paper003_probe_sweep`, `results/gate_v*`,
`results/lift_*`. Their **numbers are recorded** in the documents above and under
[`exp_surg_004_relation_expansion/results/`](../../experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/).
A rerun should regenerate them rather than hunt for the files, since the
encounter has changed since.

## Code

| Module | Role |
| --- | --- |
| [`wm_expansion/relation_dynamics.py`](../../scripts/wm_expansion/relation_dynamics.py) | Couplings, the gate, the estimators, capture |
| [`wm_expansion/cell.py`](../../scripts/wm_expansion/cell.py) | One commitment cell, simulator behind a callback |
| [`wm_expansion/encounter.py`](../../scripts/wm_expansion/encounter.py) | Encounter geometry and schedules |
| [`wm_expansion/stopping.py`](../../scripts/wm_expansion/stopping.py) | How long a struck object keeps moving |
| [`wm_expansion/commitment_episode.py`](../../scripts/wm_expansion/commitment_episode.py) | The episode driver and the arms |
| [`orbit_lift_relation_cell.py`](../../scripts/orbit_lift_relation_cell.py) | Isaac adapter for the lift scene |
| [`orbit_lift_stopping_probe.py`](../../scripts/orbit_lift_stopping_probe.py) | Strike-and-measure probe |

225 tests, all CPU.

---

## Not claiming (public, draft)

General causal discovery · relation invention outside the prepared operator ·
capability emergence outside the tested task family · clinical or hardware
deployment.
