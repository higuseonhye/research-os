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

    def validate(self) -> None:
        if self.tolerance <= 0.0:
            raise ValueError("tolerance must be > 0")
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


def run_trial(arm: str, seed: int, tray_speed: float, spec: CommitmentTaskSpec | None = None) -> bool:
    """One commit-and-dispense attempt. Returns True if the filling lands on the bread."""

    spec = spec or CommitmentTaskSpec()
    spec.validate()
    if arm not in {"B", "C", "D"}:
        raise ValueError("arm must be one of B, C, D")

    rng = np.random.default_rng(seed)
    commit = int(rng.integers(spec.commit_low, spec.commit_high))

    here = _tray_offset_at(commit, tray_speed, spec)
    previous = _tray_offset_at(commit - 1, tray_speed, spec)
    landing = _tray_offset_at(commit + spec.dispense_latency, tray_speed, spec)

    if arm == "B":
        aim = here
    elif arm == "C":
        aim = here + spec.dispense_latency * (here - previous)
    else:
        # Relation: the bread rides the tray, so roll the tray forward.
        aim = landing

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
    print(f"{'mm/step':>9}{'B':>7}{'C':>7}{'D':>7}")
    for speed in (0.002, 0.004, 0.006, 0.008, 0.010, 0.015, 0.020):
        rates = {arm: success_rate(arm, speed, spec=spec) for arm in "BCD"}
        print(f"{speed * 1000:>9.1f}{rates['B']:>7.2f}{rates['C']:>7.2f}{rates['D']:>7.2f}")
