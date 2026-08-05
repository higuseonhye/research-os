# Everything re-derived at the latency the physics fixed

> **CPU, 2026-08-05.** Supersedes every CPU number derived at
> `dispense_latency` 6. Those were not wrong when taken; they described a task
> the physical scene cannot pose, since the block carries at 2.86 mm/step and
> six steps leave it inside a 20 mm tolerance.
>
> Confirmatory for the arm comparison only, and CPU-calibration for the rest.

## Why everything moved

One measurement propagated through the whole design:

```text
carry speed 2.86 mm/step (p10, 24 Isaac capture cells)
  -> dispense_latency = ceil(20/2.86) = 8
  -> commit window +-8 instead of +-6
  -> cv_gain found to depend on the horizon, and replaced
  -> its threshold could not be re-derived: no plateau exists
  -> the collapse defence moved from the gate to H2
  -> carriage evidence now requires contact, which is what rejects drift
```

Each step has its grounds written before the measurement that tested it.

## 1. The arms, at latency 8

40 seeds per case.

| Case | B | C | **D** | D acted |
| --- | ---: | ---: | ---: | ---: |
| capture / burst / 1 body | 0.05 | 0.15 | **0.28** | 0.30 |
| capture / probe / 1 body | 0.10 | 0.03 | **0.20** | 0.88 |
| collision / probe / 1 body | 0.82 | 0.75 | **0.85** | 0.68 |
| collision / probe / 2 bodies | 0.88 | 0.00 | **0.97** | 1.00 |
| slide (control) | 0.00 | 0.85 | **0.00** | 0.00 |
| drift (control) | 0.00 | 1.00 | **0.00** | 0.00 |
| static (control) | 1.00 | 1.00 | 1.00 | 0.00 |
| noise (control) | 0.62 | 0.03 | 0.62 | 0.00 |

Every control behaves as it must: the relational arm declines outright on
`slide` and `drift`, falls back to arm B on `noise`, and is trivially right on
`static`.

## 2. The gate, after the clause moved

20 seeds per case, fraction of cells where it fires at all.

| Case | | fires |
| --- | --- | ---: |
| capture / burst | must fire | **1.00** |
| collision / probe | must fire | **1.00** |
| drift | must refuse | **0.00** |
| static | must refuse | **0.00** |
| noise | must refuse | **0.00** |
| slide | H3 ceiling 0.10 | **0.05** |
| steady push | H2's case now | 1.00 |

`slide` stays under H3's preregistered ceiling, so no control set had to move.
The sustained push fires, deliberately: a relation *is* present there and the
question of whether a simpler operator suffices is H2's, tested on outcomes.

## 3. The SELF comparison — Case A again, on better evidence

Amendment recorded before the run. Band [+4, +8], measured on seeds 2000–2119;
comparison on seeds from 3000. Rule otherwise unchanged: the arm, its ungated
asymmetry, α = 0.05, margin 0.15, n = 200, the test.

| | |
| --- | ---: |
| `p_D` | **0.735** |
| `p_SELF` | **0.045** |
| arm C | 0.145 |
| arm B | 0.000 |
| Discordant: D only / SELF only | **146 / 8** |
| One-sided exact McNemar | p = 3.0 × 10⁻³⁴ |
| Margin | **+0.690** |

**Stronger than the first Case A, not a repeat of it.** There SELF scored 0.000
and took no discordant pair, which needed a separate argument that the
competitor was not simply broken. Here it scores 0.045 and takes 8 pairs — it
can win, and still loses 146 to 8.

## 4. The bound, unchanged at +30

400 fresh seeds from 4000. The single-entity arm catches up from offset **+30**,
about two burst cycles, exactly as at latency 6.

The shape differs. At latency 8 arm D reaches 1.00 from +24, and at +30 both
arms are at 1.00 — so they become indistinguishable because the task is trivial
that far out, not because SELF overtakes. The protocol band is [+4, +8], well
inside it either way.

## What this cost

| | |
| --- | --- |
| `coupled` two-body cells resolving | 1.00 → **0.83** |
| everything else (9 combinations) | 1.00, unchanged |

At the longer horizon the pattern estimator needs more history before it can
project, and the two-body encounter switches its acting body mid-approach.
Recorded rather than tuned away: every `pusher_start_step` from 4 to 16 gives
the same rate, and the two-body encounter is retired for capture in any case.

## What is still open

Everything the Isaac pilot owes the preregistration except the first item:
capture *does* happen under real contact, and 24 of 24 cells produced one. Still
unmeasured, because they need the pilot re-run at this latency and gate:
engagement under contact jitter — which sets the confirmatory `n` —
`normal_alignment`, and the observation noise.

## Provenance

- `scripts/paper003_capture_arms.py --seeds 40`
- `scripts/paper003_self_arm.py`, band and seeds per the amendment in
  [the rule](../../../../../docs/paper003/paper003_self_arm_prereg_v1.0.md)
- `scripts/paper003_self_arm_bound.py --seeds 400`
- Grounds: [the derivation](../../../../../docs/paper003/paper003_derived_from_physics_v0.1.md) ·
  [the horizon defect](../../../../../docs/paper003/paper003_cv_gain_horizon_v0.1.md) ·
  [where collapse is defended](../../../../../docs/paper003/paper003_where_collapse_is_defended_v0.1.md)
