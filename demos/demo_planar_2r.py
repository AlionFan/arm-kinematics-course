# -*- coding: utf-8 -*-
"""
M3 / M4 演示：平面两连杆臂的正解与逆解
=======================================
左图：给定关节角 → 末端位置（正运动学）
中图：给定目标点 → 两组解（肘上 / 肘下）（逆运动学）
右图：末端可达空间 —— 圆环

运行::

    python demos/demo_planar_2r.py
    python demos/demo_planar_2r.py --impl blocks --save out.png
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib
from demos._common import parse_args, finish

args = parse_args(__doc__)
if args.save:
    matplotlib.use("Agg")
import matplotlib.pyplot as plt

from armblocks import blocks, solutions

impl = blocks if args.impl == "blocks" else solutions
L1, L2 = 0.30, 0.22


def draw_arm(ax, q1, q2, color, label):
    x1, y1 = L1 * np.cos(q1), L1 * np.sin(q1)
    x2 = x1 + L2 * np.cos(q1 + q2)
    y2 = y1 + L2 * np.sin(q1 + q2)
    ax.plot([0, x1, x2], [0, y1, y2], "-o", lw=3, color=color, label=label, ms=5)
    return x2, y2


fig, axes = plt.subplots(1, 3, figsize=(14, 4.6))

# ---------------- 左：正运动学 ----------------
ax = axes[0]
for (q1, q2), c in [((np.radians(35), np.radians(60)), "#2f5bd7"),
                    ((np.radians(120), np.radians(-70)), "#0f9d8f")]:
    x, y = draw_arm(ax, q1, q2, c, f"q=({np.degrees(q1):.0f}°, {np.degrees(q2):.0f}°)")
    ax.annotate(f"({x:.2f}, {y:.2f})", (x, y), textcoords="offset points",
                xytext=(6, 6), fontsize=9, color=c)
ax.set_title("M3 正运动学：角度 → 位置", fontsize=11)
ax.legend(fontsize=8, loc="lower left")

# ---------------- 中：逆运动学两组解 ----------------
ax = axes[1]
tx, ty = 0.28, 0.22
sols = impl.planar.ik_2r(L1, L2, tx, ty)
ax.plot(tx, ty, "*", ms=18, color="#c0392b", label=f"目标 ({tx}, {ty})")
for (q1, q2), c, nm in zip(sols, ["#2f5bd7", "#0f9d8f"], ["解1（肘上）", "解2（肘下）"]):
    draw_arm(ax, q1, q2, c, f"{nm}: ({np.degrees(q1):.0f}°, {np.degrees(q2):.0f}°)")
ax.set_title("M4 逆运动学：一个目标，两组解", fontsize=11)
ax.legend(fontsize=8, loc="lower left")

# ---------------- 右：可达空间（圆环）----------------
ax = axes[2]
rmax, rmin = L1 + L2, abs(L1 - L2)
th = np.linspace(0, 2 * np.pi, 400)
pts = [solutions.planar.fk_2r(L1, L2, a, b)
       for a in np.linspace(-np.pi, np.pi, 45)
       for b in np.linspace(-np.pi, np.pi, 45)]
ax.scatter(*zip(*pts), s=1, alpha=0.25, color="#0f9d8f", label="末端可达点")
ax.plot(rmax * np.cos(th), rmax * np.sin(th), "--", lw=1.2, color="#2f5bd7", label="外边界 L1+L2")
ax.plot(rmin * np.cos(th), rmin * np.sin(th), "--", lw=1.2, color="#c0392b", label="内边界 |L1−L2|")
ax.set_title(f"可达空间：圆环 {rmin:.2f} ≤ r ≤ {rmax:.2f} m", fontsize=11)
ax.legend(fontsize=8, loc="lower left")

for ax in axes:
    ax.set_aspect("equal")
    ax.grid(alpha=0.3)
    ax.set_xlim(-0.6, 0.6)
    ax.set_ylim(-0.6, 0.6)

plt.tight_layout()
finish(fig, args.save)
