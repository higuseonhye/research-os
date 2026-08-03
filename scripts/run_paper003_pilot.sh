#!/usr/bin/env bash
# Launch the Paper 003 calibration pilot with the right interpreter.
#
# A bare `python` does not work inside an Isaac container - the simulator ships
# its own interpreter. This resolves it the same way
# scripts/capture_paper002_viewport.sh does, so the invocation does not have to
# be remembered correctly at the terminal.
#
# STATUS: the pilot runner it launches has NEVER BEEN RUN. Expect iteration.
# This is an engineering calibration, excluded from confirmatory estimates.
#
# Usage:
#   bash scripts/run_paper003_pilot.sh                       # smoke, seed 300
#   SEED=301 CONDITION=drift bash scripts/run_paper003_pilot.sh
#   bash scripts/run_paper003_pilot.sh --reference-speed 0.02   # extra args pass through

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

SEED="${SEED:-300}"
CONDITION="${CONDITION:-coupled}"
OUT_DIR="${OUT_DIR:-results/paper003_pilot_smoke}"

if [ -x /isaac-sim/python.sh ]; then
  ISAAC_PYTHON="/isaac-sim/python.sh"
elif [ -x "${ISAACLAB_PATH:-/workspace/IsaacLab}/isaaclab.sh" ]; then
  ISAAC_PYTHON="${ISAACLAB_PATH:-/workspace/IsaacLab}/isaaclab.sh -p"
else
  echo "[pilot] no Isaac Sim / Isaac Lab launcher found." >&2
  echo "[pilot] looked for: /isaac-sim/python.sh" >&2
  echo "[pilot]        and: ${ISAACLAB_PATH:-/workspace/IsaacLab}/isaaclab.sh" >&2
  echo "[pilot] run this inside the VESSL/RunPod Isaac image, or set ISAACLAB_PATH." >&2
  exit 1
fi

echo "[pilot] interpreter : $ISAAC_PYTHON"
echo "[pilot] seed=$SEED condition=$CONDITION -> $OUT_DIR"
echo "[pilot] CALIBRATION ONLY - excluded from confirmatory estimates"

# shellcheck disable=SC2086
$ISAAC_PYTHON scripts/orbit_reach_relation_pilot.py \
  --headless \
  --seed "$SEED" \
  --condition "$CONDITION" \
  --max-cells 1 \
  --out-dir "$OUT_DIR" \
  "$@"

echo
echo "[pilot] done. Before trusting anything, check in the written JSON:"
echo "  committed_at  is not null   (null => eligibility never opened; geometry, not science)"
echo "  valid         is true"
echo "  resolved      has all five arms"
echo "  observations  show the target moving only while the reference is near"
