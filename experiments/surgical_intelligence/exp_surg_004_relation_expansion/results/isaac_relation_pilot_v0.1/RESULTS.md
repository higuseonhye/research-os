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

## Arm results — current, 10 seeds with randomised encounter geometry

Median miss distance from the true landing point, and land rate at 20 mm.

| Condition | Missing | Commits | Gate | estD | B repair | C mode | D relation | Land B / C / D |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **coupled** | relation | 9/10 | 0.80 | 0.33 | 9.1 | 23.5 | **3.0** | 0.67 / 0.44 / **0.67** |
| **drift** | mode | 10/10 | 0.00 | 0.00 | 90.0 | **0.0** | 90.0 | 0.00 / **1.00** / 0.00 |
| noise | none | 10/10 | 0.00 | 0.00 | 27.2 | 184.7 | 27.2 | 0.20 / 0.00 / 0.20 |
| static | none | 9/10 | 0.00 | 0.00 | 0.0 | 0.0 | 0.0 | 1.00 / 1.00 / 1.00 |

**Arm D does not beat parameter repair on land rate.** Both sit at 0.67 on the
coupled condition, because `estD` is only 0.33 — in two of every three
committed cells the gate had not yet fired at the commit moment and arm D fell
back to zero-order, making it identical to arm B by construction. Where arm D
does act its median miss is 3.0 mm against 9.1 mm, but that is a minority of
cells and not a rate the paper can claim.

The cause is protocol, not model: commitment fires at the **first eligible
step**, which falls during the approach, before the target has moved enough for
a proximity-conditioned gate to fire. When to commit among eligible steps is a
preregistration decision and has not been made.

### Superseded: the fixed-geometry numbers

An earlier version of this file reported arm D at 7.0 mm and a 1.00 land rate.
Those came from a degenerate encounter — the reference axis was fixed to +x
with zero lateral offset, so ten seeds produced ten translations of a single
head-on pass. Under that geometry the contact normal coincides with the
reference's heading, which happened to make a since-corrected modelling error
invisible. **Do not cite those figures.**

The dissociation survived the correction: arm C still takes the mode condition
outright at 0.0 mm, and arm D still declines there.

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

**The operators dissociate, and that is the durable finding.** Arm C takes the
mode condition outright — 0.0 mm, a 1.00 land rate — and arm D declines there,
scoring identically to plain repair. It rules out the obvious objection that
the relational arm is simply a stronger predictor that wins everywhere. This
survived every correction below.

**No regression where the relation is absent.** On static and noise arm D is
numerically identical to arm B. The gate declines and the arm falls back
rather than inventing motion.

**Arm C is not merely weaker.** It is catastrophic on noise — 184.7 mm against
arm B's 27.2 — because velocity extrapolation amplifies observation error.
Each operator has a regime where it is actively harmful.

**Arm D's advantage is not yet established.** See the land-rate parity above.

## Blocking before this can inform a preregistration

1. **Commit policy.** Committing at the first eligible step biases against arm
   D, which needs the gate to have fired. Choosing the policy after seeing
   which arm it favours is precisely what preregistration prevents, so it has
   to be settled on independent grounds.
2. **Arm D is handed the coupling parameters.** It rolls forward with the same
   `coupling_displacement`, `interaction_radius` and `coupling_gain` used to
   generate the ground truth, estimating only the reference's burst pattern.
   That is a weaker posture than Paper 002's prepared operator, where
   parameters were estimated. Either estimate them from observation, or state
   the boundary and narrow the claim.
3. **Deliverable 2 remains unmet** — the coupling is injected through the
   target command rather than emerging from contact, so there is no physical
   jitter to measure.

## What this is not

Ten seeds at one speed, one commitment per episode, and a coupling that does
not arise from simulated contact. Nothing here is a confirmatory estimate.

## Correction log

Findings that changed materially during this pilot, kept so the record is not
read as though it arrived clean:

| What | Effect |
| --- | --- |
| Arm D never consulted the relation gate | Invented 90 mm of motion on a static target |
| Gate required for commitment | Skipped every non-relational cell, making H4 untestable |
| Eligibility ignored self-driven motion | Drift never committed; the mode operator could not be shown winning |
| Fixed head-on encounter geometry | Ten seeds were ten translations of one encounter |
| Predicted along the reference's heading | Correct only head-on; arm D hit 60.4 mm under varied geometry |
| Approach shorter than one burst cycle | Four of ten cells unmeasurable |

## Reproduce

```bash
for c in coupled drift static noise; do
  CONDITION=$c OUT_DIR=results/paper003_pilot_controls \
    bash scripts/run_paper003_pilot.sh
done
```

Records are written per condition as `pilot_<condition>_seed<seed>.json` with
per-step observations, gate decisions, and every arm's aim point.
