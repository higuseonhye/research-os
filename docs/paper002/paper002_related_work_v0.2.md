# Paper 002 — Related work v0.2 (WM expansion)

> **Positioning doc** · cite in Introduction · supersedes [v0.1](paper002_related_work_v0.1.md) (mock→physics · archived)  
> **Core wedge:** failure-conditioned **model-adequacy testing** · not “add expert after failure” alone

---

## Novelty (defensible)

**Avoid:** failure-driven world-model reconstruction · add expert after failure · latent representation expansion.

**Use:**

> **Failure-conditioned model-adequacy testing for embodied world models: determining when parameter repair is insufficient and restricted structural expansion is necessary.**

Long form (manuscript):

> We study whether persistent, structured task failures can provide evidence that an embodied agent’s current dynamics model is inadequate, and whether selecting a **prepared** structural expansion operator improves prediction and control beyond parameter-only adaptation without degrading nominal behavior.

**Scope defense:**

> Paper 002 does not autonomously invent an unconstrained causal ontology. It tests a restricted first step: whether failure evidence can justify switching from parameter repair to a **prepared** structural expansion operator.

Closest prior work already adds modules, routes mixtures, or integrates new world models at test time. Our contribution is **whether and when** expansion is warranted — validated on downstream prediction · planning · recoverability · nominal regression.

---

## 1. Latent predictive world models

World models compress high-dimensional observations into latent state, learn action-conditioned dynamics, and support planning or policy learning via imagined rollouts; prediction error often drives refinement. Recent surveys treat WM roles as policy learning, planning, simulation, evaluation, and synthetic data generation ([World Model for Robot Learning survey](https://arxiv.org/abs/2605.00080)).

**Fixed model class (typical):**

```text
fixed representation / architecture
+ new observations
→ better latent state or parameters
```

**Paper 002:**

```text
persistent task failure
→ is the fixed model class still adequate?
→ repair parameters or change model structure?
```

Latent representation learning is **background**, not the novelty claim.

---

## 2. Continual and adaptive world models

Representative lines:

| Work | Focus | Trigger |
| --- | --- | --- |
| [DRAGO](https://openreview.net/forum?id=DiqeZY27XK) | Retain past dynamics across tasks | New task · same state space |
| [EvoAgent](https://arxiv.org/abs/2502.05907) | Self-reflection · curriculum on Minecraft | Long-horizon experience |
| [CAMA / embodied continual](https://openreview.net/forum?id=7M0EzjugaN) | Confidence-based adaptation | Behavior / environment change |

These ask how to **absorb** new experience, **preserve** old knowledge, or **adapt** to change — not whether the current model **class** is fundamentally wrong.

**Paper 002 gap:** repair within class vs **structural** expansion — a decision **before** continual update strategy.

---

## 3. Closest structural adaptation work (required citations)

This subsection is mandatory. “Add expert after anomaly” alone is **not** novel.

### TMoW — Test-Time Mixtures of World Models

[arXiv:2601.22647](https://arxiv.org/abs/2601.22647) · routes among world models at test time · few-shot integration of new models for dynamic environments.

| TMoW | Paper 002 |
| --- | --- |
| **How** to expand · route · refine prototypes | **Whether / when** expansion is **warranted** |
| Unseen **domain** · test-time mixture | **Task failure** after failed **parameter repair** |
| Embodied task outcomes | + **L1 vs L3 arm comparison** · nominal regression guardrail |

### MuSix — Multi-scale Mixture of World Models

[arXiv:2607.00457](https://arxiv.org/abs/2607.00457) · selects WM scale by novelty / experiential distance · different update rates per scale.

| MuSix | Paper 002 |
| --- | --- |
| Environment change · experience distance | **Structured residual** after *K* parameter updates |
| Scale selection | Model-class **adequacy** test |

### Worldscape-MoE

[arXiv:2607.03964](https://arxiv.org/abs/2607.03964) · diffusion-transformer WM · progressive **control-specific experts** for new action modalities.

| Worldscape-MoE | Paper 002 |
| --- | --- |
| Action modality coverage · shared physics | **Failure diagnosis** · repair vs expansion |
| Progressive MoE tuning | Deployment **task failure** as evidence |

L3 arm (add drift expert) is **structurally similar** — differentiation is **trigger + adequacy test + behavioral validation**, not expert addition per se.

### LMC — Local Module Composition

[OpenReview](https://openreview.net/forum?id=LJjC6DmSkgT) · input-distribution outlier → new module · local structural relevance.

| LMC | Paper 002 |
| --- | --- |
| **Observation OOD** | **Action-conditioned prediction failure** + task consequence |
| Module creation | Parameter repair **insufficiency** as gate |

---

## 4. Structural and causal world-model adaptation (program horizon)

Longer-term neighbors — Paper 002 is a **restricted confirmatory cell**, not full causal discovery:

| Work | Link |
| --- | --- |
| Variational Causal Dynamics | [OpenReview](https://openreview.net/forum?id=a1ttBXvNCLO) |
| Dynamic predicate invention | [OpenReview](https://openreview.net/forum?id=jJbzfjODQt) |
| Compositional world models | [OpenReview](https://openreview.net/forum?id=EHmjRIA4l2) |

These target invariant mechanisms, symbolic repair, or compositional abstractions. Paper 002 tests one **prepared** operator (drift expert + gating) under hidden-mode control.

---

## 5. Generative and diffusion world models

Industry and academia move toward foundation-scale video / action world models ([Cosmos](https://blogs.nvidia.com/blog/cosmos-world-foundation-models/), [World Action Models](https://arxiv.org/abs/2605.12090)). Worldscape-MoE combines diffusion transformers with experts.

**Boundary:** diffusion expresses **multimodal futures within current support**. Paper 002 asks when the **generative / dynamics family itself** is inadequate.

```text
confirmatory v0.1:  modular dynamics expert (L3)
extension:          deterministic vs diffusion vs discrete experts
```

Diffusion remains an **expansion operator candidate**, not the v0.1 confirmatory arm ([taxonomy](paper002_wm_system_expansion_v0.1.md)).

---

## 6. Failure detection, uncertainty, and model inadequacy

Three distinctions (must be explicit in method):

| Type | Meaning | Paper 002? |
| --- | --- | --- |
| Distribution shift | Input distribution changed | Related · not sufficient alone |
| Epistemic uncertainty | Model lacks knowledge | Related · not sufficient alone |
| **Structural inadequacy** | No stable explanation within current model **class** | **Primary novelty** |

**Adequacy gate (pre-specified · not τ alone):**

```text
structured residual persists
after K parameter-update attempts
AND is conditionally predictable under alternative model class
(provisional mode cluster / prepared expert explains held-out trajectories)
```

Evidence must show: **repeats** · **mode-associated** · **not absorbed by L1 repair** · **L3 explains out-of-sample**.

---

## Positioning matrix

| Line | What changes | Trigger | Structure | Behavior link | vs Paper 002 |
| --- | --- | --- | ---: | --- | --- |
| Latent WM | latent / weights | training loss | low | planning / policy | adequacy not tested |
| Continual WM | knowledge / weights | new task / data | limited | yes | no repair vs expansion test |
| LMC | modules | input outlier | yes | task perf | OOD not task failure |
| **TMoW** | mixture / router | unseen domain | yes | embodied | no failure-after-repair gate |
| **MuSix** | multi-scale WM | experiential novelty | yes | adaptation | no L1 vs L3 comparison |
| **Worldscape-MoE** | control experts | new modality | yes | generation / control | modality not deployment failure |
| Causal WM | mechanisms | intervention | yes | prediction | unconstrained discovery |
| **Paper 002** | param **or** expert | unexplained task failure | **core compare** | pred · control · recoverability | **nominal regression** |

---

## Manuscript paragraph (draft)

World models learn predictive representations of action-conditioned environmental dynamics and support planning, policy learning, simulation, evaluation, and synthetic experience generation. Recent robot-learning research has expanded this paradigm from compact latent dynamics models toward foundation-scale video and action world models. However, most approaches assume a fixed representational or architectural family and adapt its latent state or parameters as new observations arrive.

Continual world-model methods focus primarily on incorporating new experience while preserving previously acquired dynamics or task knowledge. Modular approaches move beyond monolithic adaptation by routing among multiple models or adding experts. Test-time Mixtures of World Models refine routing and construct new world models for unseen domains, while multi-scale mixtures update world knowledge at different rates across abstraction levels. Recent diffusion-transformer world models also support progressive extension through shared and control-specific experts. These methods establish that modularity can improve adaptation and scalability, but they generally begin from detected domain novelty, new task distributions, or additional control modalities rather than testing whether observed **task failure** specifically invalidates the current model class after **parameter repair has failed**.

A related body of work studies compositional and causal world models. Such methods factorize transition mechanisms, identify sparse environmental changes, or invent symbolic predicates to repair an insufficient causal representation. These approaches motivate structural adaptation but often assume predefined intervention settings or address unconstrained causal and symbolic discovery, which lies beyond the scope of the present study.

We instead study a restricted model-adequacy decision in an embodied control setting. Given an unexplained failure, we ask whether parameter-level repair within the current dynamics model is sufficient or whether a prepared model-class expansion operator is required. Our central comparison is therefore not between alternative latent representations alone, but between no adaptation, parameter adaptation, and modular structural expansion. Latent reorganization provides mechanistic evidence, while the primary outcomes are prediction, action selection, recoverability, and retention on nominal conditions.

---

## References (anchor · verify at submission)

| ID | Work | URL |
| --- | --- | --- |
| TMoW | Test-Time Mixture of World Models | [arXiv:2601.22647](https://arxiv.org/abs/2601.22647) |
| MuSix | Multi-scale Mixture of World Models | [arXiv:2607.00457](https://arxiv.org/abs/2607.00457) |
| Worldscape-MoE | Unified MoE World Model | [arXiv:2607.03964](https://arxiv.org/abs/2607.03964) |
| LMC | Local Module Composition | [OpenReview](https://openreview.net/forum?id=LJjC6DmSkgT) |
| WM survey | World Model for Robot Learning | [arXiv:2605.00080](https://arxiv.org/abs/2605.00080) |
| WAM | World Action Models | [arXiv:2605.12090](https://arxiv.org/abs/2605.12090) |
| Paper 001 | Same-state recoverability @ **S** | [../paper1/status.md](../paper1/status.md) |

---

## Links

| Doc | Path |
| --- | --- |
| Description | [paper002_description_wm_expansion_v0.1.md](paper002_description_wm_expansion_v0.1.md) |
| Industry context (brief) | [paper002_industry_context_v0.1.md](paper002_industry_context_v0.1.md) |
| Pre-reg | [paper002_prereg_wm_expansion_v0.1.md](paper002_prereg_wm_expansion_v0.1.md) |
| Mock→physics RW (archived) | [paper002_related_work_v0.1.md](paper002_related_work_v0.1.md) |
