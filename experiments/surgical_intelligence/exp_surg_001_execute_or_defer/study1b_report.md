# EXP-SURG-001B Report — Timing / recoverability curve (Fig 5)

> **Mode:** `isaac` · scripted IK-Rel · **Date:** 2026-07-16  
> Smoke: 3 episodes × 5 branches = 15 rollouts · shift +0.03 m @ onset 20 · tol 0.02 m

## Question

After a target shift at onset, does **delaying REPLAN** (t+0 / +5 / +10 / +20) change successful resolution?

## Isaac results

| Branch | Success | Unsafe | Mean dist (m) | Mean steps |
| --- | ---: | ---: | ---: | ---: |
| CONTINUE | **0 / 3** | 0 | 0.2170 | 160.0 |
| REPLAN_d0 | **3 / 3** | 0 | 0.0189 | 86.0 |
| REPLAN_d5 | **3 / 3** | 0 | 0.0195 | 87.0 |
| REPLAN_d10 | **3 / 3** | 0 | 0.0196 | 96.7 |
| REPLAN_d20 | **3 / 3** | 0 | 0.0190 | 90.0 |

### Reading

- **CONTINUE ≪ any REPLAN** — same as 001A: frozen target leaves ~3 cm residual (or worse on ep0).
- **Within +0…+20 steps, no recoverability cliff** for this mild 3 cm shift + scripted proposer: all delayed REPLANs succeed.
- Fig 5 smoke therefore shows a **flat high recoverability band** for REPLAN delays, not a sharp golden-time drop. That is still useful: it bounds *when* delay starts to matter for this severity.
- **Not claim-ready** for Paper 1 alone: n=3, one severity, scripted proposer, no camera reshape / handover.

### Implication for next smoke

To expose a timing curve (falling recoverability), harden the setting, e.g.:

1. Larger shift (e.g. 5–8 cm) and/or tighter horizon after late replan  
2. Delays out to +40 / +60  
3. Stronger forbidden region / path blocking after lingering on frozen target  
4. Or keep mild shift and treat “flat band” as the empirical finding for P2@3cm

## Artifacts

- RunPod: `artifacts/study1b_timing_curve/isaac_results.json`
- Committed: `results/study1b_isaac/isaac_aggregate.json` · figures · `tables/timing_curve.csv`

```bash
python scripts/plot_study1b_timing_curve.py \
  --results experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1b_isaac/isaac_aggregate.json
```

## Next

1. RunPod Stopped (volume keeps raw JSON).  
2. Fig 4/5 captions frozen: [`fig_captions.md`](../../../docs/paper1/fig_captions.md).  
3. Fig 4/5 captions frozen: [`fig_captions.md`](../../../docs/paper1/fig_captions.md).
