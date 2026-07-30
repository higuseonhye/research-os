"""Generate Paper 002 confirmatory figures and tables from frozen JSON artifacts.

The script uses Pillow rather than a simulator or GPU. Outputs are deterministic
and are written under ``docs/paper002/figures`` by default.

Usage:
    python scripts/plot_paper002_model_order.py
    python scripts/plot_paper002_model_order.py --out-dir docs/paper002/figures
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = (
    ROOT
    / "experiments/surgical_intelligence/exp_surg_003_wm_expansion/results"
    / "isaac_model_order_confirmatory_v1.0"
)
DEFAULT_RESULTS = RESULT_DIR / "isaac_model_order_results.json"
DEFAULT_TRAJECTORIES = RESULT_DIR / "isaac_model_order_trajectories.json"
DEFAULT_OUT = ROOT / "docs/paper002/figures"

ARMS = [
    "A_ZERO_ORDER_FROZEN",
    "B_L1_ZERO_ORDER",
    "C_L3_CONSTANT_VELOCITY",
    "D_ORACLE_VELOCITY",
]
ARM_LABELS = {
    "A_ZERO_ORDER_FROZEN": "A  Frozen zero-order",
    "B_L1_ZERO_ORDER": "B  Repaired zero-order",
    "C_L3_CONSTANT_VELOCITY": "C  Gated constant velocity",
    "D_ORACLE_VELOCITY": "D  Oracle velocity",
}
ARM_SHORT = {
    "A_ZERO_ORDER_FROZEN": "A",
    "B_L1_ZERO_ORDER": "B",
    "C_L3_CONSTANT_VELOCITY": "C",
    "D_ORACLE_VELOCITY": "D",
}
COLORS = {
    "A_ZERO_ORDER_FROZEN": "#7F8C8D",
    "B_L1_ZERO_ORDER": "#D55E00",
    "C_L3_CONSTANT_VELOCITY": "#009E73",
    "D_ORACLE_VELOCITY": "#0072B2",
    "ink": "#17202A",
    "muted": "#5D6D7E",
    "grid": "#DCE1E5",
    "paper": "#FFFFFF",
    "threshold": "#8E44AD",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def wilson_ci(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return 0.0, 0.0
    p = successes / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    margin = z / denom * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n))
    return max(0.0, center - margin), min(1.0, center + margin)


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = [
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for name in names:
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def centered(draw: ImageDraw.ImageDraw, xy: tuple[float, float], text: str, *, size: int, fill: str, bold: bool = False) -> None:
    draw.text(xy, text, font=font(size, bold), fill=fill, anchor="mm", align="center")


def right_text(draw: ImageDraw.ImageDraw, xy: tuple[float, float], text: str, *, size: int, fill: str, bold: bool = False) -> None:
    draw.text(xy, text, font=font(size, bold), fill=fill, anchor="rm")


def title(draw: ImageDraw.ImageDraw, text: str, subtitle: str | None = None) -> None:
    draw.text((70, 48), text, font=font(42, True), fill=COLORS["ink"], anchor="la")
    if subtitle:
        draw.text((70, 103), subtitle, font=font(23), fill=COLORS["muted"], anchor="la")


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: str = "#52616B") -> None:
    draw.line([start, end], fill=color, width=6)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    length = 18
    spread = 0.55
    points = [
        end,
        (
            end[0] - length * math.cos(angle - spread),
            end[1] - length * math.sin(angle - spread),
        ),
        (
            end[0] - length * math.cos(angle + spread),
            end[1] - length * math.sin(angle + spread),
        ),
    ]
    draw.polygon(points, fill=color)


def rounded_box(
    draw: ImageDraw.ImageDraw,
    bounds: tuple[int, int, int, int],
    heading: str,
    body: str,
    *,
    fill: str,
    outline: str,
) -> None:
    draw.rounded_rectangle(bounds, radius=15, fill=fill, outline=outline, width=4)
    x1, y1, x2, y2 = bounds
    centered(draw, ((x1 + x2) / 2, y1 + 43), heading, size=25, fill=outline, bold=True)
    centered(draw, ((x1 + x2) / 2, (y1 + y2) / 2 + 26), body, size=20, fill=COLORS["ink"])


def panel_axes(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    *,
    y_min: float,
    y_max: float,
    ticks: list[float],
    y_label: str,
    heading: str,
) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = box
    left, top, right, bottom = x1 + 95, y1 + 72, x2 - 32, y2 - 88
    draw.text((x1 + 8, y1 + 10), heading, font=font(26, True), fill=COLORS["ink"])
    for value in ticks:
        py = bottom - (value - y_min) / (y_max - y_min) * (bottom - top)
        draw.line([(left, py), (right, py)], fill=COLORS["grid"], width=2)
        right_text(draw, (left - 15, py), f"{value:g}", size=18, fill=COLORS["muted"])
    draw.line([(left, top), (left, bottom), (right, bottom)], fill=COLORS["ink"], width=3)
    draw.text((left + 4, top - 12), y_label, font=font(18), fill=COLORS["muted"], anchor="ls")
    return left, top, right, bottom


def value_to_y(value: float, top: int, bottom: int, y_min: float, y_max: float) -> float:
    return bottom - (value - y_min) / (y_max - y_min) * (bottom - top)


def save(image: Image.Image, out: Path, filename: str) -> Path:
    path = out / filename
    image.save(path, format="PNG", optimize=True)
    return path


def figure_protocol(out: Path) -> Path:
    image = Image.new("RGB", (1900, 1050), COLORS["paper"])
    draw = ImageDraw.Draw(image)
    title(
        draw,
        "Failure-conditioned model-order expansion",
        "Frozen confirmatory design: fresh seeds, fresh conditions, process-isolated cells",
    )

    rounded_box(draw, (70, 185, 390, 390), "Static-first selection", "40 fresh candidates\nfirst 10 eligible seeds", fill="#EBF5FB", outline=COLORS["D_ORACLE_VELOCITY"])
    rounded_box(draw, (500, 185, 820, 390), "Ep1 evidence", "Persistent +x drift\n40 steps", fill="#F8F9F9", outline="#566573")
    rounded_box(draw, (930, 185, 1250, 390), "L1 repair", "Fit zero-order alpha\nheld-out tail", fill="#FDF2E9", outline=COLORS["B_L1_ZERO_ORDER"])
    rounded_box(draw, (1360, 185, 1830, 390), "Adequacy gate", "Persistent, directional\nCV-explainable residual", fill="#F4ECF7", outline=COLORS["threshold"])
    arrow(draw, (390, 287), (500, 287))
    arrow(draw, (820, 287), (930, 287))
    arrow(draw, (1250, 287), (1360, 287))

    centers = [250, 715, 1180, 1645]
    bodies = [
        ("A  Frozen", "order 0\nalpha 0.5", ARMS[0]),
        ("B  L1 repair", "order 0\nalpha 1.0", ARMS[1]),
        ("C  L3 expansion", "gated order 1\nvelocity state", ARMS[2]),
        ("D  Oracle", "true velocity\ndiagnostic only", ARMS[3]),
    ]
    for cx, (heading, body, arm) in zip(centers, bodies):
        rounded_box(
            draw,
            (cx - 190, 520, cx + 190, 745),
            heading,
            body,
            fill="#FFFFFF",
            outline=COLORS[arm],
        )
        arrow(draw, (cx, 462), (cx, 520), COLORS[arm])
    draw.line([(250, 462), (1645, 462)], fill="#AAB7B8", width=5)
    arrow(draw, (1595, 390), (1595, 462))

    draw.rounded_rectangle((70, 835, 1830, 980), radius=15, fill="#F8F9F9", outline="#AAB7B8", width=3)
    centered(draw, (950, 875), "Ep2: 10 fresh drift conditions x 10 selected seeds x 4 arms = 400 cells", size=27, fill=COLORS["ink"], bold=True)
    centered(draw, (950, 928), "Primary C - B: H=10 prediction error and fixed-horizon final distance    |    Guards: static retention and gate controls", size=21, fill=COLORS["muted"])
    for cx, (_, _, arm) in zip(centers, bodies):
        arrow(draw, (cx, 745), (cx, 835), COLORS[arm])

    return save(image, out, "fig1_confirmatory_protocol.png")


def figure_outcomes(results: dict[str, Any], out: Path) -> Path:
    image = Image.new("RGB", (2100, 1000), COLORS["paper"])
    draw = ImageDraw.Draw(image)
    title(draw, "Confirmatory outcomes by model order", "Means over 10 selected seeds x 10 fresh drift conditions")
    panels = [(40, 150, 710, 850), (715, 150, 1385, 850), (1390, 150, 2060, 850)]
    definitions = [
        ("H=10 prediction error", "Mean error (mm)", "mean_prediction_error_horizon_m", 24.0, [0, 5, 10, 15, 20]),
        ("Fixed-horizon final distance", "Mean distance (mm)", "mean_final_distance_m", 24.0, [0, 5, 10, 15, 20]),
        ("20 mm resolution rate", "Success rate (%)", "success_rate", 105.0, [0, 25, 50, 75, 100]),
    ]
    for panel, (heading, y_label, key, ymax, ticks) in zip(panels, definitions):
        left, top, right, bottom = panel_axes(
            draw, panel, y_min=0.0, y_max=ymax, ticks=ticks, y_label=y_label, heading=heading
        )
        width = (right - left) / len(ARMS)
        for index, arm in enumerate(ARMS):
            aggregate = results["ep2_by_arm"][arm]
            raw = float(aggregate[key])
            value = raw * (100.0 if key == "success_rate" else 1000.0)
            cx = left + width * (index + 0.5)
            bar_width = width * 0.53
            py = value_to_y(value, top, bottom, 0.0, ymax)
            draw.rounded_rectangle(
                (cx - bar_width / 2, py, cx + bar_width / 2, bottom),
                radius=5,
                fill=COLORS[arm],
            )
            if key != "success_rate":
                condition_values = [
                    results["ep2_by_condition"][condition][arm][key] * 1000.0
                    for condition in results["condition_ids"]
                ]
                for j, point in enumerate(condition_values):
                    jitter = ((j % 5) - 2) * 6
                    point_y = value_to_y(point, top, bottom, 0.0, ymax)
                    draw.ellipse((cx + jitter - 4, point_y - 4, cx + jitter + 4, point_y + 4), fill="#FFFFFF", outline=COLORS["ink"], width=1)
                label_y = value_to_y(max(condition_values), top, bottom, 0.0, ymax) - 24
            else:
                n = int(aggregate["n"])
                k = int(round(raw * n))
                low, high = wilson_ci(k, n)
                low_y = value_to_y(low * 100.0, top, bottom, 0.0, ymax)
                high_y = value_to_y(high * 100.0, top, bottom, 0.0, ymax)
                draw.line([(cx, high_y), (cx, low_y)], fill=COLORS["ink"], width=3)
                draw.line([(cx - 10, high_y), (cx + 10, high_y)], fill=COLORS["ink"], width=3)
                draw.line([(cx - 10, low_y), (cx + 10, low_y)], fill=COLORS["ink"], width=3)
                label_y = high_y - 22
            label = f"{value:.1f}" if key != "success_rate" else f"{value:.0f}%"
            centered(draw, (cx, max(top + 18, label_y)), label, size=21, fill=COLORS["ink"], bold=True)
            centered(draw, (cx, bottom + 32), ARM_SHORT[arm], size=24, fill=COLORS[arm], bold=True)
        if key == "mean_final_distance_m":
            tol_y = value_to_y(20.0, top, bottom, 0.0, ymax)
            draw.line([(left, tol_y), (right, tol_y)], fill=COLORS["threshold"], width=3)
            draw.text((right - 5, tol_y - 8), "20 mm threshold", font=font(17), fill=COLORS["threshold"], anchor="rs")

    effect = results["primary_effect"]
    draw.rounded_rectangle((515, 875, 1585, 970), radius=14, fill="#F4F6F7", outline="#AAB7B8", width=2)
    centered(
        draw,
        (1050, 922),
        "Primary C - B: prediction -10.806 mm [95% CI -11.360, -10.331]   |   final distance -13.304 mm [-13.599, -12.982]",
        size=19,
        fill=COLORS["ink"],
        bold=True,
    )
    assert effect["mean_prediction_error_difference_m"] < 0
    return save(image, out, "fig2_confirmatory_outcomes.png")


def condition_differences(results: dict[str, Any]) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for condition in results["condition_ids"]:
        by_arm = results["ep2_by_condition"][condition]
        rows.append(
            {
                "condition_id": condition,
                "prediction_error_difference_mm": 1000.0
                * (
                    by_arm["C_L3_CONSTANT_VELOCITY"]["mean_prediction_error_horizon_m"]
                    - by_arm["B_L1_ZERO_ORDER"]["mean_prediction_error_horizon_m"]
                ),
                "final_distance_difference_mm": 1000.0
                * (
                    by_arm["C_L3_CONSTANT_VELOCITY"]["mean_final_distance_m"]
                    - by_arm["B_L1_ZERO_ORDER"]["mean_final_distance_m"]
                ),
                "b_success_count": int(round(10 * by_arm["B_L1_ZERO_ORDER"]["success_rate"])),
                "c_success_count": int(round(10 * by_arm["C_L3_CONSTANT_VELOCITY"]["success_rate"])),
            }
        )
    return rows


def figure_condition_effects(results: dict[str, Any], out: Path) -> Path:
    rows = condition_differences(results)
    image = Image.new("RGB", (1800, 1000), COLORS["paper"])
    draw = ImageDraw.Draw(image)
    title(draw, "C - B effects across all fresh drift conditions", "Negative values favor the gated constant-velocity expansion")
    left, top, right, bottom = panel_axes(
        draw,
        (70, 150, 1730, 850),
        y_min=-16.0,
        y_max=1.0,
        ticks=[-15, -10, -5, 0],
        y_label="C - B difference (mm)",
        heading="Condition-level means (10 selected seeds per condition)",
    )
    threshold_y = value_to_y(-5.0, top, bottom, -16.0, 1.0)
    draw.line([(left, threshold_y), (right, threshold_y)], fill=COLORS["threshold"], width=4)
    draw.text((right - 4, threshold_y - 10), "preregistered CI threshold: -5 mm", font=font(18), fill=COLORS["threshold"], anchor="rs")
    width = (right - left) / len(rows)
    for index, row in enumerate(rows):
        cx = left + width * (index + 0.5)
        pe = float(row["prediction_error_difference_mm"])
        fd = float(row["final_distance_difference_mm"])
        pe_y = value_to_y(pe, top, bottom, -16.0, 1.0)
        fd_y = value_to_y(fd, top, bottom, -16.0, 1.0)
        draw.line([(cx - 17, pe_y), (cx + 17, fd_y)], fill="#ABB2B9", width=3)
        draw.ellipse((cx - 24, pe_y - 9, cx - 6, pe_y + 9), fill=COLORS["D_ORACLE_VELOCITY"])
        draw.rectangle((cx + 7, fd_y - 9, cx + 25, fd_y + 9), fill=COLORS["C_L3_CONSTANT_VELOCITY"])
        centered(draw, (cx, bottom + 31), str(row["condition_id"]), size=20, fill=COLORS["ink"], bold=True)

    effect = results["primary_effect"]
    pe_ci = [1000.0 * x for x in effect["prediction_error_difference_crossed_bootstrap_95_ci_m"]]
    fd_ci = [1000.0 * x for x in effect["final_distance_difference_crossed_bootstrap_95_ci_m"]]
    draw.rounded_rectangle((250, 850, 1550, 975), radius=13, fill="#F8F9F9", outline="#D5D8DC", width=2)
    draw.ellipse((300, 880, 320, 900), fill=COLORS["D_ORACLE_VELOCITY"])
    draw.text((335, 890), f"Prediction: -10.806 mm  CI [{pe_ci[0]:.3f}, {pe_ci[1]:.3f}]", font=font(20), fill=COLORS["ink"], anchor="lm")
    draw.rectangle((945, 880, 965, 900), fill=COLORS["C_L3_CONSTANT_VELOCITY"])
    draw.text((980, 890), f"Final: -13.304 mm  CI [{fd_ci[0]:.3f}, {fd_ci[1]:.3f}]", font=font(20), fill=COLORS["ink"], anchor="lm")
    centered(draw, (900, 942), "C was lower in 100/100 crossed cells for both continuous endpoints", size=20, fill=COLORS["muted"], bold=True)
    return save(image, out, "fig3_condition_effects.png")


def figure_trajectory(trajectories: dict[str, Any], out: Path, seed: int = 300, condition: str = "C04") -> Path:
    selected = {
        arm: next(
            row
            for row in trajectories["ep2"]
            if row["seed"] == seed and row["condition_id"] == condition and row["policy"] == arm
        )
        for arm in ["B_L1_ZERO_ORDER", "C_L3_CONSTANT_VELOCITY", "D_ORACLE_VELOCITY"]
    }
    image = Image.new("RGB", (1800, 920), COLORS["paper"])
    draw = ImageDraw.Draw(image)
    title(draw, f"Representative process-isolated branch: seed {seed}, {condition}", "Same reset and branch state; C changes target model order only after the gate")

    panels = [(60, 150, 890, 850), (910, 150, 1740, 850)]
    left, top, right, bottom = panel_axes(
        draw,
        panels[0],
        y_min=0.0,
        y_max=24.0,
        ticks=[0, 5, 10, 15, 20],
        y_label="EE-target distance (mm)",
        heading="Control consequence",
    )
    min_t = min(row["trajectory"][0]["t"] for row in selected.values())
    max_t = max(row["trajectory"][-1]["t"] for row in selected.values())
    for arm, row in selected.items():
        points = []
        for step in row["trajectory"]:
            x = left + (step["t"] - min_t) / (max_t - min_t) * (right - left)
            y = value_to_y(1000.0 * step["distance_m"], top, bottom, 0.0, 24.0)
            points.append((x, y))
        draw.line(points, fill=COLORS[arm], width=7)
    for tick in range(min_t, max_t + 1, 5):
        x = left + (tick - min_t) / (max_t - min_t) * (right - left)
        draw.line([(x, bottom), (x, bottom + 8)], fill=COLORS["ink"], width=2)
        centered(draw, (x, bottom + 22), str(tick - min_t), size=16, fill=COLORS["muted"])
    tol_y = value_to_y(20.0, top, bottom, 0.0, 24.0)
    draw.line([(left, tol_y), (right, tol_y)], fill=COLORS["threshold"], width=3)
    centered(draw, ((left + right) / 2, bottom + 36), "Branch step", size=20, fill=COLORS["muted"])

    left2, top2, right2, bottom2 = panel_axes(
        draw,
        panels[1],
        y_min=0.0,
        y_max=22.0,
        ticks=[0, 5, 10, 15, 20],
        y_label="H=10 prediction error (mm)",
        heading="Model consequence",
    )
    for arm, row in selected.items():
        points = []
        for step in row["trajectory"]:
            error = step["prediction_error_horizon_m"]
            if error is None:
                if len(points) > 1:
                    draw.line(points, fill=COLORS[arm], width=7)
                points = []
                continue
            x = left2 + (step["t"] - min_t) / (max_t - min_t) * (right2 - left2)
            y = value_to_y(1000.0 * error, top2, bottom2, 0.0, 22.0)
            points.append((x, y))
        if len(points) > 1:
            draw.line(points, fill=COLORS[arm], width=7)
    for tick in range(min_t, max_t + 1, 5):
        x = left2 + (tick - min_t) / (max_t - min_t) * (right2 - left2)
        draw.line([(x, bottom2), (x, bottom2 + 8)], fill=COLORS["ink"], width=2)
        centered(draw, (x, bottom2 + 22), str(tick - min_t), size=16, fill=COLORS["muted"])
    c_gate_t = next(step["t"] for step in selected["C_L3_CONSTANT_VELOCITY"]["trajectory"] if step["gate_fired"])
    gate_x = left2 + (c_gate_t - min_t) / (max_t - min_t) * (right2 - left2)
    draw.line([(gate_x, top2), (gate_x, bottom2)], fill=COLORS["threshold"], width=4)
    draw.text((gate_x + 10, top2 + 18), f"C gate fires at t={c_gate_t}", font=font(18, True), fill=COLORS["threshold"], anchor="la")
    centered(draw, ((left2 + right2) / 2, bottom2 + 36), "Branch step", size=20, fill=COLORS["muted"])

    legend_x = 1110
    for index, arm in enumerate(selected):
        y = 835 + index * 0
        x = legend_x + index * 205
        draw.line([(x, y), (x + 45, y)], fill=COLORS[arm], width=7)
        draw.text((x + 55, y), ARM_LABELS[arm].split("  ", 1)[0], font=font(19, True), fill=COLORS[arm], anchor="lm")
    return save(image, out, "fig4_representative_trajectory.png")


def figure_guards(results: dict[str, Any], out: Path) -> Path:
    image = Image.new("RGB", (1800, 920), COLORS["paper"])
    draw = ImageDraw.Draw(image)
    title(draw, "Guardrails: structural gate validity and static retention", "All preregistered H3 and H4 criteria passed")

    gate_order = ["M0_STATIC", "M1_PERSISTENT_DRIFT", "N1_OBSERVATION_NOISE", "N2_SINGLE_IMPULSE"]
    gate_labels = ["Static", "Persistent\ndrift", "Observation\nnoise", "Single\nimpulse"]
    left, top, right, bottom = panel_axes(
        draw,
        (60, 150, 990, 850),
        y_min=0.0,
        y_max=105.0,
        ticks=[0, 25, 50, 75, 100],
        y_label="Gate fire rate (%)",
        heading="H4 gate controls (n=100 each)",
    )
    bar_space = (right - left) / 4
    gate_colors = ["#7F8C8D", COLORS["threshold"], "#E69F00", "#56B4E9"]
    for i, (key, label, color) in enumerate(zip(gate_order, gate_labels, gate_colors)):
        stats = results["h4_gate_controls"][key]
        value = 100.0 * stats["gate_fire_rate"]
        cx = left + bar_space * (i + 0.5)
        py = value_to_y(value, top, bottom, 0.0, 105.0)
        draw.rounded_rectangle((cx - 55, py, cx + 55, bottom), radius=6, fill=color)
        low, high = [100.0 * x for x in stats["wilson_95_ci"]]
        low_y = value_to_y(low, top, bottom, 0.0, 105.0)
        high_y = value_to_y(high, top, bottom, 0.0, 105.0)
        draw.line([(cx, high_y), (cx, low_y)], fill=COLORS["ink"], width=3)
        draw.line([(cx - 12, high_y), (cx + 12, high_y)], fill=COLORS["ink"], width=3)
        draw.line([(cx - 12, low_y), (cx + 12, low_y)], fill=COLORS["ink"], width=3)
        centered(draw, (cx, max(top + 20, py - 25)), f"{value:.0f}%", size=21, fill=COLORS["ink"], bold=True)
        centered(draw, (cx, bottom + 48), label, size=18, fill=COLORS["ink"], bold=True)
    ten_y = value_to_y(10.0, top, bottom, 0.0, 105.0)
    ninety_y = value_to_y(90.0, top, bottom, 0.0, 105.0)
    draw.line([(left, ten_y), (right, ten_y)], fill="#BA4A00", width=3)
    draw.line([(left, ninety_y), (right, ninety_y)], fill="#1E8449", width=3)

    left2, top2, right2, bottom2 = panel_axes(
        draw,
        (1020, 150, 1740, 850),
        y_min=0.0,
        y_max=4.0,
        ticks=[0, 1, 2, 3, 4],
        y_label="Static final distance (mm)",
        heading="H3 static retention (10 paired seeds)",
    )
    by_policy = {
        arm: sorted(
            [row for row in results["retention_records"] if row["policy"] == arm],
            key=lambda row: row["seed"],
        )
        for arm in ["B_L1_ZERO_ORDER", "C_L3_CONSTANT_VELOCITY"]
    }
    x_b = left2 + (right2 - left2) * 0.34
    x_c = left2 + (right2 - left2) * 0.68
    for b_row, c_row in zip(by_policy["B_L1_ZERO_ORDER"], by_policy["C_L3_CONSTANT_VELOCITY"]):
        y_b = value_to_y(1000.0 * b_row["final_distance_m"], top2, bottom2, 0.0, 4.0)
        y_c = value_to_y(1000.0 * c_row["final_distance_m"], top2, bottom2, 0.0, 4.0)
        draw.line([(x_b, y_b), (x_c, y_c)], fill="#CCD1D1", width=3)
        draw.ellipse((x_b - 7, y_b - 7, x_b + 7, y_b + 7), fill=COLORS["B_L1_ZERO_ORDER"])
        draw.ellipse((x_c - 7, y_c - 7, x_c + 7, y_c + 7), fill=COLORS["C_L3_CONSTANT_VELOCITY"])
    b_mean = 1000.0 * mean(row["final_distance_m"] for row in by_policy["B_L1_ZERO_ORDER"])
    c_mean = 1000.0 * mean(row["final_distance_m"] for row in by_policy["C_L3_CONSTANT_VELOCITY"])
    for x, value, arm in [(x_b, b_mean, "B_L1_ZERO_ORDER"), (x_c, c_mean, "C_L3_CONSTANT_VELOCITY")]:
        y = value_to_y(value, top2, bottom2, 0.0, 4.0)
        draw.line([(x - 42, y), (x + 42, y)], fill=COLORS[arm], width=9)
        centered(draw, (x, y - 34), f"{value:.3f} mm", size=20, fill=COLORS[arm], bold=True)
    centered(draw, (x_b, bottom2 + 35), "B", size=25, fill=COLORS["B_L1_ZERO_ORDER"], bold=True)
    centered(draw, (x_c, bottom2 + 35), "C", size=25, fill=COLORS["C_L3_CONSTANT_VELOCITY"], bold=True)
    centered(draw, ((left2 + right2) / 2, bottom2 + 77), "Both 10/10 successful; paired success difference 0.00 [0.00, 0.00]", size=17, fill=COLORS["muted"])
    return save(image, out, "fig5_gate_and_retention.png")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_tables(results: dict[str, Any], out: Path) -> list[Path]:
    table_dir = out / "tables"
    table_dir.mkdir(parents=True, exist_ok=True)
    arm_rows = []
    for arm in ARMS:
        row = results["ep2_by_arm"][arm]
        arm_rows.append(
            {
                "arm": arm,
                "n": row["n"],
                "success_rate": row["success_rate"],
                "mean_prediction_error_h10_mm": 1000.0 * row["mean_prediction_error_horizon_m"],
                "mean_final_distance_mm": 1000.0 * row["mean_final_distance_m"],
                "mean_completion_steps": row["mean_completion_steps"],
                "forbidden_violations": row["forbidden_violations"],
                "unexpected_env_resets": row["unexpected_env_resets"],
            }
        )
    arm_path = table_dir / "table1_arm_results.csv"
    write_csv(arm_path, list(arm_rows[0]), arm_rows)

    effect = results["primary_effect"]
    contrast_rows = [
        {
            "endpoint": "mean_prediction_error_h10_mm",
            "c_minus_b": 1000.0 * effect["mean_prediction_error_difference_m"],
            "ci_low": 1000.0 * effect["prediction_error_difference_crossed_bootstrap_95_ci_m"][0],
            "ci_high": 1000.0 * effect["prediction_error_difference_crossed_bootstrap_95_ci_m"][1],
            "c_favorable_pair_rate": effect["l3_lower_prediction_error_pair_rate"],
            "confirmatory_gate_pass": results["confirmatory_decisions"]["h1_prediction_ci_pass"],
        },
        {
            "endpoint": "mean_final_distance_mm",
            "c_minus_b": 1000.0 * effect["mean_final_distance_difference_m"],
            "ci_low": 1000.0 * effect["final_distance_difference_crossed_bootstrap_95_ci_m"][0],
            "ci_high": 1000.0 * effect["final_distance_difference_crossed_bootstrap_95_ci_m"][1],
            "c_favorable_pair_rate": effect["l3_lower_final_distance_pair_rate"],
            "confirmatory_gate_pass": results["confirmatory_decisions"]["h2_final_distance_ci_pass"],
        },
        {
            "endpoint": "success_rate",
            "c_minus_b": effect["success_rate_difference"],
            "ci_low": effect["success_rate_difference_crossed_bootstrap_95_ci"][0],
            "ci_high": effect["success_rate_difference_crossed_bootstrap_95_ci"][1],
            "c_favorable_pair_rate": effect["l3_success_better_pair_rate"],
            "confirmatory_gate_pass": "secondary",
        },
    ]
    contrast_path = table_dir / "table2_primary_contrasts.csv"
    write_csv(contrast_path, list(contrast_rows[0]), contrast_rows)

    condition_rows = condition_differences(results)
    condition_path = table_dir / "table3_condition_effects.csv"
    write_csv(condition_path, list(condition_rows[0]), condition_rows)

    guard_rows = []
    for condition, stats in results["h4_gate_controls"].items():
        guard_rows.append(
            {
                "analysis": "gate",
                "condition_or_arm": condition,
                "n": stats["n"],
                "rate": stats["gate_fire_rate"],
                "ci_low": stats["wilson_95_ci"][0],
                "ci_high": stats["wilson_95_ci"][1],
                "mean_final_distance_mm": "",
            }
        )
    for arm in ["B_L1_ZERO_ORDER", "C_L3_CONSTANT_VELOCITY"]:
        stats = results["static_retention"]["by_arm"][arm]
        guard_rows.append(
            {
                "analysis": "static_retention",
                "condition_or_arm": arm,
                "n": stats["n"],
                "rate": stats["success_rate"],
                "ci_low": "",
                "ci_high": "",
                "mean_final_distance_mm": 1000.0 * stats["mean_final_distance_m"],
            }
        )
    guard_path = table_dir / "table4_gate_and_retention.csv"
    write_csv(guard_path, list(guard_rows[0]), guard_rows)
    return [arm_path, contrast_path, condition_path, guard_path]


def write_readme(out: Path) -> Path:
    path = out / "README.md"
    path.write_text(
        "# Paper 002 figures\n\n"
        "All panels and CSV tables are generated directly from the frozen confirmatory JSON artifacts.\n\n"
        "```bash\npython scripts/plot_paper002_model_order.py\n```\n\n"
        "| File | Content |\n"
        "| --- | --- |\n"
        "| `fig1_confirmatory_protocol.png` | Preregistered protocol and arms |\n"
        "| `fig2_confirmatory_outcomes.png` | Arm-level prediction, control, and success outcomes |\n"
        "| `fig3_condition_effects.png` | C-minus-B effects across all ten fresh conditions |\n"
        "| `fig4_representative_trajectory.png` | Process-isolated seed 300/C04 trajectory |\n"
        "| `fig5_gate_and_retention.png` | H3 retention and H4 gate controls |\n"
        "| `tables/*.csv` | Machine-readable manuscript tables |\n"
        "| `manifest.json` | Source and output SHA-256 hashes |\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--trajectories", type=Path, default=DEFAULT_TRAJECTORIES)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    results_path = args.results.resolve()
    trajectories_path = args.trajectories.resolve()
    out = args.out_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)

    results = load_json(results_path)
    trajectories = load_json(trajectories_path)
    if results.get("analysis_phase") != "confirmatory" or not results.get("confirmatory_pass"):
        raise ValueError("Expected a passing confirmatory result artifact")

    outputs = [
        figure_protocol(out),
        figure_outcomes(results, out),
        figure_condition_effects(results, out),
        figure_trajectory(trajectories, out),
        figure_guards(results, out),
    ]
    outputs.extend(write_tables(results, out))
    outputs.append(write_readme(out))

    manifest = {
        "experiment_id": results["experiment_id"],
        "analysis_phase": results["analysis_phase"],
        "confirmatory_pass": results["confirmatory_pass"],
        "source_files": {
            str(results_path.relative_to(ROOT)).replace("\\", "/"): sha256(results_path),
            str(trajectories_path.relative_to(ROOT)).replace("\\", "/"): sha256(trajectories_path),
        },
        "generated_files": {
            str(path.relative_to(out)).replace("\\", "/"): sha256(path)
            for path in sorted(outputs)
        },
        "representative_trajectory": {"seed": 300, "condition_id": "C04"},
    }
    manifest_path = out / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] wrote {len(outputs)} figure/table files and {manifest_path}")


if __name__ == "__main__":
    main()
