#!/usr/bin/env bash
# EXP-SURG-002 selection ablation — top-k + bottom-k mock rank → Isaac (RunPod)
# Pre-reg: docs/stage2/study2_phase1_design_v0.1.md (selection ablation)
set -euo pipefail

export STUDY2_SKIP_MOCK=1
export STUDY2_EXPORT_STRATEGY=top_bottom
export STUDY2_TOP_K="${STUDY2_TOP_K:-5}"
export STUDY2_ISAAC_SEEDS="${STUDY2_ISAAC_SEEDS:-0,1,2,3,4}"
export STUDY2_RECORDS="${STUDY2_RECORDS:-experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/mock_smoke_v0.2/records_seed43.json}"

# Phase 2 defaults (override via env):
#   STUDY2_CONFIG=sandbox_v0.2.yaml
#   STUDY2_RUNNER=study1d
#   STUDY2_RECORDS=.../mock_smoke_v0.4/records_seed43.json

exec bash "$(dirname "$0")/run_study2_dream_curriculum_runpod.sh"
