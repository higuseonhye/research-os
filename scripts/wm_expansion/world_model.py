"""Compact GRU latent world model with L1 (F0) and L3 (F0+F1+G) expansion."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

import numpy as np

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
except ImportError as exc:  # pragma: no cover
    raise ImportError("Paper 002 WM expansion requires PyTorch: pip install torch") from exc


OBS_DIM = 6
ACT_DIM = 2
LATENT_DIM = 8
HIDDEN_DIM = 32


class GRUDynamicsCore(nn.Module):
    """Single-step latent dynamics: z_t, a_t -> predicted next observation."""

    def __init__(self, obs_dim: int = OBS_DIM, act_dim: int = ACT_DIM, hidden: int = HIDDEN_DIM) -> None:
        super().__init__()
        self.obs_dim = obs_dim
        self.encoder = nn.Linear(obs_dim, hidden)
        self.gru = nn.GRUCell(hidden + act_dim, hidden)
        self.decoder = nn.Linear(hidden, obs_dim)

    def forward_step(
        self,
        obs: torch.Tensor,
        action: torch.Tensor,
        h: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        enc = torch.tanh(self.encoder(obs))
        h_next = self.gru(torch.cat([enc, action], dim=-1), h)
        pred = self.decoder(h_next)
        return pred, h_next


class DriftExpert(nn.Module):
    """F1: adds learnable drift bias in observation space after GRU prediction."""

    def __init__(self, core: GRUDynamicsCore) -> None:
        super().__init__()
        self.core = core
        self.drift_bias = nn.Parameter(torch.zeros(core.obs_dim))

    def forward_step(
        self,
        obs: torch.Tensor,
        action: torch.Tensor,
        h: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        pred, h_next = self.core.forward_step(obs, action, h)
        pred = pred + self.drift_bias
        return pred, h_next


class ModeGate(nn.Module):
    """G: map recent residual stats -> expert mixture weights."""

    def __init__(self, obs_dim: int = OBS_DIM, hidden: int = 16) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim + 1, hidden),
            nn.ReLU(),
            nn.Linear(hidden, 2),
        )

    def forward(self, obs: torch.Tensor, residual_norm: torch.Tensor) -> torch.Tensor:
        x = torch.cat([obs, residual_norm.unsqueeze(-1)], dim=-1)
        return F.softmax(self.net(x), dim=-1)


@dataclass
class WMState:
    h: torch.Tensor


class StaticWorldModel:
    """W0 = F0 only."""

    def __init__(self, device: str = "cpu") -> None:
        self.device = torch.device(device)
        self.f0 = GRUDynamicsCore().to(self.device)
        self.opt = torch.optim.Adam(self.f0.parameters(), lr=1e-3)

    def init_state(self, batch: int = 1) -> WMState:
        h = torch.zeros(batch, HIDDEN_DIM, device=self.device)
        return WMState(h=h)

    def predict_step(
        self,
        obs: np.ndarray,
        action: np.ndarray,
        state: WMState,
    ) -> tuple[np.ndarray, WMState, float]:
        obs_t = torch.as_tensor(obs, dtype=torch.float32, device=self.device).unsqueeze(0)
        act_t = torch.as_tensor(action, dtype=torch.float32, device=self.device).unsqueeze(0)
        with torch.no_grad():
            pred, h_next = self.f0.forward_step(obs_t, act_t, state.h)
        residual = float(torch.norm(pred - obs_t).item())
        return pred.squeeze(0).cpu().numpy(), WMState(h=h_next), residual

    def train_on_trajectory(
        self,
        obs_seq: np.ndarray,
        act_seq: np.ndarray,
        steps: int = 200,
        lr: float | None = None,
    ) -> float:
        if lr is not None:
            for pg in self.opt.param_groups:
                pg["lr"] = lr
        obs_t = torch.as_tensor(obs_seq, dtype=torch.float32, device=self.device)
        act_t = torch.as_tensor(act_seq, dtype=torch.float32, device=self.device)
        n = len(obs_seq) - 1
        if n < 2:
            return 0.0
        losses: list[float] = []
        for _ in range(steps):
            self.opt.zero_grad()
            h = torch.zeros(1, HIDDEN_DIM, device=self.device)
            loss = torch.tensor(0.0, device=self.device)
            for i in range(n):
                pred, h = self.f0.forward_step(obs_t[i : i + 1], act_t[i : i + 1], h)
                loss = loss + F.mse_loss(pred, obs_t[i + 1 : i + 2])
            loss = loss / n
            loss.backward()
            self.opt.step()
            losses.append(float(loss.item()))
        return float(np.mean(losses[-10:])) if losses else 0.0

    def clone_f0(self) -> GRUDynamicsCore:
        return deepcopy(self.f0)


class ModularWorldModel:
    """W1 = F0 + F1 + G (L3)."""

    def __init__(self, f0: GRUDynamicsCore, device: str = "cpu") -> None:
        self.device = torch.device(device)
        self.f0 = f0.to(self.device)
        self.f1 = DriftExpert(deepcopy(f0)).to(self.device)
        self.gate = ModeGate().to(self.device)
        self.opt = torch.optim.Adam(
            list(self.f1.parameters()) + list(self.gate.parameters()),
            lr=1e-3,
        )
        # F0 frozen by default for L3 arm
        for p in self.f0.parameters():
            p.requires_grad = False

    def init_state(self, batch: int = 1) -> WMState:
        h = torch.zeros(batch, HIDDEN_DIM, device=self.device)
        return WMState(h=h)

    def predict_step(
        self,
        obs: np.ndarray,
        action: np.ndarray,
        state: WMState,
        force_expert: int | None = None,
    ) -> tuple[np.ndarray, WMState, float, np.ndarray]:
        obs_t = torch.as_tensor(obs, dtype=torch.float32, device=self.device).unsqueeze(0)
        act_t = torch.as_tensor(action, dtype=torch.float32, device=self.device).unsqueeze(0)
        with torch.no_grad():
            pred0, h0 = self.f0.forward_step(obs_t, act_t, state.h)
            pred1, h1 = self.f1.forward_step(obs_t, act_t, state.h)
            res_norm = torch.norm(pred0 - obs_t, dim=-1)
            if force_expert == 0:
                w = torch.tensor([[1.0, 0.0]], device=self.device)
            elif force_expert == 1:
                w = torch.tensor([[0.0, 1.0]], device=self.device)
            else:
                w = self.gate(obs_t, res_norm)
            pred = w[:, 0:1] * pred0 + w[:, 1:2] * pred1
            h_next = w[:, 0:1] * h0 + w[:, 1:2] * h1
        residual = float(torch.norm(pred - obs_t).item())
        return (
            pred.squeeze(0).cpu().numpy(),
            WMState(h=h_next),
            residual,
            w.squeeze(0).cpu().numpy(),
        )

    def train_expansion(
        self,
        obs_seq: np.ndarray,
        act_seq: np.ndarray,
        steps: int = 300,
    ) -> float:
        obs_t = torch.as_tensor(obs_seq, dtype=torch.float32, device=self.device)
        act_t = torch.as_tensor(act_seq, dtype=torch.float32, device=self.device)
        n = len(obs_seq) - 1
        if n < 2:
            return 0.0
        losses: list[float] = []
        for _ in range(steps):
            self.opt.zero_grad()
            h = torch.zeros(1, HIDDEN_DIM, device=self.device)
            loss = torch.tensor(0.0, device=self.device)
            for i in range(n):
                obs_i = obs_t[i : i + 1]
                act_i = act_t[i : i + 1]
                pred0, _ = self.f0.forward_step(obs_i, act_i, h)
                pred1, h = self.f1.forward_step(obs_i, act_i, h)
                res_norm = torch.norm(pred0 - obs_i, dim=-1)
                w = self.gate(obs_i, res_norm)
                pred = w[:, 0:1] * pred0 + w[:, 1:2] * pred1
                loss = loss + F.mse_loss(pred, obs_t[i + 1 : i + 2])
            loss = loss / n
            loss.backward()
            self.opt.step()
            losses.append(float(loss.item()))
        return float(np.mean(losses[-10:])) if losses else 0.0


def multi_step_prediction_error(
    wm: StaticWorldModel | ModularWorldModel,
    obs_seq: np.ndarray,
    act_seq: np.ndarray,
    horizon: int = 10,
    force_expert: int | None = None,
) -> float:
    """PE_H on target position channels (last 2 dims of obs)."""
    if len(obs_seq) < horizon + 1:
        return float("nan")
    state = wm.init_state()
    errors: list[float] = []
    # warm-start with first observation
    for start in range(0, len(obs_seq) - horizon - 1, max(1, horizon // 2)):
        state = wm.init_state()
        obs = obs_seq[start]
        total = 0.0
        for h in range(horizon):
            idx = start + h
            if idx >= len(act_seq):
                break
            if isinstance(wm, ModularWorldModel):
                pred, state, _, _ = wm.predict_step(obs, act_seq[idx], state, force_expert=force_expert)
            else:
                pred, state, _ = wm.predict_step(obs, act_seq[idx], state)
            true_next = obs_seq[idx + 1]
            # target channels = obs[4:6]
            err = float(np.linalg.norm(pred[4:6] - true_next[4:6]))
            total += err
            obs = true_next
        errors.append(total / horizon)
    return float(np.mean(errors)) if errors else float("nan")
