# H2 fails under real contact, and the reason is the arm

> **Isaac, 2026-08-05, A100.** `Isaac-Lift-Block-PSM-IK-Rel-Play-v0`, 60 capture
> cells at the derived latency and radius. The first physical measurement of the
> paper's central claim, and it does not survive.

## The result

60 of 60 cells produced a capture. Scored:

| Arm | | Rate |
| --- | --- | ---: |
| A | frozen | 0.000 |
| B | parameter repair | 0.133 |
| **C** | **mode expansion — Paper 002's operator** | **1.000** |
| SELF | the target's own trajectory | 0.167 |
| **D** | **relation expansion** | **0.200** |
| D\* | oracle | 1.000 |

**A constant-velocity model lands every cell.** H2 requires the relational arm
to beat the mode operator by a margin; here the mode operator beats it five to
one. This is the case the paper was built to rule out, and under real contact it
is not ruled out — it is the whole of what happens.

## Why: the arm cannot pause

The relation is made necessary by **intermittency**. A target that rides
continuously moves at constant velocity, and a constant-velocity model then
suffices; the pauses are what a single-entity or mode model cannot represent.
On CPU the carrier is a scripted point that stops the instant its schedule says
so, and the intermittency is exact.

A real arm does not stop when told. Measured over 139 goal-pauses in 20 cells:

| steps until the arm reads as stopped | median | p90 | max |
| --- | ---: | ---: | ---: |
| after the goal stands still | **22** | 59 | 85 |

against a `burst_off` of 4. The pause never begins.

The rule for fixing it was written before this was measured — the pause must
exceed the arm's settling time, plus `min_ride_steps` so the stillness is
observable, both being quantities already declared. That gives **25 steps at the
median and 62 at the ninetieth percentile.**

**The carry lasts 54 steps at the median.** A single pause long enough for the
arm to actually stop is as long as the entire time the gripper can hold the
block.

So the intermittency cannot be restored. Not by tuning: by the arm's own
dynamics against the grasp's own duration.

## It is the manipulator, and restoring the pause does not help

Two follow-ups, both of which could have narrowed the result and neither of
which did.

**A different object.** The PSM is a needle driver, and the block is not what it
was built to hold, so the needle should be the favourable case. It is held
longer and far more reliably — 68 steps at the median against 52, and a tenth
percentile of 56 against 16:

| | B | C | SELF | **D** |
| --- | ---: | ---: | ---: | ---: |
| block | 0.133 | **1.000** | 0.167 | 0.200 |
| needle | 0.087 | **0.957** | 0.348 | 0.174 |

The mode operator still lands everything. And on the needle the *single-entity*
arm beats the relational one, 0.348 to 0.174.

**Restoring the intermittency.** The settling time gave `burst_off` = 25, and
the needle's 68-step carry has room for it where the block's 52 did not. Run
with pauses long enough for the arm to actually stop:

| needle | B | C | SELF | **D** |
| --- | ---: | ---: | ---: | ---: |
| `burst_off` 4 | 0.087 | 0.957 | 0.348 | 0.174 |
| `burst_off` 25 | 0.625 | **0.958** | 0.750 | 0.583 |

**Arm C does not move: 0.957 to 0.958.** The pause the whole argument turned on
changes nothing about whether a constant-velocity model suffices.

### The number that ends it

Across both needle configurations, 47 physical cells:

> **Arm D wins zero cells that the single-entity arm loses.** Not one. SELF wins
> four that arm D loses, in each configuration.

On CPU, under injected coupling, arm D won 146 discordant pairs to SELF's 8.

| | arm D | SELF | discordant D : SELF |
| --- | ---: | ---: | ---: |
| CPU, scripted carrier | 0.735 | 0.045 | **146 : 8** |
| physical, needle, pause 4 | 0.174 | 0.348 | **0 : 4** |
| physical, needle, pause 25 | 0.583 | 0.750 | **0 : 4** |

H2 requires the relation to beat *both* competitors. Under real contact it beats
neither, in any configuration tried, with or without the intermittency the design
rests on.

## What this does and does not overturn

**It does not touch the CPU result.** The preregistered SELF comparison passed
Case A twice, and it was always labelled what it is: a comparison of arms under
injected coupling, where the carrier is a scripted point. That remains true of
scripted carriers.

**It bounds where the claim holds.** The relation is necessary when the carrier
can stop. This manipulator cannot stop inside the time it can hold an object, so
in this scene the relation is not necessary — Paper 002's operator is sufficient
and the smallest sufficient change is a mode expansion, not a relational one.

Which is the program's own governing principle returning the answer the paper
did not want:

> Intelligence chooses the smallest sufficient change.

## The chain that got here, all of it measured

| Quantity | Value | How |
| --- | --- | --- |
| capture happens under contact | yes, 60/60 | grasp probe and pilot |
| capture radius | 2.5 mm | 8 separations × 6 seeds, majority holding |
| carry duration | 54 steps median | the gripper drops the block |
| `dispense_latency` | 9 | p10 of L-step displacement clears 20 mm |
| engagement | 0.27 | 60 cells |
| arm D when it acts | 0.375 | measured, against 0.78 on CPU |
| arm's settling time | 22 steps median | 139 goal-pauses |

Each rule was written before its measurement. Three of them had to be corrected
after the first attempt measured the wrong population — the sweep's own grid,
riding steps with the pauses divided out, and windows running past the drop —
and each correction is recorded where it happened.

## What is not available in this scene

- **H3 and H4 cannot be tested here at all.** The controls are defined by
  overriding the target's motion, and under contact physics decides it. Ten
  cells requested as `static` had the arm carry the block 35 to 186 mm. The
  runner now refuses the flag.
- **`normal_alignment` does not apply to a capture.** It measures displacement
  against the contact normal, which is the direction a *struck* target leaves
  along; a carried target moves with its carrier and the sign inverts.
- **Observation noise is 0.00 mm/step**, which means there is no noise model
  rather than that noise is small. The gate's robustness to it is untested by
  this scene.

## Provenance

- `scripts/run_paper003_capture_pilot.sh --script-speed 0.004 --episode-steps 120 --seeds 60`
- `scripts/paper003_pilot_sizing.py`, `scripts/paper003_window_displacement.py`
- Settling time from `commanded_bodies` against `observed_ee` in the same records
