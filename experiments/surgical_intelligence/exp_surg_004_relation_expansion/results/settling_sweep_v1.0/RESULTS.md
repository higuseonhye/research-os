# The settling sweep: three predictions, three failures, one of them useful

> **CPU, injected coupling, 2026-08-05.** 60 fresh seeds from 7000 at each of
> nine settling values, capture + burst, everything else at the preregistered
> values. Rule and predictions fixed before implementation:
> [`paper003_settling_sweep_prereg_v1.0.md`](../../../../../docs/paper003/paper003_settling_sweep_prereg_v1.0.md)
>
> The manuscript asserted a criterion in §4.3 that it had not measured. This
> measures it, and the criterion as stated is **wrong**. A corrected one is
> supported by the same data and by both physical rows; a second claim in the
> same section is **withdrawn** and not replaced.

## The result

| settling | B | C | SELF | **D** | engagement | D given engaged | D : SELF discordant |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 0.000 | 0.133 | 0.083 | 0.417 | 0.53 | 0.781 | 21 : 1 |
| 1 | 0.000 | 0.117 | 0.017 | 0.500 | 0.57 | 0.882 | 29 : 0 |
| 2 | 0.000 | 0.133 | 0.033 | 0.300 | 0.58 | 0.514 | 16 : 0 |
| 3 | 0.000 | 0.000 | 0.017 | 0.367 | 0.58 | 0.629 | 21 : 0 |
| **4** | 0.000 | 0.100 | 0.017 | 0.367 | 0.57 | 0.647 | 21 : 0 |
| 6 | 0.000 | 0.283 | 0.050 | 0.450 | 0.88 | 0.509 | 24 : 0 |
| 9 | 0.000 | 0.350 | 0.033 | 0.883 | 0.88 | 1.000 | 51 : 0 |
| **14** | 0.000 | **0.917** | 0.017 | 0.733 | 0.73 | 1.000 | 43 : 0 |
| **22** | 0.000 | **0.800** | 0.000 | 0.450 | 0.52 | 0.871 | 27 : 0 |

Settling 4 is the commanded pause; 14 is the schedule's period; 22 is the arm's
measured settling time.

## The predictions, as they were written

| | Prediction | Result | |
| --- | --- | --- | :---: |
| P1 | C ≥ 0.90 by settling 4, monotone | 0.100 at 4 | **FAIL** |
| P2 | D − B ≤ 0.05 by settling 4 | 0.367 | **FAIL** |
| P3 | C overtakes D in settling ∈ [2, 6] | at 14 | **FAIL** |

## P1 and P3: the scale is the period, not the pause

The mechanism I wrote down was that a commanded pause of `burst_off` steps
survives as roughly `burst_off − settling`, so the intermittency should be gone
by settling 4. It is not: arm C sits at 0.100 there and does not move until
settling 9, then reaches 0.917 at **14**.

Fourteen is `burst_on + burst_off` — **the schedule's period**. The smoothing does
not eat the pause from one end; it low-pass filters the whole waveform, and the
intermittency survives as a **ripple** in the carrier's velocity whose size falls
as the smoothing window approaches the period.

### The variable is the ripple, and it is not monotone in settling

A unit test written for this section failed and corrected it. A boxcar of width
`settling + 1` over a period-`p` square wave does **not** flatten at
`settling = p`: it leaves a ripple of order `1/width`, and cancels exactly only
when the width is an integer multiple of the period. Measured, as a fraction of
the commanded advance speed:

| settling | 0 | 4 | 6 | 9 | 13 | **14** | **22** | 27 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ripple | 1.000 | 0.800 | 0.571 | 0.400 | **0.000** | 0.067 | 0.174 | **0.000** |
| arm C | 0.133 | 0.100 | 0.283 | 0.350 | — | **0.917** | **0.800** | — |

**Arm C tracks the ripple at r = −0.940** across the nine swept values. That is
the mechanism, and it explains the non-monotonicity P1 also predicted wrongly:
arm C scores *lower* at settling 22 than at 14 because the ripple there is
*larger* — 0.174 against 0.067 — not because of sampling noise. An earlier draft
of this file attributed it to noise; that was wrong and is corrected here.

### The criterion, and the gap it leaves

Stated on the ripple rather than on a threshold, and evaluated against both
physical configurations at matched ripple:

| | period | settling | ripple | arm C |
| --- | ---: | ---: | ---: | ---: |
| CPU, scripted | 14 | 0 | 1.000 | 0.133 |
| CPU | 14 | 22 | 0.174 | 0.800 |
| **physical, block** | 14 | 22 | 0.174 | **1.000** |
| CPU | 35 | 22 | 0.435 | 0.350 |
| **physical, needle, `burst_off` 25** | 35 | 22 | 0.435 | **0.958** |

The first physical pair nearly matches its CPU counterpart — 1.000 against 0.800.
**The second does not: 0.958 against 0.350 at the same ripple.** So the
smoothed-carrier model accounts for the block configuration and leaves a gap of
about 0.61 in the long-pause one.

That gap is the sharpest available statement of what is unexplained. One
nameable, untested hypothesis: the boxcar models the **arm** tracking its goal,
and not the **object** tracking the arm. A grasped object is filtered a second
time by the compliance of the grip, so the target's velocity would be smoother
than this model makes it — which is the direction the discrepancy runs.

## P2: the failure that costs the manuscript a claim

**Arm D does not collapse.** At the arm's own measured settling time of 22 it
scores 0.450 against arm B's 0.000, engages on 0.52 of cells, and is right 0.871
of the time when it engages. It beats the single-entity arm on **27 discordant
pairs to 0**.

Physically, at the same settling time, arm D scored 0.200 and lost the discordant
comparison **0 to 4**.

So settling time explains arm C's recovery and explains **neither** arm D's
physical score **nor** the D-versus-SELF reversal. There is a second factor in
the physical scene that this sweep does not contain, and it is not identified.
Candidates, none measured: contact jitter in the estimator's inputs; the carry
lasting 54 steps rather than a full episode; the grasp releasing mid-carry; the
servo approach replacing the scripted one.

### What this costs, precisely

The manuscript's §4.3 gave one criterion and used it to account for the whole
physical result. It may keep the half about arm C, corrected to the period, and
must withdraw the half about arm D. The negative result itself is untouched and
if anything strengthened: **arm C at ceiling is the finding, and the mechanism
behind it is now measured rather than inferred.**

What is lost is the tidiness. "A real arm cannot pause, therefore the relation
dies" was one sentence explaining everything. It explains one thing, and the
other thing is open.

## P4: the threshold fails, the claim it was testing is confirmed

Second sweep, `burst_off = settling + 3` — the repair rule already applied
physically, settling plus `min_ride_steps`.

| settling | `burst_off` | B | C | SELF | **D** | D : SELF discordant |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 3 | 0.000 | 0.217 | 0.033 | 0.383 | 21 : 0 |
| 9 | 12 | 0.133 | 0.300 | 0.150 | 0.383 | 14 : 0 |
| **14** | 17 | **0.400** | 0.217 | **0.417** | 0.367 | **7 : 10** |
| **22** | 25 | **0.333** | 0.350 | 0.333 | 0.367 | **9 : 7** |

**P4 predicted `B ≥ 0.40` at settling 22 and failed: 0.333.** The threshold was
set too high and is reported as a failure, not rounded toward its intent.

The claim it was set to test is nonetheless confirmed, and by more than the one
number. Arm B rises from **0.000 to 0.333** as the derived pause is applied, arm
SELF rises to meet arm D, and the discordant count stops being one-sided —
**27 : 0 at `burst_off` 4 becomes 9 : 7, and 7 : 10 at settling 14.** That is the
physical `burst_off` 25 row's signature reproduced on CPU: every arm up, the
single-entity arm level with or above the relational one, the paired comparison
no longer one-sided.

**So the physical `burst_off` 25 anomaly belongs to the commit policy, not to
Isaac.** A pause long enough for the arm to stop leaves most commit windows in
dead time, where a zero-order aim wins and the comparison stops discriminating.
That row needs no Isaac-side explanation and the manuscript can stop offering one.

## Two things the sweep still cannot account for

**The `burst_off` 4 reversal.** Physically, with the short pause, SELF scored
0.348 against arm D's 0.174 and won the discordant comparison 4 to 0. On CPU at
the arm's own settling time with the same short pause, SELF scores **0.000** and
loses **27 to 0**. Nothing in this sweep produces that.

**Arm C at `burst_off` 25.** The corrected criterion says intermittency should
partly survive there — settling 22 against a period of 35 — and on CPU it does:
arm C sits at **0.350**. Physically, at the same two numbers, arm C landed
**0.958**.

Both point the same way: something in the physical scene makes the target's
motion *more* predictable from a constant-velocity model, and the single-entity
arm *more* effective, than a smoothed carrier alone accounts for. Contact jitter,
the 54-step carry against a full CPU episode, the grasp releasing mid-carry, and
the servo approach are the candidates. None is measured.

## Why this sweep was worth running

It was written to convert an assertion into a result, and it did — by refuting
the assertion. The account in the draft would otherwise have gone out as a
mechanism supported by two loosely-connected physical measurements and no test.

## Provenance

- `scripts/paper003_settling_sweep.py --seeds 60`
- `scripts/wm_expansion/encounter.py`, `EncounterSpec.settling_steps`, boxcar of
  width `settling + 1` over the commanded velocity, default 0 so every earlier
  CPU result is reproduced exactly
- `burst_off_4.json` in this directory
