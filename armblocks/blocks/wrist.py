# -*- coding: utf-8 -*-
"""
积木 · 姿态：球形手腕的欧拉角
==============================
对应课程 **M10（姿态逆解：球形手腕）**。

位置解决"手在哪里"，**姿态**解决"手朝向哪儿"。
R1 的腕部 J5/J6/J7 三轴相交（近似球形手腕），
于是"给一个目标姿态矩阵 → 反解三个腕关节角"就变成一个**欧拉角问题**——
而它依然是 ``atan2`` 和 ``sin / cos``。
"""
from __future__ import annotations

import numpy as np


def matrix_from_euler_zyx(alpha, beta, gamma):
    """由 ZYX 欧拉角组装旋转矩阵：``R = Rz(alpha) · Ry(beta) · Rx(gamma)``。

    提示
    ----
    就是用你 M7 写好的三块旋转积木**依次相乘**——顺序很重要！
    """
    # TODO(M10): 用 rot_z / rot_y / rot_x 三个矩阵按 Rz·Ry·Rx 相乘
    raise NotImplementedError("TODO(M10): 补全 matrix_from_euler_zyx")


def euler_zyx_from_matrix(R):
    """从旋转矩阵反解 ZYX 欧拉角 ``(alpha, beta, gamma)``。

    约定：``R = Rz(alpha) · Ry(beta) · Rx(gamma)``

    返回
    ----
    (alpha, beta, gamma) ：弧度

    提示
    ----
    把 ``Rz(α)·Ry(β)·Rx(γ)`` 展开后（记 c=cos, s=sin），会得到::

        R[2,0] = −sin β
        R[1,0] = sin α · cos β        R[0,0] = cos α · cos β
        R[2,1] = cos β · sin γ        R[2,2] = cos β · cos γ

    于是：
    * ``beta  = atan2(−R[2,0], sqrt(R[0,0]² + R[1,0]²))``
    * ``alpha = atan2(R[1,0], R[0,0])``
    * ``gamma = atan2(R[2,1], R[2,2])``

    .. note::
       当 ``beta = ±90°`` 时 cos β = 0，α 与 γ 会"挤在一起"无法分开——
       这就是**万向节死锁（gimbal lock）**，也是 R1 腕部的奇异位形。
    """
    # TODO(M10): 用上面的三条 atan2 公式
    raise NotImplementedError("TODO(M10): 补全 euler_zyx_from_matrix —— 全用 atan2")
