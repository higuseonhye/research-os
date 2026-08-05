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

## Where things stood

Everything else is committed and green: 244 tests, the arms and gate re-derived
at latency 8, the SELF comparison passing Case A a second time on fresh seeds
with the competitor scoring 0.045 and taking 8 discordant pairs.

The Isaac side owes the preregistration three numbers — engagement,
`normal_alignment`, observation noise — and cannot supply them until a cell can
be trusted to be a carry.
