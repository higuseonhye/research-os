#!/usr/bin/env bash
# Download EXP-SURG-003 results from VESSL → local repo.
#
#   export VESSL_SSH="root@<host>"   # VESSL Connect tab
#   bash scripts/copy_exp_surg_003_from_vessl.sh
#   bash scripts/copy_exp_surg_003_from_vessl.sh mock
#   bash scripts/copy_exp_surg_003_from_vessl.sh isaac
#
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REMOTE="${VESSL_SSH:?Set VESSL_SSH=root@host from VESSL Connect tab}"
REMOTE_ROOT="${VESSL_REMOTE_ROOT:-/workspace/research-os}"
KEY="${VESSL_SSH_KEY:-$HOME/.ssh/id_ed25519}"
SCP=(scp -i "$KEY" -r)

WHAT="${1:-all}"

copy_mock() {
  local r="$REMOTE_ROOT/experiments/surgical_intelligence/exp_surg_003_wm_expansion/results/pilot_v0.1"
  local l="$ROOT_DIR/experiments/surgical_intelligence/exp_surg_003_wm_expansion/results/pilot_v0.1"
  mkdir -p "$l"
  "${SCP[@]}" "$REMOTE:$r/" "$l/"
  echo "[OK] mock pilot → $l"
}

copy_isaac() {
  local r="$REMOTE_ROOT/experiments/surgical_intelligence/exp_surg_003_wm_expansion/results/isaac_drift_pilot_v0.1"
  local l="$ROOT_DIR/experiments/surgical_intelligence/exp_surg_003_wm_expansion/results/isaac_drift_pilot_v0.1"
  mkdir -p "$l"
  "${SCP[@]}" "$REMOTE:$r/" "$l/"
  echo "[OK] Isaac drift → $l"
}

case "$WHAT" in
  mock) copy_mock ;;
  isaac) copy_isaac ;;
  all) copy_mock; copy_isaac ;;
  *) echo "Usage: $0 [mock|isaac|all]" >&2; exit 1 ;;
esac
