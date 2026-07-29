#!/usr/bin/env bash
# EXP-SURG-003 — Isaac persistent target drift (RunPod / VESSL / any GPU host)
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="${REPO:-$ROOT_DIR}"
OUT="${OUT:-$REPO/experiments/surgical_intelligence/exp_surg_003_wm_expansion/results/isaac_drift_pilot_v0.1}"
SEEDS="${SEEDS:-0,1,2,3,4}"
ONSET="${ONSET:-20}"
DRIFT_SPEED="${DRIFT_SPEED:-0.01}"
DRIFT_AXIS="${DRIFT_AXIS:-x}"
DRIFT_DURATION="${DRIFT_DURATION:-40}"
SKIP_BOOTSTRAP="${EXP_SURG_003_SKIP_BOOTSTRAP:-0}"

ISAACLAB_PATH="${IsaacLab_PATH:-/workspace/IsaacLab}"
ORBIT_SURGICAL_PATH="${ORBIT_SURGICAL_PATH:-/workspace/orbit-surgical}"
ISAACLAB_SH="${ISAACLAB_SH:-$ISAACLAB_PATH/isaaclab.sh}"
TASK="${ORBIT_REACH_TASK:-Isaac-Reach-Dual-STAR-IK-Rel-Play-v0}"

cd "$REPO"
mkdir -p "$OUT"
commit_sha="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
echo "$commit_sha" > "$OUT/git_commit.txt"

echo "== EXP-SURG-003 Isaac drift =="
echo "commit: $commit_sha"
echo "out: $OUT"
echo "seeds: $SEEDS onset: $ONSET drift: $DRIFT_AXIS @ $DRIFT_SPEED m/step x $DRIFT_DURATION steps"

if [ "$SKIP_BOOTSTRAP" != "1" ]; then
  bash "$REPO/scripts/bootstrap_orbit_surgical_runpod.sh"
fi

if [[ ! -x "$ISAACLAB_SH" ]]; then
  echo "[ERROR] isaaclab.sh not found at $ISAACLAB_SH" >&2
  echo "Set IsaacLab_PATH or run EXP_SURG_003_PREP_BOOTSTRAP=1 on fresh volume." >&2
  exit 1
fi

export OMNI_KIT_ALLOW_ROOT=1
export IsaacLab_PATH="$ISAACLAB_PATH"

# zero_agent smoke (infra gate — same as Study2 VESSL runbook)
if [ "${EXP_SURG_003_ZERO_AGENT:-1}" = "1" ]; then
  echo "== zero_agent smoke =="
  cd "$ORBIT_SURGICAL_PATH"
  set +e
  "$ISAACLAB_SH" -p source/standalone/environments/zero_agent.py \
    --task "$TASK" --num_envs 1 --headless
  za_rc=$?
  set -e
  cd "$REPO"
  if [ "$za_rc" -ne 0 ]; then
    echo "[FAIL] zero_agent smoke failed (code $za_rc) — log infra blocker; do not retry spiral" >&2
    exit "$za_rc"
  fi
  echo "[OK] zero_agent smoke passed"
fi

cd "$ORBIT_SURGICAL_PATH"
set +e
"$ISAACLAB_SH" -p "$REPO/scripts/orbit_reach_drift.py" \
  --headless \
  --task "$TASK" \
  --out-dir "$OUT" \
  --seeds "$SEEDS" \
  --onset "$ONSET" \
  --drift-speed "$DRIFT_SPEED" \
  --drift-axis "$DRIFT_AXIS" \
  --drift-duration "$DRIFT_DURATION" \
  --experiment-id EXP-SURG-003-drift-pilot | tee "$OUT/isaac_stdout.log"
isaac_rc=${PIPESTATUS[0]}
set -e
cd "$REPO"

if [ "$isaac_rc" -ne 0 ]; then
  echo "[FAIL] orbit_reach_drift exited with code $isaac_rc" >&2
  exit "$isaac_rc"
fi

if [ ! -f "$OUT/isaac_drift_results.json" ]; then
  echo "[FAIL] isaac_drift_results.json missing" >&2
  exit 1
fi

echo "== Done =="
echo "results: $OUT/isaac_drift_results.json"
echo "trajectories: $OUT/isaac_drift_trajectories.json"
