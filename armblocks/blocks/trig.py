# -*- coding: utf-8 -*-
"""
积木 · 三角函数：把「角度」翻译成「位置」
========================================
对应课程 **M2（单位圆与角度坐标）** 与 **M6（三维坐标与球坐标）**。

.. important::
   核心思想 —— ``sin`` 和 ``cos`` 的本质是**坐标**：
   单位圆上角度 θ 对应的点就是 ``(cos θ, sin θ)``。
"""
from __future__ import annotations

import numpy as np


# ==================================================================
# M2 · 平面：极坐标 ⇄ 直角坐标
# ==================================================================
def polar_to_xy(L, theta):
    """一根长 ``L``、与 x 轴成 ``theta`` 角（弧度）的连杆，末端在哪？

    参数
    ----
    L     : 连杆长度
    theta : 与 x 轴正方向的夹角（弧度）

    返回
    ----
    (x, y) : 末端坐标

    提示
    ----
    想象单位圆：转过 θ 角后落在 ``(cos θ, sin θ)``，再把半径从 1 放大到 L。
    """
    # TODO(M2): x = L * cos(theta) ;  y = L * sin(theta)
    raise NotImplementedError("TODO(M2): 补全 polar_to_xy —— 用 cos / sin 把角度变成坐标")


def xy_to_polar(x, y):
    """反过来：已知坐标，求「长度 + 角度」。

    返回
    ----
    (L, theta) : L ≥ 0；theta ∈ (−π, π]

    提示
    ----
    * 长度：勾股定理。
    * 角度：用 ``atan2`` 而不是 ``arctan`` —— 因为 atan2 能自动分辨四个象限。
    """
    # TODO(M2): L = hypot(x, y) ;  theta = atan2(y, x)
    raise NotImplementedError("TODO(M2): 补全 xy_to_polar —— 注意角度要用 atan2")


# ==================================================================
# M6 · 空间：球坐标 ⇄ 直角坐标
# ==================================================================
def sph2cart(r, theta, phi):
    """球坐标 → 直角坐标。

    约定
    ----
    * ``r``     : 到原点的距离
    * ``theta`` : 方位角（在 x-y 平面内，从 x 轴转向 y 轴）
    * ``phi``   : 极角（从 **+z 轴**量起，0 = 正上方）

    返回
    ----
    (x, y, z)

    提示
    ----
    先固定 ``phi = 90°``，它就退化成平面极坐标；再放开 phi，z 分量就出来了。
    """
    # TODO(M6):  x = r*sin(phi)*cos(theta)
    #           y = r*sin(phi)*sin(theta)
    #           z = r*cos(phi)
    raise NotImplementedError("TODO(M6): 补全 sph2cart —— 注意哪个角配 sin、哪个配 cos")


def cart2sph(x, y, z):
    """直角坐标 → (r, theta, phi)，约定同 :func:`sph2cart`。

    提示
    ----
    * ``r  = sqrt(x²+y²+z²)``
    * ``theta = atan2(y, x)``
    * ``phi   = atan2(sqrt(x²+y²), z)``   ← 注意用的是"到 z 轴的距离"
    """
    # TODO(M6): 反向的三个公式
    raise NotImplementedError("TODO(M6): 补全 cart2sph")
