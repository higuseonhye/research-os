# The encounter's proportions do not scale to a millimetre-radius scene

> **Finding, 2026-08-04. Measured in Isaac on the lift scene; the fix is not
> implemented, and an attempt to patch it is recorded here as a warning.**

## The measurement

In `Isaac-Lift-Block-PSM-IK-Rel-Play-v0`, with the encounter's script speed
lowered until the arm could track it:

```
min observed separation  10.1 mm
min commanded separation 10.2 mm
interaction radius       12.0 mm
```

The arm follows the script almost exactly — 10.1 against 10.2. **The script
itself never asks it to come closer than 10.2 mm**, so the closest approach
barely enters the radius, and no cell produced a gate firing or an engaged
relational arm.

## Why

`draw_geometry` places the first body at 2.2 to 2.8 interaction radii and
advances it for `probe_advance` steps. Those proportions were drawn for a 50 mm
radius:

| | radius 50 mm | radius 12 mm |
| --- | ---: | ---: |
| Approach drawn | 110–140 mm | 26–34 mm |
| Advance covers | 7 × 15 = 105 mm | 7 × 3 = 21 mm |
| Ends at | 5–35 mm — inside | ~9 mm short |
| Plus lateral offset | still inside | closest pass ≈ 10.8 mm — outside |

Two constraints were already enforced — the withdrawal must clear the radius,
and a body must not travel further per step than the radius. **The advance
covering the approach was not**, and it is the one that broke.

## The attempted fix, and why it was reverted

Drawing the approach as a fraction of what the advance can cover fixes the first
body and breaks the second: a deeper strike displaces the target further, and
the second body's line was fixed at draw time against the target's *original*
position, so it misses. Four of twenty seeds lost contact entirely.

Aiming the second body at the object continuously fixes that and breaks arm D:
a body that homes on a moving target **curves**, and the pattern estimator
assumes a straight line at constant speed, so the relational arm fell below
zero-order (0.45 against 0.60). A homing pusher is also the wrong phenomenon —
it has intent, and this is meant to be a body that happens to strike.

Aiming once at launch and then travelling straight fixes the curve and leaves
arm C dominant (0.75 against arm D's 0.15), which suggests the deeper strike
leaves the target moving steadily enough for constant velocity to explain it —
the `slide` regime again, arrived at from a different direction.

**Each patch fixed one thing and broke another, and the property tests flapped
with them.** That is the signature of a design that needs one coherent pass
rather than a sequence of local repairs, so the branch was reverted and the
suite left green at 206 tests.

## What a coherent pass has to satisfy, simultaneously

1. The first body's advance reaches and penetrates the radius.
2. Its strike does not carry the target off the second body's line, or the
   second body's line accounts for where the target will be.
3. The second body travels predictably — straight, constant speed — or arm D's
   estimator cannot act and the comparison is vacuous.
4. The target is stationary at commitment and moves during the dispense window.
5. After contact it settles, or the residual is constant-velocity and arm C
   takes it.

Constraints 2 and 3 are in tension, and that tension is the actual design
problem. Two candidates, neither tried:

- **Give the second body its own approach corridor**, offset far enough from
  the first body's strike direction that the displacement does not move the
  target off its line. Keeps both bodies ballistic; costs some encounters where
  the geometry does not admit it.
- **Draw both bodies after simulating the first strike**, so the second's line
  accounts for the displacement without homing. Requires the draw to know the
  coupling, which it currently does not, and makes the geometry depend on the
  condition — a coupling to be examined carefully, since the encounter would no
  longer be identical across conditions.

## Status

| Item | State |
| --- | --- |
| The lift scene runs cells end to end | yes, `contact=physical` |
| The arm tracks the script | yes, within ~5 mm structurally |
| The encounter reaches the object | **no** — the finding above |
| Fix | **not implemented**; needs one pass, not patches |
| Any arm-level number from this scene | **not yet meaningful** |
