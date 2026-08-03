"""What breaks arm D when the contact is real, and how many cells that costs.

CPU only. Written 2026-08-04, before the real-contact Isaac run, to answer two
questions that would otherwise be answered by a surprise on the GPU.

**Why this exists.** Arm D fits a coupling that is *linear in separation*:

    |dtarget| = gain * (radius - d)

The pilot generated its data from exactly that law, so the pilot could not tell
whether arm D works or whether arm D was reading its own assumption back. Real
contact obeys no such law. Rather than discover that during a GPU session, this
generates data from contact laws the estimator does *not* assume and measures
what survives.

Two families are tried, and they fail differently:

  * **magnitude misspecification** - the push is along the contact normal, but
    scales with penetration as pen^p or saturates. The fitted coefficients are
    biased; the predicted *direction* stays right.
  * **direction misspecification** - friction adds a tangential component, so
    the target squirts sideways. The fitted coefficients stay right, because
    the estimator only ever fits magnitude against separation; the prediction
    goes the wrong way.

The second is the dangerous one, and it is not visible in any statistic the
runner currently records.

The second half sizes the confirmatory study as a function of the engagement
rate, because friction also *shortens* contact, and engagement - not accuracy -
is what caps arm D's marginal rate.

Usage:
    python scripts/paper003_contact_robustness.py
    python scripts/paper003_contact_robustness.py --noise 0.001 --seeds 16
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from math import comb
from typing import Callable

import numpy as np

from wm_expansion.relation_dynamics import (
    CouplingSpec,
    coupling_displacement,
    estimate_coupling,
)

# Matches the pilot's Isaac configuration so the numbers are comparable to
# results/isaac_relation_pilot_v0.1, not to a fresh set of made-up constants.
TRUE_RADIUS = 0.050
TRUE_GAIN = 0.50
REFERENCE_SPEED = 0.015
BURST_ON = 10
BURST_OFF = 4
HORIZON = 6  # dispense latency: the lead time a commitment actually needs
TOLERANCE = 0.020

ContactLaw = Callable[[np.ndarray, np.ndarray], np.ndarray]


# --------------------------------------------------------------------------
# Contact laws the estimator does not assume
# --------------------------------------------------------------------------


def _normal(target: np.ndarray, reference: np.ndarray) -> tuple[float, np.ndarray] | None:
    offset = target - reference
    distance = float(np.linalg.norm(offset))
    if distance >= TRUE_RADIUS or distance == 0.0:
        return None
    return (TRUE_RADIUS - distance) / TRUE_RADIUS, offset / distance


def linear_law(target: np.ndarray, reference: np.ndarray) -> np.ndarray:
    """The law arm D assumes. Included as the control, not as a result."""
    return coupling_displacement(
        target, reference, CouplingSpec(interaction_radius=TRUE_RADIUS, coupling_gain=TRUE_GAIN)
    )


def power_law(exponent: float) -> ContactLaw:
    """Penetration raised to a power. p=1.5 is Hertzian; p>2 is a very soft body."""

    def law(target: np.ndarray, reference: np.ndarray) -> np.ndarray:
        contact = _normal(target, reference)
        if contact is None:
            return np.zeros(3)
        penetration, direction = contact
        return TRUE_GAIN * (penetration**exponent) * TRUE_RADIUS * direction

    return law


def saturating_law(sharpness: float = 3.0) -> ContactLaw:
    """A stiff body: the push reaches its maximum almost as soon as contact starts."""

    def law(target: np.ndarray, reference: np.ndarray) -> np.ndarray:
        contact = _normal(target, reference)
        if contact is None:
            return np.zeros(3)
        penetration, direction = contact
        return TRUE_GAIN * float(np.tanh(sharpness * penetration)) * TRUE_RADIUS * direction

    return law


def frictional_law(mu: float) -> ContactLaw:
    """Push deviates from the contact normal by a tangential component.

    Magnitude is deliberately left unchanged, so this isolates direction error:
    anything the estimator gets wrong here is wrong despite recovering the true
    gain and radius.
    """

    def law(target: np.ndarray, reference: np.ndarray) -> np.ndarray:
        contact = _normal(target, reference)
        if contact is None:
            return np.zeros(3)
        penetration, direction = contact
        tangent = np.array([-direction[1], direction[0], 0.0])
        combined = direction + mu * tangent
        combined = combined / float(np.linalg.norm(combined))
        return TRUE_GAIN * penetration * TRUE_RADIUS * combined

    return law


# --------------------------------------------------------------------------
# Rollout and evaluation
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Rollout:
    truth: np.ndarray  # noiseless target positions - what a prediction is scored against
    targets: np.ndarray  # what the agent observes
    references: np.ndarray
    heading: np.ndarray


def rollout(law: ContactLaw, seed: int, azimuth: float, noise: float, steps: int = 60) -> Rollout:
    """Reference approaches along an arbitrary azimuth.

    Not head-on: a fixed +x approach makes the contact normal coincide with the
    reference's heading, which is exactly the degeneracy that hid a modelling
    error in the first pilot. Every azimuth here is a genuinely different
    encounter, not a translation of one.
    """

    rng = np.random.default_rng(seed)
    heading = np.array([np.cos(azimuth), np.sin(azimuth), 0.0])
    target = np.array([0.20, 0.0, 0.0])
    reference = target - 6.0 * TRUE_RADIUS * heading

    truth, observed_targets, observed_references = [], [], []
    for step in range(steps):
        if step % (BURST_ON + BURST_OFF) < BURST_ON:
            reference = reference + REFERENCE_SPEED * heading
        target = target + law(target, reference)
        truth.append(target.copy())
        observed_targets.append(target + rng.normal(0.0, noise, 3))
        observed_references.append(reference + rng.normal(0.0, noise, 3))
    return Rollout(
        np.array(truth), np.array(observed_targets), np.array(observed_references), heading
    )


@dataclass(frozen=True)
class LawResult:
    name: str
    fits: int
    attempts: int
    scored_steps: int
    mean_gain: float
    mean_radius: float
    median_error_d: float
    median_error_b: float

    @property
    def declined_rate(self) -> float:
        return 1.0 - self.fits / self.attempts if self.attempts else 0.0


def evaluate_law(name: str, law: ContactLaw, seeds: int, noise: float) -> LawResult:
    """Prediction error at the commitment horizon, scored only during contact.

    Scoring quiet steps would be self-flattering: with nothing moving, aiming at
    the current position is exactly right and every arm posts zero. A first
    version of this analysis did that by accident and reported 0.0 mm for laws
    that are plainly misspecified. Steps count only when contact is live *and*
    the target actually moves over the horizon.
    """

    errors_d: list[float] = []
    errors_b: list[float] = []
    gains: list[float] = []
    radii: list[float] = []

    for index in range(seeds):
        azimuth = 2.0 * np.pi * index / seeds
        run = rollout(law, seed=index, azimuth=azimuth, noise=noise)
        spec = estimate_coupling(run.targets, run.references, search_radius=3.0 * TRUE_RADIUS)
        if spec is None:
            continue  # the guard declined; that is a result, counted below
        gains.append(spec.coupling_gain)
        radii.append(spec.interaction_radius)

        for step in range(4, len(run.targets) - HORIZON):
            live = float(np.linalg.norm(run.truth[step] - run.references[step])) < 1.4 * TRUE_RADIUS
            moved = float(np.linalg.norm(run.truth[step + HORIZON] - run.truth[step])) > 0.002
            if not (live and moved):
                continue

            target = run.targets[step].copy()
            reference = run.references[step].copy()
            for ahead in range(1, HORIZON + 1):
                if (step + ahead) % (BURST_ON + BURST_OFF) < BURST_ON:
                    reference = reference + REFERENCE_SPEED * run.heading
                target = target + coupling_displacement(target, reference, spec)

            landing = run.truth[step + HORIZON]
            errors_d.append(float(np.linalg.norm(target - landing)))
            # Arm B has no relational model: it aims where the target is now.
            errors_b.append(float(np.linalg.norm(run.targets[step] - landing)))

    return LawResult(
        name=name,
        fits=len(gains),
        attempts=seeds,
        scored_steps=len(errors_d),
        mean_gain=float(np.mean(gains)) if gains else float("nan"),
        mean_radius=float(np.mean(radii)) if radii else float("nan"),
        median_error_d=float(np.median(errors_d)) if errors_d else float("nan"),
        median_error_b=float(np.median(errors_b)) if errors_b else float("nan"),
    )


# --------------------------------------------------------------------------
# Sample size as a function of engagement
# --------------------------------------------------------------------------


def sign_test_power(
    cells: int,
    engagement: float,
    land_d: float = 1.00,
    land_b: float = 0.80,
    trials: int = 4000,
    seed: int = 20260804,
) -> float:
    """Power of a one-sided paired sign test at a given engagement rate.

    Cells where arm D declines are identical to arm B by construction, so they
    are ties and contribute nothing. Engagement therefore does not merely dilute
    the effect - it sets the number of informative cells, which is why halving
    it costs far more than half the power.

    A sign test is used rather than the paired bootstrap because the bootstrap's
    lower bound is structurally non-negative here and "clears zero" is not a
    meaningful rejection. The two disagree materially - see the prereg - so which
    one is confirmatory has to be preregistered rather than picked afterwards.
    """

    rng = np.random.default_rng(seed)
    detected = 0
    for _ in range(trials):
        engaged = rng.random(cells) < engagement
        d = engaged & (rng.random(cells) < land_d)
        b = engaged & (rng.random(cells) < land_b)
        wins = int(np.count_nonzero(d & ~b))
        losses = int(np.count_nonzero(b & ~d))
        discordant = wins + losses
        if discordant == 0:
            continue
        p_value = sum(comb(discordant, k) for k in range(wins, discordant + 1)) / 2**discordant
        if p_value < 0.05:
            detected += 1
    return detected / trials


def required_cells(engagement: float, target_power: float = 0.90, cap: int = 400) -> int | None:
    """Smallest cell count on a coarse grid reaching `target_power`, or None."""

    for cells in range(20, cap + 1, 20):
        if sign_test_power(cells, engagement) >= target_power:
            return cells
    return None


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------


def render_laws(results: list[LawResult], noise: float) -> str:
    lines = [
        "Arm D under contact laws it does not assume",
        f"(observation noise {noise * 1000:.1f} mm, horizon {HORIZON} steps, "
        f"tolerance {TOLERANCE * 1000:.0f} mm)",
        "",
        f"{'true contact law':<26}{'fits':>6}{'steps':>7}{'gain':>7}{'radius':>8}"
        f"{'D err':>8}{'B err':>8}",
        "-" * 70,
    ]
    for result in results:
        if not result.fits:
            lines.append(f"{result.name:<26}{'0':>6}   estimator declined every seed")
            continue
        lines.append(
            f"{result.name:<26}{result.fits:>3}/{result.attempts:<2}{result.scored_steps:>7}"
            f"{result.mean_gain:>7.2f}{result.mean_radius:>8.3f}"
            f"{result.median_error_d * 1000:>8.1f}{result.median_error_b * 1000:>8.1f}"
        )
    lines += [
        "",
        f"true gain {TRUE_GAIN:.2f}, true radius {TRUE_RADIUS:.3f}; errors are median mm",
    ]
    return "\n".join(lines)


def render_power(engagements: list[float], sizes: list[int]) -> str:
    lines = [
        "Committed cells needed, against how often arm D engages",
        "(conditional rates held at the pilot's D 1.00 / B 0.80; one-sided sign test)",
        "",
        f"{'cells':>7}" + "".join(f"{f'eng {e:.2f}':>11}" for e in engagements),
        "-" * (7 + 11 * len(engagements)),
    ]
    for cells in sizes:
        lines.append(
            f"{cells:>7}" + "".join(f"{sign_test_power(cells, e):>11.2f}" for e in engagements)
        )
    lines += ["", f"{'for 0.90':>7}"]
    lines[-1] += "".join(
        f"{(str(required_cells(e)) or '>400'):>11}" for e in engagements
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=8, help="approach azimuths per law")
    parser.add_argument("--noise", type=float, default=0.0005, help="observation noise, metres")
    args = parser.parse_args()

    laws: list[tuple[str, ContactLaw]] = [
        ("linear (model is right)", linear_law),
        ("Hertzian  pen^1.5", power_law(1.5)),
        ("very soft  pen^2.5", power_law(2.5)),
        ("stiff / saturating", saturating_law()),
        ("friction  mu=0.4", frictional_law(0.4)),
        ("friction  mu=1.0", frictional_law(1.0)),
    ]
    results = [evaluate_law(name, law, args.seeds, args.noise) for name, law in laws]
    print(render_laws(results, args.noise))
    print()
    print(render_power([0.20, 0.35, 0.56, 0.75], [40, 60, 80, 120, 160, 240]))


if __name__ == "__main__":
    main()
