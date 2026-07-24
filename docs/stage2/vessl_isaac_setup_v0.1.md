# Study 2 — VESSL Isaac workspace setup v0.1

> **When to use:** RunPod SSH proxy (`ssh.runpod.io:22`) fails from your network · Web Terminal unstable  
> **Same experiment:** [selection_ablation_run_protocol_v0.1.md](selection_ablation_run_protocol_v0.1.md)

---

## Why VESSL

| Issue (RunPod) | VESSL |
| --- | --- |
| `ssh.runpod.io:22` timeout (hospital / some ISPs) | Browser **Jupyter :8888** + `vesslctl workspace ssh` |
| Web Terminal toggle OFF on Isaac image | Jupyter terminal stays up on workspace |
| Proxy scp broken | Direct SSH + scp when TCP works |

Isaac bootstrap + ablation **scripts are unchanged** — mount persistent storage at `/workspace`.

---

## One-time: custom Isaac image

VESSL requires **openssh-server** + **JupyterLab** in the container. Raw `nvcr.io/nvidia/isaac-sim:4.1.0` is not enough.

```bash
cd docker/vessl-isaac-sim-4.1.0
docker login nvcr.io
docker build -t ghcr.io/YOUR_GH_USER/vessl-isaac-sim:4.1.0 .
docker push ghcr.io/YOUR_GH_USER/vessl-isaac-sim:4.1.0
```

See [docker/vessl-isaac-sim-4.1.0/README.md](../../docker/vessl-isaac-sim-4.1.0/README.md).

---

## Create workspace (console)

1. [VESSL Cloud](https://cloud.vessl.ai) → **New Workspace**
2. **GPU:** RTX 4090 24GB (or closest)
3. **Region:** Korea (or nearest)
4. **Cluster storage:** create or reuse · mount at **`/workspace`**
5. **Custom image:** `ghcr.io/YOUR_GH_USER/vessl-isaac-sim:4.1.0`
6. **SSH key:** register your `id_ed25519.pub` (or generate in UI)
7. **Env:** `ACCEPT_EULA=Y`, `PRIVACY_CONSENT=Y`, `OMNI_KIT_ALLOW_ROOT=1`
8. **Init script (optional):** paste contents of `scripts/vessl_workspace_init.sh`

**Billing:** pause workspace when idle (like RunPod Stop).

---

## Connect

### A · Jupyter (recommended at hospital)

Workspace → **Connect** → open **Jupyter (8888)** → Terminal:

```bash
bash /workspace/research-os/scripts/vessl_workspace_init.sh   # first time only
cd /workspace/research-os && git pull origin master
tmux new -s study2
```

### B · SSH (local)

```bash
vesslctl auth login
vesslctl workspace ssh <workspace-slug>
```

Or copy the SSH command from the Connect tab (Windows: `-i $env:USERPROFILE\.ssh\id_ed25519`).

---

## Selection ablation (same gates as RunPod)

```bash
cd /workspace/research-os && git pull origin master
tmux new -s study2

# Bootstrap (~15–25 min, cold volume)
STUDY2_PREP_BOOTSTRAP=1 bash scripts/prep_study2_selection_ablation_vessl.sh

# zero_agent smoke — MUST PASS
cd /workspace/orbit-surgical
export OMNI_KIT_ALLOW_ROOT=1
export IsaacLab_PATH=/workspace/IsaacLab
/workspace/IsaacLab/isaaclab.sh -p source/standalone/environments/zero_agent.py \
  --task Isaac-Reach-Dual-STAR-IK-Rel-Play-v0 --num_envs 1 --headless

# Full ablation
cd /workspace/research-os
export STUDY2_SKIP_BOOTSTRAP=1
bash scripts/run_study2_selection_ablation_vessl.sh
```

**Never** `pkill -9 -f '/isaac-sim/kit/kit'`.

---

## Pull results to local PC

From Connect tab SSH (or `vesslctl workspace ssh`):

```powershell
# Replace RUN_ID and paths from workspace output
scp -i $env:USERPROFILE\.ssh\id_ed25519 `
  root@<VESSL_SSH_HOST>:/workspace/research-os/results/study2_dream_curriculum/isaac/<RUN_ID>/isaac_aggregate.json `
  C:\projects\research-os\experiments\surgical_intelligence\exp_surg_002_dream_curriculum\results\selection_ablation_v0.1\
```

Or download via Jupyter file browser.

---

## If zero_agent FAIL (futex)

Log **infra blocker** in pre-reg §11 · promote CPU legs only · **no retry spiral** on same host.

---

## RunPod volume migration

If `/workspace/IsaacLab` and `/workspace/orbit-surgical` exist on an old RunPod volume only:

1. Tar on RunPod (when accessible): `tar -czf orbit-bootstrap.tgz -C /workspace IsaacLab orbit-surgical`
2. scp to local · upload to VESSL `/workspace` · extract  
3. Or accept **fresh bootstrap** (~15–25 min) on VESSL
