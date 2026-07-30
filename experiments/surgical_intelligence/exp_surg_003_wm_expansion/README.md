# EXP-SURG-003: Failure-Conditioned Model-Order Expansion

> Paper: [Paper 002](../../../docs/paper002/README.md)
>
> Status: model-order confirmatory v1.0 complete and passed
>
> Frozen tag: `paper002-model-order-confirmatory-v1.0`

## Question

When persistent target drift remains unexplained after the best allowed
zero-order parameter repair, does a gated constant-velocity state expansion
improve H=10 prediction and prediction-linked control without static regression
or false activation on matched controls?

## Arms

| Arm | Model | Role |
| --- | --- | --- |
| A | Frozen zero order, alpha 0.5 | Secondary baseline |
| B | Repaired zero order, alpha 1.0 | Primary comparator |
| C | Gated constant velocity, position/velocity alpha 1.0 | Primary intervention |
| D | True velocity | Diagnostic oracle |

All arms use the same scripted Cartesian controller. Each
seed-arm-condition cell runs in a fresh Isaac process.

## Confirmatory Result

The fixed design selected the first 10 statically eligible seeds from fresh
candidates 300-339 and evaluated 10 fresh drift conditions.

| Metric | Result |
| --- | ---: |
| Ep2 cells | 400/400 valid |
| Static retention cells | 20/20 valid |
| C-B H=10 prediction error | -10.806 mm, 95% CI [-11.360, -10.331] |
| C-B fixed-horizon final distance | -13.304 mm, 95% CI [-13.599, -12.982] |
| Resolution rate | C 100%, B 76% |
| Static retention | C 10/10, B 10/10 |
| Gate activation | drift 100/100; each control 0/100 |
| Confirmatory decision | PASS |

Exact accounting and provenance:
[`results/isaac_model_order_confirmatory_v1.0/RESULTS.md`](results/isaac_model_order_confirmatory_v1.0/RESULTS.md).

## Configs

| File | Status |
| --- | --- |
| [`model_order_confirmatory_v1.0.json`](config/model_order_confirmatory_v1.0.json) | Frozen confirmatory contract |
| [`model_order_pilot_v0.3.json`](config/model_order_pilot_v0.3.json) | Valid process-isolated engineering pilot |
| [`model_order_pilot_v0.2.json`](config/model_order_pilot_v0.2.json) | Invalid shared-process pilot; excluded |
| [`pilot_v0.1.yaml`](config/pilot_v0.1.yaml) | Earlier CPU mechanism scaffold; preliminary only |

## Results

| Directory | Tier | Use |
| --- | --- | --- |
| [`isaac_model_order_confirmatory_v1.0`](results/isaac_model_order_confirmatory_v1.0/RESULTS.md) | Confirmatory | Primary Paper 002 evidence |
| [`isaac_model_order_pilot_v0.3`](results/isaac_model_order_pilot_v0.3/RESULTS.md) | Engineering pilot | Calibration only; excluded from confirmatory estimates |
| [`isaac_static_first_confirmatory_v0.2`](results/isaac_static_first_confirmatory_v0.2/RESULTS.md) | Drift anchor | Environment/policy isolation evidence only |
| [`pilot_v0.1`](results/pilot_v0.1/) | CPU mock | Preliminary mechanism check only |

## Implementation

| Module | Role |
| --- | --- |
| [`scripts/wm_expansion/target_dynamics.py`](../../../scripts/wm_expansion/target_dynamics.py) | Zero-order, constant-velocity, oracle target models and gate |
| [`scripts/orbit_reach_drift.py`](../../../scripts/orbit_reach_drift.py) | Isaac branch runner |
| [`scripts/run_exp_surg_003_model_order.py`](../../../scripts/run_exp_surg_003_model_order.py) | Static-first selection and process-isolated orchestration |
| [`scripts/aggregate_exp_surg_003_model_order.py`](../../../scripts/aggregate_exp_surg_003_model_order.py) | Validity checks and crossed-bootstrap analysis |
| [`scripts/plot_paper002_model_order.py`](../../../scripts/plot_paper002_model_order.py) | CPU-only figures, CSV tables, and hash manifest |

## Reproduce Derived Figures

No simulator or GPU is required:

```bash
python scripts/plot_paper002_model_order.py
```

Generated assets: [`docs/paper002/figures`](../../../docs/paper002/figures/README.md).

## Reproduce Isaac Run

The GPU run is complete. Re-execution should use the immutable tag, the VESSL
Isaac image, and the frozen config; it should not be run on a low-resource local
machine. See [`docs/paper002/vessl_runbook_v0.1.md`](../../../docs/paper002/vessl_runbook_v0.1.md).

## Boundary

This package supports a restricted prepared model-order expansion claim in one
Isaac target-drift family. It does not validate arbitrary world-model
reconstruction, tissue/contact dynamics, hardware transfer, or clinical use.
