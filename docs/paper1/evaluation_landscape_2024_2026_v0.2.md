# Embodied AI Evaluation Landscape 2024–2026 (v0.2)

> **Status:** desk synthesis · PDF spot-check in progress  
> **Purpose:** validate decision-layer evaluation gap · map paradigms · feed Paper 1 baselines

---

## One-sentence verdict

Most failure/recovery work evaluates **detection → recovery action** or **task success after a monitor**; almost none standardize **same-state, multi-mode response selection** with **safety-of-decision metrics** — but **partial overlaps exist** (binary handover, HRI recovery preference, hazard HITL), so the claim must be **narrow and protocol-specific**.

---

## Paradigm map (beyond VLM failure line)

| Voice | Question | Representative | Evaluates decision menu @ S? |
| --- | --- | --- | --- |
| **VLM failure line** | Did it fail? What recovery? | Guardian · FailSafe · RoboFAC | ❌ |
| **UQ / deferral** | Uncertain → handover? | Surgical UQ · Diff-DAgger · conformal safety | Binary only |
| **RTA / assurance** | Invariant violated → backup? | Simplex · Recovery RL · When-to-act | Switch only |
| **Discovery** | Failure → new skill/concept? | **ReSYNC** · IVNTR · SymSkill | ❌ (learns abstractions) |
| **Recoverability** | Is state **S** salvageable? | RecoveryChaining · **001A–D** | ✅ (our core) |
| **Proactive** | Prevent before failure? | Scene-graph replan · UNISafe | ❌ |
| **HRI / hazard eval** | User pref · call human? | REPAIR · ResponsibleRobotBench | Partial |

---

## Master comparison — failure / eval benchmark line

| Paper | Venue | Core question | Decision menu? | Safety-of-decision? |
| --- | --- | --- | --- | --- |
| **Guardian** [2512.01946](https://arxiv.org/abs/2512.01946) | CoRL WS 2025 | Planning/execution failure detection + reasoning | No | No |
| **Dream2Fix** [2603.13528](https://arxiv.org/abs/2603.13528) | arXiv 2026 | Executable recovery from counterfactual failures | No | No |
| **FailSafe** [2510.01642](https://arxiv.org/abs/2510.01642) | arXiv 2025 | VLM detect + recovery Δpose for VLA | No | No |
| **REPAIR-Bench** [2606.29937](https://arxiv.org/abs/2606.29937) | arXiv 2026 | User recovery **preference** (medical HRI) | Partial | Partial (timing) |
| **RoboFailRing** [ACL 2026](https://aclanthology.org/2026.acl-long.602/) | ACL 2026 | Early detection + memory retrieval | No | No |
| **SuFIA-BC** [2504.14857](https://arxiv.org/abs/2504.14857) | ICRA 2025 | Surgical BC task success under shift | No | No |
| **RoboFAC** [2505.12224](https://arxiv.org/abs/2505.12224) | arXiv 2025 | Failure QA + correction rounds | No | No |
| **ResponsibleRobotBench** [2512.04308](https://arxiv.org/abs/2512.04308) | arXiv 2025 | Hazard · SSR · `call_human_help` | Partial | Partial |
| **001A–D (ours)** | research-os | Profile \(R_a(s,t)\) @ fixed **S** | **Yes** | Planned Phase C+ |

---

## Failure-as-discovery cluster (ReSYNC line)

| Paper | Link | Relation to ReSYNC [2606.18328](https://arxiv.org/abs/2606.18328) |
| --- | --- | --- |
| **ReSYNC** | [2606.18328](https://arxiv.org/abs/2606.18328) | Failure curriculum → RL recovery skill → **predicate discovery** → proactive planning |
| **IVNTR** (RSS 2025) | [2502.08697](https://arxiv.org/abs/2502.08697) | ReSYNC concept engine; demo transitions, not failure-driven |
| **RecoveryChaining** | [2410.13979](https://arxiv.org/abs/2410.13979) | ReSYNC baseline; recovery only, no concept growth |
| **SymSkill** | [2510.01661](https://arxiv.org/abs/2510.01661) | Symbol + skill co-invention from demos |
| **Recover** (neuro-symbolic) | [2404.00756](https://arxiv.org/abs/2404.00756) | Online ontology replan; not failure→predicate curriculum |
| **Predicate Invention** (AAAI 2023) | [2203.09634](https://arxiv.org/abs/2203.09634) | Silver line predicate learning root |

**vs 001:** ReSYNC **learns** abstractions from failure; 001 **measures** recoverability @ **S** (Stage 1 ruler for later discovery triggers).

---

## Tier 1 allies (Paper 1 related work · PDF required)

| Line | arXiv | Our relation |
| --- | --- | --- |
| **Surgical UQ** | [2501.10561](https://arxiv.org/abs/2501.10561) | Binary continue/handover baseline |
| **VAP-TAMP** | [2604.26988](https://arxiv.org/abs/2604.26988) | Situation→replan stack; we **eval** not compete |
| **MEDiC** | [2409.14287](https://arxiv.org/abs/2409.14287) | RESHAPE ally |
| **Recovery RL** | [2203.02638](https://arxiv.org/abs/2203.02638) | Task↔backup switch |
| **Active perception** | [2003.06734](https://arxiv.org/abs/2003.06734) | REOBSERVE ally |

---

## Metric gap (summary)

| Metric | Failure benchmarks | **001 target** |
| --- | --- | --- |
| Response selection @ fixed S | ❌ / partial | **Primary** |
| Unsafe continuation | ❌ / partial | **Primary** |
| Same-state CF fairness | ❌ | **Core method** |
| Recovery action quality | ✅ common | Secondary |

---

## Kill-test

**0 Kill** on “multi-mode response @ same onset + decision-error metrics.” Do **not** claim empty field.

---

## References

| Paper | PDF |
| --- | --- |
| Guardian | https://arxiv.org/pdf/2512.01946 |
| Dream2Fix | https://arxiv.org/pdf/2603.13528 |
| FailSafe | https://arxiv.org/pdf/2510.01642 |
| REPAIR-Bench | https://arxiv.org/pdf/2606.29937 |
| RoboFailRing | https://aclanthology.org/2026.acl-long.602/ |
| SuFIA-BC | https://arxiv.org/pdf/2504.14857 |
| RoboFAC | https://arxiv.org/pdf/2505.12224 |
| ResponsibleRobotBench | https://arxiv.org/pdf/2512.04308 |
| ReSYNC | https://arxiv.org/pdf/2606.18328 |
| IVNTR | https://arxiv.org/pdf/2502.08697 |
| RecoveryChaining | https://arxiv.org/pdf/2410.13979 |
