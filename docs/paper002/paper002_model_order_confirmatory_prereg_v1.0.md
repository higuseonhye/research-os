# Paper 002 Model-Order Confirmatory Preregistration v1.0

> Status: FROZEN BEFORE CONFIRMATORY DATA
> Freeze identity: immutable tag `paper002-model-order-confirmatory-v1.0`
> Config: `model_order_confirmatory_v1.0.json`
> Pilot data: excluded from every confirmatory estimate

## Research Question

When persistent target drift produces structured residuals that a zero-order
target model cannot absorb, does a gated constant-velocity state expansion
improve true open-loop prediction and fixed-horizon control without degrading
static behavior or firing on matched negative controls?

The claim is limited to the specified Isaac surgical-reach task and target
dynamics. It is not a claim about tissue interaction or clinical efficacy.

## Locked Arms

| Arm | Target model | Role |
| --- | --- | --- |
| A | Frozen zero-order, position alpha 0.5 | Secondary baseline |
| B | Repaired zero-order, position alpha 1.0 | Primary comparator |
| C | Gated constant velocity, position/velocity alpha 1.0 | Primary intervention |
| D | True injected velocity | Diagnostic oracle only |

All arms use the same Cartesian scripted controller. The model prediction is
the policy target; the simulator evaluation target is restored before each
step. Prediction horizon is 10 steps.

## Fresh Confirmatory Sample

- Candidate seeds are the fixed integers 300 through 339.
- Static control is run before every treatment.
- The first 10 statically eligible seeds in numeric order are locked.
- No treatment result may influence seed selection.
- Pilot seeds 101 and 200-219 cannot enter the confirmatory sample.
- Expected Ep2 grid: 10 selected seeds x 10 conditions x 4 arms = 400 cells.
- Static retention: 10 seeds x B/C = 20 cells.

Each seed-arm-condition cell runs in a fresh Isaac process. Missing cells,
failed prefixes, cross-policy branch-start gaps above 1 mm, command gaps above
1 micrometer, unexpected resets, incomplete drift exposure, or forbidden
violations make the run invalid.

## Fresh Conditions

The 10 C01-C10 conditions in the config reuse no exact pilot condition. They
balance positive and negative x/y axes and all four planar diagonals, with
locked speeds from 1.7 to 2.0 mm per step, delays from 1 to 5 steps, and
durations from 20 to 23 steps. The Ep1 adaptation trace remains +x at 1.5 mm
per step. No condition may be changed after the freeze tag.

## Confirmatory Hypotheses

### H1: Prediction

For C minus B, the upper endpoint of the 95% crossed-bootstrap confidence
interval for mean true open-loop H=10 prediction error must be at most
`-0.005 m`. Thus the entire interval must support at least 5 mm improvement.

### H2: Behavior

For C minus B, the upper endpoint of the 95% crossed-bootstrap confidence
interval for mean final end-effector distance after full drift exposure must
be at most `-0.005 m`.

The 20 mm binary success rate is secondary because the pilot showed threshold
saturation. It is reported with its crossed-bootstrap interval but cannot
replace H2.

### H3: Static Retention

C static success must be at least 95%, and the lower endpoint of the paired
seed-bootstrap interval for C minus B static success must exceed the locked
non-inferiority margin of -5 percentage points.

### H4: Gate Validity

- Persistent drift gate rate must be at least 90%.
- Static, observation-noise, and single-impulse gate rates must each be at
  most 10%.

## Diagnostic Gates

- D oracle success must be at least 80%.
- C success must be at least 80%.
- Ep1 parameter fits must reproduce the locked alpha values.
- Every execution-validity check must pass.

Confirmatory support requires every H1-H4 and diagnostic gate to pass. This
conjunctive rule is fixed before data and no successful subset is sufficient.

## Estimand And Analysis

The primary estimand includes every valid crossed selected-seed/condition cell
regardless of oracle outcome. For each endpoint, compute C minus B within every
cell and resample seeds and conditions independently with replacement for
10,000 crossed-bootstrap draws. The RNG seed is 20260730. Report the mean,
two-sided percentile 95% interval, and the fraction of pairs favoring C.

Oracle-feasible cells may be summarized as a descriptive sensitivity analysis
only. They cannot replace the intention-to-treat primary result. A and D are
secondary/diagnostic and are excluded from the primary contrast.

## Gate Controls And Safety

The structural gate remains locked at: window 8, minimum 4 deltas, speed floor
0.5 mm/step, active fraction 0.75, directional consistency 0.90, and constant-
velocity error improvement 0.50. Noise sigma is 0.2 mm. Report Wilson 95%
intervals for persistent drift, static, noise, and impulse controls.

Forbidden-region violations and simulator resets are always reported. No
episode is silently removed. A technical failure requires a new versioned
protocol; it cannot be repaired after inspecting confirmatory outcomes.

## Stopping And Reporting

There is no interim efficacy analysis and no optional stopping. Run every
locked cell or declare the run invalid. Preserve the config, selection
manifest, orchestration manifest, combined records, preconditions,
trajectories, checksums, source commit, and frozen tag.

Results will be reported even if one or all confirmatory gates fail.
