# 第三方资产声明 (NOTICE)

本仓库包含来源于**第三方**的模型文件，其版权归原作者所有，使用须遵循原协议。

## 1. UR5 机械臂模型 `models/ur5/`（主力机型）

| 项目 | 内容 |
|---|---|
| 来源 | https://github.com/ros-industrial/universal_robot |
| 路径 | `ur_description/`（分支 `noetic-devel`）—— 参数取自 `config/ur5/*.yaml`，网格取自 `meshes/ur5/{visual,collision}/` |
| 版权 | Copyright (c) 2008-2015, Universal Robots A/S 及 ROS-Industrial 贡献者 |
| 协议 | **BSD 3-Clause License**（原文存档于 `models/ur5/LICENSE`） |
| 获取方式 | `python tools/fetch_ur5_model.py`（走 jsDelivr CDN 镜像） |
| 本地生成 | `models/ur5/ur5.urdf` 由上述官方参数**展开生成**（上游只提供 xacro），数值与官方一致 |

BSD 3-Clause 允许以源代码或二进制形式再分发与修改，条件是：

1. 保留上述版权声明、条件列表与免责声明；
2. 不得使用版权持有者或贡献者的名义为衍生产品背书。

## 2. 宇树 R1 机械臂模型 `models/r1_7a/`（对照机型）

| 项目 | 内容 |
|---|---|
| 来源 | https://github.com/unitreerobotics/unitree_ros |
| 路径 | `robots/r1_7a_description/`（`R1_7a.urdf` 与 `meshes/*.STL`，共 9 个文件） |
| 版权 | Copyright (c) 2016-2022 HangZhou YuShu TECHNOLOGY CO.,LTD. ("Unitree Robotics") |
| 协议 | **BSD 3-Clause License** |
| 获取方式 | `python tools/fetch_unitree_model.py` |

BSD 3-Clause 允许以源代码或二进制形式再分发与修改，条件是：

1. 保留上述版权声明、条件列表与免责声明；
2. 不得使用版权持有者或贡献者的名义为衍生产品背书。

完整协议文本见原仓库 `LICENSE` 文件。

## 3. 本仓库自有内容

| 内容 | 路径 | 协议 |
|---|---|---|
| 代码 | `armblocks/`、`demos/`、`tools/`、`tests/` | MIT |
| 课程文档 | `docs/`、`README.md` | CC BY-NC-SA 4.0 |

## 4. 商标

- **UR5** 是 Universal Robots A/S 的产品与商标。
- **Unitree** / **宇树** 是杭州宇树科技有限公司的商标。

本项目与上述公司**无任何从属或背书关系**。

## 5. 免责

- 本项目为**教学用途**，模型仅用于离线/仿真环境。
- 如需驱动**真实硬件**，请遵循各厂商官方 SDK 及其条款：
  - Universal Robots：https://www.universal-robots.com/
  - 宇树：https://github.com/unitreerobotics/r1-7a_sdk
