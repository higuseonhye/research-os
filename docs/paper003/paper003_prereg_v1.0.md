# Paper 003 Capability-Crossing Preregistration — v1.0 (capture), CLOSED

<!-- Still v1.0: the design was not revised. The 2026-08-05 amendment adds
     outcomes and three corrections of fact, and changes no locked rule. -->

> ## Status 2026-08-05 — CLOSED. No confirmatory run will follow.
>
> The Isaac calibration pilot required below has been run. It answered its first
> question yes — **capture happens under real contact, in 60 of 60 cells** — and
> then returned a result that stops the design: the **discriminating control
> saturates**. Paper 002's mode operator lands **0.957 to 1.000** of physical
> cells across three configurations and 107 cells, while the relational arm lands
> 0.174 to 0.583 and never once beats the single-entity competitor.
>
> H1's crossing condition and H2's first clause are therefore **not merely
> unlikely to pass — they cannot pass at any `n`**. The document is closed on
> that ground and not amended to make them passable.
>
> **What may be reported, and what may not**, is written out in
> [Closure](#closure--what-the-pilot-returned-and-what-it-licenses). In short:
> the physical runs are calibration, this preregistration's own text excludes
> calibration from confirmatory estimates, and no confirmatory cell was ever run.
> So **"H2 was rejected at α = 0.05" is not a sentence this record supports.**
> What it supports is that the design's precondition failed in calibration.
>
> Every locked section below is left **exactly as it was locked on 2026-08-04**.
> Nothing in the design was rewritten after seeing a number. The additions are
> the closure section, the outcome stamps inside H2 and the pilot checklist, and
> three corrections of fact marked as such.
>
> ---
>
> **Supersedes [`paper003_prereg_draft_v0.1.md`](paper003_prereg_draft_v0.1.md)
> entirely.** That draft assumes the **collision** coupling throughout, grades
> variants by reference speed (measured non-functional), and its sample-size
> section predates the change of relation. It is kept for provenance and must
> not be cited for any design decision.
>
> **Status 2026-08-04 — superseded by the block above, kept verbatim.** The
> design is locked. The **physical** parameters are not, and are marked
> `PENDING` — they come from an Isaac calibration pilot that has not been run for
> capture. This document is frozen against everything a result could tempt us to
> change, and open only where the world has not been measured yet.
>
> Everything reported below as measured is **CPU with injected coupling**, which
> is a calibration device: the coupling is a formula, `normal_alignment` is 1.0
> by construction, and there is no contact jitter. It is legitimate for powering
> and for arm comparisons, and it is not confirmatory evidence about the world.

---

## Research question — unchanged

When repeated task failure survives both parameter repair and a mode-level
structural expansion, and the residual is conditioned on a second entity's
state, does adding a prepared relation-module expansion convert task variants
that are **unachievable** into achievable ones — without regressing on variants
that do not require the relation?

The claim is limited to the specified task family and coupling. It is not a
claim about general causal discovery, relation invention outside the prepared
operator, or capability emergence in untested task families.

**The endpoint is deliberately not prediction error.** The open-loop prediction
advantage is around 1 mm against Paper 002's 10.8 mm, so a Paper-002-style
contrast would understate or miss the effect this paper is about.

---

## What changed from v0.1, and why

**The relation.** Three candidates were measured against each other and
**capture** was chosen — a body arrives at a still target and carries it off.
Collision cannot clear the placement tolerance: the push moves the target away,
which reduces penetration, which reduces the push. Carriage clears it and makes
the relation unnecessary, because a single-entity model matched the relational
arm exactly. Capture has neither failure.
[Design](paper003_capture_design_v0.1.md) ·
[The ceiling](paper003_displacement_ceiling_v0.1.md)

**The encounter.** One body, `burst` schedule. The two-body encounter is
**retired for this relation**, not redrawn: under capture the first body to
arrive consumes the target, so "demonstrate on one body, apply with another" has
nothing left to apply to.
[Why](paper003_onset_is_not_predictable_v0.1.md)

**The commit policy**, below.

**A fifth arm**, below.

---

## Locked arms

| Arm | Target model | Role |
| --- | --- | --- |
| **A** | Frozen, no update | Secondary baseline |
| **B** | Parameter repair within the independent-entity model | **Primary comparator** |
| **C** | Mode expansion — Paper 002's prepared operator | Discriminating control |
| **SELF** | The target's own trajectory, no second entity observed | **Decisive competitor** |
| **D** | Relation expansion — prediction depends on the second entity | **Primary intervention** |
| **D\*** | Relation with the true landing supplied | Diagnostic ceiling only |

All arms share the same controller, task, tolerance, and commit policy, and
differ **only** in the predicted landing point.

**SELF is new in v1.0 and it is the arm that decides the paper.** It sees no
second body at all and learns the periodic pattern of the target's own
trajectory. It already killed one design: under carriage it matched the
relational arm exactly. Under capture it is the reason the relation can be
called necessary rather than merely sufficient.

**SELF is deliberately ungated.** Arm D may act only when the relation-adequacy
gate fires; SELF acts whenever its own pattern is identifiable. The asymmetry
favours the competitor and is not to be corrected — gating SELF would be tuning
it down.

**Arm D must estimate everything it uses.** The capture radius is recovered from
observation (`estimate_capture`); being handed the generating model is arm D\*,
excluded from every primary estimate.

---

## Task: commitment point

The agent commits to an irreversible placement onto a target that a reference
body captures and carries. The action takes `dispense_latency` steps and lands
wherever the target is at completion. There is no correction.

This structure is required, not incidental: a continuous reach-and-hold version
produced no separation between any arms, because continuous re-aiming averages
prediction error away.

---

## Commit policy — LOCKED 2026-08-04, before the run that tests it

**A commit candidate must lie within one dispense-length of a body's arrival, on
either side. Among the candidates that qualify, one is drawn uniformly at random
per cell from the cell's seed.**

Arrivals are steps at which a body crosses into contact range, per body, from
`contact_arrivals`.

### Why the window, on grounds no arm appears in

Fixed on the **structure of the action**. The dispense takes `dispense_latency`
steps and lands where the target then is, so a commit further out than that
either completes before anything has happened to the target, or measures a
regime the arrival no longer governs. Symmetric, because there is no reason to
prefer a side and preferring one is exactly how "so that arm B fails" would
enter.

What it removes is an **artefact**, not a preference. The eligibility screen
admits any step where the target will move, and under capture that is every step
after the arrival, because a carried target rides forever. So the eligible set —
and with it the commit distribution — was being set by `episode_steps`, an
arbitrary number, and almost all of its mass sat in the riding tail. The same
cell scored differently for running longer.

Uniform *within* the window, for the reason v0.1 gave and which still holds:
nobody places at the earliest physically possible instant, and the commit moment
must not depend on when any particular arm's information becomes available.

### Declared in advance: the direction of this policy's effect

Relative to v0.1's policy — uniform over every eligible step — the window
**removes the deep riding tail**. In that tail a constant-velocity model does
well, the single-entity arm eventually does better still, and arm D declines
because `cv_gain` rises past the gate's ceiling. **Removing it therefore favours
arm D**, and that is stated here rather than discovered afterwards.

The policy is chosen on the structural ground above. Had the reasoning pointed
the other way the window would be the same.

### Not permitted

The window may not be moved to improve the rate at which arm D engages, and the
gate's `min_carriage_run` may not be lowered for the same purpose. The window is
fixed on the action's structure; the run requirement is fixed on the collision
equilibrium, where a struck target momentarily rides at the body's own speed.
Either may be changed only through the **encounter**, on grounds stated before
the run.

### Recorded per cell

`commit_policy`, `arrivals`, `commit_offset`, `committed_in_window`, and the
full `eligible_steps` list, so the realised distribution of commit moments can
be audited rather than taken on trust.

---

## Engagement, and why the endpoint is reported twice

**Arm D cannot score worse than arm B.** When the gate does not fire, or the
relation cannot be fitted, arm D falls back to arm B's aim and is identical to
it cell by cell. So `D ≥ B` holds by construction and the paired difference can
never be negative.

Two consequences:

1. **"The interval includes zero" is nearly automatic** and carries almost no
   information. The lower bound is structural, not evidential.
2. The informative quantities are **how often arm D engages** and **how much it
   wins by when it does**. Both are preregistered endpoints.

The marginal rate and the conditional rate are reported together, always. On the
CPU calibration they are 0.23 and 0.78 — a difference large enough that
reporting either alone would misrepresent the design.

---

## Which test is confirmatory — LOCKED

**A one-sided paired sign test on the discordant cells**, α = 0.05.

The paired bootstrap's lower bound cannot go negative, for the structural reason
above, so "the interval clears zero" is a statement about the fallback rather
than about the model. The sign test conditions on exactly the cells where the
two arms differ, which is where the whole signal is. It is also the more
conservative of the two.

---

## Sample size — LOCKED as a rule, `PENDING` as a number

The v0.1 table does not transfer. It assumed arm D landing 1.00 against arm B's
0.80 when engaged. **Under capture arm B lands 0.00 in the commit window** — the
target travels 15 mm per step against a 20 mm tolerance, so a zero-order aim
cannot survive a carry — and the conditional effect is therefore far larger,
while engagement is lower. Recomputed for that structure, with arm D landing
0.78 when it engages:

| Committed cells | eng 0.10 | eng 0.15 | **eng 0.23** | eng 0.35 | eng 0.50 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 20 | 0.02 | 0.08 | 0.28 | 0.67 | 0.94 |
| 30 | 0.08 | 0.27 | 0.65 | 0.94 | 1.00 |
| 40 | 0.20 | 0.51 | 0.87 | 0.99 | 1.00 |
| 60 | 0.51 | 0.85 | **0.99** | 1.00 | 1.00 |
| 80 | 0.76 | 0.96 | 1.00 | 1.00 | 1.00 |
| 120 | 0.96 | 1.00 | 1.00 | 1.00 | 1.00 |
| **for 0.90** | **101** | **67** | **43** | **28** | **19** |

**Engagement is not a nuisance parameter.** Cells where arm D declines are ties,
and a sign test discards ties, so halving engagement costs far more than half
the power.

**Sizing rule — LOCKED.** The confirmatory `n` is read off this table using the
engagement rate observed in the **real-contact** calibration pilot, not the
injected-coupling one, and not the 0.23 column. Under real contact the gate's
carriage evidence has to survive contact jitter, and nothing yet measures how
often it does.

`n = PENDING`, to be filled from the pilot before any confirmatory cell is run,
and recorded here with the pilot's engagement rate beside it.

> **2026-08-05.** The rule was applied and it returned a number. Real-contact
> engagement is **0.27** (block, 60 cells) rising to **0.50** with the derived
> pause, so the rule reads **`n` ≈ 43** at 0.27 and **≈ 19–28** at the higher
> rates — all of them smaller than the 0.23 column would have given, and all of
> them moot. The sizing rule was never the binding constraint; the
> [closure](#closure--what-the-pilot-returned-and-what-it-licenses) is. Recorded
> because the rule was locked and it is owed its answer.

---

## Primary endpoint: capability threshold crossing

For a preregistered variant set `T` and arms `a`:

```text
crossed(t) :=  success(t, B)    <= NEAR_ZERO_BAND
           AND success(t, SELF) <= NEAR_ZERO_BAND
           AND success(t, D)    >= ACHIEVABLE_THRESHOLD
```

The primary estimand is the number of variants in `T` satisfying `crossed`, with
per-variant success rates and intervals reported for every arm.

**SELF joins the crossing condition in v1.0.** A variant where the relational
arm succeeds and the single-entity arm also succeeds is not a capability the
relation opened, whatever arm B does.

**`NEAR_ZERO_BAND` cannot be zero.** Under a strictly periodic reference, timing
irregularity lifts a near-zero arm to 0.05–0.09 because some dispense windows
contain fewer moving steps than the periodic minimum. Writing `== 0` would
preregister an artefact of perfect periodicity.

**How `T` is graded: `PENDING`.** Reference speed was the v0.1 grading variable
and it is **measured non-functional** — it does not move the arms apart. The
replacement must be chosen from the calibration pilot on the grounds that it
varies the difficulty of the *prediction*, and it must be fixed before the
confirmatory run.

---

## Confirmatory hypotheses

### H1 — Capability crossing (primary)

At least `K_CROSS` variants in `T` satisfy `crossed`, with the lower endpoint of
the bootstrap interval for `success(t, D)` above `ACHIEVABLE_THRESHOLD`, and the
upper endpoints for `success(t, B)` and `success(t, SELF)` below
`NEAR_ZERO_BAND`, in each counted variant.

`K_CROSS`, `ACHIEVABLE_THRESHOLD`, `NEAR_ZERO_BAND`: `PENDING`.

### H2 — The relation is necessary, not merely some expansion

Two competitors, and **both** must be beaten in every variant counted under H1:

- **Against the mode operator.** The lower endpoint of the bootstrap interval
  for `success(D) − success(C)` must exceed `C_MARGIN`. Mode expansion partially
  helping is expected and acceptable; mode expansion *matching* the relation arm
  falsifies the contribution over Paper 002.
- **Against the target's own trajectory.** A one-sided exact McNemar on the
  paired cells must reject at α = 0.05 with `success(D) − success(SELF)` ≥ 0.15.

> **Status on CPU: passed.** Under a rule locked before the arm was implemented
> — 200 paired cells, offsets [+4, +6] — arm D scored **0.650 against SELF's
> 0.000**, 130 discordant pairs none of them SELF's, p = 7.3 × 10⁻⁴⁰. The
> competitor was not broken: it acted on 0.675 of cells, and its median miss when
> acting was 60.0 mm against 30.0 mm when it declined, because it extrapolates
> through a pause it cannot see.
> [Rule](paper003_self_arm_prereg_v1.0.md) ·
> [Result](../../experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/self_arm_v1.0/RESULTS.md)
>
> This is a result about the arms, not about the world. It is restated here as a
> confirmatory hypothesis because the physical run must be able to fail it.
>
> **Status under real contact, 2026-08-05: both clauses fail.** The sentence
> above was written so that this could happen, and it did.
>
> | | arm C | arm D | SELF | cells |
> | --- | ---: | ---: | ---: | ---: |
> | block | **1.000** | 0.200 | 0.167 | 60 |
> | needle, pause 4 | **0.957** | 0.174 | 0.348 | 23 |
> | needle, pause 25 (derived) | **0.958** | 0.583 | 0.750 | 24 |
>
> `success(D) − success(C)` is **negative in every configuration**, so no
> `C_MARGIN` above zero is reachable. And across the 47 needle cells **arm D wins
> zero pairs that SELF loses**, while SELF wins four that D loses, in each
> configuration — the McNemar clause fails in the direction of the competitor.
> [Result](../../experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/physical_h2_v1.0/RESULTS.md)

### H3 — Gate specificity

The relation-adequacy gate must fire on at least 90% of coupled trials and on at
most 10% of each control: persistent drift, static, observation noise, and
post-contact slide.

**Firing on motion a constant-velocity model explains is the failure that
matters** — it would mean the existing mode operator already accounts for the
evidence.

Two admissible forms of positive evidence, one gate:

- **proximity contrast**, which collision enters through;
- **carriage**, which capture enters through — the target's displacement *is* a
  body's displacement, on ≥ 0.80 of moving steps with a run of ≥ 3.

The constant-velocity ceiling applies to **both** and is not to be scoped to
either. The `drift` control agrees with its body on 0.71 of moving steps and
would pass a carriage test outright; `cv_gain` 0.99 is what rejects it. A change
that scopes the ceiling to the proximity path alone must fail
`test_drift_would_pass_a_carriage_test_and_is_rejected_anyway` before it reaches
this document.

### H4 — No regression without the relation

Arm D must not score below arm B on any control condition, within the
preregistered equivalence margin `NO_REGRESS_MARGIN` (`PENDING`).

This is the hypothesis that ruled out the strong form of the decoy design, which
would have driven arm D to zero on `static` and `noise` in exchange for onset
prediction.

### H3 and H4 are CPU-only, and this is structural — noted 2026-08-05

Both are defined against **control conditions**, and every control here works by
overriding the target's motion: `static` holds it still, `drift` moves it
independently, `noise` perturbs it. Under contact **physics decides the target's
motion**, so the override has nothing to act on. Ten cells requested as `static`
had the arm grasp the block and carry it 35 to 186 mm, on every step.

The runner now **refuses** `--condition` other than `coupled` under contact
rather than producing such a cell. So H3 and H4 hold as CPU results and are
untested — not failed — physically, and any report of them must carry that
label. Building a contact control means building a scene where a body approaches
and does not capture, which is a different scene and was never built.

---

## Scope limits — declared, not discovered

### The paper does not claim onset prediction

Arm D cannot commit before the target is captured, and no arm could.
`static` and `noise` are worlds where a body arrives at the target and nothing
happens, and it arrives **closer** than in the treatment — 12 and 14 mm against
42 mm, in 1.00 of cells. Up to the moment of contact, a capturing approach and a
non-capturing one are the same observation.

The claim is therefore:

> Once a relation has taken hold, a prepared relation module predicts where the
> target is going when no model of the target alone can. It does not predict
> that the relation is about to take hold, and in this world nothing could.

[The measurement](paper003_onset_is_not_predictable_v0.1.md)

### The advantage is bounded in time, and the bound is outside the window

Measured on fresh seeds, the single-entity arm catches up from commit offset
**+30**, a little over two burst cycles after the arrival. The commit window is
[−6, +6], where SELF scores ≤ 0.02. The bound sits five times further out than
any commit the protocol makes, and it is reported rather than relied on.

What stops arm D first is the gate, not SELF: `cv_gain` climbs as the carry
lengthens and arm D declines exactly where it crosses the ceiling. The clause
written to keep `drift` out lands unprompted on the boundary of H2's validity.
[The bound](../../experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/self_arm_bound_v0.1/RESULTS.md)

### The capability window is a three-step band

Arm D engages from offset +4, because the gate needs a run of three carriage
steps and two consecutive crossings, so 3 of the window's 13 steps carry the
effect. That is why the marginal rate is 0.23 against a conditional 0.78.

A reader is entitled to ask whether a three-step band is a capability opening or
a curiosity. The answer must come from the confirmatory sample and from whether
the band survives real contact — not from this document.

> **2026-08-05: the band survives, and it is not enough.** Under contact the gate
> still fires — engagement 0.27 to 0.50 — so the band is real rather than an
> artefact of injected coupling. But arm C lands the same cells without it. The
> question was well posed and the answer is the second one: in this scene the
> band is a curiosity, because nothing needed it.

---

## The tuning that will not be done

Fixed here so that a later change has to argue with this list:

- The **placement tolerance stays 20 mm**, inherited from the task family's own
  `mdp/terminations.py` threshold and the block's half-height, both fixed before
  Paper 003 existed. It would stand even if it excluded arm D.
- The **commit window** is not moved to raise engagement.
- **`min_carriage_run`** and **`min_ride_steps`** are not lowered to raise
  engagement. Three consecutive steps is what separates a carry from a collision
  at its equilibrium separation.
- The **gate thresholds** are not re-derived after seeing a control fail.
- The **SELF arm is not gated**, and what it observes is not narrowed.

---

## Open parameters — must come from an Isaac calibration pilot

Every one is `PENDING`, and none may be set from the injected-coupling runs:

| Parameter | Why it cannot be inherited |
| --- | --- |
| `n` | Read from the real-contact engagement rate, per the sizing rule |
| Grading variable for `T` | Reference speed measured non-functional; replacement unchosen |
| `ACHIEVABLE_THRESHOLD`, `NEAR_ZERO_BAND`, `K_CROSS` | Depend on the realised spread under contact |
| `C_MARGIN`, `NO_REGRESS_MARGIN` | Same |
| Capture radius, approach speed, duty cycle | Physical properties of the scene |
| Observation noise | **Never measured.** The gate's statistics were re-derived once already to stop depending on it being small |

**Outcome 2026-08-05.** Four of these were measured, one is unmeasurable in this
scene, one is inapplicable to this relation, and the rest never became meaningful
because the design closed first.

| Parameter | What the pilot returned |
| --- | --- |
| Capture radius | **2.5 mm** — 8 separations × 6 seeds, the largest at which capture holds in a majority |
| Carry duration | **54 steps** median (block), **68** (needle) — bounded by the gripper dropping it |
| `dispense_latency` | **9** — p10 of the L-step displacement clears the 20 mm tolerance |
| Engagement | **0.27** block · 0.39 needle · **0.50** needle with the derived pause → `n` ≈ 28–43 |
| Arm D when it acts | **0.375**, against 0.78 on CPU |
| Observation noise | **0.00 mm/step, which means there is no noise model in this scene** — not that noise is small. It remains an unmeasured threat |
| `normal_alignment` | **Inapplicable to a capture.** See the correction below |
| Grading variable, thresholds, margins | Never chosen. `T` was never constructed, so H1 was never physically testable |

**Correction — `normal_alignment` does not apply to this relation.** It measures
displacement against the contact *normal*, the direction a **struck** target
departs along. A carried target moves *with* its carrier and the sign inverts.
It was listed below as "the dominant threat under realistic contact" on the
strength of a CPU study of **collision**, and it did not survive the change of
relation to capture. Pilot item 3 is retired rather than answered.

## What the calibration pilot must produce

1. **That capture happens at all under real contact.** Everything about the
   relation so far is arithmetic: the cell computes the target's motion and
   writes it into the command. Under `ContactWorld` the cell commands the
   bodies, steps physics, and *reads* where the object went. Whether a gripper
   or a pusher produces a capture rather than a collision in
   `Isaac-Lift-Block-PSM-IK-Rel-Play-v0` is unmeasured, and it is the first
   thing that could end this design.
2. **The engagement rate under contact jitter**, which sets `n`.
3. **`normal_alignment` under real contact.** It is 1.0 by construction in every
   result above. A contact that pushes off-normal returns correct coefficients
   while arm D aims the wrong way, and a CPU study found this to be the dominant
   threat under realistic contact laws.
4. **Observation noise**, so the gate's margin against it can be stated.

> **Answers, 2026-08-05.** (1) **Yes — 60 of 60.** The scene produces a capture,
> and the item written as "the first thing that could end this design" did not
> end it. (2) **0.27 to 0.50**, giving `n` ≈ 28–43. (3) **Retired**, not
> answered: inapplicable to a capture. (4) **0.00 mm/step = no noise model**, so
> the margin cannot be stated from this scene.
>
> The pilot was not asked to score the arms, and scoring them is what closed the
> paper. That is the honest sequence and it is recorded in that order.

---

## Analysis, stopping, reporting

- **Estimand.** Paired per-cell success, arm D against arm B and against SELF,
  in the commit window. Marginal and conditional-on-engagement reported together.
- **Stopping.** `n` is fixed before the first confirmatory cell and not extended
  after any interim look. No interim looks are planned.
- **Reporting.** Every arm, every condition, engagement rate, commit-offset
  distribution, and the gate's evidence type per cell. Cells that did not resolve
  are reported with their reason, not dropped silently.
- **Injected and contact cells are never pooled.** The record carries `world` for
  exactly this reason.

---

## Closure — what the pilot returned, and what it licenses

**The three conditions for freezing this document were:**

1. The Isaac calibration pilot above, for capture. — **Run.**
2. Every `PENDING` filled, each with the measurement it came from. — **Partly.
   Four measured, one unmeasurable here, one retired as inapplicable.**
3. The grading variable for `T` chosen and justified without reference to which
   arm it favours. — **Never chosen.**

Condition 3 was never reached, because condition 1 returned a result that makes
`T` pointless to grade. The document is therefore **closed, not frozen**, and no
cell run against it counts as confirmatory — which was true before and stays
true.

### The precondition that failed

The design rests on the mode operator being a *partial* explanation. In the
prereg's own words: "Mode expansion partially helping is expected and
acceptable; mode expansion **matching** the relation arm falsifies the
contribution over Paper 002."

Under real contact the mode operator does not match the relation arm. It
**beats** it, at ceiling, in every configuration tried:

| Configuration | arm C | arm D | SELF | cells |
| --- | ---: | ---: | ---: | ---: |
| block | **1.000** | 0.200 | 0.167 | 60 |
| needle, `burst_off` 4 | **0.957** | 0.174 | 0.348 | 23 |
| needle, `burst_off` 25 (derived) | **0.958** | 0.583 | 0.750 | 24 |

**Why no `n` rescues this.** H1 counts variants where `success(D)` clears
`ACHIEVABLE_THRESHOLD` while `success(SELF)` sits under `NEAR_ZERO_BAND`, and H2
requires `success(D) − success(C)` to clear a positive `C_MARGIN`. Arm C is at
0.957–1.000 and arm D is below it everywhere; SELF is at 0.167–0.750 and above
arm D in two configurations of three. These are not underpowered estimates near a
boundary — they are the wrong sign at ceiling. Sampling more cells narrows
intervals around the same ordering.

**Why the obvious repair was tried and failed.** The relation is made necessary
by intermittency, and the arm's measured settling time (22 steps median, over 139
goal-pauses) exceeded the `burst_off` of 4, so the pause never began. The rule
for fixing it — *the pause must exceed the settling time plus `min_ride_steps`*
— was written **before** the settling time was measured, and it gave 25 steps.
Run at 25 on the needle, whose 68-step carry has room for it, arm C moved from
**0.957 to 0.958**. The intermittency was restored and it changed nothing about
whether a constant-velocity model suffices.
[Measurement](../../experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/physical_h2_v1.0/RESULTS.md)

### What this record does and does not support

**It does not support** — and no sentence in the paper may claim —

- that H2 was *rejected at α = 0.05*. **No confirmatory cell was ever run.** The
  physical runs are calibration, and this document excludes calibration from
  confirmatory estimates in three separate places. A calibration result cannot
  be promoted to a confirmatory one by turning out to be decisive;
- that H1 was tested. `T` was never constructed;
- that H3 or H4 failed physically. They are not testable in this scene at all;
- that the CPU result was wrong. It was not. It was always labelled a comparison
  of arms under injected coupling, and it remains true of scripted carriers.

**It does support**

- that the design's stated precondition — mode expansion helping only partially
  — is **false in this scene**, measured on 107 physical cells across three
  configurations, with the one candidate repair derived in advance and tried;
- that where the carrier cannot stop, **the smallest sufficient change is a mode
  expansion, not a relational one** — which is the program's own governing
  principle returning an answer this paper did not want;
- that the gap between injected coupling and real contact is **total on the
  decisive comparison**: arm D won 146 discordant pairs to SELF's 8 with a
  scripted carrier, and **0 to SELF's 4** under contact.

### What would reopen it

Not a larger `n`, and not a threshold. A scene where **the carrier can come to
rest inside the time it holds the object**. That is a manipulator property, not a
parameter of this protocol: settling time 22 steps median against a 54-step
carry is the whole obstruction. A carrier that stops promptly — a different arm,
a conveyor, a second object driven directly — restores the intermittency the
design needs, and this document's design would then apply unchanged.

Whoever reopens it should treat every number above as calibration and re-run the
locked rule from the top.

---

## Links

- [Folder README](README.md) — read first; several documents here carry corrections
- [Capture design](paper003_capture_design_v0.1.md) — why capture, and the two rejected relations
- [SELF arm rule](paper003_self_arm_prereg_v1.0.md) and
  [result](../../experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/self_arm_v1.0/RESULTS.md)
- [What the paper may not claim](paper003_onset_is_not_predictable_v0.1.md)
- [Arm scores under each relation](../../experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/capture_arms_v0.1/RESULTS.md)
- [Where the advantage ends](../../experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/self_arm_bound_v0.1/RESULTS.md)
- [Superseded draft](paper003_prereg_draft_v0.1.md) — collision throughout; provenance only
- [**The physical result that closed this**](../../experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/physical_h2_v1.0/RESULTS.md)

## Version history

- **Amendment, 2026-08-05 — CLOSED.** The calibration pilot ran. Adds the status
  block, the [closure](#closure--what-the-pilot-returned-and-what-it-licenses),
  outcome stamps in H2 and the pilot checklist, and three corrections of fact:
  `normal_alignment` is inapplicable to a capture, H3/H4 are structurally
  CPU-only, and observation noise 0.00 means *no noise model* rather than *low
  noise*. **No locked rule was changed**, and none may be changed now — a rule
  edited after this date is editing a rule that has already been tested.
- **v1.0, 2026-08-04.** Rewritten for capture. Supersedes v0.1 entirely. Adds
  the SELF arm to the locked arms, the crossing condition and H2; replaces the
  commit policy with the arrival window; recomputes sample size for a structure
  where arm B lands 0.00; retires the two-body encounter; adds the onset and
  time-bound scope limits.
