# VESSL · Isaac Sim 4.1.0 workspace image

RunPod proxy SSH (`ssh.runpod.io:22`) is unreliable from some networks. VESSL workspaces expose **Jupyter (8888) in the browser** and **`vesslctl workspace ssh`**, which often works when RunPod does not.

## Requirements

- Docker with `nvidia` runtime (for local smoke test only)
- NGC account + `docker login nvcr.io` (to pull base image)
- VESSL Cloud account + credits
- Push target: GHCR, Docker Hub, or VESSL-integrated private registry

## Build and push

### Option A · GitHub Actions (recommended if local `docker push` fails)

Hospital / proxy networks often drop the ~8GB layer upload. Push from GitHub instead:

1. GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**
   - Name: `NGC_API_KEY` · Value: your NGC API key
2. Push this repo (includes `.github/workflows/publish-vessl-isaac-image.yml`)
3. **Actions** → **Publish VESSL Isaac Sim image** → **Run workflow**
4. Wait ~30–60 min · image: `ghcr.io/YOUR_GH_USER/vessl-isaac-sim:4.1.0-v2`
5. https://github.com/YOUR_GH_USER?tab=packages → package → **Public**

### Option B · Local Docker

```bash
cd docker/vessl-isaac-sim-4.1.0
docker login nvcr.io
docker build -t ghcr.io/YOUR_GH_USER/vessl-isaac-sim:4.1.0 .
docker login ghcr.io
docker push ghcr.io/YOUR_GH_USER/vessl-isaac-sim:4.1.0
```

If push fails with `broken pipe` / `3128` proxy: disable Docker Desktop proxy or use Option A.

## VESSL workspace settings

| Field | Value |
| --- | --- |
| GPU | RTX 4090 24GB (or closest available) |
| Region | Korea / nearest |
| Custom image | `ghcr.io/YOUR_GH_USER/vessl-isaac-sim:4.1.0` |
| Cluster storage mount | **`/workspace`** (keeps IsaacLab + orbit-surgical) |
| Env | `ACCEPT_EULA=Y`, `PRIVACY_CONSENT=Y`, `OMNI_KIT_ALLOW_ROOT=1` |
| Init script | `scripts/vessl_workspace_init.sh` from repo (optional) |

Full runbook: [docs/stage2/vessl_isaac_setup_v0.1.md](../../docs/stage2/vessl_isaac_setup_v0.1.md)
