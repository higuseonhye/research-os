# Vision narrative v0.2 — Understanding-first (public-safe)

> Long-term research program framing · **not** a company or product roadmap in this repo  
> See [PUBLIC_SCOPE.md](PUBLIC_SCOPE.md) · [PUBLIC_BOUNDARY.md](../PUBLIC_BOUNDARY.md)

---

## Vision (research program · long-term)

> **Physical AI that keeps learning when reality breaks its assumptions.**

## Public scope today (Mismatch Lab spec)

> **Robot Diff — understand what changed between runs, and when the model may no longer be adequate.**

## Value proposition (teams using the tools)

> **Reduce wasted retraining and identify the right next experiment after deployment surprises.**

한국어:

> **구조적으로 잘못된 모델을 계속 재튜닝하느라 발생하는 시간과 실험 비용을 줄인다.**

## Long-term research direction (not current repo scope)

> **An experience lifecycle framing:** real-world surprises → hypotheses → counterfactual tests → model revision → safer redeployment.

Documented here for orientation only. **Not** a commitment to ship a platform from research-os.

## Domain generality (orientation only)

> While the present studies use embodied robotic systems as the testbed,
> the underlying question — when should an autonomous decision-making
> system revise its model class rather than repair within it — is
> domain-general and may extend beyond physical robotics.

This framing does not change current scope or claims (see [PUBLIC_BOUNDARY.md](../PUBLIC_BOUNDARY.md)).
It is documented here only to record the origin of the research question.

---

## Three sentences (public-safe)

1. **Physical AI breaks when the world changes faster than the model.**
2. **We detect when parameter repair isn't enough.**
3. **We study how field experience should inform world model revision.**

---

## Two public surfaces (this repository)

```text
Research OS (this repo)
  Evidence · protocols · Paper 001/002 · promoted results

Mismatch Lab (docs/mismatch_lab/)
  Robot Diff · benchmark · SDK design · pilot invitation
```

Commercial hosting · customer contracts · operational SLAs are **out of scope** for research-os.

---

## Program structure (research · not org chart)

```text
Program question
  Physical AI that improves when reality violates its assumptions

Public wedge (now)
  Robot Diff · Replay · Explain

Mechanism chain (Paper 002)
  Difference → Mismatch → Adequacy → Revision
```

---

## Honest capability boundary (now)

> Help teams understand robot behavior differences — and flag when the current model may no longer be adequate, suggesting **repair, replan, or structural review**.

Not yet:

> determine what is missing

(hypothesis generation milestone)

---

## Roadmap by trust level (research · aspirational)

| Stage | Research question | Timeline |
| --- | --- | --- |
| **Detect** | Sustained prediction–observation divergence | 2026–28 |
| **Diagnose** | Sensor · policy · parameter · structure candidates | 2026–28 partial |
| **Test** | Counterfactual that best separates hypotheses | 2026–28 partial |
| **Revise** | What to retrain · add · replace | 2028–30 |
| **Validate** | Novel + static regression | 2030–33 |
| **Deploy** | Safe redeploy + new experience capture | 2033+ |

Later stages are **not** documented as products in this repo.

---

## Paper 002 ↔ public lab spec

```text
Paper 002     Scientific evidence for adequacy decision rule
Mismatch Lab  Explainer demos · benchmark · open SDK sketch
```

---

## Decision-interface framing (research positioning)

```text
Field telemetry
        ↓
Model adequacy layer (research + open spec)
        ↓
Collect / test / retune / expand / escalate
        ↓
Training and deployment stack (external)
```

Not tied to a single foundation model or simulator.

---

## Evidence (split)

### Preliminary (Tier B+ · mock pilot)

- Controlled mock pilot, five seeds
- Gate separated persistent drift from negative controls
- Structural expansion reduced prediction error vs parameter repair
- Mechanism validation · not real-world generalization

### Before stronger public claims

- Preregistered confirmatory sim
- Multiple mismatch families
- Behavior-level metrics (MPC)
- Isaac implementation
- Hardware observability cell

---

*Updated 2026-07-31*
