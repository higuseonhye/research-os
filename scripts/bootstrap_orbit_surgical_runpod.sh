#!/usr/bin/env bash
set -euo pipefail

ISAAC_SIM_PATH="${ISAAC_SIM_PATH:-/isaac-sim}"
WORKSPACE_DIR="${WORKSPACE_DIR:-/workspace}"
ISAACLAB_PATH="${ISAACLAB_PATH:-$WORKSPACE_DIR/IsaacLab}"
ORBIT_SURGICAL_PATH="${ORBIT_SURGICAL_PATH:-$WORKSPACE_DIR/orbit-surgical}"
DISABLED_TASK_DIR="${DISABLED_TASK_DIR:-$WORKSPACE_DIR/orbit-disabled}"

ISAACLAB_REPO="${ISAACLAB_REPO:-https://github.com/isaac-sim/IsaacLab.git}"
ISAACLAB_REF="${ISAACLAB_REF:-v1.0.0}"
ORBIT_REPO="${ORBIT_REPO:-https://github.com/orbit-surgical/orbit-surgical.git}"

export OMNI_KIT_ALLOW_ROOT="${OMNI_KIT_ALLOW_ROOT:-1}"
export IsaacLab_PATH="$ISAACLAB_PATH"

log() {
  echo
  echo "== $* =="
}

require_path() {
  local path="$1"
  if [ ! -e "$path" ]; then
    echo "Missing required path: $path" >&2
    exit 1
  fi
}

log "Checking Isaac Sim container"
require_path "$ISAAC_SIM_PATH/python.sh"
"$ISAAC_SIM_PATH/python.sh" --version
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi
fi

log "Installing system tools"
if ! command -v git >/dev/null 2>&1; then
  apt-get update
  apt-get install -y git
fi

log "Preparing repositories"
mkdir -p "$WORKSPACE_DIR"
if [ ! -d "$ISAACLAB_PATH/.git" ]; then
  rm -rf "$ISAACLAB_PATH"
  git clone --branch "$ISAACLAB_REF" "$ISAACLAB_REPO" "$ISAACLAB_PATH"
fi
if [ ! -e "$ISAACLAB_PATH/_isaac_sim" ]; then
  ln -s "$ISAAC_SIM_PATH" "$ISAACLAB_PATH/_isaac_sim"
fi
if [ ! -d "$ORBIT_SURGICAL_PATH/.git" ]; then
  rm -rf "$ORBIT_SURGICAL_PATH"
  git clone "$ORBIT_REPO" "$ORBIT_SURGICAL_PATH"
fi

IL_PY="$ISAACLAB_PATH/_isaac_sim/python.sh"
IL_KIT_PY="$ISAACLAB_PATH/_isaac_sim/kit/python/bin/python3"

log "Restoring Isaac Sim Python packaging"
"$IL_KIT_PY" -m ensurepip --upgrade || true
"$IL_KIT_PY" -m pip install --upgrade pip setuptools wheel toml

log "Installing Isaac Lab compatible dependencies"
"$IL_PY" -m pip install --force-reinstall --index-url https://download.pytorch.org/whl/cu118 torch==2.2.2 torchvision==0.17.2
"$IL_PY" -m pip install --force-reinstall \
  "numpy==1.26.4" \
  "protobuf>=3.20.2,<5.0.0" \
  gymnasium==0.29.0 \
  farama-notifications \
  jax-jumpy \
  prettytable==3.3.0 \
  "pyglet<2" \
  hidapi \
  trimesh \
  h5py \
  moviepy \
  tensorboard \
  warp-lang \
  GitPython
"$IL_PY" -m pip install --no-deps "tensordict==0.4.0"
# Isaac Lab 1.0.0 agent_cfg uses policy/algorithm keys (no obs_groups).
# rsl-rl-lib >= 3.0 requires obs_groups; >= 4.0 requires actor/critic keys.
RSL_RL_LIB_VERSION="${RSL_RL_LIB_VERSION:-2.3.1}"
"$IL_PY" -m pip install --no-deps --force-reinstall "rsl-rl-lib==${RSL_RL_LIB_VERSION}"

log "Registering Isaac Lab extensions"
"$IL_PY" -m pip install -e "$ISAACLAB_PATH/source/extensions/omni.isaac.lab" --no-deps
"$IL_PY" -m pip install -e "$ISAACLAB_PATH/source/extensions/omni.isaac.lab_tasks" --no-deps
"$IL_PY" -m pip install -e "$ISAACLAB_PATH/source/extensions/omni.isaac.lab_assets" --no-deps

log "Registering ORBIT-Surgical extensions"
"$IL_PY" -m pip install toml psutil
"$IL_PY" -m pip install -e "$ORBIT_SURGICAL_PATH/source/extensions/orbit.surgical.ext" --no-build-isolation --no-deps
"$IL_PY" -m pip install -e "$ORBIT_SURGICAL_PATH/source/extensions/orbit.surgical.assets" --no-build-isolation --no-deps
"$IL_PY" -m pip install -e "$ORBIT_SURGICAL_PATH/source/extensions/orbit.surgical.tasks" --no-build-isolation --no-deps

log "Disabling incompatible non-Reach task folders"
mkdir -p "$DISABLED_TASK_DIR"
SURGICAL_TASK_DIR="$ORBIT_SURGICAL_PATH/source/extensions/orbit.surgical.tasks/orbit/surgical/tasks/surgical"
for task_name in handover lift; do
  if [ -d "$SURGICAL_TASK_DIR/$task_name" ]; then
    rm -rf "$DISABLED_TASK_DIR/$task_name"
    mv "$SURGICAL_TASK_DIR/$task_name" "$DISABLED_TASK_DIR/$task_name"
    echo "Moved $task_name to $DISABLED_TASK_DIR/$task_name"
  fi
done
find "$ORBIT_SURGICAL_PATH/source/extensions/orbit.surgical.tasks/orbit/surgical/tasks" -maxdepth 4 -type d \
  \( -iname "*handover*" -o -iname "*hadnover*" -o -iname "*lift*" \) || true

log "Patching ORBIT zero_agent compatibility"
"$IL_PY" - <<'PY'
from pathlib import Path

path = Path("/workspace/orbit-surgical/source/standalone/environments/zero_agent.py")
text = path.read_text()

text = text.replace(
    "    if not hasattr(args_cli, \"device\"):\n"
    "        args_cli.device = f\"cuda:{args_cli.device_id}\"\n\n",
    "",
)
text = text.replace(
    "    if not hasattr(args_cli, \"device\"):\n"
    "        args_cli.device = \"cuda:0\"\n\n",
    "",
)

if "def main():\n" in text and "args_cli.device = \"cuda:0\"" not in text:
    text = text.replace(
        "def main():\n",
        "def main():\n"
        "    if not hasattr(args_cli, \"device\"):\n"
        "        args_cli.device = \"cuda:0\"\n\n",
        1,
    )

text = text.replace(
    "    env_cfg = parse_env_cfg(\n"
    "        args_cli.task, device=args_cli.device, num_envs=args_cli.num_envs, use_fabric=not args_cli.disable_fabric\n"
    "    )\n",
    "    env_cfg = parse_env_cfg(\n"
    "        args_cli.task, num_envs=args_cli.num_envs, use_fabric=not args_cli.disable_fabric\n"
    "    )\n",
)

path.write_text(text)
print("patched zero_agent.py")
PY

log "Patching ORBIT rsl_rl train/play parse_env_cfg compatibility"
"$IL_PY" - <<'PY'
from pathlib import Path

RSL_DIR = Path("/workspace/orbit-surgical/source/standalone/workflows/rsl_rl")
OLD = (
    "    env_cfg: ManagerBasedRLEnvCfg = parse_env_cfg(\n"
    "        args_cli.task, device=args_cli.device, num_envs=args_cli.num_envs, use_fabric=not args_cli.disable_fabric\n"
    "    )\n"
)
NEW = (
    "    if not hasattr(args_cli, \"device\"):\n"
    "        args_cli.device = \"cuda:0\"\n\n"
    "    env_cfg: ManagerBasedRLEnvCfg = parse_env_cfg(\n"
    "        args_cli.task, num_envs=args_cli.num_envs, use_fabric=not args_cli.disable_fabric\n"
    "    )\n"
)
OLD_PLAY = (
    "    env_cfg = parse_env_cfg(\n"
    "        args_cli.task, device=args_cli.device, num_envs=args_cli.num_envs, use_fabric=not args_cli.disable_fabric\n"
    "    )\n"
)
NEW_PLAY = (
    "    if not hasattr(args_cli, \"device\"):\n"
    "        args_cli.device = \"cuda:0\"\n\n"
    "    env_cfg = parse_env_cfg(\n"
    "        args_cli.task, num_envs=args_cli.num_envs, use_fabric=not args_cli.disable_fabric\n"
    "    )\n"
)

for name, old, new in (
    ("train.py", OLD, NEW),
    ("play.py", OLD_PLAY, NEW_PLAY),
):
    path = RSL_DIR / name
    text = path.read_text()
    if old in text:
        path.write_text(text.replace(old, new, 1))
        print(f"patched {name}")
    elif new.splitlines()[2] in text:
        print(f"already patched {name}")
    else:
        print(f"warning: unexpected {name} layout; manual patch may be needed")
PY

log "Smoke-test command"
cat <<EOF
cd "$ORBIT_SURGICAL_PATH"
export OMNI_KIT_ALLOW_ROOT=1
export IsaacLab_PATH="$ISAACLAB_PATH"
"$ISAACLAB_PATH/isaaclab.sh" -p source/standalone/environments/zero_agent.py --task Isaac-Reach-Dual-STAR-IK-Rel-Play-v0 --num_envs 1 --headless
EOF

log "Bootstrap complete"
