# Paper 002 — Status (public)

> **Updated:** 2026-07-29  
> **Direction:** world-model **structural expansion** from unexplained failures  
> **Previous direction:** mock→physics · [archived](archive/mock_to_physics/README.md)

---

## Current phase

| Phase | Status |
| --- | --- |
| Program pivot | ✅ 2026-07-29 · core question first |
| Related work v0.2 | ✅ TMoW · MuSix · Worldscape-MoE · LMC · adequacy wedge |
| Description v0.1 | ✅ [paper002_description_wm_expansion_v0.1.md](paper002_description_wm_expansion_v0.1.md) |
| Confirmatory spec v0.1 | ✅ [paper002_confirmatory_spec_v0.1.md](paper002_confirmatory_spec_v0.1.md) |
| EXP-SURG-003 scaffold | ✅ [exp_surg_003_wm_expansion](../../experiments/surgical_intelligence/exp_surg_003_wm_expansion/README.md) |
| Pre-reg v0.1 | 🔄 draft · [paper002_prereg_wm_expansion_v0.1.md](paper002_prereg_wm_expansion_v0.1.md) |
| VESSL sim pilot | 🔄 scripted_smoke PASS · mock/drift |
| Physical SO-101 | ⏸ **HOLD** until sim Go gates · [physical roadmap](paper002_physical_validation_roadmap_v0.1.md) |
| Confirmatory GPU | ⏳ after pre-reg freeze |
| Archived mock→physics GPU | ❌ cancelled |

---

## Run target (VESSL)

[vessl_runbook_v0.1.md](vessl_runbook_v0.1.md) · not local · not RunPod

| Step | Command |
| --- | --- |
| Prep | `EXP_SURG_003_PREP_BOOTSTRAP=1 bash scripts/prep_exp_surg_003_vessl.sh` |
| Mock | `bash scripts/run_exp_surg_003_mock_vessl.sh` |
| Isaac drift | `EXP_SURG_003_SKIP_BOOTSTRAP=1 bash scripts/run_exp_surg_003_vessl.sh` |

---

## Honest one-liner

> Can **persistent structured task failures** — after **K failed parameter repairs** — justify **structural inadequacy** and does **prepared L3 expansion** beat L1 on Ep2 novel drift without nominal regression?

Novelty = **whether/when expansion is warranted** · not expert addition alone (TMoW · Worldscape-MoE precedent).

---

## Archived (do not execute)

| Item | Note |
| --- | --- |
| Pre-reg v0.3 · tag `paper002-prereg-v0.3` | Historical |
| MS PDF v1.2 | Abandoned · kept for record |
| Mock 42–46 · Isaac H1–H3 confirmatory | Cancelled |

→ [archive/mock_to_physics/](archive/mock_to_physics/README.md)

---

## Links

| Resource | Path |
| --- | --- |
| Hub | [README.md](README.md) |
| Paper 001 (parallel) | [../paper1/status.md](../paper1/status.md) |
| Study 002 pilot | [../stage2/README.md](../stage2/README.md) |
| Program naming | [../NAMING.md](../NAMING.md) |
