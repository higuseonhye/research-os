# The constant-velocity ceiling was measuring the horizon as well as the motion

> **Written 2026-08-05, before the replacement was measured.** States the defect,
> the fix, and **the rule for re-deriving the threshold**, so that the value
> cannot be said to have chosen the rule.

## The defect

`cv_gain` is the gate's negative evidence: a relational claim is refused where a
constant-velocity model already accounts for the motion, which is what keeps
Paper 003 from collapsing into Paper 002. The ceiling is 0.30.

On a steadily-closing pusher — the control built for exactly this clause — the
statistic decays monotonically with the horizon:

| horizon | 4 | 5 | 6 | **7** | **8** | 10 | 12 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `cv_gain` | +0.577 | +0.490 | +0.406 | +0.314 | **+0.219** | +0.014 | −0.191 |

**It crosses the ceiling between 7 and 8 while the motion is unchanged.** The
same trajectory reads as "a constant-velocity model explains this" at horizon 6
and "it does not" at horizon 8.

The cause is in the statistic. It takes the last one-step velocity and
extrapolates it `horizon` steps, then compares that error to zero-order's. On
any curving trajectory a longer extrapolation overshoots further, so the
constant-velocity model looks worse the further ahead it is asked, and the
number falls. Two different things are being measured at once: whether the
motion is smooth, and how far ahead the question was asked.

The threshold was calibrated at horizon 6 and inherits that horizon silently.
That was invisible while `dispense_latency` never moved.

## Why it surfaced now

The physical scene forces `dispense_latency` to 8 — the block carries at
2.86 mm/step at the tenth percentile, so six steps move it 17 mm against a 20 mm
tolerance and the task is trivial.
[The derivation](paper003_derived_from_physics_v0.1.md)

So a parameter fixed by physics and a threshold calibrated at a different value
of it came into conflict. **Neither is wrong; the statistic is.** A threshold
should not change meaning because an unrelated parameter moved.

## The replacement

Ask the same question one step ahead:

```text
cv_gain = 1 - mean|x(i+1) - (x(i) + v(i))| / mean|x(i+1) - x(i)|
```

How much of the next step's motion does a constant-velocity model remove,
against zero-order. The horizon does not appear, so it cannot leak in.

The meaning is preserved: high where motion is smooth and persistent, near zero
or negative where it is intermittent or reverses, which is what the clause has
always been for.

## The rule for the new threshold, fixed here

The old 0.30 does not transfer — a different statistic needs its own value, and
carrying the number across would be the mistake this document is about.

**The threshold is derived the way `min_proximity_contrast` was**, and that
precedent is explicit in the code: *"Every value from 0.30 to 0.90 separates the
treatment from all three controls identically... 0.50 sits in the middle of the
plateau."*

So:

1. Measure the new statistic on the **treatment** and on every control —
   `drift`, `slide`, `static`, `noise` — across a range of horizons, on CPU.
2. Find the interval of thresholds that separates treatment from controls
   **identically**, if one exists.
3. Take the **midpoint of that plateau**.
4. Confirm the separation is **the same at every horizon tested**. If it is not,
   the replacement has failed at the thing it was written for and must be said
   to have failed.

No value is chosen by looking at which one lets a result through. If no plateau
exists, that is reported rather than resolved by picking a number from the
range.

## What is not licensed by this

The other gate thresholds, `min_proximity_contrast` and
`min_post_contact_far_deltas` and `min_carriage_run`, are untouched. The
tolerance, the commit window's form, and `min_ride_steps` are untouched. This
replaces one statistic that was measuring the wrong thing and re-derives one
threshold that belonged to it, and the preregistration's list of tuning that
will not be done holds in full.

Every result derived with the old statistic is re-derived, not carried over.
