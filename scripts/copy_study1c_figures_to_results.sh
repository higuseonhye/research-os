#!/usr/bin/env bash
# Copy 001C merge figures from gitignored artifacts/ to committed results/study1c_isaac/figures/
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ART="$ROOT/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/artifacts/study1c_severity_delay_surface/figures"
OUT="$ROOT/experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1c_isaac/figures"

if [[ ! -d "$ART" ]]; then
  echo "Missing: $ART" >&2
  exit 1
fi

mkdir -p "$OUT"
cp -v "$ART"/*.png "$OUT"/
echo "Copied to $OUT"
ls -la "$OUT"/*.png
