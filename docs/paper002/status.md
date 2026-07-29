# Paper 002 — Status (public)

> **Updated:** 2026-07-29  
> **Direction:** world-model **structural expansion** + **model adequacy gate**  
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
| Mock pilot v0.4 | ✅ G1 mechanism + H4 gate (5 seeds · **preliminary**) |
| Mismatch Lab v0.1 spec | ✅ [../mismatch_lab/README.md](../mismatch_lab/README.md) |
| Pre-reg v0.1 | 🔄 draft · freeze after pilot thresholds locked |
| VESSL re-run | 🔄 v0.4 code · mock + Isaac drift |
| Physical anchor (SO-101) | 🔄 Track B · observability · parallel with sim |
| EXP-REAL-001 confirmatory | ⏸ after sim Go gates · [physical roadmap](paper002_physical_validation_roadmap_v0.1.md) |
| Confirmatory GPU | ⏳ after pre-reg freeze |
| Archived mock→physics GPU | ❌ cancelled |

---

## Preliminary pilot evidence (mock v0.4 · Tier B+)

Controlled mock · five seeds · scripted behavior · **mechanism validation only**.

| Metric | Result |
| --- | --- |
| Ep1 gate fire | **100%** (5/5) |
| H4 drift_M1 | **100%** fire |
| H4 static / noise / impulse | **0%** fire |
| C vs B ΔPE (H=10) | **+0.122** (~50% relative) |
| Ep2 success | 100% all arms (scripted · not behavior claim) |

→ [`pilot_v0.1/summary.json`](../../experiments/surgical_intelligence/exp_surg_003_wm_expansion/results/pilot_v0.1/summary.json)

**Not yet claimed:** real-world generalization · MPC behavior · Isaac confirmatory · external % until CI frozen.

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

## Public product link

Research evidence feeds **Mismatch Lab** — Robot Diff entry · adequacy as premium insight · [spec](../mismatch_lab/v0.1_spec.md).

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
| Mismatch Lab | [../mismatch_lab/README.md](../mismatch_lab/README.md) |
| Paper 001 (parallel) | [../paper1/status.md](../paper1/status.md) |
| Study 002 pilot | [../stage2/README.md](../stage2/README.md) |
| Program naming | [../NAMING.md](../NAMING.md) |
