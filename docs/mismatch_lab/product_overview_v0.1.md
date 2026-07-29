# Mismatch Lab — Product Overview v0.1 (public-safe)

> Problem · product · evidence · vision — no fundraising or pricing material  
> For boundary rules see [PUBLIC_BOUNDARY.md](../PUBLIC_BOUNDARY.md)

---

## Problem

**Headline:** Robot teams compare runs all day — but can't always tell when the model itself is wrong.

- Teams ask: *What changed?* and *Why did behavior shift?*
- Diffing rollouts is often manual — videos, spreadsheets, ad-hoc plots
- Retuning can continue even when the model is **missing part of the world**
- Industrial robots need stability; **general physical AI** assumes ongoing adaptation

---

## Product

**Headline:** Robot Diff — understand what changed. Adequacy when it matters.

- **Replay · Diff · Explain · Discover** — simple verbs for robotics teams
- Compare two rollouts → aligned timeline → behavior shifts + prediction gaps
- Optional insight: *This difference looks like persistent mismatch, not noise*
- Suggested actions: repair · replan · **structural review** · escalate
- Decision layer between telemetry and training — **not** auto-fixing the robot on day one

**Demo:** [Diff Explorer](diff_explorer_v0.1.html) · Case 3 (repair plateau)

**API sketch:** [api_schema_v0.1.json](api_schema_v0.1.json) — `mismatch.diff()` · `mismatch.analyze()`

---

## Why this layer

**Headline:** A decision interface between field experience and model change.

- Compute / sim platforms · data hubs · foundation models each cover part of the stack
- **Gap:** which surprises should trigger new data · retrain · or structural review?
- Model-agnostic · simulator-agnostic · uses telemetry + predictions

```text
Field telemetry → Mismatch Lab → train / test / expand / escalate
```

---

## Evidence (tier-labeled)

**Preliminary (Research OS · Paper 002 · Tier B+):**

- Mock pilot · 5 seeds · controlled drift · scripted behavior
- Gate separated persistent drift from selected negative controls (H4)
- Structural expansion vs parameter repair on prediction (mechanism)
- *Mechanism validation · not real-world generalization*

**In build:**

- Mismatch Lab v0.1 · Robot Diff explorer · benchmark spec · evaluator prototype

**Next research milestones:**

- Preregistered confirmatory sim · MPC behavior metrics · Isaac · hardware observability cell

Do **not** cite pilot percentages in external materials until confirmatory CI is frozen.

---

## Vision (long-term · not current product scope)

> Physical AI that keeps learning when reality breaks its assumptions.

Roadmap by trust level: **Detect → Diagnose → Test → Revise → Validate → Deploy**  
2026–28 public scope: **Detect + partial Diagnose/Test** only.

See [company_narrative_v0.2.md](company_narrative_v0.2.md) for full framing.

---

## Closing line

> Show us two robot runs. We'll show you what changed — and when your model may need more than retuning.

---

*Updated 2026-07-29*
