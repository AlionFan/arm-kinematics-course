# -*- coding: utf-8 -*-
"""
积木层（★ 学生填写）
====================

这里每一块「积木」只留**数学核心**为空白。你的任务：
把标着 ``TODO`` 的地方按课程推出来的公式补全。

填写顺序（对应课程模块）：

===========  ==========================  ==============================
文件          积木                        对应模块
===========  ==========================  ==============================
trig.py       polar_to_xy / xy_to_polar   M2  角度→位置
trig.py       sph2cart / cart2sph         M6  球坐标升维
rotations.py  rot_x / rot_y / rot_z       M7  ★ 旋转矩阵（最关键的一块）
planar.py     fk_2r / ik_2r               M3–M4 平面臂正/逆运动学
wrist.py      euler / 姿态矩阵            M10 球形手腕姿态反解
===========  ==========================  ==============================

.. important::
    **只要写好 rotations.py 里的三块旋转积木，两台机械臂就都能动起来** ——
    UR5（6 轴）和宇树 R1（7 轴）的正运动学共用同一套代码。

写好后运行::

    pytest -q                       # 自动对照真值，告诉你哪块积木算错了

或直接看机械臂动起来::

    python demos/demo_ur5_arm.py        # 主力机型 UR5
    python demos/demo_compare_arms.py   # UR5 与 R1 对照
"""
from . import trig, rotations, planar, wrist

__all__ = ["trig", "rotations", "planar", "wrist"]
