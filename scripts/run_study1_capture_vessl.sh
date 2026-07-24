#!/usr/bin/env bash
# Paper 001 — Isaac EE trace capture on VESSL / RunPod (~5–10 min).
#
# Usage (VESSL Jupyter terminal):
#   cd /workspace/research-os && git pull origin master
#   bash scripts/run_study1_capture_vessl.sh
#
# Optional:
#   SEED=0 MODES=CONTINUE,REPLAN,REOBSERVE bash scripts/run_study1_capture_vessl.sh
#
# After run: download docs/paper1/figures/isaac_captures/*_ee_trace.json
# Local: python scripts/plot_paper1_from_ee_traces.py

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ISAACLAB_PATH="${ISAACLAB_PATH:-/workspace/IsaacLab}"
ORBIT_SURGICAL_PATH="${ORBIT_SURGICAL_PATH:-/workspace/orbit-surgical}"
CAPTURE_DIR="${CAPTURE_DIR:-$ROOT_DIR/docs/paper1/figures/isaac_captures}"
SEED="${SEED:-0}"
MODES="${MODES:-CONTINUE,REPLAN,REOBSERVE}"
TASK="${ORBIT_REACH_TASK:-Isaac-Reach-Dual-STAR-IK-Rel-Play-v0}"

SHIFT_M="${STUDY1_CAPTURE_SHIFT_M:-0.06}"
ONSET="${STUDY1_CAPTURE_ONSET:-20}"
MAX_STEPS="${STUDY1_CAPTURE_MAX_STEPS:-160}"
REPLAN_DELAY="${STUDY1_CAPTURE_REPLAN_DELAY:-20}"
BODY_INDEX="${STUDY1_CAPTURE_BODY_INDEX:-13}"

mkdir -p "$CAPTURE_DIR"
cd "$ROOT_DIR"
COMMIT="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
echo "== Paper001 capture commit=$COMMIT seed=$SEED modes=$MODES =="
echo "$COMMIT" > "$CAPTURE_DIR/git_commit.txt"

bash "$ROOT_DIR/scripts/bootstrap_orbit_surgical_runpod.sh"
export OMNI_KIT_ALLOW_ROOT=1
export IsaacLab_PATH="$ISAACLAB_PATH"
cd "$ORBIT_SURGICAL_PATH"

set +e
"$ISAACLAB_PATH/isaaclab.sh" -p "$ROOT_DIR/scripts/orbit_reach_study1d_counterfactual.py" \
  --experiment-id EXP-SURG-001-CAPTURE \
  --task "$TASK" \
  --num_envs 1 \
  --seeds "$SEED" \
  --onset "$ONSET" \
  --max-steps "$MAX_STEPS" \
  --shift-m "$SHIFT_M" \
  --replan-delay "$REPLAN_DELAY" \
  --occlusion-level 1 \
  --visibility-fraction 0.35 \
  --modes "$MODES" \
  --body-index "$BODY_INDEX" \
  --capture \
  --capture-dir "$CAPTURE_DIR" \
  --capture-seed "$SEED" \
  --capture-modes "$MODES" \
  --out-dir "$CAPTURE_DIR/run_output" \
  --headless | tee "$CAPTURE_DIR/capture_stdout.log"
isaac_rc=${PIPESTATUS[0]}
set -e
cd "$ROOT_DIR"

if [ "$isaac_rc" -ne 0 ]; then
  echo "[FAIL] capture exited with code $isaac_rc"
  exit "$isaac_rc"
fi

trace_count="$(find "$CAPTURE_DIR" -maxdepth 1 -name '*_ee_trace.json' | wc -l | tr -d ' ')"
if [ "$trace_count" -eq 0 ]; then
  echo "[FAIL] no *_ee_trace.json under $CAPTURE_DIR"
  exit 1
fi

cat > "$CAPTURE_DIR/capture_manifest.json" <<EOF
{
  "script": "scripts/run_study1_capture_vessl.sh",
  "git_commit": "$COMMIT",
  "seed": $SEED,
  "modes": "$MODES",
  "shift_m": $SHIFT_M,
  "onset_step": $ONSET,
  "task": "$TASK",
  "trace_files": $trace_count
}
EOF

echo "== Capture done: $trace_count trace(s) in $CAPTURE_DIR =="
ls -la "$CAPTURE_DIR"/*_ee_trace.json 2>/dev/null || true
echo ""
echo "Download traces before VESSL Pause, then locally:"
echo "  python scripts/plot_paper1_from_ee_traces.py"
