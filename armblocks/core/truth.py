# -*- coding: utf-8 -*-
"""
真值参照（平台层）
==================
与「学生积木」完全独立的一条实现路径，永远正确，用于：

* 教学：把仿真真值和学生手算结果对照（预测—验证闭环）
* 测试：自动校验学生积木写得对不对

.. note::
   这不是"另一套公式"，而是同一套公式的**独立实现**——
   ``rot=None`` 时改用罗德里格斯公式，不经过学生填写的旋转积木。
"""
from __future__ import annotations

import numpy as np

from .kinematics import fk as _fk, ik as _ik


def fk_reference(model, q):
    """正运动学真值（不依赖学生积木）。"""
    return _fk(model, q, rot=None)


def ik_reference(model, p_target, R_target=None, q0=None, **kw):
    """逆运动学数值真值（不依赖学生积木）。"""
    return _ik(model, p_target, R_target, q0=q0, rot=None, **kw)


def forward_kinematics(model, q):
    """:func:`fk_reference` 的别名，语义更直白。"""
    return fk_reference(model, q)


__all__ = ["fk_reference", "ik_reference", "forward_kinematics"]
