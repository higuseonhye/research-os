# Paper 003 figures

```bash
python scripts/plot_paper003_negative.py
```

| File | Content |
| --- | --- |
| `fig1_carrier_cannot_stop.png` | The mechanism: settling time against grip duration and duty-cycle period |
| `fig2_arm_scores.png` | Every arm, injected coupling and three physical configurations |
| `fig3_discordant_pairs.png` | Paired cells won by exactly one of arm D and SELF, CPU against physical |
| `fig4_settling_sweep.png` | The criterion measured: settling swept under injected coupling |

## Where the numbers come from

**fig4 and fig2's CPU column are computed** from
`results/settling_sweep_v1.0/burst_off_4.json`, produced by
`scripts/paper003_settling_sweep.py` in this repository. Re-running the sweep
regenerates them.

**Everything physical is transcribed** from
[`results/physical_h2_v1.0/RESULTS.md`](../../../experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/physical_h2_v1.0/RESULTS.md).
The Isaac records were written on a rented pod and are not in this repository —
their summaries are. Because transcribed constants go stale:

```bash
python scripts/plot_paper003_negative.py --check
```

re-reads that file and reports whether every transcribed number still matches the
source line it came from.

## Two things these figures deliberately do not do

**No smooth densities.** Distributions are drawn as the order statistics that
were actually measured — median, p10, p90, max. A kernel through four numbers
would be a curve we never observed.

**fig2's CPU column is not assembled by hand.** An earlier version of it took arm
B and C from the by-offset arm sweep and arm D and SELF from the preregistered
SELF comparison — different seeds, different commit bands — and printed them as
one column. It now comes from the settling sweep's `settling 0` row, which scores
all four arms on one set of cells.

## What fig4 shows that the manuscript's first draft got wrong

The predicted crossing is marked on it, at the commanded pause of 4, labelled
**REFUTED** — because it was. The observed crossing is at the duty-cycle period
of 14. The figure keeps both so a reader can see which claim was tested and which
one survived.

Arm D's curve is the other half: it does **not** collapse. Settling explains the
mode operator's return and not the relational arm's physical failure.
