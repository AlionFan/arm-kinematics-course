# -*- coding: utf-8 -*-
"""
双机对照：UR5（主力） vs 宇树 R1（对照）
=========================================
同一个框架、同一套旋转积木，驱动两台结构不同的真实机械臂，并把差异量化出来。

**核心结论**（也是本课程的一条教学主线）：

    换一台机械臂，三角函数并没有换 —— 换的只是"角度怎么串起来"。

输出内容：

* 左：两台臂的零位骨架
* 右：两台臂的可达空间
* 终端：构型 / 轴排布 / 限位 / 工作空间 的逐项对照表

运行::

    python demos/demo_compare_arms.py
    python demos/demo_compare_arms.py --save outputs/compare_arms.png
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

from armblocks import UR5_URDF, R1_URDF, load_model, solutions, blocks, viz, display_name, fk
from armblocks.core.truth import fk_reference
from armblocks.core.geometry import wrist_report

rot = blocks.rotations if args.impl == "blocks" else solutions.rotations


def workspace_radius(model, n=4000, seed=0):
    """随机采样末端点，返回 (最小半径, 最大半径, 点数)。"""
    rng = np.random.default_rng(seed)
    r = np.array([np.linalg.norm(fk_reference(model, model.random_q(rng))[0])
                  for _ in range(n)])
    return float(r.min()), float(r.max())


def axis_letter(joint) -> str:
    """把关节轴向量写成 'z' / '-x' 这样的可读形式。"""
    a = np.asarray(joint.axis, float)
    i = int(np.argmax(np.abs(a)))
    return ("-" if a[i] < 0 else "") + "xyz"[i]


def describe(model):
    """收集一台机器的关键参数，返回 dict。"""
    m = model
    p0, R0 = fk_reference(m, m.home())
    rmin, rmax = workspace_radius(m)
    wr = wrist_report(m)
    return {
        "name": display_name(m),
        "dof": m.dof,
        "fixed": [j.name for j in m.fixed_joints],
        "axes": " ".join(axis_letter(j) for j in m.joints),
        "limits": [f"{np.degrees(j.lower):.0f}~{np.degrees(j.upper):.0f}°" for j in m.joints],
        "joints": m.joint_names,
        "tip": m.tip_link,
        "p0": p0,
        "reach": float(np.linalg.norm(p0)),
        "rmin": rmin,
        "rmax": rmax,
        "wrist_concurrent": wr["concurrent"],
        "wrist_offset": wr["max_offset"],
        "wrist_par": [it["pair"] for it in wr["pairs"] if it["parallel"]],
    }


ur5 = load_model(UR5_URDF)
r1 = load_model(R1_URDF)
A, B = describe(ur5), describe(r1)


def wrist_str(d):
    if d["wrist_concurrent"]:
        return "球形腕（三轴交于一点）"
    if d["wrist_par"]:
        return f"非球形（含平行轴，偏差 {d['wrist_offset']*1000:.1f}mm）"
    return f"近似球形（偏差 {d['wrist_offset']*1000:.1f}mm）"


# ------------------------------------------------------------------ 终端对照
print("=" * 78)
print(f"{'':<14}{'UR5（主力）':<30}{'宇树 R1（对照）':<30}")
print("=" * 78)
rows = [
    ("自由度", f"{A['dof']} 轴", f"{B['dof']} 轴"),
    ("关节轴排布", A["axes"], B["axes"]),
    ("固定节", f"{len(A['fixed'])} 个", f"{len(B['fixed'])} 个"),
    ("末端参考系", A["tip"], B["tip"]),
    ("零位末端位置(m)", np.array2string(A["p0"], precision=3), np.array2string(B["p0"], precision=3)),
    ("零位末端距底座", f"{A['reach']:.3f} m", f"{B['reach']:.3f} m"),
    ("可达半径范围", f"{A['rmin']:.3f} – {A['rmax']:.3f} m", f"{B['rmin']:.3f} – {B['rmax']:.3f} m"),
    ("腕部结构", wrist_str(A), wrist_str(B)),
    ("位置/姿态解耦", "不成立", "近似成立"),
    ("冗余度", "无（6 轴 = 6 自由度）", "有（7 轴 > 6，无穷多解）"),
    ("IK 策略", "可解析（含腕部耦合修正）", "数值解 + 选解准则"),
]
for row in rows:
    label, u, r = row
    print(f"{label:<14}{u:<30}{r:<30}")
print("=" * 78)

print("\n各关节限位：")
print(f"  {'UR5':<34}{'宇树 R1':<34}")
for i in range(max(A["dof"], B["dof"])):
    lu = f"{A['joints'][i] + ' ' + A['limits'][i]:<34}" if i < A["dof"] else " " * 34
    lr = f"{B['joints'][i] + ' ' + B['limits'][i]:<34}" if i < B["dof"] else ""
    print(f"  {lu}{lr}")

print("\n[相同点]")
print("  · 都是串联臂：末端位姿 = 各关节变换依次相乘")
print("  · 都是 6 个有效位姿自由度，姿态都靠最后 3 个关节")
print("  · 关节变换都只需要 sin / cos —— 三角函数是它们的共同语")
print("  · 都用同一套代码、同一份旋转积木驱动（本框架已验证）")
print("\n[不同点]")
print("  · 轴排布：UR5 六轴全绕 z（α 角藏在原点 rpy 里），R1 是 z/x/y 混合")
print("  · 腕部几何：UR5 轴 4 ∥ 轴 6、相距 94.65 mm，位置/姿态无法解耦；")
print("              R1 三轴几乎交于一点（偏差约 5 mm），近似球形")
print("  · 自由度：UR5 恰好 6（解有限，最多 8 组）；R1 有 7 轴，冗余 → 无穷多解")
print("  · IK：UR5 可解析求解；R1 需数值解 + 选解准则（离限位最远 / 离当前位形最近）")
print("\n[教学含义]")
print("  · 平面 2R、旋转矩阵、欧拉角这些「积木」两台机器都要用 → 先练通用子问题")
print("  · 真实机型往往「不完美」（UR5 就不是球形腕）→ 必须用数值 IK 做对照")
print("  · 换机器 = 换「角度怎么串」，不换三角函数")

# ------------------------------------------------------------------ 出图
fig = plt.figure(figsize=(13, 10))
ax = fig.add_subplot(2, 2, 1, projection="3d")
p, _ = fk(ur5, ur5.home(), rot=rot)
viz.plot_arm(ur5, ur5.home(), rot=rot, ax=ax,
             title=f"{display_name(ur5)} 零位（6 轴，全绕 z）")

ax = fig.add_subplot(2, 2, 2, projection="3d")
q_r1 = r1.home()
p, _ = fk(r1, q_r1, rot=rot)
viz.plot_arm(r1, q_r1, rot=rot, ax=ax,
             title=f"{display_name(r1)} 零位（7 轴，z/x/y 混合）")

ax = fig.add_subplot(2, 2, 3, projection="3d")
viz.plot_workspace(ur5, n=3000, rot=rot, ax=ax)

ax = fig.add_subplot(2, 2, 4, projection="3d")
viz.plot_workspace(r1, n=3000, rot=rot, ax=ax)

plt.tight_layout()
finish(fig, args.save)
