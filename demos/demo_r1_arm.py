# -*- coding: utf-8 -*-
"""
宇树 R1 七轴机械臂演示（对照机型）：正运动学 & 可达空间
=========================================================
用**你自己的旋转积木**驱动真实的 R1 模型，并与主力机型 UR5 对照。

运行::

    python demos/demo_r1_arm.py                      # 用参考答案（默认）
    python demos/demo_r1_arm.py --impl blocks        # 用你写的积木
    python demos/demo_r1_arm.py --save outputs/r1.png
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

from armblocks import R1_URDF, load_model, solutions, blocks, viz, fk

rot = blocks.rotations if args.impl == "blocks" else solutions.rotations
model = load_model(R1_URDF)
print(f"模型：{model.name}  自由度={model.dof}  关节={model.joint_names}")

fig = plt.figure(figsize=(15, 5.2))

# ---- 三种姿态 ----
poses = [
    ("零位 q=0", model.home()),
    ("肩肘抬起", np.array([0.0, 1.0, 0.2, -1.4, 0.5, 0.2, 0.0])),
    ("随机位形", model.random_q(np.random.default_rng(5))),
]
for i, (title, q) in enumerate(poses, start=1):
    ax = fig.add_subplot(1, 4, i, projection="3d")
    p, R = fk(model, q, rot=rot)
    viz.plot_arm(model, q, rot=rot, ax=ax, title=f"{title}\n末端=({p[0]:.2f},{p[1]:.2f},{p[2]:.2f})")
    print(f"{title:8s} 末端位置 = {np.round(p, 3)}")

# ---- 可达空间 ----
ax = fig.add_subplot(1, 4, 4, projection="3d")
viz.plot_workspace(model, n=2500, rot=rot, ax=ax)

plt.tight_layout()
finish(fig, args.save)
