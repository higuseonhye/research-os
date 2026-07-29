# EXP-SURG-003 — Paper 002 WM expansion confirmatory

> **Paper:** [docs/paper002/](../../../docs/paper002/) · [confirmatory spec](../../../docs/paper002/paper002_confirmatory_spec_v0.1.md)  
> **Status:** mock pilot **implemented** · smoke in [`results/pilot_v0.1/`](results/pilot_v0.1/) · pre-reg not frozen  
> **Parent:** EXP-SURG-001 ORBIT reach pipeline

---

## What this experiment tests

```text
Train static-only WM (W0)
→ Ep1 persistent drift failure
→ K × L1 repair fails
→ Arms: A none · B repair F0 · C add F1+G
→ Ep2 novel drift
→ Primary: prediction error (H=10) · task success · static retention · gate H4
```

**First milestone:** find drift regime where **L1 fails but L3 succeeds** (pilot only).

---

## Quick start (VESSL — recommended)

See **[VESSL runbook](../../../docs/paper002/vessl_runbook_v0.1.md)**.

```bash
# Jupyter terminal on VESSL workspace
cd /workspace/research-os && git pull origin master
EXP_SURG_003_PREP_BOOTSTRAP=1 bash scripts/prep_exp_surg_003_vessl.sh   # first time only

# Mock pilot (CPU · milestone 1)
bash scripts/run_exp_surg_003_mock_vessl.sh --smoke
bash scripts/run_exp_surg_003_mock_vessl.sh

# Isaac drift (GPU · after bootstrap)
export EXP_SURG_003_SKIP_BOOTSTRAP=1
bash scripts/run_exp_surg_003_vessl.sh
```

Pull results locally: `bash scripts/copy_exp_surg_003_from_vessl.sh all`

## Quick start (mock pilot — local · if CPU allows)

```bash
# Smoke (~2–3 min CPU)
python scripts/run_exp_surg_003_pilot.py --smoke

# Pilot (5 seeds · arms A/B/C)
python scripts/run_exp_surg_003_pilot.py --config experiments/surgical_intelligence/exp_surg_003_wm_expansion/config/pilot_v0.1.yaml
```

Requires: `pip install torch pyyaml numpy`

## Quick start (Isaac drift data — GPU)

```bash
bash scripts/run_exp_surg_003_drift_runpod.sh
```

Collects persistent drift trajectories (`TRACK_DRIFTING` vs `TRACK_FROZEN`) for WM training data.

## Config

| File | Role |
| --- | --- |
| [`config/pilot_v0.1.yaml`](config/pilot_v0.1.yaml) | Mock pilot hyperparameters |
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
| [`pilot_v0.1/`](results/pilot_v0.1/) | B | Mock smoke · 2 seeds · C vs B ΔPE > 0 (tune drift next) |

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
- [Analysis plan v0.3](../../../docs/paper002/paper002_analysis_plan_v0.3.md)
