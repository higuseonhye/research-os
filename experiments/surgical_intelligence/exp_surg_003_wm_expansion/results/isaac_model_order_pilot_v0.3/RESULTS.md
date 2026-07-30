# EXP-SURG-003 Model-Order Pilot v0.3

> Engineering calibration only. Excluded from confirmatory evidence.

## Provenance

- Run commit: `59430cdec02d8cf97bf689a6147dab138b98b40b`
- Artifact commit: `028ebce`
- Config SHA-256: `9823a078d77aa9fe8aca939f29a5718e2b4cfae934bba5df8bec445da8f5ad8d`
- Isolation: fresh Isaac process per seed-arm-condition
- Candidate seeds: 200-219
- Selected before treatment: 200, 201, 202, 203, 205
- Ep2 grid: 5 seeds x 10 conditions x 4 arms = 200 complete cells

All validity checks passed: complete grids, matching reset fingerprints,
paired branch starts, ready prefixes, prediction windows, full drift exposure,
no unexpected resets, and no forbidden-region violations.

## Arm Results

| Arm | Success | H=10 prediction error | Final distance |
| --- | ---: | ---: | ---: |
| A frozen zero-order | 52% | 19.756 mm | 20.099 mm |
| B repaired zero-order | 82% | 18.101 mm | 18.716 mm |
| C gated constant velocity | 94% | 6.556 mm | 6.836 mm |
| D oracle velocity | 94% | 0.000 mm | 5.766 mm |

## Primary C Minus B Contrasts

| Endpoint | Estimate | Crossed-bootstrap 95% CI | Pair direction |
| --- | ---: | ---: | ---: |
| H=10 prediction error | -11.544 mm | [-12.542, -10.636] mm | C lower in 50/50 |
| Fixed-horizon final distance | -11.880 mm | [-13.761, -7.831] mm | C lower in 47/50 |
| 20 mm success rate | +0.12 | [-0.04, +0.34] | C better in 7/50 |

The three cells where C did not lower final distance were seed 200 under P04,
P05, and P09. The oracle also failed exactly those three cells. They remain in
the intention-to-treat aggregate.

## Retention And Gate Controls

- Static retention: B 5/5 and C 5/5; both mean final distance 1.365 mm.
- Persistent drift gate: 50/50 fired.
- Static, observation-noise, and single-impulse controls: 0/50 fired each.
- Forbidden violations and unexpected resets: zero.

## Pilot Decision

The original `pilot_pass` is `false` because B success was 82%, above the
predeclared 50% failure-regime ceiling. This result is preserved rather than
relabelled. The 20 mm binary endpoint saturated even though C reduced both
prediction error and fixed-horizon final distance substantially.

Before any fresh confirmatory data, the confirmatory plan therefore promotes
paired fixed-horizon final distance to the H2 primary endpoint and makes binary
success secondary. The full condition family remains represented; favorable
pilot conditions are not selected post hoc.

## Integrity

`SHA256SUMS` was generated on VESSL before commit. Git stores these text
artifacts with LF endings; the repository attributes pin LF for portable
verification. The combined result contains all Ep2 and retention records,
preconditions, condition summaries, and validity metadata. The combined
trajectory file contains all step-level traces.
