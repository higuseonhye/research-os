# Paper 003 — the two-body encounter, and what still blocks the endpoint

> **Design note, 2026-08-04. CPU proxy only, not preregistered, not run in Isaac.**
> Written after the [probe sweep](../../experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/isaac_probe_sweep_v0.2/RESULTS.md)
> showed arm B landing 0.90 on the treatment condition.

## The tension this resolves

Fixing the relation gate required the reference to **withdraw**: until the target
is observed after the reference leaves, a struck target and one still sliding
from an earlier strike are the same history. But the withdrawal is also what
leaves the target stationary at the commitment, and a stationary target is one
that zero-order predicts exactly.

Measured directly, with a single reference body:

| Encounter | Arm B | Displacement at commit | Gate fires | Commit | `estD` |
| --- | ---: | ---: | ---: | ---: | ---: |
| `burst` (advance only) | 0.55 | 16.4 mm | 36 | 26 | **0.00** |
| `probe` (with withdrawal) | 0.85 | 1.7 mm | 26 | 53 | 0.68 |

**Hard but unidentifiable, or identifiable but easy.** Sweeping the reference
speed from 4 to 80 mm/step and the coupling gain to 0.9 moved neither row; a
"probe once then pursue" schedule produced eligible cells in 8 of 40 seeds.

## The design

**Two bodies.** A *prober* contacts the target early and leaves for good. A
*pusher* arrives later and contacts during the dispense window.

At the commitment the target is **stationary** — the prober has gone, the pusher
has not arrived. So zero-order predicts no motion, and so does constant velocity.
Only a model that applies the observed relation *to a second body* predicts the
displacement.

That is a stronger test than the single-body version, which arm D could satisfy
by extrapolating one body's trajectory. Here the relation must generalise to an
instance it was not learned on.

Measured on the CPU proxy, 0.5 mm observation noise, ~90 cells per row:

| Coupling gain | Arm B | Arm C | Arm D | D\* | `estD` | Displacement |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.50 | 0.63 | 0.33 | **0.91** | 1.00 | 0.74 | 15.6 mm |
| 0.70 | 0.57 | 0.32 | **0.92** | 1.00 | 0.78 | 17.3 mm |
| 0.90 | 0.58 | 0.27 | **0.92** | 1.00 | 0.77 | 17.1 mm |

Arm D is clearly ahead, the coupling estimator fits in ~3 of 4 cells, and arm C
is *worse* than zero-order — it extrapolates the stationary target's noise.

## Eligibility, on arm-neutral grounds

A cell counts when **the pusher will enter the interaction radius early enough in
the dispense window for the contact to act**. Two things are being excluded, and
neither refers to any arm:

- Cells where no contact occurs during the action. The task is "commit before a
  contact that will displace the target"; with no contact, that task was not
  posed and every arm is trivially right.
- Cells where contact begins on the final step. The action completes before the
  displacement happens, so again the task was not posed.

The existing `motion_expected()` predicate does neither correctly. Measured
against ground truth it admits cells where the target does not move in **51%** of
cases under `burst` and **84%** under `probe` — it uses the instantaneous closing
rate as a proxy for future contact, which a schedule with reversals breaks.

## Two findings that change preregistered choices

### Reference speed does not grade difficulty

The draft grades the variant set `T` by reference speed. Measured, it does not
grade anything:

| Pusher speed (mm/step) | 10 | 15 | 20 | 25 | 30 | 40 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Arm B | 0.69 | 0.68 | 0.67 | 0.71 | 0.69 | 0.84 |
| Displacement (mm) | 10.6 | 12.5 | 12.6 | 13.0 | 11.8 | 12.7 |

Flat across a fourfold range. A faster body penetrates further per step but
spends fewer steps in contact, and the two offset. **A dimension that does not
grade cannot define a variant set**, and this is a statement about the
mechanism rather than about any arm's score.

Coupling gain grades weakly — displacement 10.5 → 17.2 mm from gain 0.3 to 0.85 —
and is the better candidate, but see below.

### Arm B never approaches zero, and the tolerance is why

Across every combination tried — both encounters, speeds from 4 to 80 mm/step,
gains from 0.3 to 0.95, and eligibility margins from 1 to 5 steps — **arm B lands
between 0.55 and 0.90**. It was never near zero.

The reason is structural. The coupling pushes the target *away*, which reduces
penetration, which reduces the push: it is self-limiting, and one pass displaces
the target by roughly 15 mm. The success tolerance is **20 mm**. A displacement
smaller than the tolerance means zero-order lands, whatever the arms do.

The CPU proxy that produced arm B in a 0.05–0.09 band did so at a **5 mm**
tolerance, on a scale the proxy chose arbitrarily. The 20 mm figure is inherited
from Paper 001/002.

**H1's capability-crossing endpoint is therefore not reachable at a 20 mm
tolerance with this coupling.** Either the displacement must be several times
larger, or the tolerance must be smaller.

## What this does not license

Choosing the tolerance so that arm B fails. That is selecting a parameter by
which arm it favours, and it is the move the preregistration exists to prevent.

The legitimate route is already open and was recorded this morning for an
independent reason: the scene reports `rigid_objects: []`, so real contact
requires **adding a body**, which forks the task family. A forked family does not
inherit its predecessor's tolerance — the 20 mm figure was established for a
scene this no longer is. The new tolerance must come from the new scene's own
geometry: the size of the object being placed and of the region it must land in.

Until that scene exists, the tolerance cannot be set, and until the tolerance is
set it cannot be known whether the capability-crossing endpoint is reachable at
all.

## Status

| Item | State |
| --- | --- |
| Two-body encounter | **implemented** in `relation_dynamics` and `commitment_episode`, 130 tests passing; not yet in the Isaac runner |
| `motion_expected()` | known-wrong under reversing schedules; needs the eligibility rule above |
| Variant grading dimension | speed shown non-functional; gain is the candidate |
| Placement tolerance | **blocking**, and cannot be set before the Branch B scene |
| H1 reachability | **unknown**, and downstream of the tolerance |

## Implemented 2026-08-04

The gate, the coupling estimator, `normal_alignment` and the projection now take
either one body or several. A single-body history is stored as a one-body list,
so nothing that passes one array changes behaviour — pinned by a test.

Three decisions the implementation forced:

**Every statistic follows the nearest body.** The interaction radius is smaller
than the separation the encounter keeps between bodies, so only the closest can
be in contact. Pooling all bodies would let a distant body's stillness dilute a
real contact.

**The projection follows the *acting* body, not the nearest one.** After the
prober leaves it can remain closer than the pusher for several steps while
having no further effect; rolling the prediction forward with it would predict a
contact that is over. The acting body is the one closing fastest, or one already
inside the radius — observable, and independent of any arm's model.

**A body that never pauses had to become predictable.** The pattern estimator
looked for a burst cycle and refused anything without a completed pause, so the
pusher — which sits still, then closes at constant speed — was unpredictable and
arm D could never act on it. It now falls back to constant motion, but only
after an unbroken run of at least twice the horizon. That threshold is what stops
the fallback reviving an older defect: a *bursting* body that has not paused yet
also shows no completed cycle, and predicting continuous motion for it is exactly
the error that once let a commitment land at step 7 of a 14-step cycle with arm D
silently degraded into arm B. At 10-on/4-off with a 6-step horizon, twelve
unbroken steps cannot occur.

Measured end to end through the real driver, 80 cells, 0.5 mm noise, gain 0.7:
**arm D 0.97, arm B 0.80, arm C 0.42**, gate firing in every cell and arm D
engaging in 0.89. Arm B is high here because the *old* eligibility predicate is
still in place and admits stationary cells; the corrected predicate above put it
at 0.57–0.63 in the standalone measurements.

A property worth stating rather than fixing: **if the second body pushes without
pause the target settles into a steady drift**, a constant-velocity model
explains it, and the gate declines — correctly, since that is arm C's case. The
commitment has to precede the sustained push, which is what the eligibility
window arranges. Pinned by a test.

## Eligibility, implemented 2026-08-04

`motion_expected()` now takes the bodies' positions over the dispense window,
**supplied by the harness**. That source matters: predicting the future instead
would route eligibility through arm D's pattern estimator and make it depend on
one arm's readiness, which is the coupling this design has had to undo three
times. The Isaac runner computes the schedule, so it knows the future exactly.

A cell is admitted when the target is already moving fast enough to leave
tolerance, or when a body occupies at least `min_contact_steps` of the window.
Two steps is the default, set from the structure of the action rather than any
arm's score: the placement lands at the end of the window, so a contact
beginning on the final step has no time to move anything.

Measured against ground truth over 80 two-body episodes:

| Eligibility rule | Admitted | Precision | B | C | D | Displacement |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| instantaneous proxy | 915 | 0.37 | 0.80 | 0.42 | 0.97 | 3.7 mm |
| future, ≥1 contact step | 757 | 0.45 | 0.77 | 0.27 | 0.99 | 7.5 mm |
| **future, ≥2 contact steps** | 673 | **0.51** | 0.76 | 0.25 | **0.99** | 7.6 mm |
| future, ≥4 contact steps | 514 | 0.57 | 0.75 | 0.17 | 0.98 | 8.7 mm |

Precision is the fraction of admitted cells where the target really moves beyond
tolerance. The old proxy was right about a third of the time; the corrected rule
about half. The instantaneous fallback is kept for single-body callers and
documented as the proxy it is.

**Arm B barely moves — 0.80 to 0.76 — and that is the expected result, not a
disappointment.** Even with perfect knowledge of the future and a guaranteed
two-step contact, the median displacement is 7.6 mm against a 20 mm tolerance.
The residual imprecision is the tolerance, not the predicate. This is the same
finding as above, arrived at from a different direction.

## The runner, 2026-08-04

The second body needed no scene construction at all: the reference bodies are
**moving points**, not rigid assets, so the runner computes their positions
analytically and hands them to the driver. A second analytic trajectory costs
nothing. `--bodies 2` now runs the encounter under Isaac with injected coupling.

That is a validation of the machinery, **not** progress on real contact.
Deliverable 2 stays unmet: the scene reports `rigid_objects: []`, so contact
physics still requires adding a body.

While doing it, all of the geometry moved out of the runner into
`wm_expansion/encounter.py` and under test. It had been inline in a file that
cannot be imported without a GPU — the surface that produced eight defects,
among them the fixed +x axis that turned ten seeds into one translation-invariant
encounter. The runner is now 426 lines and decides almost nothing; 19 tests cover
the schedules, the draw, and the body positions, including that adding a second
body leaves the first's trajectory untouched.

## What remains

1. **The placement tolerance**, which is blocking and needs the Branch B scene.
2. **The Branch B scene itself** — a rigid body in the environment, so that
   contact is simulated rather than injected. The orbit-surgical `lift` and
   `handover` task folders, which do have rigid objects, are **deliberately
   deleted by the bootstrap script** as "incompatible", with no record of why.
   Finding out is a two-minute check on the pod and is the cheapest next GPU
   action.

The tolerance moves every number here, so it should settle before any figure
from (2) is treated as more than a smoke test.
