"""Did the scene produce a capture, a collision, or nothing?

The first question the Isaac calibration pilot has to answer, and the one that
could end the design. Every Paper 003 result so far is arithmetic: the cell
computes the target's motion from a formula and writes it into the simulator's
command. Under `ContactWorld` the cell commands the bodies, steps physics, and
*reads* where the object went - and what the physics does there is not something
the runner may assume.

The verdict is decided with the **same statistics the gate and arm D use**, not
with a separate rule invented for the pilot. If a trace is a capture by this
measure, it is a capture by the measure the arms will be scored through; if the
two could disagree, the pilot would be certifying something other than what the
paper runs on.

Three outcomes, and the middle one is the interesting failure:

    capture     still, then rides a body, and the effect exceeds tolerance
    collision   moves on contact but does not ride - the relation is real and
                the displacement self-limits, which is the ceiling that made
                collision unusable in the first place
    none        never moved enough to tell
"""

from __future__ import annotations

from typing import Any

import numpy as np

from .relation_dynamics import carriage_evidence, estimate_capture


def capture_verdict(
    record: dict[str, Any],
    tolerance: float = 0.020,
    dispense_latency: int = 6,
    min_still_steps: int = 3,
    still_fraction: float = 0.25,
    interaction_radius: float | None = None,
) -> dict[str, Any]:
    """Classify one cell record. Diagnostic only - nothing gates on it.

    The stillness test is **an observable still period before the first
    motion**, not a small displacement before the carry. Two things forced that,
    and both were caught by tests before this was pointed at an Isaac trace:

    `estimate_capture.onset` is the start of the first sustained *run*, not the
    first ride - deliberately, since a struck target rides for one step at its
    equilibrium separation. When a burst pause falls just after the capture the
    run starts a step or two late, and measuring travel before it charged a real
    capture with 15 mm of motion it had made while already held.

    And a target that moves from the very first step has no still period at all
    while trivially having zero travel "before" its onset. That is `drift`, which
    agrees with its body on 0.73 of moving steps and was certified as a capture
    by the earlier rule - the single most dangerous misreading available here.

    `min_still_steps` mirrors `min_ride_steps`: the same number of consecutive
    observations that establishes a carry establishes stillness.
    """

    observations = record.get("observations") or []
    if len(observations) < 2:
        return {"verdict": "none", "reason": "fewer than two observations"}

    targets = np.asarray([o["target"] for o in observations], dtype=np.float64)
    bodies = np.asarray([o["references"] for o in observations], dtype=np.float64)

    steps = np.linalg.norm(np.diff(targets, axis=0), axis=1)
    if float(np.max(steps)) <= 0.0:
        return {"verdict": "none", "reason": "the target never moved"}

    # **With the radius, the same way the gate calls it.**
    #
    # This called it without, and the two then disagreed about what a carry is.
    # `_ride_mask` compares per-step displacement vectors and tolerates 25% of
    # the target's own step - about 0.75 mm at this speed - so sixty steps of
    # near-agreement integrate into forty-five millimetres of drift while
    # scoring 0.98 over a run of 111. Measured in the pilot, objects verdicted
    # as carried had drifted to median separations of 3, 50, 63, 55 and 178 mm
    # from the arm that was supposedly holding them.
    #
    # Carrying is a statement about relative position being *maintained*, and
    # per-step agreement is a local proxy that does not imply it. The gate was
    # already checking the accumulated quantity through its contact
    # requirement, and was refusing these cells correctly while this function
    # certified them.
    #
    # No new threshold: the bound is the measured capture radius the gate
    # already uses. What this restores is the property the verdict was trusted
    # for - that a trace it certifies is a capture by the measure the arms are
    # scored through.
    agreement, run = carriage_evidence(
        targets, bodies, interaction_radius=interaction_radius
    )
    estimate = estimate_capture(targets, bodies, interaction_radius=interaction_radius)

    out: dict[str, Any] = {
        "carriage_agreement": float(agreement),
        "carriage_run": int(run),
        "total_travel": float(np.linalg.norm(targets[-1] - targets[0])),
    }

    if estimate is None:
        # Moved, but never rode. Distinguish "struck" from "noise" by whether
        # anything came close enough to have done it.
        separations = np.linalg.norm(bodies - targets[:, None, :], axis=2).min(axis=1)
        out.update(
            verdict="collision" if float(np.min(separations)) < tolerance else "none",
            reason="no run of carriage steps; the target moved without riding",
            closest_approach=float(np.min(separations)),
        )
        return out

    # When the target first moved, judged against the **tolerance** rather than
    # against the largest step in the trace.
    #
    # A relative screen hides exactly the case that matters. A target drifting
    # at 2.5 mm/step sits under a quarter of a 15 mm/step carry and reads as
    # still, while covering 15 mm over the dispense window - most of the 20 mm
    # a placement is allowed. Its history is informative, which is precisely
    # what disqualifies a trace from being a capture.
    #
    # So: still means the motion would keep a placement well inside tolerance
    # over one dispense window, the same form `motion_expected` uses.
    floor = still_fraction * tolerance / max(dispense_latency, 1)
    moved = np.flatnonzero(steps > floor)
    first_motion = int(moved[0]) if moved.size else len(steps)
    after = float(np.linalg.norm(targets[-1] - targets[first_motion]))

    out.update(
        onset=int(estimate.onset),
        first_motion=first_motion,
        still_steps=first_motion,
        carrier=int(estimate.body),
        capture_radius=float(estimate.capture_radius),
        held_at_end=bool(estimate.held),
        travel_before_onset=float(np.linalg.norm(targets[first_motion] - targets[0])),
        travel_after_onset=after,
    )

    # Both properties capture was chosen for, checked separately so a failure
    # says which one failed.
    if not estimate.held:
        out.update(
            verdict="collision",
            reason=(
                "it was taken hold of and then lost - the carrier drifted away "
                "from it, or their motions came apart. A carry keeps its "
                "distance, and agreeing step by step does not imply that"
            ),
        )
    elif first_motion < min_still_steps:
        out.update(
            verdict="collision",
            reason=(
                f"the target was still for only {first_motion} step(s) before it "
                f"began moving, against {min_still_steps} required. It has a "
                "history of its own from the start, which is the carriage "
                "failure - a single-entity model has something to learn from it"
            ),
        )
    elif after <= tolerance:
        out.update(
            verdict="collision",
            reason=(
                f"rode, but only {1000 * after:.1f} mm against a "
                f"{1000 * tolerance:.1f} mm tolerance - the effect does not "
                "clear the placement criterion"
            ),
        )
    else:
        out.update(verdict="capture", reason="still before the arrival, then rode")
    return out
