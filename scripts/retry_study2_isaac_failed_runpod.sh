#!/usr/bin/env bash
# Retry Study2 Isaac specs missing isaac_results.json (same RUN_ID / volume).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="${STUDY2_PYTHON:-/isaac-sim/python.sh}"
RUN_ID="${STUDY2_RUN_ID:?Set STUDY2_RUN_ID from failed run (ls results/study2_dream_curriculum/isaac/)}"

SPECS_OUT="$ROOT_DIR/experiments/surgical_intelligence/exp_surg_002_dream_curriculum/artifacts/isaac_specs.json"
PER_SPEC_DIR="$ROOT_DIR/experiments/surgical_intelligence/exp_surg_002_dream_curriculum/artifacts/isaac_runs/$RUN_ID"
OUT_ISAAC="$ROOT_DIR/results/study2_dream_curriculum/isaac/$RUN_ID"
ISAACLAB_PATH="${ISAACLAB_PATH:-/workspace/IsaacLab}"
ORBIT_SURGICAL_PATH="${ORBIT_SURGICAL_PATH:-/workspace/orbit-surgical}"
TASK="${ORBIT_REACH_TASK:-Isaac-Reach-Dual-STAR-IK-Rel-Play-v0}"
ISAAC_SEEDS="${STUDY2_ISAAC_SEEDS:-0,1,2,3,4}"
MAX_STEPS="${STUDY2_MAX_STEPS:-160}"
ONSET_DEFAULT="${STUDY2_ONSET:-20}"

if [ ! -f "$SPECS_OUT" ]; then
  echo "[FAIL] Missing specs: $SPECS_OUT"
  exit 1
fi

echo "== Retry Study2 Isaac failed specs =="
echo "run_id: $RUN_ID"
echo "results: $PER_SPEC_DIR"

if [ "${STUDY2_SKIP_BOOTSTRAP:-0}" != "1" ]; then
  bash "$ROOT_DIR/scripts/bootstrap_orbit_surgical_runpod.sh"
fi

export OMNI_KIT_ALLOW_ROOT=1
export IsaacLab_PATH ORBIT_SURGICAL_PATH

"$PY" "$ROOT_DIR/scripts/run_study2_isaac_loop.py" \
  --specs "$SPECS_OUT" \
  --results-dir "$PER_SPEC_DIR" \
  --isaaclab "$ISAACLAB_PATH" \
  --orbit "$ORBIT_SURGICAL_PATH" \
  --task "$TASK" \
  --seeds "$ISAAC_SEEDS" \
  --max-steps "$MAX_STEPS" \
  --onset-default "$ONSET_DEFAULT" \
  --skip-existing

commit_sha="$(git -C "$ROOT_DIR" rev-parse HEAD 2>/dev/null || echo unknown)"
"$PY" "$ROOT_DIR/scripts/merge_study2_isaac_results.py" \
  --specs "$SPECS_OUT" \
  --results-dir "$PER_SPEC_DIR" \
  --out-dir "$OUT_ISAAC" \
  --git-commit "$commit_sha"

echo "== Retry merge done =="
echo "aggregate: $OUT_ISAAC/isaac_aggregate.json"
