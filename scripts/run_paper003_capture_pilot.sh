#!/usr/bin/env bash
# Paper 003 capture calibration pilot — the run that could end the design.
#
# Every Paper 003 result so far is arithmetic: the cell computes the block's
# motion from a formula and writes it into the command. This runs the same loop
# with the block as a physical body, and asks first whether the scene produces a
# CAPTURE - still, then carried - rather than a collision.
#
# The gripper is what makes the difference, and the mechanism came out of an
# observation already in the record: an open gripper *straddles* the block, and
# the frame point reached 0.3 mm from its centre without moving it. That was a
# failure for a push probe. For capture it is the whole device - the block must
# be perfectly still before the arrival, or its own history carries information
# and the single-entity arm has something to learn from. So: approach open,
# close on arrival, carry.
#
# STATUS: never run. Excluded from confirmatory estimates - this is calibration.
#
# Usage:
#   bash scripts/run_paper003_capture_pilot.sh                  # stage 1: one cell
#   SEEDS=40 bash scripts/run_paper003_capture_pilot.sh         # stage 2: engagement
#   CONDITION=static SEEDS=20 bash scripts/run_paper003_capture_pilot.sh
#   bash scripts/run_paper003_capture_pilot.sh --grasp-radius 0.008

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

SEED="${SEED:-300}"
SEEDS="${SEEDS:-1}"
CONDITION="${CONDITION:-coupled}"
OUT_DIR="${OUT_DIR:-results/paper003_capture_pilot/${CONDITION}}"

if [ -x "${ISAACLAB_PATH:-/workspace/IsaacLab}/isaaclab.sh" ]; then
  ISAAC_PYTHON="${ISAACLAB_PATH:-/workspace/IsaacLab}/isaaclab.sh -p"
elif [ -x /isaac-sim/python.sh ]; then
  ISAAC_PYTHON="/isaac-sim/python.sh"
else
  echo "[capture-pilot] no Isaac Sim / Isaac Lab launcher found." >&2
  echo "[capture-pilot] looked for: /isaac-sim/python.sh" >&2
  echo "[capture-pilot]        and: ${ISAACLAB_PATH:-/workspace/IsaacLab}/isaaclab.sh" >&2
  echo "[capture-pilot] run this inside the VESSL Isaac image, or set ISAACLAB_PATH." >&2
  exit 1
fi

echo "[capture-pilot] interpreter : $ISAAC_PYTHON"
echo "[capture-pilot] seeds $SEED..$((SEED + SEEDS - 1))  condition=$CONDITION"
echo "[capture-pilot] -> $OUT_DIR"
echo "[capture-pilot] CALIBRATION ONLY - excluded from confirmatory estimates"

# --grasp and --schedule burst are the capture pairing and are not optional
# here. A body that arrives and carries the target off has no reason to
# withdraw, and `probe` drags the captured block back, which breaks the
# pattern estimator - measured on CPU, arm D gains nothing there.
# shellcheck disable=SC2086
$ISAAC_PYTHON scripts/orbit_lift_relation_cell.py \
  --headless \
  --seed "$SEED" \
  --seeds "$SEEDS" \
  --condition "$CONDITION" \
  --grasp \
  --schedule burst \
  --out-dir "$OUT_DIR" \
  "$@"

echo
echo "[capture-pilot] done. Read in this order, and stop at the first failure:"
echo
echo "  1. CAPTURE VERDICT in each cell's .txt, and SUMMARY.txt for the sweep."
echo "     Anything other than 'capture' means the scene did not produce the"
echo "     relation the paper is about. Do not read arm scores from those cells."
echo
echo "  2. ARM LAGGING warnings. A median error above half the interaction"
echo "     radius means the body is not where the script says it is, so the"
echo "     contact geometry the gate reasons about is wrong. Fix before reading"
echo "     anything else: lower --script-speed or raise --approach-speed."
echo
echo "  3. engagement in SUMMARY.txt. This is the number the preregistration's"
echo "     sizing rule reads, and it must come from here rather than from the"
echo "     injected-coupling runs. docs/paper003/paper003_prereg_v1.0.md"
echo
echo "  4. normal_alignment in the JSON. It is 1.0 by construction on CPU. A"
echo "     contact that pushes off-normal returns correct coefficients while"
echo "     arm D aims the wrong way, and that is the dominant threat under"
echo "     realistic contact."
