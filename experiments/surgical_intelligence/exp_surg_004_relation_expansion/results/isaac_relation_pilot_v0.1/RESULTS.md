# Paper 003 Relation Pilot v0.1 — Isaac calibration

> **Engineering calibration only. Excluded from confirmatory evidence.**
> Same posture as [EXP-SURG-003 pilot v0.3](../../../exp_surg_003_wm_expansion/results/isaac_model_order_pilot_v0.3/RESULTS.md).
> **n = 1 seed.** Nothing here supports a claim. It exists to settle
> preregistration parameters, per the
> [draft preregistration](../../../../../docs/paper003/paper003_prereg_draft_v0.1.md).

## Provenance

- Run commit: `9770047` (`977004771dcce1c30e33c88fc4554c995b3b4717`)
- Runner: `scripts/orbit_reach_relation_pilot.py` via `scripts/run_paper003_pilot.sh`
- Task: `Isaac-Reach-Dual-STAR-IK-Rel-Play-v0`, Isaac Sim on A100-SXM4-80GB
- Isolation: fresh Isaac process per condition
- Seed: 300 (single)
- Placement tolerance: **20 mm**, inherited from this task family's existing
  success criterion, not fitted here — see the runbook for why that provenance
  matters
- Reference speed 15 mm/step, burst 10 on / 4 off, interaction radius 50 mm,
  dispense latency 6 steps

## Arm results, all four conditions

Miss distance from the true landing point at commitment.

| Condition | Missing structure | A | B repair | C mode | D relation | Gate | Lands at 20 mm |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| **coupled** | relation | 140.1 | 83.0 | 35.5 | **7.0** | 0.19 | **D** |
| **drift** | mode | — | 90.0 | **0.0** | 90.0 | 0.00 | **C** |
| noise | none | — | 27.2 | 129.9 | 27.2 | 0.00 | none |
| static | none | 0.0 | 0.0 | 0.0 | 0.0 | 0.00 | all |

All cells committed and were valid. Arm D estimated the reference pattern from
observation on the coupled cell (`d_estimated: true`); it declined to act on
every other condition, as the gate requires.

## What the pilot was for

Against the five deliverables the draft preregistration asks of it:

| # | Deliverable | Status |
| --- | --- | --- |
| 1 | Environment runs end to end, isolated per cell | **met** |
| 2 | Observation noise and timing irregularity under real physics | **not met** — the coupling is applied to the target command rather than emerging from contact, so no physical jitter is generated to measure |
| 3 | Speed sweep locating arm B's near-zero band | **not run** |
| 4 | Gate statistics across conditions | **met** — 0.19 on coupled, 0.00 on all three controls |
| 5 | Oracle clears 80%, task is solvable | **met** — oracle landed in every condition |

## Observations

**The operators dissociate.** Arm D takes the relational cell and loses the
mode cell; arm C does the reverse, landing at exactly 0.0 mm on constant drift
where a constant-velocity model is the correct one. This matters more than arm
D's win: it is what rules out arm D simply being a stronger predictor that wins
everywhere.

**No regression where the relation is absent.** On static and noise, arm D is
numerically identical to arm B — 0.0 and 27.2 mm. The gate declines and the arm
falls back rather than inventing motion.

**Arm C is not merely weaker.** It is catastrophic on noise (129.9 mm against
arm B's 27.2 mm), because velocity extrapolation amplifies observation noise.
Each operator has a regime where it is actively harmful.

## What this is not

One seed, one speed, one commitment per episode, and a coupling injected
through the target command rather than simulated contact. Deliverable 2 above
is unmet, which is the main reason the preregistration cannot be frozen from
this run. The confirmatory grid, seed sweep, and speed sweep have not run.

## Reproduce

```bash
for c in coupled drift static noise; do
  CONDITION=$c OUT_DIR=results/paper003_pilot_controls \
    bash scripts/run_paper003_pilot.sh
done
```

Records are written per condition as `pilot_<condition>_seed<seed>.json` with
per-step observations, gate decisions, and every arm's aim point.
