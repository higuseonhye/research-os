"""Live commitment-point demo: place a topping while the plate gets nudged.

STATUS: demo tool, 2026-07-31. Not an experiment - it collects no preregistered
data and must not be cited as evidence. It exists to make the Paper 003 finding
touchable: prediction quality is invisible in correctable actions and decisive
in irreversible ones.

What a viewer does
------------------
Two markers sit under an overhead camera: the PLATE (target) and the PUSHER
(reference tool). The viewer nudges the plate with the pusher, then presses
SPACE at the moment they would release a topping. The topping lands `latency`
frames later, wherever the plate is by then.

Three arms predict that landing point, and only their prediction differs:

    B  zero order        the plate is where it is now, and stays there
    C  constant velocity the plate keeps its current velocity
    D  relation          the plate is coupled to the pusher; roll the pusher
                         forward and re-apply the contact

Arm D's advantage is physically real, not scripted: while the pusher is
approaching but not yet touching, B and C both say "the plate will not move,"
and D says "contact is imminent, it will." That gap is the whole point.

Two honesty notes
-----------------
1. In `--source sim` arm D predicts with exactly the coupling model that
   generates the motion, so its 100% is self-fulfilling and proves nothing. Sim
   mode is for checking the tool runs. The camera version is the real thing,
   where D has to estimate the coupling from what it sees.
2. Outside the contact-imminent regime the plate simply will not move and every
   arm is trivially right. The overlay says so, and auto-commit only fires
   inside that regime - otherwise the demo would show a difference that is not
   there.

Run
---
    python scripts/demo_commitment_live.py --source sim        # no camera needed
    python scripts/demo_commitment_live.py --source webcam

Keys: click a marker to sample its colour (plate first, then pusher),
      SPACE commit, R reset tallies, Q quit.
"""

from __future__ import annotations

import argparse
import sys
from collections import deque
from dataclasses import dataclass, field

import cv2
import numpy as np

sys.path.insert(0, str(__file__.rsplit("demo_commitment_live.py", 1)[0]))

from wm_expansion.relation_dynamics import CouplingSpec, coupling_displacement


# --------------------------------------------------------------------------
# configuration
# --------------------------------------------------------------------------


@dataclass
class DemoConfig:
    """Defaults are the dessert-scale numbers from the design doc."""

    tolerance_mm: float = 5.0
    latency_frames: int = 6
    px_per_mm: float = 3.0
    interaction_mm: float = 45.0
    coupling_gain: float = 0.6
    history: int = 12

    @property
    def tolerance_px(self) -> float:
        return self.tolerance_mm * self.px_per_mm

    @property
    def interaction_px(self) -> float:
        return self.interaction_mm * self.px_per_mm


@dataclass
class Tally:
    hits: int = 0
    shots: int = 0

    def record(self, hit: bool) -> None:
        self.shots += 1
        self.hits += int(hit)

    @property
    def rate(self) -> float:
        return self.hits / self.shots if self.shots else 0.0

    def label(self) -> str:
        return f"{self.hits}/{self.shots}" + (f"  {self.rate:.0%}" if self.shots else "")


@dataclass
class PendingShot:
    """A committed placement, waiting for the topping to land."""

    frames_left: int
    aims: dict[str, np.ndarray]


@dataclass
class DemoState:
    plate: deque = field(default_factory=lambda: deque(maxlen=32))
    pusher: deque = field(default_factory=lambda: deque(maxlen=32))
    tallies: dict[str, Tally] = field(default_factory=lambda: {a: Tally() for a in "BCD"})
    pending: list[PendingShot] = field(default_factory=list)
    last_result: dict[str, bool] | None = None
    last_truth: np.ndarray | None = None


# --------------------------------------------------------------------------
# the three arms
# --------------------------------------------------------------------------


def contact_imminent(state: DemoState, cfg: DemoConfig) -> bool:
    """Is the pusher closing on the plate, near enough to matter within the release?

    Outside this regime the task is trivial - the plate simply will not move, so
    every arm is right and the demo shows nothing. This is the same posture as
    the confirmatory design's eligibility screen: the comparison is only
    meaningful on cells where the arms can actually differ.
    """

    if len(state.plate) < 2 or len(state.pusher) < 2:
        return False
    plate = np.asarray(state.plate[-1], dtype=np.float64)
    pusher = np.asarray(state.pusher[-1], dtype=np.float64)
    pusher_prev = np.asarray(state.pusher[-2], dtype=np.float64)

    separation = float(np.linalg.norm(plate - pusher))
    closing = float(np.linalg.norm(plate - pusher_prev)) - separation
    reach = separation - cfg.interaction_px
    return closing > 0.0 and 0.0 < reach <= closing * cfg.latency_frames


def predict_arms(state: DemoState, cfg: DemoConfig) -> dict[str, np.ndarray] | None:
    """Each arm's predicted landing point, in pixels. None if not enough history."""

    if len(state.plate) < 2 or len(state.pusher) < 2:
        return None

    plate = np.asarray(state.plate[-1], dtype=np.float64)
    plate_prev = np.asarray(state.plate[-2], dtype=np.float64)
    pusher = np.asarray(state.pusher[-1], dtype=np.float64)
    pusher_prev = np.asarray(state.pusher[-2], dtype=np.float64)

    latency = cfg.latency_frames

    # B: the plate is where it is, and stays.
    aim_b = plate.copy()

    # C: the plate keeps its current velocity.
    aim_c = plate + latency * (plate - plate_prev)

    # D: the plate is coupled to the pusher. Roll the pusher forward at its
    # observed velocity and re-apply contact each step, so an approaching
    # pusher predicts motion the other two arms cannot see coming.
    spec = CouplingSpec(
        interaction_radius=cfg.interaction_px,
        coupling_gain=cfg.coupling_gain,
    )
    pusher_velocity = pusher - pusher_prev
    aim_d = plate.copy()
    rolling_pusher = pusher.copy()
    for _ in range(latency):
        rolling_pusher = rolling_pusher + pusher_velocity
        aim_d = aim_d + coupling_displacement(aim_d, rolling_pusher, spec)

    return {"B": aim_b, "C": aim_c, "D": aim_d}


# --------------------------------------------------------------------------
# marker tracking
# --------------------------------------------------------------------------


class ColourTracker:
    """Tracks one marker by HSV colour, sampled by clicking on it."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.lower: np.ndarray | None = None
        self.upper: np.ndarray | None = None

    @property
    def ready(self) -> bool:
        return self.lower is not None

    def sample(self, frame_bgr: np.ndarray, x: int, y: int, span: int = 6) -> None:
        hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
        h0, w0 = hsv.shape[:2]
        patch = hsv[max(0, y - span):min(h0, y + span), max(0, x - span):min(w0, x + span)]
        if patch.size == 0:
            return
        h, s, v = np.median(patch.reshape(-1, 3), axis=0)
        self.lower = np.array([max(0, h - 12), max(60, s - 70), max(60, v - 70)], np.uint8)
        self.upper = np.array([min(179, h + 12), 255, 255], np.uint8)

    def locate(self, frame_bgr: np.ndarray) -> np.ndarray | None:
        if not self.ready:
            return None
        hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower, self.upper)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None
        biggest = max(contours, key=cv2.contourArea)
        if cv2.contourArea(biggest) < 60:
            return None
        moments = cv2.moments(biggest)
        if moments["m00"] == 0:
            return None
        return np.array([moments["m10"] / moments["m00"], moments["m01"] / moments["m00"]])


# --------------------------------------------------------------------------
# synthetic source, so the tool can be checked without a camera
# --------------------------------------------------------------------------


class SimSource:
    """A pusher sweeps in and shoves the plate. Same coupling as the module."""

    def __init__(self, cfg: DemoConfig, width: int = 960, height: int = 540) -> None:
        self.cfg = cfg
        self.size = (height, width)
        self.plate = np.array([width * 0.55, height * 0.5])
        self.rest = self.plate.copy()
        self.pusher = np.array([width * 0.1, height * 0.5])
        self.direction = 1.0
        self.speed = 6.0
        self.spec = CouplingSpec(
            interaction_radius=cfg.interaction_px, coupling_gain=cfg.coupling_gain
        )

    def read(self) -> tuple[bool, np.ndarray]:
        self.pusher = self.pusher + np.array([self.speed * self.direction, 0.0])
        if self.pusher[0] > self.size[1] * 0.9 or self.pusher[0] < self.size[1] * 0.05:
            self.direction *= -1.0
        self.plate = self.plate + coupling_displacement(self.plate, self.pusher, self.spec)
        # A light pull back toward the plate's rest position keeps it in frame.
        # Do NOT clip: a hard boundary is unmodelled by every arm and would score
        # the relation arm down for an artefact of this synthetic source.
        self.plate = self.plate + 0.02 * (self.rest - self.plate)

        frame = np.full((*self.size, 3), 32, np.uint8)
        cv2.circle(frame, tuple(self.plate.astype(int)), 26, (90, 200, 250), -1)
        cv2.circle(frame, tuple(self.pusher.astype(int)), 16, (250, 140, 90), -1)
        return True, frame

    def release(self) -> None:  # parity with VideoCapture
        return None


# --------------------------------------------------------------------------
# drawing
# --------------------------------------------------------------------------

ARM_COLOUR = {"B": (110, 110, 250), "C": (90, 210, 250), "D": (120, 240, 130)}
ARM_NAME = {"B": "B  zero order", "C": "C  const velocity", "D": "D  relation"}


def draw_overlay(
    frame: np.ndarray,
    state: DemoState,
    cfg: DemoConfig,
    aims: dict | None,
    speed_mm_s: float,
    imminent: bool = False,
) -> None:
    h, w = frame.shape[:2]
    panel = frame.copy()
    cv2.rectangle(panel, (0, 0), (330, 200), (18, 18, 18), -1)
    cv2.addWeighted(panel, 0.75, frame, 0.25, 0, frame)

    cv2.putText(frame, "COMMITMENT POINT", (16, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (235, 235, 235), 1, cv2.LINE_AA)
    cv2.putText(frame, f"tolerance {cfg.tolerance_mm:.0f} mm   release {cfg.latency_frames}f",
                (16, 52), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (170, 170, 170), 1, cv2.LINE_AA)

    for row, arm in enumerate("BCD"):
        y = 84 + row * 30
        tally = state.tallies[arm]
        cv2.circle(frame, (26, y - 5), 6, ARM_COLOUR[arm], -1)
        cv2.putText(frame, ARM_NAME[arm], (42, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                    (225, 225, 225), 1, cv2.LINE_AA)
        cv2.putText(frame, tally.label(), (215, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                    ARM_COLOUR[arm], 1, cv2.LINE_AA)
        if state.last_result is not None:
            mark = "HIT" if state.last_result[arm] else "MISS"
            colour = (120, 240, 130) if state.last_result[arm] else (110, 110, 250)
            cv2.putText(frame, mark, (285, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, colour, 1,
                        cv2.LINE_AA)

    # speed bar against the analytic lockout for arm B
    lockout = cfg.tolerance_mm / 2.0 / (cfg.latency_frames / 60.0) / 10.0
    over = speed_mm_s > lockout
    cv2.putText(frame, f"plate {speed_mm_s:6.0f} mm/s", (16, 182),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                (110, 110, 250) if over else (170, 170, 170), 1, cv2.LINE_AA)

    # The arms can only differ while contact is coming. Say so, rather than
    # letting a viewer commit in the trivial regime and conclude nothing.
    if imminent:
        cv2.rectangle(frame, (2, 2), (w - 3, h - 3), (120, 240, 130), 3)
        cv2.putText(frame, "CONTACT COMING - commit now", (w - 350, 34),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (120, 240, 130), 2, cv2.LINE_AA)
    else:
        cv2.putText(frame, "plate will not move - any arm wins", (w - 380, 34),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1, cv2.LINE_AA)

    if aims is not None:
        for arm, point in aims.items():
            p = tuple(np.asarray(point, dtype=int))
            cv2.drawMarker(frame, p, ARM_COLOUR[arm], cv2.MARKER_CROSS, 18, 2)
    if state.plate:
        cv2.circle(frame, tuple(np.asarray(state.plate[-1], int)), int(cfg.tolerance_px),
                   (200, 200, 200), 1)
    if state.last_truth is not None:
        cv2.drawMarker(frame, tuple(np.asarray(state.last_truth, int)), (255, 255, 255),
                       cv2.MARKER_TILTED_CROSS, 22, 2)

    cv2.putText(frame, "click plate then pusher  |  SPACE commit  |  R reset  |  Q quit",
                (16, h - 16), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (200, 200, 200), 1, cv2.LINE_AA)


# --------------------------------------------------------------------------
# main loop
# --------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=["webcam", "sim"], default="webcam")
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--px-per-mm", type=float, default=3.0)
    parser.add_argument("--tolerance-mm", type=float, default=5.0)
    parser.add_argument("--latency-frames", type=int, default=6)
    parser.add_argument("--max-frames", type=int, default=0, help="stop after N frames (testing)")
    args = parser.parse_args()

    cfg = DemoConfig(
        tolerance_mm=args.tolerance_mm,
        latency_frames=args.latency_frames,
        px_per_mm=args.px_per_mm,
    )
    state = DemoState()
    trackers = {"plate": ColourTracker("plate"), "pusher": ColourTracker("pusher")}
    headless = args.max_frames > 0

    if args.source == "sim":
        source = SimSource(cfg)
    else:
        source = cv2.VideoCapture(args.camera)
        if not source.isOpened():
            raise SystemExit(
                f"could not open camera {args.camera}. Try --source sim to check the tool."
            )

    window = "commitment point"
    click_target = {"which": "plate"}
    latest = {"frame": None}

    def on_click(event: int, x: int, y: int, flags: int, param: object) -> None:
        if event != cv2.EVENT_LBUTTONDOWN or latest["frame"] is None:
            return
        which = click_target["which"]
        trackers[which].sample(latest["frame"], x, y)
        click_target["which"] = "pusher" if which == "plate" else "plate"

    if not headless:
        cv2.namedWindow(window)
        cv2.setMouseCallback(window, on_click)

    frames = 0
    while True:
        ok, frame = source.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1) if args.source == "webcam" else frame
        latest["frame"] = frame.copy()

        if args.source == "sim":
            # markers are known exactly in sim; skip colour tracking
            plate_xy, pusher_xy = source.plate.copy(), source.pusher.copy()
        else:
            plate_xy = trackers["plate"].locate(frame)
            pusher_xy = trackers["pusher"].locate(frame)

        if plate_xy is not None:
            state.plate.append(plate_xy)
        if pusher_xy is not None:
            state.pusher.append(pusher_xy)

        aims = predict_arms(state, cfg)

        # resolve any in-flight placements
        landed = []
        for shot in state.pending:
            shot.frames_left -= 1
            if shot.frames_left <= 0 and state.plate:
                truth = np.asarray(state.plate[-1], dtype=np.float64)
                result = {
                    arm: bool(np.linalg.norm(aim - truth) <= cfg.tolerance_px)
                    for arm, aim in shot.aims.items()
                }
                for arm, hit in result.items():
                    state.tallies[arm].record(hit)
                state.last_result, state.last_truth = result, truth
                landed.append(shot)
        for shot in landed:
            state.pending.remove(shot)

        speed_mm_s = 0.0
        if len(state.plate) >= 2:
            step_px = float(np.linalg.norm(state.plate[-1] - state.plate[-2]))
            speed_mm_s = step_px / cfg.px_per_mm * 30.0  # assume ~30 fps

        imminent = contact_imminent(state, cfg)
        draw_overlay(frame, state, cfg, aims, speed_mm_s, imminent)

        frames += 1
        if headless:
            if frames >= args.max_frames:
                break
            # Auto-commit only in the regime where the arms can differ.
            if aims is not None and contact_imminent(state, cfg):
                state.pending.append(PendingShot(cfg.latency_frames, aims))
            continue

        cv2.imshow(window, frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("r"):
            state.tallies = {a: Tally() for a in "BCD"}
            state.last_result = state.last_truth = None
        if key == ord(" ") and aims is not None:
            state.pending.append(PendingShot(cfg.latency_frames, aims))

    source.release()
    if not headless:
        cv2.destroyAllWindows()

    print("final tallies")
    for arm in "BCD":
        print(f"  {ARM_NAME[arm]:<20} {state.tallies[arm].label()}")
    if args.source == "sim":
        print(
            "\nnote: in sim, arm D uses the same coupling model that generates the\n"
            "motion, so its score is self-fulfilling. Not evidence - run the camera."
        )


if __name__ == "__main__":
    main()
