# Paper 002 — Description · world-model expansion v0.1

> **Program L0:** When reality cannot be explained by the agent’s **model class**, how should an embodied system revise **parameters and the architecture/composition** of its world-modeling system?  
> **Architecture note:** [paper002_wm_system_expansion_v0.1.md](paper002_wm_system_expansion_v0.1.md)

---

## Working title

**When Parameter Update Is Not Enough: Structural World-Model Expansion from Unexplained Failures in Embodied Simulation**

---

## Central question

> **Can unexplained failure trigger selection of a more adequate world-model architecture (not parameter tuning alone), improving prediction and control on novel related encounters without nominal regression?**

Paper 002 v0.1 tests **one** L3 operator: **add dynamics expert M₁ (drift)** vs L1 parameter update on fixed M₀.

Recoverability is a **measurement window**, not the program center.

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

1. **No Update** — frozen WM  
2. **Parameter Update** — position / velocity estimates only  
3. **Structural Expansion** — add `target_mode` or motion-mode latent  

### Episode 2 — novel but related

Change: start pose · drift direction · drift speed · mismatch onset  
**Hold fixed:** hidden structure = drifting mode  

Avoid pure memorization of Ep1.

---

## Expansion gate (parsimony)

Do **not** expand on first failure. Allow expansion only when:

```text
persistent structured residual
+ multiple parameter updates fail
+ errors cluster by latent condition
→ candidate structural gap
```

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

> Under a controlled hidden-mode setting, persistent unexplained failures can trigger a representation expansion that improves generalization to related encounters beyond parameter-only adaptation.

**Not claimed:** autonomous concept invention · general WM expansion · clinical deployment.

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

Layout: **Reality | Agent belief** · belief panel gains `motion mode` node after expansion.

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
| Pre-reg skeleton | [paper002_prereg_wm_expansion_v0.1.md](paper002_prereg_wm_expansion_v0.1.md) |
| Status | [status.md](status.md) |
| Archive (mock→physics) | [archive/mock_to_physics/](archive/mock_to_physics/) |
