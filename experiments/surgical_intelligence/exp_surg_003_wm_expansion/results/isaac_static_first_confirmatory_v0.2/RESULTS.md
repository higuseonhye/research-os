# EXP-SURG-003 Isaac drift anchor confirmatory v0.2

> **Decision:** PASS
> **Executed:** 2026-07-30 on VESSL
> **Execution code:** `ccf9bb0620a74b098d79ba34c538b20abd8b70e2`
> **Artifact commit:** `4e67c61`

## Scope

This run tests whether the Isaac surgical reach environment produces an isolated, reproducible persistent-drift contrast between a policy that follows the updated target and a policy that continues to follow the pre-drift target.

It is an engineering and task-regime anchor for EXP-SURG-003. It is not the Paper 002 world-model structural-expansion comparison.

## Locked design

- Candidate seeds: fixed order `100–139`
- Eligibility: static control only, before treatment
- Quota: first 10 eligible seeds
- Selected seeds: `101, 102, 103, 104, 105, 107, 108, 109, 111, 112`
- Process isolation: one fresh Isaac process per `(seed, policy)`
- Drift: x-axis, `0.0003 m/step`, 80 steps, onset 40
- Success tolerance: `0.02 m`
- Prefix readiness: 5 stable steps, maximum 200 steps
- Paired-start tolerance: `0.001 m`

The selection manifest was written before `TRACK_DRIFTING` or `TRACK_FROZEN` ran. Of 40 candidates, 29 were eligible. Eleven were ineligible: eight failed or exceeded the static-control tolerance and three did not reach prefix readiness.

## Protocol validity

| Check | Result |
| --- | ---: |
| Requested / ready paired seeds | 10 / 10 |
| Cross-policy prefix match | PASS |
| Maximum branch-start EE gap | `0.0 m` |
| Maximum branch-start command gap | `0.0 m` |
| Maximum branch-start distance | `0.014230 m` |
| Full drift exposure | PASS |
| Static control | PASS |
| Static/frozen EE and action isolation | `0.0 / 0.0` over 160 steps per seed |
| Unexpected environment resets | 0 |
| Selection locked before treatment | PASS |

## Outcomes

| Policy | n | Success | Mean final distance | Mean completion steps |
| --- | ---: | ---: | ---: | ---: |
| `STATIC_CONTROL` | 10 | **100%** | `0.0000075 m` | 221.9 |
| `TRACK_DRIFTING` | 10 | **100%** | `0.0037504 m` | 141.9 |
| `TRACK_FROZEN` | 10 | **0%** | `0.0240001 m` | 221.9 |

The mean paired frozen-minus-moving final-distance improvement was `0.0202497 m` (**20.250 mm**). The moving-target policy was better on all 10 paired seeds; paired improvements ranged from 20.097 mm to 20.389 mm. No forbidden violations occurred.

All locked effect gates passed:

- moving-target success rate at least 0.8
- frozen-target success rate at most 0.2
- positive mean paired final-distance improvement
- zero forbidden violations

The generated aggregate therefore reports `confirmatory_pass: true`.

## Claim boundary

Supported: the persistent-drift environment, static-first eligibility protocol, process isolation, and moving-vs-frozen policy contrast work as intended on fresh seeds.

Not supported by this run: L3 structural expansion vs L1 parameter repair, H=10 world-model prediction error, the complete H1–H4 gate study, hardware transfer, or clinical claims.

## Artifacts

- [`selection_manifest.json`](selection_manifest.json): locked selection, candidate accounting, parameters, and analysis contract
- [`isaac_drift_results.json`](isaac_drift_results.json): preconditions, per-policy records, validity checks, and effect gates
- [`isaac_drift_trajectories.json`](isaac_drift_trajectories.json): selected-seed trajectories used for isolation checks
- [`git_commit.txt`](git_commit.txt): execution code revision
- [`SHA256SUMS`](SHA256SUMS): integrity checks for the generated artifacts

Verify from this directory with:

```bash
sha256sum -c SHA256SUMS
```
