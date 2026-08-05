# Two numbers the scene decides, and the rule for reading them off it

> **Written 2026-08-05, before the measurements it specifies.** The rules are
> here first so that the values cannot be said to have chosen them. This is the
> same order the SELF arm comparison used.

## Why this exists

The first capture produced *through the protocol* also produced two failures,
and neither is a defect in the code:

```text
eligible_steps []          no step was ever worth committing at
cv_gain 0.748              the carry is constant velocity; the gate refuses
```

Both come from parameters that were never derived from anything. They were
carried over from a CPU proxy where the spatial and temporal scale was
arbitrary, and the physical scene has now contradicted them.

## 1. `dispense_latency` — from the tolerance and the carry speed

The eligibility screen asks whether the target will leave tolerance during the
dispense. Measured in the cell:

```text
carry 157.51 mm over 111 riding steps   =  1.42 mm/step
1.42 mm/step x 6 steps                  =  8.5 mm
placement tolerance                     =  20 mm
```

The target does not leave tolerance, so **arm B succeeds by aiming where the
target already is** and the cell poses no prediction problem at all. That is
what an empty `eligible_steps` means, and the screen was right to refuse.

Raising the carry speed cannot fix it. The arm saturates near 3 mm/step and does
not respond to the command — 40 and 80 mm/step of commanded approach gave
tracking identical to the millimetre.

**Rule.** With the tolerance fixed and the carry speed a physical limit, the
latency is their quotient rather than a choice:

```text
dispense_latency  >  tolerance / achievable_carry_speed
```

Both inputs are fixed independently of it, and neither mentions an arm:

- **tolerance, 20 mm** — inherited from the task family's own
  `mdp/terminations.py`, fixed long before Paper 003 existed. It does not move.
- **achievable carry speed** — a property of this arm holding this object, to be
  **measured** by sweeping the commanded carry and recording what the block
  actually does, not assumed from the unloaded figure.

The value is then the quotient rounded up, with **no margin added** — a margin
would be the one free parameter in the derivation and there is no ground for
choosing its size.

### Which carry speed, since it varies by cell

An omission in the first draft of this rule, closed here **before the
distribution was looked at**: "the achievable carry speed" is not one number,
and the statistic chosen changes the answer.

**The tenth percentile across at least twenty seeds.** Not the median.

The eligibility screen exists to discard cells where the target never leaves
tolerance and every arm is trivially right. A latency set from the median makes
the task non-trivial in about half the cells and throws the rest away; set from
a low percentile, nearly every cell poses the problem the design is about.

This is not a thumb on the scale. **Whether a cell is posed at all is arm-blind**
— it decides that a prediction problem exists, not who solves it — and the
screen's own definition already says as much: where the target will not move,
"every arm is trivially right and committing there measures nothing".

The tenth rather than the first percentile because the first is a single draw
at twenty seeds and would be reading noise.

### Corrected 2026-08-05: measure the displacement, not a speed

The quotient rule above is wrong, and arm B is what showed it. At the latency it
derived, **arm B lands 0.58 of the time** — a comparator that aims where the
target already is should be near zero if the task is posed at all.

The arithmetic said otherwise: 2.946 mm/step × 7 steps = 20.6 mm against a 20 mm
tolerance. But that "speed" is the block's travel divided by its **riding**
steps, and a dispense window contains pauses as well. Under a burst schedule the
target stands still for part of every window, so the displacement over a window
is smaller than speed × latency, and the tolerance is not cleared.

**The intermediate quantity was the mistake.** The eligibility screen asks how
far the target moves over one window; a speed measured on riding steps alone
cannot answer that, because it has divided the pauses out.

So the displacement is measured directly:

> `dispense_latency` is the smallest **L** for which the tenth percentile of the
> target's **L-step displacement** exceeds the tolerance.

The tolerance is inherited and fixed. The displacement is read from the traces.
The tenth percentile is the statistic already fixed above, for the reason
already given. And there is now **no speed in the derivation at all** — which is
where the pauses were being lost.

## 2. `interaction_radius` — from where taking hold actually happens

`contact_arrivals` anchors the commit window on a body crossing
`interaction_radius`, currently 12 mm. In this cell that fired at step 10, the
gripper took hold at step 23, and the target first moved at step 27.

**Seventeen steps between the anchor and the event it is supposed to anchor.**
Under collision the two coincide, because contact and effect are the same
instant. Under a capture they do not: the arm decelerates as it closes, and the
last twelve millimetres take longer than the first hundred.

The 12 mm was never measured. Its comment says "observed contact in this scene
is 2-5 mm", which was a guess about contact, and the quantity that matters is
where the relation *takes hold* — measured in the radius sweep at **under 1 mm**.

**Rule.** `interaction_radius`, in a physical scene, is the separation at which
the relation takes hold, measured. Not a contact distance, not a guess, and not
a value that may be moved to bring the anchor and the arrival closer together.

The servo note left this open and said it would be settled by measurement rather
than by choice. This is that settlement.

### Which separation, since capture degrades rather than stopping

The same omission as the carry speed's, closed the same way and **before the gap
was measured**: capture does not fail at a sharp boundary, so "the separation at
which it takes hold" needs a statistic.

**The largest separation at which capture still holds in a majority of cells**,
six seeds each. Not the value with a perfect record - that is 0.8 mm, which is
where the grasp is *best*, not where the relation ends - and not the largest
tested, which would measure the sweep grid rather than the scene.

Measured:

| separation | 0.8 | 1.2 | 1.6 | 2.0 | **2.5** | 3.0 | 3.5 | 4.0 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| held and carried | 6/6 | 4/6 | 4/6 | 5/6 | **4/6** | 2/6 | 0/6 | 0/6 |

So **`interaction_radius` = 2.5 mm**, replacing a guessed 12 mm whose comment
said "observed contact in this scene is 2-5 mm" and which fired the commit
window's anchor seventeen steps before the grasp it anchors.

A first attempt took the ninetieth percentile of the separations at which held
cells had closed. That was circular - those separations are the sweep's own grid
- and it is recorded because the number it produced, 1.84 mm, looked perfectly
reasonable.

### One check does not survive the change

`EncounterSpec.validate` refuses a body advancing further per step than the
radius, because a scripted fly-by would then step over its own contact zone
between observations. The carry runs at 3 mm/step against a 2.5 mm radius, so it
would be refused.

**That check belongs to collisions.** A servo has no crossing to miss: it
decelerates as it closes, and the grasp fires on the observed separation rather
than on the schedule. Once held, the object travels with the body at whatever
speed the body travels. The check is now scoped to scripted approaches, and a
scripted encounter is still refused exactly as before.

## The derived latency is 9, and it narrows the design to one body

Measured over 24 physical capture cells, windows taken inside the carry:

| L | 6 | 7 | 8 | **9** | 10 |
| --- | ---: | ---: | ---: | ---: | ---: |
| p10 displacement | 12.79 | 15.40 | 17.92 | **20.79** | 23.50 mm |

Nine is the smallest that clears the 20 mm tolerance, and the curve is smooth
with no sign of the contaminated-population flatness that two earlier attempts
produced.

A window of ±9 is 18 steps, and the carry runs 54 steps at the median, so for
the first time **the commit window fits inside the relation**.

### What it costs: the two-body encounter

At this latency two-body cells stop resolving — `static` at 0.00 and `coupled`
at 0.33, while every one-body condition stays at 1.00.

It is not a new breakage. Measured at latency 8, `static` with two bodies had
**one** eligible step in eighty, and a cell with a single eligible step is
degenerate anyway: the commit policy has nothing to choose between. The two-body
encounter has no real overlap between the steps where the pattern estimator can
project and the steps where the target will move, and the rising latency only
made that visible.

**So the design is one-body.** Nothing the paper runs depends on the two-body
encounter: it is separately retired for capture, where the first body to arrive
consumes the target, and its transfer claim — applying the relation to a body it
was not learned on — was already given up with onset prediction. Collision keeps
it, and collision is not the paper's relation.

## What follows, and what it costs

Both values feed the commit window, which is one dispense-length either side of
the arrival. Changing the latency changes the window, and the window defines the
band the SELF arm comparison was preregistered in.

**So the SELF comparison must be re-run.** Its preregistration anticipated
exactly this:

> Any of these may be *proposed* after the run, and if so the proposal is
> recorded here with the result that prompted it, and it applies to a future run
> on fresh seeds — never to this one.

That is what this is. The Case A result stands as what it was: a comparison at
`dispense_latency = 6`, on seeds 300-922, which is now known to describe a task
the physical scene cannot pose. The re-run is a new comparison, on seeds
disjoint from those, under the same decision rule with the band recomputed from
the new latency. **The rule itself - the arm's definition, its ungated
asymmetry, α, the margin, n - does not change.** Only the band moves, and it
moves because the window moved, not because anyone looked at a result.

Every other CPU result derived at latency 6 - the arm scores, the +30 bound -
is re-derived rather than carried over.

## What is not derived this way

The tolerance, the commit window's *form* (one dispense-length, symmetric),
`min_carriage_run`, `min_ride_steps`, and the gate thresholds. Those are fixed
on the structure of the action, the collision equilibrium, and prior work, and
none of them is touched here. A physical measurement licenses a physical
parameter; it does not license reopening the design.
