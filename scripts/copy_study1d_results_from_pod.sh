#!/usr/bin/env bash
# Copy full isaac_results.json from RunPod to committed results/ (optional upgrade).
#
# Local PC (PowerShell / Git Bash) — replace POD_IP and PORT from RunPod Connect tab:
#   scp -P <PORT> -i ~/.ssh/id_ed25519 \
#     root@<POD_IP>:/workspace/research-os/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/artifacts/study1d_occlusion_multimode/isaac_smoke/isaac_results.json \
#     experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1d_isaac/isaac_results.json
#
# Or on pod before Stop:
#   cp artifacts/study1d_occlusion_multimode/isaac_smoke/isaac_results.json \
#      results/study1d_isaac/isaac_results.json
set -euo pipefail
echo "See comments in this script for scp/copy commands."
