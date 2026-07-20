#!/usr/bin/env bash
# EXP-SURG-001D — Occlusion × multi-mode D0 smoke (RunPod / Isaac host)
#
# Usage (RunPod pod shell):
#   bash scripts/run_study1d_runpod.sh
#
# D1 full grid (5 seeds · all modes):
#   STUDY1D_FULL=1 bash scripts/run_study1d_runpod.sh
#
# Contract: experiments/.../docs/study1d_occlusion_proxy_v0.1.md
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ISAACLAB_PATH="${ISAACLAB_PATH:-/workspace/IsaacLab}"
ORBIT_SURGICAL_PATH="${ORBIT_SURGICAL_PATH:-/workspace/orbit-surgical}"
ARTIFACT_ROOT="$ROOT_DIR/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/artifacts/study1d_occlusion_multimode"
CFG="$ROOT_DIR/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/config/study1d_occlusion_multimode.yaml"
TASK="${ORBIT_REACH_TASK:-Isaac-Reach-Dual-STAR-IK-Rel-Play-v0}"

# Locked 001C anchor + proxy v0.1 defaults (override via env)
SHIFT_M="${STUDY1D_SHIFT_M:-0.06}"
REPLAN_DELAY="${STUDY1D_REPLAN_DELAY:-20}"
ONSET="${STUDY1D_ONSET:-20}"
MAX_STEPS="${STUDY1D_MAX_STEPS:-160}"
BODY_INDEX="${STUDY1D_BODY_INDEX:-13}"
GAIN="${STUDY1D_GAIN:-1.0}"
MAX_DELTA="${STUDY1D_MAX_DELTA:-0.08}"
EPISODE_LEN_S="${STUDY1D_EPISODE_LENGTH_S:-20}"
OCCLUSION_LEVEL="${STUDY1D_OCCLUSION_LEVEL:-1}"
VIS_FRAC="${STUDY1D_VISIBILITY_FRACTION:-0.35}"
REOBSERVE_HOLD="${STUDY1D_REOBSERVE_HOLD:-10}"
RESHAPE_STEPS="${STUDY1D_RESHAPE_STEPS:-20}"

if [[ "${STUDY1D_FULL:-0}" == "1" ]]; then
  SEEDS="${STUDY1D_SEEDS:-0,1,2,3,4}"
  MODES="${STUDY1D_MODES:-CONTINUE,REPLAN,REOBSERVE,RESHAPE,HANDOVER}"
  OUT_SUB="isaac_full"
  PHASE="full"
else
  SEEDS="${STUDY1D_SEEDS:-0}"
  MODES="${STUDY1D_MODES:-CONTINUE,REPLAN,REOBSERVE}"
  OUT_SUB="isaac_smoke"
  PHASE="smoke"
fi

OUT_DIR="$ARTIFACT_ROOT/$OUT_SUB"
mkdir -p "$OUT_DIR/videos" "$OUT_DIR/figures"

cd "$ROOT_DIR"
COMMIT="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
echo "== EXP-SURG-001D ($PHASE) commit=$COMMIT =="
echo "shift=${SHIFT_M}m replan_d=${REPLAN_DELAY} vis=${VIS_FRAC} modes=${MODES} seeds=${SEEDS}"
echo "$COMMIT" > "$OUT_DIR/git_commit.txt"
cp -f "$CFG" "$OUT_DIR/config.yaml"

bash "$ROOT_DIR/scripts/bootstrap_orbit_surgical_runpod.sh"

export OMNI_KIT_ALLOW_ROOT=1
export IsaacLab_PATH="$ISAACLAB_PATH"
cd "$ORBIT_SURGICAL_PATH"

set +e
"$ISAACLAB_PATH/isaaclab.sh" -p "$ROOT_DIR/scripts/orbit_reach_study1d_counterfactual.py" \
  --experiment-id EXP-SURG-001D \
  --task "$TASK" \
  --num_envs 1 \
  --seeds "$SEEDS" \
  --onset "$ONSET" \
  --max-steps "$MAX_STEPS" \
  --shift-m "$SHIFT_M" \
  --replan-delay "$REPLAN_DELAY" \
  --occlusion-level "$OCCLUSION_LEVEL" \
  --visibility-fraction "$VIS_FRAC" \
  --reobserve-hold-steps "$REOBSERVE_HOLD" \
  --reshape-steps "$RESHAPE_STEPS" \
  --modes "$MODES" \
  --body-index "$BODY_INDEX" \
  --gain "$GAIN" \
  --max-delta "$MAX_DELTA" \
  --episode-length-s "$EPISODE_LEN_S" \
  --out-dir "$OUT_DIR" \
  --headless | tee "$OUT_DIR/isaac_stdout.log"
isaac_rc=${PIPESTATUS[0]}
set -e
cd "$ROOT_DIR"

if [ "$isaac_rc" -ne 0 ]; then
  echo "[FAIL] Isaac study1d exited with code $isaac_rc"
  echo "See: $OUT_DIR/isaac_stdout.log"
  exit "$isaac_rc"
fi

if [ ! -f "$OUT_DIR/isaac_results.json" ]; then
  echo "[FAIL] isaac_results.json missing under $OUT_DIR"
  exit 1
fi

ISAAC_PYTHON="${ISAAC_PYTHON:-$ISAACLAB_PATH/_isaac_sim/python.sh}"
if [ ! -x "$ISAAC_PYTHON" ]; then
  ISAAC_PYTHON="/isaac-sim/python.sh"
fi

echo "== Ensuring merge dependencies (pyyaml) =="
"$ISAAC_PYTHON" -m pip install -q pyyaml

echo "== Merging + report =="
if [[ "$PHASE" == "smoke" ]]; then
  "$ISAAC_PYTHON" "$ROOT_DIR/scripts/run_study1d.py" --merge --smoke --artifact-root "$ARTIFACT_ROOT"
else
  "$ISAAC_PYTHON" "$ROOT_DIR/scripts/run_study1d.py" --merge --full --artifact-root "$ARTIFACT_ROOT"
fi

echo "== Done EXP-SURG-001D ($PHASE) =="
echo "artifacts: $ARTIFACT_ROOT"
echo "isaac_results: $OUT_DIR/isaac_results.json"
echo "report: $ROOT_DIR/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/study1d_report.md"
echo ""
echo "One-liner template (fill X from aggregate):"
echo "  occlusion @ 6cm · REPLAN d20 · X/5 vs CONTINUE 0/5"
