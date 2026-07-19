#!/usr/bin/env bash
# EXP-SURG-001B — Timing curve on RunPod / Isaac host (skip full bootstrap if stack ready)
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/artifacts/study1b_timing_curve"
ISAACLAB_PATH="${ISAACLAB_PATH:-/workspace/IsaacLab}"
ORBIT_SURGICAL_PATH="${ORBIT_SURGICAL_PATH:-/workspace/orbit-surgical}"
TASK="${ORBIT_REACH_TASK:-Isaac-Reach-Dual-STAR-IK-Rel-Play-v0}"
SEED="${STUDY1B_SEED:-0}"
EPISODES="${STUDY1B_EPISODES:-3}"
ONSET="${STUDY1B_ONSET:-20}"
STEPS="${STUDY1B_MAX_STEPS:-160}"
SHIFT="${STUDY1B_SHIFT_M:-0.03}"
BODY_INDEX="${STUDY1B_BODY_INDEX:-13}"
MAX_DELTA="${STUDY1B_MAX_DELTA:-0.08}"
EPISODE_LEN_S="${STUDY1B_EPISODE_LENGTH_S:-20}"
DELAYS="${STUDY1B_REPLAN_DELAYS:-0,5,10,20}"

mkdir -p "$OUT_DIR/videos" "$OUT_DIR/figures"
cd "$ROOT_DIR"

commit_sha="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
echo "$commit_sha" > "$OUT_DIR/git_commit.txt"
cp -f "$ROOT_DIR/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/config/study1b_timing_curve.yaml" \
  "$OUT_DIR/config.yaml"

echo "== EXP-SURG-001B =="
echo "commit: $commit_sha"
echo "delays: $DELAYS episodes: $EPISODES"

export OMNI_KIT_ALLOW_ROOT=1
export IsaacLab_PATH="$ISAACLAB_PATH"

cd "$ORBIT_SURGICAL_PATH"
set +e
"$ISAACLAB_PATH/isaaclab.sh" -p "$ROOT_DIR/scripts/orbit_reach_study1a_counterfactual.py" \
  --experiment-id EXP-SURG-001B \
  --task "$TASK" \
  --num_envs 1 \
  --seed "$SEED" \
  --episodes "$EPISODES" \
  --onset "$ONSET" \
  --max-steps "$STEPS" \
  --shift-m "$SHIFT" \
  --body-index "$BODY_INDEX" \
  --max-delta "$MAX_DELTA" \
  --episode-length-s "$EPISODE_LEN_S" \
  --include-continue \
  --replan-delays "$DELAYS" \
  --out-dir "$OUT_DIR" \
  --headless | tee "$OUT_DIR/isaac_stdout.log"
isaac_rc=${PIPESTATUS[0]}
set -e
cd "$ROOT_DIR"

if [ "$isaac_rc" -ne 0 ]; then
  echo "[FAIL] Isaac study1b exited with code $isaac_rc"
  exit "$isaac_rc"
fi

if [ ! -f "$OUT_DIR/isaac_results.json" ]; then
  echo "[FAIL] isaac_results.json missing"
  exit 1
fi

echo "== Done (Isaac 001B) =="
echo "artifacts: $OUT_DIR"
echo "Next: copy aggregate locally → python scripts/plot_study1b_timing_curve.py"
