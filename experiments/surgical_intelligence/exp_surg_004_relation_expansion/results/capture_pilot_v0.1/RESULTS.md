# Capture exists in the lift scene, and its radius is under a millimetre

> **Isaac calibration pilot, 2026-08-04/05, A100-SXM4-80GB.**
> `Isaac-Lift-Block-PSM-IK-Rel-Play-v0`, orbit-surgical on Isaac Lab v1.0.0.
> Calibration, not confirmatory evidence — but the question it answers is the
> one the [preregistration](../../../../../docs/paper003/paper003_prereg_v1.0.md)
> named as the first thing that could end the design.
>
> **Read the retraction section before quoting any contact number from the
> earlier part of this session.**

## The answer

**Capture happens under real contact.** Servoed onto the block with nothing else
running, the gripper closes and:

| | |
| --- | ---: |
| object travel on closing | **0.25 mm** |
| largest single step during the hold | 0.28 mm |
| travel while the arm then moves | 14.53 mm |
| carriage agreement | **0.93** |
| consecutive riding steps | **10** |

Held, and carried. Every result in Paper 003 up to this point was arithmetic —
the cell computed the target's motion and wrote it into the command. This is the
first time the relation was produced by physics and read back out.

**The gate's own statistic recognises it.** `carriage_evidence` requires 0.80
agreement over a run of 3; the physical trace gives 0.93 over 10. That is not
luck: `capture_verdict` was built to decide with the same statistic the gate and
arm D use, precisely so that a trace certified here is a capture by the measure
the arms are scored through.

## The radius, which is the constraint

Closing at a chosen separation instead of the closest reachable:

| Closed at | Riding steps | Verdict |
| ---: | ---: | --- |
| **0.81 mm** | **10** | **captured** |
| 1.99 mm | 1 | nudged |
| 3.92 mm | 0 | missed |
| 4.91 mm | 0 | missed |
| 7.71 mm | 0 | missed |
| 9.65 mm | 0 | missed |

**The capture radius is under 1 mm.** Past about 2 mm the jaws close on nothing.

Those last rows were labelled `held_not_carried` when the sweep was run, and the
label was wrong in a way worth recording: an object that neither moves on closing
nor follows afterwards was never held. Without a contact force, riding is the
only evidence of holding, so a label claiming holding without it invents its own
premise — and points at fixing the carry when the grasp is what missed.

## What this does to the encounter

| | |
| --- | ---: |
| arm's steady-state error while following a moving script | **7.3 mm** |
| capture radius | **< 1 mm** |
| separation the arm reaches when servoed, no script | **0.002 mm** |

Seven-fold apart. **A script-following approach cannot produce a capture in this
scene**, at any script speed — 7.5 mm at 2 mm/step, 7.7 mm at 2.5, and the error
is the IK controller's, not the schedule's. Only servo-to-contact reaches the
radius.

So the encounter has to **arrive before it carries**: servo onto the object,
take hold, and only then run the burst schedule. That is what the probe does and
it is what produced the capture above.

## Retraction: the reset artefact

**Every contact number from the first two thirds of this session is withdrawn.**
The 51 mm, the 72 mm, the 36 mm, the 38 mm, and the `COLLISION` verdict in every
pilot cell were read across an environment reset.

`ManagerBasedRLEnv` auto-resets when an episode ends, which teleports the object
to a fresh spawn pose — one step, tens of millimetres, no contact involved. Both
scripts were discarding `terminated` and `truncated`. Measured once they were
recorded: `truncated: True` during the hold, at roughly 93 steps.

It killed three hypotheses that were each an explanation for the artefact:

| Hypothesis | How it died |
| --- | --- |
| The block is too big for the gripper | A **needle** — the object a PSM is built to hold — ejected at 38.1 mm against the block's 36.2. Two objects sharing neither size nor shape do not agree like that |
| 9.7 mm of misalignment is too much | Servoed with no script, the end effector reaches 0.002 mm. It closed there and the object still left |
| The jaws slam shut in one step | Held **open** at the arrival, the object travelled 35.1 mm — the same as closed — and the first six steps of the hold were exactly 0.0 mm |

The control that broke it open is the third: holding with the gripper *open*.
Four cases agreeing to within 2 mm — block and needle, open and closed — is not
something physics produces.

**The signal was there from the first GPU run and was read past.** Every pilot
cell returned `valid=False`, which `run_cell` sets exactly when the simulator
reports termination. It was attributed to the arm lagging.

### What survives the retraction

Everything measured before a truncation could occur, which is the approach phase:

- **The arm saturates near 3 mm/step** — median 3.27, p90 5.36 — and does not
  respond to the command. Doubling `--approach-speed` from 40 to 80 mm/step gave
  tracking identical to the millimetre. This refutes the claim in
  `orbit_lift_relation_cell.py` that the arm achieves "roughly a sixth of the
  commanded value", which could not have been checked on CPU.
- **Steady-state tracking error 7.3 mm**, unmoved by script speed.
- **Servo reaches 0.002 mm.**
- **The block settles 10.1 mm after reset**, identically regardless of the arm's
  path — which is why `--settle` exists and why `block_disturbed` fell to
  0.00004 mm once it did.

These are what motivated the rendezvous change, and they stand.

## Fixes this session, in order

| Change | What it was for |
| --- | --- |
| `--preroll` | The arm began a fixed 50.2 mm from the encounter's first point and was scored as though tracking. Converges in 16 steps |
| `--settle` | The block's own settling after reset was entering the geometry as a stale `target0` |
| `lateral_offset_scale=0` under `--grasp` | A grasp is a rendezvous; the ±6 mm offset belongs to the fly-by |
| close at closest approach | A radius is a knob; the arrival is an observable event |
| `--grasp-closing-steps` | The arrival test fired on step 1, because the first separation always improves on an infinite initial best |
| `episode_length_s` | The environment was ending every run at ~93 steps |

One change was made on a wrong diagnosis and reverted: an up-and-over pre-roll,
built on the theory that the arm was brushing the block. It reported the same
`block_disturbed` to eight decimal places, and cost all 80 pre-roll steps.

## What is still `PENDING`

The capture radius is now measured rather than assumed — **under 1 mm** — and
the preregistration should record it with this sweep beside it. Engagement,
`normal_alignment` and the observation noise still need the encounter rebuilt
around servo-to-contact, because no cell has yet produced a capture *through the
protocol*.

## Provenance

- `scripts/orbit_lift_grasp_probe.py` — the probe, and the radius sweep
- `scripts/orbit_lift_relation_cell.py` — the pilot cell
- `scripts/run_paper003_capture_pilot.sh`, and the
  [runbook](../../../../../docs/paper003/paper003_capture_pilot_runbook_v0.1.md)
- Grounds for the rendezvous change:
  [paper003_rendezvous_v0.1.md](../../../../../docs/paper003/paper003_rendezvous_v0.1.md)
