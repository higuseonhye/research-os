#!/usr/bin/env bash
# Real Isaac Sim viewport capture for Paper 002 figure/portfolio teasers.
#
# STATUS: prepared 2026-07-31, NOT YET RUN — no GPU/Isaac Lab available in the
# authoring session. Run on VESSL/RunPod (Isaac Sim 4.1 + Isaac Lab, see
# docs/paper002/vessl_runbook_v0.1.md), then sanity-check every PNG before
# promoting into docs/paper002/figures/ or docs/index.md. See
# docs/FIGURE_STANDARDS.md.
#
# Read-only visualization pass — does NOT touch the frozen confirmatory
# script (scripts/orbit_reach_drift.py) or its results.
#
# Usage:
#   bash scripts/capture_paper002_viewport.sh
#   SEED=300 CAPTURE_STEPS=0,20,40,80 bash scripts/capture_paper002_viewport.sh

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

SEED="${SEED:-300}"
CAPTURE_STEPS="${CAPTURE_STEPS:-0,20,40,80}"
CAPTURE_DIR="${CAPTURE_DIR:-docs/paper002/figures/isaac_captures}"
DRIFT_AXIS="${DRIFT_AXIS:-x}"
DRIFT_SPEED="${DRIFT_SPEED:-0.01}"
ONSET="${ONSET:-20}"

if command -v /isaac-sim/python.sh >/dev/null 2>&1; then
  ISAAC_PYTHON="/isaac-sim/python.sh"
elif [ -x "${ISAACLAB_PATH:-/workspace/IsaacLab}/isaaclab.sh" ]; then
  ISAAC_PYTHON="${ISAACLAB_PATH:-/workspace/IsaacLab}/isaaclab.sh -p"
else
  echo "[capture] no Isaac Sim / Isaac Lab launcher found — run this on VESSL/RunPod" >&2
  exit 1
fi

echo "[capture] seed=$SEED steps=$CAPTURE_STEPS -> $CAPTURE_DIR"

$ISAAC_PYTHON scripts/capture_paper002_viewport.py \
  --headless \
  --enable_cameras \
  --seed "$SEED" \
  --capture-steps "$CAPTURE_STEPS" \
  --capture-dir "$CAPTURE_DIR" \
  --drift-axis "$DRIFT_AXIS" \
  --drift-speed "$DRIFT_SPEED" \
  --onset "$ONSET"

echo "[capture] done -> $CAPTURE_DIR — review frames before promoting into figures/README.md"
