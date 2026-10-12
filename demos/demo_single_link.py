# -*- coding: utf-8 -*-
"""
M2 演示：一根连杆转起来，末端画出什么？
=======================================
运行::

    python demos/demo_single_link.py                # 弹窗
    python demos/demo_single_link.py --save out.png # 存图
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

from armblocks import solutions

L = 0.3                                   # 连杆长度 0.3 m
theta = np.linspace(0, 2 * np.pi, 361)
xs, ys = zip(*(solutions.trig.polar_to_xy(L, t) for t in theta))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.6))

# 左：某个角度的连杆
for t, c in [(np.radians(30), "#2f5bd7"), (np.radians(140), "#0f9d8f")]:
    x, y = solutions.trig.polar_to_xy(L, t)
    ax1.plot([0, x], [0, y], "-o", lw=3, color=c)
    ax1.annotate(f"θ={np.degrees(t):.0f}°\n({x:.2f}, {y:.2f})", (x, y),
                 textcoords="offset points", xytext=(8, 6), fontsize=9, color=c)
ax1.set_title("一根连杆：角度 → 坐标", fontsize=11)
ax1.set_xlabel("x (m)"); ax1.set_ylabel("y (m)")

# 右：转一整圈的轨迹
ax2.plot(xs, ys, "-", color="#2f5bd7", lw=1.5)
ax2.set_title("转一整圈：末端轨迹是「圆」", fontsize=11)
ax2.set_xlabel("x (m)"); ax2.set_ylabel("y (m)")

for ax in (ax1, ax2):
    ax.set_aspect("equal"); ax.grid(alpha=0.3)
    ax.set_xlim(-0.36, 0.36); ax.set_ylim(-0.36, 0.36)

plt.tight_layout()
finish(fig, args.save)
