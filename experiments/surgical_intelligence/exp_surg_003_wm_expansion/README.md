# EXP-SURG-003 — Paper 002 WM expansion confirmatory

> **Paper:** [docs/paper002/](../../../docs/paper002/) · [confirmatory spec](../../../docs/paper002/paper002_confirmatory_spec_v0.1.md)  
> **Status:** mock pilot **v0.4** · preliminary G1 + H4 pass · pre-reg not frozen  
> **Public lab:** [Mismatch Lab spec](../../../docs/mismatch_lab/README.md)  
> **Parent:** EXP-SURG-001 ORBIT reach pipeline

---

## What this experiment tests

```text
Train static-only WM (W0)
→ Ep1 persistent drift failure
→ K × L1 repair fails
→ Arms: A none · B repair F0 · C add F1+G · D oracle
→ Ep2 novel drift
→ Primary: prediction error (H=10) · task success · static retention · gate H4
```

**First milestone:** find drift regime where **L1 fails but L3 succeeds** — **pilot v0.4 preliminary pass**.

---

## Pilot v0.4 (latest · 5 seeds · local)

| Metric | Result |
| --- | --- |
| Ep1 gate fire | **100%** (5/5) |
| H4 drift_M1 / negatives | **100% / 0%** |
| **C vs B ΔPE** | **+0.122** (~50% relative) |
| A / B / C / D PE | 0.187 / 0.243 / **0.121** / 0.114 |
| Ep2 success | 100% all arms (scripted) |

Fixes in v0.4: full Ep1 drift window · unified F1-probe gate · H4 aggregation in summary.

→ [`results/pilot_v0.1/summary.json`](results/pilot_v0.1/summary.json)

**Tier:** B+ preliminary · not confirmatory · not behavior (MPC) claim.

---

## Quick start (local CPU)

```bash
python scripts/run_exp_surg_003_pilot.py --smoke
python scripts/run_exp_surg_003_pilot.py --config experiments/surgical_intelligence/exp_surg_003_wm_expansion/config/pilot_v0.1.yaml
```

Requires: `pip install torch pyyaml numpy`

## Quick start (VESSL — recommended)

See **[VESSL runbook](../../../docs/paper002/vessl_runbook_v0.1.md)**.

```bash
cd /workspace/research-os && git pull origin master
EXP_SURG_003_PREP_BOOTSTRAP=1 bash scripts/prep_exp_surg_003_vessl.sh
bash scripts/run_exp_surg_003_mock_vessl.sh
export EXP_SURG_003_SKIP_BOOTSTRAP=1
bash scripts/run_exp_surg_003_vessl.sh
```

## Quick start (Isaac drift — GPU)

```bash
bash scripts/run_exp_surg_003_drift_runpod.sh
```

---

## Config

| File | Role |
| --- | --- |
| [`config/pilot_v0.1.yaml`](config/pilot_v0.1.yaml) | Mock pilot v0.4 hyperparameters |
| [`config/confirmatory_v0.1.yaml`](config/confirmatory_v0.1.yaml) | Confirmatory design contract |

## Implementation

| Module | Path |
| --- | --- |
| Mock env (drift / noise / impulse) | `scripts/wm_expansion/env.py` |
| GRU world model + L3 expansion | `scripts/wm_expansion/world_model.py` |
| MPC controller | `scripts/wm_expansion/mpc.py` |
| Adequacy gate | `scripts/wm_expansion/gate.py` |
| Pilot protocol | `scripts/wm_expansion/protocol.py` |
| Orchestrator | `scripts/run_exp_surg_003_pilot.py` |
| Isaac drift runner | `scripts/orbit_reach_drift.py` |

---

## Results

| Label | Tier | Note |
| --- | --- | --- |
| [`pilot_v0.1/`](results/pilot_v0.1/) | B+ | 5-seed v0.4 · G1 + H4 preliminary |

---

## Boundary

- Not Paper 001 confirmatory  
- Not mock→physics (archived)  
- Oracle arm D = diagnostic only · excluded from primary contrasts  
- Public: frozen design + tier-labeled results per [`PUBLIC_BOUNDARY.md`](../../../docs/PUBLIC_BOUNDARY.md)

---

## Docs

- [Confirmatory spec](../../../docs/paper002/paper002_confirmatory_spec_v0.1.md)
- [Pre-reg draft](../../../docs/paper002/paper002_prereg_wm_expansion_v0.1.md)
- [Mismatch Lab v0.1 spec](../../../docs/mismatch_lab/v0.1_spec.md)
- [Analysis plan v0.3](../../../docs/paper002/paper002_analysis_plan_v0.3.md)
