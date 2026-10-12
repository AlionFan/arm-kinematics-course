# -*- coding: utf-8 -*-
"""参考答案 · 旋转矩阵积木（对应 M7）。"""
from __future__ import annotations

import numpy as np


def rot_x(alpha):
    c, s = np.cos(alpha), np.sin(alpha)
    return np.array([[1, 0, 0],
                     [0, c, -s],
                     [0, s, c]], dtype=float)


def rot_y(beta):
    c, s = np.cos(beta), np.sin(beta)
    return np.array([[c, 0, s],
                     [0, 1, 0],
                     [-s, 0, c]], dtype=float)


def rot_z(gamma):
    c, s = np.cos(gamma), np.sin(gamma)
    return np.array([[c, -s, 0],
                     [s, c, 0],
                     [0, 0, 1]], dtype=float)
