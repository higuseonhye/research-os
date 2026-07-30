# Paper 002 / EXP-SURG-003 — VESSL runbook v0.1

> **When to use:** Local laptop too slow · RunPod SSH/proxy unstable  
> **Same infra as Study 2:** [vessl_isaac_setup_v0.1.md](../stage2/vessl_isaac_setup_v0.1.md) · custom Isaac image · `/workspace` mount
>
> **Current state:** model-order confirmatory v1.0 completed and pushed as
> `73a7e16`; the VESSL workspace may remain paused. Use this runbook for audit
> or an exact reproduction, not for additional confirmatory sampling.

---

## Why VESSL for Paper 002

| Path | Needs GPU | Notes |
| --- | --- | --- |
| **Mock pilot** (GRU + MPC + arms A/B/C) | No (CPU OK) | ~3–15 min · validates L1 vs L3 separation |
| **Isaac drift** (persistent target M1) | Yes | ORBIT Reach · trajectory data for WM |

Both run on the **same VESSL workspace** (Isaac image). Mock can start **before** bootstrap finishes if you only need CPU.

---

## One-time workspace (reuse Study 2 if available)

1. [VESSL Cloud](https://cloud.vessl.ai) → **New Workspace**
2. **GPU:** RTX 4090 24GB (Isaac drift) · or CPU workspace for mock-only
3. **Mount:** cluster storage at **`/workspace`**
4. **Image:** `ghcr.io/YOUR_GH_USER/vessl-isaac-sim:4.1.0` ([docker README](../../docker/vessl-isaac-sim-4.1.0/README.md))
5. **Env:** `ACCEPT_EULA=Y`, `PRIVACY_CONSENT=Y`, `OMNI_KIT_ALLOW_ROOT=1`
6. **Init script:** `scripts/vessl_workspace_init.sh`

**Billing:** Pause workspace when idle.

---

## Connect

**Jupyter (8888)** → Terminal (recommended):

```bash
cd /workspace/research-os && git pull origin master
tmux new -s exp003
```

Or SSH: `vesslctl workspace ssh <slug>`

---

## Step 1 — Prep

```bash
# First time on empty volume (15–25 min bootstrap)
EXP_SURG_003_PREP_BOOTSTRAP=1 bash scripts/prep_exp_surg_003_vessl.sh

# Reuse existing IsaacLab on /workspace
bash scripts/prep_exp_surg_003_vessl.sh
```

---

## Step 2 — Mock pilot (milestone 1 · no Isaac)

```bash
# Smoke (~2–3 min)
bash scripts/run_exp_surg_003_mock_vessl.sh --smoke

# Full pilot (5 seeds)
bash scripts/run_exp_surg_003_mock_vessl.sh
```

**Output:** `experiments/.../exp_surg_003_wm_expansion/results/pilot_v0.1/summary.json`

Check `summary.C_vs_B.delta_prediction_error > 0` before Isaac spend.

---

## Step 3 — Isaac drift (GPU)

```bash
# Quick smoke (1 seed · skip zero_agent if scripted_smoke already passed)
export EXP_SURG_003_SKIP_BOOTSTRAP=1
export EXP_SURG_003_ZERO_AGENT=0
export DISABLE_FABRIC=1
export OUT="$PWD/experiments/surgical_intelligence/exp_surg_003_wm_expansion/results/isaac_drift_smoke"
export SEEDS=0
export ONSET=40
export MAX_STEPS=200
export DRIFT_SPEED=0.0003
export DRIFT_DURATION=80
bash scripts/run_exp_surg_003_drift.sh
```

**Direct Python (same flags):** `orbit_reach_drift.py` uses `--max-steps`, `--onset`, `--drift-speed`, `--drift-axis`, `--out-dir` — **not** `--steps` / `--drift-onset` / `--out` (those are `orbit_reach_scripted_smoke.py`).

```bash
/workspace/IsaacLab/isaaclab.sh -p scripts/orbit_reach_drift.py \
  --task Isaac-Reach-Dual-STAR-IK-Rel-Play-v0 \
  --num_envs 1 --seed 0 --episodes 1 --headless --disable_fabric \
  --onset 40 --max-steps 200 --drift-speed 0.0003 --drift-axis x --drift-duration 80 \
  --out-dir experiments/surgical_intelligence/exp_surg_003_wm_expansion/results/isaac_drift_smoke
```

**Output:** `.../isaac_drift_smoke/isaac_drift_results.json` (+ trajectories)

**Full pilot via wrapper:**

```bash
export EXP_SURG_003_SKIP_BOOTSTRAP=1
export EXP_SURG_003_ZERO_AGENT=0
export DISABLE_FABRIC=1
bash scripts/run_exp_surg_003_vessl.sh
```

**Tunable env:**

| Var | Default | Meaning |
| --- | --- | --- |
| `SEEDS` | `0,1,2,3,4` | Episode seeds |
| `ONSET` | `20` | Drift start step |
| `MAX_STEPS` | `160` | Episode length (steps) |
| `DRIFT_SPEED` | `0.01` | m per step |
| `DRIFT_AXIS` | `x` | `x` · `y` · `z` |
| `DRIFT_DURATION` | `40` | Drift steps |
| `DISABLE_FABRIC` | `0` | Set `1` on VESSL headless if fabric errors |
| `EXP_SURG_003_ZERO_AGENT` | `1` | Set `0` to skip after scripted_smoke passed |

**Output:** `results/isaac_drift_pilot_v0.1/isaac_drift_results.json`

---

## Step 3B - L1-vs-L3 model-order pilot (GPU)

This is the active Paper 002 experiment. It uses static-first seed selection,
paired A/B/C/D arms, H=10 target prediction, static retention, and H4 controls.
Each Ep2 seed-arm-condition cell runs in a fresh Isaac process. This v0.3
isolation closes the arm-dependent reset carryover found in v0.2.

```bash
cd /workspace/research-os
git switch codex/paper002-l1-l3-confirmatory
git pull --ff-only

export DISABLE_FABRIC=1
unset EXP_SURG_003_SKIP_BOOTSTRAP
export EXP_SURG_003_ZERO_AGENT=0
bash scripts/run_exp_surg_003_model_order_vessl.sh --smoke

export EXP_SURG_003_SKIP_BOOTSTRAP=1
export EXP_SURG_003_ZERO_AGENT=0
bash scripts/run_exp_surg_003_model_order_vessl.sh
```

The run is resumable. Final decision output:

```bash
python3 -c "import json; d=json.load(open('experiments/surgical_intelligence/exp_surg_003_wm_expansion/results/isaac_model_order_pilot_v0.3/isaac_model_order_results.json')); print(json.dumps({k:d[k] for k in ['validity','ep2_by_arm','primary_effect','static_retention','h4_gate_controls','pilot_decisions','pilot_pass']},indent=2))"
```

Protocol and decision rules:
[paper002_model_order_protocol_v0.3.md](paper002_model_order_protocol_v0.3.md).
Do not run confirmatory seeds until this pilot is audited and the preregistration
is frozen.

## Step 3C - Frozen model-order confirmatory v1.0

Run only from the immutable preregistration tag. The confirmatory uses fresh
candidate seeds 300-339, selects the first 10 static-eligible seeds before
treatment, and executes 400 process-isolated Ep2 cells.

```bash
cd /workspace/research-os
git fetch origin --tags
git switch codex/paper002-l1-l3-confirmatory
git pull --ff-only
git describe --tags --exact-match

export CONFIG="$PWD/experiments/surgical_intelligence/exp_surg_003_wm_expansion/config/model_order_confirmatory_v1.0.json"
export OUT="$PWD/experiments/surgical_intelligence/exp_surg_003_wm_expansion/results/isaac_model_order_confirmatory_v1.0"
EXP_SURG_003_SKIP_BOOTSTRAP=1 EXP_SURG_003_ZERO_AGENT=0 DISABLE_FABRIC=1 \
  bash scripts/run_exp_surg_003_model_order_vessl.sh
```

The exact tag must be `paper002-model-order-confirmatory-v1.0`. Do not alter
the config, seed list, conditions, endpoints, or decision thresholds after
starting the run. See
[the frozen preregistration](paper002_model_order_confirmatory_prereg_v1.0.md).

---

## Step 4 — Pull results to Windows

```powershell
$env:VESSL_SSH = "root@<VESSL_SSH_HOST>"   # Connect tab

bash scripts/copy_exp_surg_003_from_vessl.sh all
# or: mock · isaac
```

Or download via Jupyter file browser before **Pause**.

---

## Failure policy

| Symptom | Action |
| --- | --- |
| `zero_agent` FAIL (futex / GPU) | Log infra blocker · do **not** retry spiral on same host |
| `ssh.runpod.io` N/A on VESSL | Use Jupyter :8888 |
| Mock C ≈ B | Tune drift in `config/pilot_v0.1.yaml` · re-run mock only |

**Never** `pkill -9 -f '/isaac-sim/kit/kit'`.

---

## Scripts map

| Script | Role |
| --- | --- |
| `prep_exp_surg_003_vessl.sh` | Clone · pull · optional bootstrap |
| `run_exp_surg_003_mock_vessl.sh` | CPU mock pilot |
| `run_exp_surg_003_vessl.sh` | Entry · `EXP_SURG_003_MODE` |
| `run_exp_surg_003_drift.sh` | Isaac drift (shared RunPod/VESSL) |
| `copy_exp_surg_003_from_vessl.sh` | scp results home |

---

## Links

- [Confirmatory spec](paper002_confirmatory_spec_v0.1.md)
- [EXP-SURG-003 README](../../experiments/surgical_intelligence/exp_surg_003_wm_expansion/README.md)
- [Study 2 VESSL setup](../stage2/vessl_isaac_setup_v0.1.md)
