# World-model system · expansion levels · taxonomy v0.1

> **Program doc** · Paper 002 uses a **minimal slice** of this · [description](paper002_description_wm_expansion_v0.1.md)

---

## L0 (v2)

> **When reality cannot be explained by the agent’s current model class, how should an embodied system revise not only its parameters, but the architecture and composition of its world-modeling system?**

Experimental question:

> **Can unexplained failure trigger the selection or construction of a more adequate world-model architecture, improving future prediction and control without catastrophic regression?**

Recoverability = **measurement window** for whether reconstruction helped · not the program center.

---

## World model = system (not one network)

```text
Observation encoder
        ↓
Latent state / belief
        ↓
Dynamics or video predictor
        ↓
Possible future trajectories
        ↓
Planner / value / risk estimator
        ↓
Policy or controller
```

**Diffusion** may implement:

- dynamics / video generator (multimodal futures)
- diffusion policy
- latent planner

Diffusion ≠ entire world model. It is one **expansion operator** candidate (multimodal futures), not automatic invention of new mechanisms outside training support.

---

## Four expansion levels

| Level | What changes | Example | Paper 002? |
| --- | --- | --- | --- |
| **L1 Parameter** | Same architecture · θ → θ′ | friction estimate · encoder FT · score-net update | **Baseline arm** |
| **L2 Latent reorganize** | Same size · new factorization in z | static vs drift clusters in latent | Weak alone for “structural” claim |
| **L3 Model-class / architecture** | New module · expert · slot · generative family | MoE dynamics · mode inference head · deterministic → multimodal generator | **Primary arm** |
| **L4 System reconstruction** | Adequacy monitor · multi-model · human gate | self-reconstructing stack | Program horizon · not Paper 002 |

Paper 002 confirmatory = **L1 vs L3 (restricted menu)** · L4 deferred.

---

## Computational core

```text
Observation → prediction residual
Can current model class explain it?
├── Yes → parameter / belief update (L1)
└── No  → model reconstruction
          ├── recalibrate uncertainty
          ├── add latent mode / expert (L3)
          ├── add diffusion future generator (L3)
          ├── add relation module (later)
          └── request human / experiment (L4)
```

Question is **not** “how to fine-tune weights?” but **which expansion operator to invoke**.

---

## Expansion operator menu (program)

```text
Expand(model, failure evidence) ∈ {
  recalibrate,
  add_latent_mode,
  add_dynamics_expert,      ← Paper 002 v0.1 primary
  add_diffusion_generator,  ← extension / Paper 003
  add_relation_module,
  system_recompose           ← L4
}
```

First paper: **finite menu** · failure selects among **prepared** operators · not free neural architecture search.

---

## Failure cause → expansion type (taxonomy)

| Failure cause | Appropriate expansion |
| --- | --- |
| Wrong value | parameter update (L1) |
| Underestimated uncertainty | probabilistic recalibration |
| Single deterministic future | diffusion / generative (L3) |
| New dynamics regime | expert / module (L3) · **Paper 002 cell** |
| New entity | object-centric slot |
| New causal relation | graph / causal module |
| Wrong planning interface | system recomposition (L4) |
| Unknown which applies | meta-model / selection |

---

## Paper 002 v0.1 scope (honest)

**True env mechanisms (full program):** M₀ static · M₁ drift · M₂ external perturb (later)

**Initial agent:** only M₀ (deterministic static dynamics)

**Arms (confirmatory v0.1):**

| Arm | Level | Mechanism |
| --- | --- | --- |
| A No update | — | frozen |
| B Parameter | L1 | θ update on M₀ |
| C Modular expansion | L3 | add expert M₁ + gating |

**Extension (not confirmatory v0.1):** monolithic fine-tune · diffusion future model · M₂

**Compare:** C > B > A on novel drift Ep2 · no static regression.

---

## Diffusion — role and limits

**Useful when:** futures are multimodal within learned support.

**Does not solve:** discovering entirely new causal structure (e.g. external actor) without meta-system or prepared operator.

Diffusion = **expanded possibility generator** · expansion **decision** needs separate adequacy / selection layer.

---

## Latent space — experiment substrate, not the claim

**Do not** frame the program as “latent representation expansion” alone — readers will classify it as representation learning.

**Do** run experiments largely in latent world models (RSSM / JEPA-style stack: image → encoder → z → dynamics → prediction) for efficiency and analysis.

### What the paper must show (vs what it must not claim)

| Show | Do not center the claim on |
| --- | --- |
| **The agent’s way of modeling the world changed** (new mode · expert · gating · planner interface) | “Latent representation quality improved” |
| Layer 3 gain: prediction · planning · recoverability | “z split into two clusters” alone |

Most WM papers ask *why latent changed* or optimize *latent representation quality*. This program asks:

> **Is changing / reorganizing latent alone sufficient — or must the world-model system (architecture / composition) be reconstructed?**

That is a larger question than representation learning; recoverability · exception handling · human intervention · shared autonomy sit **downstream of** reconstruction, not as the program title.

### Experiment vs claim (recommended split)

| | Role |
| --- | --- |
| **Experiment space** | Latent world model (efficient · analyzable) |
| **Observation targets** | z before/after · residual · uncertainty · which operator fired |
| **Paper claim** | **Failure-driven world-model reconstruction** improves prediction · control · recoverability |

Research **starts** when the agent (or adequacy monitor) recognizes **current latent / model class is insufficient** — not when we report SOTA latent metrics.

| Role | Latent |
| --- | --- |
| **Claim** | Failure-driven **world-model system** reconstruction improves prediction · planning · recoverability |
| **Observation** | How z reorganizes (clusters · uncertainty · new slots) **supports** the claim |
| **Not sufficient alone** | “z split into two clusters” without behavior gain |

### Three linked layers (required in every paper)

```text
Layer 1  Reality          3D sim · mismatch · trajectories
Layer 2  Latent / belief  before vs after expansion · residual · uncertainty
Layer 3  Behavior         prediction · planning · recoverability · (later) human timing
```

Novelty chain:

```text
Failure → representation change → behavior change → recoverability (measurement window)
```

Reviewer “so what?” must be answered on **Layer 3**, with Layer 2 as mechanistic evidence.

### Expansion trigger (program core)

```text
Current latent / model class
  → prediction residual
  → residual not explained by parameter update
  → latent uncertainty / structured residual rises
  → invoke expansion operator (L3)
  → planner / policy interface may change
```

Research starts at **“latent is insufficient”** (self-recognized inadequacy), not at “we improved latent quality.”

### Figure convention — latent panel (optional Fig 4)

| Panel | Content |
| --- | --- |
| Before failure | single z cluster ●●●●● |
| After expansion | z_static ●●● · z_drift □□□□ |
| Linked | same seed · Ep2 success ↑ on drift · static unchanged |

Always pair with Layer 1 (Reality | Belief) and Layer 3 metrics table.

### Boundary vs prior work

Latent WM (Dreamer · JEPA · RSSM) · continual WM · object-centric models adapt latents under a **fixed model class**. Closest structural neighbors **add modules or route mixtures**:

| Prior | Trigger | Paper 002 difference |
| --- | --- | --- |
| [TMoW](https://arxiv.org/abs/2601.22647) | Unseen domain · test-time mixture | **Task failure after failed L1 repair** · adequacy **necessity test** |
| [MuSix](https://arxiv.org/abs/2607.00457) | Experiential novelty · multi-scale | **Structured residual** after *K* repairs |
| [Worldscape-MoE](https://arxiv.org/abs/2607.03964) | New action modality · MoE | **Deployment failure diagnosis** · L1 vs L3 comparison |
| [LMC](https://openreview.net/forum?id=LJjC6DmSkgT) | Input OOD | **Action-conditioned prediction failure** + task consequence |

**Differentiation (one line):**

> **Whether and when** expansion is warranted — not **how** to expand — validated on prediction · control · recoverability · nominal regression.

Full matrix: [related work v0.2](paper002_related_work_v0.2.md).

---

## Program ladder (non-sequential with Paper 001)

```text
Paper 001  Recoverability @ S (optional credential)
Paper 002  L1 vs L3 · select expansion operator (drift expert)
Next       diffusion vs MoE vs relation · gap-type taxonomy
Later      L4 · human-provided representation · surgical exceptions
```

---

## Figure convention

**Reality | Agent WM system** — not only state vector: show **which module** was added (expert node · gating · optional diffusion head).
