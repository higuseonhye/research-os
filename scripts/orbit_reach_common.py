"""Shared ORBIT reach helpers for Isaac runners (001A, 003 drift, etc.)."""

from __future__ import annotations

from typing import Any

import numpy as np
import torch
from omni.isaac.lab.utils.math import combine_frame_transforms


def tensor_to_np(value: object) -> np.ndarray:
    if torch.is_tensor(value):
        return value.detach().cpu().numpy()
    return np.asarray(value)


def find_robot_name(scene: Any) -> str:
    for cand in ("robot_1", "robot", "star", "dual_star"):
        try:
            _ = scene[cand]
            return cand
        except Exception:
            continue
    try:
        return str(next(iter(scene.keys())))
    except Exception:
        return "robot"


def resolve_ee_body_index(asset: Any, preferred: int = -1) -> int:
    n = int(asset.data.body_state_w.shape[1])
    if preferred >= 0 and preferred < n:
        return preferred
    names: list[str] = []
    for attr in ("body_names", "body_names_list"):
        val = getattr(asset.data, attr, None) or getattr(asset, attr, None)
        if val is not None:
            names = [str(x) for x in val]
            break
    for target in ("endo360_needle", "endo360_calibrated", "star_link_ee"):
        if target in names:
            return names.index(target)
    return 13 if n > 13 else n - 1


def ee_distance(
    env: Any, robot_name: str, command_name: str, body_index: int
) -> tuple[float, np.ndarray, np.ndarray]:
    base = env.unwrapped
    asset = base.scene[robot_name]
    command = base.command_manager.get_command(command_name)
    desired_pos_body = command[:, :3]
    desired_pos_world, _ = combine_frame_transforms(
        asset.data.root_state_w[:, :3],
        asset.data.root_state_w[:, 3:7],
        desired_pos_body,
    )
    current_pos_world = asset.data.body_state_w[:, body_index, :3]
    dist = torch.norm(current_pos_world - desired_pos_world, dim=1)
    return float(dist.mean().item()), tensor_to_np(current_pos_world[0]), tensor_to_np(desired_pos_world[0])


def get_command_xyz(env: Any, command_name: str) -> torch.Tensor:
    cmd = env.unwrapped.command_manager.get_command(command_name)
    return cmd[:, :3].clone()


def set_command_xyz(env: Any, command_name: str, xyz: torch.Tensor) -> None:
    cmd = env.unwrapped.command_manager.get_command(command_name)
    cmd[:, :3] = xyz


def scripted_action(
    env: Any,
    robot_name: str,
    command_name: str,
    gain: float,
    body_index: int,
    max_delta: float = 0.05,
) -> torch.Tensor:
    from omni.isaac.lab.utils.math import axis_angle_from_quat, quat_apply, quat_inv, quat_mul

    base = env.unwrapped
    device = base.device
    asset = base.scene[robot_name]
    command = base.command_manager.get_command(command_name)
    desired_pos_body = command[:, :3]
    desired_quat_body = command[:, 3:7]
    root_pos = asset.data.root_state_w[:, :3]
    root_quat = asset.data.root_state_w[:, 3:7]
    desired_pos_world, desired_quat_world = combine_frame_transforms(
        root_pos, root_quat, desired_pos_body, desired_quat_body
    )
    current_pos_world = asset.data.body_state_w[:, body_index, :3]
    current_quat_world = asset.data.body_state_w[:, body_index, 3:7]

    err_world = desired_pos_world - current_pos_world
    err_body = quat_apply(quat_inv(root_quat), err_world)
    delta_pos = torch.clamp(gain * err_body, -max_delta, max_delta)

    q_err = quat_mul(desired_quat_world, quat_inv(current_quat_world))
    delta_rot = torch.clamp(gain * axis_angle_from_quat(q_err), -max_delta, max_delta)

    action = torch.zeros(env.action_space.shape, device=device)
    action[..., 0:3] = delta_pos
    action[..., 3:6] = delta_rot
    return action


def in_forbidden(ee_world: np.ndarray, center: np.ndarray, half: np.ndarray) -> bool:
    return bool(np.all(np.abs(ee_world - center) <= half))


def classify(success: bool, violation: bool, timed_out: bool) -> str:
    if violation:
        return "unsafe_failure"
    if success:
        return "successful_resolution"
    if timed_out:
        return "timeout_failure"
    return "safe_unresolved"
