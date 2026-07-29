# Company Narrative v0.2 — Understanding-first

> Internal + external narrative · understanding entry · adequacy as premium insight

---

## Vision

> **We help physical AI learn and adapt when reality breaks its assumptions.**

## Current product (public)

> **Robot Diff — understand what changed between runs, and when the model may no longer be adequate.**

## Customer value

> **We reduce wasted retraining and help robotics teams identify the right next experiment after deployment surprises.**

한국어:

> **구조적으로 잘못된 모델을 계속 재튜닝하느라 발생하는 시간과 실험 비용을 줄인다.**

## Long-term platform

> **An experience lifecycle system that turns real-world surprises into hypotheses, counterfactual tests, model revisions, and safer redeployment.**

---

## Three sentences (any room)

1. **Physical AI breaks when the world changes faster than the model.**
2. **We detect when parameter repair isn't enough.**
3. **We connect field experience to world model revision.**

---

## Company structure

```text
Company mission
  Physical AI that improves when reality violates its assumptions

First wedge (public)
  Robot Diff · Replay · Explain

First wedge (internal)
  Difference → Mismatch → Adequacy → Revision

Long-term platform
  Experience lifecycle
```

---

## Honest capability boundary (now)

> We help teams understand robot behavior differences — and flag when the current model may no longer be adequate, suggesting **repair, replan, or structural review**.

Not yet:

> determine what is missing

(hypothesis generation milestone)

---

## Roadmap by trust level

| Stage | Commitment | Timeline |
| --- | --- | --- |
| **Detect** | Sustained prediction–observation divergence | 2026–28 |
| **Diagnose** | Sensor · policy · parameter · structure candidates | 2026–28 partial |
| **Test** | Counterfactual that best separates hypotheses | 2026–28 partial |
| **Revise** | What to retrain · add · replace | 2028–30 |
| **Validate** | Novel + static regression | 2030–33 |
| **Deploy** | Safe redeploy + new experience capture | 2033+ |

---

## Paper 002 ↔ SDK ↔ Company

```text
Paper 002     Scientific evidence for adequacy decision rule
SDK           Operational implementation + customer log pipeline
Company       Detect → diagnose → test → revise → validate → deploy
```

---

## Competitive position: decision interface

```text
Field telemetry
        ↓
Model adequacy layer          ← us
        ↓
Collect / test / retune / expand / escalate
        ↓
Training and deployment stack
```

Not tied to a single foundation model or simulator.

---

## Evidence (split)

### Preliminary (internal / research partners)

- Controlled mock pilot, five seeds
- Gate separated persistent drift from negative controls
- Structural expansion reduced prediction error vs parameter repair
- Mechanism validation · not real-world generalization

### Before external claims

- Preregistered confirmatory sim
- Multiple mismatch families
- Behavior-level metrics (MPC)
- Isaac implementation
- Hardware anchor validation

---

*Updated 2026-07-29*
