# Paper 002 — Description · world-model expansion v0.1

> **Program L0:** When reality cannot be explained by the agent’s **model class**, how should an embodied system revise **parameters and the architecture/composition** of its world-modeling system?  
> **Architecture note:** [paper002_wm_system_expansion_v0.1.md](paper002_wm_system_expansion_v0.1.md)

---

## Working title

**When Parameter Update Is Not Enough: Structural World-Model Expansion from Unexplained Failures in Embodied Simulation**

---

## Central question

> **Can persistent, structured task failures provide evidence that the current dynamics model class is inadequate — and does selecting a prepared structural expansion operator improve prediction and control on novel related encounters beyond parameter-only repair, without nominal regression?**

Paper 002 v0.1 tests **one** adequacy decision: **L1 parameter repair insufficient** → invoke **L3** operator (add dynamics expert M₁ + gating) vs L1 vs no update.

Recoverability is a **measurement window**, not the program center.

**Related work:** [paper002_related_work_v0.2.md](paper002_related_work_v0.2.md) · closest prior: TMoW · MuSix · Worldscape-MoE · LMC.

---

## Conceptual frame

| | Parameter update | Structural expansion |
| --- | --- | --- |
| Failure meaning | Wrong value in known state | **Missing variable, mode, or relation** |
| Action | Re-estimate position, friction, noise | Add `target_mode`, dynamics mode, etc. |
| Test | Residual shrinks under same representation | Residual **persists** until representation changes |

---

## Minimal environment

**True simulator:** `target_mode ∈ {static, drifting}` (hidden from initial agent WM)

**Initial agent representation:**

```text
state = target_position   (static target assumed)
```

Agent cannot represent drift → interprets as repeated position-estimation error.

---

## Protocol (two-encounter)

### Episode 1 — unexplained failure

```text
Static assumption → target drifts → persistent prediction error → recovery fails
```

Evidence needed: **parameter-only updates do not absorb structured residual.**

### Competing update arms (between Ep1 and Ep2)

| Arm | Expansion level | Mechanism |
| --- | --- | --- |
| **No Update** | — | frozen M₀ |
| **Parameter Update** | L1 | θ on static dynamics only |
| **Modular expansion** | L3 | add expert M₁ (drift) + regime gating |

**Deferred arms (extension):** monolithic fine-tune · diffusion future generator · M₂ external perturb.

Diffusion is an **expansion operator candidate**, not the whole world model — see [taxonomy doc](paper002_wm_system_expansion_v0.1.md).

### Episode 2 — novel but related

Change: start pose · drift direction · drift speed · mismatch onset  
**Hold fixed:** hidden structure = drifting mode  

Avoid pure memorization of Ep1.

---

## Expansion gate (parsimony · model-adequacy test)

Do **not** expand on first failure. Expand only when evidence supports **structural inadequacy** (not distribution shift or uncertainty alone):

```text
structured residual persists
after K parameter-update attempts
+ errors cluster by provisional mode / hidden condition
+ not absorbed by L1 repair on Ep1
→ candidate structural gap → invoke prepared L3 operator
```

Three-way distinction (method text): distribution shift · epistemic uncertainty · **structural inadequacy** (Paper 002 target).

---

## Primary outcomes (Ep2 · vs Ep1 baseline)

| Metric | Role |
| --- | --- |
| Next-state prediction error | Prediction |
| Mismatch detection latency | Diagnosis |
| Correct response selection | Decision |
| Task success / recoverability | Outcome (window) |
| Repeated failure rate | Utility |
| Static-condition regression | Guardrail |

**Success pattern:** Structural Expansion > Parameter Update > No Update on **novel drift** · **no harm** on static nominal.

---

## Defensible claim (first paper)

> **Failure-conditioned model-adequacy testing:** persistent structured task failures justify switching from parameter repair to a **prepared** model-class expansion operator, improving **prediction and control** on novel related encounters beyond parameter-only adaptation — with latent reorganization as **observed mechanism**, not primary claim.

**Not claimed:** adding experts alone (TMoW · Worldscape-MoE precedent) · latent representation learning SOTA · arbitrary z invention without behavior gain · unconstrained causal ontology invention.

---

## Figure 1 (storyboard)

```text
A. Reality — unobserved motion mode
B. Initial WM — position only
C. Failure — persistent mismatch
D. Parameter update vs structural expansion
E. Next encounter — mode predicted · action changed
F. Evaluation — improved prediction/recovery · no static regression
```

Layout: **Primary results table** (L1 repair failure on Ep1 → L3 advantage on Ep2 · Layer 3) · **Reality | Agent belief** · **Latent before/after** (Fig 4 · supporting · mechanistic secondary).

---

## Program position

```text
L0  Representation reconstruction under model-inadequate reality
Paper 001 (optional)  Recoverability @ S — credential · measurement window
Paper 002 (this)      Missing dynamic mode — detect · expand · validate
Next                  Missing relations / causal variables
Later                 Human-provided representation · surgical exceptions
```

Paper 001 **not required** as logical prerequisite.

---

## Links

| Doc | Path |
| --- | --- |
| Confirmatory spec | [paper002_confirmatory_spec_v0.1.md](paper002_confirmatory_spec_v0.1.md) |
| Pre-reg skeleton | [paper002_prereg_wm_expansion_v0.1.md](paper002_prereg_wm_expansion_v0.1.md) |
| Related work | [paper002_related_work_v0.2.md](paper002_related_work_v0.2.md) |
| Industry context | [paper002_industry_context_v0.1.md](paper002_industry_context_v0.1.md) |
| Status | [status.md](status.md) |
| Archive (mock→physics) | [archive/mock_to_physics/](archive/mock_to_physics/) |
