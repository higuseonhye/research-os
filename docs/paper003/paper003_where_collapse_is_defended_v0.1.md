# The collapse threat belongs to H2, not to the gate

> **Written 2026-08-05, before the change was measured.** Follows the finding
> that no constant-velocity ceiling can admit a capture while rejecting a
> sustained push. States where the defence actually lives, and closes the hole
> that removing the ceiling would otherwise open.

## What forced this

The gate's negative evidence refuses a relational claim where a constant-velocity
model already accounts for the motion. Measured across 40 seeds each:

| case | | min | median | max |
| --- | --- | ---: | ---: | ---: |
| capture / burst | admit | 0.756 | 0.779 | 0.796 |
| capture / probe | admit | 0.636 | 0.652 | 0.672 |
| **steady push** | reject | **0.252** | **0.415** | **0.636** |
| slide | reject | 0.985 | 0.987 | 1.000 |
| drift | reject | 1.000 | 1.000 | 1.000 |

**A captured target is more constant-velocity than a pushed one**, and the order
is inverted, so no ceiling separates them. The derivation rule anticipated this
and said to report it rather than pick a number from the range.

The reason is structural. A carried target rides *with* its carrier, so during a
burst its motion is exactly constant velocity. A pushed target sits at an
equilibrium separation and jitters. **The ceiling was calibrated when the
treatment was collision**, where contact is episodic and the target's motion
jumps; capture moved the treatment to the other side of the clause.

## The category error underneath

`slide` and the sustained push are described as controls for **H3, gate
specificity**. That is the wrong hypothesis for them.

H3 asks whether the gate can tell *the relation is present* from *the relation is
absent*. In `static`, `noise` and `drift` the relation is genuinely absent — the
target's motion has nothing to do with any body. The gate should refuse, and it
does.

In `slide` and in a sustained push **the relation is present**. Contact really
does cause the motion. What is true of them is something else: a *simpler
operator already suffices*. That is not a question about the gate's ability to
detect a relation. It is a question about which operator to choose, and choosing
the smallest sufficient operator is the program's own governing principle.

**So they are H2's controls, not H3's.** H2 already requires arm D to beat the
mode operator by a margin in every counted variant; where a constant-velocity
model suffices, arm C succeeds, the margin vanishes, and H2 fails. The defence
is in the scoring, measured on outcomes, and it does not depend on a threshold
being right.

The gate refusing them as well was belt-and-braces, and the braces are now
demonstrably mis-calibrated for this relation.

## Two changes

**1. Carriage evidence requires the carrier to be in contact.**

Removing the ceiling from the carriage path alone would let `drift` in: its
target runs along the first body's own axis at its own speed and agrees with it
on 0.71 of moving steps. But that body is **183 mm away** and never comes within
the interaction radius.

You cannot carry what you are not touching. Requiring the agreeing body to be
within the interaction radius during the riding run is the definition of
carrying rather than a tuned threshold, and `drift` fails it outright while a
capture passes it trivially.

**2. The constant-velocity ceiling applies to the proximity path only.**

Where it was derived, where it works, and where the treatment is episodic. The
carriage path keeps the contact requirement above as its negative evidence.

## What this gives up, stated plainly

The gate will now fire on a sustained push and on some slides — cases where a
relation is present and arm C is sufficient. **Arm D will act where it does not
need to.** That is a real cost and it shows up as engagement without advantage,
which the endpoint already reports as marginal-versus-conditional rates.

**Measured after the change, and the worry was mostly unfounded**: `slide` fires
on 0.05 of trials, still under H3's 0.10 ceiling, so the preregistered control
set is unaffected. `drift`, `static` and `noise` are at 0.00, and the treatment
at 1.00.

The only case that now fires and did not before is the **sustained push**, which
was never in H3's list - it could not be expressed until the `steady` schedule
was added today. So no preregistered hypothesis has to move for this change, and
the argument above stands as the reason the sustained push is *not* added to
H3's controls now that it can be run.

## What is untouched

`min_proximity_contrast`, `min_post_contact_far_deltas`, `min_carriage_run`,
`min_ride_steps`, the tolerance, and the commit window. The one-step
`cv_gain` replacement stands on its own grounds — a threshold should not change
meaning because the action's length changed — independently of where the clause
is applied.
