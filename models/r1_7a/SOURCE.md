# 宇树 R1 七轴机械臂 · 模型文件说明

## 来源

| 项目 | 说明 |
|---|---|
| 来源仓库 | [`unitreerobotics/unitree_ros`](https://github.com/unitreerobotics/unitree_ros) |
| 目录 | `robots/r1_7a_description/` |
| 分支 | `master` |
| 获取方式 | `python tools/fetch_unitree_model.py`（可重复执行，已存在则跳过） |
| 抓取日期 | 2026-10-12 |

## 文件清单

```
models/r1_7a/
├── R1_7a.urdf      # 机械臂描述文件（7 关节 + 底座）
└── meshes/         # 8 个 STL 网格
    ├── base_link.STL
    └── Link1.STL … Link7.STL
```

## 机械臂参数

- 型号：宇树 R1 机械臂（R1-A7）
- 自由度：**7 轴**（J1–J7）
- 关节类型：全部为 `revolute`（旋转关节）
- 底座安装：J1 原点在 base_link 上方 0.069 m

## 开源协议

模型文件来自 Unitree 的 `unitree_ros` 仓库，采用 **BSD 3-Clause License**：

> Copyright (c) 2016-2022 HangZhou YuShu TECHNOLOGY CO.,LTD. ("Unitree Robotics")

允许再分发与修改，须保留版权声明。详见仓库根目录 `NOTICE.md`。

## 说明

- URDF 中 `mesh filename="meshes/xxx.STL"` 为**相对路径**，因此 `R1_7a.urdf` 必须与 `meshes/` 保持同级目录关系。
- 本课程仅将模型用于**教学仿真**；如需商用硬件控制，请遵循宇树官方 SDK 条款（见 [`unitreerobotics/r1-7a_sdk`](https://github.com/unitreerobotics/r1-7a_sdk)）。
