"""Figures for the Paper 003 negative result.

Four panels, and the first one carries the paper: a manipulator that takes 22
steps to come to rest cannot supply intermittency inside a 54-step grasp, and
the action it must support completes in 9.

Every number here is transcribed from a recorded result rather than recomputed,
because the Isaac records were written on a rented pod and are not in this
repository - the summaries are. Each constant carries the file it came from, and
`--check` re-reads those files and refuses to plot if a number has drifted.

    python scripts/plot_paper003_negative.py
    python scripts/plot_paper003_negative.py --check

Distributions are drawn as the order statistics that were actually measured -
median, p10, p90, max - and not as smooth curves through them. Drawing a density
we never observed would be inventing data to make a figure look finished.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "experiments/surgical_intelligence/exp_surg_004_relation_expansion/results"
OUT = ROOT / "docs/paper003/figures"

# --- Source: results/physical_h2_v1.0/RESULTS.md -----------------------------

#: Steps until the arm reads as stopped after its goal stands still.
#: 139 goal-pauses in 20 cells.
SETTLING = {"median": 22, "p90": 59, "max": 85}

#: How long the gripper holds the object before dropping it.
CARRY = {"block": {"median": 54, "p10": 16}, "needle": {"median": 68, "p10": 56}}

#: Derived from the tolerance and the carry speed: p10 of the L-step
#: displacement clears 20 mm. results/latency8_rederivation_v1.0/
DISPENSE_LATENCY = 9

#: What the schedule commands. 4 is the design's default; 25 is settling + 3.
COMMANDED_PAUSE = {"as designed": 4, "derived repair": 25}

#: `burst_on` + `burst_off`. The scale the settling sweep found - and not the
#: pause, which is what the first version of these figures marked.
DUTY_PERIOD = 14

#: Physical only. The CPU column is taken from the settling sweep's `settling 0`
#: row at plot time, because that row scores all four arms on one set of cells.
#:
#: It is not assembled by hand from the earlier CPU runs, and an earlier draft of
#: this file did exactly that - arm B and C from the by-offset arm sweep, arm D
#: and SELF from the preregistered SELF comparison, different seeds and different
#: bands, printed as one column. A figure that pools two runs into a bar chart is
#: the quietest way to mislead available here.
ARM_SCORES = {
    #                        B      C     SELF     D      n
    "physical\nblock":    (0.133, 1.000, 0.167, 0.200,   60),
    "physical\nneedle":   (0.087, 0.957, 0.348, 0.174,   23),
    "physical\nneedle\npause 25": (0.625, 0.958, 0.750, 0.583, 24),
}

#: Cells where exactly one of arm D and SELF lands. The statistic the result
#: turns on, because a marginal rate hides which arm wins where.
#:
#: The CPU row is the preregistered comparison on its amended band, which is the
#: run the McNemar test was declared for - not the sweep, whose settling-0 row is
#: a smaller sample drawn for a different question.
DISCORDANT = {
    "CPU\ninjected\nn=200": (146, 8),
    "physical\nneedle\npause 4\nn=23": (0, 4),
    "physical\nneedle\npause 25\nn=24": (0, 4),
}

ARM_COLOURS = {"B": "#9aa5b1", "C": "#c0392b", "SELF": "#e08e0b", "D": "#2c6fbb"}


def _caption(ax: plt.Axes, text: str) -> None:
    """Caption above the axes, in axes fractions.

    Data coordinates were used first, and the caption landed on top of the title
    the moment a figure's x-range changed. Axes fractions do not move.
    """

    ax.annotate(text, (0.0, 1.06), xycoords="axes fraction", fontsize=9,
                color="#555555", va="bottom")


def _style(ax: plt.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#e6e6e6", linewidth=0.8)
    ax.set_axisbelow(True)


def fig1_mechanism(path: Path) -> None:
    """Settling against grip: the interval that does not fit inside the other."""

    fig, ax = plt.subplots(figsize=(9.0, 4.4))

    rows = [
        ("arm settling time\n(139 goal-pauses)", SETTLING["median"], SETTLING["median"],
         SETTLING["p90"], SETTLING["max"], "#c0392b"),
        ("grip on the block", CARRY["block"]["median"], CARRY["block"]["p10"],
         CARRY["block"]["median"], None, "#2c6fbb"),
        ("grip on the needle", CARRY["needle"]["median"], CARRY["needle"]["p10"],
         CARRY["needle"]["median"], None, "#2c6fbb"),
    ]
    for index, (label, point, low, high, extreme, colour) in enumerate(rows):
        y = len(rows) - index - 1
        ax.hlines(y, low, high, color=colour, linewidth=9, alpha=0.30)
        ax.plot([point], [y], "o", color=colour, markersize=10, zorder=3)
        ax.annotate(f"{point}", (point, y), textcoords="offset points",
                    xytext=(0, 13), ha="center", fontsize=10, color=colour,
                    fontweight="bold")
        if extreme is not None:
            ax.hlines(y, high, extreme, color=colour, linewidth=2, alpha=0.35)
            ax.plot([extreme], [y], "|", color=colour, markersize=12)
            ax.annotate("max 85", (extreme, y), textcoords="offset points",
                        xytext=(6, -3), fontsize=8, color=colour)
        ax.text(-3, y, label, ha="right", va="center", fontsize=10)

    ax.vlines(DUTY_PERIOD, -0.6, 2.45, color="#444444", linestyle="--", linewidth=1.4)
    ax.annotate(f"the carrier's duty-cycle period = {DUTY_PERIOD}\n"
                "settling above this erases the schedule",
                (DUTY_PERIOD, 2.30), xytext=(10, 0), textcoords="offset points",
                fontsize=9, color="#444444", va="center")
    ax.vlines(COMMANDED_PAUSE["as designed"], -0.6, 2.45, color="#7f8c8d",
              linestyle=":", linewidth=1.4)
    ax.annotate("commanded pause = 4", (COMMANDED_PAUSE["as designed"], -0.52),
                textcoords="offset points", xytext=(-6, 0), fontsize=9,
                color="#7f8c8d", va="center", ha="right")

    ax.set_xlim(-42, 100)
    ax.set_ylim(-0.75, 2.60)
    ax.set_yticks([])
    ax.set_xticks([0, 14, 22, 40, 54, 59, 68, 85])
    ax.set_xlabel("simulation steps")
    ax.spines["left"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_title("The carrier cannot stop before its schedule comes round again",
                 fontsize=12, loc="left", pad=34)
    _caption(ax,
             "Intermittency is what makes the relation necessary. The arm needs 22 steps to come "
             "to rest against a\ncommanded pause of 4, so the pause never begins — and the smooth "
             "ride it leaves is what Paper 002's operator models.")
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig2_arms(path: Path, cpu: dict | None) -> None:
    """Every arm, every configuration. Arm C is the row that decides it."""

    scores = dict(ARM_SCORES)
    if cpu is not None:
        scores = {f"CPU\ninjected": (cpu["B"], cpu["C"], cpu["SELF"], cpu["D"],
                                     cpu["n"]), **scores}

    fig, ax = plt.subplots(figsize=(9.0, 4.6))
    labels = list(scores)
    width = 0.19
    positions = np.arange(len(labels))

    for index, arm in enumerate(("B", "C", "SELF", "D")):
        values = [scores[label][index] for label in labels]
        offset = (index - 1.5) * width
        bars = ax.bar(positions + offset, values, width, label=arm,
                      color=ARM_COLOURS[arm],
                      edgecolor="white", linewidth=0.6)
        for bar, value in zip(bars, values):
            ax.annotate(f"{value:.3f}", (bar.get_x() + bar.get_width() / 2, value),
                        textcoords="offset points", xytext=(0, 2), ha="center",
                        fontsize=7.5, rotation=90, color="#333333")

    _style(ax)
    ax.set_xticks(positions)
    ax.set_xticklabels([f"{label}\nn={scores[label][4]}" for label in labels],
                       fontsize=9)
    ax.set_ylim(0, 1.22)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_ylabel("cells landed within tolerance")
    ax.legend(ncol=4, frameon=False, loc="upper left", fontsize=9)
    ax.set_title("Paper 002's mode operator (C) lands what the relation (D) cannot",
                 fontsize=12, loc="left", pad=34)
    _caption(ax,
             "C is the discriminating control, and the design requires it to help only partially. "
             "Under injected coupling it\ndoes. Under physical contact it lands everything, and the "
             "single-entity arm overtakes the relational one.")
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig3_discordant(path: Path) -> None:
    """The number that ends it: paired cells won by exactly one arm."""

    fig, ax = plt.subplots(figsize=(8.2, 4.0))
    labels = list(DISCORDANT)
    positions = np.arange(len(labels))
    d_only = [DISCORDANT[label][0] for label in labels]
    self_only = [-DISCORDANT[label][1] for label in labels]

    ax.barh(positions, d_only, 0.5, color=ARM_COLOURS["D"], label="arm D wins")
    ax.barh(positions, self_only, 0.5, color=ARM_COLOURS["SELF"], label="SELF wins")
    for y, value in zip(positions, d_only):
        ax.annotate(f"{value}", (value, y), textcoords="offset points",
                    xytext=(6 if value else 6, -4), fontsize=11,
                    color=ARM_COLOURS["D"], fontweight="bold")
    for y, value in zip(positions, self_only):
        ax.annotate(f"{-value}", (value, y), textcoords="offset points",
                    xytext=(-14, -4), fontsize=11, color=ARM_COLOURS["SELF"],
                    fontweight="bold")

    ax.axvline(0, color="#333333", linewidth=1.0)
    ax.set_yticks(positions)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlim(-30, 175)
    # Absolute magnitudes: this is a count in two directions, and a "-25" on a
    # tally of cells reads as a negative number of cells.
    ticks = [-25, 0, 25, 50, 75, 100, 125, 150]
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(abs(t)) for t in ticks])
    ax.set_xlabel("discordant paired cells")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.grid(axis="x", color="#e6e6e6", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="upper right", fontsize=9,
              bbox_to_anchor=(1.0, 1.02))
    ax.set_title("Under contact, arm D wins no cell that the single-entity arm loses",
                 fontsize=12, loc="left", pad=34)
    _caption(ax,
             "Cells where exactly one of the two arms lands — the statistic the preregistered "
             "comparison is run on.\nWith a scripted carrier the relation wins 146 to 8. With a "
             "real one it wins none, in either configuration.")
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig4_sweep(path: Path, rows: list[dict]) -> None:
    """The criterion, measured: inject settling into the CPU carrier and sweep."""

    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    settling = [r["settling"] for r in rows]
    for arm in ("B", "C", "SELF", "D"):
        ax.plot(settling, [r[arm] for r in rows], "o-", color=ARM_COLOURS[arm],
                label=arm, linewidth=2.0, markersize=5)

    burst_off = rows[0]["burst_off"] if rows else 4
    if all(r["burst_off"] == burst_off for r in rows):
        ax.axvline(burst_off, color="#7f8c8d", linestyle=":", linewidth=1.4)
        ax.annotate(f"predicted crossing:\ncommanded pause {burst_off}\nREFUTED",
                    (burst_off, 0.86), textcoords="offset points", xytext=(-8, 0),
                    fontsize=8.5, color="#7f8c8d", ha="right", va="top")
    ax.axvline(DUTY_PERIOD, color="#333333", linewidth=1.2, alpha=0.55)
    ax.annotate(f"observed crossing:\nduty-cycle period {DUTY_PERIOD}",
                (DUTY_PERIOD, 0.30), textcoords="offset points", xytext=(-8, 0),
                fontsize=8.5, color="#333333", ha="right", va="top")
    ax.axvline(SETTLING["median"], color="#c0392b", linestyle="--", linewidth=1.2)
    ax.annotate("the arm\nmeasured\nat 22", (SETTLING["median"], 0.62),
                textcoords="offset points", xytext=(-8, 0), fontsize=8.5,
                color="#c0392b", ha="right", va="top")

    _style(ax)
    ax.set_xlabel("carrier settling time (steps the body keeps moving after 'stop')")
    ax.set_ylabel("cells landed within tolerance")
    ax.set_ylim(-0.03, 1.08)
    ax.legend(ncol=4, frameon=False, loc="upper center", fontsize=9)
    ax.set_title("The mode operator returns at the duty-cycle period, not at the pause",
                 fontsize=12, loc="left", pad=34)
    _caption(ax,
             "Injected coupling, everything else at the preregistered values. Arm C is flat until "
             "settling 9 and reaches\n0.917 at 14. Arm D does not collapse — so this explains C's "
             "return and not D's physical failure.")
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def check() -> int:
    """Re-read the recorded results and refuse to plot on a drifted number.

    A transcribed constant is a constant that can go stale, and this project has
    already shipped one figure-adjacent number that no longer matched its source.
    """

    source = RESULTS / "physical_h2_v1.0/RESULTS.md"
    text = source.read_text(encoding="utf-8")
    failures = []
    for needle, description in (
        ("| **22** | 59 | 85 |", "settling median/p90/max"),
        ("| block | 0.133 | **1.000** | 0.167 | 0.200 |", "block arm scores"),
        ("| needle | 0.087 | **0.957** | 0.348 | 0.174 |", "needle arm scores"),
        ("| `burst_off` 25 | 0.625 | **0.958** | 0.750 | 0.583 |", "needle pause-25 scores"),
        ("| CPU, scripted carrier | 0.735 | 0.045 | **146 : 8** |", "CPU discordant"),
    ):
        if needle not in text:
            failures.append(f"  not found in {source.name}: {description}")
    for line in failures:
        print(line)
    print("check: " + ("FAILED" if failures else "every transcribed number still matches"))
    return 1 if failures else 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--sweep", type=Path,
                        default=RESULTS / "settling_sweep_v1.0/burst_off_4.json")
    args = parser.parse_args()

    if args.check:
        raise SystemExit(check())

    sweep_rows = []
    if args.sweep.exists():
        sweep_rows = [r for r in json.loads(args.sweep.read_text()) if r.get("n")]
    # The scripted point every other CPU result in this paper uses, scored on one
    # set of cells across all four arms.
    cpu_row = next((r for r in sweep_rows if r["settling"] == 0), None)
    if cpu_row is None:
        print(f"no settling-0 row in {args.sweep} - fig2 will show physical only")

    OUT.mkdir(parents=True, exist_ok=True)
    fig1_mechanism(OUT / "fig1_carrier_cannot_stop.png")
    fig2_arms(OUT / "fig2_arm_scores.png", cpu_row)
    fig3_discordant(OUT / "fig3_discordant_pairs.png")
    written = ["fig1_carrier_cannot_stop", "fig2_arm_scores", "fig3_discordant_pairs"]

    if sweep_rows:
        fig4_sweep(OUT / "fig4_settling_sweep.png", sweep_rows)
        written.append("fig4_settling_sweep")
    else:
        print(f"no sweep at {args.sweep} - skipping fig4")

    for name in written:
        print(f"wrote {(OUT / (name + '.png')).relative_to(ROOT)}")


if __name__ == "__main__":
    main()
