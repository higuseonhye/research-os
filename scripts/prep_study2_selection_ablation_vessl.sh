#!/usr/bin/env bash
# VESSL prep for Study2 selection ablation — same flow as RunPod, /workspace mount.
set -euo pipefail

export CLOUD_PROVIDER=vessl
export CLOUD_WORKSPACE_DIR="${CLOUD_WORKSPACE_DIR:-/workspace}"
export STUDY2_REPO_ROOT="${STUDY2_REPO_ROOT:-$CLOUD_WORKSPACE_DIR/research-os}"
export WORKSPACE_DIR="${WORKSPACE_DIR:-$CLOUD_WORKSPACE_DIR}"
export IsaacLab_PATH="${IsaacLab_PATH:-$WORKSPACE_DIR/IsaacLab}"
export ORBIT_SURGICAL_PATH="${ORBIT_SURGICAL_PATH:-$WORKSPACE_DIR/orbit-surgical}"

exec bash "$(dirname "$0")/prep_study2_selection_ablation_runpod.sh"
