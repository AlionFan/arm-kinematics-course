# -*- coding: utf-8 -*-
"""参考答案 · 球形手腕欧拉角（对应 M10）。"""
from __future__ import annotations

import numpy as np

from . import rotations as _R


def matrix_from_euler_zyx(alpha, beta, gamma):
    """R = Rz(α) · Ry(β) · Rx(γ)。"""
    return _R.rot_z(alpha) @ _R.rot_y(beta) @ _R.rot_x(gamma)


def euler_zyx_from_matrix(R):
    """从 R = Rz(α)Ry(β)Rx(γ) 反解 (α, β, γ)。"""
    R = np.asarray(R, dtype=float)
    beta = np.arctan2(-R[2, 0], np.hypot(R[0, 0], R[1, 0]))
    alpha = np.arctan2(R[1, 0], R[0, 0])
    gamma = np.arctan2(R[2, 1], R[2, 2])
    return float(alpha), float(beta), float(gamma)
