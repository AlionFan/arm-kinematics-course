# -*- coding: utf-8 -*-
"""
自动化测试 —— 用真值校验学生积木
================================
默认测试 ``armblocks.blocks``（学生写得对不对）。

用法::

    pytest -q                                    # 测学生积木
    ARMBLOCKS_IMPL=solutions pytest -q           # 测参考答案（应全绿）

未填写的积木会抛 ``NotImplementedError``，测试会显示"这块还没填"，
这正是给学生看的**待办清单**。
"""
import importlib
import os

import numpy as np
import pytest

import armblocks
from armblocks import UR5_URDF, R1_URDF, load_model
from armblocks.core.truth import fk_reference

IMPL = os.environ.get("ARMBLOCKS_IMPL", "blocks")


@pytest.fixture(scope="session")
def impl():
    return importlib.import_module(f"armblocks.{IMPL}")


@pytest.fixture(scope="session")
def model():
    """默认机型（UR5，主力）。"""
    return load_model(UR5_URDF)


@pytest.fixture(scope="session")
def ur5():
    return load_model(UR5_URDF)


@pytest.fixture(scope="session")
def r1():
    return load_model(R1_URDF)


# ------------------------------------------------------------------ M2 / M6
def test_polar_roundtrip(impl):
    for L, th in [(1.0, 0.3), (2.5, -1.1), (0.7, 2.9)]:
        x, y = impl.trig.polar_to_xy(L, th)
        L2, th2 = impl.trig.xy_to_polar(x, y)
        assert np.isclose(L2, L, atol=1e-9)
        assert np.isclose(np.cos(th2), np.cos(th), atol=1e-9)


def test_spherical_roundtrip(impl):
    for r, th, ph in [(1.0, 0.4, 1.2), (0.8, -2.0, 0.7), (1.5, 3.0, 2.4)]:
        x, y, z = impl.trig.sph2cart(r, th, ph)
        r2, th2, ph2 = impl.trig.cart2sph(x, y, z)
        assert np.isclose(r2, r, atol=1e-9)
        assert np.isclose(ph2, ph, atol=1e-9)


# ------------------------------------------------------------------ M7
def test_rotations_basic(impl):
    R = impl.rotations.rot_z(np.pi / 2)
    v = R @ np.array([1.0, 0.0, 0.0])
    assert np.allclose(v, [0, 1, 0], atol=1e-9)          # 绕 z 转 90°，x → y

    R = impl.rotations.rot_x(np.pi / 2)
    v = R @ np.array([0.0, 1.0, 0.0])
    assert np.allclose(v, [0, 0, 1], atol=1e-9)          # 绕 x 转 90°，y → z

    R = impl.rotations.rot_y(np.pi / 2)
    v = R @ np.array([0.0, 0.0, 1.0])
    assert np.allclose(v, [1, 0, 0], atol=1e-9)          # 绕 y 转 90°，z → x


def test_rotations_orthonormal(impl):
    for a in (0.0, 0.7, -2.3):
        for fn in (impl.rotations.rot_x, impl.rotations.rot_y, impl.rotations.rot_z):
            R = fn(a)
            assert np.allclose(R @ R.T, np.eye(3), atol=1e-9)
            assert np.isclose(np.linalg.det(R), 1.0, atol=1e-9)


# ------------------------------------------------------------------ M3 / M4
def test_fk_ik_2r_consistency(impl):
    L1, L2 = 0.3, 0.25
    for q1, q2 in [(0.4, 0.8), (-0.9, 1.4), (1.2, -0.6)]:
        x, y = impl.planar.fk_2r(L1, L2, q1, q2)
        sols = impl.planar.ik_2r(L1, L2, x, y)
        assert sols, "目标可达却返回空解"
        # 至少有一组解能正解回原目标
        ok = False
        for s1, s2 in sols:
            xs, ys = impl.planar.fk_2r(L1, L2, s1, s2)
            ok = ok or (np.isclose(xs, x, atol=1e-7) and np.isclose(ys, y, atol=1e-7))
        assert ok, "逆解无法正解回目标"


def test_ik_2r_unreachable(impl):
    assert impl.planar.ik_2r(0.3, 0.25, 5.0, 0.0) == []


# ------------------------------------------------------------------ M10
def test_euler_roundtrip(impl):
    for a, b, g in [(0.3, 0.5, -0.8), (1.0, -0.4, 0.2)]:
        R = impl.wrist.matrix_from_euler_zyx(a, b, g)
        a2, b2, g2 = impl.wrist.euler_zyx_from_matrix(R)
        R2 = impl.wrist.matrix_from_euler_zyx(a2, b2, g2)
        assert np.allclose(R, R2, atol=1e-9)


# ------------------------------------------------------------------ 集成：两台机械臂的正运动学
@pytest.mark.parametrize("which", ["ur5", "r1"])
def test_fk_matches_truth(which, impl, request):
    """学生旋转积木驱动的正解，应与平台真值完全一致（两台机型都要过）。"""
    m = request.getfixturevalue(which)
    rng = np.random.default_rng(7)
    for _ in range(5):
        q = m.random_q(rng)
        p_t, R_t = fk_reference(m, q)
        p_s, R_s = armblocks.fk(m, q, rot=impl.rotations)
        assert np.allclose(p_s, p_t, atol=1e-9)
        assert np.allclose(R_s, R_t, atol=1e-9)


@pytest.mark.parametrize("which", ["ur5", "r1"])
def test_ik_reaches_target(which, request):
    """数值 IK 应能到达一个随机生成的可达目标。"""
    from armblocks import ik
    from armblocks.core.kinematics import reachable_pair

    m = request.getfixturevalue(which)
    (p, R), q_true = reachable_pair(m, np.random.default_rng(3))
    q = ik(m, p, R, rng=np.random.default_rng(3))
    p2, R2 = fk_reference(m, q)
    assert np.linalg.norm(p2 - p) < 1e-2
    assert np.linalg.norm(R2 - R) < 5e-2


# ------------------------------------------------------------------ 模型结构
def test_ur5_structure(ur5):
    """UR5：6 自由度、全部绕 z、末端落在 tool0（说明固定关节被正确串进链条）。"""
    assert ur5.dof == 6
    assert ur5.base_link == "base_link"
    assert ur5.tip_link == "tool0"
    assert len(ur5.fixed_joints) == 3
    for j in ur5.joints:
        assert j.align_axis() == (1, "z")


def test_r1_structure(r1):
    """宇树 R1：7 自由度、轴 z/x/y 混合。"""
    assert r1.dof == 7
    assert r1.tip_link == "Link7"
    letters = [j.align_axis()[1] for j in r1.joints]
    assert set(letters) == {"x", "y", "z"}


def test_r1_zero_pose_unchanged(r1):
    """R1 零位末端位置（回归基准，防止解析改动引入漂移）。"""
    p, _ = fk_reference(r1, r1.home())
    assert np.allclose(p, [0.0027, -0.0341, 0.1929], atol=1e-3)


def test_ur5_zero_pose_matches_dh(ur5):
    """UR5 零位末端位置必须等于 DH 表的解析结果。

    在 UR 控制器的 Base 坐标系里，零位末端恰为 ``(a₂+a₃, −(d₄+d₆), d₁−d₅)``；
    ``base_link`` 相对 Base 多一个绕 z 的 π，所以 x、y 同时反号。
    """
    p, _ = fk_reference(ur5, ur5.home())
    a2, a3 = -0.425, -0.39225
    d1, d4, d5, d6 = 0.089159, 0.10915, 0.09465, 0.0823
    expect_in_base = np.array([a2 + a3, -(d4 + d6), d1 - d5])
    # base_link = Base 绕 z 转 π → 只有 x、y 反号，z 不变
    expect = np.array([-expect_in_base[0], -expect_in_base[1], expect_in_base[2]])
    assert np.allclose(p, expect, atol=1e-6)
    assert np.allclose(p, [0.8172, 0.1914, -0.0055], atol=1e-3)


# ------------------------------------------------------------------ 腕部几何
@pytest.mark.parametrize("which", ["ur5", "r1"])
def test_wrist_axis_distances_are_invariant(which, request):
    """轴间距离是机构固有属性，不随整体位形改变。"""
    from armblocks.core.geometry import wrist_report

    m = request.getfixturevalue(which)
    rng = np.random.default_rng(11)
    ref = tuple(round(it["distance"], 9) for it in wrist_report(m)["pairs"])
    for _ in range(4):
        cur = tuple(round(it["distance"], 9)
                    for it in wrist_report(m, m.random_q(rng))["pairs"])
        assert cur == ref


def test_ur5_wrist_is_not_spherical(ur5):
    """UR5 不是球形手腕：轴 4 与轴 6 平行且相距 94.65 mm。"""
    from armblocks.core.geometry import wrist_report

    r = wrist_report(ur5)
    assert not r["concurrent"]
    par = [it for it in r["pairs"] if it["parallel"]]
    assert len(par) == 1
    assert abs(par[0]["distance"] - 0.09465) < 1e-5
    assert abs(r["max_offset"] - 0.09465 / 2) < 1e-5


def test_r1_wrist_is_near_spherical(ur5, r1):
    """R1 的三轴几乎交于一点（偏差远小于 UR5） —— 两台机型的结构性差异。"""
    from armblocks.core.geometry import wrist_report

    dev_r1 = wrist_report(r1)["max_offset"]
    dev_ur5 = wrist_report(ur5)["max_offset"]
    assert dev_r1 < 0.01          # 约 5 mm
    assert dev_r1 < dev_ur5 / 5   # 明显比 UR5 更接近球形


def test_only_wrist3_leaves_tool0_fixed(ur5):
    """tool0 落在轴 6 上 → 只转 wrist_3，末端位置不变。"""
    from armblocks import fk

    p0, _ = fk(ur5, ur5.home())
    for ang in (0.5, 1.57, 3.0):
        q = ur5.home()
        q[5] = ang
        p, _ = fk(ur5, q)
        assert np.linalg.norm(p - p0) < 1e-12

