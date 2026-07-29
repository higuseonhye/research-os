#!/usr/bin/env bash
# VESSL prep for EXP-SURG-003 (Paper 002 WM expansion).
set -euo pipefail

export CLOUD_PROVIDER=vessl
export CLOUD_WORKSPACE_DIR="${CLOUD_WORKSPACE_DIR:-/workspace}"
export REPO_ROOT="${REPO_ROOT:-$CLOUD_WORKSPACE_DIR/research-os}"
export WORKSPACE_DIR="${WORKSPACE_DIR:-$CLOUD_WORKSPACE_DIR}"
export IsaacLab_PATH="${IsaacLab_PATH:-$WORKSPACE_DIR/IsaacLab}"
export ORBIT_SURGICAL_PATH="${ORBIT_SURGICAL_PATH:-$WORKSPACE_DIR/orbit-surgical}"
REPO_URL="${REPO_URL:-https://github.com/higuseonhye/research-os.git}"

echo "== EXP-SURG-003 VESSL prep =="
echo "repo: $REPO_ROOT"

if ! command -v git >/dev/null 2>&1 || ! command -v tmux >/dev/null 2>&1; then
  apt-get update
  apt-get install -y git tmux
fi

mkdir -p "$CLOUD_WORKSPACE_DIR"
if [ ! -d "$REPO_ROOT/.git" ]; then
  git clone "$REPO_URL" "$REPO_ROOT"
fi
cd "$REPO_ROOT"
git fetch origin master
git checkout master
git pull origin master

if [ ! -f "scripts/run_exp_surg_003_vessl.sh" ]; then
  echo "[FAIL] Missing EXP-SURG-003 scripts — git pull master (need 97bded0+)" >&2
  exit 1
fi

if [ "${EXP_SURG_003_PREP_BOOTSTRAP:-0}" = "1" ]; then
  echo "== Bootstrap IsaacLab + orbit-surgical (15–25 min) — keep tmux open =="
  bash scripts/bootstrap_orbit_surgical_runpod.sh
  echo "[OK] Bootstrap complete"
else
  echo "Bootstrap skipped. Fresh volume:"
  echo "  EXP_SURG_003_PREP_BOOTSTRAP=1 bash scripts/prep_exp_surg_003_vessl.sh"
  echo "Existing /workspace/IsaacLab:"
  echo "  export EXP_SURG_003_SKIP_BOOTSTRAP=1"
fi

echo
echo "== Ready =="
echo "tmux new -s exp003"
echo "cd $REPO_ROOT"
echo
echo "# Mock pilot (CPU · no Isaac):"
echo "bash scripts/run_exp_surg_003_mock_vessl.sh --smoke"
echo "bash scripts/run_exp_surg_003_mock_vessl.sh"
echo
echo "# Isaac drift (GPU · after bootstrap):"
echo "export EXP_SURG_003_SKIP_BOOTSTRAP=1"
echo "bash scripts/run_exp_surg_003_vessl.sh"
echo
echo "Pause workspace when idle to save credits."
