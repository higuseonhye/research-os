# Study 2 — Paper outline v0.1 (Stage 1 · dream curriculum)

> **Working title:** *Agentic Curricula and Diffusion Dreaming for Informative Failure Generation*  
> **Status:** outline · pre-Isaac · maps to [`study2_prereg_v0.1.md`](study2_prereg_v0.1.md)  
> **L1 RQ:** [`l1_research_question_v0.1.md`](l1_research_question_v0.1.md)  
> **Tier today:** design + mock smoke · Isaac = confirmatory arm

---

## 1. Abstract (draft bullets)

- Non-average embodied settings need **informative failures** before discovery / proactive planning.
- ReSYNC dreams with **Gaussian** sampling; we ask whether **diffusion dreaming** + **agentic curriculum** improves **informative failure yield** under fair CF evaluation @ ORBIT reach.
- Phase 1: Gaussian vs diffusion · rule vs LLM curriculum · Isaac ORBIT injection.
- **Claim boundary:** scenario generation + yield metrics · not full IVNTR/ReSYNC replication (Phase 2+).

---

## 2. Introduction

| Block | Content |
| --- | --- |
| **Hook** | Average-world success rates hide tail failures; discovery pipelines need curated failure data |
| **Gap** | ReSYNC manual curriculum + Gaussian dreaming; no benchmark for **dreamer quality** |
| **Wedge** | Same-state CF **informative failure** as measurable object @ surgical reach proxy |
| **Contributions** | See §4 |

**Fig 1 (target):** Pipeline — agent → dreamer → Isaac CF @ S → informative filter

---

## 3. Related work

| Cluster | Papers | Our relation |
| --- | --- | --- |
| Failure-as-discovery | ReSYNC, IVNTR, SymSkill | **Extend** dreaming + curriculum |
| Reactive recovery | RecoveryChaining, FLARE | Informative failures feed recovery stack |
| Active / interactive perception | VAP-TAMP, active perception | Stage 3 · not Phase 1 |
| CF recovery data | Dream2Fix | Parallel data line |
| Recoverability eval | **001 / Paper 1** | Measurement leg · fixed-S CF protocol |

Full captures: Obsidian Batch B · [`evaluation_landscape_2024_2026_v0.2.md`](../paper1/evaluation_landscape_2024_2026_v0.2.md)

---

## 4. Research question & contributions

### L1 (program)

> Failure lifecycle (explore → dream → validate → crystallize): which stages are separable and measurable?

### Study 2 Phase 1 RQs

- **RQ 1.1:** Does agentic curriculum cover taxonomy families better than fixed P2?
- **RQ 1.2:** Does diffusion dreaming increase **informative failure yield** vs Gaussian?

### Contributions (scoped)

1. **Metric:** informative failure @ fixed **S** (CONTINUE fail ∧ REPLAN success) for dreamer comparison  
2. **System:** agentic curriculum + dreamer ablation harness on ORBIT (open artifact path)  
3. **Empirical:** Phase 1 Gaussian vs diffusion on mock + Isaac (pre-reg n)  
4. **Bridge:** connects Paper 1 recoverability measure to ReSYNC-style discovery pipeline  

---

## 5. Method

### 5.1 Problem setting

- ORBIT Dual-STAR reach · P2 target shift @ onset step  
- Dream space: `(shift_m, onset_step, occlusion_gain)` v0.1  
- **Informative:** CF branches at **S** separate CONTINUE vs REPLAN outcomes  

### 5.2 Agentic curriculum

- Rule agent: `exception_taxonomy.yaml` family cycle  
- Stretch: LLM JSON curriculum (`--agent json-file`)  

### 5.3 Dreamers

- **Gaussian:** ReSYNC-style baseline  
- **Diffusion:** toy DDPM on normalized dream space · bootstrap from informative pool  

### 5.4 Evaluation protocol

- Mock desk validation → export top-k specs → Isaac 001A runner  
- Seeds · pre-reg in [`study2_prereg_v0.1.md`](study2_prereg_v0.1.md)  

### 5.5 Implementation

- `scripts/study2_dream_curriculum/` · `run_study2_dream_curriculum_runpod.sh`  

---

## 6. Results (placeholder · fill after RunPod)

| Table | Content |
| --- | --- |
| **T1** | Mock informative rate · diversity · by dreamer × seed |
| **T2** | Isaac informative rate · top-k specs |
| **T3** | Mock–Isaac agreement (Spearman ρ) |
| **Fig 2** | Dream space scatter · informative vs not |
| **Fig 3** | Mode gap (REPLAN − CONTINUE) by dreamer |

---

## 7. Ablations

| Arm | Tests |
| --- | --- |
| Gaussian + rule | ReSYNC baseline |
| Diffusion + rule | **Primary** |
| Diffusion + LLM JSON | Agentic stretch |
| Fixed P2 (0.04m, onset 20) | Human curriculum control |
| No dreaming (fixed grid) | Optional Phase 1b |

---

## 8. Discussion

- **If diffusion wins on diversity but loses on informative rate:** trade-off · classifier-guided filter (Phase 2)  
- **If mock–Isaac disagree:** mock insufficient · Isaac-first curriculum  
- **Relation to 001:** generation layer vs measurement layer  
- **Limits:** no IVNTR predicate invention · no interactive perception · single task  

---

## 9. Conclusion

- Phase 1 answers whether **dreamer choice matters** for informative failures @ surgical reach proxy.  
- Phase 2: classifier-guided diffusion on sim states · predicate yield.  
- Phase 3: full pipeline + Paper 1 profiles as decision leg.  

---

## 10. PI sign-off checklist

- [ ] L1 RQ wording approved  
- [ ] Phase 1 pre-reg frozen · GPU authorized (~0.5 pod-day)  
- [ ] Claim tier: Phase 1 = scenario generation paper / workshop · not clinical  
- [ ] Paper 1 Phase C can run in parallel or after  

---

## Doc map

| Doc | Role |
| --- | --- |
| [`study2_prereg_v0.1.md`](study2_prereg_v0.1.md) | Experiment contract |
| [`dream_curriculum_sandbox_v0.1.md`](dream_curriculum_sandbox_v0.1.md) | Sandbox design |
| [`l1_research_question_v0.1.md`](l1_research_question_v0.1.md) | Program RQ |
| [`../paper1/research_framing_v1.md`](../paper1/research_framing_v1.md) | L0 vision · Paper 1 boundary |
