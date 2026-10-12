# -*- coding: utf-8 -*-
"""参考答案 · 平面两连杆臂（对应 M3 / M4）。"""
from __future__ import annotations

import numpy as np


def fk_2r(L1, L2, q1, q2):
    """M3：平面 2R 正运动学。"""
    x = L1 * np.cos(q1) + L2 * np.cos(q1 + q2)
    y = L1 * np.sin(q1) + L2 * np.sin(q1 + q2)
    return float(x), float(y)


def ik_2r(L1, L2, x, y):
    """M4：平面 2R 逆运动学（余弦定理 + atan2），返回肘上/肘下两组解。"""
    r2 = x * x + y * y
    r = np.sqrt(r2)
    if r > L1 + L2 + 1e-12 or r < abs(L1 - L2) - 1e-12:
        return []                                    # 不可达
    c2 = (r2 - L1 * L1 - L2 * L2) / (2.0 * L1 * L2)
    c2 = float(np.clip(c2, -1.0, 1.0))               # 防止浮点误差越界
    sols = []
    for sign in (+1.0, -1.0):
        q2 = sign * np.arccos(c2)
        q1 = np.arctan2(y, x) - np.arctan2(L2 * np.sin(q2), L1 + L2 * np.cos(q2))
        sols.append((float(q1), float(q2)))
    return sols
