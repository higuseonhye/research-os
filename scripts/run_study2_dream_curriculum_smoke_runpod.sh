#!/usr/bin/env bash
# EXP-SURG-002 Isaac smoke on RunPod (~$1 Community · TOP_K=2 · seeds 0,1)
# Uses committed mock records (seed 43); skips CPU mock on pod.
set -euo pipefail

export STUDY2_SMOKE=1
export STUDY2_SKIP_MOCK=1
export STUDY2_RECORDS="${STUDY2_RECORDS:-experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/mock_smoke_v0.2/records_seed43.json}"

exec bash "$(dirname "$0")/run_study2_dream_curriculum_runpod.sh"
