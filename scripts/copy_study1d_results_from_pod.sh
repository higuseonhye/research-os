#!/usr/bin/env bash
# Copy 001D artifacts from RunPod to committed results/ (optional upgrade).
#
# D0 raw JSON (isaac_smoke):
#   scp -P <PORT> -i ~/.ssh/id_ed25519 \
#     root@<POD_IP>:/workspace/research-os/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/artifacts/study1d_occlusion_multimode/isaac_smoke/isaac_results.json \
#     experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1d_isaac/isaac_results.json
#
# D1 raw JSON (isaac_full):
#   scp -P <PORT> -i ~/.ssh/id_ed25519 \
#     root@<POD_IP>:/workspace/research-os/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/artifacts/study1d_occlusion_multimode/isaac_full/isaac_results.json \
#     experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1d_isaac/d1/isaac_results.json
#
# D1 aggregate after re-merge on pod (summary.json lives at artifact ROOT, not isaac_full/):
#   cat /workspace/research-os/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/artifacts/study1d_occlusion_multimode/summary.json
#   cat /workspace/research-os/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/artifacts/study1d_occlusion_multimode/aggregate_by_mode.csv
#
# Re-merge on pod (if old git read D0 smoke by mistake):
#   cd /workspace/research-os && git pull origin master
#   /isaac-sim/python.sh scripts/run_study1d.py --merge --full \
#     --artifact-root experiments/surgical_intelligence/exp_surg_001_execute_or_defer/artifacts/study1d_occlusion_multimode
set -euo pipefail
echo "See comments in this script for scp/copy commands."
