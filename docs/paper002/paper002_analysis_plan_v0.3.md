# Paper 002 — Analysis plan v0.3 (WM expansion confirmatory)

> Superseded before confirmatory data by
> [model-order confirmatory preregistration v1.0](paper002_model_order_confirmatory_prereg_v1.0.md).

> **Spec:** [paper002_confirmatory_spec_v0.1.md](paper002_confirmatory_spec_v0.1.md)  
> **Pre-reg:** [paper002_prereg_wm_expansion_v0.1.md](paper002_prereg_wm_expansion_v0.1.md)  
> **Supersedes:** [v0.2](paper002_analysis_plan_v0.2.md) (mock→physics · archived)

---

## Primary contrasts (pre-registered)

```text
C Modular expansion vs B Parameter update   ← primary
C Modular expansion vs A No update          ← secondary
```

---

## Endpoints

| ID | Role | Analysis |
| --- | --- | --- |
| O1 | **Primary** · multi-step prediction error Ep2 · H=10 | Mixed model or paired bootstrap |
| O2 | **Primary** · Ep2 task success | Logistic mixed or paired bootstrap |
| O6 | H3 guardrail · static retention | One-sided non-inferiority · margin δ |
| O9 | H4 · gate FP rate on N1/N2 | Descriptive + binomial CI |
| O7 | H1 diagnostic · Ep1 L1 residual | Descriptive · gate support |
| O8 | Mechanistic · latent | Exploratory · pairs with O1/O2 |

---

## Models

### Prediction error (O1)

```text
PE_H ~ arm + drift_speed + drift_direction + onset + (1 | seed) + (1 | condition)
```

Non-normal residuals → **paired permutation** or **bootstrap CI** on condition-level means (seed-stratified).

### Task success (O2)

```text
logit(success) ~ arm + drift_speed + onset + (1 | seed) + (1 | condition)
```

Report arm-wise success rate + paired bootstrap on (seed, condition) blocks.

### Retention (H3 / O6)

One-sided non-inferiority:

```text
P(static_success_L3 ≥ static_success_baseline - δ) > 0.95   [bootstrap one-sided]
```

δ fixed at pre-reg freeze (default candidate: 5 percentage points).

### Gate validity (H4)

| Control | Metric |
| --- | --- |
| N1 noise | P(gate=1) |
| N2 impulse | P(gate=1) |
| M0 static | P(gate=1) |
| M1 drift | P(gate=1) |

Report confusion-style table · not a single τ threshold hunt.

---

## Presentation order

```text
1. Ep1: L1 repair failure evidence (O7)
2. Ep2: O1 + O2 by arm (Fig 3)
3. Phase 6: static retention (H3)
4. H4 gate controls
5. Fig 4 mechanism (O8) — always adjacent to O1/O2
```

---

## Pilot vs confirmatory

| Tier | Seeds | In primary analysis? |
| --- | --- | --- |
| Engineering pilot | 5 · 10 Ep2 conditions | **No** |
| Threshold tuning | pilot only | — |
| Confirmatory | 10+ · 20–30 conditions | **Yes** |

Confirmatory seeds **never** used for τ_error · K · τ_a · τ_nll tuning.

---

## Exclusion rules (draft · freeze at pre-reg)

- Episode abort: safety violation before drift onset  
- Simulator reset failure  
- Pretrain static success below floor  
- Oracle arm: excluded from primary contrasts · diagnostic only  

---

## Links

- [Confirmatory spec](paper002_confirmatory_spec_v0.1.md)
- [Pre-reg](paper002_prereg_wm_expansion_v0.1.md)
