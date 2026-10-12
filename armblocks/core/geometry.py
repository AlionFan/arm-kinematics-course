# -*- coding: utf-8 -*-
"""
关节几何分析（平台层）
========================
回答课程里两个很实际的问题：

1. **某根关节轴在空间里是哪条直线？** —— :func:`joint_axis`
2. **"球形手腕"到底成不成立？** —— :func:`wrist_report`

"球形手腕"（spherical / monocentric wrist）的定义是：
最后三个关节的轴线**交于同一点**。交于同一点时，
末端**位置**只由前几个关节决定、**姿态**只由腕关节决定，
于是逆运动学能"位置 / 姿态解耦"。

.. important::
   实测结论（见 ``demos/demo_wrist_geometry.py``）：

   ======================  ==========================================
   机型                    腕部几何
   ======================  ==========================================
   **UR5**（主力）          **不是**球形腕：轴 4 ∥ 轴 6，相距 94.65 mm
   **宇树 R1**（对照）       轴 5 / 6 / 7 两两异面，同样不是球形腕
   ======================  ==========================================

   所以"用球坐标解位置 + 用欧拉角解姿态"这套漂亮的分工，
   在真实机型上只是**近似**。这不影响教学（子问题照样要练），
   但必须让学生知道真相 —— 这也正是本课程"用数值 IK 做对照"的意义。

本文件属于**平台层**，学生无需修改。
"""
from __future__ import annotations

import numpy as np

from .transform import rpy_to_matrix

_EPS = 1e-12


def joint_axis(model, q, joint_name: str):
    """返回关节 ``joint_name`` 在**基座坐标系**下的旋转轴直线 ``(点, 单位方向)``。

    旋转轴一定通过该关节的**子连杆原点**，方向为子连杆姿态作用在该关节
    ``axis`` 上的结果。固定关节没有旋转，返回 ``None``。
    """
    q = np.asarray(q, dtype=float)
    T = np.eye(4)
    k = 0
    for j in model.segments:
        qi = q[k] if j.is_revolute else 0.0
        if j.is_revolute:
            k += 1
        if j.name == joint_name:
            if not j.is_revolute:
                return None
            R = T[:3, :3] @ rpy_to_matrix(*j.origin_rpy)
            p = T[:3, 3] + T[:3, :3] @ j.origin_xyz
            d = R @ (j.axis / (np.linalg.norm(j.axis) + _EPS))
            return p, d
        T = T @ _segment_transform(j, qi)
    raise KeyError(f"找不到关节 {joint_name!r}")


def _segment_transform(joint, q) -> np.ndarray:
    """与 ``core.kinematics.joint_transform`` 等价（这里独立实现，避免循环导入）。"""
    from .transform import homogeneous, axis_rotation
    T = homogeneous(rpy_to_matrix(*joint.origin_rpy), joint.origin_xyz)
    if not joint.is_revolute:
        return T
    return T @ homogeneous(axis_rotation(joint.axis, q), np.zeros(3))


def line_distance(p1, d1, p2, d2, tol=1e-7):
    """两条直线的公垂线距离，以及是否平行。

    距离为 0 表示两轴**相交**；平行时给出的是两平行线间的垂直距离。
    """
    p1, d1, p2, d2 = map(np.asarray, (p1, d1, p2, d2))
    d1 = d1 / (np.linalg.norm(d1) + _EPS)
    d2 = d2 / (np.linalg.norm(d2) + _EPS)
    n = np.cross(d1, d2)
    nn = np.linalg.norm(n)
    if nn < tol:                                    # 平行（或重合）
        return float(np.linalg.norm(np.cross(p2 - p1, d1))), True
    return float(abs(np.dot(p2 - p1, n / nn))), False


def wrist_report(model, q=None, wrist_joints: int = 3) -> dict:
    """检查一台机械臂**最后 ``wrist_joints`` 个关节**是否构成球形手腕。

    返回 dict：
        ``joints``/``points``/``directions``  轴的信息（基座坐标系）
        ``pairs``   两两轴的 (名称, 最短距离[m], 平行?) 
        ``concurrent``  三轴是否共点（球形手腕）
        ``common_point`` 共点时的那一点，否则 None
        ``max_offset``  到"最理想公共点"的最大偏差（越小越接近球形）
    """
    names = model.joint_names[-wrist_joints:]
    q = model.home() if q is None else np.asarray(q, dtype=float)
    axes = {n: joint_axis(model, q, n) for n in names}

    pairs = []
    for i in range(len(names)):
        for k in range(i + 1, len(names)):
            a, b = names[i], names[k]
            dist, par = line_distance(*axes[a], *axes[b])
            pairs.append({"pair": (a, b), "distance": dist, "parallel": par})

    # 共点判据：所有两两距离都接近 0，且不存在平行轴
    concurrent = all(p["distance"] < 1e-6 and not p["parallel"] for p in pairs)

    # "最接近公共点"的最小二乘解：到各轴距离平方和最小
    common = _closest_common_point([axes[n] for n in names]) if not concurrent else None
    max_offset = None
    if not concurrent and common is not None:
        max_offset = max(_point_line_distance(common, *axes[n]) for n in names)

    return {
        "model": model.name,
        "joints": names,
        "points": {n: axes[n][0] for n in names},
        "directions": {n: axes[n][1] for n in names},
        "pairs": pairs,
        "concurrent": bool(concurrent),
        "common_point": common,
        "max_offset": max_offset,
    }


def _point_line_distance(p, p0, d) -> float:
    v = np.asarray(p, float) - np.asarray(p0, float)
    d = np.asarray(d, float)
    return float(np.linalg.norm(np.cross(v, d)) / (np.linalg.norm(d) + _EPS))


def _closest_common_point(axes) -> np.ndarray:
    """求一个点，使得到各条轴线距离的平方和最小（最小二乘"腕心"）。"""
    A = np.zeros((3, 3))
    b = np.zeros(3)
    for p, d in axes:
        d = np.asarray(d, float)
        d = d / (np.linalg.norm(d) + _EPS)
        P = np.eye(3) - np.outer(d, d)          # 投影到 ⊥d 的平面
        A += P
        b += P @ np.asarray(p, float)
    return np.linalg.solve(A, b)


def print_wrist_report(model, q=None) -> None:
    """把 :func:`wrist_report` 的结果打印成一张可读的表。"""
    r = wrist_report(model, q)
    print(f"——— {model.name} 腕部几何 ———")
    for n in r["joints"]:
        p, d = r["points"][n], r["directions"][n]
        print(f"  {n:<18} 轴上一点 {np.array2string(p, precision=5)}"
              f"   方向 {np.array2string(d, precision=4)}")
    for it in r["pairs"]:
        a, b = it["pair"]
        tag = "  ← 平行!" if it["parallel"] else ""
        print(f"  轴间最短距离 {a[:8]}–{b[:8]}: {it['distance'] * 1000:9.3f} mm{tag}")
    if r["concurrent"]:
        print("  ⇒ 三轴交于一点：**是**球形手腕")
    else:
        print(f"  ⇒ 三轴**不共点**（最大偏差 {r['max_offset'] * 1000:.2f} mm）"
              f"：不是球形手腕，位置/姿态无法严格解耦")
    print()
