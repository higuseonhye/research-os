# Paper 003 Probe-Encounter Sweep v0.2 — Isaac calibration

> **Engineering calibration only. Excluded from confirmatory evidence.**
> 50 cells: 5 conditions × 10 seeds, one speed, injected coupling.
> Supersedes [v0.1](../isaac_relation_pilot_v0.1/RESULTS.md) for the gate and
> the encounter; the arm comparison in both is calibration, not a result.

## Provenance

- Runs: 2026-08-04 on A100-SXM4-80GB at commit `d6c8cdd`
- Runner: `scripts/orbit_reach_relation_pilot.py` via `scripts/run_paper003_pilot.sh`
- Task: `Isaac-Reach-Dual-STAR-IK-Rel-Play-v0`, fresh Isaac process per cell
- Seeds 300–309; encounter `probe` (advance 7, withdraw 5, hold 2)
- Gate: post-contact contrast, fixed 3-step displacement window, two consecutive
  crossings required
- Placement tolerance 20 mm, inherited from the task family

## What this sweep was for, and what it settled

### 1. The real-contact branch is decided — Branch B

```json
{"articulations": ["robot_1", "robot_2"], "rigid_objects": [], "sensors": ["ee_1_frame", "ee_2_frame"]}
```

**`rigid_objects` is empty.** There is no existing rigid body to reuse, so real
contact physics requires **adding one**. That forks the task family, and the
20 mm tolerance inherited from Paper 001/002 has to be re-argued rather than
carried across — it was established for a task whose scene this no longer is.

This is the question the session was opened to answer, and it is now settled by
observation rather than assumption.

### 2. H3 gate specificity — met, and the new control was the real test

| Condition | Gate (trial) | Gate (per-step) | H3 requires |
| --- | ---: | ---: | --- |
| **coupled** | **1.00** | 0.77 | ≥ 0.90 |
| drift | 0.00 | 0.00 | ≤ 0.10 |
| static | 0.00 | 0.00 | ≤ 0.10 |
| noise | 0.00 | 0.00 | ≤ 0.10 |
| **slide** | **0.00** | 0.00 | ≤ 0.10 |

`slide` is the control added the same day, and the only one that exercises the
constant-velocity clause — the clause that keeps Paper 003 from collapsing into
Paper 002. Every earlier control rejected on proximity contrast alone. Under the
original gate this control failed outright, claiming a relation in **every**
trial. It is now silent in all ten.

`normal_alignment` is 1.000 at both median and minimum, which is the correct
value under injected coupling and confirms the diagnostic is wired correctly. It
carries no information until contact is real.

### 3. The operator dissociation survived

| Condition | B | C | D | D\* |
| --- | ---: | ---: | ---: | ---: |
| coupled | 0.90 | 0.70 | 0.90 | 1.00 |
| drift | 0.00 | **1.00** | 0.00 | 1.00 |
| slide | 0.00 | **1.00** | 0.00 | 1.00 |
| noise | 0.40 | 0.00 | 0.40 | 1.00 |
| static | 1.00 | 1.00 | 1.00 | 1.00 |

Arm C takes drift and slide outright and is catastrophic on noise (163.9 mm
median against arm B's 22.4 mm). Each operator still has a regime where it is
actively harmful, which is what rules out "the relational arm is simply a
stronger predictor".

## The regression this sweep exposed

**Arm B is now indistinguishable from arm D on the treatment condition.**

| | v0.1 (`burst`) | v0.2 (`probe`) |
| --- | ---: | ---: |
| B median miss | 14.4 mm | **0.1 mm** |
| B land rate | 0.56 | **0.90** |
| D median miss | 4.9 mm | 0.1 mm |
| D land rate | 0.67 | 0.90 |

The `probe` encounter advances for 7 steps, withdraws for 5 and holds for 2, so
the reference is closing for only half the cycle. Commit steps are drawn
uniformly over eligible steps, and in most cells the resulting 6-step dispense
window contains no contact at all. The target does not move, so zero-order is
exact.

**This removes H1's premise.** A capability threshold requires `success(B)` to
sit in a near-zero band; at 0.90 there is no threshold to cross. The
identifiability fix that made the gate honest was bought at the cost of the
task's discriminating power, and that trade is not acceptable as it stands.

### What will not be done about it

Adjusting the encounter until arm B fails again. The parameters would then have
been chosen by looking at which arm they favour, which is the move
preregistration exists to prevent.

### What the actual defect is

`CommitmentEpisode.motion_expected()` decides eligibility, and it does not know
about the withdrawal. It admits steps on the grounds that contact is coming
when the reference is in fact retreating, so cells are scored in which nothing
moves during the action.

A cell where the target does not move is not a trial of "commit to an
irreversible placement on a moving target" — it is a different task that every
arm solves. This is the same category of defect as the v0.1 approach distance
being shorter than one burst cycle, and it admits the same arm-neutral remedy:
**eligibility must reflect whether the world produces motion over the dispense
window**, which is a property of the world and not of any arm's readiness.

Fixing it is CPU work with test coverage, not a parameter change — but it is
**not sufficient**. Measured against ground truth, the predicate admits
stationary cells in 51% of cases under `burst` as well, so it was always
over-admitting; `probe` only made it worse. Correcting it does not bring arm B
near zero, and neither does any encounter parameter tried.

See [the two-body encounter note](../../../../../docs/paper003/paper003_two_body_encounter_v0.1.md)
for what the follow-up found: the identifiability/difficulty tension is resolved
by splitting the reference into two bodies, but **arm B still never approaches
zero**, because one contact pass displaces the target by roughly 15 mm against a
20 mm tolerance. The endpoint's reachability is downstream of the tolerance,
which cannot be set before the Branch B scene exists.

## Status against the pilot's deliverables

| # | Deliverable | Status |
| --- | --- | --- |
| 1 | Environment runs end to end, isolated per cell | met |
| 2 | Observation noise and timing under real physics | **not met** — Branch B now known to be required |
| 3 | Speed sweep locating arm B's near-zero band | **run on CPU, and it fails**: reference speed does not grade difficulty at all — flat across a fourfold range, because faster bodies penetrate further per step but spend fewer steps in contact |
| 4 | Gate statistics across all five conditions | **met** |
| 5 | Oracle clears 80% | **met** — D\* landed in every cell of every condition |
| 6 | `normal_alignment` under real contact | pending Branch B |

## What this is not

Fifty cells at one speed with a coupling injected through the target command
rather than emerging from contact. Nothing here is a confirmatory estimate, and
the arm comparison in particular is currently measuring a task that arm B
already solves.

## Reproduce

```bash
for c in coupled drift static noise slide; do
  for s in $(seq 300 309); do
    SEED=$s CONDITION=$c OUT_DIR=results/paper003_probe_sweep \
      bash scripts/run_paper003_pilot.sh
  done
done
```

Records were written on the pod and not pushed — the sweep must be regenerated
after the eligibility fix in any case, since that changes which cells count as
measurements.
