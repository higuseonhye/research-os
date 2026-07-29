#!/usr/bin/env bash
# EXP-SURG-003 on VESSL — mock and/or Isaac drift.
#
#   EXP_SURG_003_MODE=mock|isaac_drift|both  (default: isaac_drift)
#
set -euo pipefail

export CLOUD_PROVIDER=vessl
export CLOUD_WORKSPACE_DIR="${CLOUD_WORKSPACE_DIR:-/workspace}"
export REPO_ROOT="${REPO_ROOT:-$CLOUD_WORKSPACE_DIR/research-os}"
export WORKSPACE_DIR="${WORKSPACE_DIR:-$CLOUD_WORKSPACE_DIR}"
export IsaacLab_PATH="${IsaacLab_PATH:-$WORKSPACE_DIR/IsaacLab}"
export ORBIT_SURGICAL_PATH="${ORBIT_SURGICAL_PATH:-$WORKSPACE_DIR/orbit-surgical}"

MODE="${EXP_SURG_003_MODE:-isaac_drift}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$REPO_ROOT"
git pull origin master 2>/dev/null || true

case "$MODE" in
  mock)
    exec bash "$SCRIPT_DIR/run_exp_surg_003_mock_vessl.sh" "$@"
    ;;
  isaac_drift)
    exec bash "$SCRIPT_DIR/run_exp_surg_003_drift.sh"
    ;;
  both)
    bash "$SCRIPT_DIR/run_exp_surg_003_mock_vessl.sh" "$@"
    export EXP_SURG_003_SKIP_BOOTSTRAP=1
    exec bash "$SCRIPT_DIR/run_exp_surg_003_drift.sh"
    ;;
  *)
    echo "[FAIL] Unknown EXP_SURG_003_MODE=$MODE (mock|isaac_drift|both)" >&2
    exit 1
    ;;
esac
