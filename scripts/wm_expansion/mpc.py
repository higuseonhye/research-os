"""Simple MPC using world-model rollouts."""

from __future__ import annotations

import numpy as np

from .world_model import ModularWorldModel, StaticWorldModel


def mpc_action(
    wm: StaticWorldModel | ModularWorldModel,
    obs: np.ndarray,
    state,
    n_candidates: int = 17,
    horizon: int = 10,
    force_expert: int | None = None,
) -> tuple[np.ndarray, object]:
    """Pick action minimizing predicted EE distance to **observed** target over horizon."""
    candidates = _action_candidates(obs, n_candidates)
    best_cost = float("inf")
    best_a = candidates[0]
    best_state = state

    for a in candidates:
        cost, _ = _rollout_cost(wm, obs.copy(), state, a, horizon, force_expert)
        if cost < best_cost:
            best_cost = cost
            best_a = a

    return best_a, best_state


def _action_candidates(obs: np.ndarray, n: int) -> list[np.ndarray]:
    """Greedy-to-observed-target first, then evenly spaced directions."""
    out: list[np.ndarray] = [_greedy_toward_target(obs)]
    if n <= 1:
        return out
    angles = np.linspace(0, 2 * np.pi, n - 1, endpoint=False)
    for t in angles:
        out.append(np.array([np.cos(t), np.sin(t)], dtype=np.float64))
    return out


def _rollout_cost(
    wm: StaticWorldModel | ModularWorldModel,
    obs: np.ndarray,
    state,
    first_action: np.ndarray,
    horizon: int,
    force_expert: int | None,
) -> tuple[float, object]:
    total = 0.0
    cur_obs = obs
    cur_state = state
    for h in range(horizon):
        action = first_action if h == 0 else _greedy_toward_target(cur_obs)
        if isinstance(wm, ModularWorldModel):
            pred, cur_state, _, _ = wm.predict_step(cur_obs, action, cur_state, force_expert=force_expert)
        else:
            pred, cur_state, _ = wm.predict_step(cur_obs, action, cur_state)
        # Plan toward observed target (claim path), not WM-predicted target position.
        target = cur_obs[4:6]
        ee = pred[0:2]
        total += float(np.linalg.norm(ee - target))
        cur_obs = pred
    return total, cur_state


def _greedy_toward_target(obs: np.ndarray) -> np.ndarray:
    err = obs[4:6] - obs[0:2]
    norm = np.linalg.norm(err) + 1e-8
    return np.clip(err / norm, -1.0, 1.0)
