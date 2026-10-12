# UR5 机械臂 · 模型文件说明

> 本课程**主力机型**。6 自由度、标准 DH 构型、全关节绕自身 z 轴 —— 三角函数推导最"干净"的一台工业臂。

## 来源

| 项目 | 说明 |
|---|---|
| 上游仓库 | [`ros-industrial/universal_robot`](https://github.com/ros-industrial/universal_robot) |
| 目录 | `ur_description/` |
| 分支 | `noetic-devel` |
| 获取方式 | `python tools/fetch_ur5_model.py`（可重复执行，已存在则跳过） |
| 抓取日期 | 2026-10-12 |
| 下载镜像 | `fastly.jsdelivr.net` / `jsdelivr.b-cdn.net`（GitHub API 匿名限速 60 次/时，`raw.githubusercontent` 在部分网络不可达） |

## 文件清单

```
models/ur5/
├── ur5.urdf                 # ★ 教学用纯 URDF（已展开 xacro，不依赖 ROS）
├── config/                  # 官方参数原件（ur5.urdf 的数值全部来自这里）
│   ├── default_kinematics.yaml     # 关节原点 xyz/rpy（官方标定）
│   ├── joint_limits.yaml           # 关节限位/力矩/速度
│   ├── physical_parameters.yaml    # 质量、质心、惯量张量
│   └── visual_parameters.yaml      # 网格路径与材质
├── meshes/
│   ├── visual/              # 7 个 .dae（高精度外观，PyBullet/MuJoCo 渲染用）
│   └── collision/           # 7 个 .stl（简化碰撞体）
└── LICENSE                  # 上游 BSD-3-Clause 原文
```

## 关于 `ur5.urdf` 是怎么来的

上游**只提供 xacro**（`ur5.xacro` → `inc/ur5_macro.xacro` → `inc/ur_macro.xacro`），
需要 ROS 才能展开。为了让课程"开箱即用、不装 ROS"，本仓库改为：

1. 从上游下载 4 份参数 yaml（存档在 `config/`）；
2. 用 `tools/fetch_ur5_model.py` 的 `build_urdf()` 按官方数值生成**扁平 URDF**。

与上游 xacro 的等价性：

| 项 | 处理 |
|---|---|
| `${prefix}` | 置空 |
| 网格路径 | `package://ur_description/meshes/...` → 相对路径 `meshes/...` |
| `transmission` / `ros2_control` / `safety_controller` | 删除（教学不需要） |
| 关节原点、限位、质量、惯量 | **原样保留**（数值与官方 yaml 完全一致） |
| `base_link` / `base` / `flange` / `tool0` 固定帧 | 保留 |

## 结构

6 个可动关节，**全部 `axis = 0 0 1`**，靠关节原点的 `rpy` 实现轴向偏置（标准 DH 的 `α`）

```
base_link ─(fixed, rpy 0 0 π)─ base_link_inertia
   └─ shoulder_pan_joint    xyz(0, 0, 0.089159)      rpy(0,0,0)
      └─ shoulder_lift_joint  xyz(0, 0, 0)             rpy(π/2, 0, 0)
         └─ elbow_joint         xyz(−0.425, 0, 0)          rpy(0,0,0)
            └─ wrist_1_joint      xyz(−0.39225, 0, 0.10915)  rpy(0,0,0)
               └─ wrist_2_joint     xyz(0, −0.09465, 0)        rpy(π/2, 0, 0)
                  └─ wrist_3_joint  xyz(0, 0.0823, 0)           rpy(π/2, π, π)
                     └─ wrist_3_link ─(fixed)─ flange ─(fixed)─ tool0
```

## 机械臂参数

| 项目 | 数值 |
|---|---|
| 型号 | UR5（Universal Robots） |
| 自由度 | **6** |
| 关节类型 | 全部 `revolute` |
| 关节限位 | 肩回转/肩俯仰/腕 1–3：**±360°**；肘：**±180°** |
| 额定负载 | 5 kg |
| 自重 | 18.4 kg |
| 工作半径 | 850 mm |
| 大臂长度 a₂ | 0.425 m |
| 小臂长度 a₃ | 0.39225 m |
| 腕部三轴 | **交于一点** → 球形手腕，位置与姿态可解耦 |

> 关键尺寸：d₁ = 0.089159 m（底座到肩关节）、d₄ = 0.10915 m、d₅ = 0.09465 m、d₆ = 0.0823 m。

## 开源协议

上游 `ur_description/LICENSE` 为 **BSD 3-Clause License**，允许再分发与修改，须保留版权声明。
原文已存档为 `models/ur5/LICENSE`，详见仓库根目录 `NOTICE.md`。

## 说明

- URDF 中 `mesh filename="meshes/..."` 为**相对路径**，`ur5.urdf` 必须与 `meshes/` 保持同级目录关系。
- 本课程仅将模型用于**教学仿真**；UR5 为 Universal Robots A/S 的商标与产品，
  如需驱动真机请遵循官方条款（[Universal Robots 官网](https://www.universal-robots.com/)）。
