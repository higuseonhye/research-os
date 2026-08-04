# Paper 003 — capture calibration pilot runbook v0.1

> **Never run.** Written 2026-08-04 on a machine with no GPU, so everything here
> is verified only as far as CPU and a compile check reach. Expect iteration at
> stage 1.
>
> **This is the run that could end the design**, and that is not a figure of
> speech. Every Paper 003 result so far is arithmetic: the cell computes the
> block's motion from a formula and writes it into the simulator's command.
> Nothing yet shows that the lift scene produces a **capture** rather than a
> collision. [Preregistration](paper003_prereg_v1.0.md), *What the calibration
> pilot must produce*.

## The mechanism, and where it came from

A capture needs the target **perfectly still** before the arrival — if it drifts,
its own history carries information and the single-entity arm has something to
learn from, which is the failure that killed carriage.

The device is already in the record, as a failure note from the stopping probe:

> an open gripper straddles the block — the frame point reached 0.3 mm from its
> centre without moving it.

For a push probe that was useless. For capture it is exactly right. So:

```text
gripper OPEN, approach        block perfectly still, jaws straddling it
gripper CLOSES on arrival     takes hold at the observed separation
gripper CLOSED, burst motion  the block rides
```

`--grasp` schedules that on the **observed** separation rather than on a step
count, so the block is taken hold of when the arm actually reaches it, not when
the script says it should have. `--grasp-radius` is the physical capture radius;
arm D does not receive it and estimates it from the observed onset.

---

## Stage 0 — workspace

Same VESSL workspace and Isaac image as Paper 002; see the
[Paper 002 runbook](../paper002/vessl_runbook_v0.1.md) for creation. Then:

```bash
cd /workspace/research-os && git pull
```

Nothing here needs a rebuild — the changes are Python and shell.

## Stage 1 — does the scene produce a capture at all?

One cell. This is the gate on everything after it.

```bash
bash scripts/run_paper003_capture_pilot.sh
```

Read `CAPTURE VERDICT` in the printed output.

| Verdict | Meaning | What to do |
| --- | --- | --- |
| **`CAPTURE`** | Still, then rode, and the effect clears 20 mm | Go to stage 2 |
| `COLLISION` | The block moved but did not ride, or rode too little, or was never still | See the decision table below |
| `NONE` | The block never moved | The arm did not reach it — check `ARM LAGGING` first |

The verdict is computed with **the same statistics the gate and arm D use**
(`carriage_evidence`, `estimate_capture`), not a rule invented for the pilot. If
a trace is a capture by this measure it is a capture by the measure the arms are
scored through.

### If it is not a capture

| Reason in the verdict | Likely cause | First thing to try |
| --- | --- | --- |
| "still for only N steps" | The block is being nudged during the approach — the jaws are not straddling it | `--grasp-radius` smaller, or aim so the gap rather than a jaw meets it |
| "rode, but only X mm" | The gripper closed but lost the block, or the burst is too short | Check `held_at_end` in the JSON; raise `--burst-on` or `--episode-steps` |
| "no run of carriage steps" | The close did not take hold at all | Check `grasp.closed_at` is not null; try `--gripper-close` sign flipped |
| `ARM LAGGING` present | The arm cannot follow the script, so the geometry is wrong | Lower `--script-speed` or raise `--approach-speed` **before** anything else |

**Do not raise the tolerance, widen the commit window, or lower
`min_carriage_run` to obtain a capture.** Those are on the preregistration's
list of tuning that will not be done, and a capture obtained that way is not one.

## Stage 2 — engagement, which sets the confirmatory `n`

```bash
SEEDS=40 bash scripts/run_paper003_capture_pilot.sh
```

Read `SUMMARY.txt`:

- **capture / collision / none counts.** A mixed population is a finding, not a
  nuisance: cells that are not captures must not be pooled with cells that are.
- **engagement** — the fraction of cells where arm D acted. This is the number
  the sizing rule reads, and it must come from here rather than from the
  injected-coupling runs, where it is 0.23.

Then read `n` off the table in the
[preregistration](paper003_prereg_v1.0.md), *Sample size*, and record it there
with this engagement figure beside it.

## Stage 3 — the controls

H3 needs the gate to fire on ≥ 0.90 of coupled trials and ≤ 0.10 of each
control; H4 needs arm D not to regress on any of them.

```bash
for c in static noise drift slide; do
  CONDITION=$c SEEDS=20 bash scripts/run_paper003_capture_pilot.sh
done
```

The one to watch is **`slide`** — a struck block that keeps its velocity is the
case that would collapse Paper 003 into Paper 002, and the gate leaked on it at
14–19% in the near-frictionless limit on CPU. Under real contact the friction is
whatever the scene's friction is, which is the point of measuring it here.

Also read `gate_evidence` per observation. A capture cell that fires through
`proximity` rather than `carriage` is not firing for the reason the design says
it should.

## Stage 4 — bring it back

```bash
# from the laptop
bash scripts/copy_exp_surg_003_from_vessl.sh   # adapt the paths for this run
```

Record under
`experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/`
with a `RESULTS.md` that states, in this order: the capture verdict distribution,
engagement, `normal_alignment`, and the observation noise. Those are the four
things the preregistration is waiting on.

---

## What this pilot is not

It is **not** the confirmatory sample and no cell from it may be pooled into
one. `n` is fixed from this pilot's engagement figure and the confirmatory cells
are run afterwards, on fresh seeds, against the frozen preregistration.

It is also not a test of the arms. If stage 1 says the scene produces a
collision, the honest outcome is that the capture relation is not available in
this scene — which is a result, and one the collision and carriage records
already give the map for.
