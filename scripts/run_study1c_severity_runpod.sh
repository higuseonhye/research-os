#!/usr/bin/env bash
# EXP-SURG-001C — Severity × Delay surface (RunPod / Isaac host)
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ISAACLAB_PATH="${ISAACLAB_PATH:-/workspace/IsaacLab}"
ORBIT_SURGICAL_PATH="${ORBIT_SURGICAL_PATH:-/workspace/orbit-surgical}"
ARTIFACT_ROOT="$ROOT_DIR/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/artifacts/study1c_severity_delay_surface"

# Smoke: STUDY1C_SMOKE=1 · Full: default
if [[ "${STUDY1C_SMOKE:-0}" == "1" ]]; then
  SHIFTS="${STUDY1C_SHIFTS:-0.03 0.06 0.09}"
  DELAYS="${STUDY1C_REPLAN_DELAYS:-0,10,20,40}"
  SEEDS="${STUDY1C_SEEDS:-0,1,2}"
  PHASE="smoke"
else
  SHIFTS="${STUDY1C_SHIFTS:-0.01 0.03 0.06 0.09}"
  DELAYS="${STUDY1C_REPLAN_DELAYS:-0,5,10,20,40,60}"
  SEEDS="${STUDY1C_SEEDS:-0,1,2,3,4}"
  PHASE="full"
fi

cd "$ROOT_DIR"
COMMIT="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
echo "== EXP-SURG-001C ($PHASE) commit=$COMMIT =="

# New pods: bootstrap Isaac Lab + ORBIT (~10-25 min first time).
bash "$ROOT_DIR/scripts/bootstrap_orbit_surgical_runpod.sh"

export OMNI_KIT_ALLOW_ROOT=1
export IsaacLab_PATH="$ISAACLAB_PATH"
cd "$ORBIT_SURGICAL_PATH"

for SHIFT in $SHIFTS; do
  OUT="$ARTIFACT_ROOT/isaac_shift_${SHIFT}"
  mkdir -p "$OUT"
  echo "== 001C shift=$SHIFT seeds=$SEEDS delays=$DELAYS =="
  "$ISAACLAB_PATH/isaaclab.sh" -p "$ROOT_DIR/scripts/orbit_reach_study1a_counterfactual.py" \
    --experiment-id EXP-SURG-001C \
    --task Isaac-Reach-Dual-STAR-IK-Rel-Play-v0 \
    --num_envs 1 --seeds "$SEEDS" \
    --onset 20 --max-steps 160 --shift-m "$SHIFT" \
    --body-index 13 --gain 1.0 --max-delta 0.08 --episode-length-s 20 \
    --include-continue --replan-delays "$DELAYS" \
    --out-dir "$OUT" --headless | tee "$OUT/isaac_stdout.log"
done

ISAAC_PYTHON="${ISAAC_PYTHON:-$ISAACLAB_PATH/_isaac_sim/python.sh}"
if [ ! -x "$ISAAC_PYTHON" ]; then
  ISAAC_PYTHON="/isaac-sim/python.sh"
fi

echo "== Ensuring merge dependencies (matplotlib, pyyaml) =="
"$ISAAC_PYTHON" -m pip install -q matplotlib pyyaml

echo "== Merging + figures =="
"$ISAAC_PYTHON" "$ROOT_DIR/scripts/run_study1c.py" --merge --artifact-root "$ARTIFACT_ROOT" \
  $([[ "$PHASE" == "smoke" ]] && echo --smoke || true)

echo "== Done 001C ($PHASE) artifacts=$ARTIFACT_ROOT =="
