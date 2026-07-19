# EXP-SURG-001 Study 1 — Pre-Registration

> **Date:** 2026-07-16 · **Status:** method lock **v0.3** · **Paper RQ v0.5** (A/B/C · RESHAPE first-class)
> **Paper 1 RQ:** [`research_question.md`](../../../docs/paper1/research_question.md)  
> **This doc:** **Study 1 = Counterfactual recovery atlas** (+ property ablations). Include **one** RESHAPE skill in next config bump.  
> **Config:** [`config/study1_execute_or_defer.yaml`](config/study1_execute_or_defer.yaml)
> **Rule:** Do not change primary endpoints or baseline IDs after first reported seed without a new version tag.
> **Next pre-reg bump (v0.4→v0.5):** modes `+ RESHAPE` · delay checkpoints · modifiability flags · recoverability gain / newly enabled success · imperfect human · pick camera **or** rigid displace.

---

## 1. Research questions

**Paper 1 (v0.4):** Does joint prediction of response feasibility + remaining recovery time beat UQ→handover / fixed recovery on successful resolution?

**Study 1 deep Q (this pre-reg):** Which properties / counterfactual outcomes make a mode **outcome-feasible** at a given delay — and which characterization fields are necessary?

**Empirical RQ (v0.3 block — still executed inside atlas):** Does a learned selector conditioned on **response-relevant characterization** improve the safety–task-disruption–human-assistance Pareto vs **scalar uncertainty gating** — and which properties are necessary?

**H1:** **B6** ≻ **B2** @ matched safety (handover ↓, disruption ↓, success ≥).  
**H2:** Property ablations **B5a–d** identify necessary fields.  
**H3:** **B3** = sanity only.  
**H4:** **B6** ≻ **B4** (multi-mode vs binary).  
**H0:** Characterization unused.

---

## 2. Anti-circularity + feasibility labels (RoboAbstention principle)

1. Prefer response from **environment counterfactuals**, not type→label:

```yaml
safe_alternative_path_exists: bool
visibility_recoverable: bool
target_reachable: bool
current_path_intersects_forbidden: bool
```

2. Pipeline: fix physical conditions → compute feasible responses → generate observation/language.  
3. Same type → ≥2 preferred modes by severity/feasibility.  
4. **B3** = oracle characterization + utility-optimal; **not** a positive claim.  
5. Primary metrics = **outcomes**, not label agreement.

---

## 3. Task

| Field | Spec |
| --- | --- |
| Platform | ORBIT Reach (`Isaac-Reach-Dual-STAR-IK-Rel-Play-v0` or documented successor) |
| Skill | Constrained target reach + forbidden region |
| Language | Fixed commands; **P5 exploratory only** |
| Proposer | **Option A (Paper 1 preferred):** frozen **BC ensemble** (e.g. 5×MLP) for honest Surgical-UQ-style variance · **Option B (smoke):** scripted/zero → B2 = **scalar risk gate** (never “policy UQ”) |

**Month 1 smoke:** Option B OK if labeled. **Report:** Option A preferred (matches Surgical UQ baseline honesty).

---

## 4. Perturbations — within-type branching

| ID | Family | Feasibility-driven preferred mode (examples) |
| --- | --- | --- |
| P0 | Nominal | continue |
| P1a | Obs delay | recoverable → reobserve · persistent → handover · mild+margin → continue |
| P1b/c | Action noise / latency | optional |
| P2 | Target shift | reachable → replan · unreachable → handover · post-goal → continue |
| P3 | Occlusion | recoverable view → reobserve · persistent loss → handover |
| P4 | Forbidden | alt path → replan · no path → handover · near safe → continue |
| P5 | Instruction | exploratory |

**Paper 1 minimum:** P0, P1a, P2, P3, P4 with ≥2 severities flipping preferred mode.

Taxonomy: [`config/exception_taxonomy.yaml`](config/exception_taxonomy.yaml)

---

## 5. Response-relevant characterization

```text
source / type
severity
timing
predicted_consequence       # if continue
information_deficit
recoverability              # e.g. visibility_recoverable
alternative_feasibility     # e.g. safe_alternative_path_exists
```

**B6:** inferred (or noisy oracle) full vector.  
**B3:** oracle full vector.  
**B5a–d:** nested subsets (see §7).

---

## 6. Response set (v1)

```text
CONTINUE · REOBSERVE · REPLAN · HANDOVER
```

---

## 7. Baselines (locked v0.3)

| ID | Name | Role |
| --- | --- | --- |
| **B0** | Always continue | Floor |
| **B1** | Always handover after mismatch alarm | Surgical UQ extreme |
| **B2** | Best scalar uncertainty **or** risk threshold | **Primary competitor** (UQ / KnowNo-family gate) |
| **B3** | Oracle characterization + utility-optimal | **Sanity only** |
| **B4** | Learned binary execute/handover | RoboAbstention / KnowNo-like binary |
| **B5** | Multi-response, no characterization | Capacity ablation |
| **B5a** | Multi + type/source | Property ablation |
| **B5b** | + severity | Property ablation |
| **B5c** | + predicted consequence | Property ablation |
| **B5d** | + recoverability + info deficit + feasibility | Property ablation |
| **B6** | Full characterization | **Primary system** |

### Critical comparisons

```text
B6 vs B2   → H1 system vs scalar gate
B6 vs B5   → any characterization?
B5a…B5d vs B5 / vs B6  → which properties are necessary? (deep Q)
B6 vs B4   → multi-mode vs binary
B3 vs B2   → sanity only
```

---

## 8. Metrics

### Primary

| # | Metric |
| ---: | --- |
| P1 | Catastrophic violation rate + max / integrated penetration |
| P2 | Task success @ matched safety |
| P3 | Full **handover** rate @ matched safety (human-assistance **proxy**) |
| P4 | Task disruption cost |
| P5 | Safety–assistance Pareto / hypervolume |

Matched safety: catastrophic rate **and** mean integrated penetration — not binary penetration alone.

### Secondary

reobserve/replan/handover/non_continue rates · completion time · early-warning · label agreement (diagnostic) · composite score sensitivity (3 weight schemes)

### Deprecated as primary

`intervention = any non-continue` · sole weighted score · taxonomy accuracy

---

## 9. Data and seeds

Smoke: 1 seed · ≥20 ep · P0 + ≥1 branched family.  
Report: seeds `[0,1,2,3,4]`. Target ~500+1500 (adjust).

---

## 10. Analysis plan

1. B0–B6 (+ B5a–d) on primary endpoints.  
2. H1: B6 vs B2 @ matched safety.  
3. Deep Q: nested ablations B5 → B5a → … → B6.  
4. H4: B6 vs B4.  
5. Sanity: B3 vs B2.  
6. Per-family / severity.  
7. Weight sensitivity.  
8. H0 → Go/No-Go pivot.

---

## 11. Success / Go–No-Go

| Result | Action |
| --- | --- |
| B6 ≻ B2; ablation informative | Draft / Month 5–6 |
| B3 ≻ B2, B6 ≰ B2 | Improve inference — not claim system win |
| B5a ≈ B6 | Type alone enough — simplify claim |
| H0 | Pivot |

---

## 12. Non-goals

PPO/VLA/FM · detection AUROC as claim · IRB surgeon burden · circular type→label accuracy · “only stop/handover exists in prior work”

---

## 13. Versioning

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-07-16 | type-aware; B3 primary-eligible |
| 0.2 | 2026-07-16 | characterization; B0–B6; Pareto |
| **0.3** | 2026-07-16 | Deep Q; B5a–d; feasibility labels; five-paper map |

---

## Checklist before smoke

- [x] RQ v0.3 + related work five-paper map
- [x] Feasibility-based preferred modes
- [x] B0–B6 + B5a–d named
- [x] B3 sanity-only
- [ ] Proposer Option A or B labeled in evidence JSON
- [ ] Feasibility flags implemented in generator
- [ ] ≥2 severities per smoke family
