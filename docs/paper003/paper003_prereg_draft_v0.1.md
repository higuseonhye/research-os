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

### How many cells

Simulating the pilot's observed structure — engagement 0.56, arm D landing 1.00
against arm B's 0.80 when engaged, identical otherwise — and asking how often the
paired interval's lower bound clears zero:

| Committed treatment cells | Power |
| ---: | ---: |
| 9 (the pilot) | **0.03** |
| 20 | 0.19 |
| 40 | 0.67 |
| **60** | **0.91** |
| 100 | 0.99 |

**The confirmatory needs on the order of 60 committed treatment cells**, roughly
70 seeds at the observed ~0.9 commit rate. At nine, power is 0.03: the pilot
could not have detected this effect even if it is real, which is the correct way
to read its inconclusive interval.

**This is an order-of-magnitude guide, not a precise n.** It assumes the observed
engagement rate and conditional advantage are the true values, and those come
from nine and five cells respectively. Under real contact both are expected to
move — engagement unknown, conditional advantage expected to fall — so the
figure is re-derived from the real-contact pilot before the confirmatory is
sized, not inherited from here.

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
at most 10% of each of: Paper 002's persistent-drift condition, static, and
observation-noise controls. **Firing on persistent drift is the failure that
matters** — it would mean the existing mode operator already explains the
evidence.

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
| 6 | Gate thresholds | The proxy has no contact noise and yields an unrealistically clean proximity contrast of exactly 1.0 | Gate separation 10/10 vs 0/10 in proxy |

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
4. Gate statistics on coupled, drift, static, and noise conditions → §6.
5. Confirmation that arm D\* clears 80%, i.e. the task is solvable at all.

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
