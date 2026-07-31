# Paper 003 — Description · missing relation & capability expansion v0.1

> **Program L0:** When reality cannot be explained by the agent's **model class**, how should an embodied system revise **parameters and the architecture/composition** of its world-modeling system?
> **RQ:** [paper003_rq_v0.1.md](paper003_rq_v0.1.md)

---

## Working title

**Beyond Error Reduction: Does Structural Expansion Enable Task Capability That Repair Cannot?**

---

## Central question

> Can persistent, structured task failures reveal a missing **causal relation** in the agent's model class — and does adding a prepared relation-module expansion, once activated, expand the space of **achievable tasks** beyond what parameter repair or a single mode-expert reaches, without regressing non-relational baseline performance?

Recoverability / error reduction is a **measurement window**, not the claim. The claim is about the **achievable-task space** before vs after expansion.

---

## Conceptual frame

| | Parameter update (L1) | Mode expansion (L3, Paper 002) | Relation expansion (L3, Paper 003) |
| --- | --- | --- | --- |
| Failure meaning | Wrong value in known state | Missing regime/mode | **Missing dependency between two entities** |
| Action | Re-estimate value | Add mode/expert + gating | Add relation module (e.g. pairwise interaction term) |
| Test | Residual shrinks under same representation | Residual explained by regime label | Residual explained by **second entity's state**, not by regime alone |
| Success metric (Paper 002) | — | Prediction error ↓, recoverability ↑ | Same, **plus** capability threshold crossing (below) |

---

## Minimal environment (locked v0.1)

**Simulator: Isaac Sim / ORBIT Reach, continuing Paper 002's environment** (not a cheaper proxy). Paper 002's own mock→physics rank-transfer direction was tried and archived — building a separate proxy for Paper 003 repeats a path this program already closed out. Reusing Isaac keeps the controller, VESSL runbook, and M0/M1 baseline directly comparable.

**Relation form: physical coupling.** A second dynamic body (`reference_object`) intermittently contacts and displaces the target — target's dynamics depend on `reference_object_position`, hidden from the initial agent WM. Chosen over occlusion-dependent (too close to a perception problem, muddies the "missing relation in dynamics" claim) and multi-agent (adds a second controllable agent, out of scope for a restricted first cell).

**Initial agent representation:**

```text
state = target_position   (independent-entity assumption, same as Paper 002 M0)
```

Agent cannot represent the coupling → repeated position-estimation error that looks identical to Paper 002's drift failure at the residual level, but has a different generating cause.

**Task family for capability measurement:** a graded set of task variants where success requires exploiting the relation with increasing severity (e.g. increasing coupling strength, decreasing time-to-contact). Some variants are constructed to be **~0% achievable under L0/L1/L3-mode by design** — the point at which RQ-3 is tested.

---

## Protocol (two-encounter, reused from Paper 002)

### Episode 1 — unexplained failure

```text
Independent-entity assumption → relation-driven deviation → persistent prediction error → recovery fails
```

Evidence needed: parameter-only updates **and** mode-only expansion both fail to absorb the structured residual.

### Competing update arms (between Ep1 and Ep2)

| Arm | Level | Mechanism |
| --- | --- | --- |
| A No update | — | frozen M0 |
| B Parameter update | L1 | θ update, independent-entity model |
| C Mode expansion | L3-mode | Paper-002-style expert + gating (control — should **not** fix a relational gap) |
| D Relation expansion | L3-relation | add relation module (pairwise term / graph edge) |

Arm C is the key discriminating control: if mode expansion also "fixes" the failure, the residual was not diagnostic of a missing relation and RQ-1 fails.

### Episode 2 — novel but related

Change: start pose, coupling strength, relative timing.
**Hold fixed:** hidden structure = relation exists and is active.

---

## Expansion gate (parsimony · reused logic, new signature)

Do not expand on first failure. Expand into a relation module only when:

```text
structured residual persists after K parameter-update attempts
+ residual NOT absorbed by mode expansion (arm C)
+ residual correlates with second entity's state (not with time/regime alone)
→ candidate relational gap → invoke prepared relation-module operator
```

Distinguishing signature vs Paper 002: mode expansion absorbs regime-correlated residual; relation expansion is needed when residual instead correlates with a **second entity's trajectory**.

---

## Primary outcomes

| Metric | Role | Source |
| --- | --- | --- |
| Next-state prediction error | Prediction | reused from Paper 002 |
| Mismatch detection latency | Diagnosis | reused |
| Correct response/arm selection | Decision | reused |
| Task success / recoverability | Outcome (window) | reused |
| Static/independent-entity regression | Guardrail | reused |
| **Capability threshold crossing** | **Primary novel outcome** | new — see below |

### Capability threshold crossing (definition draft)

For a preregistered task-variant set `T` (graded by relation severity) and each arm `a`:

```text
success_rate(t, a)  for t in T

capability_crossing(a) = |{ t in T : success_rate(t, A_baseline) ≈ 0
                                     AND success_rate(t, a) > threshold }|
```

- `A_baseline` = best of {No update, Parameter update} (arms A/B)
- `threshold` prereg'd (e.g. >20%, non-trivial and above chance/floor)
- Compare `capability_crossing(D relation)` vs `capability_crossing(C mode)` vs `capability_crossing(B parameter)`

**Success pattern:** Relation expansion (D) crosses capability thresholds on relation-dependent variants that mode expansion (C) and parameter repair (B) do not — not merely a lower mean error.

---

## Defensible claim (draft)

> **Capability-conditioned model-adequacy testing:** persistent structured task failures that survive both parameter repair and mode expansion justify invoking a prepared relation-module operator, converting previously unachievable task variants into achievable ones — a claim about the achievable-task space, not only about prediction error — with no regression on non-relational tasks.

**Not claimed:** general causal discovery, relation invention outside the prepared operator, capability emergence outside the tested task family.

---

## Open design questions (to resolve before prereg)

- [x] Concrete simulator choice — Isaac Sim / ORBIT Reach, continuing Paper 002 (locked 2026-07-31)
- [x] Exact form of the relation — physical coupling via `reference_object` (locked 2026-07-31)
- [ ] Threshold value(s) for capability crossing — needs prereg, not post-hoc
- [ ] Whether Arm C (mode expansion) needs its own sub-gate or can reuse Paper 002's trained expert directly

---

## Links

| Doc | Path |
| --- | --- |
| RQ | [paper003_rq_v0.1.md](paper003_rq_v0.1.md) |
| Related work | [paper003_related_work_v0.1.md](paper003_related_work_v0.1.md) |
| Paper 002 description (parent method) | [paper002_description_wm_expansion_v0.1.md](../paper002/paper002_description_wm_expansion_v0.1.md) |
| Expansion taxonomy | [paper002_wm_system_expansion_v0.1.md](../paper002/paper002_wm_system_expansion_v0.1.md) |

---

## Version history

| Version | Date | Note |
| --- | --- | --- |
| v0.1 | 2026-07-31 | Initial method draft — relation expansion + capability threshold crossing metric |
| v0.1 (update) | 2026-07-31 | Locked environment: Isaac Sim/ORBIT Reach continuation + physical-coupling relation form |
