# -*- coding: utf-8 -*-
"""
可视化（平台层）
================
用 matplotlib 画机械臂的**运动学骨架**（关节点位 + 连杆 + 末端坐标系）。

.. note::
   这里画的是"骨架"，用于看清几何关系；要渲染 UR5 / R1 的真实
   ``.dae`` / ``.stl`` 外观，请用 PyBullet 加载 ``models/`` 下的 URDF
   （网格文件已随仓库提供）。
"""
from __future__ import annotations

import numpy as np

from .core.kinematics import link_frames

import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  (注册 3D 投影)

from .plotstyle import use_cjk_font
from . import display_name as _display_name

use_cjk_font()

_LINK_CMAP = plt.get_cmap("viridis")


def new_axes(figsize=(7, 6)):
    """新建一个 3D 坐标轴。"""
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection="3d")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_zlabel("Z (m)")
    return fig, ax


def _set_equal(ax, points, pad=0.12):
    c = points.mean(axis=0)
    r = float(np.abs(points - c).max()) + pad
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r, c[2] + r)
    try:
        ax.set_box_aspect((1, 1, 1))
    except Exception:                                # pragma: no cover
        pass


def _draw_frame(ax, T, length=0.05, lw=2.0):
    o = T[:3, 3]
    for i, col in enumerate(("r", "g", "b")):
        d = T[:3, i] * length
        ax.plot([o[0], o[0] + d[0]], [o[1], o[1] + d[1]], [o[2], o[2] + d[2]],
                color=col, lw=lw, solid_capstyle="round")


def plot_arm(model, q, rot=None, ax=None, show_tip_frame=True,
             title=None, show=True):
    """把机械臂在姿态 ``q`` 下画出来（运动学骨架）。"""
    frames = link_frames(model, q, rot)
    pts = np.array([T[:3, 3] for T in frames])
    n = len(pts) - 1

    if ax is None:
        _, ax = new_axes()
        show = True

    for i in range(n):
        ax.plot(*zip(pts[i], pts[i + 1]), color=_LINK_CMAP(i / max(n - 1, 1)),
                lw=4.0, solid_capstyle="round", zorder=3)
    ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], s=28, c="#1a2233",
               depthshade=False, zorder=4)
    ax.scatter(*pts[-1], s=90, c="#c0392b", depthshade=False, zorder=5,
               label="末端 (end-effector)")
    _draw_frame(ax, frames[0], length=0.06)
    if show_tip_frame:
        _draw_frame(ax, frames[-1], length=0.06)

    ax.set_title(title or f"{_display_name(model)}  |  q = " +
                 np.array2string(np.asarray(q), precision=2, suppress_small=True),
                 fontsize=10)
    _set_equal(ax, pts)
    ax.legend(loc="upper right", fontsize=8)
    if show:
        plt.tight_layout()
        plt.show()
    return ax


def plot_workspace(model, n=4000, q_fixed=None, rot=None, seed=0,
                   ax=None, show=True):
    """散点画出末端可达空间（工作空间），用于讲"可达 / 不可达"。"""
    rng = np.random.default_rng(seed)
    pts = []
    for _ in range(n):
        q = model.random_q(rng)
        if q_fixed:
            for k, v in q_fixed.items():
                q[k] = v
        T = link_frames(model, q, rot)[-1]
        pts.append(T[:3, 3])
    pts = np.array(pts)

    if ax is None:
        _, ax = new_axes()
        show = True
    ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], s=1.2, c=pts[:, 2],
               cmap="viridis", alpha=0.35)
    ax.set_title(f"{_display_name(model)} 可达空间（{n} 个随机姿态的末端点）", fontsize=10)
    _set_equal(ax, pts)
    if show:
        plt.tight_layout()
        plt.show()
    return ax
