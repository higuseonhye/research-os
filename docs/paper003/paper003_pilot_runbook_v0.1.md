# Paper 003 — calibration pilot runbook v0.1

> **The runner has never been executed.** `scripts/orbit_reach_relation_pilot.py`
> was written without a GPU or Isaac Lab available, so no Isaac-facing line in it
> has run. It passes a syntax check and its pure schedule function is tested;
> everything touching the simulator is unverified. Budget for iteration.
>
> **This is an engineering calibration pilot, excluded from every confirmatory
> estimate** — the same posture as Paper 002's `isaac_model_order_pilot_v0.3`.
> It cannot support a claim. See the [draft preregistration](paper003_prereg_draft_v0.1.md).

---

## What the pilot has to produce

Nothing here tests the hypothesis. The pilot exists to turn six guessed
parameters into measured ones so the preregistration can be frozen honestly.

| # | Output | Feeds |
| --- | --- | --- |
| 1 | The environment runs end to end, one process per cell | go/no-go |
| 2 | Observation noise and timing irregularity under real physics | prereg §1–2 |
| 3 | Speed sweep locating where arm B enters the near-zero band | variant set `T`, §3–4 |
| 4 | Gate statistics on coupled / drift / static / noise | prereg §6 |
| 5 | Oracle arm clears 80%, i.e. the task is solvable at all | diagnostic gate |

---

## Order of operations

Do not skip to a sweep. Each step below exists because the one before it can
fail in a way that makes the next meaningless.

### 1. Smoke — one cell, read the output by eye

```bash
cd /workspace/research-os && git pull origin master
python scripts/orbit_reach_relation_pilot.py \
  --seed 300 --condition coupled --max-cells 1 \
  --out-dir results/paper003_pilot_smoke
```

Check in the written JSON:

- `committed_at` is not `null` — if it is, the eligibility screen never opened
  and the geometry is wrong, not the science.
- `resolved` contains all five arms.
- `valid` is `true`.
- `observations` show the target actually moving while the reference is near,
  and not moving while it is far.

**If `committed_at` is null**, the likely causes in order: the reference never
reaches the interaction radius (raise `--reference-speed` or lower
`--interaction-radius`), the episode is too short (`--episode-steps`), or the
command frame differs from what the script assumes.

### 2. Sanity — the controls must behave differently from the treatment

```bash
for c in coupled drift static noise; do
  python scripts/orbit_reach_relation_pilot.py \
    --seed 300 --condition $c --out-dir results/paper003_pilot_controls
done
```

The `drift` condition is the important one: the target moves, but not because
of the reference. If the relation gate fires there, arm C already explains the
evidence and the paper has no contribution — see H3 in the draft.

### 3. Measure noise and irregularity

Repeat the coupled condition across seeds and extract, from `observations`:

- the residual of the observed reference position against its fitted burst
  schedule → **observation noise**;
- the spread of realised burst and pause lengths → **timing jitter**.

These two numbers are the pilot's main deliverable. The CPU proxy currently
guesses them as abstract fractions of a step, which is not defensible.

### 4. Speed sweep

Vary `--reference-speed` and record per-arm success. Locate the speed at which
arm B enters the near-zero band; that region defines the confirmatory variant
set `T`.

### 5. Record and stop

Write results under `experiments/.../results/paper003_pilot_v0.1/` with a
`RESULTS.md` stating plainly that the run is a calibration pilot and excluded
from confirmatory estimates. Then freeze the preregistration — **before** any
confirmatory cell runs.

---

## Known limitations of this pilot runner

Stated now so they are not discovered as surprises:

- **The reference body is a moving point, not a rigid asset.** This pilot
  measures prediction, not contact dynamics. A second articulated body is
  deferred until the environment itself is trusted.
- **The coupling is applied to the target command**, following the pattern
  `orbit_reach_drift.py` uses for drift, rather than emerging from simulated
  contact. Real contact physics would change the measured jitter.
- **The robot's own reach is scripted and incidental** to the score. The arms
  are compared on predicted landing point, not on end-effector execution.
- **One commit per episode.** Multiple commits per episode would give more
  cells per unit of GPU time, and is worth adding once the single-commit path
  is trusted.

---

## Infrastructure

Same VESSL workspace and image as Paper 002 — see
[vessl_runbook_v0.1.md](../paper002/vessl_runbook_v0.1.md). Pause the workspace
when idle; this pilot does not need a long-lived session.

---

## Links

| Doc | Path |
| --- | --- |
| Draft preregistration | [paper003_prereg_draft_v0.1.md](paper003_prereg_draft_v0.1.md) |
| Commitment-point task and CPU design numbers | [paper003_commitment_task_v0.1.md](paper003_commitment_task_v0.1.md) |
| Episode driver (CPU-tested logic the runner delegates to) | [`scripts/wm_expansion/commitment_episode.py`](../../scripts/wm_expansion/commitment_episode.py) |
| Paper 002 VESSL runbook | [vessl_runbook_v0.1.md](../paper002/vessl_runbook_v0.1.md) |
