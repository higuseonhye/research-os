# EXP-SURG-001 — Proportionate Response Selection

> **Paper 1 summary:** [`docs/paper1/README.md`](../../../docs/paper1/README.md) · RQ [`research_question.md`](../../../docs/paper1/research_question.md)  
> **Pre-registration:** [`study1_pre_registration.md`](study1_pre_registration.md)

## Done smokes (Isaac)

| Exp | Question | Report |
| --- | --- | --- |
| **001A** | CONTINUE vs REPLAN @ same onset | [`study1a_report.md`](study1a_report.md) |
| **001B** | REPLAN delay 0–20 @ 3 cm (flat band) | [`study1b_report.md`](study1b_report.md) |
| **001C** | Severity × delay surface (full grid) | [`study1c_report.md`](study1c_report.md) · [`results/study1c_isaac/`](results/study1c_isaac/) |
| **001D** | Occlusion × multi-mode @ 6 cm (D0 + D1 smoke) | [`study1d_report.md`](study1d_report.md) · [`results/study1d_isaac/`](results/study1d_isaac/) · [`d1/`](results/study1d_isaac/d1/) |

**Phase B/C (planning · no GPU):** [`docs/paper1/phase_b_smoke_review.md`](../../../docs/paper1/phase_b_smoke_review.md) · [`phase_c_proper_run_prereg_v1.0.md`](../../../docs/paper1/phase_c_proper_run_prereg_v1.0.md) · [`roadmap.md`](../../../docs/paper1/roadmap.md)

---

## EXP-SURG-001A — Counterfactual Recovery Smoke

**Question:** Same target-shift state → does CONTINUE vs REPLAN change terminal outcome?

| | |
| --- | --- |
| Config | [`config/study1a_counterfactual_target_shift.yaml`](config/study1a_counterfactual_target_shift.yaml) |
| Local mock | `python scripts/run_study1a.py --mock --fallback-small` |
| Isaac / RunPod | `bash scripts/run_study1a_counterfactual_runpod.sh` |
| Isaac script | [`scripts/orbit_reach_study1a_counterfactual.py`](../../../scripts/orbit_reach_study1a_counterfactual.py) |
| Report | [`study1a_report.md`](study1a_report.md) |
| Artifacts | `artifacts/study1a_counterfactual_target_shift/` |

**Acceptance:** branch replay · result table · figures · report (real mp4 on Isaac host).

---

## Paper 1 RQ (locked v1.0)

> **How do intervention choice and start time jointly determine successful resolution after a task-relevant mismatch at fixed state S?**

- RQ: [`docs/paper1/research_question.md`](../../../docs/paper1/research_question.md)
- Pre-registration (Stage 1): [`study1_pre_registration.md`](study1_pre_registration.md)
- Proper-run pre-reg v1.0 (frozen · not run): [`docs/paper1/phase_c_proper_run_prereg_v1.0.md`](../../../docs/paper1/phase_c_proper_run_prereg_v1.0.md)

## Six-month question (program)

> **Does response-relevant characterization enable safer and less disruptive multi-mode response selection than scalar uncertainty gating under a shared safety–assistance trade-off?**

## Working title

**Proportionate Response Selection under Task-Relevant Mismatch in Constrained Surgical Reaching**

(Language-guided removed from Paper 1 title — P5 exploratory only.)

## One line

Frozen proposer produces a motion proposal; a **response policy** selects continue · reobserve · replan · handover. Primary claim: **characterization-conditioned B6** vs **scalar gate B2** on the **safety–disruption–assistance Pareto** — not detection accuracy, not taxonomy label match.

## Core question (precise — Paper 1)

> **In constrained surgical reaching with injected task-relevant mismatches, does a learned response selector conditioned on exception characterization improve the safety–task-disruption–human-assistance Pareto frontier over scalar uncertainty gating?**

한국어: **예외 특성화에 조건화한 학습 대응 선택기가 스칼라 불확실성 gating보다 안전–방해–지원 Pareto를 개선하는가?**

**Anti-circularity:** same exception type must admit ≥2 preferred responses by severity; do not claim novelty by matching taxonomy labels.

```text
Collision-free ≠ clinically appropriate
```

| Field | Value |
| --- | --- |
| Atlas ID | **Q-APPLICABILITY** (L3 execution-decision benchmark) |
| L0 theme | Handle expert exceptions / applicability mismatch |
| L2 prior | AV ODD/MRC structure, KnowNo deferral, RoboAbstention line — **ports exist** |
| L3 contribution | **S-ODD** + **proportionate response** benchmark atop frozen proposer |
| S-ODD spec | [`config/s_odd_needle_reaching.yaml`](config/s_odd_needle_reaching.yaml) |

## System stack

```text
Language command + surgical observation
    → motion proposal (frozen VLA / scripted / ACT — not trained here)
    → uncertainty & risk estimator (ensemble disagreement, CP proxy, kinematic risk, forbidden-region score)
    → response policy  ∈ { Execute | Reobserve | Replan | Defer_to_human }
    → (later: slow · clarify · reduce_autonomy)
    → low-level controller (ORBIT Reach / teleop channel)
```

**Design principle:** Motion generation is **frozen**. The research object is **which response** after mismatch—not **whether** mismatch exists (detection = baseline). Translate AV **MRC/fallback chain** into **S-ODD response menu** for language-conditioned surgical skills.

## AV → surgical translation (program vocabulary)

| Autonomous driving | Surgical robot |
| --- | --- |
| ODD | **S-ODD** — skill operating domain |
| Safety envelope | Forbidden region / tissue constraint |
| Minimal risk condition | Hold / retract / freeze |
| Remote assistance | Surgeon clarification (Study 3) |

Example S-ODD: [`config/s_odd_needle_reaching.yaml`](config/s_odd_needle_reaching.yaml)

## Abstention levels (where we sit)

| Level | Example | Study 1 |
| --- | --- | --- |
| L1 — Hard safety stop | collision / force limit | Baseline only (forbidden region) |
| L2 — Task failure | grasp fail → retry | Out of scope |
| **L3 — Semantic abstention** | ambiguous language, occluded target, feasible but inappropriate | **Primary** |

Perturbations P3–P5 target **semantic** mismatch; P1/P4 include kinematic envelope violations.

## Study 1 — sim benchmark (needle reach + forbidden region)

### Task

- ORBIT Reach (or RCM-constrained proxy): language command specifies target region (e.g. “approach needle entry”).
- **Forbidden region** in workspace (tissue proxy / no-go zone).
- Nominal proposer: frozen checkpoint or scripted reach policy (quality gate **not** required for gate study—use fixed proposer + injected failures).

### Perturbation suite

See [`config/exception_taxonomy.yaml`](config/exception_taxonomy.yaml) v0.4. **Same type → ≥2 preferred outcomes by severity.**

| ID | Family | Notes |
| --- | --- | --- |
| P0 | Nominal | continue |
| P1a | Obs delay | short→reobserve · persistent→handover · mild+margin→continue |
| P1b/c | Action noise / latency | optional (Study 2) |
| P2 | Target shift | small→replan · unreachable→handover |
| P3 | Occlusion | partial→reobserve · persistent→handover |
| P4 | Forbidden path | alt path→replan · none→handover · near→continue |
| P5 | Instruction–scene | exploratory only |

### Baselines (v0.2)

| ID | Description | Role |
| --- | --- | --- |
| **B0** | Always continue | Floor |
| **B1** | Always handover after alarm | Max assistance |
| **B2** | Best scalar uncertainty / risk threshold | **Primary competitor** |
| **B3** | Oracle characterization + utility-optimal | **Sanity only** — not positive claim |
| **B4** | Learned binary execute/handover | Multi-response ablation |
| **B5** | Multi-response, no characterization | Capacity ablation |
| **B5a–d** | Nested characterization subsets | **Property ablation** (deep Q) |
| **B6** | Full characterization | **Primary system** |

### Primary metrics (v0.2)

| Metric | Role |
| --- | --- |
| Catastrophic violation + penetration depth/integral | Safety (matched) |
| Task success @ matched safety | Utility |
| Full **handover** rate @ matched safety | Human-assistance **proxy** |
| Task disruption cost | Disruption |
| Safety–assistance Pareto / hypervolume | Primary trade-off |

**Secondary:** reobserve/replan/handover rates separately; label agreement diagnostic only; weighted score = sensitivity (3 schemes).

**Not primary:** `intervention = any non-continue`; taxonomy label accuracy.

## What this is NOT

| Closed track | Reason |
| --- | --- |
| Novel **detection** mechanism for surgery | PA-01 surgical UQ · EV-WM — cite as baselines |
| Binary execute-or-stop only | PA-01, KnowNo — extend to **response menu** |
| “Robots should stop when unsafe” (generic) | AV / ISO — decades settled |
| EXP-SAFE-001 GRU detector scaling | Run 0c nominal gate failed; assets reused as perturbation harness only |
| Surgical foundation model / ARDY transplant | Out of scope — frozen proposer |
| PPO SOTA on ORBIT Reach | Engineering, not program center |

## Relation to other tracks

| Track | Role |
| --- | --- |
| **EXP-SAFE-001** | **Archived sim line** — rollout schema, perturb configs, metrics reused |
| **EXP-SAFE-004** | **Study 3 (later)** — human shared autonomy when gate defers to expert |
| **EXP-SI-COG-001/002** | Frozen VLA / language interface notes — proposer candidates |
| **Mechanism Atlas** | Methods spine — discard log justifies L3 benchmark framing |

## Deliverables (Study 1)

| Artifact | Path |
| --- | --- |
| Exception taxonomy | [`config/exception_taxonomy.yaml`](config/exception_taxonomy.yaml) |
| S-ODD spec (needle reach) | [`config/s_odd_needle_reaching.yaml`](config/s_odd_needle_reaching.yaml) |
| Study 1 spec | [`config/study1_execute_or_defer.yaml`](config/study1_execute_or_defer.yaml) |
| Gate training script | `scripts/train_execution_gate.py` (planned) |
| Eval harness | `scripts/evaluate_execute_or_defer.py` (planned) |
| Evidence JSON | `results/study1_*.json` (planned) |

## Success criteria

| Stage | Gate |
| --- | --- |
| **Desk** | Lead axis in register + one-pager approved |
| **Engineering** | Forbidden region + within-type severity branch + B0 smoke |
| **Study 1** | **B6** beats **B2** on primary endpoints @ matched safety; B3 = sanity only; **or** clean H0 / oracle-only |
| **Study 3 (optional)** | EXP-SAFE-004 — human defer pathway when gate triggers |

## Prerequisites (ordered)

- [x] Atlas Phase 2 desk + Run 0c evidence (sim platform validated; PPO line closed)
- [ ] Select frozen proposer (scripted reach, zero policy + language wrapper, or smoke VLA)
- [ ] Forbidden-region collision proxy in ORBIT Reach
- [ ] Gate feature contract (proposal logits, ensemble var, distance-to-forbidden, language embedding)
- [ ] Pre-register B0–B2 comparison + perturbation seeds

**Not prerequisites:** RunPod PPO retrain, M5 detector training, IRB (Study 1 is sim-only).

## References (prior art ports)

- KnowNo — language-calibrated deferral
- ReconVLA / selective execution in VLA stacks
- HITL recovery and shared autonomy (Javdani M4) — Study 3 defer pathway (planned)
