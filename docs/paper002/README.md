# Paper 002 — Mock-to-physics validation (confirmatory)

> **Positioning:** cheap proxy validates expensive physics selection · **not** LLM curriculum · **not** policy training  
> **Status:** pre-reg **v0.3 frozen** · manuscript PDF v1.2 **under review** · GPU not started  
> **Program:** Paper 001 = measure @ **S** · **Paper 002 = which mismatch to evaluate**

---

## Manuscript (under review)

| Artifact | Link | Note |
| --- | --- | --- |
| **Pre-results PDF v1.2** | [`paper002_pre_results_v1.2.pdf`](paper002_pre_results_v1.2.pdf) | Discussion draft · placeholder tables · *not peer-reviewed* |
| **Status** | [`status.md`](status.md) | Phase map · review boundary |

While under review, PDF prose may change. **Frozen protocol:** [`paper002_prereg_v0.3.md`](paper002_prereg_v0.3.md) · tag `paper002-prereg-v0.3`.

---

## Start here

| Doc | Purpose |
| --- | --- |
| [**Status**](status.md) | Phase · tiers · review boundary |
| [**Description**](paper002_description_v0.1.md) | Title · abstract · program position |
| [**Related work**](paper002_related_work_v0.1.md) | POET · PLR · GenSim · differentiation |
| [**Pre-reg v0.3**](paper002_prereg_v0.3.md) | **Frozen** confirmatory design |
| [**Method v0.2**](paper002_method_spec_v0.2.md) | Continuous score · consensus export |
| [**Analysis v0.2**](paper002_analysis_plan_v0.2.md) | Bootstrap · H2 · H3 CI |
| [**Run protocol v0.2**](paper002_run_protocol_v0.2.md) | Staged execution |
| [**Operational gate**](paper002_operational_gate_v0.1.md) | Engineering go/no-go |
| [**Smoke protocol**](paper002_smoke_protocol_v0.1.md) | Seed-43 engineering only |
| **Config** | [`sandbox_v0.4.yaml`](../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/config/sandbox_v0.4.yaml) |

Markdown manuscript skeleton: [`paper002_manuscript_pre_results_v0.1.md`](paper002_manuscript_pre_results_v0.1.md) (superseded by PDF v1.2 for narrative).

---

## One-line claim

> Prior work asks whether generated environments **improve learning**; Paper 002 asks whether a cheap mock **predicts which physics experiments** expose same-state counterfactual response differences.

---

## Execute pipeline (after review + GPU)

```text
1. Finish PDF review
2. seed-43 smoke (engineering)
3. mock 42–46 · consensus · export · checksum
4. rule Isaac → operational gate → LLM Isaac
5. H1 → H2 → H3 analysis
```

---

## Program stack

```text
Paper 002 — which mismatch to evaluate? (proxy validation)
Paper 001 — how do responses compare @ S? (recoverability ruler)
Paper 003 — latent mismatch + response policy (deferred)
```

Study 002 = Tier B pilot only · see [`../stage2/`](../stage2/)
