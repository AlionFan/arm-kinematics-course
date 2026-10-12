# -*- coding: utf-8 -*-
"""
齐次变换工具 —— 三角函数的「打包」与「搬运」
================================================
包含 rpy→旋转矩阵、罗德里格斯公式等**已实现**的基础工具。

关键点：:func:`axis_rotation` 在「轴与坐标轴对齐」时，会**调用学生的积木**
``blocks.rotations.rot_x / rot_y / rot_z``。因此：

    学生把三个旋转矩阵积木写对 → 两台机械臂（UR5 与宇树 R1）的正运动学都通了。

* **UR5**：6 个关节全部 ``axis = 0 0 1`` → 每次转动都调用 ``rot_z``；
  而关节原点里的 ``rpy = (π/2, 0, 0)``（标准 DH 的 α）会经 :func:`rpy_to_matrix`
  调用 ``rot_x`` / ``rot_y``。
* **宇树 R1**：关节轴为 z / x / y 混合，三块积木都会被关节转动直接调用。

本文件属于**平台层**，学生无需修改。
"""
from __future__ import annotations

import numpy as np

_EPS = 1e-12


# ---------------------------------------------------------------- 基础
def homogeneous(R=None, p=None) -> np.ndarray:
    """由旋转矩阵 R(3×3) 与平移 p(3,) 组装 4×4 齐次变换矩阵。"""
    T = np.eye(4)
    if R is not None:
        T[:3, :3] = np.asarray(R, dtype=float)
    if p is not None:
        T[:3, 3] = np.asarray(p, dtype=float)
    return T


def rpy_to_matrix(roll, pitch, yaw, rot=None) -> np.ndarray:
    """URDF 的固定轴 rpy → 旋转矩阵：R = Rz(yaw) · Ry(pitch) · Rx(roll)。

    * ``rot=None``            → 直接展开（真值路径，不依赖学生积木）
    * ``rot=blocks.rotations``→ **调用学生的三块旋转积木**（教学路径）

    UR5 的关节原点带 ``rpy = (π/2, 0, 0)`` 这类固定旋转（标准 DH 的 α 角），
    所以走 ``rot`` 这条路径时，学生的 ``rot_x`` / ``rot_y`` / ``rot_z``
    **三块都会真正被用到**。
    """
    if rot is not None:
        return (axis_rotation((0, 0, 1), yaw, rot)
                @ axis_rotation((0, 1, 0), pitch, rot)
                @ axis_rotation((1, 0, 0), roll, rot))

    cr, sr = np.cos(roll), np.sin(roll)
    cp, sp = np.cos(pitch), np.sin(pitch)
    cy, sy = np.cos(yaw), np.sin(yaw)
    Rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
    Ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]])
    Rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def rodrigues(axis, angle) -> np.ndarray:
    """罗德里格斯公式：绕任意单位轴 ``axis`` 旋转 ``angle`` 弧度。

    R = I + sinθ·K + (1−cosθ)·K²    （K 为 axis 的反对称矩阵）
    """
    a = np.asarray(axis, dtype=float)
    n = np.linalg.norm(a)
    if n < _EPS:
        return np.eye(3)
    a = a / n
    K = np.array([[0, -a[2], a[1]],
                  [a[2], 0, -a[0]],
                  [-a[1], a[0], 0]])
    return np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * (K @ K)


# ---------------------------------------------------------------- 调度
def axis_rotation(axis, angle, rot=None) -> np.ndarray:
    """绕 ``axis`` 旋转 ``angle``。

    参数
    ----
    axis  : (3,) 旋转轴（子坐标系下）
    angle : 弧度
    rot   : 提供 ``rot_x/rot_y/rot_z`` 的模块。
            * 传入 ``blocks.rotations`` → 用**学生积木**（教学路径）
            * 传 ``None``               → 用罗德里格斯公式（真值路径）
    """
    a = np.asarray(axis, dtype=float)
    n = np.linalg.norm(a)
    if n < _EPS:
        return np.eye(3)
    a = a / n

    if rot is not None:
        for i, fn_name in enumerate(("rot_x", "rot_y", "rot_z")):
            if abs(abs(a[i]) - 1.0) < 1e-6:          # 轴与第 i 个坐标轴对齐
                return np.asarray(getattr(rot, fn_name)(a[i] * angle), dtype=float)

    return rodrigues(a, angle)                        # 非对齐轴 → 兜底真值


def rotvec_to_matrix(v) -> np.ndarray:
    """旋转向量(轴×角) → 旋转矩阵。"""
    v = np.asarray(v, dtype=float)
    ang = np.linalg.norm(v)
    if ang < _EPS:
        return np.eye(3)
    return rodrigues(v / ang, ang)


def matrix_to_rotvec(R) -> np.ndarray:
    """旋转矩阵 → 旋转向量(轴×角)，用于计算姿态误差。"""
    R = np.asarray(R, dtype=float)
    v = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])
    s = np.linalg.norm(v) / 2.0
    c = (np.trace(R) - 1.0) / 2.0
    ang = np.arctan2(s, c)
    if s < 1e-9:
        return np.zeros(3)
    return v / np.linalg.norm(v) * ang
