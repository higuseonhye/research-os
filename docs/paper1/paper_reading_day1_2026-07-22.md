# Paper reading — Day 1 (2026-07-22)

> **Goal:** PDF deep read + NotebookLM batch · before Phase C GPU  
> **Obsidian:** check off `[ ]` → `[x]` as you finish each paper  
> **Capture:** one block per paper (template at bottom) · private notes OK in builder-os-private

---

## How to use NotebookLM today

1. Create notebook: **`Paper1-NonAverage-2026-07-22`**
2. Upload **Batch A** PDFs first (6 papers · ~2–3 h)
3. Ask NotebookLM:
   - *What is evaluated? What is NOT evaluated?*
   - *What metrics? What baselines? What ablations?*
   - *Where would same-state multi-mode response evaluation fit or not?*
   - *One sentence: closest overlap with our 001 wedge.*
4. Fill **capture block** below each paper in Obsidian or private doc
5. Batch B if time · Batch C skim only

---

## Batch A — Must read today (Paper 1 core)

Priority order.

| # | Paper | PDF | Why today | Read for |
| --- | --- | --- | --- | --- |
| A1 | **Surgical UQ** — Early Failure Detection… | [pdf](https://arxiv.org/pdf/2501.10561) · [abs](https://arxiv.org/abs/2501.10561) | Phase C **stretch baseline** · surgical | UQ signal · handover rule · metrics · sim2real dVRK |
| A2 | **SuFIA-BC** | [pdf](https://arxiv.org/pdf/2504.14857) · [abs](https://arxiv.org/abs/2504.14857) | Same **ORBIT-Surgical** line · BC benchmark | Tasks · metrics · failure modes noted · no corrective eval |
| A3 | **Guardian** | [pdf](https://arxiv.org/pdf/2512.01946) · [abs](https://arxiv.org/abs/2512.01946) | Failure **eval protocol** reference | Perturbation · datasets · detection metrics · pipeline uplift |
| A4 | **FailSafe** | [pdf](https://arxiv.org/pdf/2510.01642) · [abs](https://arxiv.org/abs/2510.01642) | Recovery+VLA monitor · closest engineering pattern | Failure gen · recovery action · VLA uplift · no decision menu |
| A5 | **RoboFAC** | [pdf](https://arxiv.org/pdf/2505.12224) · [abs](https://arxiv.org/abs/2505.12224) | Failure QA + correction rounds | Taxonomy · 8 QA types · closed-loop success table |
| A6 | **ResponsibleRobotBench** | [pdf](https://arxiv.org/pdf/2512.04308) · [abs](https://arxiv.org/abs/2512.04308) | **HITL + safety metrics** overlap | SSR · call_human_help · HITL vs autonomous ablation |

**Batch A exit:** Can fill one row of [evaluation landscape v0.2](evaluation_landscape_2024_2026_v0.2.md) from **primary sources**, not desk notes.

---

## Batch B — Must read today if Batch A done (discovery + recoverability)

| # | Paper | PDF | Why today | Read for |
| --- | --- | --- | --- | --- |
| B1 | **ReSYNC** — Recover, Discover, Plan | [pdf](https://arxiv.org/pdf/2606.18328) · [abs](https://arxiv.org/abs/2606.18328) | Your **discovery** interest · Stage 2+ | Dual learning · dreaming · vs RC baseline |
| B2 | **IVNTR** — Bilevel Learning for Bilevel Planning | [pdf](https://arxiv.org/pdf/2502.08697) · [abs](https://arxiv.org/abs/2502.08697) | ReSYNC engine · predicate invention | Effect-centric predicates · planning objective |
| B3 | **RecoveryChaining** | [pdf](https://arxiv.org/pdf/2410.13979) · [abs](https://arxiv.org/abs/2410.13979) | **Recoverability @ state** ally | Recovery policy · hybrid action · metrics |
| B4 | **VAP-TAMP** | [pdf](https://arxiv.org/pdf/2604.26988) · [abs](https://arxiv.org/abs/2604.26988) | Tier 1 · situation→replan | Stack vs our eval-only wedge |

---

## Batch C — Important · skim or defer to Day 2

| # | Paper | PDF | Note |
| --- | --- | --- | --- |
| C1 | **MEDiC** | [2409.14287](https://arxiv.org/abs/2409.14287) | RESHAPE ally |
| C2 | **Dream2Fix** | [2603.13528](https://arxiv.org/abs/2603.13528) | Counterfactual recovery data |
| C3 | **REPAIR-Bench** | [2606.29937](https://arxiv.org/abs/2606.29937) | Medical HRI prefs |
| C4 | **RoboFailRing** | [ACL 2026](https://aclanthology.org/2026.acl-long.602/) | Detection timing |
| C5 | **Recover** (neuro-symbolic) | [2404.00756](https://arxiv.org/abs/2404.00756) | Ontology replan |
| C6 | **SymSkill** | [2510.01661](https://arxiv.org/abs/2510.01661) | Symbol+skill co-invention |
| C7 | **Recovery RL** | [2203.02638](https://arxiv.org/abs/2203.02638) | Backup policy switch |
| C8 | **Active perception** | [2003.06734](https://arxiv.org/abs/2003.06734) | REOBSERVE classic |

---

## Baseline papers (Phase C · extract protocol details)

| Baseline | Source paper | Extract |
| --- | --- | --- |
| CONTINUE (always) | — | Our rule · no PDF |
| REPLAN @ delay | 001 pre-reg | Our protocol |
| **UQ binary handover** | **A1 Surgical UQ** | Threshold · ensemble · when handover triggered |
| VLM monitor (discussion only) | A3 Guardian · A4 FailSafe | How they attach to pipeline — not Phase C v1.0 |

---

## Checklist (Obsidian-friendly)

### Batch A
- [ ] A1 Surgical UQ
- [ ] A2 SuFIA-BC
- [ ] A3 Guardian
- [ ] A4 FailSafe
- [ ] A5 RoboFAC
- [ ] A6 ResponsibleRobotBench

### Batch B
- [ ] B1 ReSYNC
- [ ] B2 IVNTR
- [ ] B3 RecoveryChaining
- [ ] B4 VAP-TAMP

### Batch C (optional today)
- [ ] C1 MEDiC
- [ ] C2 Dream2Fix
- [ ] C3 REPAIR-Bench
- [ ] C4 RoboFailRing
- [ ] C5 Recover
- [ ] C6 SymSkill
- [ ] C7 Recovery RL
- [ ] C8 Active perception

---

## Per-paper capture template

Copy into Obsidian / private notes:

```markdown
### [Short name] · [arxiv id]

**One-line:** 
**Evaluates:** 
**Does NOT evaluate:** 
**Metrics:** 
**Baselines / ablations:** 
**Experiment pattern:** (env · perturbation · output)
**Overlap with 001:** (kill / refine / ally)
**Quote / figure to cite:** 
**Open question for us:** 
```

---

## After today

1. Update kill matrix (private `prior_art_recoverability_matrix.yaml`) if any **Kill** found  
2. Confirm Phase C baseline: include Surgical UQ binary? (PI)  
3. Draft exception–response taxonomy v0.1 from A1 + 001D modes  
4. Mark [`related_work_index.md`](related_work_index.md) honest status: Tier 1 PDF progress

---

## Quick links

| Doc | Path |
| --- | --- |
| Framing | [`research_framing_v1.md`](research_framing_v1.md) |
| Landscape | [`evaluation_landscape_2024_2026_v0.2.md`](evaluation_landscape_2024_2026_v0.2.md) |
| RQ | [`research_question.md`](research_question.md) |
| Phase C pre-reg | [`phase_c_proper_run_prereg_v1.0.md`](phase_c_proper_run_prereg_v1.0.md) |
