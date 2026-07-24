#!/usr/bin/env bash
# Paper 001 — pre-reg v2.0 proper blocks D1–D3 (RunPod / VESSL)
#
# Usage:
#   STUDY1_PROPER_BLOCK=d1 bash scripts/run_study1_proper_v2.sh
#   STUDY1_PROPER_BLOCK=d2 bash scripts/run_study1_proper_v2.sh
#   STUDY1_PROPER_BLOCK=d3 bash scripts/run_study1_proper_v2.sh
#
# Pre-reg: docs/paper1/phase_c_proper_run_prereg_v2.0.md
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ISAACLAB_PATH="${ISAACLAB_PATH:-/workspace/IsaacLab}"
ORBIT_SURGICAL_PATH="${ORBIT_SURGICAL_PATH:-/workspace/orbit-surgical}"
BLOCK="${STUDY1_PROPER_BLOCK:?Set STUDY1_PROPER_BLOCK=d1|d2|d3}"
SEEDS="${STUDY1_PROPER_SEEDS:-0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19}"
ARTIFACT_ROOT="$ROOT_DIR/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/artifacts/study1_proper_v2"
OUT_DIR="$ARTIFACT_ROOT/$BLOCK"
TASK="${ORBIT_REACH_TASK:-Isaac-Reach-Dual-STAR-IK-Rel-Play-v0}"

SHIFT_M="${STUDY1_PROPER_SHIFT_M:-0.06}"
ONSET="${STUDY1_PROPER_ONSET:-20}"
MAX_STEPS="${STUDY1_PROPER_MAX_STEPS:-160}"
REPLAN_DELAY="${STUDY1_PROPER_REPLAN_DELAY:-20}"
BODY_INDEX="${STUDY1_PROPER_BODY_INDEX:-13}"
GAIN="${STUDY1_PROPER_GAIN:-1.0}"
MAX_DELTA="${STUDY1_PROPER_MAX_DELTA:-0.08}"
EPISODE_LEN_S="${STUDY1_PROPER_EPISODE_LENGTH_S:-20}"

mkdir -p "$OUT_DIR"
cd "$ROOT_DIR"
COMMIT="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
echo "== Paper001 proper v2.0 block=$BLOCK commit=$COMMIT =="
echo "$COMMIT" > "$OUT_DIR/git_commit.txt"

bash "$ROOT_DIR/scripts/bootstrap_orbit_surgical_runpod.sh"
export OMNI_KIT_ALLOW_ROOT=1
export IsaacLab_PATH="$ISAACLAB_PATH"
cd "$ORBIT_SURGICAL_PATH"

set +e
case "$BLOCK" in
  d1)
    "$ISAACLAB_PATH/isaaclab.sh" -p "$ROOT_DIR/scripts/orbit_reach_study1a_counterfactual.py" \
      --experiment-id EXP-SURG-001-PROPER-v2-D1 \
      --task "$TASK" \
      --num_envs 1 \
      --seeds "$SEEDS" \
      --onset "$ONSET" \
      --max-steps "$MAX_STEPS" \
      --shift-m "$SHIFT_M" \
      --replan-delays "$REPLAN_DELAY" \
      --include-continue \
      --body-index "$BODY_INDEX" \
      --gain "$GAIN" \
      --max-delta "$MAX_DELTA" \
      --episode-length-s "$EPISODE_LEN_S" \
      --out-dir "$OUT_DIR" \
      --headless | tee "$OUT_DIR/isaac_stdout.log"
    ;;
  d2)
    "$ISAACLAB_PATH/isaaclab.sh" -p "$ROOT_DIR/scripts/orbit_reach_study1d_counterfactual.py" \
      --experiment-id EXP-SURG-001-PROPER-v2-D2 \
      --task "$TASK" \
      --num_envs 1 \
      --seeds "$SEEDS" \
      --onset "$ONSET" \
      --max-steps "$MAX_STEPS" \
      --shift-m "$SHIFT_M" \
      --replan-delay "$REPLAN_DELAY" \
      --occlusion-level 1 \
      --visibility-fraction 0.35 \
      --baseline b2 \
      --body-index "$BODY_INDEX" \
      --gain "$GAIN" \
      --max-delta "$MAX_DELTA" \
      --episode-length-s "$EPISODE_LEN_S" \
      --out-dir "$OUT_DIR" \
      --headless | tee "$OUT_DIR/isaac_stdout.log"
    ;;
  d3)
    "$ISAACLAB_PATH/isaaclab.sh" -p "$ROOT_DIR/scripts/orbit_reach_study1d_counterfactual.py" \
      --experiment-id EXP-SURG-001-PROPER-v2-D3 \
      --task "$TASK" \
      --num_envs 1 \
      --seeds "$SEEDS" \
      --onset "$ONSET" \
      --max-steps "$MAX_STEPS" \
      --shift-m "$SHIFT_M" \
      --replan-delay "$REPLAN_DELAY" \
      --occlusion-level 1 \
      --visibility-fraction 0.35 \
      --baseline b3 \
      --body-index "$BODY_INDEX" \
      --gain "$GAIN" \
      --max-delta "$MAX_DELTA" \
      --episode-length-s "$EPISODE_LEN_S" \
      --out-dir "$OUT_DIR" \
      --headless | tee "$OUT_DIR/isaac_stdout.log"
    ;;
  *)
    echo "[FAIL] Unknown STUDY1_PROPER_BLOCK=$BLOCK (use d1|d2|d3)"
    exit 1
    ;;
esac
isaac_rc=${PIPESTATUS[0]}
set -e
cd "$ROOT_DIR"

if [ "$isaac_rc" -ne 0 ]; then
  echo "[FAIL] Isaac proper v2 block $BLOCK exited with code $isaac_rc"
  exit "$isaac_rc"
fi

if [ ! -f "$OUT_DIR/isaac_results.json" ]; then
  echo "[FAIL] isaac_results.json missing under $OUT_DIR"
  exit 1
fi

echo "== Done Paper001 proper v2.0 block=$BLOCK =="
echo "results: $OUT_DIR/isaac_results.json"
echo "Promote to: experiments/.../results/study1_proper_v2/$BLOCK/"
