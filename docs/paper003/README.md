# Paper 003 — Missing relation & capability expansion

> **Status 2026-08-05.** Design stage. The main preregistration is still
> unwritten and there is no confirmatory *physical* data — but H2's decisive
> arm comparison **is** preregistered and settled: see
> [the SELF arm rule](paper003_self_arm_prereg_v1.0.md) and
> [its result](../../experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/self_arm_v1.0/RESULTS.md).
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
| [`paper003_prereg_v1.0.md`](paper003_prereg_v1.0.md) | **The preregistration.** Locked in design, open in numbers until an Isaac calibration pilot for capture |
| [`paper003_self_arm_prereg_v1.0.md`](paper003_self_arm_prereg_v1.0.md) | **H2's decisive comparison**, and its rule fixed before the arm existed |
| [`paper003_onset_is_not_predictable_v0.1.md`](paper003_onset_is_not_predictable_v0.1.md) | **What the paper may not claim**, and why the three-step band is the right answer |
| [`paper003_rendezvous_v0.1.md`](paper003_rendezvous_v0.1.md) | Why a grasp needs an arrival, not a fly-by |
| [`paper003_capture_pilot_runbook_v0.1.md`](paper003_capture_pilot_runbook_v0.1.md) | How to run the Isaac calibration pilot, and what to read first |
| [`paper003_derived_from_physics_v0.1.md`](paper003_derived_from_physics_v0.1.md) | The two numbers the scene decides, and the rule for reading them off it |
| [`paper003_cv_gain_horizon_v0.1.md`](paper003_cv_gain_horizon_v0.1.md) | The gate statistic was measuring the horizon as well as the motion |
| [`paper003_where_collapse_is_defended_v0.1.md`](paper003_where_collapse_is_defended_v0.1.md) | Why the collapse threat belongs to H2 and not to the gate |
| [`paper003_servo_encounter_v0.1.md`](paper003_servo_encounter_v0.1.md) · [`paper003_rendezvous_v0.1.md`](paper003_rendezvous_v0.1.md) | Why the encounter arrives before it carries |
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
| [`paper003_prereg_draft_v0.1.md`](paper003_prereg_draft_v0.1.md) | **Superseded entirely** by [`paper003_prereg_v1.0.md`](paper003_prereg_v1.0.md). Collision throughout; provenance only, not to be cited for any design decision |
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
- **The gate, and it now has two forms of positive evidence.** The claim that
  one threshold set covered both relations was **wrong, and corrected
  2026-08-04**: with an off-by-one fixed in `capture_displacement`, the
  proximity contrast abstains on *every* capture cell — a carrier that never
  leaves supplies no far field. The 1.00 previously recorded came from that
  defect, which threw a captured target one body-step past its carrier so the
  pauses sorted into the far field.

  One gate still covers both relations, by admitting **carriage** as a second
  form of positive evidence: the target's displacement *is* a body's
  displacement, on ≥ 0.80 of moving steps with a run of ≥ 3. Collision still
  enters through the contrast; capture enters here; every other clause applies
  unchanged. The constant-velocity ceiling is what keeps `drift` out, which
  agrees with its body on 0.71 of steps and would otherwise pass.
  [The measurement](../../experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/capture_arms_v0.1/RESULTS.md)
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
2. ~~The commit window relative to the capture.~~ **Done.** Within one
   dispense-length of a body's arrival, on either side, anchored on
   `contact_arrivals`. Fixed on the structure of the action: the dispense takes
   `dispense_latency` steps, so a commit further out than that either completes
   before anything has happened or measures a regime the arrival no longer
   governs. Symmetric because there is no reason to prefer a side. What it
   removes is an artefact, not a preference — under capture the eligibility
   screen admits every step after the arrival, so the commit distribution was
   being set by `episode_steps` and sat almost entirely in the riding tail where
   a constant-velocity model absorbs the motion.
3. ~~Score the arms under capture in a cell.~~ **Done.** Under `capture` +
   `burst`, where arm D can act it is right **0.78** of the time against 0.06
   where it declines; by commit offset the relation pays **0.53 → 0.71** against
   0.00 for parameter repair and ≤ 0.07 for the mode operator. All four
   controls and the collision cells are unchanged.
   [The measurement](../../experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/capture_arms_v0.1/RESULTS.md)
4. ~~Decide how the gate admits a capture.~~ **Done** — carriage, as a second
   form of positive evidence in the same gate. See Settled, above.
5. ~~The overlap between the commit window and arm D's readiness.~~ **Not a
   defect, and settled.** Arm D cannot act before +4 because **there is nothing
   to act on before the capture**: `static` and `noise` are worlds where a body
   arrives at the target and nothing happens, and it arrives *closer* than in
   the treatment — 12 and 14 mm against 42 mm, in 1.00 of cells. Up to contact,
   a capturing approach and a non-capturing one are the same observation. An arm
   that declined there was correct.
   [Why](paper003_onset_is_not_predictable_v0.1.md)
6. ~~Measure the single-entity arm under capture + burst.~~ **Done, and H2
   stands.** Preregistered rule locked before the arm was implemented; 200
   paired cells; **arm D 0.650, SELF 0.000**, 130 discordant pairs all in D's
   favour, one-sided exact McNemar p = 7.3 × 10⁻⁴⁰, margin +0.650. SELF acted
   on 0.675 of cells and was not broken — it holds a median of 4 steps of its
   own motion against a 14-step cycle and extrapolates through a pause it
   cannot see.
   [Rule](paper003_self_arm_prereg_v1.0.md) ·
   [Result](../../experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/self_arm_v1.0/RESULTS.md)

   **The limitation that came with it is now measured too.** The protection is
   bounded in time, and the bound is **+30** — a little over two burst cycles
   after the arrival, on fresh seeds. The protocol band is [−6, +6] and SELF
   scores ≤ 0.02 inside it, so the catch-up sits five times further out than any
   commit the protocol makes. What stops arm D first is **the gate**: `cv_gain`
   climbs as the carry lengthens and arm D declines exactly where it crosses the
   ceiling, so the clause written for `drift` lands unprompted on the boundary
   of H2's validity. Past it the sufficient model is a single-entity *periodic*
   one — neither B, nor C, nor D, and proposed by neither paper.
   [The bound](../../experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/self_arm_bound_v0.1/RESULTS.md)
7. ~~Redraw the two-body encounter for capture.~~ **Retired for this relation,
   not redrawn.** Under capture the first body to arrive consumes the target, so
   "demonstrate on one body, apply with another" has nothing to apply to. A
   decoy repair was designed and rejected for the same reason as item 5: its
   strong form requires predicting the onset, which would drive arm D to zero on
   `static` and `noise` and fail H4, and its weak form moves the usable band by
   a step or two. The two-body encounter stays with collision.
   [Why](paper003_onset_is_not_predictable_v0.1.md)
8. ~~Rewrite the preregistration, which assumes collision throughout.~~
   **Done** — [`paper003_prereg_v1.0.md`](paper003_prereg_v1.0.md), which
   supersedes the draft entirely. Locked in design: arms including SELF, the
   commit window, the confirmatory test, the sizing *rule*, the scope limits,
   and a list of tuning that will not be done. **Open in numbers**, all marked
   `PENDING`, because none of them may be inherited from injected coupling.
9. **An Isaac calibration pilot for capture.** ~~The first thing that could end
   this design.~~ **It does not: capture happens under real contact.** Servoed
   onto the block, the gripper closes with 0.25 mm of disturbance and the object
   then rides for **10 consecutive steps at 0.93 agreement** — against the gate's
   own requirement of 3 steps at 0.80. **But the capture radius is under 1 mm**,
   while the arm's steady-state error following a moving script is 7.3 mm, so
   **a script-following encounter cannot produce a capture here**: it has to
   servo to contact first, then carry.
   [The measurement](../../experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/capture_pilot_v0.1/RESULTS.md)

   Three hypotheses died on the way, all of them explanations for an artefact:
   the environment was resetting mid-run and the teleport was being read as a
   36 mm ejection. Engagement, `normal_alignment` and the observation noise are
   still unmeasured, because no cell has yet produced a capture *through the
   protocol*.

   ~~Formality check.~~ Every result before this was arithmetic —
   the cell computes the target's motion and writes it into the command.
   Whether the lift scene produces a *capture* rather than a collision is
   unmeasured. The pilot must also give the engagement rate under contact
   jitter (which sets `n`), `normal_alignment` under real contact, and the
   observation noise the gate's margin is stated against.
10. **Then** the confirmatory sample. Not on this machine — GPU, on the pod.

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
| [`paper003_capture_arms.py`](../../scripts/paper003_capture_arms.py) | Scores every arm under each relation, in the commit window |
| [`wm_expansion/cell.py`](../../scripts/wm_expansion/cell.py) | One commitment cell, simulator behind a callback |
| [`wm_expansion/encounter.py`](../../scripts/wm_expansion/encounter.py) | Encounter geometry and schedules |
| [`wm_expansion/stopping.py`](../../scripts/wm_expansion/stopping.py) | How long a struck object keeps moving |
| [`wm_expansion/commitment_episode.py`](../../scripts/wm_expansion/commitment_episode.py) | The episode driver and the arms |
| [`orbit_lift_relation_cell.py`](../../scripts/orbit_lift_relation_cell.py) | Isaac adapter for the lift scene |
| [`orbit_lift_stopping_probe.py`](../../scripts/orbit_lift_stopping_probe.py) | Strike-and-measure probe |

| [`paper003_self_arm.py`](../../scripts/paper003_self_arm.py) | The preregistered SELF arm test, with no flag to relax the rule |
| [`paper003_self_arm_bound.py`](../../scripts/paper003_self_arm_bound.py) | Off-protocol probe: where the single-entity arm catches up |
| [`wm_expansion/capture_verdict.py`](../../scripts/wm_expansion/capture_verdict.py) | Was that trace a capture, a collision, or nothing |
| [`orbit_lift_grasp_probe.py`](../../scripts/orbit_lift_grasp_probe.py) | What grasp the scene supports, and at what separation |

232 tests, all CPU.

---

## Not claiming (public, draft)

General causal discovery · relation invention outside the prepared operator ·
capability emergence outside the tested task family · clinical or hardware
deployment.
