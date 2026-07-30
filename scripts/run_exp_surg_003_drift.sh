#!/usr/bin/env bash
# EXP-SURG-003 — Isaac persistent target drift (RunPod / VESSL / any GPU host)
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="${REPO:-$ROOT_DIR}"
OUT="${OUT:-$REPO/experiments/surgical_intelligence/exp_surg_003_wm_expansion/results/isaac_drift_pilot_v0.1}"
SEEDS="${SEEDS:-0,1,2,3,4}"
ONSET="${ONSET:-20}"
MAX_STEPS="${MAX_STEPS:-160}"
TOL_M="${TOL_M:-0.02}"
PREFIX_MAX_STEPS="${PREFIX_MAX_STEPS:-200}"
PREFIX_STABLE_STEPS="${PREFIX_STABLE_STEPS:-5}"
PAIRED_START_TOL_M="${PAIRED_START_TOL_M:-0.001}"
REQUIRED_ELIGIBLE_SEEDS="${REQUIRED_ELIGIBLE_SEEDS:-0}"
DRIFT_SPEED="${DRIFT_SPEED:-0.01}"
DRIFT_AXIS="${DRIFT_AXIS:-x}"
DRIFT_DURATION="${DRIFT_DURATION:-40}"
SKIP_BOOTSTRAP="${EXP_SURG_003_SKIP_BOOTSTRAP:-0}"
DISABLE_FABRIC="${DISABLE_FABRIC:-0}"

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
echo "readiness: <= tolerance for $PREFIX_STABLE_STEPS steps (max prefix $PREFIX_MAX_STEPS); paired start <= $PAIRED_START_TOL_M m"
echo "eligibility: tolerance $TOL_M m; required static-control quota $REQUIRED_ELIGIBLE_SEEDS"

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
FABRIC_ARGS=()
if [ "$DISABLE_FABRIC" = "1" ]; then
  FABRIC_ARGS+=(--disable_fabric)
fi
: > "$OUT/isaac_stdout.log"
IFS=',' read -r -a raw_seed_list <<< "$SEEDS"
seed_list=()
for raw_seed in "${raw_seed_list[@]}"; do
  seed="${raw_seed//[[:space:]]/}"
  if [[ ! "$seed" =~ ^-?[0-9]+$ ]]; then
    echo "[FAIL] invalid seed: $raw_seed" >&2
    exit 1
  fi
  seed_list+=("$seed")
done
if [[ ! "$REQUIRED_ELIGIBLE_SEEDS" =~ ^[0-9]+$ ]]; then
  echo "[FAIL] REQUIRED_ELIGIBLE_SEEDS must be a non-negative integer" >&2
  exit 1
fi

run_arm() {
  local seed="$1"
  local policy="$2"
  local arm_out="$OUT/seed_$seed/$policy"
  local isaac_rc
  mkdir -p "$arm_out"
  echo "== Isolated Isaac seed $seed policy $policy ==" | tee -a "$OUT/isaac_stdout.log"
  set +e
  "$ISAACLAB_SH" -p "$REPO/scripts/orbit_reach_drift.py" \
    --headless \
    "${FABRIC_ARGS[@]}" \
    --task "$TASK" \
    --out-dir "$arm_out" \
    --seeds "$seed" \
    --policy "$policy" \
    --onset "$ONSET" \
    --max-steps "$MAX_STEPS" \
    --tol-m "$TOL_M" \
    --prefix-max-steps "$PREFIX_MAX_STEPS" \
    --prefix-stable-steps "$PREFIX_STABLE_STEPS" \
    --paired-start-tol-m "$PAIRED_START_TOL_M" \
    --drift-speed "$DRIFT_SPEED" \
    --drift-axis "$DRIFT_AXIS" \
    --drift-duration "$DRIFT_DURATION" \
    --experiment-id EXP-SURG-003-drift-pilot \
    | tee "$arm_out/isaac_stdout.log" \
    | tee -a "$OUT/isaac_stdout.log"
  isaac_rc=${PIPESTATUS[0]}
  set -e
  if [ "$isaac_rc" -ne 0 ]; then
    echo "[FAIL] seed $seed policy $policy exited with code $isaac_rc" >&2
    return "$isaac_rc"
  fi
}

selected_seeds="$SEEDS"
selection_args=()
POLICIES=(STATIC_CONTROL TRACK_DRIFTING TRACK_FROZEN)
if [ "$REQUIRED_ELIGIBLE_SEEDS" -gt 0 ]; then
  for seed in "${seed_list[@]}"; do
    run_arm "$seed" STATIC_CONTROL
  done
  cd "$REPO"
  selected_seeds="$(python3 "$REPO/scripts/select_exp_surg_003_candidates.py" \
    --out-dir "$OUT" \
    --seeds "$SEEDS" \
    --required "$REQUIRED_ELIGIBLE_SEEDS" \
    --tol-m "$TOL_M" \
    --onset "$ONSET" \
    --max-steps "$MAX_STEPS" \
    --prefix-max-steps "$PREFIX_MAX_STEPS" \
    --prefix-stable-steps "$PREFIX_STABLE_STEPS" \
    --paired-start-tol-m "$PAIRED_START_TOL_M" \
    --drift-speed "$DRIFT_SPEED" \
    --drift-axis "$DRIFT_AXIS" \
    --drift-duration "$DRIFT_DURATION")"
  echo "[INFO] locked eligible seeds before treatment: $selected_seeds" \
    | tee -a "$OUT/isaac_stdout.log"
  selection_args=(--selection-manifest "$OUT/selection_manifest.json")
  IFS=',' read -r -a selected_seed_list <<< "$selected_seeds"
  cd "$ORBIT_SURGICAL_PATH"
  for seed in "${selected_seed_list[@]}"; do
    run_arm "$seed" TRACK_DRIFTING
    run_arm "$seed" TRACK_FROZEN
  done
else
  selected_seed_list=("${seed_list[@]}")
  for seed in "${selected_seed_list[@]}"; do
    for policy in "${POLICIES[@]}"; do
      run_arm "$seed" "$policy"
    done
  done
fi
cd "$REPO"

python3 "$REPO/scripts/aggregate_exp_surg_003_drift.py" \
  --out-dir "$OUT" \
  --seeds "$selected_seeds" \
  "${selection_args[@]}" \
  | tee -a "$OUT/isaac_stdout.log"

if [ ! -f "$OUT/isaac_drift_results.json" ]; then
  echo "[FAIL] isaac_drift_results.json missing" >&2
  exit 1
fi

echo "== Done =="
echo "results: $OUT/isaac_drift_results.json"
echo "trajectories: $OUT/isaac_drift_trajectories.json"
