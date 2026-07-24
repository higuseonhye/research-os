#!/usr/bin/env bash
# Download Paper 001 proper v2.0 artifacts from VESSL → local results/
#
#   export VESSL_SSH="root@<host>"   # from VESSL Connect tab
#   bash scripts/copy_study1_proper_v2_from_vessl.sh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REMOTE="${VESSL_SSH:?Set VESSL_SSH=root@host}"
REMOTE_ROOT="${VESSL_REMOTE_ROOT:-/workspace/research-os}"
ART="$REMOTE_ROOT/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/artifacts/study1_proper_v2"
LOCAL_ART="$ROOT_DIR/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/artifacts/study1_proper_v2"
LOCAL_RES="$ROOT_DIR/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1_proper_v2"

KEY="${VESSL_SSH_KEY:-$HOME/.ssh/id_ed25519}"
SCP=(scp -i "$KEY" -r)

mkdir -p "$LOCAL_ART" "$LOCAL_RES"
"${SCP[@]}" "$REMOTE:$ART/" "$LOCAL_ART/"

cd "$ROOT_DIR"
python scripts/merge_study1_proper_v2_summary.py
echo "[OK] Local merge done → $LOCAL_RES/summary.json"
