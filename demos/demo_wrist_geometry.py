# -*- coding: utf-8 -*-
"""
腕部几何检查：机械臂到底是不是「球形手腕」？
=============================================
这是本课程 **M9–M11（三维逆解）** 的关键前置实验。

课本里常说："六轴臂的最后三根轴交于一点（球形手腕），
于是位置与姿态可以解耦 —— 位置用球坐标解前三个关节，姿态用欧拉角解腕关节。"

**但真实机型往往不是这样。** 本脚本用量化方法检查两台机型：

* **UR5**（主力）：轴 4 与轴 6 **平行**，相距 94.65 mm → 三轴不共点，**不是**球形腕；
* **宇树 R1**（对照）：三轴几乎交于一点，最大偏差约 5 mm → **近似**球形腕。

结论会直接改变 M9–M11 的教学设计：不能假设解耦，必须让数值 IK 兜底。

运行::

    python demos/demo_wrist_geometry.py
    python demos/demo_wrist_geometry.py --save outputs/wrist_geometry.png
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

from armblocks import UR5_URDF, R1_URDF, load_model, display_name
from armblocks.core.geometry import wrist_report, print_wrist_report
from armblocks.core.kinematics import link_frames

models = [load_model(UR5_URDF), load_model(R1_URDF)]

print("=" * 74)
print("腕部几何检查：最后三根轴的相对位置")
print("=" * 74)
for m in models:
    print_wrist_report(m)

# ---------------------------------------------------------------- 一致性检查
print("=" * 74)
print("检查：轴间距离是「机构固有属性」，与整体位形无关")
print("=" * 74)
for m in models:
    rng = np.random.default_rng(0)
    ref = None
    for _ in range(5):
        q = m.random_q(rng)
        rep = wrist_report(m, q)
        dists = tuple(round(it["distance"], 9) for it in rep["pairs"])
        if ref is None:
            ref = dists
        assert dists == ref, f"{m.name} 轴距随位形变化了？"
    print(f"  {display_name(m):<16} 5 组随机位形下轴距完全一致 ✓  {ref}")

# ---------------------------------------------------------------- 出图
fig = plt.figure(figsize=(14, 6))

for i, m in enumerate(models, start=1):
    ax = fig.add_subplot(1, 2, i, projection="3d")
    r = wrist_report(m)
    T = link_frames(m, m.home())

    # 画整条臂的骨架（淡）
    pts = np.array([t[:3, 3] for t in T])
    ax.plot(*zip(*pts), color="#b7c0cf", lw=3, zorder=1)
    ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], s=14, c="#8892a6", depthshade=False)

    # 画最后三根轴（延伸出来的直线）
    colors = ["#2f5bd7", "#d9822b", "#c0392b"]
    for c, n in zip(colors, r["joints"]):
        p, d = r["points"][n], r["directions"][n]
        L = 0.22
        seg = np.array([p - L * d, p + L * d])
        ax.plot(seg[:, 0], seg[:, 1], seg[:, 2], color=c, lw=2.6, zorder=4)
        ax.scatter(*p, s=70, c=c, depthshade=False, zorder=5,
                   label=f"{n} 轴")

    # 标出"最接近公共点"
    if r["common_point"] is not None:
        cp = r["common_point"]
        ax.scatter(*cp, s=170, marker="*", c="#1a2233", depthshade=False,
                   zorder=6, label=f"最接近公共点\n(偏差 {r['max_offset']*1000:.1f} mm)")

    verdict = ("球形手腕：三轴交于一点" if r["concurrent"]
               else "非球形腕：三轴不共点")
    ax.set_title(f"{display_name(m)}\n{verdict}", fontsize=11)
    ax.set_xlabel("X (m)"); ax.set_ylabel("Y (m)"); ax.set_zlabel("Z (m)")
    allp = np.vstack([pts, np.array(list(r["points"].values()))])
    c = allp.mean(axis=0)
    rad = float(np.abs(allp - c).max()) + 0.1
    ax.set_xlim(c[0] - rad, c[0] + rad)
    ax.set_ylim(c[1] - rad, c[1] + rad)
    ax.set_zlim(c[2] - rad, c[2] + rad)
    ax.legend(fontsize=7, loc="upper left")

plt.tight_layout()
finish(fig, args.save)
