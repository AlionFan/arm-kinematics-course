# -*- coding: utf-8 -*-
"""
UR5 逆运动学演示（主力机型）：把末端送到指定位置与姿态
========================================================
随机生成一个**保证可达**的目标 → 用数值 IK 求关节角 → 画出求解结果。

UR5 有解析解，但课堂上让学生推的是**两个几何子问题**：

* 位置：把 ``wrist_1_link`` 的原点（= 腕心，三个腕轴的交点）当作"手"，用
  **球坐标 + 余弦定理** 解前三个关节；
* 姿态：腕心定住后，用**欧拉角** 解后三个腕关节。

本演示给出数值解作为对照，方便学生检验自己的推导。

运行::

    python demos/demo_ur5_ik.py
    python demos/demo_ur5_ik.py --save outputs/ur5_ik.png
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

from armblocks import UR5_URDF, load_model, solutions, blocks, viz, display_name
from armblocks import fk, ik
from armblocks.core.kinematics import reachable_pair
from armblocks.core.truth import fk_reference

rot = blocks.rotations if args.impl == "blocks" else solutions.rotations
model = load_model(UR5_URDF)
print(f"模型：{display_name(model)}  自由度={model.dof}\n")

fig = plt.figure(figsize=(15, 5.4))
for i in range(3):
    rng = np.random.default_rng(10 + i)
    (p_t, R_t), q_true = reachable_pair(model, rng)
    q_sol = ik(model, p_t, R_t, restarts=8, rng=rng)
    p_sol, R_sol = fk_reference(model, q_sol)

    err_p = np.linalg.norm(p_sol - p_t)
    err_o = np.linalg.norm(R_sol - R_t)
    print(f"目标 {i + 1}: 位置误差 = {err_p:.2e} m ({err_p * 1000:.3f} mm), "
          f"姿态误差 = {err_o:.2e}")

    ax = fig.add_subplot(1, 3, i + 1, projection="3d")
    viz.plot_arm(model, q_sol, rot=rot, ax=ax,
                 title=f"目标 {i + 1}\n误差 {err_p * 1000:.3f} mm")
    ax.scatter(*p_t, s=140, marker="*", c="#c0392b", depthshade=False,
               label="目标点", zorder=6)
    ax.legend(fontsize=8, loc="upper right")

print("\n提示：UR5 的 tool0 恰好落在三个腕轴的交点上，所以『末端位置』"
      "本质就是『腕心位置』——这正是位置/姿态能解耦的原因。")
plt.tight_layout()
finish(fig, args.save)
