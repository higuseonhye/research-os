#!/usr/bin/env bash
# EXP-SURG-003 — Isaac drift data collection (RunPod / GPU host)
set -euo pipefail

REPO="${REPO:-/workspace/research-os}"
OUT="${OUT:-$REPO/experiments/surgical_intelligence/exp_surg_003_wm_expansion/results/isaac_drift_pilot_v0.1}"
SEEDS="${SEEDS:-0,1,2}"
ONSET="${ONSET:-20}"
DRIFT_SPEED="${DRIFT_SPEED:-0.01}"
DRIFT_AXIS="${DRIFT_AXIS:-x}"
DRIFT_DURATION="${DRIFT_DURATION:-40}"

cd "$REPO"
mkdir -p "$OUT"

ISAACLAB_SH="${ISAACLAB_SH:-/workspace/isaaclab/isaaclab.sh}"
if [[ ! -x "$ISAACLAB_SH" ]]; then
  echo "[ERROR] isaaclab.sh not found at $ISAACLAB_SH"
  exit 1
fi

"$ISAACLAB_SH" -p scripts/orbit_reach_drift.py \
  --headless \
  --out-dir "$OUT" \
  --seeds "$SEEDS" \
  --onset "$ONSET" \
  --drift-speed "$DRIFT_SPEED" \
  --drift-axis "$DRIFT_AXIS" \
  --drift-duration "$DRIFT_DURATION" \
  --experiment-id EXP-SURG-003-drift-pilot

echo "[INFO] results in $OUT"
