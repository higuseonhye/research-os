# Paper 1 — Research framing v1 (public lock)

> **Date:** 2026-07-22 · Synthesizes smoke atlas + evaluation-protocol direction + paradigm map  
> **Status:** strategic framing · not a survey · feeds related work + Phase C baselines

---

## Vision (long-term)

**Physical Intelligence for the Non-Average World**

Average-world robotics: success demos → policy → success rate on i.i.d. test.  
Non-average world: deviation, tail events, compounding error, irrecoverable states, human takeover.

Paper 1 is **Stage 1**: measure **recoverability and response** at fixed mismatch onset — not train a new foundation model.

---

## Primary research question (v1.0)

> After a task-relevant mismatch at a fixed execution state **S**, how do **intervention choice** and **start time** jointly determine the probability of **successful resolution**?

**Measured object:** intervention-conditioned recoverability profile \(R_a(s,t)\) via **same-state counterfactual replay**.

See [`research_question.md`](research_question.md).

---

## What we are building (honest)

| Layer | Paper 1 | Later stages |
| --- | --- | --- |
| **Evaluation protocol** | Same-state CF · multi-mode menu · profile metrics | Open benchmark suite |
| **Empirical profiles** | \( \hat{R}_a(s,t) \) on ORBIT reach proxy | Surgical + manipulation scenarios |
| **Learned selector / VLA** | ❌ not claim | Stage 2+ |
| **Clinical deployment** | ❌ not claim | Long-term |

**Claim tiers today:** Tier A (scaffold) + Tier B (smoke n=5). Tier C only after Phase C proper run.

---

## Evaluation protocol — what it means

Not “one new metric.” A full **experiment contract**:

1. **Scenarios** — what non-nominal situations to test  
2. **Perturbation** — how deviation / failure is injected  
3. **Ground truth** — correct response class @ **S**  
4. **Output space** — continue · reobserve · retry/replan · reshape · stop · handover  
5. **Baselines** — rules · UQ binary · (stretch) VLM monitors  
6. **Metrics** — resolution **and** decision errors (unsafe continue, premature stop, wrong escalation)  
7. **Generalization** — OOD · timing · repeatability  

**Wedge (narrow):** prior work evaluates **detection → recovery action** or **task success after monitor**. We evaluate **which response class @ fixed S** with **safety-of-decision metrics**. Kill-test: **0 Kill** — partial overlaps (Surgical UQ, REPAIR, ResponsibleRobotBench) exist; claim must stay protocol-specific.

Full table: [`evaluation_landscape_2024_2026_v0.2.md`](evaluation_landscape_2024_2026_v0.2.md).

---

## Four paradigm voices (non-average world)

Most embodied failure papers follow:

```text
Trajectory → Failure → VLM → Recovery → Task success
```

Alternative voices (smaller but real):

| ID | Voice | Core idea | Examples |
| --- | --- | --- | --- |
| **① Discovery** | Failure expands **world model** | New skills + predicates from failure | ReSYNC · IVNTR · SymSkill |
| **② Policy rewrite** | Failure changes **policy** | Negative guidance · failure-aware training | AFIL · VINE · FEMA |
| **③ Proactive** | Act **before** failure | Graph mismatch · latent safety filter | Scene-graph replan · UNISafe |
| **④ Recoverability** | **State property**, not policy SOTA | Is this state salvageable? | RecoveryChaining · **001A–D** |

**Our interest stack (2026-07-22):**

- Conceptual pull: ① discovery · ② policy rewrite  
- Practical pull: **④ recoverability first**, then ③ proactive  

**001 sits in ④** — the **measurement layer** that makes ①–③ comparable later.

```text
Stage 1 (Paper 1):  profile @ S  (④ measure)
Stage 2:            proactive + escalation metrics  (③)
Stage 3:            discovery / policy  (①②) — profile as supervision trigger
```

---

## Mainstream vs our entry

| | Mainstream (2024–2026) | Our entry |
| --- | --- | --- |
| Novelty | New VLA · failure dataset · recovery VLM | **Evaluation protocol + profiles** |
| Metric | Success · detection · recovery uplift | **Response selection · decision errors · CF fairness** |
| Resource | GPU · large data · robot fleet | Isaac smoke → pre-reg proper · existing baselines |
| Audience | CoRL · RSS · NeurIPS D&B | Same + surgical / deployment validation language |

**University:** benchmark + metric = first-class contribution.  
**Industry:** regression testing · escalation · incident reduction (not leaderboard).

---

## Experiment scaffold (001A–D)

```text
Shared rollout → mismatch @ S → fork(response, delay) → terminal judge → profile table
```

| Study | Role |
| --- | --- |
| **001A** | Mode separation @ 3 cm (CONTINUE ≪ REPLAN) |
| **001B/C** | Delay band (mostly flat @ smoke) |
| **001D** | 5-mode menu + occlusion proxy (REOBSERVE · RESHAPE) |

**Phase C (frozen, not run):** n=20 · 6 cm + occlusion L1 · delay 20 · see [`phase_c_proper_run_prereg_v1.0.md`](phase_c_proper_run_prereg_v1.0.md).

---

## Baselines (Phase C)

| Tier | Baseline | Role |
| --- | --- | --- |
| **1** | CONTINUE · REPLAN profile | Primary comparison |
| **2 (stretch)** | Surgical UQ binary (continue vs handover) | Decision confusion vs multi-mode |
| **Log only** | HANDOVER stub | Stage 2 collaboration |

---

## Positioning one-liner (PI / abstract)

> Prior failure benchmarks ask whether failure occurred and what recovery to execute. We ask which **response class** at fixed mismatch onset maximizes successful resolution — and measure unsafe continuation, premature stop, and escalation error via **same-state counterfactual evaluation** on a surgical reach proxy.

---

## Doc map

| Doc | Purpose |
| --- | --- |
| [`research_question.md`](research_question.md) | RQ + sub-RQs + claim tiers |
| [`lit_positioning_v1.md`](lit_positioning_v1.md) | One-page public stance |
| [`evaluation_landscape_2024_2026_v0.2.md`](evaluation_landscape_2024_2026_v0.2.md) | Benchmark · metric · gap tables |
| [`paper_reading_day1_2026-07-22.md`](paper_reading_day1_2026-07-22.md) | **Today’s PDF queue + NotebookLM** |
| [`phase_b_smoke_review.md`](phase_b_smoke_review.md) | What smoke supports |
| [`roadmap.md`](roadmap.md) | Stage 3–5 plan |

Private extended notes: builder-os-private · Obsidian `03_Research/`.
