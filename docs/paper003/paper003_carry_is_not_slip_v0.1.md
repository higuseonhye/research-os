# A carry keeps its distance; the statistic only checked its steps

> **Open finding, 2026-08-05. Nothing is fixed yet.** Written at the end of a
> session so the next one starts from it rather than rediscovering it. It
> invalidates results recorded earlier the same day, including "24 of 24 cells
> produced a capture".

## What was seen

In the Isaac pilot at the derived latency and radius, every cell was verdicted
`CAPTURE` and arm D never once acted. The gate was refusing, and the refusal was
traced to the contact requirement on the carriage path — the agreeing body was
not within the interaction radius.

That looked like the requirement being too tight. It is not. Measured:

| | grasp closed at | post-grasp separation, median |
| --- | ---: | ---: |
| seed 300 | 0.65 mm | 3.35 mm |
| seed 301 | 0.67 mm | **49.83 mm** |
| seed 302 | 0.77 mm | **62.85 mm** |
| seed 303 | 0.64 mm | **54.88 mm** |
| seed 304 | 0.75 mm | **177.75 mm** |

**The object is not being held.** The arm and the object drift tens to hundreds
of millimetres apart after the grasp.

## Why the statistic said otherwise

`_ride_mask` compares **per-step displacement vectors** and admits a mismatch of
up to `agreement` — 25% — of the target's own step. At roughly 3 mm/step that is
0.75 mm per step of permitted disagreement, and **sixty steps of it integrates
to forty-five millimetres**.

So a target that moves *almost* with the arm, every step, and steadily falls
behind, scores 0.98 agreement over a run of 111. That is slipping, not carrying.

The gate was right and the verdict was wrong. The contact requirement added
earlier the same day is the only thing that checked the accumulated quantity,
and it caught exactly what it was written to catch.

## The shape of the defect

The same shape as three others found today: **a statistic that is correct
locally and wrong when integrated.** `cv_gain` measured the horizon along with
the motion; the pre-roll fixed `max` error while the median was a different
quantity; the capture-radius p90 measured the sweep's own grid.

Carrying is a statement about *relative position being maintained*. Per-step
agreement is a local proxy for it, and the proxy does not imply the thing.

## What this invalidates

- Every `VERDICT CAPTURE` in `results/pilot_lat8`
- **"24 of 24 cells produced a capture"** in the carry-speed measurement, which
  used the same statistic — and therefore, possibly, the carry speed of
  2.86 mm/step derived from it, which is what set `dispense_latency` to 8
- Any `held_and_carried` from the grasp probe, though its carry is 60 steps
  rather than 111 and it may be less affected

The capture *does* happen — the probe held an object with 0.25 mm of disturbance
and carried it. What is in question is how many of the cells scored as captures
were carries rather than slips, and for how long they held.

## What the fix has to be

`carriage_evidence` and `capture_verdict` must require the separation to stay
bounded through the riding run, not merely the steps to agree. The gate already
does this via contact; the verdict and the evidence statistic have to follow it,
not the other way round.

## Decided 2026-08-05, before re-measuring: the measured capture radius

Of the three candidates, this one **introduces no new parameter**, which the
others do. The grasp separation needs a tolerance band around it; a fraction of
the total carry needs the fraction, and would call 20 mm of drift over a 200 mm
carry a success.

More to the point, it is not really a choice. `capture_verdict` was trusted for
one reason, stated in its own docstring: it decides "with the same statistics the
gate and arm D use, not with a separate rule invented for the pilot". That
property had quietly broken — the gate called `carriage_evidence` with the
radius and the verdict called it without — and the verdict then certified
exactly the cells the gate was refusing. **Restoring the invariant is the fix;
the radius was already fixed by measurement at 2.5 mm.**

### Where the bound had to go

Three attempts, and the first two moved numbers without moving the verdict:

1. Passing the radius to `carriage_evidence` from the verdict changed only the
   *reported* agreement. The verdict branches on `estimate_capture`, not on
   that number.
2. Passing it to `estimate_capture` too was still not enough. It finds the
   *first* run of three agreeing steps, and the first three steps after a grasp
   are inside the radius however badly the carry later comes apart.
3. It belongs in `_ride_mask`, which all three callers share, **and in what
   `held` means.** Held is a statement about now: an object the carrier has
   drifted away from is not held, however well each individual step agreed. The
   verdict now requires it.

The first two are recorded because each looked like the fix and neither was.

## Second attempt: the bound was the wrong kind

The first fix bounded the separation by the capture radius, and that is wrong in
a way the data showed immediately. A carry means the separation is **bounded**,
not that it is **small**. Measured over eight cells, one held at a perfectly
constant 3.35 mm — drift +0.004 mm/step, flat to three decimals — and the 2.5 mm
radius rejected it. `ee_frame` is a virtual point between the jaws, so an object
genuinely held sits a few millimetres from it by construction.

The other seven drifted at 0.44 to 1.23 mm/step, out to 68–209 mm. Those are
slips and the first fix was right about them. **Both kinds are present**, and a
test that cannot tell a constant 3.35 mm from a growing one is not measuring
carrying.

### The statistic, from the principle rather than from those eight cells

A carried object inherits its carrier's displacement. Inherit all of it and the
separation is constant; inherit a fraction and the rest becomes separation. So
the quantity is **the share of the carrier's motion the target failed to
inherit**, over the run:

```text
slip = (separation at the end − smallest separation in the run)
       / (distance the carrier travelled over the run)
```

Dimensionless and free of scale: 0 is a perfect carry, 1 is an object left
where it was. The baseline is the run's own minimum rather than its first step,
which skips the settling just after a grasp without introducing a number for how
many steps that takes.

**The bound is `agreement`, which already exists.** It declares that a mismatch
of up to a quarter of the target's step still counts as riding. The defect was
never that quarter — it was that a *per-step* allowance accumulated without
limit. The same quarter applied to the *run* is a bound, and no parameter is
added.

### This has to be confirmed on cells I have not seen

The eight cells above were examined before the statistic was written, so the
statistic is not independent of them however carefully it was derived from
principle. **It is validated on fresh seeds**, and if it disagrees there, the
disagreement is the result.

## Third position, and the one that holds: three questions were being conflated

The statistic above does not survive its own first test, and the reason is that
the whole line of reasoning was answering the wrong question.

A synthetic slip of 2 mm per step against a 15 mm/step carry is 13% — inside the
`agreement` bound the statistic proposed. Tightening the bound until it fails
would have caught it, and would also have caught real Isaac cells slipping at
14%, which is where the question should have been asked instead: **is a cell
that slips 14% unusable?**

It is not. Arm D predicts the target by rolling the carrier forward. A target
inheriting 86% of its carrier's motion is mispredicted by 14% of what the
carrier travels over one dispense window — about **3.6 mm against a 20 mm
tolerance**. Arm D still lands.

Three questions had been collapsed into one:

| | answered by |
| --- | --- |
| Is this trace a capture — still, then riding, effect accumulating? | the **verdict** |
| Can arm D predict it? | the **scoring** |
| Should the gate let arm D act? | the **gate** |

The verdict was built for the first. The contact bound was added while thinking
about the third. The slip discussion was really about the second — and the
second is *measured*, not asserted in advance.

**By the design's own definition a slipping carry is a capture.** Capture names
two properties: the target is perfectly still before the arrival, and the effect
then accumulates without bound. A target inheriting 86% of its carrier's motion
has both, and travels 157 mm doing it.

### So what was actually wrong

Only one thing, and it was in the gate: the contact requirement was applied **at
every step**. An object genuinely held sits a few millimetres from `ee_frame`,
which is a virtual point between the jaws, so per-step contact rejects real
carries — including the one cell holding at a constant 3.35 mm.

Required **once in a run**, it does the job it was added for: `drift` agrees
with its body step for step, has zero slip, and never comes within 183 mm of
it, so it has no moment of contact anywhere in the run.

Measured after the change, on CPU: treatment 1.00, `drift`, `static` and `noise`
0.00, `slide` 0.05 — still under H3's ceiling. And the earlier "24 of 24
captures" stands after all.

### What this episode cost, recorded

Three positions in one afternoon on the same question, and the middle one was
wrong in both directions — it rejected real carries while being too loose to
catch the synthetic slip it was written for. The tests hold all three, because
each looked right at the time and the next person will reach for them in the
same order.

## Where things stood

Everything else is committed and green: 244 tests, the arms and gate re-derived
at latency 8, the SELF comparison passing Case A a second time on fresh seeds
with the competitor scoring 0.045 and taking 8 discordant pairs.

The Isaac side owes the preregistration three numbers — engagement,
`normal_alignment`, observation noise — and cannot supply them until a cell can
be trusted to be a carry.
