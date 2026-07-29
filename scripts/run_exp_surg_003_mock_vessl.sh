#!/usr/bin/env bash
# EXP-SURG-003 mock pilot on VESSL (CPU-friendly · no Isaac required).
#
# Usage (Jupyter terminal or SSH):
#   cd /workspace/research-os && git pull origin master
#   bash scripts/run_exp_surg_003_mock_vessl.sh
#   bash scripts/run_exp_surg_003_mock_vessl.sh --smoke
#
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="${REPO_ROOT:-$ROOT_DIR}"
OUT="${OUT:-$REPO/experiments/surgical_intelligence/exp_surg_003_wm_expansion/results/pilot_v0.1}"
CFG="${CFG:-$REPO/experiments/surgical_intelligence/exp_surg_003_wm_expansion/config/pilot_v0.1.yaml}"
SMOKE="${SMOKE:-0}"

for arg in "$@"; do
  case "$arg" in
    --smoke) SMOKE=1 ;;
  esac
done

cd "$REPO"
commit_sha="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
echo "== EXP-SURG-003 mock pilot (VESSL) commit=$commit_sha =="

# Prefer Isaac Sim Python on GPU workspace; else system python3
PY=""
for cand in \
  "${ISAAC_SIM_PATH:-/isaac-sim}/python.sh" \
  "/isaac-sim/python.sh" \
  python3 \
  python; do
  if [ -x "$cand" ] || command -v "$cand" >/dev/null 2>&1; then
    PY="$cand"
    break
  fi
done
if [ -z "$PY" ]; then
  echo "[FAIL] no python found" >&2
  exit 1
fi
echo "python: $PY"

"$PY" -m pip install -q torch pyyaml numpy 2>/dev/null || true

mkdir -p "$(dirname "$OUT")"
ARGS=(--config "$CFG" --out-dir "$OUT")
if [ "$SMOKE" = "1" ]; then
  ARGS+=(--smoke)
fi

set +e
"$PY" "$REPO/scripts/run_exp_surg_003_pilot.py" "${ARGS[@]}" | tee "$OUT/pilot_stdout.log"
rc=${PIPESTATUS[0]}
set -e

echo "$commit_sha" > "$OUT/git_commit.txt"
if [ "$rc" -ne 0 ]; then
  echo "[FAIL] mock pilot exit $rc" >&2
  exit "$rc"
fi
echo "[OK] wrote $OUT/summary.json"
