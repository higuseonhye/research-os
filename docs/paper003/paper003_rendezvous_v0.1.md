# A grasp needs a rendezvous, not a fly-by

> **Design note, 2026-08-05, written before the change was measured.** The
> grounds are here so that the result cannot be said to have chosen them.
> Follows the same order the SELF arm comparison used: fix the reasoning, then
> run.

## What the pilot found

With the block settling before anything is read (`block_disturbed` 0.00004 mm),
the arm converging to the start line in 16 steps, tracking error at 7.3 mm and
the gripper closing at step 11, the block still does not ride. It is **kicked**:

```text
block moved 36.5 mm     max step 51.68 mm
```

51.68 mm in one 0.02 s step is 2.6 m/s, from an arm moving at 2 mm/step. And the
largest single step exceeds the total displacement, so the block flew and came
partway back. That is penetration resolution — a jaw and the block interpenetrate
and the solver separates them explosively — not a push.

## Why, and why it is not a threshold to tune

The gripper closes while the block is **not between the jaws**. Closest approach
was 10.3 mm, and closing there drives one jaw into the block.

That distance is not an accident of tuning. `draw_geometry` draws a lateral
offset of `uniform(-0.5, 0.5) × interaction_radius` — up to 6 mm — **on purpose**,
so that contacts vary in geometry rather than repeating one head-on pass. Added
to a 7.3 mm steady-state tracking error, the end effector arrives about 10 mm
from the block's centre.

So `--grasp-radius` cannot fix it in either direction: smaller and the gripper
never closes, larger and it closes harder off-centre. The encounter and the
mechanism disagree about what an arrival is.

## The disagreement, stated plainly

The encounter geometry was drawn for a body that **sweeps past and strikes**. A
grasp requires a body that **arrives at** the object and stays with it.

The capture design has said the latter from the first line it was written:

> Capture — the reference **arrives at** a still target, then carries it.

Never "passes". The lateral offset belongs to the collision encounter, where
varying the contact geometry is the point, and it does not belong to the
definition of this relation.

## Two changes, and the grounds for each

**1. Aim at the centre under `--grasp`.** The lateral offset goes to zero. The
approach *azimuth* stays randomised, which is the substantive variation — an
earlier version fixed the axis and made the whole interaction
translation-invariant, so ten seeds gave one encounter. Nothing about which arm
profits enters this: it is what makes an arrival an arrival.

**2. Close at closest approach, not at a radius.** `--grasp-radius` is replaced
by an observable event: the separation stops decreasing. That *is* the arrival,
it is what `capture_displacement` means by taking hold, and it removes a
threshold that could otherwise be moved until the result improved.

The cost is one step of lateness — the minimum is only recognisable once passed —
which at 2 mm/step is 2 mm. Stated rather than hidden.

## What this does not license

The placement tolerance stays 20 mm. The commit window, `min_carriage_run`,
`min_ride_steps` and the gate thresholds are untouched. None of them appears
above, and the preregistration's list of tuning that will not be done still
holds in full.

## What would end this design instead

If the block is still ejected with the jaws centred on it and closing at the
arrival, then the PSM gripper cannot take hold of this block under a scripted
approach, and **capture is not available in this scene**. That is a result, and
the collision and carriage records already map what it would leave.

The next thing to try in that case is not a third threshold. It is to measure
what grasp this scene actually supports — a probe that approaches slowly and
closes at a range of separations, reporting where the block is held rather than
thrown. The preregistration already lists the capture radius as `PENDING` and a
physical property of the scene, not a number to choose.
