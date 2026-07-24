#!/usr/bin/env bash
# Paper 001 — run pre-reg v2.0 blocks D1 → D2 → D3 sequentially (VESSL / RunPod).
#
#   tmux new -s proper_v2
#   bash scripts/run_study1_proper_v2_all.sh
#
# Optional smoke first:
#   STUDY1_PROPER_SKIP_SMOKE=1 bash scripts/run_study1_proper_v2_all.sh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ "${STUDY1_PROPER_SKIP_SMOKE:-0}" != "1" ]]; then
  echo "== zero_agent smoke =="
  export OMNI_KIT_ALLOW_ROOT=1
  export IsaacLab_PATH="${IsaacLab_PATH:-/workspace/IsaacLab}"
  export ORBIT_SURGICAL_PATH="${ORBIT_SURGICAL_PATH:-/workspace/orbit-surgical}"
  cd "$ORBIT_SURGICAL_PATH"
  "$IsaacLab_PATH/isaaclab.sh" -p source/standalone/environments/zero_agent.py \
    --task Isaac-Reach-Dual-STAR-IK-Rel-Play-v0 --num_envs 1 --headless
  cd "$ROOT_DIR"
fi

for block in d1 d2 d3; do
  echo "========== STUDY1_PROPER_BLOCK=$block =========="
  STUDY1_PROPER_BLOCK="$block" bash "$ROOT_DIR/scripts/run_study1_proper_v2.sh"
done

echo "== All blocks done. Merge summary: =="
PY="${ISAAC_PYTHON:-}"
if [[ -z "$PY" && -x "${IsaacLab_PATH:-/workspace/IsaacLab}/_isaac_sim/python.sh" ]]; then
  PY="${IsaacLab_PATH:-/workspace/IsaacLab}/_isaac_sim/python.sh"
elif command -v python3 >/dev/null 2>&1; then
  PY="python3"
elif command -v python >/dev/null 2>&1; then
  PY="python"
else
  echo "[WARN] No python — run manually: python3 scripts/merge_study1_proper_v2_summary.py"
  PY=""
fi
if [[ -n "$PY" ]]; then
  "$PY" "$ROOT_DIR/scripts/merge_study1_proper_v2_summary.py"
fi
echo "== Download artifacts/study1_proper_v2/ before VESSL Pause (ephemeral volume) =="
