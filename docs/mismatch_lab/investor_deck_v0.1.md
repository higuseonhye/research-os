# Mismatch Lab — Investor Deck v0.1

> 6 slides · understanding-first · adequacy as wedge  
> Format: headline + bullets + speaker notes per slide

---

## Slide 1 — Problem

**Headline:** Robot teams compare runs all day — but can't tell when the model itself is wrong.

**Bullets:**

- Every embodied AI team asks: *What changed?* and *Why did behavior shift?*
- Diffing rollouts is manual — spreadsheets, videos, ad-hoc plots
- Worse: teams **retune for weeks** when the model is **missing part of the world**
- Industrial robots need stability; **general physical AI** needs continuous adaptation

**Speaker notes:**

Don't lead with "failure." Lead with daily workflow pain: ablation diff, sim-vs-real, version regression. The expensive mistake is retuning a structurally wrong model. That's the wedge beneath understanding tools.

---

## Slide 2 — Product

**Headline:** Robot Diff — understand what changed. Adequacy when it matters.

**Bullets:**

- **Replay · Diff · Explain · Discover** — Twelve Labs-style verbs for robotics
- Upload two rollouts → auto-aligned timeline → behavior shifts + prediction gaps
- Premium insight: *This difference looks like persistent mismatch, not noise*
- Recommendation: repair · replan · **structural review** · escalate
- Not auto-fixing the robot — **decision layer** between telemetry and training stack

**Demo:** Case 3 — repair plateau → adequacy hint fires

**Speaker notes:**

We sell understanding first. Customers use Diff daily without failures. Adequacy is the upsell when difference persists after recovery. API: `mismatch.diff()` and `mismatch.analyze()`.

---

## Slide 3 — Why now

**Headline:** The decision interface between field experience and model change doesn't exist yet.

**Bullets:**

- **NVIDIA** — compute · sim · Isaac
- **OpenGraph** — experience → data
- **Model cos** — policies · foundation models
- **Gap:** which field surprises should trigger data collection · retrain · structural change?
- Model-agnostic · simulator-agnostic · sits on telemetry + predictions

**Diagram:**

```text
Field telemetry → Mismatch Lab → train / test / expand / deploy
```

**Speaker notes:**

We're not competing on GPU or datasets. We're the adequacy layer — decision interface. Platform is outcome; wedge is Diff + adequacy report.

---

## Slide 4 — Traction & evidence

**Headline:** Research-validated mechanism · product seed in build

**Bullets:**

**Preliminary (Research OS · Paper 002):**

- Mock pilot · 5 seeds · controlled drift
- Gate: persistent drift vs noise/impulse (H4)
- Structural expansion vs parameter repair on prediction (mechanism)
- *Mechanism validated · not yet real-world generalization*

**Product (next 4–6 weeks):**

- Mismatch Lab v0.1 · Robot Diff explorer
- 4 public cases · Python evaluator · pilot waitlist

**Next milestones:**

- Preregistered confirmatory sim · Isaac · behavior metrics · hardware anchor

**Speaker notes:**

Be honest. Numbers stay in appendix until confirmatory. Story: scientific decision rule → SDK → public lab adoption.

---

## Slide 5 — Business model

**Headline:** Start with tools engineers use daily. Expand to adequacy contracts.

**Bullets:**

| Phase | Offer | Buyer |
| --- | --- | --- |
| **Now** | Public lab + pilot SDK | Researchers · early robotics teams |
| **Year 1** | Team tier — batch diff + adequacy reports | Embodied AI startups · OEM sim teams |
| **Year 2+** | Enterprise — failure triage · regression suite · CI integration | Deployed robot fleets |

**Value:** Reduce engineer-weeks wasted on wrong retuning · faster root-cause · right next experiment

**Pricing hypothesis:** SaaS per seat + usage per rollout analyzed · enterprise annual

**Speaker notes:**

Twelve Labs started with search API. We start with Diff. Adequacy report is Team tier differentiator. Don't sell "platform" day one.

---

## Slide 6 — Vision & ask

**Headline:** Physical AI that keeps learning when reality breaks its assumptions.

**Bullets:**

**Today:** Robot Diff + model adequacy hints  
**2028:** Experience selection · counterfactual tests  
**2030+:** Closed-loop revision · deployment  
**Platform:** Experience lifecycle — outcome, not starting point

**The ask (placeholder):**

- **Use of funds:** Mismatch Lab v0.1 launch · confirmatory sim · first design partners
- **Milestone:** 3 pilot teams on SDK · confirmatory pass · Isaac case export
- **Team:** [founder + research + eng hires as needed]

**Closing line:**

> Show us two robot runs. We'll show you what changed — and when your model needs more than retuning.

**Speaker notes:**

End on simple CTA matching homepage. Vision slide is short — one paragraph. Investor remembers Diff + adequacy decision layer.

---

## Appendix (not slides · leave-behind)

- Company narrative v0.2
- API schema excerpt
- Case 3 screenshot
- Paper 002 one-pager
- Competitive table
- Roadmap by trust level (Detect → Deploy)

---

*Updated 2026-07-29*
