"""How long a struck object keeps moving, and what that costs the relation gate.

CPU only. This is the measurement everything in Paper 003 now waits on.

The gate requires motion to be *proximity-conditioned*: the target moves while a
body is near and stops when it leaves. A struck rigid body does not stop when
the body leaves - it slides, and a constant-velocity model explains the slide.
Driving the cell through toy contact physics found the gate firing on 0.00 of
steps at a friction coefficient of 0.15 or 0.35, and recovering only at 0.60,
where the object halts within a step or two.

So the question is not "does the gate work" but "how fast does this object
stop", and it is answered from a pose trace rather than argued. This module does
the arithmetic; the Isaac shell only records poses.

Nothing here decides anything about an arm. Stopping time is a property of the
object, the table and the strike.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class StoppingEstimate:
    """What a single strike revealed about how the object comes to rest."""

    contact_end: int
    """Last step at which a body was within the interaction radius."""
    steps_to_stop: int | None
    """Steps after `contact_end` until the object's speed falls below the floor.
    None if it never stopped within the trace, which is itself the answer."""
    retention: float | None
    """Per-step fraction of speed kept while coasting.

    0.0 is the injected coupling's regime - the object halts the instant contact
    ends - and every pilot so far has run there. Values near 1.0 are a free
    slide, which a constant-velocity model predicts outright.
    """
    peak_speed: float
    coast_distance: float
    """How far the object travelled after contact ended. Compared against the
    placement tolerance, this is what decides whether a commitment made before
    the strike can still be right."""

    def to_dict(self) -> dict:
        return {
            "contact_end": self.contact_end,
            "steps_to_stop": self.steps_to_stop,
            "retention": self.retention,
            "peak_speed": self.peak_speed,
            "coast_distance": self.coast_distance,
        }


def estimate_stopping(
    positions,
    separations,
    interaction_radius: float,
    speed_floor: float = 2e-4,
) -> StoppingEstimate | None:
    """Measure the coast after the last contact in a pose trace.

    `separations` is the distance to the nearest body at each step, so this does
    not need to know how many bodies there were or which one struck.

    Returns None when the trace contains no contact, or no motion, or when
    contact runs to the end and there is no coast to measure - all of which are
    "this trace cannot answer the question" rather than a stopping time of zero.
    """

    poses = np.asarray(positions, dtype=np.float64)
    gaps = np.asarray(separations, dtype=np.float64)
    if poses.ndim != 2 or len(poses) < 3 or len(gaps) != len(poses):
        return None
    if interaction_radius <= 0.0:
        raise ValueError("interaction_radius must be > 0")
    if speed_floor <= 0.0:
        raise ValueError("speed_floor must be > 0")

    in_contact = gaps < interaction_radius
    if not in_contact.any():
        return None
    contact_end = int(np.max(np.flatnonzero(in_contact)))
    if contact_end >= len(poses) - 2:
        return None  # contact ran to the end; nothing to observe afterwards

    speeds = np.linalg.norm(np.diff(poses, axis=0), axis=1)
    peak = float(np.max(speeds)) if speeds.size else 0.0
    if peak <= speed_floor:
        return None  # the strike never moved it; not a measurement of stopping

    coasting = speeds[contact_end:]
    moving = np.flatnonzero(coasting >= speed_floor)
    if moving.size == 0:
        steps_to_stop: int | None = 0
    else:
        last = int(moving[-1])
        steps_to_stop = None if last == len(coasting) - 1 else last + 1

    # Retention from the coast's own decay, fitted only on steps that are
    # actually moving: log-linear, because a constant fraction lost per step is
    # what a viscous or Coulomb drag looks like over a few steps.
    retention: float | None = None
    usable = coasting[coasting >= speed_floor]
    if usable.size >= 3:
        ratios = usable[1:] / usable[:-1]
        finite = ratios[np.isfinite(ratios) & (ratios > 0.0)]
        if finite.size:
            retention = float(np.clip(np.exp(np.mean(np.log(finite))), 0.0, 1.0))
    elif steps_to_stop == 0:
        retention = 0.0

    coast = float(np.linalg.norm(poses[-1] - poses[contact_end]))
    if steps_to_stop is not None:
        end = min(contact_end + steps_to_stop, len(poses) - 1)
        coast = float(np.linalg.norm(poses[end] - poses[contact_end]))

    return StoppingEstimate(
        contact_end=contact_end,
        steps_to_stop=steps_to_stop,
        retention=retention,
        peak_speed=peak,
        coast_distance=coast,
    )


#: Retention above which the toy sweep found the relation gate silent. At 0.65
#: (friction 0.35) and 0.85 (friction 0.15) it fired on 0.00 of steps; at 0.40
#: (friction 0.60) it recovered to 0.31. The boundary is not sharp and this is a
#: single toy model, so it is a threshold for *reporting a concern*, not a
#: decision rule.
GATE_VIABLE_RETENTION = 0.45


def gate_outlook(estimate: StoppingEstimate | None, dispense_latency: int = 6) -> str:
    """A one-line reading of what a stopping estimate implies for the gate.

    Deliberately coarse and deliberately not a pass/fail: one toy friction model
    and one strike do not settle a design. It exists so a run reports its own
    implication instead of leaving a number to be interpreted later, when the
    interpretation could be chosen.
    """

    if estimate is None:
        return "no usable strike in this trace"
    if estimate.steps_to_stop is None:
        return "object never stopped within the trace - the slide regime outright"
    if estimate.steps_to_stop <= 1:
        return "stops within a step - the regime the injected pilots assumed"
    if estimate.retention is not None and estimate.retention > GATE_VIABLE_RETENTION:
        return (
            f"coasts {estimate.steps_to_stop} steps at retention "
            f"{estimate.retention:.2f} - constant velocity explains this, "
            "and the gate is expected to decline"
        )
    if estimate.steps_to_stop >= dispense_latency:
        return "coast outlasts the dispense window - a commitment cannot anticipate it"
    return f"stops in {estimate.steps_to_stop} steps - borderline, measure more strikes"
