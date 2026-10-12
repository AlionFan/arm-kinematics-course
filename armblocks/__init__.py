# -*- coding: utf-8 -*-
"""
armblocks —— 机械臂运动学「积木式」教学框架
=============================================

设计思想
--------
把一门机械臂运动学课程拆成两层：

* ``armblocks.core``   —— **平台层**（已搭好，学生不动）
  URDF 解析、齐次变换、真值正/逆运动学、可视化。

* ``armblocks.blocks`` —— **积木层**（★ 学生填写）
  每个文件是一块「积木」，只留数学核心为空白（TODO），
  其余脚手架全部就绪。把数学写好，仿真机械臂即可动起来。

* ``armblocks.solutions`` —— **参考答案**（教师用/自检用）

两台机械臂
----------
======================  ==========================================  ==========================
机型                    结构                                        课程定位
======================  ==========================================  ==========================
**UR5**（``UR5_URDF``）  6-DOF，标准 DH，6 个关节**全部绕自身 z 轴**   **主力机**：推导最干净
**宇树 R1**（``R1_URDF``） 7-DOF，关节轴 z/x/y/x/y/x/z 混合              **对照机**：多一个冗余自由度
======================  ==========================================  ==========================

两台臂的正运动学**共用同一套代码**：写好 ``blocks.rotations`` 里那三块旋转积木，
两台就都能动起来。

典型用法
--------
>>> from armblocks import UR5_URDF, blocks, load_model, fk
>>> import numpy as np
>>> model = load_model(UR5_URDF)
>>> p, R = fk(model, np.zeros(6), rot=blocks.rotations)   # 学生积木驱动
>>> print(p)
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: **主力机型** UR5（6-DOF，标准 DH，全关节绕 z）
UR5_URDF = ROOT / "models" / "ur5" / "ur5.urdf"
#: **对照机型** 宇树 R1 机械臂（7-DOF，冗余）
R1_URDF = ROOT / "models" / "r1_7a" / "R1_7a.urdf"

#: 默认机型 = UR5
DEFAULT_URDF = UR5_URDF

#: 两台机型的中文显示名
ROBOT_NAMES = {"ur5": "UR5 机械臂", "ur5e": "UR5e 机械臂", "ur5_robot": "UR5 机械臂",
               "r1_7a": "宇树 R1 机械臂"}

from . import blocks, solutions                               # noqa: E402
from .core.urdf_model import ArmModel, Joint, load_model      # noqa: E402
from .core.kinematics import fk, ik, link_frames              # noqa: E402
from .core.truth import fk_reference, ik_reference            # noqa: E402

__all__ = [
    "ROOT", "DEFAULT_URDF", "UR5_URDF", "R1_URDF", "ROBOT_NAMES",
    "blocks", "solutions",
    "ArmModel", "Joint", "load_model",
    "fk", "ik", "link_frames", "fk_reference", "ik_reference",
]
__version__ = "0.2.0"


def display_name(model) -> str:
    """给模型起一个好看的中文名（``ur5`` → ``UR5 机械臂``）。"""
    return ROBOT_NAMES.get(model.name, model.name)
