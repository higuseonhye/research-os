# Where the SELF arm catches up — and what stops arm D first

> **Off-protocol probe, fresh seeds (1000+), CPU. Not a protocol result.**
> Rule fixed before running, in the script's docstring. The commit window admits
> only [-6, +6] around an arrival; everything outside that is a commit the
> protocol would never make, evaluated to characterise the arms rather than to
> score them.

## What was asked

The preregistered comparison recorded a limitation: SELF loses in [+4, +6]
partly because it holds a median of 4 steps of its own motion against a 14-step
burst cycle, so **H2's protection is bounded in time rather than absolute**.
This measures where the bound is. 200-400 seeds, `capture` + `burst`, one body.

## Result: SELF catches up from +30

| Offset | n | B | C | **D** | **SELF** | D acts | `cv_gain` |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| −4 … 0 | ~130 | 0.02 | 0.02 | 0.02 | 0.02 | 0.00 | 0.00 |
| +1 … +3 | ~136 | 0.00 | ≤0.38 | 0.00 | 0.00 | 0.00 | 0.00 |
| **+4** | 144 | 0.00 | 0.01 | **0.67** | 0.00 | 0.77 | 0.00 |
| **+5** | 153 | 0.00 | 0.00 | **0.76** | 0.00 | 0.78 | 0.00 |
| **+6** | 155 | 0.00 | 0.03 | **0.78** | 0.02 | 0.79 | 0.00 |
| +8 | 172 | 0.00 | 0.34 | 0.59 | 0.02 | 0.59 | −0.09 |
| +12 | 196 | 0.00 | 0.69 | 0.57 | 0.17 | 0.87 | −0.11 |
| +16 | 200 | 0.00 | 0.27 | 0.62 | 0.47 | 0.81 | 0.11 |
| +20 | 200 | 0.00 | 0.02 | 0.48 | 0.48 | 0.51 | 0.30 |
| +21 | 200 | 0.00 | 0.17 | **0.00** | 0.51 | **0.00** | 0.31 |
| +28 | 200 | 0.00 | 0.55 | 0.68 | 0.56 | 0.68 | 0.23 |
| **+30** | 200 | 0.00 | 0.27 | 0.56 | **0.72** | 0.56 | 0.26 |
| +32 | 200 | 0.00 | 0.01 | 0.52 | **1.00** | 0.52 | 0.29 |
| +36 | 200 | 0.00 | 0.29 | **0.00** | **1.00** | **0.00** | 0.34 |

By the preregistered-style criterion in the script — one-sided exact McNemar at
α = 0.05, from the first offset at which SELF is no longer beaten and stays that
way — **SELF catches up from +30**, which is a little over two burst cycles
after the arrival.

**The protocol band is [-6, +6].** Inside it the relation is unchallenged:
SELF ≤ 0.02 against arm D's 0.67 to 0.78. The catch-up sits five times further
out than any commit the protocol makes.

## What stops arm D is the gate, working as designed

Arm D's zeroes are not mispredictions. **It declines** — `D acts` is 0.00 at
exactly those offsets, so it falls back to arm B and misses by the 60 mm the
target travelled.

`cv_gain` climbs monotonically as the carry lengthens, from 0.00 early to past
0.30 deep in, and arm D stops acting precisely where it crosses the gate's
ceiling. That clause exists to refuse a relational claim wherever a
constant-velocity model already accounts for the motion — Paper 002's regime.
It was written for `drift` and it lands, unprompted, on the boundary of H2's
validity.

**The two mechanisms are the same mechanism.** A carry that has run long enough
to be regular is one whose future is written in the target's own history, which
is what lets SELF in, and is also what makes a constant-velocity model adequate,
which is what makes the gate withdraw. The relation stops being necessary and
the gate stops claiming it, from the same evidence, without either having been
tuned against the other.

## An honest correction to the expected story

The regime past +30 does **not** belong to the mode operator. Arm C is erratic
throughout — 0.69 at +12, 0.02 at +20, 0.01 at +32 — because the carry is
intermittent and a constant-velocity model cannot represent a pause.

What is sufficient there is a single-entity model that has learned the
*periodic* pattern of the target's own trajectory. That is neither B, nor C,
nor D. Paper 003's operator is not needed in that regime and Paper 002's is not
adequate to it, so the correct reading is not "the mode operator takes over" but
**"a fourth kind of model would be, and neither paper proposes it."**

## What this changes

Nothing in the preregistered result, which is confined to [+4, +6] and stands.
It converts a stated limitation into a measured number: the protection is
bounded, the bound is about +30, and the protocol never commits within a factor
of five of it.

## Provenance

- `scripts/paper003_self_arm_bound.py --seeds 400`, seeds from 1000 — disjoint
  from the 300..922 the preregistered run consumed
- The episode is replayed over recorded observations, which is exact: it is
  physics-agnostic and consumes only the (target, bodies) stream. `run_cell` is
  not modified, and the commit window is not bypassed in the protocol - only in
  this probe
