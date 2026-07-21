#!/usr/bin/env bash
# EXP-SURG-002 Phase 1 — Dream curriculum: mock → Isaac (RunPod)
# Pre-reg: builder-os-private/working/research/stage2/study2_prereg_v0.1.md
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARTIFACT_DIR="$ROOT_DIR/experiments/surgical_intelligence/exp_surg_002_dream_curriculum/artifacts"
MOCK_EPISODES="${STUDY2_MOCK_EPISODES:-48}"
MOCK_SEEDS="${STUDY2_MOCK_SEEDS:-42,43,44}"
TOP_K="${STUDY2_TOP_K:-5}"
ISAAC_SEEDS="${STUDY2_ISAAC_SEEDS:-0,1,2,3,4}"
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
echo "mock episodes: $MOCK_EPISODES seeds: $MOCK_SEEDS top_k: $TOP_K"

# --- Step 1: CPU mock (both dreamers) ---
IFS=',' read -ra SEED_ARR <<< "$MOCK_SEEDS"
mock_idx=0
for mock_seed in "${SEED_ARR[@]}"; do
  mock_idx=$((mock_idx + 1))
  sub="$OUT_MOCK/seed_${mock_seed}"
  mkdir -p "$sub"
  python scripts/run_study2_dream_curriculum_mock.py \
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

# Use latest compare records for spec export
LATEST_MOCK="$(ls -td "$ROOT_DIR/results/study2_dream_curriculum/mock"/*/ 2>/dev/null | head -1)"
if [ -z "$LATEST_MOCK" ] || [ ! -f "$LATEST_MOCK/records.json" ]; then
  echo "[FAIL] No mock records.json — run mock manually first"
  exit 1
fi
cp -f "$LATEST_MOCK/records.json" "$OUT_MOCK/records_merged.json"
cp -f "$LATEST_MOCK/summary.json" "$OUT_MOCK/summary_merged.json"

python scripts/export_study2_isaac_specs.py \
  --records "$LATEST_MOCK/records.json" \
  --out "$SPECS_OUT" \
  --top-k "$TOP_K" \
  --mock-run-id "$(basename "$LATEST_MOCK")"

# --- Step 2: Isaac bootstrap ---
bash "$ROOT_DIR/scripts/bootstrap_orbit_surgical_runpod.sh"

export OMNI_KIT_ALLOW_ROOT=1
export IsaacLab_PATH="${ISAACLAB_PATH:-/workspace/IsaacLab}"
ORBIT_SURGICAL_PATH="${ORBIT_SURGICAL_PATH:-/workspace/orbit-surgical}"
export ORBIT_SURGICAL_PATH
TASK="${ORBIT_REACH_TASK:-Isaac-Reach-Dual-STAR-IK-Rel-Play-v0}"
export TASK

# --- Step 3: Isaac per spec ---
export ROOT_DIR SPECS_OUT PER_SPEC_DIR IsaacLab_PATH ORBIT_SURGICAL_PATH TASK ISAAC_SEEDS MAX_STEPS ONSET_DEFAULT

python3 << 'PY'
import json
import os
import subprocess
from pathlib import Path

root = Path(os.environ["ROOT_DIR"])
specs_path = Path(os.environ["SPECS_OUT"])
per_spec = Path(os.environ["PER_SPEC_DIR"])
isaaclab = Path(os.environ["IsaacLab_PATH"])
orbit = Path(os.environ["ORBIT_SURGICAL_PATH"])
task = os.environ["TASK"]
seeds = os.environ["ISAAC_SEEDS"]
max_steps = os.environ["MAX_STEPS"]
onset_default = os.environ["ONSET_DEFAULT"]

pack = json.loads(specs_path.read_text(encoding="utf-8"))
failures = []

for spec in pack["specs"]:
    spec_id = spec["spec_id"]
    out = per_spec / spec_id
    out.mkdir(parents=True, exist_ok=True)
    shift = spec["shift_m"]
    onset = int(spec.get("onset_step", onset_default))
    (out / "spec.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")

    cmd = [
        str(isaaclab / "isaaclab.sh"),
        "-p",
        str(root / "scripts/orbit_reach_study1a_counterfactual.py"),
        "--experiment-id",
        f"EXP-SURG-002-{spec_id}",
        "--task",
        task,
        "--num_envs",
        "1",
        "--seeds",
        seeds,
        "--onset",
        str(onset),
        "--max-steps",
        max_steps,
        "--shift-m",
        str(shift),
        "--include-continue",
        "--replan-delays",
        "0",
        "--out-dir",
        str(out),
        "--headless",
    ]
    print(f"[Isaac] {spec_id} shift={shift} onset={onset}", flush=True)
    rc = subprocess.run(cmd, cwd=str(orbit)).returncode
    if rc != 0:
        failures.append(spec_id)
        print(f"[WARN] Isaac failed for {spec_id} rc={rc}", flush=True)

if failures:
    import sys
    print(f"[WARN] Failed specs: {failures}", file=sys.stderr)
PY

# --- Step 4: Merge ---
python scripts/merge_study2_isaac_results.py \
  --specs "$SPECS_OUT" \
  --results-dir "$PER_SPEC_DIR" \
  --out-dir "$OUT_ISAAC" \
  --git-commit "$commit_sha"

echo "== Done EXP-SURG-002 Phase 1 =="
echo "mock: $OUT_MOCK"
echo "isaac: $OUT_ISAAC"
echo "specs: $SPECS_OUT"
echo "aggregate: $OUT_ISAAC/isaac_aggregate.json"
