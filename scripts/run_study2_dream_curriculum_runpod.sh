#!/usr/bin/env bash
# EXP-SURG-002 Phase 1 — Dream curriculum: mock → Isaac (RunPod)
# Pre-reg: builder-os-private/working/research/stage2/study2_prereg_v0.1.md
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ISAAC_SIM_PATH="${ISAAC_SIM_PATH:-/isaac-sim}"
PY="${STUDY2_PYTHON:-$ISAAC_SIM_PATH/python.sh}"
if [ ! -x "$PY" ]; then
  PY="/isaac-sim/python.sh"
fi
if [ ! -x "$PY" ]; then
  echo "[FAIL] No Python on Isaac pod — set STUDY2_PYTHON=/isaac-sim/python.sh" >&2
  exit 1
fi
ARTIFACT_DIR="$ROOT_DIR/experiments/surgical_intelligence/exp_surg_002_dream_curriculum/artifacts"
DEFAULT_RECORDS="$ROOT_DIR/experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/mock_smoke_v0.2/records_seed43.json"
MOCK_EPISODES="${STUDY2_MOCK_EPISODES:-48}"
MOCK_SEEDS="${STUDY2_MOCK_SEEDS:-42,43,44}"
TOP_K="${STUDY2_TOP_K:-5}"
EXPORT_STRATEGY="${STUDY2_EXPORT_STRATEGY:-top_k}"
ISAAC_SEEDS="${STUDY2_ISAAC_SEEDS:-0,1,2,3,4}"

if [ "${STUDY2_SMOKE:-0}" = "1" ]; then
  TOP_K="${STUDY2_TOP_K:-2}"
  ISAAC_SEEDS="${STUDY2_ISAAC_SEEDS:-0,1}"
fi
ONSET_DEFAULT="${STUDY2_ONSET:-20}"
MAX_STEPS="${STUDY2_MAX_STEPS:-160}"
RUN_ID="${STUDY2_RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"

OUT_MOCK="$ROOT_DIR/results/study2_dream_curriculum/mock/$RUN_ID"
OUT_ISAAC="$ROOT_DIR/results/study2_dream_curriculum/isaac/$RUN_ID"
SPECS_OUT="$ARTIFACT_DIR/isaac_specs.json"
PER_SPEC_DIR="$ARTIFACT_DIR/isaac_runs/$RUN_ID"

mkdir -p "$OUT_MOCK" "$OUT_ISAAC" "$PER_SPEC_DIR" "$ARTIFACT_DIR"
cd "$ROOT_DIR"

commit_sha="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
echo "$commit_sha" > "$OUT_ISAAC/git_commit.txt"
cp -f "$ROOT_DIR/experiments/surgical_intelligence/exp_surg_002_dream_curriculum/config/sandbox_v0.1.yaml" \
  "$ARTIFACT_DIR/config_snapshot_${RUN_ID}.yaml"

echo "== EXP-SURG-002 Phase 1 =="
echo "run_id: $RUN_ID commit: $commit_sha"
echo "smoke: ${STUDY2_SMOKE:-0} skip_mock: ${STUDY2_SKIP_MOCK:-0}"
echo "mock episodes: $MOCK_EPISODES seeds: $MOCK_SEEDS top_k: $TOP_K strategy: $EXPORT_STRATEGY isaac_seeds: $ISAAC_SEEDS"

# --- Step 1: CPU mock (both dreamers) or reuse committed records ---
RECORDS_FOR_EXPORT=""
if [ "${STUDY2_SKIP_MOCK:-0}" = "1" ]; then
  RECORDS_FOR_EXPORT="${STUDY2_RECORDS:-$DEFAULT_RECORDS}"
  if [ ! -f "$RECORDS_FOR_EXPORT" ]; then
    echo "[FAIL] STUDY2_SKIP_MOCK=1 but records missing: $RECORDS_FOR_EXPORT"
    exit 1
  fi
  cp -f "$RECORDS_FOR_EXPORT" "$OUT_MOCK/records_merged.json"
  echo "Using precomputed mock records: $RECORDS_FOR_EXPORT"
else
  IFS=',' read -ra SEED_ARR <<< "$MOCK_SEEDS"
  mock_idx=0
  for mock_seed in "${SEED_ARR[@]}"; do
    mock_idx=$((mock_idx + 1))
    sub="$OUT_MOCK/seed_${mock_seed}"
    mkdir -p "$sub"
    "$PY" scripts/run_study2_dream_curriculum_mock.py \
      --compare \
      --episodes "$MOCK_EPISODES" \
      --seed "$mock_seed" \
      || true
    latest="$(ls -td "$ROOT_DIR/results/study2_dream_curriculum/mock"/*/ 2>/dev/null | head -1)"
    if [ -n "$latest" ]; then
      cp -f "$latest/summary.json" "$sub/summary.json"
      cp -f "$latest/records.json" "$sub/records.json"
    fi
  done

  LATEST_MOCK="$(ls -td "$ROOT_DIR/results/study2_dream_curriculum/mock"/*/ 2>/dev/null | head -1)"
  if [ -z "$LATEST_MOCK" ] || [ ! -f "$LATEST_MOCK/records.json" ]; then
    echo "[FAIL] No mock records.json — run mock manually first or set STUDY2_SKIP_MOCK=1"
    exit 1
  fi
  RECORDS_FOR_EXPORT="$LATEST_MOCK/records.json"
  cp -f "$RECORDS_FOR_EXPORT" "$OUT_MOCK/records_merged.json"
  cp -f "$LATEST_MOCK/summary.json" "$OUT_MOCK/summary_merged.json"
fi

"$PY" scripts/export_study2_isaac_specs.py \
  --records "$RECORDS_FOR_EXPORT" \
  --out "$SPECS_OUT" \
  --top-k "$TOP_K" \
  --strategy "$EXPORT_STRATEGY" \
  --mock-run-id "$(basename "$(dirname "$RECORDS_FOR_EXPORT")")"

# --- Step 2: Isaac bootstrap ---
if [ "${STUDY2_SKIP_BOOTSTRAP:-0}" != "1" ]; then
  bash "$ROOT_DIR/scripts/bootstrap_orbit_surgical_runpod.sh"
else
  echo "Skipping bootstrap (STUDY2_SKIP_BOOTSTRAP=1)"
fi

export OMNI_KIT_ALLOW_ROOT=1
export IsaacLab_PATH="${ISAACLAB_PATH:-/workspace/IsaacLab}"
ORBIT_SURGICAL_PATH="${ORBIT_SURGICAL_PATH:-/workspace/orbit-surgical}"
export ORBIT_SURGICAL_PATH
TASK="${ORBIT_REACH_TASK:-Isaac-Reach-Dual-STAR-IK-Rel-Play-v0}"
export TASK

# --- Step 3: Isaac per spec ---
export ROOT_DIR SPECS_OUT PER_SPEC_DIR IsaacLab_PATH ORBIT_SURGICAL_PATH TASK ISAAC_SEEDS MAX_STEPS ONSET_DEFAULT

"$PY" "$ROOT_DIR/scripts/run_study2_isaac_loop.py" \
  --specs "$SPECS_OUT" \
  --results-dir "$PER_SPEC_DIR" \
  --isaaclab "$IsaacLab_PATH" \
  --orbit "$ORBIT_SURGICAL_PATH" \
  --task "$TASK" \
  --seeds "$ISAAC_SEEDS" \
  --max-steps "$MAX_STEPS" \
  --onset-default "$ONSET_DEFAULT" \
  || true

# --- Step 4: Merge ---
"$PY" scripts/merge_study2_isaac_results.py \
  --specs "$SPECS_OUT" \
  --results-dir "$PER_SPEC_DIR" \
  --out-dir "$OUT_ISAAC" \
  --git-commit "$commit_sha"

echo "== Done EXP-SURG-002 Phase 1 =="
echo "mock: $OUT_MOCK"
echo "isaac: $OUT_ISAAC"
echo "specs: $SPECS_OUT"
echo "aggregate: $OUT_ISAAC/isaac_aggregate.json"
