# Study 2 — Dream curriculum Phase 1 pre-registration v0.1

> **Experiment:** EXP-SURG-002  
> **Status:** **FROZEN DESIGN · NOT EXECUTED**  
> **Date frozen:** 2026-07-22  
> **Execute after:** PI sign-off · RunPod GPU available  
> **L1 RQ:** [`l1_research_question_v0.1.md`](l1_research_question_v0.1.md) · RQ 1.1 + 1.2

---

## 0. Scope boundary

**Paper 1 (001 Phase C) is separate.** This study tests **failure scenario generation** (Stage 1 of L1), not confirmatory recoverability profiles.

| In scope | Out of scope |
| --- | --- |
| Gaussian vs diffusion **dreamer** | Full ReSYNC / IVNTR stack |
| Rule vs JSON **agentic curriculum** | Classifier-guided diffusion on images |
| Isaac ORBIT reach @ dreamed specs | ManiSkill / new sim |
| Informative rate mock ↔ Isaac correlation | Predicate invention metrics |

---

## 1. Primary hypothesis (RQ 1.2)

> **Diffusion dreaming** produces a **higher rate of informative failures** on Isaac ORBIT reach than **Gaussian dreaming**, under matched agentic curricula and seed budget.

**Informative failure @ spec:** CONTINUE unsuccessful ∧ REPLAN successful (same-state CF @ mismatch onset **S**).

**Directional · not registry claim until Phase 1 completes.**

---

## 2. Secondary hypotheses

| ID | Hypothesis |
| --- | --- |
| **H2** | Diffusion yields **higher param diversity** than Gaussian at matched informative rate |
| **H3** | Mock informative rate **correlates** with Isaac informative rate (rank correlation ≥ 0.5 on top-k specs) |
| **H4 (exploratory)** | LLM JSON curriculum ≥ rule curriculum on informative yield |

---

## 3. Design (frozen v0.1)

| Parameter | Value |
| --- | --- |
| **Dreamers** | `gaussian` · `diffusion` (toy DDPM · desk-trained bootstrap) |
| **Agent default** | `rule` (taxonomy families cycle) |
| **Agent stretch** | `json-file` (LLM curriculum · optional arm) |
| **Mock episodes / dreamer** | 48 |
| **Mock seeds** | 42, 43, 44 (3 runs · report mean ±) |
| **Isaac top-k specs / dreamer** | 5 (highest mock informative; tie-break diversity) |
| **Isaac seeds / spec** | 0,1,2,3,4 (n=5) |
| **Perturbation** | P2 target shift (+Y); onset + shift from dream space |
| **Branches** | CONTINUE · REPLAN_d0 |
| **Platform** | Isaac Sim 4.1 · ORBIT Reach IK-Rel · RunPod RTX 4090 |
| **Task** | `Isaac-Reach-Dual-STAR-IK-Rel-Play-v0` |

**Dream space (normalized in config):**

- `shift_m` ∈ [0.02, 0.08]
- `onset_step` ∈ [10, 40]
- `occlusion_gain` ∈ [0, 0.85] — mock only v0.1; Isaac arm uses shift+onset only

---

## 4. Baselines & ablations

| Arm | Role |
| --- | --- |
| **B0 Gaussian + rule agent** | ReSYNC-style dreaming baseline |
| **B1 Diffusion + rule agent** | Primary contrast |
| **B2 Diffusion + json agent** | Stretch · agentic curriculum |
| **B3 Fixed P2 mid (shift=0.04, onset=20)** | Human curriculum control |

---

## 5. Metrics

| Metric | Definition |
| --- | --- |
| **Primary:** informative_rate | #(CONTINUE fail ∧ REPLAN ok) / #specs |
| **param_diversity** | mean std(shift, onset, occlusion) across specs |
| **mode_gap** | REPLAN success − CONTINUE success |
| **mock–isaac agree** | Spearman ρ on per-spec informative (0/1) |

---

## 6. Execution protocol (RunPod)

```bash
# On pod (repo root)
bash scripts/run_study2_dream_curriculum_runpod.sh

# Optional env
STUDY2_MOCK_EPISODES=48 STUDY2_MOCK_SEEDS=42,43,44 STUDY2_TOP_K=5 bash scripts/run_study2_dream_curriculum_runpod.sh
```

**Steps (script):**

1. CPU mock: `--compare` for gaussian + diffusion × mock seeds
2. Export top-k specs → `artifacts/study2_dream_curriculum/isaac_specs.json`
3. GPU bootstrap + Isaac loop per spec (001A runner)
4. Merge → `results/study2_dream_curriculum/isaac/<run_id>/`

---

## 7. Artifacts (on completion)

```
results/study2_dream_curriculum/
  mock/<run_id>/summary.json
  mock/<run_id>/records.json
  isaac/<run_id>/
    isaac_aggregate.json
    summary.json
    run_manifest.json   # git commit · prereg hash · timestamp
    per_spec/*.json
artifacts/study2_dream_curriculum/
  isaac_specs.json
  config_snapshot.yaml
```

---

## 8. Success criteria (Phase 1 GO → Phase 2)

- [ ] 3 mock seeds × 2 dreamers complete
- [ ] Isaac top-k × 5 seeds × 2 dreamers complete
- [ ] `branch_replay_ok` = 100% on Isaac
- [ ] Primary direction: diffusion informative_rate ≥ gaussian (any mock seed mean)
- [ ] Mock–Isaac ρ documented (pass/fail H3)
- [ ] PI review: proceed to classifier-guided diffusion (Phase 2)?

---

## 9. GPU budget

| Phase | Est. |
| --- | --- |
| Mock (CPU) | < 5 min |
| Bootstrap (cold) | 15–25 min once |
| Isaac 2 dreamers × 5 specs × 5 seeds × ~2 branches | ~2–4 h |
| Buffer | 1 h |
| **Total** | **~0.5 pod-day** |

---

## 10. Version history

| Version | Date | Note |
| --- | --- | --- |
| v0.1 | 2026-07-22 | Initial freeze · Phase 1 gaussian vs diffusion |

**Bump only via PR + changelog · never retro-edit after GPU start.**
