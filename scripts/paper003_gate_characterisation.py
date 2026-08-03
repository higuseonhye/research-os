"""Re-derive the relation gate's thresholds from Isaac data, and find what they miss.

CPU only. `RelationGateThresholds` carries an explicit note that its values were
"derived 2026-07-31 from the CPU proxy ... they must be re-derived from Isaac
data before the prereg is frozen, because the proxy has no contact noise and
produces an unrealistically clean proximity_contrast of exactly 1.0". This does
that, using the 40 records of the v5 sweep.

Two halves, because the answer has two parts.

**Threshold plateau** reads the recorded per-step gate statistics and asks how
much the fire/no-fire decision actually depends on where the thresholds sit. It
turns out barely at all, which is the good news: `min_proximity_contrast = 0.50`
is not a tuned value, it is the middle of a wide plateau.

**Post-contact sliding** is the bad news, and it is the reason this script
exists rather than a one-line note. The sweep's `drift` control is degenerate:
the target runs along the reference's own axis at the reference's own speed, so
the two never close and the gate rejects `drift` because nothing is nearby. The
constant-velocity clause - the clause that is supposed to keep Paper 003 from
collapsing into Paper 002 - was therefore never put to the test. Across the
entire sweep, **zero** steps passed the contrast test and were then blocked by
it.

The case that would actually collapse the paper is a target that is genuinely
struck by the reference and then *slides on at constant velocity*, because arm C
absorbs exactly that. Real rigid-body contact produces it. This simulates it and
measures whether the gate stays silent.

Usage:
    python scripts/paper003_gate_characterisation.py results/paper003_sweep_v5
    python scripts/paper003_gate_characterisation.py results/paper003_sweep_v5 --json
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from wm_expansion.relation_dynamics import (
    CouplingSpec,
    RelationGateThresholds,
    coupling_displacement,
    evaluate_relation_gate,
)

# The pilot's configuration. Reproduced here so the sliding study is comparable
# to the recorded sweep rather than to a fresh set of constants.
RADIUS = 0.050
GAIN = 0.50
REFERENCE_SPEED = 0.015
BURST_ON = 10
BURST_OFF = 4
HORIZON = 6  # dispense latency; CommitmentEpisode passes this, not the default 10
MIN_DELTAS = 6


# --------------------------------------------------------------------------
# Half one: what the recorded Isaac statistics support
# --------------------------------------------------------------------------


def load_gate_statistics(paths: Iterable[str]) -> dict[str, list[tuple[float, float]]]:
    """Per-condition (proximity_contrast, constant_velocity_gain) over decidable steps."""

    by_condition: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for path in paths:
        root = Path(path)
        files = sorted(root.rglob("*.json")) if root.is_dir() else [root]
        for file in files:
            try:
                record = json.loads(file.read_text())
            except (json.JSONDecodeError, OSError) as exc:
                print(f"  ! skipped {file}: {exc}")
                continue
            for observation in record.get("observations", []):
                if observation.get("step", 0) < MIN_DELTAS:
                    continue  # the gate needs min_deltas of history to decide
                by_condition[record.get("condition", "?")].append(
                    (
                        float(observation["proximity_contrast"]),
                        float(observation["constant_velocity_gain"]),
                    )
                )
    return dict(by_condition)


def threshold_plateau(
    statistics: dict[str, list[tuple[float, float]]],
    treatment: str = "coupled",
    cv_max: float = 0.30,
    grid: tuple[float, ...] = (0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90),
) -> list[dict[str, Any]]:
    """Fire rates across candidate contrast thresholds, per condition.

    A wide range over which the treatment fires and every control stays silent
    means the threshold is not doing fitted work - which is the only honest way
    to keep a value that was originally picked on a noiseless proxy.
    """

    rows = []
    for threshold in grid:
        rates: dict[str, float] = {}
        for condition, pairs in statistics.items():
            values = np.asarray(pairs)
            fires = (values[:, 0] >= threshold) & (values[:, 1] <= cv_max)
            rates[condition] = float(np.mean(fires))
        controls = [rate for name, rate in rates.items() if name != treatment]
        rows.append(
            {
                "threshold": threshold,
                "rates": rates,
                "separates": bool(rates.get(treatment, 0.0) > 0.0 and max(controls, default=0.0) == 0.0),
            }
        )
    return rows


def constant_velocity_clause_work(
    statistics: dict[str, list[tuple[float, float]]],
    contrast_min: float = 0.50,
    cv_max: float = 0.30,
) -> dict[str, dict[str, int]]:
    """How many steps the constant-velocity clause is the *only* thing rejecting.

    If this is zero everywhere, the clause is carried on design grounds alone
    and the sweep provides no evidence that it works - which is a statement
    about the controls, not about the clause.
    """

    work: dict[str, dict[str, int]] = {}
    for condition, pairs in statistics.items():
        values = np.asarray(pairs)
        passes_contrast = values[:, 0] >= contrast_min
        blocked = passes_contrast & (values[:, 1] > cv_max)
        work[condition] = {
            "steps": int(len(values)),
            "passed_contrast": int(np.count_nonzero(passes_contrast)),
            "blocked_by_constant_velocity": int(np.count_nonzero(blocked)),
        }
    return work


# --------------------------------------------------------------------------
# Half two: the control the sweep does not have
# --------------------------------------------------------------------------


def slide_rollout(
    damping: float,
    seed: int,
    steps: int = 60,
    noise: float = 0.0005,
    encounter: str = "probe",
) -> tuple[list[np.ndarray], list[np.ndarray]]:
    """Reference strikes the target, which then retains `damping` of its velocity.

    `damping = 0` reproduces the pilot's injected coupling, where the target
    stops the instant contact ends. `damping = 1` is a frictionless slide, which
    a constant-velocity model predicts perfectly - arm C's case, and the one the
    gate must refuse.

    `encounter` is the reference's schedule. `burst` only advances, which is the
    v5 sweep; `probe` withdraws after striking. The encounter matters as much as
    the gate does: under `burst` the target is never observed after the
    reference departs, and the two dampings produce the same history until then.

    The geometry is drawn per seed - azimuth and lateral offset - because a
    fixed head-on approach makes every seed a translation of one encounter.
    """

    if not 0.0 <= damping <= 1.0:
        raise ValueError("damping must be in [0, 1]")

    rng = np.random.default_rng(seed)
    spec = CouplingSpec(interaction_radius=RADIUS, coupling_gain=GAIN)
    azimuth = float(rng.uniform(0.0, 2.0 * np.pi))
    axis = np.array([np.cos(azimuth), np.sin(azimuth), 0.0])
    lateral = np.array([-axis[1], axis[0], 0.0]) * float(rng.uniform(-0.5, 0.5)) * RADIUS

    target = np.array([0.20, 0.0, 0.0])
    start = (6.0 if encounter == "burst" else 2.5) * RADIUS
    reference = target - start * axis + lateral
    velocity = np.zeros(3)

    targets, references = [], []
    for step in range(steps):
        if encounter == "burst":
            direction = 1 if step % (BURST_ON + BURST_OFF) < BURST_ON else 0
        else:
            cycle = step % 14
            direction = 1 if cycle < 7 else (-1 if cycle < 12 else 0)
        reference = reference + direction * REFERENCE_SPEED * axis
        velocity = damping * velocity + coupling_displacement(target, reference, spec)
        target = target + velocity
        targets.append(target + rng.normal(0.0, noise, 3))
        references.append(reference + rng.normal(0.0, noise, 3))
    return targets, references


def gate_under_sliding(
    damping: float,
    thresholds: RelationGateThresholds | None = None,
    seeds: int = 16,
    encounter: str = "probe",
) -> dict[str, float]:
    """Fire rates over a growing history at horizon 6, as CommitmentEpisode runs it.

    The configuration matters more than it looks: evaluating over a fixed
    12-step window instead, or at the module default horizon of 10, moves the
    constant-velocity statistic by enough to change the verdict. These are the
    settings the pilot actually ran.

    Both a per-step and a per-trial rate are returned, and **the per-trial one is
    what H3 is stated in**. They can disagree completely: firing on one step in
    eight still means firing somewhere in every trial, which is how a 12-16%
    per-step leak was in fact a 100% per-trial failure.
    """

    thresholds = thresholds or RelationGateThresholds()
    fired: list[bool] = []
    trials: list[bool] = []
    contrasts: list[float] = []
    gains: list[float] = []
    for seed in range(seeds):
        targets, references = slide_rollout(damping, seed=seed, encounter=encounter)
        this_trial = False
        for end in range(MIN_DELTAS + 1, len(targets) + 1):
            decision = evaluate_relation_gate(
                targets[:end],
                references[:end],
                thresholds,
                interaction_radius=RADIUS,
                horizon=HORIZON,
            )
            fired.append(decision.fired)
            this_trial = this_trial or decision.fired
            contrasts.append(decision.proximity_contrast)
            gains.append(decision.constant_velocity_gain)
        trials.append(this_trial)
    return {
        "damping": damping,
        "encounter": encounter,
        "fire_rate": float(np.mean(fired)),
        "trial_rate": float(np.mean(trials)),
        "median_contrast": float(np.median(contrasts)),
        "median_constant_velocity_gain": float(np.median(gains)),
        "max_constant_velocity_gain": float(np.max(gains)),
    }


#: The v5 sweep's commit steps ran 11-25. A decision that arrives after the
#: commitment is already made is of no use to any arm, so "fires eventually" is
#: not the quantity of interest - "fires in time" is.
COMMIT_WINDOW_END = 25


def first_fire_step(
    damping: float, seed: int, thresholds: RelationGateThresholds, encounter: str
) -> int | None:
    targets, references = slide_rollout(damping, seed=seed, encounter=encounter)
    for end in range(MIN_DELTAS + 1, len(targets) + 1):
        if evaluate_relation_gate(
            targets[:end], references[:end], thresholds,
            interaction_radius=RADIUS, horizon=HORIZON,
        ).fired:
            return end
    return None


def gate_comparison(seeds: int = 16) -> list[dict[str, Any]]:
    """Both gates on both encounters, scored on whether they decide *in time*.

    Firing eventually is not enough and is actively misleading here: under the
    advance-only schedule the reference does eventually pass the target and move
    away, so far-field evidence accrues - but around step 34, long after the
    commitment. Measured that way the encounter looks fine. Measured against the
    commit window it is not: replaying the sweep's own nine coupled cells, the
    corrected gate fires at **none** of the commit steps they actually used.
    """

    old = RelationGateThresholds(contrast_from_first_contact=False)
    new = RelationGateThresholds()
    rows = []
    for encounter in ("burst", "probe"):
        for label, thresholds in (("all-history", old), ("post-contact", new)):
            coupled = [first_fire_step(0.0, s, thresholds, encounter) for s in range(seeds)]
            slide = [first_fire_step(1.0, s, thresholds, encounter) for s in range(seeds)]
            in_time = [f is not None and f <= COMMIT_WINDOW_END for f in coupled]
            slide_in_time = [f is not None and f <= COMMIT_WINDOW_END for f in slide]
            timely = [f for f in coupled if f is not None]
            rows.append(
                {
                    "encounter": encounter,
                    "gate": label,
                    "coupled_in_time": float(np.mean(in_time)),
                    "slide_in_time": float(np.mean(slide_in_time)),
                    "median_first_fire": (
                        float(np.median(timely)) if timely else None
                    ),
                    "passes_h3": bool(
                        np.mean(in_time) >= 0.90 and np.mean(slide_in_time) <= 0.10
                    ),
                }
            )
    return rows


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------


def render(
    plateau: list[dict[str, Any]],
    clause: dict[str, dict[str, int]],
    sliding: list[dict[str, float]],
    comparison: list[dict[str, Any]] | None = None,
) -> str:
    conditions = sorted(clause)
    lines = [
        "Relation gate, re-derived from Isaac rather than the CPU proxy",
        "",
        "Fire rate by proximity_contrast threshold (constant-velocity clause at 0.30)",
        f"{'threshold':>10}" + "".join(f"{c:>10}" for c in conditions) + "   separates?",
        "-" * (10 + 10 * len(conditions) + 14),
    ]
    for row in plateau:
        lines.append(
            f"{row['threshold']:>10.2f}"
            + "".join(f"{row['rates'].get(c, 0.0):>10.2f}" for c in conditions)
            + f"   {'yes' if row['separates'] else 'no'}"
        )
    separating = [r["threshold"] for r in plateau if r["separates"]]
    if separating:
        lines.append(
            f"\nSeparating range {min(separating):.2f}-{max(separating):.2f}. "
            "The threshold in use is not doing fitted work."
        )

    lines += [
        "",
        "Does the constant-velocity clause ever reject anything on its own?",
        f"{'condition':<10}{'steps':>8}{'passed contrast':>18}{'then blocked by cv':>21}",
        "-" * 57,
    ]
    for condition in conditions:
        stats = clause[condition]
        lines.append(
            f"{condition:<10}{stats['steps']:>8}{stats['passed_contrast']:>18}"
            f"{stats['blocked_by_constant_velocity']:>21}"
        )
    total_blocked = sum(s["blocked_by_constant_velocity"] for s in clause.values())
    if total_blocked == 0:
        lines.append(
            "\nNever. The sweep provides no evidence the clause works, because no\n"
            "control ever places the gate in the situation it exists for."
        )

    lines += [
        "",
        "Post-contact sliding - the control the sweep does not have",
        "(damping 0 = stops dead, 1 = frictionless slide, which arm C absorbs)",
        "",
        f"{'damping':>8}{'contrast':>11}{'cv_gain':>10}{'per-step':>10}{'per-trial':>11}   required",
        "-" * 72,
    ]
    for row in sliding:
        damping = row["damping"]
        required = "fire" if damping <= 0.5 else ("SILENT" if damping >= 0.9 else "-")
        lines.append(
            f"{damping:>8.2f}{row['median_contrast']:>11.3f}"
            f"{row['median_constant_velocity_gain']:>10.3f}"
            f"{row['fire_rate']:>10.2f}{row['trial_rate']:>11.2f}   {required}"
        )
    lines.append(
        "\nH3 is stated per trial, and the two columns can disagree completely:\n"
        "firing on one step in eight still means firing somewhere in every trial."
    )

    if comparison:
        lines += [
            "",
            f"Both gates, both encounters - decided by the commit window (step {COMMIT_WINDOW_END})",
            f"{'encounter':<10}{'gate':<15}{'coupled':>9}{'slide':>8}{'first fire':>12}   H3",
            "-" * 64,
        ]
        for row in comparison:
            first = row["median_first_fire"]
            lines.append(
                f"{row['encounter']:<10}{row['gate']:<15}{row['coupled_in_time']:>9.2f}"
                f"{row['slide_in_time']:>8.2f}"
                f"{(f'{first:.0f}' if first else 'never'):>12}"
                f"   {'pass' if row['passes_h3'] else 'FAIL'}"
            )
        lines.append(
            "\nThe encounter matters as much as the gate. Without a withdrawal the\n"
            "target is never seen after the reference leaves in time, so a struck\n"
            "target and a sliding one are the same history at the commitment - the\n"
            "corrected gate abstains, and the original claims a relation it has not\n"
            "established. Firing eventually is not the same as firing in time."
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="pilot result directories or JSON files")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    args = parser.parse_args()

    statistics = load_gate_statistics(args.paths)
    if not statistics:
        raise SystemExit("no gate statistics found")

    plateau = threshold_plateau(statistics)
    clause = constant_velocity_clause_work(statistics)
    sliding = [
        gate_under_sliding(d) for d in (0.0, 0.30, 0.50, 0.70, 0.85, 0.95, 1.0)
    ]
    comparison = gate_comparison()

    if args.json:
        print(json.dumps(
            {"plateau": plateau, "clause": clause, "sliding": sliding,
             "comparison": comparison}, indent=2))
    else:
        print(render(plateau, clause, sliding, comparison))


if __name__ == "__main__":
    main()
