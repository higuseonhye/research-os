#!/usr/bin/env bash
# Reproducible Isaac Sim viewport capture for Paper 001 figure panels.
#
# Run on VESSL / RunPod with Isaac Sim 4.1 + ORBIT (see docker/vessl-isaac-sim-4.1.0/).
# Produces PNG frames under CAPTURE_DIR for paper static figures.
#
# Usage:
#   bash scripts/capture_study1_viewport.sh
#   SEED=0 MODES=CONTINUE,REPLAN_d20 CAPTURE_DIR=docs/paper1/figures/isaac_captures bash scripts/capture_study1_viewport.sh
#
# After capture, promote PNGs and reference in docs/paper1/fig_captions.md.

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

SEED="${SEED:-0}"
MODES="${MODES:-CONTINUE,REPLAN,REOBSERVE}"
CAPTURE_DIR="${CAPTURE_DIR:-docs/paper1/figures/isaac_captures}"
STEPS="${CAPTURE_STEPS:-0,20,40,80,120}"
SHIFT_M="${SHIFT_M:-0.06}"
ONSET="${ONSET:-20}"

# Prefer VESSL wrapper (isaaclab.sh + bootstrap)
if [ -f "$ROOT/scripts/run_study1_capture_vessl.sh" ] && [ -d "${ISAACLAB_PATH:-/workspace/IsaacLab}" ]; then
  exec bash "$ROOT/scripts/run_study1_capture_vessl.sh"
fi

if command -v /isaac-sim/python.sh >/dev/null 2>&1; then
  ISAAC_PYTHON="/isaac-sim/python.sh"
fi

echo "[capture] seed=$SEED modes=$MODES steps=$STEPS -> $CAPTURE_DIR"

"$ISAAC_PYTHON" scripts/orbit_reach_study1d_counterfactual.py \
  --headless \
  --capture \
  --capture-dir "$CAPTURE_DIR" \
  --capture-seed "$SEED" \
  --capture-modes "$MODES" \
  --out-dir "$CAPTURE_DIR/run_output" \
  --shift-m "$SHIFT_M" \
  --onset "$ONSET" \
  --seeds "$SEED" \
  --modes "$MODES" \
  --num_envs 1 \
  --episodes 1

cat > "$CAPTURE_DIR/capture_manifest.json" <<EOF
{
  "script": "scripts/capture_study1_viewport.sh",
  "seed": $SEED,
  "modes": "$MODES",
  "steps": "$STEPS",
  "shift_m": $SHIFT_M,
  "onset_step": $ONSET,
  "task": "Isaac-Reach-Dual-STAR-IK-Rel-Play-v0",
  "note": "Promote PNGs to docs/paper1/figures/ for paper; keep this dir for reproducibility."
}
EOF

echo "[capture] done -> $CAPTURE_DIR"
