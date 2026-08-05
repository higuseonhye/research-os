# The settling sweep — rule fixed before the measurement, v1.0

> **Written 2026-08-05, before the sweep was implemented or run.** The manuscript
> draft states a criterion in §4.3 that it does not measure: *the carrier must
> come to rest inside the time it holds the target, and its settling time must be
> short relative to the action's commitment latency*. That is an inference from
> two separate physical measurements — settling 22 steps, grip 54 steps — and an
> inference is not a result.
>
> This turns it into one. Settling time is a property of the **carrier**, and on
> CPU the carrier is ours to specify. So we inject settling into the injected
> coupling and sweep it, over a configuration where the relation is known to be
> necessary, and watch whether Paper 002's operator returns.
>
> Nothing here is confirmatory. It is a claim about **which model suffices for a
> given carrier**, and that question does not need the world in it — which is
> exactly why this is the one part of the physical story CPU can settle.

## The mechanism under test

The relation is made necessary by **intermittency**. The design commands the
carrier to advance for `burst_on` steps and hold for `burst_off`. A real arm does
not hold when told: it takes `s` steps to come to rest, so a commanded pause of
`burst_off` steps produces an observable pause of roughly `burst_off − s` steps,
and none at all when `s ≥ burst_off`.

This predicts the physical result exactly, and the prediction is what makes it
worth testing rather than merely restating:

| | commanded pause | settling | pause that survives |
| --- | ---: | ---: | ---: |
| CPU, scripted carrier | 4 | 0 | **4** |
| physical, `burst_off` 4 | 4 | 22 | **0** |
| physical, `burst_off` 25 | 25 | 22 | **3** |

## Implementation

`EncounterSpec.settling_steps`, defaulting to **0**, which reproduces the current
carrier exactly. The commanded velocity is smoothed by a boxcar of width
`settling_steps + 1` before being integrated into the body's position.

A boxcar rather than an exponential lag, for one reason: after the command stops,
a boxcar of width `w` keeps the body moving for exactly `w − 1` further steps.
So `settling_steps` **is** the measured quantity — "steps until the arm reads as
stopped" — with no time-constant conversion in between, and the sweep's x-axis is
directly comparable to the 22 measured on the arm.

## Predictions — fixed before the sweep runs

Configuration: capture + burst, `burst_on` 10, `burst_off` 4 (period 14),
`dispense_latency` 9, the commit window and gate exactly as preregistered.

- **P1 — arm C returns as settling grows.** `success(C)` increases monotonically
  in `s` and reaches ≥ 0.90 by `s = burst_off = 4`. Below 0.90 at s = 4, or
  non-monotone, and the account in §4.3 is wrong.
- **P2 — arm D collapses to arm B.** `success(D) − success(B)` falls to ≤ 0.05 by
  `s = 4`, and arm D's engagement falls with it. The relation stops being
  identifiable because there is nothing left to identify.
- **P3 — the crossing is at the commanded pause, not at the latency.** The
  settling value at which C overtakes D lies in [2, 6], i.e. near `burst_off` = 4
  rather than near `dispense_latency` = 9.
- **P4 — the derived repair reproduces the physical anomaly.** With
  `burst_off = s + 3` (the rule already used physically: settling plus
  `min_ride_steps`), arm D recovers **and arm B rises with it**, because the duty
  cycle falls and more commit windows land in dead time. Specifically at
  `s = 22`, `burst_off = 25`: `success(B) ≥ 0.40`, against 0.00 at `burst_off` 4.

P4 is the one that carries the most weight, because it tests whether the physical
`burst_off` 25 row's anomaly — arm B jumping from 0.087 to 0.625 — is a property
of **the protocol** or of **Isaac**. If CPU reproduces it, the protocol explains
it and the physical row needs no further defence.

## What a failure of each prediction would mean

- **P1 fails** → settling is not what erases the intermittency, and §4.3's
  criterion is withdrawn from the manuscript rather than softened.
- **P2 fails while P1 holds** → arm D survives a carrier it cannot read, which
  would mean the gate is firing on something other than the pauses. That is a
  defect in the gate and takes priority over the manuscript.
- **P3 fails toward the latency** → the criterion is about the action's horizon
  rather than the commanded pause, and §4.3 is rewritten with the latency as the
  scale. This one is genuinely open; the manuscript currently gestures at the
  latency and the mechanism above says the pause.
- **P4 fails** → the physical `burst_off` 25 anomaly is *not* explained by the
  protocol, and the manuscript must treat it as an unexplained Isaac-side effect
  rather than as a known artefact of the commit policy.

## Not permitted

- The commit window, the gate thresholds, `min_ride_steps` and the tolerance are
  **not** touched by this sweep. It varies one previously-fixed-at-zero parameter
  of the carrier and nothing else.
- The sweep does **not** enter any confirmatory estimate, and no arm score from
  it may be reported beside a physical one without the injected-coupling label.
- If P1–P3 hold, that is not evidence that the relation expansion works — it is
  evidence about **when Paper 002's operator is sufficient**, which is a claim
  against this paper, not for it.

## Seeds and size

Seeds from **7000**, distinct from every run so far (300 for the arm sweeps,
3000 for the amended SELF band), so no configuration is being re-read on cells it
was tuned against. 60 seeds per settling value, `s ∈ {0, 1, 2, 3, 4, 6, 9, 14, 22}`.

The value **22** is included because it is the arm's measured settling time, so
one row of this sweep is the CPU counterpart of the physical run.

## Outcome, 2026-08-05

**All four predictions failed.** Recorded here beside the rule they were written
against, and in full at
[`settling_sweep_v1.0`](../../experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/settling_sweep_v1.0/RESULTS.md).

| | Prediction | Measured | |
| --- | --- | --- | :---: |
| P1 | C ≥ 0.90 by settling 4, monotone | 0.100; not monotone | **FAIL** |
| P2 | D − B ≤ 0.05 by settling 4 | 0.367 | **FAIL** |
| P3 | C overtakes D at settling ∈ [2, 6] | at 14 | **FAIL** |
| P4 | B ≥ 0.40 at settling 22, `burst_off` 25 | 0.333 | **FAIL** |

The document above states what each failure would mean, and those consequences
were applied rather than renegotiated:

- **P1 and P3 fail toward the period, not the latency.** The section anticipated
  exactly this — *"this one is genuinely open; the manuscript currently gestures
  at the latency and the mechanism above says the pause"* — and the answer was
  neither. §4.3 is rewritten with the **velocity ripple** as the scale, which
  tracks arm C at r = −0.940 and also explains the non-monotonicity.
- **P2 fails while P1 holds in its corrected form.** The document says this would
  mean the gate is firing on something other than the pauses and would take
  priority over the manuscript. On inspection it means something weaker and more
  specific: arm D survives a smoothed carrier *on CPU* — 0.450 at settling 22,
  discordant 27 : 0 — so settling does not account for its physical collapse.
  The gate is not defective; the account was incomplete. §4.4 says so.
- **P4 fails on its threshold and is confirmed in its direction.** Arm B rises
  from 0.000 to 0.333 and the discordant count goes 27 : 0 → 9 : 7. The physical
  `burst_off` 25 anomaly is therefore the **commit policy**, not Isaac, which is
  what P4 existed to determine.

**Nothing in this document was edited after the sweep ran** except the addition of
this section. The predictions stand as written, including the one that named 0.40
and got 0.333.

## Version history

- **v1.0, 2026-08-05.** Written before implementation.
