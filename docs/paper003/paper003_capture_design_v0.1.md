# Three relations, and only one of them is the paper's

> **Design decision, 2026-08-04**, taken after measuring all three. Supersedes
> the collision coupling the Isaac line has been running, and rejects an
> intermediate proposal that looked right for an hour.

## The test that decides it

A **single-entity** model is added to the comparison: it sees no second body at
all and learns the burst pattern of the *target's own* trajectory. If it matches
the relational arm, the relation is not necessary and H2 fails, whatever else
the design achieves.

| Relation | B zero-order | C constant velocity | **SELF pattern** | D relation |
| --- | ---: | ---: | ---: | ---: |
| **Carriage** — target rides the reference | 0.00 | 0.25 | **1.00** | 1.00 |
| **Capture** — reference arrives, then carries | 0.33 | 0.36 | **0.33** | 0.50 |

Under carriage the single-entity model is **identical to the relational one**.
The intermittency that makes the task hard is written into the target's own
trajectory, so nothing needs to look at a second entity. H2 fails outright.

Under capture the single-entity model is **identical to zero-order**. Before the
capture the target is still, so its own history contains no information about
what is about to happen to it, and only the approaching body does.

## Why the three differ

| Design | Relation necessary | Effect exceeds tolerance |
| --- | :---: | :---: |
| Collision — struck and released | **yes** | no — self-limiting |
| Carriage — rides throughout | no | yes |
| **Capture — arrives, then carries** | **yes** | **yes** |

Collision fails on magnitude for a reason now measured five ways: the push moves
the target away, which reduces penetration, which reduces the push, so
displacement per contact is on the order of the interaction radius, and the
radius is below the placement tolerance
([the ceiling](paper003_displacement_ceiling_v0.1.md)).

Carriage fails on necessity because an accumulating effect leaves its own trace.

Capture has neither failure: the onset is invisible in the target's history, and
what follows accumulates without bound.

## The wrong turn this corrects

Carriage was recommended first, on the grounds that it restores the task's
original framing — `commitment_task.py` describes "a bread slice carried by an
intermittently nudged tray", and the 1-D proxy that put arm B in a 0.05–0.09
band was that model. The reasoning was that the Isaac line had silently
substituted collision for carriage and the ceiling was an artefact of the
substitution.

The first half of that is true. The conclusion was wrong, and the single-entity
model is what showed it. **A recommendation that survives an hour of reasoning
can still fail the first measurement aimed at it**, which is why the measurement
came before the implementation.

## What capture requires

**A two-phase relational prediction.** The quick proxy scored arm D at 0.50
against arm B's 0.33 by rolling the reference's pattern forward and applying it
to the target immediately — which is wrong before the capture, when the target
is not yet attached. A correct arm D predicts *when* the reference reaches the
target, and applies carriage only from that step. So 0.50 is a floor produced by
a deliberately crude model, not a ceiling on the design.

**A gate that fires on capture — which turned out to need nothing.**

> **Reversed later the same day. Everything from here to the end of this
> section is wrong.** The gate fires on capture at **0.00**, not 1.00, and has
> no post-contact far-field steps at all. The prediction below was correct and
> the measurement that overturned it was reading an off-by-one in
> `capture_displacement`: a captured target was thrown one body-step past its
> carrier, which put the riding separation outside the radius and sorted the
> pauses into the far field. The variant deleted for failing its own test was
> deleted against an artefact.
>
> What replaced it is neither the old claim nor that variant. The gate admits a
> second form of positive evidence — **carriage**, the target's displacement
> being a body's own — so one gate still covers both relations, but not by
> sharing this statistic. Capture fires at 1.00 through the new path.
> [The measurement](../../experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/capture_arms_v0.1/RESULTS.md)

The prediction here was that capture inverts the evidence. Under collision the
discriminating question is whether the target stops once the body leaves, so
evidence from before the first contact is discarded; under capture the body
never leaves, so there should be no post-contact far-field period and the gate
should abstain on every cell.

**Measured, it does not.** A carried target keeps a small separation from its
carrier, and the pauses supply far-field steps in any case: 20 usable deltas
rather than none. The same thresholds fire on capture at **1.00** and reject a
target moving on its own at **0.00**, which is exactly what a capture-specific
variant gave. That variant was written and then deleted rather than shipped on a
premise its own test contradicted.

One gate covers both relations.

### A control that was not one

The first control for capture had the target begin moving with the *same*
pattern at the *same* step the body arrived. That is not a different world: the
trajectories are identical and only the causal story differs, so no gate can
separate them and none should be claimed to. It fired at 1.00 with statistics
identical to capture, which is the correct behaviour and an uninformative test.

The controls now differ in onset and direction, and are rejected at 0.00.

## What is not settled

The commit window relative to the capture, the approach speed, and the duty
cycle are all unfixed. They must be set on grounds independent of which arm they
favour before any confirmatory run, and the numbers above are exploration.
