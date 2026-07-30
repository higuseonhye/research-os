# EXP-SURG-003 — Paper 002 WM expansion confirmatory

> **Paper:** [docs/paper002/](../../../docs/paper002/) · [confirmatory spec](../../../docs/paper002/paper002_confirmatory_spec_v0.1.md)  
> **Status:** Isaac drift anchor confirmatory **pass** (10 paired seeds) · Paper 002 L3-vs-L1 pre-reg not frozen
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

## Isaac drift anchor (VESSL · confirmatory)

Fresh seeds `100–139` were screened using static control only. The protocol locked the first 10 eligible seeds before either treatment policy ran, then executed every `(seed, policy)` arm in a separate Isaac process.

| Metric | Result |
| --- | --- |
| Static-control eligibility | **29/40** candidates |
| Locked paired seeds | **10** (`101,102,103,104,105,107,108,109,111,112`) |
| `TRACK_DRIFTING` success | **10/10** |
| `TRACK_FROZEN` success | **0/10** |
| Mean paired final-distance improvement | **20.250 mm** |
| Moving policy better | **10/10** seeds |
| Forbidden violations / unexpected resets | **0 / 0** |
| Protocol and effect gates | **PASS / PASS** |

→ [Result record and trajectories](results/isaac_static_first_confirmatory_v0.2/RESULTS.md)

This confirms the persistent-drift tracking anchor and evaluation isolation. It does **not** test the Paper 002 L3 structural-expansion vs L1 parameter-repair hypotheses.

## Active pilot: explicit model order v0.2

The active pilot replaces the non-identifying GRU comparison with an explicit
zero-order versus constant-velocity model-order test. H=10 predictions drive
the Isaac controller target, so prediction gains must transfer to behavior.

```bash
export EXP_SURG_003_SKIP_BOOTSTRAP=1
export EXP_SURG_003_ZERO_AGENT=0
export DISABLE_FABRIC=1
bash scripts/run_exp_surg_003_model_order_vessl.sh
```

The static-first protocol selects five of 20 pilot candidates before treatment,
then runs 10 paired conditions across A/B/C/D plus B/C static retention. Every
seed-arm-condition cell uses a fresh Isaac process. The pilot is excluded from
confirmatory analysis. See the
[v0.3 protocol](../../../docs/paper002/paper002_model_order_protocol_v0.3.md).

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
| [`config/model_order_pilot_v0.2.json`](config/model_order_pilot_v0.2.json) | Invalidated shared-process pilot contract |
| [`config/model_order_pilot_v0.3.json`](config/model_order_pilot_v0.3.json) | Active process-isolated model-order pilot contract |

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
| Model-order target models | `scripts/wm_expansion/target_dynamics.py` |
| Model-order VESSL orchestrator | `scripts/run_exp_surg_003_model_order.py` |
| Model-order aggregation | `scripts/aggregate_exp_surg_003_model_order.py` |

---

## Results

| Label | Tier | Note |
| --- | --- | --- |
| [`pilot_v0.1/`](results/pilot_v0.1/) | B+ | 5-seed v0.4 · G1 + H4 preliminary |
| [`isaac_static_first_confirmatory_v0.2/`](results/isaac_static_first_confirmatory_v0.2/) | Isaac anchor confirmatory | Static-first selection · 10 paired fresh seeds · all locked gates pass |

---

## Boundary

- Not Paper 001 confirmatory  
- Not mock→physics (archived)  
- Isaac drift anchor is an environment/control validation, not the Paper 002 L3-vs-L1 confirmatory
- Oracle arm D = diagnostic only · excluded from primary contrasts  
- Public: frozen design + tier-labeled results per [`PUBLIC_BOUNDARY.md`](../../../docs/PUBLIC_BOUNDARY.md)

---

## Docs

- [Confirmatory spec](../../../docs/paper002/paper002_confirmatory_spec_v0.1.md)
- [Pre-reg draft](../../../docs/paper002/paper002_prereg_wm_expansion_v0.1.md)
- [Mismatch Lab v0.1 spec](../../../docs/mismatch_lab/v0.1_spec.md)
- [Analysis plan v0.3](../../../docs/paper002/paper002_analysis_plan_v0.3.md)
