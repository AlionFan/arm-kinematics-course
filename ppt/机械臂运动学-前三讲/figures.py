# -*- coding: utf-8 -*-
"""生成三份讲义所用的配图（白底、无页眉页脚），与 PPT 同源。"""
import math

from pptx import Presentation
from pptx.enum.dml import MSO_LINE_DASH_STYLE

import build_pptx as B


def newprs():
    p = Presentation()
    p.slide_width = B.E(1280)
    p.slide_height = B.E(720)
    B.prs = p
    return p


def fig1_joint_chain():
    """M1 配图：关节链 + 六个关节角表盘。"""
    s = B.slide(B.WHITE)
    P = [(240, 560), (240, 430), (320.3, 315.3), (469.7, 302.2),
         (524.7, 397.5), (616.5, 422.1)]
    B.rect(s, 216, 568, 48, 14, fill=B.BLUE)
    for i in range(len(P) - 1):
        c = B.BLUE if i % 2 == 0 else B.MID
        B.line(s, P[i][0], P[i][1], P[i + 1][0], P[i + 1][1], color=c,
               w=10 if i < 3 else 8)
    for i, (px, py) in enumerate(P):
        B.oval(s, px, py, 12, fill=B.WHITE, linec=B.BLUE, lw=2.6)
        B.text(s, px + 17, py - 30, 30, 22, str(i + 1), size=13, color=B.BLUE,
               bold=True, font=B.EN, spacing=1.0)
    B.line(s, P[5][0], P[5][1], P[5][0] + 26, P[5][1] - 14, color=B.INK, w=4)
    B.line(s, P[5][0], P[5][1], P[5][0] + 26, P[5][1] + 14, color=B.INK, w=4)
    B.label(s, 168, 586, '底座', size=14, color=B.MUTED, w=90)
    B.label(s, 664, 452, '末端', size=14, color=B.MUTED, w=80)
    B.arrow(s, 690, 330, 916, 330, color=B.MID, w=2.2)
    B.label(s, 802, 304, 'q1 … q6', size=17, color=B.BLUE, font=B.EN, w=150)
    angs = [90, 55, 5, -60, -25, 30]
    xs, ys = [1010, 1170], [200, 340, 480]
    for i in range(6):
        B.dial(s, xs[i % 2], ys[i // 2], 36, angs[i], color=B.MID,
               needle=B.BLUE, lab='q%d' % (i + 1), lab_size=14)


def fig2_unit_circle():
    """M2 配图：单位圆与投影。"""
    s = B.slide(B.WHITE)
    ox, oy, R = 520, 348, 226
    B.line(s, ox - 320, oy, ox + 330, oy, color=B.LIGHT, w=2.0)
    B.line(s, ox, oy + 262, ox, oy - 262, color=B.LIGHT, w=2.0)
    B.oval(s, ox, oy, R, linec=B.MID, lw=3.0)
    ang = 52
    tx = ox + R * math.cos(math.radians(ang))
    ty = oy - R * math.sin(math.radians(ang))
    B.line(s, ox, oy, tx, ty, color=B.BLUE, w=4.0)
    B.line(s, tx, ty, tx, oy, color=B.MID, w=2.0, dash=MSO_LINE_DASH_STYLE.DASH)
    B.line(s, tx, ty, ox, ty, color=B.MID, w=2.0, dash=MSO_LINE_DASH_STYLE.DASH)
    B.arc(s, ox, oy, 80, 0, ang, color=B.BLUE, w=2.4)
    B.oval(s, ox, oy, 6, fill=B.BLUE)
    B.oval(s, tx, ty, 10, fill=B.BLUE)
    B.label(s, ox + 42, oy - 48, 'θ', size=24, color=B.BLUE, font=B.EN, w=60)
    B.label(s, 860, 140, 'P (cos θ, sin θ)', size=18, color=B.INK, font=B.EN, w=300)
    B.label(s, (tx + ox) / 2, oy + 30, 'cos θ', size=18, color=B.BLUE, font=B.EN, w=150)
    B.label(s, ox - 76, (ty + oy) / 2, 'sin θ', size=18, color=B.BLUE, font=B.EN, w=150)
    B.text(s, 40, 624, 1200, 50, 'x = cos θ            y = sin θ', size=30,
           color=B.NAVY, font=B.EN, align=1, spacing=1.0)


def fig3_vector_sum():
    """M3 配图：2R 两段向量相加。"""
    s = B.slide(B.WHITE)
    ox, oy = 300, 566
    L1, L2, a1, a2 = 262, 196, 55, 22
    p1 = (ox + L1 * math.cos(math.radians(a1)), oy - L1 * math.sin(math.radians(a1)))
    p2 = (p1[0] + L2 * math.cos(math.radians(a2)),
          p1[1] - L2 * math.sin(math.radians(a2)))
    B.line(s, ox - 50, oy, ox + 450, oy, color=B.LIGHT, w=1.6)
    B.line(s, ox, oy + 50, ox, oy - 360, color=B.LIGHT, w=1.6)
    B.line(s, ox, oy, p2[0], p2[1], color=B.MUTED, w=1.8,
           dash=MSO_LINE_DASH_STYLE.DASH)
    B.arc(s, ox, oy, 82, 0, a1, color=B.BLUE, w=2.2)
    B.arc(s, ox, oy, 148, 0, a1 + a2, color=B.MID, w=2.0)
    B.oval(s, ox, oy, 8, fill=B.BLUE)
    B.oval(s, p2[0], p2[1], 8, fill=B.RED)
    B.arrow(s, ox, oy, p1[0], p1[1], color=B.BLUE, w=9, hs='lg')
    B.arrow(s, p1[0], p1[1], p2[0], p2[1], color=B.MID, w=8, hs='lg')
    B.oval(s, p1[0], p1[1], 9, fill=B.WHITE, linec=B.BLUE, lw=2.4)
    B.oval(s, p2[0], p2[1], 9, fill=B.RED, linec=B.WHITE, lw=2.0)
    B.oval(s, ox, oy, 9, fill=B.BLUE)
    B.label(s, ox + 104, oy - 30, 'θ1', size=19, color=B.BLUE, font=B.EN, w=70)
    B.label(s, ox + 190, oy - 94, 'θ1+θ2', size=17, color=B.MID, font=B.EN, w=140)
    B.label(s, (ox + p1[0]) / 2 - 20, (oy + p1[1]) / 2 + 16, 'a1', size=19,
            color=B.BLUE, font=B.EN, w=60)
    B.label(s, (p1[0] + p2[0]) / 2 + 22, (p1[1] + p2[1]) / 2 - 6, 'a2', size=19,
            color=B.MID, font=B.EN, w=60)
    B.label(s, (ox + p2[0]) / 2 - 34, (oy + p2[1]) / 2 + 10, 'r', size=19,
            color=B.MUTED, font=B.EN, w=50)
    B.label(s, p2[0] + 26, p2[1] - 34, '(x, y)', size=17, color=B.RED, font=B.EN, w=120)

    B.text(s, 700, 150, 540, 40, 'a1 = L1 · ( cos θ1 , sin θ1 )', size=20,
           color=B.NAVY, font=B.EN, spacing=1.0)
    B.text(s, 700, 206, 540, 40, 'a2 = L2 · ( cos(θ1+θ2) , sin(θ1+θ2) )', size=20,
           color=B.NAVY, font=B.EN, spacing=1.0)
    B.line(s, 700, 266, 1240, 266, color=B.LIGHT, w=1.6)
    B.text(s, 700, 292, 540, 40, 'r = a1 + a2', size=22, color=B.NAVY,
           font=B.EN, bold=True, spacing=1.0)
    B.text(s, 700, 380, 540, 90,
           ['x = L1·cos θ1 + L2·cos(θ1+θ2)',
            'y = L1·sin θ1 + L2·sin(θ1+θ2)'], size=18, color=B.BLUE,
           font=B.EN, spacing=1.7)


def fig4_annulus():
    """M3 配图：可达圆环（真实比例 + 局部放大）。"""
    s = B.slide(B.WHITE)
    ox, oy, R = 264, 330, 194
    inner = R * (0.08 / 0.52)
    sh = B.rect(s, ox - R, oy - R, 2 * R, 2 * R, fill=B.MID,
                shape=B.MSO_SHAPE.DONUT)
    sh.adjustments[0] = (R - inner) / (2.0 * R)
    B.oval(s, ox, oy, inner, fill=B.WHITE, linec=B.BLUE, lw=2.0)
    B.oval(s, ox, oy, R, linec=B.BLUE, lw=2.0)
    B.line(s, ox, oy, ox + R, oy, color=B.WHITE, w=1.4)
    B.label(s, ox + R * 0.55, oy - 24, '0.52', size=15, color=B.WHITE, font=B.EN, w=90)
    zoom_r = R * (0.16 / 0.52)
    zc = B.oval(s, ox, oy, zoom_r, linec=B.NAVY, lw=1.8)
    zc.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    ix, iy, iR = 676, 330, 144
    ii = iR * (0.08 / 0.16)
    for sgn in (1, -1):
        pa = (ox + zoom_r * math.cos(math.radians(35 * sgn)),
              oy - zoom_r * math.sin(math.radians(35 * sgn)))
        qa = (ix + iR * math.cos(math.radians(145 * sgn)),
              iy - iR * math.sin(math.radians(145 * sgn)))
        B.line(s, pa[0], pa[1], qa[0], qa[1], color=B.MUTED, w=1.2,
               dash=MSO_LINE_DASH_STYLE.DASH)
    sh2 = B.rect(s, ix - iR, iy - iR, 2 * iR, 2 * iR, fill=B.MID,
                 shape=B.MSO_SHAPE.DONUT)
    sh2.adjustments[0] = (iR - ii) / (2.0 * iR)
    B.oval(s, ix, iy, ii, fill=B.WHITE, linec=B.RED, lw=2.4)
    B.oval(s, ix, iy, iR, linec=B.BLUE, lw=2.0)
    B.line(s, ix, iy, ix + ii, iy, color=B.WHITE, w=1.4)
    B.label(s, ix, oy + iR + 34, '放大：只看 r ≤ 0.16 的范围', size=14,
            color=B.MUTED, w=440)
    B.label(s, ox, oy + R + 34, '外圈 L1 + L2 = 0.52 m', size=14, color=B.MUTED, w=380)

    B.text(s, 866, 178, 374, 74, '0.08', size=54, color=B.NAVY, bold=True,
           font=B.EN, spacing=1.0)
    B.text(s, 866, 258, 374, 30, '最小可达距离 / m　|L1 − L2|', size=14,
           color=B.SUB, spacing=1.0)
    B.line(s, 866, 310, 1240, 310, color=B.LIGHT, w=1.4)
    B.text(s, 866, 332, 374, 74, '0.52', size=54, color=B.NAVY, bold=True,
           font=B.EN, spacing=1.0)
    B.text(s, 866, 412, 374, 30, '最大可达距离 / m　L1 + L2', size=14,
           color=B.SUB, spacing=1.0)
    B.text(s, 866, 470, 374, 40, '区间内任意一点都能到达', size=15, color=B.SUB,
           spacing=1.0)


if __name__ == '__main__':
    newprs()
    fig1_joint_chain()
    fig2_unit_circle()
    fig3_vector_sum()
    fig4_annulus()
    B.prs.save('figures.pptx')
    print('figures.pptx saved, slides =', len(B.prs.slides._sldIdLst))
