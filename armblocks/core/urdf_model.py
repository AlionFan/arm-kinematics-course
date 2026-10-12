# -*- coding: utf-8 -*-
"""
URDF 解析 → 关节链模型
======================
把机械臂的 ``.urdf`` 读成一条「从底座到末端」的有序关节链，供正/逆运动学使用。

本课程支持两台机器：

* **UR5**（主力）：6 自由度，标准 DH，全部关节绕自身 z 轴；
* **宇树 R1**（对照）：7 自由度，轴排布为 z/x/y/x/y/x/z。

解析时会**把链条里的固定关节一起收进** :attr:`ArmModel.segments`
（例如 UR5 的 ``base_link → base_link_inertia``、末端的 ``flange`` / ``tool0``），
这样末端坐标系才能真正落到 ``tool0`` 上。

本文件属于**平台层**，已实现完毕，学生无需修改。
"""
from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

import numpy as np

_EPS = 1e-9


@dataclass
class Joint:
    """链条里的一节（可动关节或固定关节）的静态参数（来自 URDF）。"""
    name: str
    parent: str
    child: str
    origin_xyz: np.ndarray          # 父坐标系 → 子坐标系 的平移
    origin_rpy: np.ndarray          # 父坐标系 → 子坐标系 的固定旋转（roll,pitch,yaw）
    axis: np.ndarray                # 旋转轴（子坐标系下，单位向量）
    lower: float                    # 关节下限（弧度）
    upper: float                    # 关节上限（弧度）
    effort: float = 0.0
    velocity: float = 0.0
    type: str = "revolute"
    mesh: str | None = None         # 子连杆的可视网格（用于渲染）

    @property
    def is_revolute(self) -> bool:
        """是否是可动旋转关节（``fixed`` 为 False）。"""
        return self.type in ("revolute", "continuous")

    def align_axis(self):
        """若旋转轴与某坐标轴对齐，返回 (+1/-1, 'x'|'y'|'z')，否则返回 None。"""
        a = self.axis / (np.linalg.norm(self.axis) + _EPS)
        for i, ch in enumerate("xyz"):
            if abs(abs(a[i]) - 1.0) < 1e-6:
                return (1 if a[i] > 0 else -1), ch
        return None


@dataclass
class ArmModel:
    """一条串联臂：有序的关节链 + 关节限位。

    .. important::
       ``segments`` 是**完整链条**（含固定关节），``joints`` 只含**可动关节**。
       学生写的关节角向量 ``q`` 与 ``joints`` 一一对应，长度等于 :attr:`dof`。
    """
    name: str
    urdf_path: str
    segments: list[Joint] = field(default_factory=list)
    links: list[str] = field(default_factory=list)

    # ---- 可动关节 ----------------------------------------------------
    @property
    def joints(self) -> list[Joint]:
        """可动关节（顺序 = ``q`` 的顺序）。"""
        return [j for j in self.segments if j.is_revolute]

    @property
    def fixed_joints(self) -> list[Joint]:
        """链条中的固定关节（不占 ``q`` 的位置，但会贡献位姿变换）。"""
        return [j for j in self.segments if not j.is_revolute]

    # ---- 便捷属性 ----------------------------------------------------
    @property
    def dof(self) -> int:
        """自由度（可动关节数）。"""
        return len(self.joints)

    @property
    def joint_names(self) -> list[str]:
        return [j.name for j in self.joints]

    @property
    def limits(self) -> np.ndarray:
        """关节限位，形状 (dof, 2)。"""
        return np.array([[j.lower, j.upper] for j in self.joints], dtype=float)

    @property
    def base_link(self) -> str:
        return self.segments[0].parent

    @property
    def tip_link(self) -> str:
        return self.segments[-1].child

    @property
    def link_lengths(self) -> list[float]:
        """相邻关节原点之间的直线距离（画「等效连杆」用）。"""
        out = []
        for j in self.segments:
            if j.is_revolute:
                out.append(float(np.linalg.norm(j.origin_xyz)))
        return out or [float(np.linalg.norm(j.origin_xyz)) for j in self.segments]

    def home(self) -> np.ndarray:
        """默认零位（全部关节角 = 0）。"""
        return np.zeros(self.dof)

    def clip(self, q) -> np.ndarray:
        """把关节角裁剪到限位范围内。"""
        lim = self.limits
        return np.clip(np.asarray(q, dtype=float), lim[:, 0], lim[:, 1])

    def random_q(self, rng: np.random.Generator | None = None) -> np.ndarray:
        """在限位内随机取一组关节角（用于生成「保证可达」的目标）。"""
        rng = rng or np.random.default_rng()
        lim = self.limits
        return lim[:, 0] + rng.random(self.dof) * (lim[:, 1] - lim[:, 0])

    def mesh_path(self, joint: Joint) -> str | None:
        """把 URDF 中的相对网格路径解析为绝对路径。"""
        if not joint.mesh:
            return None
        rel = joint.mesh
        for prefix in ("package://", "file://"):
            if rel.startswith(prefix):
                rel = rel[len(prefix):]
        return os.path.normpath(os.path.join(os.path.dirname(self.urdf_path), rel))


# ---------------------------------------------------------------------
def load_model(urdf_path) -> ArmModel:
    """读取 URDF，返回从底座到末端排好序的 :class:`ArmModel`。"""
    urdf_path = os.path.abspath(str(urdf_path))
    root = ET.parse(urdf_path).getroot()

    links = [e.get("name") for e in root.findall("link")]
    mesh_of_link: dict[str, str] = {}
    for link in root.findall("link"):
        vis = link.find("visual")
        if vis is not None:
            m = vis.find("geometry/mesh")
            if m is not None:
                mesh_of_link[link.get("name")] = m.get("filename")

    all_joints: list[Joint] = []
    children: set[str] = set()
    for j in root.findall("joint"):
        jtype = (j.get("type") or "revolute").lower()
        if jtype in ("floating", "planar"):
            continue                     # 本课不涉及
        origin = j.find("origin")
        xyz = _vec(origin.get("xyz") if origin is not None else None, [0, 0, 0])
        rpy = _vec(origin.get("rpy") if origin is not None else None, [0, 0, 0])
        ax = j.find("axis")
        axis = _vec(ax.get("xyz") if ax is not None else None, [0, 0, 1])
        lim = j.find("limit")
        lo = float(lim.get("lower", -np.inf)) if lim is not None else -np.inf
        hi = float(lim.get("upper", np.inf)) if lim is not None else np.inf
        child = j.find("child").get("link")
        children.add(child)
        all_joints.append(Joint(
            name=j.get("name"),
            parent=j.find("parent").get("link"),
            child=child,
            origin_xyz=xyz,
            origin_rpy=rpy,
            axis=axis,
            lower=lo,
            upper=hi,
            effort=float(lim.get("effort", 0.0)) if lim is not None else 0.0,
            velocity=float(lim.get("velocity", 0.0)) if lim is not None else 0.0,
            type=jtype,
            mesh=mesh_of_link.get(child),
        ))

    # 排序：从「不是任何关节子连杆」的根连杆出发，沿 parent → child 串起来。
    roots = [ln for ln in links if ln not in children]
    if not roots:
        raise ValueError("URDF 中找不到根连杆（可能形成闭环）。")

    by_parent: dict[str, list[Joint]] = {}
    for j in all_joints:
        by_parent.setdefault(j.parent, []).append(j)

    # 若某连杆有多个子关节（如 UR5 的 base_link 同时挂着 base 与
    # base_link_inertia），优先走「下游可动关节更多」的那条，保证取到主运动链。
    memo: dict[str, int] = {}

    def _chain_movable(link: str, seen: frozenset[str] = frozenset()) -> int:
        if link in memo:
            return memo[link]
        if link in seen:
            return 0                                  # 防环
        best = 0
        for j in by_parent.get(link, []):
            n = (1 if j.is_revolute else 0) + _chain_movable(j.child, seen | {link})
            best = max(best, n)
        memo[link] = best
        return best

    ordered: list[Joint] = []
    cur = roots[0]
    guard = 0
    while guard <= len(all_joints) + 1:
        guard += 1
        cands = by_parent.get(cur, [])
        if not cands:
            break
        nxt = max(cands, key=lambda j: (_chain_movable(j.child), j.is_revolute))
        ordered.append(nxt)
        cur = nxt.child

    if not any(j.is_revolute for j in ordered):
        raise ValueError("URDF 中找不到可动关节。")
    return ArmModel(name=root.get("name", "robot"), urdf_path=urdf_path,
                    segments=ordered, links=links)


def _vec(text, default) -> np.ndarray:
    if not text:
        return np.array(default, dtype=float)
    return np.array([float(v) for v in text.split()], dtype=float)
