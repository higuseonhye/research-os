# Paper 003 Capability-Crossing Preregistration — DRAFT v0.1

> **Status: DRAFT. NOT FROZEN. NOT A PREREGISTRATION YET.**
> No confirmatory data may be collected against this document in its current
> state. Six parameters are still open (§ Open parameters) and each of them
> moves the primary endpoint, so freezing now would preregister nothing.
>
> **Purpose:** lock every decision that the CPU design work *can* settle, and
> name precisely what the calibration pilot has to measure so that the GPU time
> is spent answering the right questions.
>
> **Order this follows:** Paper 002 ran an engineering calibration pilot
> (`isaac_model_order_pilot_v0.3`, excluded from evidence), then froze
> [its preregistration](../paper002/paper002_model_order_confirmatory_prereg_v1.0.md),
> then ran the confirmatory. Paper 003 is at the step before the pilot.

---

## Research Question

When repeated task failure survives both parameter repair and a mode-level
structural expansion, and the residual is conditioned on a second entity's
state, does adding a prepared relation-module expansion convert task variants
that are **unachievable** into achievable ones — without regressing on variants
that do not require the relation?

The claim is limited to the specified task family and coupling. It is not a
claim about general causal discovery, relation invention outside the prepared
operator, or capability emergence in untested task families.

**The endpoint is deliberately not prediction error.** The design work found the
open-loop prediction advantage to be roughly 1 mm against Paper 002's 10.8 mm,
so a Paper-002-style contrast would understate or miss the effect this paper is
about ([method doc](paper003_description_v0.1.md)).

---

## Locked Arms

| Arm | Target model | Role |
| --- | --- | --- |
| **A** | Frozen, no update | Secondary baseline |
| **B** | Parameter repair within the independent-entity model | **Primary comparator** |
| **C** | Mode expansion — Paper 002's prepared operator | **Discriminating control** |
| **D** | Relation expansion — prediction depends on the second entity | **Primary intervention** |
| **D\*** | Relation with the true reference motion supplied | Diagnostic ceiling only |

All arms share the same controller, task, tolerance, and commit policy, and
differ **only** in the predicted landing point. Arm D must estimate the
reference body's motion from observation; being handed it is arm D\*, which is
excluded from every primary estimate.

**Arm C carries the paper.** If C reaches D's performance, the residual was not
diagnostic of a missing *relation* and Paper 002's operator already suffices —
H2 below is the test that fails in that case.

---

## Task: commitment point

The agent commits to an irreversible placement onto a target carried by an
intermittently moving reference body. The action takes `dispense_latency` steps
and lands wherever the target is at completion. There is no correction.

This structure is required, not incidental. A continuous reach-and-hold version
of the same task produced **no separation between any arms** because continuous
re-aiming averages prediction error away; the design record is in the
[method doc](paper003_description_v0.1.md) and the
[commitment task doc](paper003_commitment_task_v0.1.md).

---

## Commit policy — LOCKED 2026-08-03, before the run that tests it

**Every eligible step is a commit candidate, and one is drawn uniformly at
random per cell from the cell's seed.**

Locked here rather than left to the runner's default because the choice moves
the primary endpoint and is therefore exactly the kind of decision that must
not be made after seeing which arm it favours.

### Why uniform

Two reasons, both independent of any measured outcome:

1. **"First eligible" is not a policy an agent would follow.** Nobody places at
   the earliest physically possible instant. Across trials the commit moment
   spreads over the window, and uniform sampling models that; taking the
   earliest step concentrates every measurement in the approach phase, before
   the encounter has produced any evidence for any arm to use.
2. **Arm independence.** The commit step must not depend on when a particular
   arm's information becomes available, or the arms are no longer compared on
   the same cells. Uniform sampling is arm-blind by construction; so is "first",
   but it is biased in *phase* rather than by arm.

Policies considered and rejected: a fixed offset (the constant is arbitrary),
and letting each arm commit when it judges best (arms would then be scored on
different cells, which is not a comparison).

### Declared in advance: the expected direction of the effect

Under "first eligible" the observed `d_estimated` rate was 0.33 — in two of
three committed cells the relation gate had not yet fired, so arm D fell back
to zero-order and scored identically to arm B by construction. Admitting later
commits will raise that rate, and **is therefore expected to favour arm D**.

That expectation is stated before the run precisely because it is known. The
policy is chosen on the two grounds above, and the direction of its effect is
declared rather than discovered afterwards. Had the reasoning pointed the other
way, the policy would still be uniform.

### Recorded per cell

`commit_policy` and the full `eligible_steps` list are written into every
record, so the realised distribution of commit moments can be audited rather
than taken on trust.

---

## Engagement, and why the endpoint is reported twice — LOCKED 2026-08-03

Arm D can only act once the relation is **characterisable**: the gate must fire
*and* the coupling must be fitted from enough observed contacts. In the pilot it
acted in 0.56 of committed cells, and the reason was diagnosed from the raw
records rather than assumed.

**The gate was not the obstacle.** In three of the four cells where arm D
declined, gate statistics were excellent — proximity contrast 0.96 to 1.00,
constant-velocity gain 0.000, both clearing their thresholds comfortably. What
declined was the coupling fit: only 0, 2, 3 and 2 usable contacts had occurred
by the commit, against the four a line with a fit-quality guard requires.

They missed by **one to three steps**.

### The tuning that will not be done

Opening the commit window a few steps later would raise engagement from 0.56
toward 1.00. It is declined.

When the approach distance was lengthened earlier, the justification was
arm-neutral: *the measurement does not exist* unless the reference pattern is
identifiable before the encounter ends. No such justification is available
here. The only reason to delay the window is that arm D is not ready yet, and
eligibility must be a property of the world rather than of one arm's
readiness — a principle this design has already violated twice, once with the
gate and once with the coupling estimate, and had to reverse both times.

Lowering `min_contacts` from four to three is declined for the same reason and
an independent one: a line through three points leaves a single degree of
freedom, which makes the fit-quality guard nearly vacuous.

### What is preregistered instead

Both estimates, with the conditional one specified in advance rather than
introduced after seeing the marginal:

| Estimate | Population | Reading |
| --- | --- | --- |
| **Marginal** (primary) | All committed cells | What the operator delivers in deployment, including encounters it cannot characterise in time |
| **Conditional** (secondary, prespecified) | Cells where arm D engaged | Whether the relational model is right when it applies |

Neither may be dropped after the fact, and the marginal remains primary. A
conditional advantage with a low engagement rate is a real but bounded result
and must be reported as one.

**Engagement rate is itself an outcome**, not a nuisance parameter. "The
relation was characterisable at commit time in *x* of encounters" is a finding
about when the operator is applicable at all, and is reported with its interval.

---

## Sample size, and a structural fact about the comparison — LOCKED 2026-08-04

### Arm D cannot score worse than arm B

When the gate does not fire, or the coupling cannot be fitted, arm D **falls
back to arm B's aim**. It is then identical, cell by cell. So `D ≥ B` holds by
construction, and the paired difference can never be negative.

Two consequences for how this is read:

1. **"The interval includes zero" is nearly automatic** and carries almost no
   information here. The pilot's paired interval was `[+0.00, +0.33]`; the lower
   bound is structural, not evidential.
2. The informative quantities are **how often arm D engages** and **how much it
   wins by when it does** — which is why both the engagement rate and the
   conditional estimate are preregistered above.

A confirmatory result therefore rests on the *upper* part of the paired interval
being separated from zero, not on the interval's sign.

### Which test is confirmatory — LOCKED

**A one-sided paired sign test on the discordant cells**, not the paired
bootstrap interval.

The bootstrap's lower bound cannot go negative here, for the structural reason
above, so "the interval clears zero" is not a meaningful rejection — it is a
statement about the fallback, not about the model. The sign test conditions on
exactly the cells where the two arms differ, which is where the whole signal is.

The choice is not cosmetic. On the same simulated structure the two disagree by
roughly a third in required sample size, so it has to be fixed in advance rather
than selected once both are visible:

| Committed cells | Bootstrap lower bound clears zero | Sign test |
| ---: | ---: | ---: |
| 40 | 0.67 | 0.47 |
| 60 | 0.91 | 0.81 |
| 80 | — | 0.95 |

The sign test is the more conservative of the two, which is the reason to prefer
it rather than an accident of it being reported second.

### How many cells

Simulating the pilot's observed structure — arm D landing 1.00 against arm B's
0.80 when engaged, identical otherwise — across plausible engagement rates
(`scripts/paper003_contact_robustness.py`):

| Committed cells | eng 0.20 | eng 0.35 | **eng 0.56** | eng 0.75 |
| ---: | ---: | ---: | ---: | ---: |
| 40 | 0.02 | 0.16 | 0.47 | 0.74 |
| 60 | 0.10 | 0.41 | **0.81** | 0.96 |
| 80 | 0.21 | 0.66 | 0.95 | 1.00 |
| 120 | 0.51 | 0.93 | 1.00 | 1.00 |
| 240 | 0.97 | 1.00 | 1.00 | 1.00 |
| **for 0.90** | **200** | **120** | **80** | **60** |

**Engagement is not a nuisance parameter that merely dilutes the effect — it
sets how many cells carry any information at all.** Cells where arm D declines
are ties, and a sign test discards ties. Halving engagement therefore costs far
more than half the power: 0.56 → 0.20 raises the requirement from 80 cells to
200.

At the pilot's nine committed cells power is under 0.10 on any of these rows.
The pilot could not have detected this effect even if it is real, which is the
correct way to read its inconclusive interval.

**Sizing rule — LOCKED.** The confirmatory n is read off this table using the
engagement rate observed in the *real-contact* pilot, not the injected-coupling
one. It is not inherited from the 0.56 row. The contact-misspecification study
below gives a specific reason to expect the real figure to be lower.

---

## What breaks arm D when the contact is real — declared 2026-08-04

Arm D fits a coupling that is **linear in separation**. The pilot generated its
data from exactly that law, so the pilot cannot distinguish "arm D works" from
"arm D read its own assumption back". Real contact obeys no such law.

Rather than discover this during a GPU session, it was measured on CPU first
(`scripts/paper003_contact_robustness.py`): data generated from contact laws the
estimator does *not* assume, scored at the commitment horizon and only on steps
where contact is live and the target actually moves.

| True contact law | Fits | Fitted gain | Fitted radius | Arm D | Arm B |
| --- | ---: | ---: | ---: | ---: | ---: |
| linear *(the assumption)* | 8/8 | 0.49 | 0.051 | 4.7 | 57.6 |
| Hertzian `pen^1.5` | 8/8 | 0.54 | 0.042 | 8.1 | 57.2 |
| very soft `pen^2.5` | 8/8 | 0.69 | 0.031 | 17.9 | 54.2 |
| stiff / saturating | **2/8** | 0.98 | 0.054 | 2.5 | 60.1 |
| friction `mu=0.4` | 8/8 | 0.49 | 0.050 | 9.1 | 19.3 |
| friction `mu=1.0` | 8/8 | 0.49 | 0.050 | **20.7** | 23.9 |

True gain 0.50, true radius 0.050; errors are median mm against a 20 mm tolerance.

**The threat is direction, not nonlinearity.** Getting the penetration law wrong
biases the coefficients but keeps the aim pointing the right way, and arm D
still clears the tolerance up to a very soft `pen^2.5`. Friction does the
opposite: the fitted gain and radius come back *exactly right* — the estimator
only ever fits magnitude against separation, so it cannot see a tangential push
— while the aim goes sideways and arm D exceeds the tolerance at `mu=1.0`.

Two consequences, both declared before the real-contact run:

1. **A new diagnostic is recorded**: `normal_alignment`, the mean cosine between
   observed displacement and the contact normal. Under injected coupling it is
   ~1.0 by construction; under real contact it is the first thing to read if arm
   D underperforms while the gate is healthy and the fit is clean. It is
   **purely diagnostic — nothing gates on it**, so recording it cannot change an
   arm's behaviour.
2. **Engagement is expected to fall, not just accuracy.** Friction shortens the
   usable contact: scored steps dropped from 280 to 88 at `mu=0.4` and 64 at
   `mu=1.0`. Since engagement sets the sample size, the real-contact pilot may
   move the requirement toward the 120–200 rows above.

**Declared expectation for the real-contact run**, so it is not fitted
afterwards: `normal_alignment` below roughly 0.9, engagement at or below the
injected-coupling pilot's 0.56, and arm D's conditional advantage smaller than
1.00 vs 0.80. If arm D instead performs *better* under real contact, that is a
surprise to be explained, not a result to be reported as expected.

The saturating row is also a check on the guard: it declined 6 of 8 seeds rather
than returning a gain of 0.98 against a true 0.50. Refusing is the intended
behaviour and it works.

---

## Primary Endpoint: capability threshold crossing

For a preregistered variant set `T` graded by reference speed, and arms `a`:

```text
crossed(t) :=  success(t, B) <= NEAR_ZERO_BAND
           AND success(t, D) >= ACHIEVABLE_THRESHOLD
```

The primary estimand is the number of variants in `T` satisfying `crossed`,
with per-variant success rates and intervals reported for every arm.

**`NEAR_ZERO_BAND` cannot be zero.** Under a strictly periodic reference arm B
is exactly 0.00, but any timing irregularity lifts it to 0.05–0.09 because some
dispense windows then contain fewer moving steps than the periodic minimum.
Writing `== 0` would preregister an artefact of perfect periodicity.

---

## Confirmatory Hypotheses

### H1: Capability crossing (primary)

At least `K_CROSS` variants in `T` satisfy `crossed`, with the lower endpoint of
the bootstrap interval for `success(t, D)` above `ACHIEVABLE_THRESHOLD` and the
upper endpoint for `success(t, B)` below `NEAR_ZERO_BAND` in each counted
variant.

### H2: The relation is necessary, not merely some expansion

In every variant counted under H1, the lower endpoint of the bootstrap interval
for `success(D) − success(C)` must exceed `C_MARGIN`. Mode expansion partially
helping is expected and acceptable; mode expansion *matching* the relation arm
falsifies the paper's contribution over Paper 002.

### H3: Gate specificity

The relation-adequacy gate must fire on at least 90% of coupled trials, and on
at most 10% of each control: Paper 002's persistent-drift condition, static,
observation-noise, and **post-contact slide** (below). **Firing on motion a
constant-velocity model explains is the failure that matters** — it would mean
the existing mode operator already accounts for the evidence.

#### The drift control is degenerate, and `slide` replaces its role — added 2026-08-04

In the v5 sweep the `drift` target runs along the reference's own axis at the
reference's own speed, so the two never close: **the reference never came within
92 mm of the target in any drift cell.** The gate rejects `drift` because
nothing is nearby, not because it distinguished proximity-conditioned motion
from constant-velocity motion.

The consequence is measurable. Across all 2,960 decidable steps of the sweep,
the number that passed the proximity-contrast test and were then rejected by the
constant-velocity clause is **zero**, in every condition. The clause that is
supposed to keep Paper 003 from collapsing into Paper 002 has never been
exercised.

**`slide` is the control that exercises it.** The reference genuinely strikes
the target — so the relation is real and proximity contrast is high — but the
target then retains its velocity, and a constant-velocity model absorbs the
result. Only the second clause can reject it. This is not a contrived case: it
is what real rigid-body contact produces, because struck objects slide.

The original gate failed it outright. A first pass recorded the leak as "14–19%
of steps", which was **the wrong unit** — H3 is stated per trial. Measured per
trial, the original gate claimed a relation in **every single slide trial**:
firing on one step in eight still means firing somewhere in every episode.

#### Two changes were needed, and neither is sufficient alone

**The gate.** Evidence gathered *before the first contact* is not evidence. A
target that has not yet been touched is still because nothing has happened to
it, not because contact ended and it stopped — yet the far-field class was being
filled with exactly those steps, which drove `proximity_contrast` to +1.0 for
any target that had ever been struck. Worse, at the commit steps the v5 sweep
actually chose, the number of post-departure observations was **zero in all nine
cells**: that +1.0 came from the degenerate branch where the far-field class is
empty. The contrast is now computed from the first contact onward, and the gate
abstains until at least one post-contact far-field observation exists.

**The encounter.** The `burst` schedule only ever advances, so the reference
arrives and stays. The target is therefore never observed after the reference
departs — and until that is observed, a struck target and a target still sliding
from an earlier strike are *the same history*. **This is an identifiability
limit, not an arm's shortcoming**: no method and no ideal observer can separate
them from that record. The `probe` schedule adds a withdrawal (advance 7,
withdraw 5, hold 2 — the same 14-step period, so only the retreat is new), which
places one completed strike-and-release before the commit window.

The change is **arm-neutral**: it alters what the world reveals, not what any
arm is ready to do. That distinction is the one this project has had to restore
three times, and it is why the alternative — delaying the commit window until
arm D is ready — was refused.

| Encounter | Gate | Coupled in time | Slide in time | Median first fire | H3 |
| --- | --- | ---: | ---: | ---: | --- |
| burst | all-history *(original)* | 1.00 | **1.00** | 22 | **fail** |
| burst | post-contact | **0.00** | 0.00 | 34 | **fail** |
| probe | all-history | 1.00 | **1.00** | 7 | **fail** |
| **probe** | **post-contact** | **1.00** | **0.00** | **9** | **pass** |

Scored on whether the gate decides by step 25, the end of the v5 commit window.
Firing eventually is not the same as firing in time: under `burst` the corrected
gate does fire, at around step 34, long after the commitment is made.

#### Declared risk: the gate is noise-sensitive and the noise is unmeasured

Characterised at 0.5 mm observation noise. At 2 mm the coupled fire rate falls to
0.25 and at 5 mm to 0.12, because after contact the target is still and every
far-field sample is pure noise. **The real figure is unknown** — deliverable 2 is
unmet, so no physical jitter has ever been measured. If real contact is noisier
than 1 mm, the gate as specified will not fire often enough, and that is a
threat to H3 from the opposite direction. The real-contact pilot must measure
the noise before the gate can be frozen.

#### The contrast threshold is not fitted

Re-derived from the Isaac records rather than the noiseless proxy: every
`min_proximity_contrast` from **0.30 to 0.90** gives the same separation —
coupled fires, all three controls stay silent — with the coupled step rate
moving only from 0.91 to 0.80 across that entire range. The value in use (0.50)
sits in the middle of a wide plateau, so it is not doing fitted work. This
closes the open item recorded in `RelationGateThresholds`, which had flagged the
proxy's unrealistically clean contrast of exactly 1.0.

### H4: No regression without the relation

On variants that do not require the relation, the lower endpoint of the paired
interval for `success(D) − success(B)` must exceed a non-inferiority margin of
−5 percentage points.

### Diagnostic gates

- `D*` (oracle) success must be at least 80% in every counted variant, i.e. the
  variant is solvable with perfect relational knowledge and H1's failure would
  be attributable to estimation, not impossibility.
- `success(D) <= success(D*)` in every variant. A violation indicates a leak of
  privileged information into arm D and invalidates the run.
- Every execution-validity check passes.

Confirmatory support requires **all** of H1–H4 and every diagnostic gate. The
conjunctive rule is fixed before data; no successful subset is sufficient.

---

## Open parameters — must be set by the calibration pilot

Each of these moves the primary endpoint, so none may be chosen after seeing
confirmatory data. The CPU proxy gives their *shape*, not defensible values.

| # | Parameter | Why it cannot be guessed | Proxy sensitivity |
| --- | --- | --- | --- |
| 1 | `OBSERVATION_NOISE` | Must come from real Isaac perception, not an abstract fraction of a step | Moves arm D from **1.00 to 0.32** |
| 2 | `TIMING_JITTER` | Must come from real contact physics | Moves arm D from **1.00 to 0.61** |
| 3 | `NEAR_ZERO_BAND` | Determined by how far jitter lifts arm B off zero | Arm B **0.00 → 0.05–0.09** |
| 4 | `ACHIEVABLE_THRESHOLD` | Must sit above the achievable floor at the chosen noise/jitter | — |
| 5 | `C_MARGIN` | Depends on how much of the structure mode expansion captures in Isaac | C plateaus **0.24–0.50** in proxy |
| 6 | `min_proximity_contrast` | ~~Proxy has no contact noise~~ — **settled 2026-08-04.** Re-derived from the Isaac sweep: 0.30–0.90 all separate identically | 0.50 sits mid-plateau; not fitted |
| 7 | `max_constant_velocity_gain` | **Untested by the sweep**, whose controls never exercise it; now exercised by `slide` on CPU | Original gate claimed **every** slide trial; corrected gate 0.00 |
| 8 | Observation noise | **Unmeasured.** The gate is characterised at 0.5 mm and its fire rate falls to 0.25 at 2 mm | Blocks freezing the gate; needs the real-contact pilot |

Also pending: the speed grid defining `T`, the placement tolerance, and
`dispense_latency` — all three follow from the physical scale of the Isaac
objects rather than from the 1-D proxy.

---

## What the calibration pilot must produce

Explicitly an **engineering calibration**, excluded from every confirmatory
estimate, matching Paper 002's excluded pilot:

1. The Isaac commit-and-dispense environment runs end to end and is
   process-isolated per cell.
2. Measured observation noise and timing irregularity under real physics → §1–3.
3. A speed sweep locating where arm B falls into the near-zero band → the
   variant set `T`.
4. Gate statistics on coupled, drift, static, noise, **and slide** conditions
   → §6–7, run under the `probe` encounter. The slide control is the one that
   can fail: it is the only condition that exercises the constant-velocity
   clause.
5. **Measured observation noise**, because the gate's fire rate depends on it
   sharply and no physical jitter has ever been measured → §8.
6. Confirmation that arm D\* clears 80%, i.e. the task is solvable at all.
7. `normal_alignment` under real contact, to tell a tangential-push failure
   apart from a coefficient failure if arm D underperforms.

Pilot seeds must be disjoint from the confirmatory sample and are named in the
frozen config.

---

## Sample and validity (structure locked, numbers pending)

- Candidate seeds fixed in advance; static/nominal control run before treatment.
- Seed selection may not be influenced by any treatment result.
- Pilot seeds cannot enter the confirmatory sample.
- Each seed-arm-variant cell runs in a fresh Isaac process.
- Missing cells, unexpected resets, incomplete exposure, or forbidden-region
  violations invalidate the run.

## Estimand and analysis

Per-variant success rates by arm over all valid cells. Bootstrap resampling
over seeds within each variant, and over variants for the crossing count, with
the RNG seed fixed in the frozen config. Report means, two-sided percentile 95%
intervals, and per-variant arm-by-arm tables.

Arm A and arm D\* are secondary and diagnostic and are excluded from the primary
contrast.

## Stopping and reporting

No interim analysis and no optional stopping. Run every locked cell or declare
the run invalid. Preserve config, selection manifest, records, trajectories,
checksums, source commit, and the freeze tag.

**Results will be reported whether or not the hypotheses hold.** The design
record already contains one failed endpoint attempt and two corrected accuracy
claims; a negative confirmatory result is publishable on the same terms.

---

## Before this can be frozen

- [ ] Calibration pilot run and its five outputs recorded
- [ ] Parameters 1–6 filled from pilot data, never from confirmatory data
- [ ] Variant set `T`, tolerance, and `dispense_latency` locked to Isaac scale
- [ ] Config file written and hashed
- [ ] Immutable freeze tag created **before** any confirmatory cell runs

---

## Links

| Doc | Path |
| --- | --- |
| RQ | [paper003_rq_v0.1.md](paper003_rq_v0.1.md) |
| Method + the failed tracking probe | [paper003_description_v0.1.md](paper003_description_v0.1.md) |
| Commitment-point task and all design numbers | [paper003_commitment_task_v0.1.md](paper003_commitment_task_v0.1.md) |
| Related work | [paper003_related_work_v0.1.md](paper003_related_work_v0.1.md) |
| Paper 002 frozen prereg (structural model for this one) | [paper002_model_order_confirmatory_prereg_v1.0.md](../paper002/paper002_model_order_confirmatory_prereg_v1.0.md) |

---

## Version history

| Version | Date | Note |
| --- | --- | --- |
| draft v0.1 | 2026-07-31 | Locks arms, task, endpoint, and hypotheses; names six parameters the calibration pilot must set |
