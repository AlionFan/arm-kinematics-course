# -*- coding: utf-8 -*-
"""
正 / 逆运动学（平台层）
========================
* :func:`fk`          —— 正运动学：关节角 → 末端位姿（可选用学生旋转积木驱动）
* :func:`ik`          —— 逆运动学：目标位姿 → 关节角（数值法，作「真值」对照）
* :func:`link_frames` —— 各连杆坐标系，供可视化

本文件属于**平台层**，学生无需修改。
"""
from __future__ import annotations

import numpy as np

from .transform import (homogeneous, rpy_to_matrix, axis_rotation, matrix_to_rotvec)

_ZERO = np.zeros(3)


# ------------------------------------------------------------------ 正运动学
def joint_transform(joint, q, rot=None) -> np.ndarray:
    """单个关节（或固定节）的齐次变换：**T = 平移(origin_xyz) · 固定旋转(rpy) · 绕轴旋转(q)**。

    这正是课程里反复强调的"变换链"的一环：
    固定部分描述"关节装在哪里、朝哪边"，旋转部分描述"这次转了 q 角"。
    固定关节没有自由度，等价于 ``q = 0``。
    """
    T = homogeneous(rpy_to_matrix(*joint.origin_rpy, rot=rot), joint.origin_xyz)
    Rq = axis_rotation(joint.axis, q, rot)
    return T @ homogeneous(Rq, _ZERO)


def link_frames(model, q, rot=None) -> list[np.ndarray]:
    """返回从底座到末端的**每一节**位姿矩阵 ``[T0, T1, …, TN]``（T0 = 底座）。

    链条里含固定关节（如 UR5 的 ``base_link_inertia`` / ``flange`` / ``tool0``），
    它们不消耗 ``q`` 里的角度，但同样贡献一次变换 —— 所以末位就是真正的末端坐标系。
    """
    q = np.asarray(q, dtype=float)
    frames = [np.eye(4)]
    T = np.eye(4)
    k = 0
    for j in model.segments:
        if j.is_revolute:
            qi = q[k]
            k += 1
        else:
            qi = 0.0
        T = T @ joint_transform(j, qi, rot)
        frames.append(T.copy())
    return frames


def fk(model, q, rot=None):
    """正运动学：给定关节角 ``q``，返回末端 (位置(3,), 姿态矩阵(3,3))。

    * ``rot=None``                  → 用罗德里格斯真值（**参考答案路径**）
    * ``rot=blocks.rotations``      → 用**学生写的旋转积木**（教学路径）
    """
    T = link_frames(model, q, rot)[-1]
    return T[:3, 3].copy(), T[:3, :3].copy()


# ------------------------------------------------------------------ 逆运动学
def _jacobian(model, q, rot=None, eps=1e-6) -> np.ndarray:
    """数值雅可比 (6×dof)：末端的平移/旋转速度对关节角速度的敏感度。"""
    p0, R0 = fk(model, q, rot)
    J = np.zeros((6, model.dof))
    for i in range(model.dof):
        dq = np.zeros(model.dof)
        dq[i] = eps
        p1, R1 = fk(model, q + dq, rot)
        J[:3, i] = (p1 - p0) / eps
        J[3:, i] = matrix_to_rotvec(R1 @ R0.T) / eps
    return J


def _pose_error(p, R, p_t, R_t):
    e = p_t - p
    if R_t is not None:
        e = np.concatenate([e, matrix_to_rotvec(R_t @ R.T)])
    return e


def ik(model, p_target, R_target=None, q0=None, iters=600, lam=0.06,
       tol=1e-4, rot=None, restarts=6, rng=None) -> np.ndarray:
    """数值逆运动学（阻尼最小二乘 DLS）—— 作为课程的「真值」参照。

    说明：UR5 有解析解，但课堂上让学生推的是**几何子问题**（平面 2R 的余弦定理、
    球腕的欧拉角），完整 6 轴联立反而繁琐；R1 则是 7 自由度冗余臂，解析解更复杂。
    所以这里统一用数值法给出"一组可用解"，学生拿它做对照。
    """
    rng = rng or np.random.default_rng(0)
    p_target = np.asarray(p_target, dtype=float)
    R_target = None if R_target is None else np.asarray(R_target, dtype=float)

    starts = [q0 if q0 is not None else model.home()]
    starts += [model.random_q(rng) for _ in range(max(0, restarts))]

    best_q, best_err = None, np.inf
    for s in starts:
        q = model.clip(np.asarray(s, dtype=float))
        for _ in range(iters):
            p, R = fk(model, q, rot)
            e = _pose_error(p, R, p_target, R_target)
            err = float(np.linalg.norm(e))
            if err < best_err:
                best_q, best_err = q.copy(), err
            if err < tol:
                return q
            J = _jacobian(model, q, rot)
            A = J @ J.T + (lam ** 2) * np.eye(J.shape[0])
            dq = J.T @ np.linalg.solve(A, e)
            step = np.linalg.norm(dq)
            if step > 0.5:                       # 限制单步，避免跳飞
                dq *= 0.5 / step
            q = model.clip(q + dq)
    return best_q


# ------------------------------------------------------------------ 工具
def reachable_pair(model, rng=None):
    """随机取一个**保证可达**的目标：随机 q → 正解 → (目标位姿, 真值 q)。"""
    rng = rng or np.random.default_rng(1)
    q_true = model.random_q(rng)
    p, R = fk(model, q_true)
    return (p, R), q_true
