#!/usr/bin/env bash
# EXP-SURG-003 model-order pilot/confirmatory runner for VESSL GPU workspaces.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="${REPO:-$ROOT_DIR}"
if [ "${1:-}" = "--smoke" ]; then
  default_config="$REPO/experiments/surgical_intelligence/exp_surg_003_wm_expansion/config/model_order_smoke_v0.2.json"
  default_out="$REPO/experiments/surgical_intelligence/exp_surg_003_wm_expansion/results/isaac_model_order_smoke_v0.2"
else
  default_config="$REPO/experiments/surgical_intelligence/exp_surg_003_wm_expansion/config/model_order_pilot_v0.2.json"
  default_out="$REPO/experiments/surgical_intelligence/exp_surg_003_wm_expansion/results/isaac_model_order_pilot_v0.2"
fi
CONFIG="${CONFIG:-$default_config}"
OUT="${OUT:-$default_out}"
ISAACLAB_PATH="${IsaacLab_PATH:-/workspace/IsaacLab}"
ORBIT_SURGICAL_PATH="${ORBIT_SURGICAL_PATH:-/workspace/orbit-surgical}"

args=(
  --repo "$REPO"
  --config "$CONFIG"
  --out-dir "$OUT"
  --isaaclab-path "$ISAACLAB_PATH"
  --orbit-surgical-path "$ORBIT_SURGICAL_PATH"
)

if [ "${EXP_SURG_003_SKIP_BOOTSTRAP:-0}" = "1" ]; then
  args+=(--skip-bootstrap)
fi
if [ "${EXP_SURG_003_ZERO_AGENT:-0}" = "0" ]; then
  args+=(--skip-zero-agent)
fi
if [ "${DISABLE_FABRIC:-0}" = "1" ]; then
  args+=(--disable-fabric)
fi

cd "$REPO"
python3 scripts/run_exp_surg_003_model_order.py "${args[@]}"
