# VESSL workspace image for ORBIT-Surgical / Isaac Sim 4.1.0
# Extends NGC Isaac Sim with openssh-server + JupyterLab (VESSL requirements).
#
# Build (requires NGC login: docker login nvcr.io):
#   docker build -t ghcr.io/YOUR_USER/vessl-isaac-sim:4.1.0 .
#   docker push ghcr.io/YOUR_USER/vessl-isaac-sim:4.1.0

FROM nvcr.io/nvidia/isaac-sim:4.1.0

ENV ACCEPT_EULA=Y \
    PRIVACY_CONSENT=Y \
    OMNI_KIT_ALLOW_ROOT=1 \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server \
    git \
    tmux \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /var/run/sshd \
    && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

# VESSL expects jupyter at /usr/local/bin/jupyter
RUN /isaac-sim/python.sh -m pip install --no-cache-dir jupyterlab \
    && JUP="$(/isaac-sim/python.sh -c "import shutil; print(shutil.which('jupyter-lab') or shutil.which('jupyter'))")" \
    && ln -sf "$JUP" /usr/local/bin/jupyter \
    && ln -sf "$JUP" /usr/local/bin/jupyter-lab

WORKDIR /workspace
CMD ["/bin/bash", "-lc", "sleep infinity"]
