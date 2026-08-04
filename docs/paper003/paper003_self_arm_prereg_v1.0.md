# Paper 003 — SELF arm decision rule

> **Preregistration. Written 2026-08-04, before the arm existed and before any
> capture cell was scored against it.** Fixed in advance precisely so that the
> result cannot change it. Nothing in this document may be revised after the run
> except by recording the revision, the date, and the reason in place.
>
> **Locked 2026-08-04 by the co-PI**, before implementation began: the arm
> definition, the ungated asymmetry, `n = 200` in the `[+4, +6]` band, α = 0.05,
> and the 0.15 margin. Implementation and run follow this line in the history.

## Why this arm decides the paper

H2 requires the ordering

```text
relation arm  >  parameter repair  >  the target's own trajectory
```

The third term has never been measured in this repository. It is the
hypothesis's most dangerous competitor, and it is the one that already killed a
previous design: **carriage** was recommended, and rejected within the hour,
because a single-entity model that learned the burst pattern of the *target's
own* trajectory matched the relational arm exactly. Capture was chosen over it
on the argument that a still target has no history to learn from before the
arrival.

That argument is now in question, and not from any doubt about the relation.
It is from a measured property of arm D: **arm D cannot act before commit offset
+4**, because the gate requires a run of at least three carriage steps and two
consecutive crossings. So every commit that scores anything is at least four
steps into the carry — and by then the target's own trajectory has begun to
carry the carrier's burst pattern. The condition capture was chosen to avoid is
exactly the condition every scored cell now sits in.

Either the relation survives that or it does not. Both outcomes are results.

## The SELF arm

A single-entity model. It observes **only the target's own position history**
and never sees that a second body exists.

- Project the target's history onto its own net direction of travel.
- Estimate the burst pattern of that 1-D signal with the same
  `ReferencePatternEstimator` arm D uses for the carrier, over the same
  `dispense_latency` horizon.
- Apply the predicted per-step displacements along that direction.
- Where the pattern is not identifiable, fall back to the target's current
  position — which is arm B, the same fallback arm D takes.

It is scored on every cell as a fifth arm, alongside A, B, C, D.

### It is deliberately given the easier deal

Arm D may act only when the relation-adequacy gate fires. **The SELF arm is not
gated at all** — it acts whenever its own pattern is identifiable.

That asymmetry is not an oversight and is not to be corrected. It favours SELF,
so it makes the test harder for the hypothesis, and a relation that beats an
ungated single-entity competitor has answered the objection in its strongest
form. Gating SELF would be tuning the competitor down.

## Population, fixed in advance

| | |
| --- | --- |
| Cells | `capture` coupling, `burst` schedule, 1 body, `coupled` condition |
| Loop | `run_cell` with `InjectedWorld`, CPU, `EpisodeSpec()` defaults |
| Eligibility | valid, resolved, and **commit offset in [+4, +6]** |
| Sample | **n = 200 eligible cells**, seeds drawn from 300 upward until 200 are collected |
| Pairing | SELF and D are scored on the *same* cell, so outcomes are paired |

The offset band is not chosen here — it is where arm D can act at all, measured
before this document. Cells outside it are reported but do not enter the test,
because there SELF is compared against an arm that declined.

n = 200 is fixed now and does not move. The exploratory run put roughly a third
of seeds in the band, so this needs about 600 seeds.

## Decision rule

Let `p_D` and `p_SELF` be the success rates on the 200 paired cells, and let the
discordant pairs be those where exactly one of the two landed.

**H2 survives only if both hold:**

1. **Superiority.** One-sided exact McNemar test (binomial on discordant pairs),
   `H_a: p_D > p_SELF`, **α = 0.05**.
2. **Margin.** `p_D − p_SELF ≥ 0.15`.

**If either fails, H2 is rejected.** Not "inconclusive", not "underpowered" —
rejected. The burden is on the relation to show it is necessary; a relation that
cannot be distinguished from the target's own trajectory is not doing the work
the paper claims for it.

### Where 0.15 comes from

Set from what the design has already demonstrated against the arm it was built
to beat, not from anything measured against SELF. At offsets +4 to +6 arm D
scores 0.53 to 0.71 against the mode operator's 0.00 to 0.07 — a margin of
roughly 0.5. The floor here is under a third of that. It is deliberately low
enough that it cannot be accused of having been set to whatever arm D turns out
to achieve, and high enough that a marginal edge does not count as a capability
opening.

## What happens next, decided now

**Case A — `p_D > p_SELF` at α = 0.05 with margin ≥ 0.15.**
H2 stands. The relation is necessary in the regime where it can act. Proceed to
the two-body redraw, then the preregistration rewrite, then the confirmatory
sample.

**Case B — either condition fails.**
H2 is rejected for capture as currently defined, and it is written up as such.
The relation definition reopens; the collision and carriage results, and the
reason each was rejected, are already recorded and stand as the map of what has
been ruled out. Paper 003 becomes a paper about what the missing-relation cell
requires and why three candidate relations did not supply it — which is a
result, and is the reason this rule can be fixed without fear.

---

## Outcome, recorded 2026-08-04

**Case A. H2 stands.** 200 paired cells from 623 seeds.

| | |
| --- | ---: |
| `p_D` | 0.650 |
| `p_SELF` | 0.000 |
| Discordant: D only / SELF only | 130 / 0 |
| One-sided exact McNemar | p = 7.3 × 10⁻⁴⁰ |
| Margin | +0.650 |

Both conditions passed. Nothing in this document was changed to reach that.

SELF acted on 0.675 of cells and landed on none of them, and it was not broken:
its median miss when acting was 60.0 mm against 30.0 mm when it declined to arm
B — it extrapolates through a pause it cannot see, and 60 mm is exactly one
pause at 15 mm/step. It holds a median of 4 steps of its own motion at
commitment against a 14-step cycle.

[Full record](../../experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/self_arm_v1.0/RESULTS.md)

**One limitation is recorded there and not resolved:** SELF's disadvantage rests
on how little of its own history it holds at +4 to +6, so the protection is
bounded in time rather than absolute. Where the bound lies is a separate
question on fresh seeds, and the clause below is why it was not answered by
widening this run.

## Not permitted after the run

- Changing α, the margin, n, the offset band, or the test.
- Changing the commit window, the gate thresholds, `min_carriage_run`, or
  `min_ride_steps`.
- Gating the SELF arm, or narrowing what it observes.
- Adding a post-hoc subgroup in which the ordering holds.

Any of these may be *proposed* after the run, and if so the proposal is recorded
here with the result that prompted it, and it applies to a future run on fresh
seeds — never to this one.
