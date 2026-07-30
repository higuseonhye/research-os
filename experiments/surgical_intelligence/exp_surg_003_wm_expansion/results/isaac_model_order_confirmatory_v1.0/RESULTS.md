# EXP-SURG-003 Model-Order Confirmatory v1.0

> Confirmatory result: PASS. All preregistered validity, prediction,
> behavior, retention, gate-control, and diagnostic criteria passed.

## Provenance

- Frozen preregistration tag: `paper002-model-order-confirmatory-v1.0`
- Run source commit: `bea5a6ce78755db6f94b9cb74f6e841e3ebf6f01`
- Artifact commit: `73a7e16`
- Config SHA-256: `9cbca0202f784a3a60569dbcf6f36e31a484c95393cb72ef5a030909e9e19635`
- Execution isolation: fresh Isaac process per seed-arm-condition cell
- Bootstrap: crossed seed and condition resampling, 10,000 draws, RNG seed `20260730`
- Pilot data: excluded from every confirmatory estimate

The immutable preregistration was frozen before any confirmatory seed was
executed. Raw artifacts can be checked from this directory with
`sha256sum -c SHA256SUMS` on an LF-preserving checkout.

## Accounting And Validity

- Candidate seeds: fixed integers 300 through 339.
- Static-control eligible: 34/40.
- Selected before treatment: 300, 301, 302, 303, 304, 305, 307, 308, 310, 311.
- Ep2 grid: 10 seeds x 10 fresh conditions x 4 arms = 400/400 cells.
- Static retention: 10 seeds x B/C = 20/20 cells.
- Maximum paired branch-start end-effector gap: 0 mm.
- Maximum paired command gap: 0 mm.
- Maximum branch-start distance: 15.396 mm, below the locked 21 mm limit.
- Failed prefixes, missing prediction windows, incomplete drift exposures,
  unexpected resets, and forbidden-region violations: zero.

The complete crossed grid and every execution-validity gate passed.

## Arm Results

| Arm | n | Success | H=10 prediction error | Final distance |
| --- | ---: | ---: | ---: | ---: |
| A frozen zero-order | 100 | 39% | 20.081 mm | 20.388 mm |
| B repaired zero-order | 100 | 76% | 18.401 mm | 18.905 mm |
| C gated constant velocity | 100 | 100% | 7.595 mm | 5.601 mm |
| D oracle velocity | 100 | 100% | 0.000 mm | 4.087 mm |

All arms used the same scripted Cartesian controller. Only the target model
and, for C, the preregistered structural gate differed.

## Primary C Minus B Contrasts

| Endpoint | Estimate | Crossed-bootstrap 95% CI | C-favorable pairs | Decision |
| --- | ---: | ---: | ---: | --- |
| H=10 prediction error | -10.806 mm | [-11.360, -10.331] mm | 100/100 | H1 PASS |
| Fixed-horizon final distance | -13.304 mm | [-13.599, -12.982] mm | 100/100 | H2 PASS |
| 20 mm success rate | +0.24 | [+0.08, +0.45] | 24/100 strictly better | Secondary |

Both primary interval upper bounds are below the preregistered -5 mm
criterion. Binary success is reported but remains secondary, as frozen before
the run.

## Condition Robustness

| Condition | Prediction C-B | Final distance C-B | B success | C success |
| --- | ---: | ---: | ---: | ---: |
| C01 | -11.769 mm | -12.865 mm | 9/10 | 10/10 |
| C02 | -10.364 mm | -13.166 mm | 9/10 | 10/10 |
| C03 | -12.462 mm | -13.807 mm | 9/10 | 10/10 |
| C04 | -10.000 mm | -13.586 mm | 5/10 | 10/10 |
| C05 | -10.461 mm | -12.801 mm | 10/10 | 10/10 |
| C06 | -10.364 mm | -13.593 mm | 5/10 | 10/10 |
| C07 | -11.768 mm | -12.716 mm | 10/10 | 10/10 |
| C08 | -10.502 mm | -13.192 mm | 9/10 | 10/10 |
| C09 | -10.367 mm | -13.427 mm | 5/10 | 10/10 |
| C10 | -9.998 mm | -13.888 mm | 5/10 | 10/10 |

C had lower prediction error and lower final distance in every one of the 100
crossed seed-condition cells. No oracle cell failed, so the preregistered
intention-to-treat result and the descriptive oracle-feasible subset coincide.

## Ep1 Diagnostic

The locked zero-order alpha search selected 1.0 after four attempts but left
15.000 mm mean held-out H=10 prediction error. The order-one
constant-velocity fit selected position and velocity alpha 1.0 and reduced the
same diagnostic error to numerical zero. The structural gate fired with
active fraction 1.0, directional consistency 1.0, and constant-velocity error
improvement 1.0. This diagnostic reproduced the preregistered parameter lock.

## Retention And Gate Controls

- Static retention: B 10/10 and C 10/10 successful.
- Static mean final distance: B = C = 1.501 mm.
- Paired static success difference: 0.00, 95% CI [0.00, 0.00]; H3 PASS.
- Persistent drift gate: 100/100, Wilson 95% CI [96.30%, 100%].
- Static, observation noise, and single impulse: 0/100 each, Wilson upper
  95% bound 3.70% for each; H4 PASS.

## Confirmatory Decision

All conjunctive criteria passed: execution validity, Ep1 parameter lock,
oracle behavior, C success floor, H1 prediction interval, H2 final-distance
interval, H3 static retention, and both H4 drift/control gates. The recorded
field `confirmatory_pass` is therefore `true`.

## Claim Boundary

This result supports a restricted claim in one Isaac surgical-reach target
dynamics setting: after a zero-order repair cannot represent persistent
constant drift, a prepared gated velocity-state expansion improves prediction
and fixed-horizon control without static regression. It does not establish
autonomous model invention, arbitrary world-model expansion, tissue-contact
validity, hardware transfer, or clinical efficacy.

## Derived Materials

Publication figures and machine-readable tables are generated directly from
the frozen result and trajectory JSON files:

```bash
python scripts/plot_paper002_model_order.py
```

See [`docs/paper002/figures`](../../../../../docs/paper002/figures/).
