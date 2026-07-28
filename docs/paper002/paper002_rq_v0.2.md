# Paper 002 — Research questions v0.2

> **Method:** [paper002_method_spec_v0.1.md](paper002_method_spec_v0.1.md)  
> **Pre-reg:** [paper002_prereg_v0.2.md](paper002_prereg_v0.2.md)  
> **Supersedes:** v0.1 (desk draft)  
> **Date:** 2026-07-28

---

## Central question (sharp)

**EN:**

> Under a **frozen mock–Isaac occlusion contract**, does mock-ranked generative curriculum selection identify perturbation specs whose **same-state counterfactual informativeness** (CONTINUE fail · REPLAN success @ **S**) **replicates on Isaac** — and does an **LLM goal planner** match or beat a **rule planner** on that validation metric?

**KR:**

> **Mock–Isaac occlusion contract** 하에서, generative curriculum의 mock rank가 perturbation spec의 **same-state CF informativeness**를 Isaac에서 **예측**하는가 — **LLM goal planner**가 **rule planner**와 동등 이상의 validation을 달성하는가?

---

## Measured object

**Spec-level validation pair** \((m_i, y_i)\):

- \(m_i\): mock informative (0/1) after rank export
- \(y_i\): Isaac informative (0/1) · majority over 8 CF seeds
- **S** fixed by spec `(shift_m, onset_step, occlusion_gain)` at mismatch onset

Counterfactual evaluation = Paper 001 method · **generation** = Paper 002 object.

---

## Sub-questions (priority order)

| ID | Sub-RQ | Hypothesis | Tier |
| --- | --- | --- | --- |
| **RQ-B1** | Mock rank → Isaac rank? | H1 · ρ ≥ 0.5 @ rule | **Confirmatory** |
| **RQ-B2** | Mock top/bottom stratum separates Isaac yield? | H2 · IR_bottom ≤ 0.5 · gap ≥ 0.4 | **Confirmatory** |
| **RQ-B3** | LLM goal planner validates @ Isaac vs rule? | H3a floor + H3b non-inferiority | **Confirmatory extension** |
| **RQ-B4** | Coverage (Gaussian) vs diversity (diffusion) tradeoff? | S2 · descriptive | Exploratory |
| **RQ-B5** | Export robust to mock seed? | S1 · median ρ across 5 seeds | Sensitivity |

---

## Hypothesis map

```text
RQ-B1 ──► H1  Spearman ρ (rule · n=40)
RQ-B2 ──► H2  Tier IR + gap (rule)
RQ-B3 ──► H3  LLM ρ floor + non-inferiority vs rule
            (gate: H1 ∧ H2 pass first)
```

---

## What pilot established (not re-asked as primary)

| Study 002 finding | Paper 002 action |
| --- | --- |
| Diffusion > Gaussian yield | **Closed** · exploratory S2 only |
| Occlusion misalignment | **Contract frozen** in method spec §3 |
| H3′ ρ=0.899 @ n=20 | **Replication target** @ n=40 · threshold lowered to ρ≥0.5 |
| LLM = rule on mock | **Isaac** is RQ-B3 test |

---

## Success tiers (paper)

| Tier | Condition | Title-level claim |
| --- | --- | --- |
| **A** | H1+H2+H3 | CF-validated curriculum · mock filter · LLM goals |
| **B** | H1+H2 · H3 fail | CF-validated curriculum · rule planner |
| **B−** | H1 · ¬H2 | Rank correlation without reliable tier filter |
| **C** | ¬H1 | Honest negative · pilot did not replicate @ scale |

---

## Non-claims

Clinical deployment · foundation model · SOTA reach · latent mismatch (Paper 003) · RL menu (Paper 003) · classifier-guided diffusion
