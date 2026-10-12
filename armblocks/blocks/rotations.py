# -*- coding: utf-8 -*-
"""
积木 · 旋转矩阵 ★ 最关键的一块
================================
对应课程 **M7（旋转矩阵的三角本质）**。

.. important::
   旋转矩阵**不是黑魔法**——它只是把一批 sin / cos 打包成表格。
   逐列看：矩阵的**第一列**就是"原来的 x 轴转到哪去了"，
   那个新坐标恰好是 ``(cos α, sin α)``。

这三块积木写对，**两台机械臂的正运动学就都通了**：

* **UR5**（主力，6 轴）：6 个关节全部 ``axis = 0 0 1``，每转一次都调用 ``rot_z``；
  关节原点里的 ``rpy = (π/2, 0, 0)``（标准 DH 的 α 角）会调用 ``rot_x`` / ``rot_y``。
* **宇树 R1**（对照，7 轴）：关节轴是 z / x / y 混合，三块都会被直接调用。
"""
from __future__ import annotations

import numpy as np


def rot_x(alpha):
    """绕 **x 轴** 旋转 ``alpha`` 弧度，返回 3×3 旋转矩阵。

    结构（把 ``?`` 换成 ``cos(alpha)`` / ``sin(alpha)`` / ``0`` / ``-sin(alpha)``）::

        [ 1    0      0   ]
        [ 0    ?      ?   ]
        [ 0    ?      ?   ]

    提示
    ----
    绕 x 轴转，x 坐标不变；y、z 坐标像平面里那样转一个角度。
    """
    # TODO(M7): 补全绕 x 轴的旋转矩阵
    raise NotImplementedError("TODO(M7): 补全 rot_x")


def rot_y(beta):
    """绕 **y 轴** 旋转 ``beta`` 弧度，返回 3×3 旋转矩阵。

    结构::

        [ ?    0    ? ]
        [ 0    1    0 ]
        [ ?    0    ? ]

    提示
    ----
    绕 y 轴转，y 坐标不变；x、z 坐标在 x-z 平面里转。
    注意：与 rot_x 相比，sin 的**正负号位置**会不一样（右手系）。
    """
    # TODO(M7): 补全绕 y 轴的旋转矩阵
    raise NotImplementedError("TODO(M7): 补全 rot_y")


def rot_z(gamma):
    """绕 **z 轴** 旋转 ``gamma`` 弧度，返回 3×3 旋转矩阵。

    结构::

        [ ?    ?    0 ]
        [ ?    ?    0 ]
        [ 0    0    1 ]

    提示
    ----
    这是你 M2 就学过的东西：平面里把点转一个角。
    第一列 = 原 x 轴转后的坐标 = ``(cos γ, sin γ, 0)``。
    """
    # TODO(M7): 补全绕 z 轴的旋转矩阵
    raise NotImplementedError("TODO(M7): 补全 rot_z")
