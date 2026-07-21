# Paper 1 — Related work index (public)

> **Full review index (private):** [related_work_review_index_v1.md](https://github.com/higuseonhye/builder-os-private/blob/master/working/research/related_work_review_index_v1.md)  
> **Obsidian:** [related-work-review-index](https://github.com/higuseonhye/builder-os-vault/blob/master/03_Research/related-work-review-index.md)

This repo does not duplicate the full survey. Use the links below.

---

## Start here

1. [Research framing v1](research_framing_v1.md) — vision · paradigm map · Stage 1–3 arc
2. [**Paper reading Day 1 (2026-07-22)**](paper_reading_day1_2026-07-22.md) — **today's PDF queue + NotebookLM** · **Batch B first**
3. [Research question v1.0](research_question.md)
4. [Evaluation landscape v0.2](evaluation_landscape_2024_2026_v0.2.md) — benchmark · metric · ReSYNC cluster
5. [Lit positioning v1](lit_positioning_v1.md) — one-page public stance
6. [Phase B smoke review](phase_b_smoke_review.md) — what smoke supports

---

## Today's reading (Batch B first · then A)

| Batch | Papers | PDF pack |
| --- | --- | --- |
| **B (now)** | ReSYNC · IVNTR · RecoveryChaining · VAP-TAMP | [2606.18328](https://arxiv.org/pdf/2606.18328) · [2502.08697](https://arxiv.org/pdf/2502.08697) · [2410.13979](https://arxiv.org/pdf/2410.13979) · [2604.26988](https://arxiv.org/pdf/2604.26988) |
| **A (after)** | Surgical UQ · SuFIA · Guardian · FailSafe · RoboFAC · ResponsibleRobotBench | see [reading Day 1](paper_reading_day1_2026-07-22.md) |

Full checklist: [`paper_reading_day1_2026-07-22.md`](paper_reading_day1_2026-07-22.md)

---

## Core prior lines (Tier 1 · PDF deep read)

| Line | arXiv | Our relation |
| --- | --- | --- |
| Surgical UQ | [2501.10561](https://arxiv.org/abs/2501.10561) | Binary baseline |
| VAP-TAMP | [2604.26988](https://arxiv.org/abs/2604.26988) | High refine · eval vs stack |
| MEDiC | [2409.14287](https://arxiv.org/abs/2409.14287) | RESHAPE ally |
| Recovery RL | [2203.02638](https://arxiv.org/abs/2203.02638) | 2-policy switch |
| Introspective recovery | [2103.11881](https://arxiv.org/abs/2103.11881) | Recovery exists |
| When-to-act | [2605.12561](https://arxiv.org/abs/2605.12561) | RTA / timing (control) |
| Active perception | [2003.06734](https://arxiv.org/abs/2003.06734) | REOBSERVE ally |

---

## Evaluation / failure benchmark line (2024–2026)

| Paper | arXiv | Note |
| --- | --- | --- |
| Guardian | [2512.01946](https://arxiv.org/abs/2512.01946) | Detection + pipeline |
| Dream2Fix | [2603.13528](https://arxiv.org/abs/2603.13528) | Counterfactual recovery |
| FailSafe | [2510.01642](https://arxiv.org/abs/2510.01642) | VLA monitor |
| REPAIR-Bench | [2606.29937](https://arxiv.org/abs/2606.29937) | HRI recovery prefs |
| RoboFailRing | [ACL 2026](https://aclanthology.org/2026.acl-long.602/) | Early detection |
| SuFIA-BC | [2504.14857](https://arxiv.org/abs/2504.14857) | Surgical BC bench |
| RoboFAC | [2505.12224](https://arxiv.org/abs/2505.12224) | Failure critic |
| ResponsibleRobotBench | [2512.04308](https://arxiv.org/abs/2512.04308) | Hazard + HITL |

Table: [`evaluation_landscape_2024_2026_v0.2.md`](evaluation_landscape_2024_2026_v0.2.md)

---

## Failure-as-discovery cluster (Stage 2+ interest)

| Paper | arXiv |
| --- | --- |
| **ReSYNC** | [2606.18328](https://arxiv.org/abs/2606.18328) |
| IVNTR | [2502.08697](https://arxiv.org/abs/2502.08697) |
| RecoveryChaining | [2410.13979](https://arxiv.org/abs/2410.13979) |
| SymSkill | [2510.01661](https://arxiv.org/abs/2510.01661) |
| Recover | [2404.00756](https://arxiv.org/abs/2404.00756) |

---

## Private docs (maps · matrix · KR table)

| Doc | URL |
| --- | --- |
| Related work map EN | [paper1_related_work.md](https://github.com/higuseonhye/builder-os-private/blob/master/program/mechanism_atlas/paper1_related_work.md) |
| Related work KR | [paper1_related_work_kr.md](https://github.com/higuseonhye/builder-os-private/blob/master/meeting/2026-07-21-first-share/paper1_related_work_kr.md) |
| Kill matrix | [prior_art_recoverability_matrix.yaml](https://github.com/higuseonhye/builder-os-private/blob/master/program/mechanism_atlas/prior_art_recoverability_matrix.yaml) |
| Lit sprint v2 | [lit_sprint_v2_smoke_synthesis.md](https://github.com/higuseonhye/builder-os-private/blob/master/working/research/lit_sprint_v2_smoke_synthesis.md) |

---

## Honest status (2026-07-22)

- Desk maps + evaluation landscape v0.2 ✅  
- **PDF deep read:** Batch B in progress — see [reading Day 1](paper_reading_day1_2026-07-22.md)  
- Phase C GPU blocked until Batch B + Batch A PDF read + PI baseline sign-off
