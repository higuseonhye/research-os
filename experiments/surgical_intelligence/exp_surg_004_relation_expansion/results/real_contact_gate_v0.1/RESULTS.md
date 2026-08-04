# Real contact and the relation gate — first measurement

> **Engineering calibration. Excluded from confirmatory evidence.**
> Ten traces, one scene, a single-body probe. No arms were scored.
> Supersedes the conclusion in [the sliding problem note](../../../../../docs/paper003/paper003_sliding_problem_v0.1.md).

## Provenance

- 2026-08-04 on A100-SXM4-80GB, `Isaac-Lift-Block-PSM-IK-Rel-Play-v0`
- `scripts/orbit_lift_stopping_probe.py`, gripper closed, contact radius 12 mm
- Analysis: `scripts/paper003_gate_on_traces.py`, the real gate at every prefix

## The gate fires on real contact

| v (mm/step) | Seed | Retention | Coast | Contrast | `cv_gain` | Fired |
| ---: | ---: | ---: | ---: | ---: | ---: | :---: |
| 40 | 300 | 0.54 | 26.6 mm | 0.814 | −0.363 | yes |
| 40 | 301 | 0.77 | 20.8 mm | 0.507 | −0.627 | yes |
| 40 | 302 | 0.76 | 10.5 mm | 0.904 | −0.752 | yes |
| 40 | 303 | 0.80 | 11.7 mm | 0.838 | −0.606 | yes |
| 40 | 304 | — | 0.0 mm | 1.000 | −0.487 | no |
| 50 | 300 | — | 0.0 mm | 1.000 | −0.275 | no |
| 50 | 301 | 0.73 | 23.1 mm | 0.704 | −0.531 | yes |
| 50 | 302 | — | 0.0 mm | −0.369 | −0.201 | no |
| 50 | 303 | 0.72 | 26.1 mm | 0.581 | −0.420 | yes |
| 50 | 304 | 0.78 | 22.8 mm | 0.719 | −0.602 | yes |

Marginal per-trial rate **0.80** at 40 mm/step and **0.60** at 50 mm/step.

**Every trace containing a measured strike fired; every trace that did not fire
lacks one.** The three failures are exactly the rows with no retention and zero
coast — the probe produced no usable strike there, which is an engineering
matter rather than a property of the gate. Conditional on a strike, the rate is
**7 of 7**.

**`cv_gain` is negative in every trace**, from −0.20 to −0.75. A constant-velocity
model is *worse than zero-order* on this motion, so the residual is not the one
Paper 002's operator handles. That is the discrimination the paper needs, and it
survives real contact.

Proximity contrast runs 0.50 to 0.90 where a strike occurred: the motion really
is proximity-conditioned.

## A conclusion this reverses

Earlier the same day, toy contact physics and a per-step **retention** statistic
led to the opposite reading — that a struck object slides, the gate declines,
and real contact puts the treatment condition in the `slide` control's regime.
The retention measured here, 0.72 to 0.80, is well above the 0.45 line that toy
model suggested.

**The retention proxy was wrong, and the gate says so.** Retention describes the
decay of one coast in isolation. The gate reads the whole episode, where the
target is still before contact, moves during it, and settles after — which is
proximity conditioning whatever the coast's decay rate looks like.

A single seed at 0.38 briefly made the proxy look workable; replication put
retention at 0.72 to 0.80 and would have made it look fatal. Neither reading was
the gate's. The lesson is the same one twice in a day: a proxy built to stand in
for a measurement should not be believed once the measurement is available.

## What this does not establish

- **No arms were scored.** This is a probe, not a cell: nothing here says
  whether arm D beats arm B under real contact.
- **A single body.** The two-body encounter — one body demonstrating the
  relation, another applying it — has not been run in this scene.
- **Ten traces, one object, one table.** Coast distances of 10 to 27 mm against
  a 20 mm tolerance mean displacement sits right at the criterion, so the
  capability threshold is neither established nor excluded.
- **H3's 0.90 is not met marginally** (0.60–0.80). Whether the conditional 7/7
  is the right reading depends on making the strike reliable, which is
  unfinished work rather than an interpretive choice.

## Next

1. Make the strike reliable — 3 of 10 traces produced none.
2. Port the two-body encounter to this scene: `robot`, `ee_frame`, `object_pose`,
   and a target that is read rather than written.
3. Then score the arms, and only then ask whether H1's threshold exists.
