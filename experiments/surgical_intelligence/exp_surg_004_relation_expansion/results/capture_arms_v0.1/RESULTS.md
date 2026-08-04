# The arms under capture, and the gate that had to learn a second kind of evidence

> **CPU calibration, injected coupling. Excluded from confirmatory evidence.**
> 40 seeds per case unless stated, `scripts/paper003_capture_arms.py`, 2026-08-04.
>
> Three things happened in order, and the middle one reverses something recorded
> as settled. Read them in order.

## What was being measured

Open item 3 of the [Paper 003 README](../../../../../docs/paper003/README.md):
the capture relation and the cell loop had been connected but never scored
through together. Two things were fixed first — the commit window (item 2) and
arm D's capture prediction, which existed in `predict_capture` but was never
wired into `CommitmentEpisode.aims`.

---

## 1. A defect in the relation itself

`capture_displacement` returned the carrier's own step on the step it *took
hold*. The body has already moved when the separation is tested, so handing the
target that same step threw it one body-step past its carrier: **captured at
49.9 mm, carried at 64.7 mm** — outside the radius it was captured at, for the
rest of the episode, by a margin equal to one body-step.

Fixed: the arrival step carries nothing, and the target holds at the separation
it arrived at.

## 2. Which reversed the gate result

With that fixed, the relation-adequacy gate **abstained on every capture cell**:
20 rollouts, fire rate 0.00, `post_contact_far_deltas` 0 in all 20.

That is what the deleted capture-specific gate variant was built for. Its
premise — a body that never leaves supplies no post-contact far-field period, so
a contrast measured from first contact onward has nothing to compare — had been
recorded as refuted by a measurement showing 20 usable far-field deltas and a
1.00 fire rate.

**That measurement was reading the defect.** The riding separation sat outside
the radius; the gate's near-field allowance covers a body-step during motion but
not during a pause; so the pauses sorted into the far field and supplied exactly
the deltas that refuted the prediction. The premise was right.

Since `can_estimate` requires the gate, an abstaining gate meant arm D never
acted under capture and scored exactly arm B — 0.00 in every configuration.

## 3. So the gate was given a second admissible form of evidence

Not a capture-specific threshold set, and not a second gate. One more way for
the same gate to find **positive** evidence:

> **Carriage.** The target's displacement *is* a second body's displacement —
> agreement on ≥ 0.80 of moving steps, with a run of ≥ 3 consecutive steps
> against a single body.

The run requirement is there for the reason `estimate_capture` has one: a struck
target has an equilibrium separation where the push equals the body's own
advance, and there collision and carriage are momentarily the same observation.
A collision passes through it; a carry does not.

Every other clause of the gate applies unchanged, **including the
constant-velocity ceiling**, and that is what makes the new path safe. The
`drift` control runs its target along the first body's own axis at its own
speed, so its displacement genuinely agrees with that body's on **0.71** of
moving steps under a burst schedule — it would clear any carriage threshold
worth setting. Its `cv_gain` is 0.99 and the ceiling rejects it. Pinned by
`test_drift_would_pass_a_carriage_test_and_is_rejected_anyway`.

---

## Result

| Case | B | C | **D** | D acted | in window | n |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| capture / burst / 1 body | 0.05 | 0.20 | **0.23** | 0.23 | 0.88 | 40 |
| capture / probe / 1 body | 0.10 | 0.05 | **0.15** | 0.88 | 0.33 | 40 |
| capture / probe / 2 bodies | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | 27 |
| collision / probe / 1 body | 0.80 | 0.68 | **0.82** | 0.72 | 1.00 | 40 |
| collision / probe / 2 bodies | 0.50 | 0.15 | **0.70** | 0.60 | 1.00 | 40 |
| slide (control) | 0.00 | 0.82 | 0.00 | 0.00 | 0.78 | 40 |
| drift (control) | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 40 |
| static (control) | 1.00 | 1.00 | 1.00 | 0.00 | 1.00 | 40 |
| noise (control) | 0.47 | 0.03 | 0.47 | 0.00 | 1.00 | 40 |

**All four controls are unchanged**, and collision is unchanged — it still
enters through the proximity contrast, with a carriage run below threshold.

## The marginal rates understate it: arm D is limited by readiness, not accuracy

| capture / burst | n | arm D |
| --- | ---: | ---: |
| cells where D acted | 9 | **0.78** |
| cells where D declined | 31 | 0.06 |

Under `probe` the same split is 0.14 against 0.20 — arm D acts on 35 of 40 cells
and gains nothing. **Capture belongs with `burst`**, as the README already
pairs it. `probe` reverses, so the carrier drags the captured target back, and
the pattern estimator takes median run lengths on the projection onto a net
direction that a reversal drives toward zero. `capture / probe / 2 bodies` is
degenerate for a separate reason: the prober captures the target and carries it
out of the pusher's approach line, so 13 of 40 cells never resolved.

### Where the relation pays, by commit offset

100 seeds, `capture / burst`, in-window cells only:

| offset | n | D acted | **D** | B | C |
| ---: | ---: | ---: | ---: | ---: | ---: |
| −5 | 5 | 0.00 | 1.00 | 1.00 | 1.00 |
| −4 … +3 | 42 | **0.00** | 0.00 | 0.00 | ≤ 0.33 |
| +4 | 15 | 0.80 | **0.53** | 0.00 | 0.07 |
| +5 | 5 | 0.80 | **0.60** | 0.00 | 0.00 |
| +6 | 14 | 0.86 | **0.71** | 0.00 | 0.07 |

The boundary is sharp at **+4**, and it is not a tuning artefact: arm D needs a
run of ≥ 3 carriage steps before the gate will admit the evidence, plus two
consecutive crossings. Before that it has nothing to fit and correctly declines.

Past it, the relation is worth what the paper claims for it: **0.53 → 0.71
against 0.00 for parameter repair and ≤ 0.07 for the mode operator.**

## Open, and not to be closed by tuning

The commit window runs to ±6 steps around the arrival; arm D's evidence
requirement starts at +4. **Three of the window's thirteen steps are usable**,
which is why the marginal rate is 0.23 while the conditional rate is 0.78.

Either side could be moved, and neither should be moved for this reason. The
window is fixed on the structure of the action, chosen so that it could not be
placed where an arm profits; the evidence requirement is fixed on the collision
equilibrium, and lowering it would admit a struck target as a carried one. If
the overlap is to change it has to change through the encounter — how fast the
carrier moves, how long the dispense takes — on grounds stated before the run.

Also unresolved, and untouched here: under `burst` a carried target rides the
carrier's intermittency, so its **own** trajectory carries the burst pattern.
That is the single-entity threat to H2 that the capture design rejected carriage
over, and it now applies to every commit at offset ≥ +4. The single-entity arm
is not among the arms this cell scores, so nothing here measures it.

## Provenance

- `scripts/paper003_capture_arms.py --seeds 40`, CPU, injected coupling
- Gate rates and control rejections from `scripts/test_paper003_capture.py::GateTests`
- 228 tests pass, all CPU
