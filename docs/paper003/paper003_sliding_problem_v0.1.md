# Paper 003 — a struck object slides, and that is arm C's case

> **Reversed the same day by measurement.** The gate was run on real contact
> traces and fires on every trace containing a strike, with `cv_gain` negative
> throughout — a constant-velocity model is *worse* than zero-order on this
> motion. See
> [real_contact_gate_v0.1](../../experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/real_contact_gate_v0.1/RESULTS.md).
>
> The reasoning below is kept because the toy model and the retention statistic
> were built here, and because the failure is instructive: retention describes
> one coast in isolation, while the gate reads the whole episode. **The proxy
> was not the gate, and should not have been read as it.**

> **Finding, 2026-08-04. CPU, toy contact physics, not Isaac.** The most
> consequential result of the design work so far, and it threatens the paper's
> premise rather than supporting it.

## What was run

The cell loop now takes the target's pose from a `World` rather than computing
it. Two implementations share every other line — the gate, the arms, the
eligibility screen, the scoring:

- `InjectedWorld` — the target moves by formula and the simulator is told where
  it is. Every pilot so far.
- `ContactWorld` — the pushing bodies are commanded, physics is stepped, and the
  object's pose is **read back**.

`ContactWorld` was driven by a toy rigid body with momentum and friction: an
approaching body imparts an impulse along the contact normal, and the object
then coasts, decelerating by a friction coefficient. Twenty seeds per setting.

## The result

| Friction | B | C | **D** | D\* | Gate | `estD` | Displacement |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| μ = 0.35 | 0.85 | 0.25 | 0.85 | 1.00 | **0.00** | 0.00 | 16.8 mm |
| μ = 0.15 (slippery) | **0.15** | 0.30 | 0.15 | 1.00 | **0.00** | 0.00 | 39.6 mm |
| μ = 0.60 (stops fast) | 0.80 | 0.20 | 0.80 | 1.00 | 0.31 | 0.05 | 6.5 mm |

Two things at once, and they pull in opposite directions.

**Real contact makes the task hard, which is what was wanted.** At μ = 0.15 the
object is displaced 39.6 mm against the 20 mm tolerance and arm B falls to
**0.15** — the near-zero band the injected coupling could never produce at any
speed or gain.

**And the gate never fires.** `estD` is 0.00, so arm D falls back to arm B in
every cell and the two are identical by construction. The operator the paper is
about never acts.

## Why, and why it was predicted

A struck object **slides**. Motion therefore continues while the bodies are far
away, `proximity_contrast` collapses, and a constant-velocity model explains a
good part of what happens. That is precisely the `slide` control — the condition
added specifically because it "is what real rigid-body contact produces: struck
objects slide" — and the gate declines it correctly.

The gate is not malfunctioning. It is reporting that under real contact the
residual is substantially constant-velocity, which is Paper 002's operator.

The injected coupling never showed this because it is effectively μ = 1.0: the
target stops the instant contact ends. The whole pilot series has been run in a
regime that does not exist in a physics engine.

## The question this reduces to

**How fast does a struck block stop on the lift task's table?**

The μ = 0.60 row is the clue: when the object stops within a step or two, the
gate recovers to 0.31 and the encounter starts to look like the injected case.
Below that it does not.

This is now a measurement, not a design argument. It is answered by striking the
object in `Isaac-Lift-Block-PSM-IK-Rel-Play-v0` and recording how many steps its
velocity takes to reach zero, against the 6-step dispense window.

## What follows either way

**If the object stops quickly** — one or two steps — the relation is
proximity-conditioned in the sense the gate requires, and the design stands with
real contact substituted for the formula.

**If it slides** — several steps — then the residual genuinely is part relation
and part constant velocity, and the honest options are:

1. Change the endpoint. The claim becomes about a *composite* residual that
   neither operator alone handles, which is a weaker but true statement.
2. Change the task so the object cannot slide — constrained, or struck into a
   detent. That is a design change requiring an arm-neutral justification, and
   "so that arm D can act" is not one.
3. Report that the relational operator does not survive real contact in this
   task family. A negative result, and a publishable one given the operator is
   Paper 002's own and the comparison is prepared.

**None of these may be chosen by seeing which arm they favour.** The measurement
comes first.

## How it is measured

`wm_expansion/stopping.py` takes a pose trace and the separation to the nearest
body at each step, and reports when contact last occurred, how many steps the
object then coasted, the per-step speed retention, and how far it travelled
afterwards. All of it is under test, including the ways it could be quietly
wrong: a trace with no strike, a strike that moved nothing, and contact running
to the end of the recording are each refused rather than reported as a stopping
time of zero.

It also emits a one-line `gate_outlook`, deliberately coarse and deliberately
not a pass/fail, so a run states its own implication instead of leaving a number
to be interpreted later — when the interpretation could be chosen.

`scripts/orbit_lift_stopping_probe.py` is the Isaac side: drive the end effector
into the block, retreat, hold still, record poses. It has never been run.

```bash
/workspace/IsaacLab/isaaclab.sh -p scripts/orbit_lift_stopping_probe.py     --headless --seed 300 --out-dir results/paper003_stopping
```

The result is written to a file as well as printed, because Isaac's app swallows
stdout — which cost a diagnostic earlier today.

## Status

| Item | State |
| --- | --- |
| `World` abstraction | **implemented**, 179 tests, injected path unchanged |
| `ContactWorld` | implemented and exercised against toy physics |
| Isaac contact runner | not started — needs the lift scene's names and a real pusher |
| Stopping-time measurement | **built**: `wm_expansion/stopping.py` (12 tests) and `scripts/orbit_lift_stopping_probe.py` |
| The measurement itself | **the next GPU action**, and everything waits on it |
| H1 reachability | in doubt, for a reason that is now specific and testable |
