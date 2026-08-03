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
| Two-body encounter | designed and measured on CPU; **not implemented** in the episode driver or the Isaac runner |
| `motion_expected()` | known-wrong under reversing schedules; needs the eligibility rule above |
| Variant grading dimension | speed shown non-functional; gain is the candidate |
| Placement tolerance | **blocking**, and cannot be set before the Branch B scene |
| H1 reachability | **unknown**, and downstream of the tolerance |

The next implementation step is the two-body support in `commitment_episode.py`
and `relation_dynamics.py` — the gate, the estimator and the projection all
currently assume a single reference. That is CPU work with test coverage. It
should not begin before the tolerance question is settled, because a tolerance
change moves every number above.
