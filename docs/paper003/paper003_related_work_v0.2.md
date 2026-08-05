# Paper 003 — Related work v0.2 (negative result)

> **Supersedes [`paper003_related_work_v0.1.md`](paper003_related_work_v0.1.md)
> as the positioning for the manuscript.** v0.1 positions a *positive* claim —
> "failure-triggered relational expansion, validated by capability threshold
> crossing" — and its §1–§3 remain correct and reusable as the relational
> world-model background. What it cannot do is position the paper we have, whose
> claim is a requirement set and a negative result. This document adds the three
> literatures that were not needed while the result was expected to be positive.
>
> **Citation status.** Every entry below is marked `✓` where the work is one I am
> confident exists with the attributes stated, and `?` where the attribution,
> year, or venue must be checked against the actual paper before submission.
> Nothing here should reach a bibliography unverified.

---

## The wedge, restated for a negative result

v0.1's wedge:

> Failure-triggered relational-adequacy testing, validated by achievable-task-space growth.

That is the wedge of the *design*, and it survives — the design is intact and
preregistered. The wedge of the **paper** is now:

> **What a missing-relation task family must supply, and a measured demonstration
> that a coupling built to be outside a mode operator is absorbed by it as soon
> as the carrier is a real actuator.** Three task-level requirements, each
> eliminating a candidate relation on measured grounds, plus one physical
> requirement on the manipulator — the carrier's settling time against its grip
> duration — that this scene fails by a factor of about seven.

Two things make it a contribution rather than a report of a failed experiment:

1. **The requirement set is checkable in advance.** Three of the four
   requirements cost nothing to evaluate before hardware is involved.
2. **The failure is a shortcut, not a null.** The relational task was solvable —
   the oracle arm lands 1.000 of physical cells — by a mechanism simpler than the
   one the benchmark names. That is a *shortcut-learning* result about a
   benchmark, and it has a literature.

---

## 4. Negative and null results in machine learning

The paper needs to establish that a negative result of this shape is publishable
and what form makes it so: a null that discriminates, not a null that is
uninformative about power.

| Work | Status | What it gives us |
| --- | :---: | --- |
| **"I Can't Believe It's Not Better" (ICBINB)**, NeurIPS workshop series | ✓ | The venue-level precedent for negative results with a diagnosed mechanism. Its framing — *why did the well-motivated method not work* — is exactly this paper's shape, and its standard is that the mechanism must be identified, not merely the failure reported |
| **ReScience C** | ✓ | Reproduction and non-reproduction as a first-class publication type |
| **"Deep Reinforcement Learning that Matters"**, Henderson et al., AAAI 2018 | ✓ | The canonical demonstration that apparently decisive comparisons in embodied RL turn on implementation and seed choice. Our discipline — rule locked before measurement, seeds declared, controls preregistered — answers the threats it identifies |
| **NeurIPS pre-registration experiment / workshop**, 2020–21 | ? venue details | Precedent for preregistered ML studies reporting whatever the locked rule returns |

**How we differ.** These establish *that* negative results belong and *what
methodology* makes them credible. None of them supplies a requirement set for a
task family. The transferable object here is the checklist, not the null.

**What we must state to meet their standard**, and do: the instrument would have
shown a positive result — the oracle arm lands 1.000, the gate engages at 0.27
under contact against 0.23 on CPU, and the same code produced a decisive positive
result under injected coupling on 200 preregistered cells.

---

## 5. Benchmark design, shortcuts, and controls that were not run

This is the closest literature to the actual finding, and v0.1 does not touch it.

| Work | Status | What it gives us |
| --- | :---: | --- |
| **"Shortcut Learning in Deep Neural Networks"**, Geirhos et al., *Nature Machine Intelligence* 2020 | ✓ | The direct analogue. A benchmark is not testing what it names if a simpler mechanism solves it. **Arm C is a shortcut for a relational task**: it never observes the second entity and lands 0.957–1.000 of cells. Their prescription — build the control that the shortcut would pass — is what arm C *is* in our design, and it fired |
| **"The Benchmark Lottery"**, Dehghani et al., 2021 | ✓ | Benchmark choice, not method quality, determines reported rankings. Our version is sharper and measurable: the *carrier's dynamics*, a detail no benchmark description would record, flips the ranking of two model classes from 146:8 to 0:4 |
| **"Are We Done With ImageNet?"**, Beyer et al., 2020 | ✓ | Re-examination of whether a benchmark's measurements mean what they are taken to mean |
| **"Are GANs Created Equal?"**, Lucic et al., NeurIPS 2018 | ✓ | Precedent for "the reported advantage does not survive a fair control" as a publishable finding |

**How we differ, and this is the contribution.** These works diagnose benchmarks
*after* the fact, from the outside. We report the control firing **inside a
preregistered design that named it in advance as the discriminating control** —
the preregistration states, before any physical cell was run, that "mode
expansion *matching* the relation arm falsifies the contribution over Paper 002".
The shortcut was anticipated, named, given an arm, and it won.

That is a methodological point worth making on its own: a design that cannot lose
to its own control has not tested anything.

---

## 6. The reality gap, and actuator dynamics specifically

The failure is not "sim is not real" — everything here is simulated. It is
narrower and, we think, more interesting: **an idealised carrier and a physically
actuated one differ in exactly the property the phenomenon depends on.**

| Work | Status | What it gives us |
| --- | :---: | --- |
| **"Noise and the Reality Gap"**, Jakobi, Husbands & Harvey, ECAL 1995 | ✓ | The origin of the term, and the framing that a controller can exploit properties of a simulation that do not survive embodiment |
| **"Sim-to-Real: Learning Agile Locomotion for Quadruped Robots"**, Tan et al., RSS 2018 | ✓ | **The most precisely relevant prior.** They find that modelling *actuator dynamics* is what closes the gap for locomotion. We find the mirror image: actuator dynamics do not merely degrade the phenomenon, they **delete** it — the intermittency the relation depends on is a property of an idealised actuator and vanishes at a settling time of 22 steps |
| **Domain randomization**, Tobin et al., IROS 2017 | ✓ | The standard response to the gap: randomise what you cannot model. Not available here — you cannot randomise your way to a carrier that stops, because the property needed is *shorter settling*, not *uncertain settling* |
| Sim-to-real surveys in robot learning, e.g. Zhao et al. 2020 | ? exact ref | Background |

**How we differ.** The reality-gap literature is overwhelmingly about *policies*
that fail to transfer. This is about a **task property** that fails to transfer:
the thing that made one model class necessary is itself an artefact of the
idealisation. A policy gap is fixed by better simulation; this one is not fixed
by better simulation, because the more faithful simulation is the one where the
phenomenon is absent.

---

## 7. Minimum sufficient model class (unchanged in substance, restated)

Paper 002's positioning carries over: model-order selection, MDL, and the
principle that the smallest sufficient change is the correct one. The new content
is that **the boundary between "missing mode" and "missing relation" sits further
out than the taxonomy assumes.** A constant-velocity operator absorbed a coupling
designed specifically to lie outside it, once the coupling was produced by
dynamics rather than by arithmetic.

That is a claim about the taxonomy the program is built on, and it belongs in the
Discussion rather than the Related Work — noted here so it is not lost.

---

## What v0.1 still supplies, and should be cited from

- **§1 Relational / graph-based world models** — NRI, interaction networks,
  factored world models. Still the correct background for "how relations are
  represented", and still not what this paper competes on.
- **§2 Compositional generalization** — still the right neighbour for the
  capability-space framing, which survives as the *design's* endpoint even though
  it was never tested.
- **§3 Capability-boundary framing** — unchanged.

Their positioning sentences need one edit each: they currently say what Paper 003
*will* show, and must say what it *set out to* show.

---

## Framing options for the venue

| Framing | Lead claim | Best fit |
| --- | --- | --- |
| **Benchmark critique** | A preregistered relational benchmark, and the control that solved it without the relation | Shortcut-learning and benchmark-design venues; workshop track |
| **Reality-gap** | Actuator dynamics delete the phenomenon a relational world model was built for | Robot-learning venues; pairs directly with Tan et al. |
| **Negative result with a checklist** | What a missing-relation task family requires, and why four candidates failed it | ICBINB-style venue |

**Recommendation: the second, with the first as the method section.** The
reality-gap framing has the sharpest single sentence — *the property that made
the relation necessary is an artefact of an idealised actuator* — and it is the
one a robot-learning reader can act on. The requirement set then arrives as the
constructive half rather than as a consolation.

## Version history

- **v0.2, 2026-08-05.** Repositioned for the negative result. Adds §4 negative
  results, §5 benchmark design and shortcuts, §6 the reality gap and actuator
  dynamics. v0.1's §1–§3 stand as background and are cited rather than repeated.
