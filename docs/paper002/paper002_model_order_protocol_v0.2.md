# Paper 002 Model-Order Protocol v0.2

> Status: engineering pilot specification, not confirmatory evidence
> Date: 2026-07-30
> Config: `model_order_pilot_v0.2.json`

## Why this protocol exists

The earlier GRU pilot did not identify structural inadequacy cleanly. Its L1
model could predict every observation channel, including the target, so the
same model class could in principle learn constant drift. A failure under a
small update budget would therefore show optimization or sample-efficiency
limits, not that parameter update was structurally insufficient.

Protocol v0.2 makes the tested model classes explicit:

- L1 uses a zero-order target state: filtered position, zero future velocity.
- L1 repair may tune the position filter but cannot add a velocity state.
- L3 adds a first-order velocity state and a mode gate.
- The oracle uses the true injected velocity and is diagnostic only.

The claim is correspondingly narrow: a prepared constant-velocity expansion
can be warranted when a zero-order target model leaves persistent structured
residuals.

## Arms

| Arm | Model | Behavioral target |
| --- | --- | --- |
| A | Frozen zero-order, alpha 0.5 | Filtered current target |
| B | Repaired zero-order, alpha selected on Ep1 | Current target, no velocity rollout |
| C | Gated constant-velocity expansion | H-step predicted target |
| D | Oracle velocity, diagnostic | H-step oracle target |

The confirmatory horizon is `H=10`. The target prediction is passed to the
same Cartesian scripted controller in every arm. The evaluation command is
restored before each simulator step, so changing the policy target cannot
change the ground-truth target dynamics.

## Structural gate

The gate fires only if all criteria hold over the target-position history:

1. At least four deltas are present.
2. Mean speed exceeds 0.5 mm per step.
3. At least 75% of deltas are active.
4. Directional consistency is at least 0.90.
5. A constant-velocity predictor reduces one-step transition RMSE by at least 50%.

H4 uses matched target histories for persistent drift, static, observation
noise, and a single impulse. Synthetic control generation is deterministic and
uses fixed integer seeds; Python process hash values are not used.

## Pilot design

- Candidate simulator seeds: 200 through 219.
- Eligibility: static control first, before any treatment arm.
- Selection: first five eligible seeds in fixed numeric order.
- Ep2: 10 locked direction, speed, delay, and duration conditions.
- Pairing: same simulator seed and condition across A, B, C, and D.
- Retention: static target under B and C.
- Pilot observations are excluded from confirmatory analysis.

Each seed-policy pair runs all Ep2 conditions in one Isaac process. The
environment is deterministically reset for every condition. Aggregation rejects
the run if paired branch starts differ by more than 1 mm, commands differ by
more than 1 micrometer, any record is missing, a reset occurs, or a forbidden
region is entered.

## Pilot decision rules

The pilot is usable for preregistration freeze only when all checks pass:

- complete and paired execution grid;
- oracle success at least 80%;
- L3 success at least 70%;
- L1 success at most 50%;
- L3 mean H=10 prediction error lower than L1;
- L3 static retention at least 95%;
- drift gate rate at least 90%;
- each negative-control gate rate at most 10%.

These are engineering calibration gates, not confirmatory hypothesis tests.
If the oracle fails, the condition is infeasible and the controller/task must
be repaired. If L1 succeeds too often, drift speed or deadline may be adjusted
using pilot seeds only. If L3 prediction improves but behavior does not, the
world-model-to-controller connection is inadequate.

## VESSL execution

Run from the GPU workspace only:

```bash
cd /workspace/research-os
git switch codex/paper002-l1-l3-confirmatory
git pull --ff-only

export DISABLE_FABRIC=1
unset EXP_SURG_003_SKIP_BOOTSTRAP
export EXP_SURG_003_ZERO_AGENT=0
bash scripts/run_exp_surg_003_model_order_vessl.sh --smoke

export EXP_SURG_003_SKIP_BOOTSTRAP=1
export EXP_SURG_003_ZERO_AGENT=0
bash scripts/run_exp_surg_003_model_order_vessl.sh
```

Run the one-seed smoke first. It uses previously exposed seed 101 only for
infrastructure validation and is excluded from both pilot and confirmatory
analysis. Start the full pilot only after the smoke produces a complete valid
grid.

The command is resumable. Completed isolated outputs are skipped. The final
files are:

```text
results/isaac_model_order_pilot_v0.2/selection_manifest.json
results/isaac_model_order_pilot_v0.2/isaac_model_order_results.json
results/isaac_model_order_pilot_v0.2/isaac_model_order_trajectories.json
```

Do not create or run the confirmatory config until the pilot result has been
audited and the thresholds, conditions, seed-generation rule, exclusions, and
analysis decisions have been frozen in a commit and tag.
