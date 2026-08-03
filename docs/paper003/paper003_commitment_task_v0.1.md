# Paper 003 — Commitment-point task design v0.1

> **Status:** design, 2026-07-31. Abstract simulation only — no Isaac run, no hardware.
> **Solves:** the blocking failure recorded in [paper003_description_v0.1.md](paper003_description_v0.1.md) — the first closed-loop probe could not produce a capability threshold crossing in a continuous reach-and-hold task.
> **Origin:** breakfast-assembly domain (see [Domain note](#domain-note-breakfast-assembly) below). The *task structure* is what matters; the food framing is a demo surface, not the evidence.

---

## The problem this fixes

The first capability probe failed for a structural reason, not a tuning reason:

> In a continuous tracking task the binding constraint is velocity matching, not target prediction, and at loose tolerance every arm succeeds by hovering near the oscillation mean.

Continuous re-aiming **averages away** prediction error. A wrong prediction at step *t* is corrected at step *t+1*, so no arm is ever locked out of the task. That is why success degraded for all arms together instead of opening a window.

A capability threshold needs an action that **cannot be corrected after the fact**.

---

## Task: commit-to-dispense

The agent must deposit filling onto a bread slice that sits on a tray. The tray is intermittently nudged (bursts of motion separated by pauses). Dispensing:

- takes **L steps** to complete once started,
- lands wherever the bread **is at completion**, not where it was at commit,
- is **irreversible** — filling cannot be un-poured, and a miss is a failed unit.

```text
commit at t  ->  [dispense in flight, L steps]  ->  filling lands
                                                    bread has moved by then
```

The agent must therefore predict the bread's position **L steps ahead, at the moment of commitment.** There is no second chance and no averaging.

### Arms (unchanged from the main protocol)

| Arm | Aims at |
| --- | --- |
| **B** parameter repair | Bread's currently observed position |
| **C** mode expansion (Paper 002's operator) | Constant-velocity extrapolation of the bread |
| **D** relation expansion | Bread is rigidly attached to the tray → predict via the **tray's** motion |

Arm D is the same `add_relation_module` operator as the rest of Paper 003: the prediction depends on a **second entity's** state, which no parameter setting of B or C can express.

---

## Result: the threshold exists (200 seeds/cell)

Tolerance 20 mm, dispense latency 6 steps, tray burst pattern 10 on / 4 off.

Reproduce with `python -m wm_expansion.commitment_task` from `scripts/`.

| Tray speed | B zero-order | C constant velocity | D relation |
| ---: | ---: | ---: | ---: |
| 2 mm/step | 1.00 | 1.00 | 1.00 |
| 4 mm/step | 0.57 | 0.89 | 1.00 |
| 6 mm/step | 0.39 | 0.61 | 1.00 |
| 8 mm/step | 0.20 | 0.43 | 1.00 |
| 10 mm/step | 0.10 | 0.36 | 1.00 |
| **15 mm/step** | **0.00** | 0.36 | **1.00** |
| 20 mm/step | 0.00 | 0.32 | 1.00 |

**Arm B reaches a genuine 0%** and arm D remains at 100% — the transition the reach-and-hold task could not produce.

### One threshold is exactly predicted; the other only bounded

This is what makes part of the endpoint preregisterable rather than post-hoc — but the two limits are **not** on equal footing, and an earlier draft of this document overstated the second.

- **B's lockout — exact.** With a 10-on/4-off burst and a 6-step dispense window, every window contains **at least 2 moving steps**, so the bread is displaced by at least `2 × speed`. Arm B survives only while that stays within tolerance, giving a lockout *strictly above* `tol / 2 = 10 mm/step`. At exactly 10 mm/step the minimum displacement equals the tolerance and still counts as a hit (observed 0.10); by 15 mm/step arm B is at **0.00**. The geometry predicts the cutoff; the marginal point behaves as the inequality says it should.
- **C's plateau — lower bound only.** Constant velocity is *exactly* right when the burst state does not change during the window: `(ON − L) / (ON + OFF) = 4 / 14 ≈ 0.286`. The observed plateau is **0.32–0.36**, higher, because arm C also succeeds on state changes whose residual error still falls within tolerance. So 0.286 is a floor on C's ceiling, not the ceiling itself.

For the preregistration this means arm B's lockout speed can be stated in advance as a point prediction, while arm C's plateau can only be prespecified as a **bounded interval**.

### Reading of arm C

C is not simply "worse" — it is *partially* right, and its plateau is set by how often the world happens to look constant-velocity (plus how often the residual error is small enough to be forgiven). This is a cleaner result for the paper than C failing outright: it shows the mode operator captures some of the structure and is still **structurally incapable** of the rest, no matter how the tray speed rises.

---

## Arm D now estimates the pattern (2026-07-31, second pass)

The first pass handed arm D the tray's burst pattern, which made it an oracle rather than an arm. It now infers speed, burst and pause lengths, and current phase **from the observed position history alone** (`ReferencePatternEstimator`), and declines to predict when no complete cycle has been seen rather than guessing. `D_oracle` is retained as an explicit ceiling.

### The noiseless proxy hides the cost of estimating

With clean observations the estimator recovers the pattern almost exactly, so D ≈ D_oracle. **That is a property of the proxy, not a result** — noiseless deterministic bursts make recovery nearly trivial, which is the same criticism as the original oracle, moved one step back. The estimator is only meaningfully tested under observation noise.

### Under noise, at the speed where arm B is locked out (15 mm/step, 300 seeds)

| Observation noise | B | C | **D (estimated)** | D_oracle |
| ---: | ---: | ---: | ---: | ---: |
| 0 mm | 0.00 | 0.37 | **1.00** | 1.00 |
| 1.5 mm | 0.00 | 0.35 | **0.96** | 1.00 |
| 3.0 mm | 0.00 | 0.29 | **0.69** | 1.00 |
| 5.25 mm | 0.00 | 0.24 | **0.42** | 1.00 |
| 15.0 mm | 0.04 | 0.12 | **0.32** | 1.00 |

The estimator degrades substantially — it costs 0.31 at 20% noise and 0.68 at the extreme — but **the capability crossing survives**: arm B stays at or near zero throughout while arm D does not.

### Across speeds at 20% observation noise (300 seeds)

| Tray speed | B | C | **D** | D_oracle | D − B |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 4 mm/step | 0.61 | 0.85 | 1.00 | 1.00 | +0.39 |
| 8 mm/step | 0.20 | 0.51 | 0.95 | 1.00 | +0.75 |
| 10 mm/step | 0.10 | 0.40 | 0.86 | 1.00 | +0.76 |
| **15 mm/step** | **0.00** | 0.29 | **0.69** | 1.00 | **+0.69** |
| **20 mm/step** | **0.00** | 0.24 | **0.59** | 1.00 | **+0.59** |

This is the defensible form of the claim: at speeds where parameter repair cannot succeed at all, an arm that must *estimate* the relation still does — at a real and measurable cost relative to knowing it.

---

## Caveats (must not be glossed)

- **Abstract simulation.** 1-D tray offset, no contact physics. Observation noise is additive Gaussian on position, which is a crude stand-in for perception error. Isaac implementation may move both thresholds; the analytic forms should survive, the numbers may not.
- **The burst pattern is strictly periodic.** The estimator exploits that. A reference body with irregular timing would be harder, and this has not been tested.
- **Noise is applied only to the reference observation**, not to the dispense itself or to the landing.
- **Not preregistered.** These are design-stage values chosen to demonstrate that the transition is constructible at all.

---

## Domain note: breakfast assembly

The task came from asking what real setting has irreversible commitment points. Food assembly does: you cannot un-dispense filling, un-close a sandwich, or un-pour a coffee. A tray nudged by a person reaching past is a mundane, physically honest source of the relational mismatch.

**On scope.** The program decision rule ([`docs/program/README.md`](../program/README.md)) admits an application only when it *sharpens* the central question. Applying it here:

| Element | Verdict |
| --- | --- |
| Irreversible dispense → capability threshold | **In** — supplies the structure the endpoint needs |
| Bread-attached-to-moving-tray → relation | **In** — a physical instance of `add_relation_module` |
| Ingredient exhaustion → replan the assembly order | **In** — model-class inadequacy, later paper |
| Per-person preference learning, user models | **Out** — a different research question (personalisation, not world-model adequacy) |
| Companion interaction, scheduling, greetings | **Out** — product feature |

A physical breakfast robot is a **demonstration and external-validity surface**, not the primary evidence. Paper 003's evidence remains simulated; hardware would follow the same deferred-hardware posture as [Paper 002's physical validation roadmap](../paper002/paper002_physical_validation_roadmap_v0.1.md).

---

## Live demo tool

[`scripts/demo_commitment_live.py`](../../scripts/demo_commitment_live.py) makes the finding touchable. Two markers under an overhead camera — a plate (target) and a pusher (reference tool). A viewer nudges the plate and presses SPACE at the moment they would release a topping; it lands `latency` frames later, wherever the plate is by then. All three arms' predicted landing points are drawn, and hit/miss tallies accumulate.

Arm D's advantage here is physically real rather than scripted: while the pusher is approaching but not yet touching, B and C both say *the plate will not move*, and D says *contact is imminent, it will*.

```bash
python scripts/demo_commitment_live.py --source sim      # check it runs, no camera
python scripts/demo_commitment_live.py --source webcam   # the real thing
```

**This is a demo, not an experiment** — it collects no preregistered data and must not be cited as evidence. Two specific cautions are built into the tool:

- In `--source sim`, arm D predicts with exactly the coupling model that generates the motion, so its 100% is self-fulfilling. Sim mode only checks that the tool runs.
- Outside the contact-imminent regime the plate does not move and every arm is trivially right. The overlay states this, and auto-commit only fires inside the regime — otherwise the demo would appear to show a difference that is not there. This is the same posture as the confirmatory design's eligibility screen.

A first synthetic run gave B 50%, C 50%, D 100% under the contact-imminent gate. Committing at uniformly random moments instead gave B 84%, C 100%, D 95% — i.e. **random commit timing hides the effect entirely**, which is worth knowing before anyone stages this.

---

## What this changes upstream

- The capability-crossing endpoint moves from **unvalidated** to **constructible** — a task shape now exists that produces it, and it survives an arm that has to estimate rather than be told.
- The Isaac environment choice needs revisiting: the oscillating-coupling reach world was built for a tracking task. A commitment-point task may be a better fit for the same relation, and is cheaper to run.
- **Resolved:** online estimation of the reference pattern by arm D.
- **Still blocking before prereg:** an Isaac implementation of the commit structure; gate thresholds re-derived from Isaac data; and a decision on how much observation noise the preregistered cells should carry, since that single parameter moves arm D from 1.00 to 0.32.

---

## Links

| Doc | Path |
| --- | --- |
| RQ | [paper003_rq_v0.1.md](paper003_rq_v0.1.md) |
| Method + the failed tracking probe | [paper003_description_v0.1.md](paper003_description_v0.1.md) |
| Related work | [paper003_related_work_v0.1.md](paper003_related_work_v0.1.md) |
| Program decision rule | [docs/program/README.md](../program/README.md) |

---

## Version history

| Version | Date | Note |
| --- | --- | --- |
| v0.1 | 2026-07-31 | Commitment-point task; first construction of a capability threshold crossing |
