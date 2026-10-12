# -*- coding: utf-8 -*-
"""
R1 逆运动学演示：让它把末端送到指定位置
=========================================
随机生成一个**保证可达**的目标 → 用数值 IK 求关节角 → 画出求解结果。

运行::

    python demos/demo_r1_ik.py
    python demos/demo_r1_ik.py --save outputs/r1_ik.png
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

from armblocks import DEFAULT_URDF, load_model, solutions, blocks, viz
from armblocks import fk, ik
from armblocks.core.kinematics import reachable_pair
from armblocks.core.truth import fk_reference

rot = blocks.rotations if args.impl == "blocks" else solutions.rotations
model = load_model(DEFAULT_URDF)

fig = plt.figure(figsize=(15, 5.2))
for i in range(3):
    rng = np.random.default_rng(10 + i)
    (p_t, R_t), q_true = reachable_pair(model, rng)
    q_sol = ik(model, p_t, R_t, restarts=8, rng=rng)
    p_sol, R_sol = fk_reference(model, q_sol)

    err_p = np.linalg.norm(p_sol - p_t)
    err_o = np.linalg.norm(R_sol - R_t)
    print(f"目标 {i+1}: 位置误差={err_p:.2e} m, 姿态误差={err_o:.2e}")

    ax = fig.add_subplot(1, 3, i + 1, projection="3d")
    viz.plot_arm(model, q_sol, rot=rot, ax=ax,
                 title=f"目标 {i+1}\n误差 {err_p*1000:.1f} mm")
    ax.scatter(*p_t, s=140, marker="*", c="#c0392b", depthshade=False,
               label="目标点", zorder=6)
    ax.legend(fontsize=8, loc="upper right")

plt.tight_layout()
finish(fig, args.save)
