#!/usr/bin/env bash
# EXP-SURG-001A — Counterfactual Recovery Smoke on RunPod / Isaac host
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/artifacts/study1a_counterfactual_target_shift"
ISAACLAB_PATH="${ISAACLAB_PATH:-/workspace/IsaacLab}"
ORBIT_SURGICAL_PATH="${ORBIT_SURGICAL_PATH:-/workspace/orbit-surgical}"
TASK="${ORBIT_REACH_TASK:-Isaac-Reach-Dual-STAR-IK-Rel-Play-v0}"
SEED="${STUDY1A_SEED:-0}"
EPISODES="${STUDY1A_EPISODES:-5}"
ONSET="${STUDY1A_ONSET:-20}"
STEPS="${STUDY1A_MAX_STEPS:-160}"
SHIFT="${STUDY1A_SHIFT_M:-0.03}"
BODY_INDEX="${STUDY1A_BODY_INDEX:-13}"
MAX_DELTA="${STUDY1A_MAX_DELTA:-0.08}"
EPISODE_LEN_S="${STUDY1A_EPISODE_LENGTH_S:-20}"

mkdir -p "$OUT_DIR/videos" "$OUT_DIR/figures"
cd "$ROOT_DIR"

commit_sha="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
echo "$commit_sha" > "$OUT_DIR/git_commit.txt"
cp -f "$ROOT_DIR/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/config/study1a_counterfactual_target_shift.yaml" \
  "$OUT_DIR/config.yaml"

echo "== EXP-SURG-001A =="
echo "commit: $commit_sha"
echo "task: $TASK"
echo "seed: $SEED episodes: $EPISODES onset: $ONSET shift: $SHIFT"

bash "$ROOT_DIR/scripts/bootstrap_orbit_surgical_runpod.sh"

export OMNI_KIT_ALLOW_ROOT=1
export IsaacLab_PATH="$ISAACLAB_PATH"

cd "$ORBIT_SURGICAL_PATH"
set +e
"$ISAACLAB_PATH/isaaclab.sh" -p "$ROOT_DIR/scripts/orbit_reach_study1a_counterfactual.py" \
  --experiment-id EXP-SURG-001A \
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
  --replan-delays 0 \
  --out-dir "$OUT_DIR" \
  --headless | tee "$OUT_DIR/isaac_stdout.log"
isaac_rc=${PIPESTATUS[0]}
set -e
cd "$ROOT_DIR"

if [ "$isaac_rc" -ne 0 ]; then
  echo "[FAIL] Isaac study1a exited with code $isaac_rc"
  echo "See: $OUT_DIR/isaac_stdout.log"
  echo "Do NOT trust mock figures as Isaac results."
  exit "$isaac_rc"
fi

if [ ! -f "$OUT_DIR/isaac_results.json" ]; then
  echo "[FAIL] isaac_results.json missing"
  exit 1
fi

echo "== Done (Isaac) =="
echo "artifacts: $OUT_DIR"
echo "isaac_results: $OUT_DIR/isaac_results.json"
echo "Next: EXP-SURG-001B timing curve (replan at t+0/+5/+10/+20)"
