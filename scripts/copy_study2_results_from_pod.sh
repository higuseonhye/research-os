#!/usr/bin/env bash
# Copy Study2 Isaac artifacts from RunPod → committed results/ (optional full aggregate).
#
# Pod paths (same /workspace volume):
#   results/study2_dream_curriculum/isaac/<RUN_ID>/isaac_aggregate.json
#   results/study2_dream_curriculum/isaac/<RUN_ID>/summary.json
#   experiments/.../artifacts/isaac_runs/<RUN_ID>/<spec_id>/isaac_results.json
#
# Smoke run_id:  20260722T020640Z
# Full run_id:   20260722T042707Z
#
# Example (RunPod TCP / SSH — replace POD_IP, PORT, RUN_ID):
#
#   RUN_ID=20260722T042707Z
#   scp -P <PORT> -i ~/.ssh/id_ed25519 \
#     root@<POD_IP>:/workspace/research-os/results/study2_dream_curriculum/isaac/$RUN_ID/isaac_aggregate.json \
#     experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/isaac_full_v0.1/isaac_aggregate.json
#
#   scp -P <PORT> -i ~/.ssh/id_ed25519 \
#     root@<POD_IP>:/workspace/research-os/results/study2_dream_curriculum/isaac/$RUN_ID/summary.json \
#     experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/isaac_full_v0.1/summary_pod.json
#
# Re-merge on pod (if per-spec JSON exists but aggregate stale):
#   cd /workspace/research-os
#   export STUDY2_RUN_ID=20260722T042707Z
#   /isaac-sim/python.sh scripts/merge_study2_isaac_results.py \
#     --specs experiments/surgical_intelligence/exp_surg_002_dream_curriculum/artifacts/isaac_specs.json \
#     --results-dir experiments/surgical_intelligence/exp_surg_002_dream_curriculum/artifacts/isaac_runs/$STUDY2_RUN_ID \
#     --out-dir results/study2_dream_curriculum/isaac/$STUDY2_RUN_ID \
#     --git-commit "$(git rev-parse HEAD)"
set -euo pipefail
echo "See comments in this script for scp / re-merge commands."
