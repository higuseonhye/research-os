# Paper 002: Failure-Conditioned Model-Order Expansion

> Status: confirmatory complete; manuscript v1.0 drafted
>
> Frozen preregistration: `paper002-model-order-confirmatory-v1.0`
>
> Result artifact: `73a7e16`

## Headline Result

In a complete 400-cell Isaac Sim confirmatory grid, the gated
constant-velocity model reduced H=10 prediction error by 10.806 mm and
fixed-horizon final distance by 13.304 mm relative to repaired zero order.
Both crossed-bootstrap 95% intervals cleared the preregistered 5 mm criterion.
Static retention and all gate-specificity controls passed.

## Start Here

| Document | Purpose |
| --- | --- |
| [Manuscript v1.0](paper002_manuscript_model_order_v1.0.md) | Complete confirmatory paper draft |
| [Status](status.md) | Current phase, decisions, and next publication work |
| [Frozen preregistration](paper002_model_order_confirmatory_prereg_v1.0.md) | Fresh sample, endpoints, and locked decision rules |
| [Confirmatory result](../../experiments/surgical_intelligence/exp_surg_003_wm_expansion/results/isaac_model_order_confirmatory_v1.0/RESULTS.md) | Exact accounting, estimates, intervals, and provenance |
| [Figures and CSV tables](figures/README.md) | Reproducible manuscript panels and machine-readable tables |
| [Process-isolated pilot](../../experiments/surgical_intelligence/exp_surg_003_wm_expansion/results/isaac_model_order_pilot_v0.3/RESULTS.md) | Excluded engineering calibration |
| [Model-order protocol v0.3](paper002_model_order_protocol_v0.3.md) | Isolation amendment that closed simulator carryover |
| [Related work v0.2](paper002_related_work_v0.2.md) | Positioning and bibliography checklist |
| [Physical validation roadmap](paper002_physical_validation_roadmap_v0.1.md) | Deferred hardware evidence track |

## Confirmatory Design

```text
Static-first seed selection
  -> shared Ep1 persistent drift
  -> best allowed zero-order parameter repair
  -> persistent/directional/CV-explainable residual gate
  -> A frozen order 0 | B repaired order 0 | C gated order 1 | D oracle
  -> 10 fresh seeds x 10 fresh drift conditions x 4 arms
  -> static retention and gate controls
```

All arms use the same scripted Cartesian controller. The model's H=10 forecast
is the controller target. Every seed-arm-condition cell runs in a fresh Isaac
process.

## Confirmatory Summary

| Endpoint | B repaired zero order | C gated constant velocity | C-B |
| --- | ---: | ---: | ---: |
| H=10 prediction error | 18.401 mm | 7.595 mm | -10.806 mm, 95% CI [-11.360, -10.331] |
| Fixed-horizon final distance | 18.905 mm | 5.601 mm | -13.304 mm, 95% CI [-13.599, -12.982] |
| 20 mm resolution rate | 76% | 100% | +0.24, secondary |
| Static retention | 10/10 | 10/10 | non-inferior |

Gate activation was 100/100 on persistent drift and 0/100 on each of static,
observation-noise, and single-impulse controls. There were no missing cells,
unexpected resets, or forbidden-region violations.

## Reproduce Derived Materials

No simulator or GPU is required to recreate the paper figures and CSV tables:

```bash
python scripts/plot_paper002_model_order.py
```

The Isaac experiment itself should run only on the documented VESSL image and
frozen source/config. See [the VESSL runbook](vessl_runbook_v0.1.md).

## Claim Boundary

Supported: in the specified Isaac target-drift family, structured failure after
zero-order repair warrants a prepared velocity-state expansion that improves
prediction-linked control without static regression.

Not supported: unconstrained model invention, arbitrary world-model expansion,
tissue/contact validity, hardware transfer, clinical efficacy, or operating-
room deployment.

Historical mock-to-physics documents remain under
[`archive/mock_to_physics`](archive/mock_to_physics/README.md) and must not be
cited as Paper 002 evidence.
