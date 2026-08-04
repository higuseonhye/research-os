# The capture onset is not predictable, and that is the answer

> **Negative result, 2026-08-04.** Settles open items 5 and 7 together, and
> retroactively justifies a boundary that had been recorded as a limitation.
> Measured on CPU, but the argument is about what is observable rather than
> about any estimator.

## What was being attempted

Two open items pointed at the same build. The two-body encounter does not
survive the change of relation — under capture the first body to arrive
consumes the target, so "demonstrate the relation on one body, apply it with
another" has nothing left to apply to. The chosen repair was a **decoy**: a
third object the prober captures and carries off, so that arm D learns the
capture radius from one object pair and applies it to another.

That design comes in two versions, and the difference is whether arm D may act
**before** the target is captured:

- **Weak.** The decoy supplies the capture radius; arm D still waits for the
  target's own carriage before acting.
- **Strong.** The demonstration licenses arm D to predict the *onset* — to
  commit before anything has happened to the target, on the strength of a body
  approaching it. This is the capability claim the paper wants, and it is what
  would close the gap between the commit window and arm D's readiness.

The strong version was chosen. It is not available.

## Why not

For arm D to predict the onset it must distinguish an approach that will
capture from one that will not. Measured across 40 seeds per condition, one
body, burst schedule, capture radius 50 mm:

| Condition | Captures the target | Body's closest approach | Within the radius |
| --- | :---: | ---: | ---: |
| `coupled` | **yes** | 42 mm | 1.00 of cells |
| `static` | no | **12 mm** | **1.00 of cells** |
| `noise` | no | **14 mm** | **1.00 of cells** |
| `slide` | struck, not held | 44 mm | 1.00 of cells |
| `drift` | no | 183 mm | 0.00 of cells |

**`static` and `noise` are worlds where a body arrives at the target and
nothing happens** — and it arrives *closer* than in the treatment. Up to the
moment of contact, a capturing approach and a non-capturing one are the same
observation. There is no statistic over the approach that separates them,
because the difference is a counterfactual about what contact will do, and
contact has not happened yet.

The decoy does not rescue this. To be evidence about the relation rather than a
label for the treatment cell, the demonstration has to be present in every
condition — otherwise arm D is reading "is this the treatment?" and not "is the
relation here". Present in every condition, it licenses arm D to predict a
capture in `static` and `noise` too, where it misses.

Arm D scores **1.00 on `static`** and 0.47 on `noise` today, by aiming where the
target already is. The strong version drives both toward zero. That is H4 —
*the relational operator does not regress where the relation is absent* —
failing, in exchange for a capability the world does not offer.

## What this settles

**Open item 5 is not a defect.** The commit window runs to ±6 around the
arrival and arm D cannot act before +4, so 3 of 13 window steps are usable. That
was recorded as an unresolved tension between two independently-fixed
quantities. It is neither a tension nor tunable: **there is nothing to act on
before the capture**, so an arm that declined there was correct, and an arm that
acted would be guessing. The measured boundary is the right answer rather than a
cost.

**Open item 7 has no build.** The two-body encounter exists to show a relation
applied to a body it was not learned on. Under capture the strong form of that
is impossible for the reason above, and the weak form buys very little: arm D
already recovers the radius from the target's own carriage by +4, and the gate's
own carriage evidence needs a run of 3 regardless, so a decoy-supplied radius
moves the usable band by a step or two at most. The two-body encounter is
retired for this relation rather than redrawn.

## What the paper can still claim, unchanged

Everything already measured. The relation is necessary and sufficient in the
regime where it applies: at commit offsets +4 to +6, arm D scores 0.53 to 0.71
against 0.00 for parameter repair, ≤ 0.07 for the mode operator, and **0.000 for
the single-entity arm** on the preregistered 200-cell comparison.

What it may not claim is onset prediction. The honest statement of the
capability is:

> Once a relation has taken hold, a prepared relation module predicts where the
> target is going when no model of the target alone can. It does not predict
> that the relation is about to take hold, and in this world nothing could.

## What this costs, stated plainly

The paper's capability window is **narrower than the design intended**. The
relation pays over a three-step band, not over the whole encounter, and the
reason is a property of the task rather than of the operator. A reader is
entitled to ask whether a three-step band is a capability opening or a
curiosity, and the answer has to come from the confirmatory sample and from
whether the band survives real contact — not from this document.

## Provenance

- Approach measurements: 40 seeds per condition, `EncounterSpec(bodies=1,
  schedule="burst")`, `CellSpec(coupling="capture")`
- Arm rates: [capture_arms_v0.1](../../experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/capture_arms_v0.1/RESULTS.md)
- SELF comparison: [self_arm_v1.0](../../experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/self_arm_v1.0/RESULTS.md)
