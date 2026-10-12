# -*- coding: utf-8 -*-
"""参考答案 · 三角函数积木（对应 M2 / M6）。"""
from __future__ import annotations

import numpy as np


def polar_to_xy(L, theta):
    """M2：极坐标 → 直角坐标。"""
    return L * np.cos(theta), L * np.sin(theta)


def xy_to_polar(x, y):
    """M2：直角坐标 → 极坐标（角度用 atan2）。"""
    return float(np.hypot(x, y)), float(np.arctan2(y, x))


def sph2cart(r, theta, phi):
    """M6：球坐标 → 直角坐标。"""
    return (r * np.sin(phi) * np.cos(theta),
            r * np.sin(phi) * np.sin(theta),
            r * np.cos(phi))


def cart2sph(x, y, z):
    """M6：直角坐标 → 球坐标。"""
    r = float(np.sqrt(x * x + y * y + z * z))
    theta = float(np.arctan2(y, x))
    phi = float(np.arctan2(np.hypot(x, y), z))
    return r, theta, phi
