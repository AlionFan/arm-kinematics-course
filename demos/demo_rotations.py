# -*- coding: utf-8 -*-
"""
M7 演示：旋转矩阵到底在做什么？
=================================
把「原坐标轴」用三个旋转矩阵分别转一下，看看它们去了哪 ——
你会发现矩阵的每一列，就是坐标轴旋转后的新坐标。

运行::

    python demos/demo_rotations.py --impl blocks
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

R = blocks if args.impl == "blocks" else solutions

cases = [
    ("绕 z 轴转 90°", R.rotations.rot_z(np.pi / 2)),
    ("绕 y 轴转 90°", R.rotations.rot_y(np.pi / 2)),
    ("绕 x 轴转 90°", R.rotations.rot_x(np.pi / 2)),
    ("绕 z 轴转 40°", R.rotations.rot_z(np.radians(40))),
]

fig = plt.figure(figsize=(15, 4.4))
for i, (title, M) in enumerate(cases, start=1):
    ax = fig.add_subplot(1, 4, i, projection="3d")
    for k, (col, lab) in enumerate(zip(("r", "g", "b"), ("x", "y", "z"))):
        v0 = np.eye(3)[k]
        v1 = M @ v0
        ax.quiver(0, 0, 0, *v0, color=col, alpha=0.28, arrow_length_ratio=0.15, lw=1.5)
        ax.quiver(0, 0, 0, *v1, color=col, lw=2.6, arrow_length_ratio=0.18)
        ax.text(*(v1 * 1.12), lab + "'", color=col, fontsize=11, ha="center")
    ax.set_title(title, fontsize=11)
    ax.set_xlim(-1.2, 1.2); ax.set_ylim(-1.2, 1.2); ax.set_zlim(-1.2, 1.2)
    ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("z")
    ax.set_box_aspect((1, 1, 1))

plt.tight_layout()
finish(fig, args.save)
