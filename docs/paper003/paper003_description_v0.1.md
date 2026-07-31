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

## CPU-proxy design evidence (2026-07-31)

Implemented in [`scripts/wm_expansion/relation_dynamics.py`](../../scripts/wm_expansion/relation_dynamics.py), pinned by [`scripts/test_paper003_relation_dynamics.py`](../../scripts/test_paper003_relation_dynamics.py). Design-stage only — **not preregistered, not run in Isaac.**

### What the coupling has to look like

The first two coupling designs failed, and the failures are informative:

| Design | Outcome | Why it fails |
| --- | --- | --- |
| Reference sweeps past once | Sustained one-directional push (directional consistency 0.92) | Looks like drift → **arm C absorbs it** → no contribution over Paper 002 |
| Reference oscillates at an offset | Target escapes the band after the first bump | Phenomenon dies out; no sustained signal |
| **Reference oscillates *through* the target band** | Repeated, direction-alternating bumps | Constant velocity cannot extrapolate it — this is the usable design |

The relation must produce **episodic, direction-varying** motion. A coupling that produces smooth drift is a Paper 002 experiment wearing a different label.

### Gate separation achieved

Two statistics, both required to fire (positive evidence + negative evidence against arm C):

| Case | `proximity_contrast` | `constant_velocity_gain` | Gate fires |
| --- | ---: | ---: | :---: |
| **Coupling (relation present)** | +1.000 | −0.641 | **10/10** |
| Drift (Paper 002 positive) | −1.000 | +0.899 | 0/10 |
| Static | 0.000 | 0.000 | 0/10 |
| Observation noise | −1.000 | −9.049 | 0/10 |

The drift row is the important one: the relation gate stays silent on exactly the condition Paper 002's gate fires on.

### The finding that constrains the endpoint

Open-loop H=10 prediction error under coupling, 10 seeds:

| Arm | Error |
| --- | ---: |
| B zero-order | 9.35 mm |
| C constant velocity | 9.96 mm (worse than B — CV actively hurts) |
| **D relation** | **8.21 mm** |

Arm D wins, but by **~1.1 mm** — against Paper 002's 10.8 mm C−B gap and its 5 mm preregistered criterion. Sweeping coupling gain 0.4→0.8 and geometry *shrinks* the advantage (best observed −1.66 mm), because a stronger push ejects the target from the interaction zone faster and makes the forward roll-out less accurate.

**Consequence:** Paper 003 cannot rest on a Paper-002-style prediction-error contrast. This is not a setback for the RQ — it is the RQ. The paper's claim was always about achievable-task space rather than error reduction, and this result says that framing is *required*, not optional. It also raises the stakes: the capability-crossing effect must be demonstrated in closed loop, and it has not been yet.

---

## Closed-loop capability probe — first attempt, NOT successful (2026-07-31)

The capability-threshold-crossing endpoint is the paper's whole claim, so it was probed directly on the CPU proxy. **No capability gap was produced.** Recorded here because it is a live risk to the premise, not a detail.

### What was tried, in order

| Step | Result |
| --- | --- |
| Coupling without an anchor | Target is repelled out of the interaction zone and **settles** (moves 15 of 119 steps). No sustained phenomenon; every arm succeeds because a static target is trivially reachable. |
| Coupling with an elastic anchor (target springs back, gets hit again) | Sustained indefinitely — 113/119 moving steps, no decay. This is the usable world. |
| Closed loop, aim a fixed *H* steps ahead | Arm D **worse** than B and C. Control-law error, not a model error: aiming a constant horizon ahead leaves the effector perpetually leading the target and never coincident with it. |
| Closed loop, interception control (horizon = estimated time-to-arrival) | Correct law, but **all three arms perform identically** across a tolerance × coupling-speed grid (see below). |

### The tension this exposes

Open-loop prediction in the anchored world separates the arms **strongly** — comparable to Paper 002:

| Horizon | B zero-order | C constant velocity | D relation |
| ---: | ---: | ---: | ---: |
| H=3 | 9.36 mm | 9.07 mm | **3.83 mm** |
| H=5 | 13.08 mm | 18.43 mm | **4.64 mm** |
| H=10 | 14.82 mm | 38.68 mm | **4.52 mm** |

(period 20; arm C is *catastrophically* worse than zero-order, as velocity extrapolation should be on an oscillation.)

But closed-loop task success does not separate at all:

| Tolerance | Period | B | C | D |
| ---: | ---: | ---: | ---: | ---: |
| 6 mm | 20 / 12 / 8 | 1.00 | 1.00 | 1.00 |
| 4 mm | 8 | 0.35 | 0.35 | 0.45 |
| 3 mm | 20 | 0.30 | 0.25 | 0.35 |
| 2 mm | any | 0.00 | 0.00 | 0.00 |

Success degrades with tolerance for *all* arms simultaneously and never opens a window where B and C are at zero while D succeeds.

### Diagnosis

In a continuous reach-and-hold task, the binding constraint is not *where the target will be* but *whether the effector can match the target's instantaneous motion*. The target moves ~3.6 mm/step; holding a 2–3 mm tolerance requires velocity matching, which none of the arms do — they all aim at a point. Conversely, at loose tolerance every arm succeeds by hovering near the oscillation's mean, which zero-order tracking finds for free.

**Implication for the design:** a continuous-tracking task cannot express capability threshold crossing here. The metric likely needs a task with a **commitment point** — a moment where the agent must commit an irreversible action (grasp, intercept, place) and a wrong prediction fails outright, rather than being averaged away by continuous re-aiming. Designing that task is the open item that now gates the prereg.

This does not falsify the RQ, but it does mean the central endpoint is **unvalidated**, and the paper should not be preregistered until a task is found that produces the transition.

---

## Open design questions (to resolve before prereg)

- [x] Concrete simulator choice — Isaac Sim / ORBIT Reach, continuing Paper 002 (locked 2026-07-31)
- [x] Exact form of the relation — physical coupling via an oscillating `reference_object` that sweeps through the target band (locked 2026-07-31; a single pass-by is disqualified, see above)
- [ ] **A task with a commitment point** — blocking. The first closed-loop probe (above) failed to produce a capability threshold in a continuous reach-and-hold task; a task where a wrong prediction fails outright is needed before the endpoint is credible
- [ ] Decide whether the elastic anchor becomes part of the specified environment (it is what makes the phenomenon sustained, but it is intrinsic target dynamics, not the relation itself — arms B and C should arguably be given it too)
- [ ] Threshold value(s) for capability crossing — needs prereg, not post-hoc
- [ ] Re-derive gate thresholds from Isaac data — the CPU proxy has no contact noise and gives an unrealistically clean `proximity_contrast` of exactly 1.0
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
