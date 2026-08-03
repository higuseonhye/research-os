# Paper 003 Relation Pilot v0.1 — Isaac calibration

> **Engineering calibration only. Excluded from confirmatory evidence.**
> Same posture as [EXP-SURG-003 pilot v0.3](../../../exp_surg_003_wm_expansion/results/isaac_model_order_pilot_v0.3/RESULTS.md).
> **10 seeds, one speed.** Nothing here supports a claim. It exists to settle
> preregistration parameters, per the
> [draft preregistration](../../../../../docs/paper003/paper003_prereg_draft_v0.1.md).

## Provenance

- Runs: sweep v5 at commit `30a3db0` (uniform commit policy, estimated coupling).
  Earlier sweeps at `9770047` and `b3721b0` are superseded; see below.
- Runner: `scripts/orbit_reach_relation_pilot.py` via `scripts/run_paper003_pilot.sh`
- Task: `Isaac-Reach-Dual-STAR-IK-Rel-Play-v0`, Isaac Sim on A100-SXM4-80GB
- Isolation: fresh Isaac process per condition
- Seeds: 300-309, encounter geometry drawn per seed
- Placement tolerance: **20 mm**, inherited from this task family's existing
  success criterion, not fitted here — see the runbook for why that provenance
  matters
- Reference speed 15 mm/step, burst 10 on / 4 off, interaction radius 50 mm,
  dispense latency 6 steps

## Arm results — current (sweep v5), 10 seeds, randomised encounter geometry

Uniform commit policy and coupling parameters estimated from observation.
Median miss distance from the true landing point, and land rate at 20 mm.

| Condition | Missing | Commits | Gate | estD | B repair | C mode | D relation | Land B / C / D |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **coupled** | relation | 9/10 | 0.80 | 0.56 | 14.4 | 37.8 | **4.9** | 0.56 / 0.22 / **0.67** |
| **drift** | mode | 10/10 | 0.00 | 0.00 | 90.0 | **0.0** | 90.0 | 0.00 / **1.00** / 0.00 |
| noise | none | 10/10 | 0.00 | 0.00 | 22.4 | 152.5 | 22.4 | 0.40 / 0.00 / 0.40 |
| static | none | 9/10 | 0.00 | 0.00 | 0.0 | 0.0 | 0.0 | 1.00 / 1.00 / 1.00 |

### Both declared directions materialised

The commit policy and the removal of the parameter loan were locked before this
run with their expected effects written down. Both appeared, and they pulled
against each other:

| | v4: first-eligible, coupling supplied | v5: uniform, coupling estimated |
| --- | ---: | ---: |
| `estD` | 0.33 | **0.56** |
| Arm D median miss | 3.0 mm | **4.9 mm** |
| Arm D land rate | 0.67 | 0.67 |
| Arm B land rate | 0.67 | 0.56 |

Uniform commitment raised the rate at which arm D could act, as predicted.
Estimating the coupling cost it accuracy, also as predicted. Neither direction
was inferred after the fact.

### Arm D leads for the first time, and it is one cell

Arm D is ahead of parameter repair on land rate without an oracle and without
being handed the coupling — 0.67 against 0.56.

**That is 6 of 9 against 5 of 9.** A single cell. It is not evidence of
anything and must not be reported as an effect; the sweep is far too small for
a rate comparison. What it establishes is only that the comparison is now being
made on honest terms.

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
| 4 | Gate statistics across conditions | **met** — 0.80 on coupled, 0.00 on all three controls |
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

**Arm C is not merely weaker.** It is catastrophic on noise — 152.5 mm against
arm B's 22.4 — because velocity extrapolation amplifies observation error.
Each operator has a regime where it is actively harmful.

**Arm D's advantage is not yet established.** It leads parameter repair by one
cell out of nine. That is a sample-size problem, not a finding.

## Blocking before this can inform a preregistration

1. ~~Commit policy~~ — **settled.** Uniform over eligible steps, locked with
   its expected directional effect declared in advance.
2. ~~Arm D is handed the coupling parameters~~ — **settled.** Radius and gain
   are fitted from the observed contacts; arm D declines when the fit is not
   identifiable.
3. **Sample size.** Nine committed coupled cells cannot support a land-rate
   comparison. The current 0.67 against 0.56 is one cell.
4. **Deliverable 2 remains unmet** — the coupling is injected through the
   target command rather than emerging from contact, so there is no physical
   jitter to measure, and the observation noise the estimator was characterised
   against is absent here.

## What this is not

Ten seeds at one speed, one commitment per episode, and a coupling that does
not arise from simulated contact. Nine committed cells on the treatment
condition. Nothing here is a confirmatory estimate.

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
| Committed at the first eligible step | Gate rarely fired yet; arm D fell back in two of three cells |
| Coupling parameters handed to arm D | Its accuracy measured the loan, not inference |

## Reproduce

```bash
for c in coupled drift static noise; do
  CONDITION=$c OUT_DIR=results/paper003_pilot_controls \
    bash scripts/run_paper003_pilot.sh
done
```

Records are written per condition as `pilot_<condition>_seed<seed>.json` with
per-step observations, gate decisions, and every arm's aim point.
