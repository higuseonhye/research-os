#!/usr/bin/env bash
# Promote Isaac EE trace captures from VESSL artifacts path.
# Prefer Jupyter download; this script documents expected layout.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$ROOT/docs/paper1/figures/isaac_captures"
mkdir -p "$DEST"
echo "Place *_ee_trace.json and capture_manifest.json under:"
echo "  $DEST"
echo "Then: python scripts/plot_paper1_from_ee_traces.py"
