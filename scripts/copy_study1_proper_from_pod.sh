#!/usr/bin/env bash
# Copy Paper 1 Phase C (001D full n=20) from RunPod → committed results/study1_proper/
#
# Pod paths:
#   experiments/surgical_intelligence/exp_surg_001_execute_or_defer/artifacts/study1d_occlusion_multimode/isaac_full/isaac_results.json
#   experiments/surgical_intelligence/exp_surg_001_execute_or_defer/artifacts/study1d_occlusion_multimode/summary.json
#   experiments/surgical_intelligence/exp_surg_001_execute_or_defer/artifacts/study1d_occlusion_multimode/aggregate_by_mode.csv
#
# Example:
#   scp -P <PORT> -i ~/.ssh/id_ed25519 \
#     root@<POD_IP>:/workspace/research-os/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/artifacts/study1d_occlusion_multimode/isaac_full/isaac_results.json \
#     experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1_proper/isaac_results.json
#
#   scp -P <PORT> -i ~/.ssh/id_ed25519 \
#     root@<POD_IP>:/workspace/research-os/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/artifacts/study1d_occlusion_multimode/aggregate_by_mode.csv \
#     experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1_proper/tables/aggregate_by_mode.csv
set -euo pipefail
echo "See comments in this script for scp commands."
