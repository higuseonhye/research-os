#!/usr/bin/env bash
# Copy full isaac_results.json from RunPod to committed results/ (optional upgrade).
#
# D0 (isaac_smoke):
#   scp -P <PORT> -i ~/.ssh/id_ed25519 \
#     root@<POD_IP>:/workspace/research-os/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/artifacts/study1d_occlusion_multimode/isaac_smoke/isaac_results.json \
#     experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1d_isaac/isaac_results.json
#
# D1 (isaac_full):
#   scp -P <PORT> -i ~/.ssh/id_ed25519 \
#     root@<POD_IP>:/workspace/research-os/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/artifacts/study1d_occlusion_multimode/isaac_full/isaac_results.json \
#     experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1d_isaac/d1/isaac_results.json
#
# Or on pod before Stop (D1):
#   mkdir -p results/study1d_isaac/d1
#   cp artifacts/study1d_occlusion_multimode/isaac_full/isaac_results.json results/study1d_isaac/d1/
#   cp artifacts/study1d_occlusion_multimode/isaac_full/summary.json results/study1d_isaac/d1/
#   cp artifacts/study1d_occlusion_multimode/aggregate_by_mode.csv results/study1d_isaac/d1/tables/  # if merged at root
set -euo pipefail
echo "See comments in this script for scp/copy commands."
