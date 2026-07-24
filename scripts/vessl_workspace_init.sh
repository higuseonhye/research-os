#!/usr/bin/env bash
# VESSL workspace init script (paste in Advanced → Init script, or run once after first SSH/Jupyter).
set -euo pipefail

export ACCEPT_EULA="${ACCEPT_EULA:-Y}"
export PRIVACY_CONSENT="${PRIVACY_CONSENT:-Y}"
export OMNI_KIT_ALLOW_ROOT="${OMNI_KIT_ALLOW_ROOT:-1}"

WORKSPACE="${CLOUD_WORKSPACE_DIR:-/workspace}"
REPO="${STUDY2_REPO_ROOT:-$WORKSPACE/research-os}"
REPO_URL="${STUDY2_REPO_URL:-https://github.com/higuseonhye/research-os.git}"

mkdir -p "$WORKSPACE"

if ! command -v git >/dev/null 2>&1 || ! command -v tmux >/dev/null 2>&1; then
  apt-get update
  apt-get install -y git tmux
fi

if [ ! -d "$REPO/.git" ]; then
  git clone "$REPO_URL" "$REPO"
fi

cd "$REPO"
git fetch origin master
git checkout master
git pull origin master

echo "[OK] VESSL workspace ready: $REPO"
echo "Next: STUDY2_PREP_BOOTSTRAP=1 bash scripts/prep_study2_selection_ablation_vessl.sh"
