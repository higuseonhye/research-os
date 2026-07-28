# Paper 002 — Mock-to-physics validation (confirmatory)

> **Positioning:** cheap proxy validates expensive physics selection · **not** LLM curriculum · **not** policy training  
> **Status:** pre-reg **v0.3 frozen** · code ready · **execute after commit**  
> **Program:** Paper 001 = measure @ **S** · **Paper 002 = which mismatch to evaluate**

---

## Start here

| Doc | Purpose |
| --- | --- |
| [**Description**](paper002_description_v0.1.md) | Title · abstract · program position · novelty |
| [**Related work**](paper002_related_work_v0.1.md) | POET · PLR · GenSim · differentiation table |
| [**Manuscript pre-results**](paper002_manuscript_pre_results_v0.1.md) | Full methods · tables · interpretation rules |
| [**RQ v0.3**](paper002_rq_v0.3.md) | Sharp research questions |
| [**Pre-reg v0.3**](paper002_prereg_v0.3.md) | **Frozen** confirmatory design |
| [**Method v0.2**](paper002_method_spec_v0.2.md) | Continuous score · consensus export |
| [**Analysis v0.2**](paper002_analysis_plan_v0.2.md) | Bootstrap · binomial · H3 CI |
| [**Run protocol v0.2**](paper002_run_protocol_v0.2.md) | Staged execution · operational gate |
| [**Operational gate**](paper002_operational_gate_v0.1.md) | Engineering go/no-go (not H1∧H2) |
| [**Smoke protocol**](paper002_smoke_protocol_v0.1.md) | Seed-43 engineering only |
| **Config** | [`sandbox_v0.4.yaml`](../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/config/sandbox_v0.4.yaml) |

*v0.1–v0.2 superseded · Study 002 = Tier B pilot only.*

---

## One-line claim

> Prior work asks whether generated environments **improve learning**; Paper 002 asks whether a cheap mock **predicts which physics experiments** expose same-state counterfactual response differences.

---

## v0.3 vs v0.2 (why upgrade before GPU)

| Fix | Reason |
| --- | --- |
| **Continuous mock score** | Binary Spearman ≈ point-biserial · many ties |
| **5-seed median export** | Separates planner quality from one RNG draw |
| **Within-planner export** | Fair rule vs LLM comparison |
| **H2 IR_top ≥ 0.80** | Rate thresholds pass · binomial p **reported only** |
| **Operational vs hypothesis gate** | LLM leg = engineering gate · H1–H3 = post-hoc |
| **H3b bootstrap CI** | Non-inferiority needs interval, not point Δρ |
| **Extreme-export claim label** | Top/bottom only → honest scope |

---

## Execute pipeline (summary)

```text
1. v0.3 commit + tag
2. seed-43 smoke (engineering · optional)
3. mock seeds 42–46 · consensus · export · checksum
4. rule Isaac leg
5. operational go/no-go → LLM Isaac leg
6. H1 → H2 → H3 confirmatory analysis
```

---

## Program stack

```text
Paper 002 — which mismatch to evaluate? (proxy validation)
Paper 001 — how do responses compare @ S? (recoverability ruler)
Paper 003 — latent mismatch + response policy
Paper 004 — adaptive world model update
```

---

## Deferred

Paper 003 (mismatch + RL) · middle-tier 50-spec leg (Tier B optional) · policy training claims
