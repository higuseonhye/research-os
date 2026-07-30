# Paper 002 Status

> Updated: 2026-07-30
>
> Scientific phase: confirmatory complete
>
> Writing phase: manuscript v1.0 complete; venue formatting and citation audit remain

## Decision

The frozen model-order confirmatory passed every conjunctive criterion. The
core evidence package is complete enough for a full paper draft.

| Milestone | Status |
| --- | --- |
| Isaac persistent-drift anchor | Complete and passed |
| Shared-process pilot v0.2 | Invalidated and excluded |
| Process-isolated pilot v0.3 | Complete; calibration only |
| Confirmatory preregistration v1.0 | Frozen before fresh data |
| Confirmatory VESSL execution | Complete: 400/400 Ep2 and 20/20 retention cells |
| Confirmatory validity | Passed |
| H1 prediction | Passed |
| H2 fixed-horizon behavior | Passed |
| H3 static retention | Passed |
| H4 drift/control gate validity | Passed |
| Manuscript v1.0 | Complete draft |
| Figures and CSV tables | Generated and hash-manifested |

## Primary Evidence

- C-B H=10 prediction error: -10.806 mm, 95% CI [-11.360, -10.331].
- C-B fixed-horizon final distance: -13.304 mm, 95% CI [-13.599, -12.982].
- C lower on both continuous endpoints in 100/100 paired cells.
- Secondary resolution rate: C 100%, B 76%.
- Static retention: B and C both 10/10; identical 1.501 mm mean distance.
- Gate: drift 100/100; static/noise/impulse each 0/100.
- Unexpected resets and forbidden violations: zero.

Exact report:
[`RESULTS.md`](../../experiments/surgical_intelligence/exp_surg_003_wm_expansion/results/isaac_model_order_confirmatory_v1.0/RESULTS.md).

## Audit Trail

| Item | Identity |
| --- | --- |
| Preregistration tag | `paper002-model-order-confirmatory-v1.0` |
| Frozen run source | `bea5a6ce78755db6f94b9cb74f6e841e3ebf6f01` |
| Raw artifact commit | `73a7e16` |
| Config SHA-256 | `9cbca0202f784a3a60569dbcf6f36e31a484c95393cb72ef5a030909e9e19635` |
| Execution isolation | Fresh Isaac process per seed-arm-condition |

## Publication Work Remaining

1. Verify and format the linked bibliography for the selected venue.
2. Choose venue template and convert the Markdown manuscript to its source format.
3. Perform author, affiliation, acknowledgements, and disclosure pass.
4. Decide whether hardware validation is a supplement, follow-up, or explicit limitation.
5. Freeze a submission tag after review; do not alter the raw confirmatory artifact.

## Claim Boundary

The positive result is scoped to a prepared zero-order-to-constant-velocity
expansion in one Isaac surgical-reach target-dynamics family. Hardware,
tissue-contact, autonomous representation invention, and clinical claims remain
open.
