# -*- coding: utf-8 -*-
"""
UR5 机械臂演示（主力机型）：正运动学 · 平面 2R 结构 · 腕部几何
==============================================================
UR5 是本课程的**主力机型**：6 自由度、标准 DH、6 个关节全部绕自身 z 轴，
因此"三角函数 → 机械臂"的映射最干净。

本演示用**你自己的旋转积木**驱动真实 UR5 模型，依次看四件事：

1. **零位**：全 0 时机械臂伸向哪里；
2. **平面 2R 结构**：只动 ``shoulder_lift`` + ``elbow``，末端被"锁"在一个竖直平面内
   —— 这就是 M3/M4 那个平面 2R 臂在真实机械臂上的样子；
3. **腕部几何（重要！）**：UR5 的**三根腕轴并不交于一点**，轴 4 与轴 6 平行、
   相距 94.65 mm。所以"末端位置只由前三个关节决定"这句话在 UR5 上**不成立**。
   本演示用数据把它量出来；
4. **可达空间**：随机姿态打点，看 UR5 的工作空间形状。

运行::

    python demos/demo_ur5_arm.py                      # 用参考答案（默认）
    python demos/demo_ur5_arm.py --impl blocks        # 用你写的积木
    python demos/demo_ur5_arm.py --save outputs/ur5_arm.png
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

from armblocks import UR5_URDF, load_model, solutions, blocks, viz, fk, display_name
from armblocks.core.geometry import print_wrist_report

rot = blocks.rotations if args.impl == "blocks" else solutions.rotations
model = load_model(UR5_URDF)
print(f"模型：{display_name(model)}  自由度={model.dof}")
print(f"关节：{model.joint_names}")
print(f"固定节（不占自由度，但贡献位姿）：{[j.name for j in model.fixed_joints]}")
print()

JN = {n: i for i, n in enumerate(model.joint_names)}


def set_q(**kv):
    """按关节名设置角度（度）。"""
    q = np.zeros(model.dof)
    for name, deg in kv.items():
        q[JN[name]] = np.radians(deg)
    return q


fig = plt.figure(figsize=(16, 5.4))
panels = [
    ("① 零位 q = 0", model.home()),
    ("② 平面 2R：只动肩俯仰 + 肘",
     set_q(shoulder_lift_joint=-45, elbow_joint=-70)),
    ("③ 腕部转动：末端位置会变（非球形腕）",
     set_q(shoulder_lift_joint=-60, elbow_joint=-90, wrist_1_joint=35,
           wrist_2_joint=55, wrist_3_joint=-25)),
]

for i, (title, q) in enumerate(panels, start=1):
    ax = fig.add_subplot(1, 4, i, projection="3d")
    p, R = fk(model, q, rot=rot)
    viz.plot_arm(model, q, rot=rot, ax=ax,
                 title=f"{title}\n末端=({p[0]:.2f}, {p[1]:.2f}, {p[2]:.2f}) m")
    print(f"{title}  末端位置 = {np.round(p, 4)}")

# ---- 腕部几何：量化"是不是球形手腕" ----
print()
print_wrist_report(model)
p_home = fk(model, model.home(), rot=rot)[0]
print("[逐个腕关节测试：末端 tool0 会不会动]")
for nm in ("wrist_1_joint", "wrist_2_joint", "wrist_3_joint"):
    q = set_q(**{nm: 90})
    d = np.linalg.norm(fk(model, q, rot=rot)[0] - p_home)
    why = "（tool0 正好在这根轴上）" if d < 1e-9 else ""
    print(f"  只动 {nm:<18} 90°  →  末端移动 {d * 1000:8.2f} mm {why}")
print("  结论：只有 wrist_3 不动（tool0 在轴 6 上），轴 4 / 5 都会带动末端 —— "
      "所以 UR5 **不能**把位置与姿态解耦。")

# ---- 可达空间 ----
ax = fig.add_subplot(1, 4, 4, projection="3d")
viz.plot_workspace(model, n=2500, rot=rot, ax=ax)

plt.tight_layout()
finish(fig, args.save)
