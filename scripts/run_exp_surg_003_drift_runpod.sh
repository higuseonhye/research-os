#!/usr/bin/env bash
# EXP-SURG-003 drift on RunPod — delegates to unified runner.
set -euo pipefail
exec bash "$(dirname "$0")/run_exp_surg_003_drift.sh"
