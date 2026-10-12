#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_ur5_model.py
==================
拉取 UR5 机械臂官方描述包（URDF 参数 + 网格），生成课程用的**扁平 URDF**。

上游：``ros-industrial/universal_robot`` → ``ur_description``（分支 ``noetic-devel``）

注意：上游只提供 **xacro**（需要 ROS 环境展开）。本脚本改为：
1. 下载官方 4 份参数 yaml（ kinematics / joint_limits / physical_parameters /
   visual_parameters ）与 LICENSE，原样存档在 ``models/ur5/config/``；
2. 下载 visual(.dae) 与 collision(.stl) 网格；
3. 按官方参数**生成一份不依赖 ROS 的纯 URDF** ``models/ur5/ur5.urdf``，
   数值全部取自上面那 4 份 yaml，可直接被本课程的 ``armblocks`` 解析。

下载走 ``fastly.jsdelivr.net`` CDN 镜像（GitHub API 匿名限速 60 次/小时，
raw.githubusercontent 在部分网络下不可达）。

用法::

    python tools/fetch_ur5_model.py             # 缺什么下什么
    python tools/fetch_ur5_model.py --force     # 全部重下
"""
from __future__ import annotations

import argparse
import os
import sys
import urllib.error
import urllib.request

REPO = "ros-industrial/universal_robot"
BRANCH = "noetic-devel"
CDN_HOSTS = [
    # jsDelivr 的多个边缘节点。注意：任一副本对「仓库总体积 > 50MB」的包会返回 403，
    # 因此必须逐个 host 回退（实测 fastly 对个别文件 403、b-cdn 可以）。
    "https://fastly.jsdelivr.net",
    "https://jsdelivr.b-cdn.net",
    "https://gcore.jsdelivr.net",
    "https://cdn.jsdelivr.net",
]
SUB = "ur_description"
CDN = f"{CDN_HOSTS[0]}/gh/{REPO}@{BRANCH}/{SUB}"
DST_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "ur5"
)

PI = 3.141592653589793
TAU = 2 * PI

# --------------------------------------------------------------------------- #
# 下载清单
# --------------------------------------------------------------------------- #
CONFIG_FILES = [
    "config/ur5/default_kinematics.yaml",
    "config/ur5/joint_limits.yaml",
    "config/ur5/physical_parameters.yaml",
    "config/ur5/visual_parameters.yaml",
]

MESH_NAMES = ["base", "shoulder", "upperarm", "forearm", "wrist1", "wrist2", "wrist3"]
MESH_FILES = (
    [f"meshes/ur5/visual/{n}.dae" for n in MESH_NAMES]
    + [f"meshes/ur5/collision/{n}.stl" for n in MESH_NAMES]
)


# --------------------------------------------------------------------------- #
# UR5 纯 URDF（数值来自官方 4 份 yaml，见上方注释）
# --------------------------------------------------------------------------- #
URDF_HEADER = """<?xml version="1.0" encoding="utf-8"?>
<!--
  UR5 机械臂 · 教学用纯 URDF（不依赖 ROS / xacro）
  =================================================
  本文件由 tools/fetch_ur5_model.py 依据 Universal Robots 官方描述包自动生成。

  上游：https://github.com/ros-industrial/universal_robot  (ur_description, noetic-devel)
  参数来源：ur_description/config/ur5/{default_kinematics, joint_limits,
            physical_parameters, visual_parameters}.yaml  —— 已存档于 ./config/

  结构（6 个可动关节，全部绕自身 z 轴转）：
      base_link ─(fixed)─ base_link_inertia ─ shoulder_pan ─ shoulder_link
        └─ shoulder_lift ─ upper_arm_link ─ elbow ─ forearm_link
        └─ wrist_1 ─ wrist_1_link ─ wrist_2 ─ wrist_2_link ─ wrist_3 ─ wrist_3_link
        └─(fixed)─ flange ─(fixed)─ tool0

  与上游 xacro 的差异：把 ${prefix} 置空；网格路径由 package:// 改为相对路径
  ./meshes/...；去掉 transmission / ros2_control / safety_controller（教学不需要）。
-->
<robot name="ur5">
"""


def _visual(link_mesh: str, xyz: str, rpy: str, color: str = "0.7 0.7 0.7 1.0") -> str:
    return f"""    <visual>
      <origin xyz="{xyz}" rpy="{rpy}"/>
      <geometry>
        <mesh filename="meshes/visual/{link_mesh}.dae"/>
      </geometry>
      <material name="LightGrey">
        <color rgba="{color}"/>
      </material>
    </visual>
    <collision>
      <origin xyz="{xyz}" rpy="{rpy}"/>
      <geometry>
        <mesh filename="meshes/collision/{link_mesh}.stl"/>
      </geometry>
    </collision>
"""


def _inertial(mass: float, xyz: str, rpy: str, ixx: float, iyy: float, izz: float) -> str:
    return f"""    <inertial>
      <mass value="{mass}"/>
      <origin xyz="{xyz}" rpy="{rpy}"/>
      <inertia ixx="{ixx}" ixy="0" ixz="0" iyy="{iyy}" iyz="0" izz="{izz}"/>
    </inertial>
"""


def build_urdf() -> str:
    """生成 UR5 纯 URDF 正文。"""
    out = [URDF_HEADER]

    # ---- links ---------------------------------------------------------- #
    out.append("""  <!-- ================= links ================= -->
  <link name="base_link"/>

  <link name="base_link_inertia">
""")
    out.append(_visual("base", "0 0 0", f"0 0 {PI}"))
    out.append(_inertial(4.0, "0 0 0", "0 0 0", 0.00443333156, 0.00443333156, 0.0072))
    out.append("  </link>\n")

    # shoulder_link：视觉原点 rpy 0 0 pi（与上游一致）
    out.append('  <link name="shoulder_link">\n')
    out.append(_visual("shoulder", "0 0 0", f"0 0 {PI}"))
    out.append(_inertial(3.7, "0 -0.00193 -0.02561", "0 0 0",
                         0.014972358333333331, 0.014972358333333331, 0.01040625))
    out.append("  </link>\n")

    # upper_arm_link：肩偏置 0.13585，视觉原点 rpy pi/2 0 -pi/2
    out.append('  <link name="upper_arm_link">\n')
    out.append(_visual("upperarm", "0 0 0.13585", f"{PI / 2} 0 {-PI / 2}"))
    out.append(_inertial(8.393, "-0.2125 0 0.11336", f"0 {PI / 2} 0",
                         0.13388583541666665, 0.13388583541666665, 0.0151074))
    out.append("  </link>\n")

    # forearm_link：肘偏置 0.0165
    out.append('  <link name="forearm_link">\n')
    out.append(_visual("forearm", "0 0 0.0165", f"{PI / 2} 0 {-PI / 2}"))
    out.append(_inertial(2.33, "-0.24225 0 0.0265", f"0 {PI / 2} 0",
                         0.031216803515624995, 0.031216803515624995, 0.004095))
    out.append("  </link>\n")

    out.append('  <link name="wrist_1_link">\n')
    out.append(_visual("wrist1", "0 0 -0.093", f"{PI / 2} 0 0"))
    out.append(_inertial(1.219, "0 -0.01634 -0.0018", "0 0 0",
                         0.002013889583333333, 0.002013889583333333, 0.0021942))
    out.append("  </link>\n")

    out.append('  <link name="wrist_2_link">\n')
    out.append(_visual("wrist2", "0 0 -0.095", "0 0 0"))
    out.append(_inertial(1.219, "0 0.01634 -0.0018", "0 0 0",
                         0.0018310395833333333, 0.0018310395833333333, 0.0021942))
    out.append("  </link>\n")

    out.append('  <link name="wrist_3_link">\n')
    out.append(_visual("wrist3", "0 0 -0.0818", f"{PI / 2} 0 0"))
    out.append(_inertial(0.1879, "0 0 -0.001159", "0 0 0",
                         8.062475833333332e-05, 8.062475833333332e-05, 0.0001321171875))
    out.append("  </link>\n")

    out.append("""  <link name="flange"/>
  <link name="tool0"/>

  <!-- ================= joints ================= -->
  <!-- 固定帧：REP-103 的 base_link(X+ 前) 与 UR 控制器 Base 坐标系相差绕 Z 的 pi -->
  <joint name="base_link-base_link_inertia" type="fixed">
    <parent link="base_link"/>
    <child link="base_link_inertia"/>
    <origin xyz="0 0 0" rpy="0 0 {pi}"/>
  </joint>
""".format(pi=PI))

    # 6 个可动关节：xyz / rpy 来自 config/ur5/default_kinematics.yaml
    movable = [
        # name, parent, child, xyz, rpy, lower, upper, effort, velocity, 中文说明
        ("shoulder_pan_joint", "base_link_inertia", "shoulder_link",
         "0 0 0.089159", "0 0 0", -TAU, TAU, 150.0,
         "肩部回转：整条臂绕底座竖直轴转（底座方位角）"),
        ("shoulder_lift_joint", "shoulder_link", "upper_arm_link",
         "0 0 0", f"{PI / 2} 0 0", -TAU, TAU, 150.0,
         "肩部俯仰：大臂抬起/放下（平面 2R 的『第一根杆』）"),
        ("elbow_joint", "upper_arm_link", "forearm_link",
         "-0.425 0 0", "0 0 0", -PI, PI, 150.0,
         "肘部：小臂弯曲（平面 2R 的『第二根杆』）"),
        ("wrist_1_joint", "forearm_link", "wrist_1_link",
         "-0.39225 0 0.10915", "0 0 0", -TAU, TAU, 28.0,
         "腕 1：绕小臂轴线转（前臂滚转）"),
        ("wrist_2_joint", "wrist_1_link", "wrist_2_link",
         "0 -0.09465 0", f"{PI / 2} 0 0", -TAU, TAU, 28.0,
         "腕 2：手腕俯仰"),
        ("wrist_3_joint", "wrist_2_link", "wrist_3_link",
         "0 0.0823 0",
         f"{1.570796326589793} {PI} {PI}", -TAU, TAU, 28.0,
         "腕 3：末端自转（三个腕关节轴交于一点 → 球形手腕）"),
    ]
    for name, parent, child, xyz, rpy, lo, hi, eff, note in movable:
        out.append(f"""  <!-- {note} -->
  <joint name="{name}" type="revolute">
    <parent link="{parent}"/>
    <child link="{child}"/>
    <origin xyz="{xyz}" rpy="{rpy}"/>
    <axis xyz="0 0 1"/>
    <limit lower="{lo}" upper="{hi}" effort="{eff}" velocity="{PI}"/>
    <dynamics damping="0" friction="0"/>
  </joint>
""")

    out.append(f"""  <!-- 法兰面（末端执行器安装基准） -->
  <joint name="wrist_3-flange" type="fixed">
    <parent link="wrist_3_link"/>
    <child link="flange"/>
    <origin xyz="0 0 0" rpy="0 {-PI / 2} {-PI / 2}"/>
  </joint>

  <!-- tool0：全零工具坐标系（X+ 左、Y+ 上、Z+ 前） -->
  <joint name="flange-tool0" type="fixed">
    <parent link="flange"/>
    <child link="tool0"/>
    <origin xyz="0 0 0" rpy="{PI / 2} 0 {PI / 2}"/>
  </joint>
</robot>
""")
    return "".join(out)


# --------------------------------------------------------------------------- #
def _download(rel: str, dst: str, force: bool) -> None:
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst) and os.path.getsize(dst) > 1024 and not force:
        print(f"    = 跳过（已存在）{rel}")
        return
    last = ""
    for host in CDN_HOSTS:
        url = f"{host}/gh/{REPO}@{BRANCH}/{SUB}/{rel}"
        req = urllib.request.Request(url, headers={"User-Agent": "ur5-model-fetcher"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read()
        except Exception as e:                       # noqa: BLE001
            last = f"{type(e).__name__}: {e}"
            continue
        if len(raw) < 1024:                          # CDN 的错误页
            last = raw[:80].decode("utf-8", "replace")
            continue
        with open(dst, "wb") as f:
            f.write(raw)
        print(f"    + {rel}  ({len(raw):,} bytes)  [{host.split('//')[1]}]")
        return
    print(f"    ! {rel} 全部镜像失败：{last}")


def main() -> int:
    ap = argparse.ArgumentParser(description="拉取 UR5 模型并生成纯 URDF")
    ap.add_argument("--force", action="store_true", help="已存在也重新下载")
    args = ap.parse_args()

    print(f"[*] 目标目录：{DST_DIR}")
    print(f"[*] 镜像：{', '.join(h.split('//')[1] for h in CDN_HOSTS)}")

    print("\n[1/4] 官方参数文件 …")
    for rel in CONFIG_FILES:
        _download(rel, os.path.join(DST_DIR, "config", os.path.basename(rel)), args.force)

    print("\n[2/4] 网格文件（visual .dae + collision .stl）…")
    for rel in MESH_FILES:
        dst = os.path.join(DST_DIR, rel.replace("meshes/ur5/", "meshes/"))
        _download(rel, dst, args.force)

    print("\n[3/4] 生成纯 URDF …")
    urdf_path = os.path.join(DST_DIR, "ur5.urdf")
    with open(urdf_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(build_urdf())
    print(f"    + ur5.urdf  ({os.path.getsize(urdf_path):,} bytes)")

    print("\n[4/4] 上游 LICENSE（BSD-3-Clause）…")
    _download("LICENSE", os.path.join(DST_DIR, "LICENSE"), args.force)

    print(f"\n[√] 完成，模型位于：{DST_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
