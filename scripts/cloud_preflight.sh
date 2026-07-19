#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/experiments/srfm_quick_prototype/demo_artifacts"
LOG_PATH="$OUT_DIR/cloud_preflight_$(date -u +%Y%m%dT%H%M%SZ).log"

mkdir -p "$OUT_DIR"

run_check() {
  local title="$1"
  shift
  {
    echo
    echo "## $title"
    echo "\$ $*"
    "$@" 2>&1
  } | tee -a "$LOG_PATH"
}

{
  echo "# SRFM Cloud Preflight"
  echo "timestamp_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "root_dir: $ROOT_DIR"
} | tee "$LOG_PATH"

run_check "OS" bash -lc 'uname -a; if command -v lsb_release >/dev/null 2>&1; then lsb_release -a; else cat /etc/os-release; fi'
run_check "GPU" bash -lc 'if command -v nvidia-smi >/dev/null 2>&1; then nvidia-smi; else echo "nvidia-smi not found"; fi'
run_check "Python" bash -lc 'if command -v python3 >/dev/null 2>&1; then python3 --version; else echo "python3 not found"; fi'
run_check "Git" bash -lc 'if command -v git >/dev/null 2>&1; then git --version; else echo "git not found"; fi'
run_check "Disk" df -h
run_check "Memory" free -h
run_check "Docker" bash -lc 'if command -v docker >/dev/null 2>&1; then docker --version; docker info 2>&1 | sed -n "1,80p"; else echo "docker not found"; fi'
run_check "Conda" bash -lc 'if command -v conda >/dev/null 2>&1; then conda --version; elif command -v micromamba >/dev/null 2>&1; then micromamba --version; else echo "conda/micromamba not found"; fi'

{
  echo
  echo "# Summary"
  echo "log_path: $LOG_PATH"
  echo "next_step: paste this log into experiments/srfm_quick_prototype/cloud_run_log.md"
} | tee -a "$LOG_PATH"

echo "$LOG_PATH"
