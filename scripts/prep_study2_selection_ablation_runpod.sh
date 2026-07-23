#!/usr/bin/env bash
# Prep RunPod for Study2 selection ablation (top-k + bottom-k → Isaac).
# Run after SSH, before or during lunch — bootstrap in tmux (~10–25 min).
set -euo pipefail

ROOT="${STUDY2_REPO_ROOT:-/workspace/research-os}"
REPO_URL="${STUDY2_REPO_URL:-https://github.com/higuseonhye/research-os.git}"
RECORDS="${STUDY2_RECORDS:-experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/mock_smoke_v0.2/records_seed43.json}"

echo "== Study2 selection ablation · Pod prep =="
echo "repo: $ROOT"
echo "records: $RECORDS"

if ! command -v git >/dev/null 2>&1 || ! command -v tmux >/dev/null 2>&1; then
  apt-get update
  apt-get install -y git tmux
fi

mkdir -p /workspace
if [ ! -d "$ROOT/.git" ]; then
  git clone "$REPO_URL" "$ROOT"
fi
cd "$ROOT"
git fetch origin master
git checkout master
git pull origin master

if [ ! -f "scripts/run_study2_selection_ablation_runpod.sh" ]; then
  echo "[FAIL] Missing selection ablation script — git pull research-os master (need 2aba765+)" >&2
  exit 1
fi

PY="${STUDY2_PYTHON:-/isaac-sim/python.sh}"
if [ ! -x "$PY" ]; then
  echo "[FAIL] Isaac Sim python missing at $PY — use nvcr.io/nvidia/isaac-sim:4.1.0 pod" >&2
  exit 1
fi

echo
echo "== Export preview (20 specs) =="
"$PY" scripts/export_study2_isaac_specs.py \
  --records "$RECORDS" \
  --out experiments/surgical_intelligence/exp_surg_002_dream_curriculum/artifacts/isaac_specs_preview.json \
  --top-k 5 \
  --strategy top_bottom \
  --mock-run-id mock_smoke_v0.2

"$PY" - <<'PY'
import json
from collections import Counter
from pathlib import Path

p = Path("experiments/surgical_intelligence/exp_surg_002_dream_curriculum/artifacts/isaac_specs_preview.json")
pack = json.loads(p.read_text())
c = Counter((s["dreamer"], s["selection_tier"], s["mock_informative"]) for s in pack["specs"])
print(f"n_specs={len(pack['specs'])} strategy={pack.get('export_strategy')}")
for k, v in sorted(c.items()):
    print(f"  {k}: {v}")
PY

if [ "${STUDY2_PREP_BOOTSTRAP:-0}" = "1" ]; then
  echo
  echo "== Bootstrap (10–25 min) — keep tmux open =="
  bash scripts/bootstrap_orbit_surgical_runpod.sh
  echo "[OK] Bootstrap complete"
else
  echo
  echo "Bootstrap skipped (STUDY2_PREP_BOOTSTRAP=0)."
  echo "If this is a NEW pod/volume, re-run with:"
  echo "  STUDY2_PREP_BOOTSTRAP=1 bash scripts/prep_study2_selection_ablation_runpod.sh"
  echo "Or same /workspace as prior Isaac run:"
  echo "  export STUDY2_SKIP_BOOTSTRAP=1"
fi

echo
echo "== Ready after lunch =="
echo "tmux new -s study2   # or: tmux attach -t study2"
echo "cd $ROOT"
if [ -d /workspace/IsaacLab ] && [ -d /workspace/orbit-surgical ]; then
  echo "export STUDY2_SKIP_BOOTSTRAP=1   # volume already bootstrapped"
fi
echo "bash scripts/run_study2_selection_ablation_runpod.sh"
echo
echo "Detach: Ctrl+B then D · Stop pod in console when done to save \$"
