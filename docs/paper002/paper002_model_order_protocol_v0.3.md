# Paper 002 Model-Order Protocol v0.3

> Status: engineering pilot amendment, not confirmatory evidence
> Date: 2026-07-30
> Config: `model_order_pilot_v0.3.json`

## Scope

All scientific hypotheses, arms, model parameters, gate thresholds, pilot
seeds, conditions, retention checks, and decision rules remain identical to
v0.2. This amendment changes execution isolation only.

## Reason for amendment

The v0.2 pilot batched ten conditions for a seed-policy pair inside one Isaac
process. Although the environment received the same reset seed before every
condition, the preceding policy trajectory affected later reset outcomes.
This produced arm-dependent static-prefix failures, including seed 200/P02
and several seed 205 conditions. The aggregation correctly rejected the
incomplete crossed grid. No v0.2 treatment result is admissible as pilot or
confirmatory evidence.

## Isolation contract

Ep2 v0.3 launches a fresh Isaac process for every `seed x arm x condition`
cell. Each output directory must contain exactly one result, one trajectory,
and one precondition. Eligibility and static retention remain isolated by
seed and arm as before. Aggregation rejects missing cells, condition-ID
mismatches, cross-policy branch-start gaps above 1 mm, command gaps above
1 micrometer, failed prefixes, simulator resets, or forbidden-region entries.

The two-condition isolation smoke uses already exposed pilot seed 200 and
conditions P01/P02 solely to reproduce and close the v0.2 execution defect.
It is excluded from all pilot and confirmatory analyses.

## Execution

```bash
cd /workspace/research-os
git pull --ff-only

EXP_SURG_003_SKIP_BOOTSTRAP=1 EXP_SURG_003_ZERO_AGENT=0 DISABLE_FABRIC=1 \
  bash scripts/run_exp_surg_003_model_order_vessl.sh --smoke

EXP_SURG_003_SKIP_BOOTSTRAP=1 EXP_SURG_003_ZERO_AGENT=0 DISABLE_FABRIC=1 \
  bash scripts/run_exp_surg_003_model_order_vessl.sh
```

The pilot output is written to
`results/isaac_model_order_pilot_v0.3/`. Confirmatory seeds remain untouched
until this engineering pilot is audited and the preregistration is frozen.

## Outcome

The process-isolated pilot completed a valid 200-cell grid. Prediction error
and fixed-horizon final distance favored L3, while the original 20 mm binary
success gate saturated and the preregistered pilot pass remained false. See
the [exact pilot results](../../experiments/surgical_intelligence/exp_surg_003_wm_expansion/results/isaac_model_order_pilot_v0.3/RESULTS.md).

The frozen fresh-data design is
[confirmatory preregistration v1.0](paper002_model_order_confirmatory_prereg_v1.0.md).
