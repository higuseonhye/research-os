"""Commitment-point task for Paper 003's capability-crossing endpoint.

STATUS: design sketch, 2026-07-31. Abstract 1-D simulation, not preregistered,
not implemented in Isaac. See docs/paper003/paper003_commitment_task_v0.1.md.

Why this exists: the first capability probe used a continuous reach-and-hold
task and produced no threshold, because continuous re-aiming averages
prediction error away - a wrong aim at step t is corrected at t+1, so no arm is
ever locked out. A capability threshold needs an action that cannot be
corrected after the fact.

Here the agent commits to dispensing onto a bread slice carried by an
intermittently nudged tray. The dispense takes `latency` steps, lands wherever
the bread is at completion, and is irreversible. The agent must predict the
bread's position at commit time, with no second chance.

Arms mirror the main protocol:
    B  aim at the observed position          (parameter repair)
    C  constant-velocity extrapolation       (Paper 002's mode operator)
    D  predict via the tray's motion         (relation expansion)

Arm B's lockout speed follows exactly from the task geometry (see
`predicted_zero_order_cutoff`), so it can be stated in a preregistration
before any run rather than fitted. Arm C's plateau has only a geometric
*lower* bound (`constant_velocity_exact_fraction`); the observed plateau sits
above it because near-misses within tolerance also succeed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class CommitmentTaskSpec:
    """Task geometry. All distances in metres, all times in simulation steps."""

    tolerance: float = 0.020
    dispense_latency: int = 6
    burst_on: int = 10
    burst_off: int = 4
    episode_steps: int = 60
    commit_low: int = 15
    commit_high: int = 40
    observation_noise: float = 0.0
    """Per-step Gaussian noise on the *observed* reference position.

    Zero by default to keep the geometric predictions exact, but the noiseless
    case makes pattern recovery nearly trivial, so arm D lands close to its own
    oracle there. That is a property of this proxy, not a finding. Sweep this
    to see where the estimator actually breaks.
    """

    def validate(self) -> None:
        if self.tolerance <= 0.0:
            raise ValueError("tolerance must be > 0")
        if self.observation_noise < 0.0:
            raise ValueError("observation_noise must be >= 0")
        if self.dispense_latency < 1:
            raise ValueError("dispense_latency must be >= 1")
        if self.burst_on < 1 or self.burst_off < 1:
            raise ValueError("burst_on and burst_off must be >= 1")
        if self.commit_high <= self.commit_low:
            raise ValueError("commit_high must exceed commit_low")
        if self.commit_high + self.dispense_latency > self.episode_steps:
            raise ValueError("episode_steps must cover the latest dispense window")

    @property
    def period(self) -> int:
        return self.burst_on + self.burst_off

    def is_moving(self, step: int) -> bool:
        return (step % self.period) < self.burst_on

    def min_moving_steps_in_window(self) -> int:
        """Fewest moving steps any dispense window can contain."""
        return min(
            sum(self.is_moving(start + h) for h in range(1, self.dispense_latency + 1))
            for start in range(self.period)
        )

    def predicted_zero_order_cutoff(self) -> float:
        """Tray speed *strictly above* which aiming at the observed position always misses.

        Every dispense window contains at least `min_moving_steps_in_window`
        moving steps, so the bread is displaced by at least that many times the
        speed. Arm B succeeds only while that displacement stays within
        tolerance, so it is locked out above tolerance / that count.

        Note this is the *marginal* speed: at exactly the cutoff the minimum
        displacement equals the tolerance and still counts as a hit, so arm B
        reaches a hard zero only strictly above it.
        """
        moving = self.min_moving_steps_in_window()
        if moving == 0:
            return float("inf")
        return self.tolerance / moving

    def constant_velocity_exact_fraction(self) -> float:
        """LOWER bound on arm C's ceiling: commits where constant velocity is *exact*.

        Constant-velocity extrapolation is exactly right only when the burst
        state does not change during the dispense window. It is a lower bound,
        not the ceiling: arm C also succeeds on state changes whose resulting
        error still falls within tolerance, so the observed plateau sits above
        this value (0.286 predicted vs ~0.32-0.36 observed at the default spec).
        """
        unchanged = sum(
            1
            for start in range(self.period)
            if len({self.is_moving(start + h) for h in range(0, self.dispense_latency + 1)}) == 1
        )
        return unchanged / self.period


def _tray_offset_at(step: int, speed: float, spec: CommitmentTaskSpec) -> float:
    return speed * sum(spec.is_moving(s) for s in range(step + 1))


class ReferencePatternEstimator:
    """Infers the reference body's motion from observed positions alone.

    This is what makes arm D an arm rather than an oracle. It sees only the
    history of reference positions up to the moment of commitment and must
    work out, from that: how fast the body moves while moving, how long its
    bursts and pauses last, and where in that cycle it currently sits.

    All three are estimated, so all three can be wrong - the estimator has real
    failure modes, most obviously when the observed history is shorter than a
    couple of cycles. That is the intended behaviour; an arm that cannot be
    wrong is not evidence of anything.
    """

    def __init__(self, motion_floor_ratio: float = 0.25) -> None:
        if not 0.0 < motion_floor_ratio < 1.0:
            raise ValueError("motion_floor_ratio must be in (0, 1)")
        self.motion_floor_ratio = float(motion_floor_ratio)

    @staticmethod
    def _run_lengths(flags: list[bool]) -> tuple[list[int], list[int], int, bool]:
        """Split a boolean sequence into runs; return on-runs, off-runs, and the tail."""
        runs: list[tuple[bool, int]] = []
        for flag in flags:
            if runs and runs[-1][0] == flag:
                runs[-1] = (flag, runs[-1][1] + 1)
            else:
                runs.append((flag, 1))
        on = [n for value, n in runs[:-1] if value]
        off = [n for value, n in runs[:-1] if not value]
        tail_value, tail_len = runs[-1]
        return on, off, tail_len, tail_value

    def predict_displacement(self, history: Sequence[float], horizon: int) -> float | None:
        """Displacement expected over the next `horizon` steps. None if unusable."""

        if horizon < 0:
            raise ValueError("horizon must be >= 0")
        if len(history) < 4:
            return None

        deltas = np.diff(np.asarray(history, dtype=np.float64))
        largest = float(np.max(np.abs(deltas)))
        if largest <= 0.0:
            return 0.0  # nothing has moved; predicting no motion is the estimate

        moving = [bool(abs(d) >= self.motion_floor_ratio * largest) for d in deltas]
        speed = float(np.mean(np.abs(deltas[np.asarray(moving)]))) if any(moving) else 0.0

        on_runs, off_runs, tail_len, tail_moving = self._run_lengths(moving)

        # Without at least one completed burst and one completed pause the cycle
        # is not identifiable; say so rather than guessing.
        if not on_runs or not off_runs:
            return None

        burst_on = int(round(float(np.median(on_runs))))
        burst_off = int(round(float(np.median(off_runs))))
        if burst_on < 1 or burst_off < 1:
            return None

        direction = 1.0 if float(np.sum(deltas)) >= 0.0 else -1.0
        phase = tail_len  # steps already spent in the current run
        currently_moving = tail_moving

        displacement = 0.0
        for _ in range(horizon):
            if currently_moving:
                displacement += speed
                phase += 1
                if phase >= burst_on:
                    currently_moving, phase = False, 0
            else:
                phase += 1
                if phase >= burst_off:
                    currently_moving, phase = True, 0
        return direction * displacement


ARMS = ("B", "C", "D", "D_oracle")


def run_trial(arm: str, seed: int, tray_speed: float, spec: CommitmentTaskSpec | None = None) -> bool:
    """One commit-and-dispense attempt. Returns True if the filling lands on the bread.

    Every arm sees the same observed history of reference positions up to the
    commit step, and differs only in what it does with it. `D_oracle` is kept
    as a reference ceiling: it is handed the true landing point, so it is not a
    result - it bounds what perfect knowledge of the relation would buy.
    """

    spec = spec or CommitmentTaskSpec()
    spec.validate()
    if arm not in ARMS:
        raise ValueError(f"arm must be one of {ARMS}")

    rng = np.random.default_rng(seed)
    commit = int(rng.integers(spec.commit_low, spec.commit_high))

    truth = [_tray_offset_at(step, tray_speed, spec) for step in range(commit + 1)]
    if spec.observation_noise > 0.0:
        history = list(np.asarray(truth) + rng.normal(0.0, spec.observation_noise, len(truth)))
    else:
        history = truth
    here = history[-1]
    # The filling lands on the true tray, not the noisy estimate of it.
    landing = _tray_offset_at(commit + spec.dispense_latency, tray_speed, spec)

    if arm == "B":
        aim = here
    elif arm == "C":
        aim = here + spec.dispense_latency * (here - history[-2])
    elif arm == "D_oracle":
        aim = landing
    else:
        estimated = ReferencePatternEstimator().predict_displacement(
            history, spec.dispense_latency
        )
        # An unusable estimate falls back to the zero-order aim rather than
        # inventing one; the arm is penalised for it, which is correct.
        aim = here if estimated is None else here + estimated

    return bool(abs(aim - landing) <= spec.tolerance)


def success_rate(
    arm: str, tray_speed: float, seeds: int = 200, spec: CommitmentTaskSpec | None = None
) -> float:
    return float(np.mean([run_trial(arm, s, tray_speed, spec) for s in range(seeds)]))


if __name__ == "__main__":
    spec = CommitmentTaskSpec()
    print(f"arm-B lockout (strictly above): {spec.predicted_zero_order_cutoff() * 1000:.1f} mm/step")
    print(f"arm-C exact-fraction lower bound: {spec.constant_velocity_exact_fraction():.3f}")
    print()
    print(f"{'mm/step':>9}{'B':>7}{'C':>7}{'D':>7}{'D_oracle':>10}")
    for speed in (0.002, 0.004, 0.006, 0.008, 0.010, 0.015, 0.020):
        rates = {arm: success_rate(arm, speed, spec=spec) for arm in ARMS}
        print(
            f"{speed * 1000:>9.1f}{rates['B']:>7.2f}{rates['C']:>7.2f}"
            f"{rates['D']:>7.2f}{rates['D_oracle']:>10.2f}"
        )
    print("\nD estimates the reference pattern from observation; D_oracle is handed")
    print("the answer and is a ceiling, not a result.")
