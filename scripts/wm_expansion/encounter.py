"""Encounter geometry and schedules for the Paper 003 commitment episode.

Physics-free and Isaac-free, for the same reason `commitment_episode` is: the
Isaac runner cannot be imported, executed or even syntax-checked without a GPU,
so anything decided inside it ships unverified. That surface has produced eight
defects in this project already - an invented task name, a wrong command name, a
gate that was never consulted, a projection along the wrong axis. Geometry
decides which encounter happens, so it belongs here where tests can reach it.

The runner keeps only what genuinely needs Isaac: build a scene, step physics,
read poses, write the command.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class EncounterSpec:
    """How the reference bodies move. Distances in metres, times in steps."""

    interaction_radius: float = 0.05
    reference_speed: float = 0.015

    #: `burst` only ever advances - the v5 schedule. `probe` withdraws after
    #: striking, which is what lets a completed contact be observed before the
    #: commitment; without it a struck target and a sliding one are the same
    #: history and the relation is not identifiable.
    schedule: str = "probe"
    burst_on: int = 10
    burst_off: int = 4
    probe_advance: int = 7
    probe_withdraw: int = 5
    probe_hold: int = 2

    #: A second body turns the task from "extrapolate this body" into "apply the
    #: relation to a body it was not learned on". At the commitment the target
    #: is stationary - the first body has gone, the second has not arrived - so
    #: zero-order and constant velocity both predict no motion.
    bodies: int = 1
    pusher_speed: float = 0.015
    pusher_start_step: int = 16

    def validate(self) -> None:
        if self.interaction_radius <= 0.0:
            raise ValueError("interaction_radius must be > 0")
        if self.reference_speed <= 0.0 or self.pusher_speed <= 0.0:
            raise ValueError("speeds must be > 0")
        if self.schedule not in ("burst", "probe"):
            raise ValueError("schedule must be 'burst' or 'probe'")
        if self.burst_on < 1 or self.burst_off < 1:
            raise ValueError("burst_on and burst_off must be >= 1")
        if self.probe_advance < 1 or self.probe_withdraw < 1 or self.probe_hold < 0:
            raise ValueError("probe phases must be >= 1, hold >= 0")
        if self.probe_withdraw * self.reference_speed <= self.interaction_radius:
            raise ValueError(
                "the withdrawal must clear the interaction radius, or the target "
                "is never observed after the body leaves and the relation stays "
                "unidentifiable"
            )
        # A body that advances further per step than the interaction radius
        # steps over the contact zone between observations: the encounter has no
        # observable contact episode in it, however the gate is configured.
        #
        # This is the ratio the design was drawn at - 15 mm against a 50 mm
        # radius, 0.3 - and porting to a scene where contact happens at 2 to
        # 5 mm silently broke it: 40 mm against 12 mm is 3.3, and eligibility
        # never opened in any cell.
        #
        # Note this is the speed of the *scripted* point. On a real arm the
        # command is a goal, not a teleport, and the arm's achievable speed is
        # what belongs here - measured at roughly a sixth of the commanded
        # value in the lift scene.
        for name, speed in (("reference_speed", self.reference_speed),
                            ("pusher_speed", self.pusher_speed)):
            if speed >= self.interaction_radius:
                raise ValueError(
                    f"{name} ({speed}) must stay below the interaction radius "
                    f"({self.interaction_radius}), or a body crosses the contact "
                    "zone between observations and no contact is ever seen"
                )
        if self.bodies not in (1, 2):
            raise ValueError("bodies must be 1 or 2")
        if self.pusher_start_step < 0:
            raise ValueError("pusher_start_step must be >= 0")

    @property
    def period(self) -> int:
        if self.schedule == "burst":
            return self.burst_on + self.burst_off
        return self.probe_advance + self.probe_withdraw + self.probe_hold


@dataclass(frozen=True)
class EncounterGeometry:
    """One cell's drawn encounter. Everything a body's position depends on."""

    prober_start: np.ndarray
    prober_axis: np.ndarray
    phase_offset: int
    pusher_start: np.ndarray
    pusher_axis: np.ndarray
    azimuth: float
    pusher_azimuth: float
    lateral_offset: float

    def to_dict(self) -> dict:
        return {
            "azimuth": float(self.azimuth),
            "pusher_azimuth": float(self.pusher_azimuth),
            "lateral_offset": float(self.lateral_offset),
            "phase_offset": int(self.phase_offset),
        }


def schedule_direction(step: int, spec: EncounterSpec) -> int:
    """+1 advancing, -1 withdrawing, 0 holding, for the *first* body.

    With two bodies the first body strikes once and stops for good. That is not
    a simplification, it is required: a first body that keeps cycling keeps
    pushing the target, and the second body's approach line was fixed at draw
    time against the target's *initial* position. Measured, a cycling prober
    carried the target 74 mm away and the pusher's closest approach became
    61 mm against a 50 mm radius - it never touched, and a two-body run was
    byte-identical to a one-body one.

    A single body still cycles, because there the recurring contacts are what
    give the coupling estimator enough points to fit.
    """

    if spec.bodies == 2 and step >= spec.probe_advance + spec.probe_withdraw:
        return 0
    cycle = step % spec.period
    if spec.schedule == "burst":
        return 1 if cycle < spec.burst_on else 0
    if cycle < spec.probe_advance:
        return 1
    if cycle < spec.probe_advance + spec.probe_withdraw:
        return -1
    return 0


def reference_offset(step: int, spec: EncounterSpec) -> float:
    """Cumulative displacement of the first body along its approach axis."""

    return spec.reference_speed * sum(
        schedule_direction(s, spec) for s in range(step + 1)
    )


def draw_geometry(seed: int, target: np.ndarray, spec: EncounterSpec) -> EncounterGeometry:
    """Draw one cell's encounter from its seed.

    The approach azimuth and lateral offset are drawn rather than fixed. An
    earlier version fixed the axis to +x at a constant offset, which made the
    whole interaction translation-invariant: ten seeds gave ten positions but
    one identical encounter, and every arm's miss came out the same every time.
    """

    spec.validate()
    rng = np.random.default_rng(seed)
    target = np.asarray(target, dtype=np.float64)

    azimuth = float(rng.uniform(0.0, 2.0 * np.pi))
    axis = np.array([np.cos(azimuth), np.sin(azimuth), 0.0])
    lateral = np.array([-axis[1], axis[0], 0.0])
    offset = float(rng.uniform(-0.5, 0.5)) * spec.interaction_radius

    # How far the first body starts back. Under `burst` it must stay outside the
    # radius long enough for one full cycle to be observed, or the encounter is
    # over before the pattern can be identified. Under `probe` the binding
    # requirement is different and tighter: one *completed* contact - strike,
    # withdraw past the radius, and at least one observation afterwards - must
    # fit before the commit window.
    if spec.schedule == "burst":
        floor = spec.burst_on * spec.reference_speed + spec.interaction_radius
        approach = floor * float(rng.uniform(1.05, 1.6))
    else:
        approach = spec.interaction_radius * float(rng.uniform(2.2, 2.8))
    # A phase offset places the encounter somewhere in a repeating cycle. With
    # two bodies there is no cycle - the first body strikes once and stops - so
    # an offset would start it partway through, or past its only advance
    # entirely. Measured, that left the prober's closest approach at 51.8 mm
    # against a 50 mm radius: the body that is supposed to demonstrate the
    # relation never touched the target.
    phase_offset = 0 if spec.bodies == 2 else int(rng.integers(0, spec.period))

    # The second body approaches from at least 60 degrees away, so the two are
    # distinguishable encounters rather than one approach in two parts, and
    # starts far enough back to arrive only after the first has withdrawn.
    pusher_azimuth = azimuth + float(rng.uniform(np.pi / 3.0, 5.0 * np.pi / 3.0))
    pusher_axis = np.array([np.cos(pusher_azimuth), np.sin(pusher_azimuth), 0.0])
    pusher_lateral = np.array([-pusher_axis[1], pusher_axis[0], 0.0])
    pusher_travel = spec.interaction_radius + spec.pusher_speed * 12.0

    return EncounterGeometry(
        prober_start=target - axis * approach + lateral * offset,
        prober_axis=axis,
        phase_offset=phase_offset,
        pusher_start=(
            target
            - pusher_axis * pusher_travel
            + pusher_lateral * (float(rng.uniform(-0.4, 0.4)) * spec.interaction_radius)
        ),
        pusher_axis=pusher_axis,
        azimuth=azimuth,
        pusher_azimuth=pusher_azimuth,
        lateral_offset=offset,
    )


def bodies_at(step: int, geometry: EncounterGeometry, spec: EncounterSpec) -> np.ndarray:
    """Every reference body's position at `step`, as ``[body, 3]``.

    Analytic rather than simulated: these are moving points, not rigid assets,
    so a second one costs nothing to construct. **Real contact physics is a
    separate branch and remains unmet** - the scene reports no rigid objects at
    all, so a body would have to be added to it.
    """

    if step < 0:
        raise ValueError("step must be >= 0")
    prober = geometry.prober_start + geometry.prober_axis * reference_offset(
        step + geometry.phase_offset, spec
    )
    if spec.bodies == 1:
        return prober[None, :]
    closed = max(0, step - spec.pusher_start_step) * spec.pusher_speed
    return np.stack([prober, geometry.pusher_start + geometry.pusher_axis * closed])


def bodies_over(
    start: int, count: int, geometry: EncounterGeometry, spec: EncounterSpec
) -> np.ndarray:
    """Body positions for `count` steps from `start`, as ``[step, body, 3]``.

    This is what the eligibility screen consumes. It comes from the harness
    rather than from a prediction on purpose: predicting it would route
    eligibility through arm D's pattern estimator and make it depend on one
    arm's readiness.
    """

    if count < 0:
        raise ValueError("count must be >= 0")
    if count == 0:
        return np.empty((0, spec.bodies, 3), dtype=np.float64)
    return np.stack([bodies_at(start + ahead, geometry, spec) for ahead in range(count)])
