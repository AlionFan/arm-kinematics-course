# -*- coding: utf-8 -*-
"""
UR5 正运动学的**独立交叉验证**
================================
本文件用一条与 ``armblocks`` 完全无关的路径重算 UR5 正解：**教科书标准 DH 矩阵**。

* 一条路径：``armblocks`` 解析官方 URDF（关节原点 xyz/rpy + axis）
* 另一条路径：Universal Robots 公开的 DH 表，直接乘 4×4 矩阵

两条路径对同一组关节角给出相同的末端位姿，才能说明模型没问题。

DH 表（classic / distal，长度 m，角度 rad）::

    i   a_i        d_i        α_i
    1   0          0.089159   π/2
    2   −0.425     0           0
    3   −0.39225   0           0
    4   0          0.10915    π/2
    5   0          0.09465   −π/2
    6   0          0.0823     0

.. note::
   DH 的 frame 0 就是 UR 控制器的 ``Base`` 坐标系；而 URDF 的 ``base_link``
   是 REP-103 对齐的（X+ 朝前），两者相差一个绕 z 的 π。
"""
import numpy as np
import pytest

from armblocks import UR5_URDF, load_model
from armblocks.core.kinematics import link_frames

PI = np.pi
DH = [
    (0.0, 0.089159, 0.0, PI / 2),
    (0.0, 0.0, -0.425, 0.0),
    (0.0, 0.0, -0.39225, 0.0),
    (0.0, 0.10915, 0.0, PI / 2),
    (0.0, 0.09465, 0.0, -PI / 2),
    (0.0, 0.0823, 0.0, 0.0),
]

#: Base → base_link 的固定变换（绕 z 转 π）
BASE_TO_BASE_LINK = np.array([[-1, 0, 0, 0],
                              [0, -1, 0, 0],
                              [0, 0, 1, 0],
                              [0, 0, 0, 1]], dtype=float)


def dh_transform(theta, d, a, alpha):
    """单个 DH 环节的 4×4 变换：Rz(θ)·Tz(d)·Tx(a)·Rx(α)。"""
    ct, st = np.cos(theta), np.sin(theta)
    ca, sa = np.cos(alpha), np.sin(alpha)
    return np.array([
        [ct, -st * ca,  st * sa, a * ct],
        [st,  ct * ca, -ct * sa, a * st],
        [0.0,      sa,       ca,      d],
        [0.0,     0.0,      0.0,    1.0],
    ])


def fk_dh(q):
    """纯 DH 正运动学（与 armblocks 无关的独立实现）。"""
    T = np.eye(4)
    for theta, (off, d, a, alpha) in zip(q, DH):
        T = T @ dh_transform(theta + off, d, a, alpha)
    return T


@pytest.mark.parametrize("q_deg", [
    [0, 0, 0, 0, 0, 0],
    [90, -90, 0, -90, 0, 0],
    [10, -20, 30, -40, 50, -60],
    [-90, 0, 45, 90, -135, 180],
    [37, 12, -128, 76, -53, 141],
    [180, 180, 180, 180, 180, 180],
])
def test_urdf_matches_standard_dh(q_deg):
    """URDF 解析结果与标准 DH 矩阵在数值上必须一致。"""
    model = load_model(UR5_URDF)
    q = np.radians(q_deg)

    T_urdf_in_base = BASE_TO_BASE_LINK @ link_frames(model, q)[-1]
    T_dh = fk_dh(q)

    assert np.linalg.norm(T_urdf_in_base[:3, 3] - T_dh[:3, 3]) < 1e-9
    assert np.abs(T_urdf_in_base[:3, :3] - T_dh[:3, :3]).max() < 1e-8


def test_ur5_zero_pose_closed_form():
    """零位末端的闭式解：Base 系下 (a₂+a₃, −(d₄+d₆), d₁−d₅)。"""
    model = load_model(UR5_URDF)
    a2, a3 = DH[1][2], DH[2][2]
    d1, d4, d5, d6 = DH[0][1], DH[3][1], DH[4][1], DH[5][1]
    assert np.allclose(fk_dh(np.zeros(6))[:3, 3],
                       [a2 + a3, -(d4 + d6), d1 - d5], atol=1e-9)
