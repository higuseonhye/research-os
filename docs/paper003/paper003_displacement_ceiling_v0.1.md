# One contact cannot displace the target past its own tolerance

> **Structural finding, 2026-08-04.** Reached from five independent directions
> over one day, and it decides what Paper 003 can claim.

## The measurement

A coherent encounter, expressed in radii so it scales with the scene: the first
body advances to penetrate, withdraws clear, and stops; the second is launched
once at the object and travels four radii, passing through. Both bodies contact
in **every** seed and the target settles afterwards.

| Script speed | Gain | Body 1 hits | Body 2 hits | Window displacement | Over 20 mm | Settles |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4 mm/step | 0.5 | 1.00 | 1.00 | 11.4 mm | **0.00** | 1.00 |
| 6 mm/step | 0.5 | 1.00 | 1.00 | 14.9 mm | **0.00** | 1.00 |
| 8 mm/step | 0.9 | 1.00 | 1.00 | 16.0 mm | **0.00** | 1.00 |
| 10 mm/step | 0.9 | 1.00 | 1.00 | 16.0 mm | **0.00** | 1.00 |

Displacement over the dispense window never clears the 20 mm tolerance, at any
speed or coupling strength tried.

## The same wall, five times

| Where | Displacement | Tolerance |
| --- | ---: | ---: |
| Injected coupling, 50 mm radius, speeds 4–80 mm/step | ~15 mm | 20 mm |
| Injected coupling, gains 0.3–0.95 | 10.5–17.2 mm | 20 mm |
| Two-body encounter on the CPU proxy | 15.6–17.3 mm | 20 mm |
| Real contact in the lift scene, coast after a strike | 10.5–26.6 mm | 20 mm |
| This encounter, 12 mm radius, speeds 4–10 mm/step | 8–17 mm | 20 mm |

Every route arrives within a few millimetres of the same number, and it sits
just below the criterion.

## Why it is bounded

Three constraints multiply out to a ceiling, and none of them is a parameter
that can be relaxed without giving something else up.

**The target cannot be pushed faster than the body pushing it.** So displacement
over a window is at most the body's speed times the window.

**The body's speed is capped by observability.** A body travelling further per
step than the interaction radius crosses the contact zone between observations,
so nothing sees the contact. That is already enforced.

**Contact is self-limiting.** The push moves the target away, which reduces
penetration, which reduces the push. The target escapes after roughly one radius
of travel, and a body that keeps up instead becomes a bulldozer — measured, a
pusher that never stops shoves the target 111 mm and the residual becomes
constant-velocity, which is arm C's case, not arm D's.

So displacement per contact is on the order of the interaction radius, and the
radius here is 12 mm against a 20 mm tolerance. Raising the radius above the
tolerance would mean declaring contact at distances the scene's geometry does
not support — real contact in this scene happens at 2 to 5 mm.

## What this means for H1

The capability-crossing endpoint requires `success(B)` in a near-zero band. Arm B
aims where the target is and fails only when the target moves further than the
tolerance during the dispense. **One contact does not move it that far.**

So H1 is not reachable in this task family from a single contact, and this is a
property of the mechanism rather than of a parameter that was not tuned hard
enough.

Three honest routes remain, and the choice between them is the researcher's:

1. **Accumulate contacts.** Several strikes inside one window would clear the
   tolerance — but a sustained push is what a constant-velocity model explains,
   so the residual moves into arm C's regime and the paper loses its
   discrimination. Measured directly: the bulldozer case.
2. **Change the endpoint.** Drop capability crossing for a statement the
   evidence supports: the relational operator predicts a displacement that
   neither zero-order nor constant-velocity does, at a magnitude below the task
   tolerance. Weaker, and true.
3. **Report the ceiling as the finding.** That a prepared relational operator
   cannot cross a capability threshold in this family because contact is
   self-limiting is itself a result, and it is preregisterable, testable, and
   informative about when relation-level expansion pays.

**None may be chosen by which arm it favours.** Route 1 is already measured to
fail on its own terms, which leaves 2 and 3 as genuine alternatives.

## What is not in doubt

The gate works. On real contact traces it fires on every trace containing a
strike, with the constant-velocity clause comfortably satisfied — `cv_gain`
between −0.20 and −0.75, meaning a constant-velocity model is *worse* than
zero-order on this motion. The discrimination Paper 003 rests on survives real
physics. What does not survive is the *endpoint* built on top of it.
