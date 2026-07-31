# Naming guide — research program

> **Updated:** 2026-07-31 · Independent personal research

---

## L0 (program center · v2)

> **When reality cannot be explained by the agent’s current model class, how should a system revise not only its parameters, but the architecture and composition of its world-modeling system?**

**Recoverability** = measurement window · not the program center.

**Embodiment** = current testbed · not part of L0. The studies run in embodied simulation because it makes mismatch, timing, and recovery observable — the question itself is stated without it. See [program](program/README.md) · [domain generality](mismatch_lab/vision_narrative_v0.2.md#domain-generality-orientation-only).

Full architecture · expansion levels · taxonomy: [paper002_wm_system_expansion_v0.1.md](paper002/paper002_wm_system_expansion_v0.1.md)

---

## Three layers (what changes at what rate)

| Layer | Content | Changes |
| --- | --- | --- |
| **L0 · Program** | The question above | Does not change |
| **Testbed** | Physical AI · embodied simulation (now) | Over years; other domains admissible under the [application policy](program/README.md) |
| **Projects** | Paper 001 · 002 · 003 · Mismatch Lab | Per project |

Naming by audience is intentional and does not indicate a change of question — the program name, the testbed name, and a project title describe the same work at three different levels.

---

## Completed / archived

| Label | Experiment ID | Role | Status |
| --- | --- | --- | --- |
| **Paper 001** | **EXP-SURG-001** | Recoverability profiles @ fixed **S** (optional credential) | ✅ Tier C complete |
| **Study 002** | **EXP-SURG-002** | Dream curriculum **pilot** (Tier B) | ✅ archived |
| **Paper 002 (mock→physics)** | EXP-SURG-003 | Mock→Isaac selection | ❌ **archived** · [archive](paper002/archive/mock_to_physics/) |

---

## Active (now)

| Label | Experiment ID | Role | Status |
| --- | --- | --- | --- |
| **Paper 002** | **EXP-SURG-003** | **Structural WM expansion** · hidden mode minimal cell | ✅ confirmatory complete · [submission v1.1](paper002/README.md) |
| **Paper 003** | TBD | **Missing causal relation** · capability-threshold expansion (not just error reduction) | 🔄 design v0.1 · relation module + commitment task built · [docs](paper003/README.md) |
| **Paper 004+** | TBD | Human representation · surgical exceptions | design |

### Paper 003 scope (design v0.1)

| Component | In Paper 003 | Status |
| --- | --- | --- |
| Missing **relation** between entities (vs Paper 002's mode) | ✅ | [relation module](../scripts/wm_expansion/relation_dynamics.py) implemented |
| Relation-adequacy gate · must stay silent on Paper 002's drift | ✅ | separates 10/10 vs 0/10 on the CPU proxy |
| Four arms: none / parameter / mode / **relation** | ✅ | arm C is the discriminating control |
| **Capability threshold crossing** as primary endpoint | ✅ | constructed on a [commitment-point task](paper003/paper003_commitment_task_v0.1.md) |
| Arm D estimating the reference pattern online | — | **blocking** before any confirmatory run |
| Isaac implementation · prereg | — | not started |
| Preference / user modelling | — | **out of scope** (different question — see [application policy](program/README.md)) |

Paper 001 **not required** as logical prerequisite for Paper 002.

---

## Paper 002 scope (WM expansion v0.1)

| Component | In Paper 002 | Deferred |
| --- | --- | --- |
| Hidden `target_mode` (static / drift) | ✅ | — |
| Three arms: none / parameter / structural | ✅ | — |
| Ep1 fail · Ep2 novel drift | ✅ | — |
| Expansion gate (parsimony) | ✅ | — |
| Reality \| Belief figures | ✅ | — |
| Missing causal variables | — | [Paper 003](paper003/README.md) |
| Human-in-the-loop expansion | — | Paper 004+ |
| Mock→physics curriculum | — | archived |

---

## Disambiguation

| Term | Means | Does **not** mean |
| --- | --- | --- |
| **`docs/stage2/`** | Study 002 public docs | Paper 002 body |
| **Parameter update** | Re-estimate within fixed representation | Structural expansion |
| **Structural expansion** | Add variable · mode · relation | Mock rank transfer |
| **Mode gap** (Paper 002) | Regime the model cannot represent | Relation gap |
| **Relation gap** (Paper 003) | Dependency on a *second entity* the model treats as independent | Mode gap · preference |
| **Capability crossing** | Task variants going from ~0% to achievable | Lower mean prediction error |
| **Commitment point** | An irreversible action; a wrong prediction fails outright | Any hard task |
| **Physical AI** | Current **testbed** | The program's identity |

---

## One-line program

> When failures are structurally unexplained, expand representation · validate on novel encounters · recoverability measures whether it helped.
