# -*- coding: utf-8 -*-
"""
《机械臂运动学》前三讲 讲课 PPT 生成器  v2 —— 以图为主
================================================================
设计体系：学术风（蓝白克制 / 证据驱动）
画布：1280 x 720 px  (96 px = 1 in)
版心：页眉 0–76 / 内容区 88–640 / 页脚 656–700

v2 改版原则
  1) 每页以 1 张大图（原生矢量形状，可在 PPT 里继续编辑）为主体，图占内容区 ≥ 60%
  2) 页面上只保留：标题 + 图上标注 + 至多一行公式；不写解释性句子
  3) 所有讲稿、解释、提问、易错点 → 演讲者备注（notes）
"""
import math

from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.oxml.ns import qn

PX = 9525  # EMU per px


def E(v):
    return Emu(int(round(v * PX)))


# ---------------- 调色板（学术风预设） ----------------
NAVY = RGBColor(0x0E, 0x3F, 0x8C)
NAVY2 = RGBColor(0x16, 0x51, 0xA8)
NAVY3 = RGBColor(0x1B, 0x5C, 0xBC)
BLUE = RGBColor(0x1E, 0x4F, 0xA8)
MID = RGBColor(0x3D, 0x7B, 0xD9)
LIGHT = RGBColor(0xE8, 0xEF, 0xF8)
LIGHT2 = RGBColor(0xF4, 0xF8, 0xFD)
INK = RGBColor(0x1A, 0x22, 0x30)
SUB = RGBColor(0x4A, 0x55, 0x68)
MUTED = RGBColor(0x8B, 0x97, 0xA8)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
RED = RGBColor(0xD9, 0x53, 0x4F)
ONDK = RGBColor(0xCF, 0xE0, 0xF5)
ONDK2 = RGBColor(0x9F, 0xBE, 0xE6)
ONDK3 = RGBColor(0x6E, 0x95, 0xC8)

CN = 'Microsoft YaHei'
EN = 'Times New Roman'
MONO = 'Consolas'

prs = Presentation()
prs.slide_width = E(1280)
prs.slide_height = E(720)
BLANK = prs.slide_layouts[6]
TOTAL = 21

CX, CW = 40, 1200
TOP, BOT = 88, 640


# =====================================================================
# 基础绘制
# =====================================================================
def slide(bg=WHITE):
    s = prs.slides.add_slide(BLANK)
    b = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, E(1280), E(720))
    b.fill.solid()
    b.fill.fore_color.rgb = bg
    b.line.fill.background()
    b.shadow.inherit = False
    return s


def rect(s, x, y, w, h, fill=None, linec=None, lw=1.0, dash=None,
         shape=MSO_SHAPE.RECTANGLE, radius=None):
    sh = s.shapes.add_shape(shape, E(x), E(y), E(w), E(h))
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
    if linec is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = linec
        sh.line.width = Pt(lw)
        if dash is not None:
            sh.line.dash_style = dash
    sh.shadow.inherit = False
    if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        sh.adjustments[0] = radius
    return sh


def oval(s, cx, cy, r, fill=None, linec=None, lw=1.0, rx=None, ry=None):
    rx = r if rx is None else rx
    ry = r if ry is None else ry
    return rect(s, cx - rx, cy - ry, 2 * rx, 2 * ry, fill=fill, linec=linec,
                lw=lw, shape=MSO_SHAPE.OVAL)


def line(s, x1, y1, x2, y2, color=MID, w=1.5, dash=None):
    cn = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, E(x1), E(y1), E(x2), E(y2))
    cn.line.color.rgb = color
    cn.line.width = Pt(w)
    if dash is not None:
        cn.line.dash_style = dash
    return cn


def arrow(s, x1, y1, x2, y2, color=BLUE, w=2.0, dash=None, both=False,
          head='triangle', hs='med'):
    cn = line(s, x1, y1, x2, y2, color=color, w=w, dash=dash)
    ln = cn.line._get_or_add_ln()
    if both:
        he = ln.makeelement(qn('a:headEnd'), {'type': head, 'w': hs, 'len': hs})
        ln.append(he)
    te = ln.makeelement(qn('a:tailEnd'), {'type': head, 'w': hs, 'len': hs})
    ln.append(te)
    return cn


def polyline(s, pts, color=BLUE, w=2.0, closed=False, fill=None, dash=None):
    fb = s.shapes.build_freeform(E(pts[0][0]), E(pts[0][1]), scale=1.0)
    fb.add_line_segments([(E(px), E(py)) for px, py in pts[1:]], close=closed)
    sh = fb.convert_to_shape()
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
    if color is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = color
        sh.line.width = Pt(w)
        if dash is not None:
            sh.line.dash_style = dash
    sh.shadow.inherit = False
    return sh


def arc_pts(cx, cy, r, a0, a1, n=40):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy - r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def arc(s, cx, cy, r, a0, a1, color=MID, w=2.0, n=40, dash=None):
    return polyline(s, arc_pts(cx, cy, r, a0, a1, n), color=color, w=w, dash=dash)


def set_font(run, name):
    run.font.name = name
    rPr = run._r.get_or_add_rPr()
    for tag in ('a:ea', 'a:cs'):
        el = rPr.find(qn(tag))
        if el is None:
            el = rPr.makeelement(qn(tag), {})
            rPr.append(el)
        el.set('typeface', name)


def text(s, x, y, w, h, paras, size=16, color=INK, bold=False, font=CN,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=1.25, space_after=0):
    tb = s.shapes.add_textbox(E(x), E(y), E(w), E(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    if isinstance(paras, str):
        paras = [paras]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        p.space_after = Pt(space_after)
        runs = para if isinstance(para, list) else [(para, {})]
        for t, st in runs:
            r = p.add_run()
            r.text = t
            r.font.size = Pt(st.get('size', size))
            r.font.bold = st.get('bold', bold)
            r.font.color.rgb = st.get('color', color)
            set_font(r, st.get('font', font))
    return tb


def notes(s, lines):
    """把解释性文字写进演讲者备注。"""
    if isinstance(lines, str):
        lines = [lines]
    tf = s.notes_slide.notes_text_frame
    tf.text = lines[0]
    for t in lines[1:]:
        tf.add_paragraph().text = t
    for p in tf.paragraphs:
        for r in p.runs:
            r.font.size = Pt(12)
            set_font(r, CN)


def hdr(s, title, tag, page, dark=False):
    if dark:
        line(s, 0, 76, 1280, 76, color=NAVY2, w=1.2)
        text(s, CX, 0, 860, 76, title, size=30, color=WHITE, bold=True,
             anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
        text(s, 900, 0, 340, 76, tag, size=14, color=ONDK2,
             align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
        text(s, CX, 656, 800, 44, '机械臂运动学 · 前三讲', size=13, color=ONDK3,
             anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
        text(s, 840, 656, 400, 44, '%02d / %d' % (page, TOTAL), size=13, color=ONDK2,
             bold=True, font=EN, align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    else:
        rect(s, 0, 0, 1280, 76, fill=BLUE)
        text(s, CX, 0, 860, 76, title, size=30, color=WHITE, bold=True,
             anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
        text(s, 900, 0, 340, 76, tag, size=14, color=ONDK,
             align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
        text(s, CX, 656, 800, 44, '机械臂运动学 · 前三讲', size=13, color=MUTED,
             anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
        text(s, 840, 656, 400, 44, '%02d / %d' % (page, TOTAL), size=13, color=NAVY,
             bold=True, font=EN, align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)


def label(s, cx, cy, txt, size=14, color=SUB, font=CN, bold=False, w=160, h=26):
    """以 (cx, cy) 为中心的短标注。"""
    text(s, cx - w / 2.0, cy - h / 2.0, w, h, txt, size=size, color=color,
         font=font, bold=bold, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
         spacing=1.0)


def chip(s, x, y, w, h, txt, color=ONDK, linec=ONDK2, size=15):
    rect(s, x, y, w, h, fill=None, linec=linec, lw=1.2,
         shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.5)
    text(s, x, y, w, h, txt, size=size, color=color,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)


def dial(s, cx, cy, r, ang, color=MID, needle=WHITE, lab=None,
         label_color=SUB, lw=1.6, fill=None, lab_size=13):
    oval(s, cx, cy, r, fill=fill, linec=color, lw=lw)
    line(s, cx, cy, cx + r * 0.78 * math.cos(math.radians(ang)),
         cy - r * 0.78 * math.sin(math.radians(ang)), color=needle, w=2.4)
    oval(s, cx, cy, 2.6, fill=needle)
    if lab:
        label(s, cx, cy + r + 16, lab, size=lab_size, color=label_color)


def pic_chain(s, cx, cy, k=1.0, c=BLUE, c2=MID):
    """关节链小图标。"""
    p0 = (cx - 46 * k, cy + 44 * k)
    p1 = (cx - 18 * k, cy - 16 * k)
    p2 = (cx + 30 * k, cy + 2 * k)
    p3 = (cx + 48 * k, cy - 36 * k)
    line(s, p0[0], p0[1], p1[0], p1[1], color=c, w=7 * k)
    line(s, p1[0], p1[1], p2[0], p2[1], color=c2, w=6 * k)
    line(s, p2[0], p2[1], p3[0], p3[1], color=c, w=5 * k)
    oval(s, p0[0], p0[1], 7 * k, fill=c)
    oval(s, p1[0], p1[1], 6 * k, fill=c2, linec=WHITE, lw=1.4)
    oval(s, p2[0], p2[1], 5 * k, fill=c2)
    oval(s, p3[0], p3[1], 6 * k, fill=c, linec=WHITE, lw=1.4)


def pic_unit(s, cx, cy, r, c=MID, ang=52, dlab=False, lab_color=SUB, lw=2.4):
    """单位圆小图标。"""
    oval(s, cx, cy, r, linec=c, lw=lw)
    tx = cx + r * math.cos(math.radians(ang))
    ty = cy - r * math.sin(math.radians(ang))
    line(s, cx, cy, tx, ty, color=c, w=2.0)
    line(s, tx, ty, tx, cy, color=c, w=1.2, dash=MSO_LINE_DASH_STYLE.DASH)
    line(s, tx, ty, cx, ty, color=c, w=1.2, dash=MSO_LINE_DASH_STYLE.DASH)
    oval(s, tx, ty, 4.5, fill=c)
    arc(s, cx, cy, r * 0.34, 0, ang, color=c, w=1.6)


def pic_ring(s, cx, cy, r, inner_r, c=MID, ang=28, hole=WHITE):
    """圆环（可达空间）小图标：显式填出空腔，保证任何渲染器下一致。"""
    sh = rect(s, cx - r, cy - r, 2 * r, 2 * r, fill=c, shape=MSO_SHAPE.DONUT)
    sh.adjustments[0] = max(0.02, min(0.49, (r - inner_r) / (2.0 * r)))
    oval(s, cx, cy, inner_r, fill=hole, linec=hole, lw=0.75)
    tx = cx + r * math.cos(math.radians(ang))
    ty = cy - r * math.sin(math.radians(ang))
    line(s, cx, cy, tx, ty, color=WHITE, w=1.4)
    oval(s, cx, cy, 3.0, fill=WHITE)


# =====================================================================
# P1 · 封面
# =====================================================================
def p01():
    s = slide(NAVY)
    text(s, 80, 158, 660, 26, '高中 · 机器人运动学入门课', size=16, color=ONDK2)
    text(s, 80, 190, 680, 84, '机械臂运动学', size=56, color=WHITE, bold=True, spacing=1.05)
    text(s, 80, 284, 680, 34, 'Robotic Arm Kinematics with Trigonometry',
         size=20, color=ONDK2, font=EN, spacing=1.0)
    rect(s, 80, 338, 92, 4, fill=BLUE)
    text(s, 80, 364, 620, 30, '用三角函数看懂机械臂：从关节角到末端位置',
         size=20, color=WHITE, spacing=1.2)
    text(s, 80, 470, 620, 130, [
        '适用对象  高中 · 有三角函数基础、会一点 Python',
        '课时安排  5 课时（M1 两课时 · M2 一课时 · M3 两课时）',
        '配套机型  UR5（主力）· 宇树 R1（对照）',
    ], size=15, color=ONDK2, spacing=1.9)

    ox, oy = 870, 486
    polyline(s, arc_pts(ox, oy, 310, -12, 118), color=NAVY3, w=1.6,
             dash=MSO_LINE_DASH_STYLE.DASH)
    rect(s, ox - 42, oy + 2, 84, 16, fill=NAVY3)
    p1x, p1y = 909.5, 300.2
    p2x, p2y = 1044.3, 234.4
    line(s, ox, oy, p1x, p1y, color=WHITE, w=9)
    line(s, p1x, p1y, p2x, p2y, color=MID, w=8)
    arc(s, ox, oy, 76, 0, 78, color=ONDK2, w=2.2)
    arc(s, p1x, p1y, 52, 26, 78, color=ONDK2, w=2.2)
    oval(s, ox, oy, 12, fill=WHITE)
    oval(s, p1x, p1y, 10, fill=BLUE, linec=WHITE, lw=2.0)
    oval(s, p2x, p2y, 11, fill=WHITE)
    label(s, 972, 420, 'θ1', size=20, color=ONDK2, font=EN, w=60)
    label(s, 916, 268, 'θ2', size=18, color=ONDK2, font=EN, w=60)
    label(s, 1096, 220, '末端', size=15, color=ONDK2, w=70)
    label(s, 1082, 158, '可达范围', size=14, color=NAVY3, w=110)
    notes(s, [
        '开场 3 分钟。',
        '不要先讲公式。先指着这张图问三个问题：',
        '① 这台机械臂"手"（末端）现在在哪里？',
        '② 我如果想让手移动到别处，该拧哪几个关节？',
        '③ 有没有可能拧法不止一种？',
        '这三个问题分别对应：正运动学、逆运动学、逆解多解性——也就是前三讲要解决的全部内容。',
        '强调本课的一句话主线：机械臂运动学，本质上就是三角函数。',
        '版本信息：UR5 为主力模型（6 自由度），宇树 R1 为对照模型（7 自由度），',
        '两台机器人的参数文件都已放在课程仓库里，学生可以自己打开对照。',
        '预告考核方式：每讲一次"预测—验证"记录，期末做一个能在仿真里到达指定点位的小项目。',
    ])


# =====================================================================
# P2 · 目录
# =====================================================================
def p02():
    s = slide()
    hdr(s, '本讲内容', '目录', 2)
    rows = [
        ('01', '机械臂怎么“知道”手在哪？', 'P3–P7'),
        ('02', '单位圆与“角度坐标”', 'P8–P12'),
        ('03', '平面正运动学：1R → 2R → 3R', 'P13–P20'),
    ]
    y = 96
    for i, (num, title, pg) in enumerate(rows):
        cx = 246
        cy = y + 84
        if i == 0:
            pic_chain(s, cx, cy, k=1.05)
        elif i == 1:
            pic_unit(s, cx, cy, 46, c=BLUE, ang=52)
        else:
            pic_ring(s, cx, cy, 46, 20, c=BLUE, ang=30)
        text(s, 48, y, 110, 168, num, size=54, color=BLUE, bold=True, font=EN,
             anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
        line(s, 336, y + 26, 336, y + 142, color=LIGHT, w=1.4)
        text(s, 368, y + 40, 700, 46, title, size=26, color=INK, bold=True,
             anchor=MSO_ANCHOR.MIDDLE, spacing=1.1)
        text(s, 1120, y, 120, 168, pg, size=15, color=BLUE, bold=True, font=EN,
             align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
        if i < 2:
            line(s, 48, y + 176, 1232, y + 176, color=LIGHT, w=1.2)
        y += 180
    notes(s, [
        '本章只走三站，每站一个问题。',
        '第 1 站（P3–P7）：机械臂怎么"知道"手在哪？建立两个空间的直觉，并用 UR5 与宇树 R1 的实测数据做对照。',
        '第 2 站（P8–P12）：单位圆与"角度坐标"。把 sin、cos 从"三角形里的比值"升级成"坐标"，再引出 atan2。',
        '第 3 站（P13–P20）：平面正运动学。从 1R 讲到 3R，亲手推出角度累加公式，最后发现可达空间是一个圆环。',
        '节奏说明：每站都是"先看懂图 → 再推公式 → 最后写代码验证"。',
        '整门课的计算量很小，难点全在"把图看对"。提醒学生随时可以打断提问。',
    ])


# =====================================================================
# 章节扉页
# =====================================================================
def section(num, title, pills, widths, page, pict):
    s = slide(NAVY)
    text(s, 58, 96, 420, 300, num, size=210, color=NAVY2, bold=True, font=EN,
         anchor=MSO_ANCHOR.MIDDLE, spacing=0.9)
    text(s, 60, 392, 800, 80, title, size=42, color=WHITE, bold=True, spacing=1.1)
    rect(s, 62, 484, 84, 4, fill=BLUE)
    x = 60
    for i, p in enumerate(pills):
        chip(s, x, 512, widths[i], 44, p)
        x += widths[i] + 14
    pict(s)
    text(s, CX, 656, 800, 44, '机械臂运动学 · 前三讲', size=13, color=ONDK3,
         anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(s, 840, 656, 400, 44, '%02d / %d' % (page, TOTAL), size=13, color=ONDK2,
         bold=True, font=EN, align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    return s


def _s1_pict(s):
    pic_chain(s, 960, 300, k=2.1, c=MID, c2=ONDK)


def _s2_pict(s):
    pic_unit(s, 960, 300, 152, c=MID, ang=52, lw=3.0)
    oval(s, 960, 300, 3.4, fill=ONDK)


def _s3_pict(s):
    pic_ring(s, 960, 300, 152, 64, c=MID, ang=28, hole=NAVY)


def p03():
    s = section('01', '机械臂怎么“知道”手在哪？',
                ['正运动学 FK', '逆运动学 IK', '两个空间'], [132, 132, 118], 3, _s1_pict)
    notes(s, [
        '第 1 讲驱动问题：机械臂怎么"知道"自己的手在哪？',
        '这一讲不写代码，只做三件事：认识"关节链"这个结构、分清"两个空间"、说清 FK 与 IK 的方向。',
        '课堂先让学生看一眼实物/仿真里的 UR5，数一数它有几个关节，再猜"要控制手的位置，至少要几个数"。',
        '结论先不给，留到 P4–P7 逐张图揭晓。本讲结束时学生要能自己复述：',
        '"关节角是输入，末端位置是输出；反过来求就是逆运动学。"',
    ])


def p04():
    s = slide()
    hdr(s, '机械臂是一串“关节”', 'M1 · 第 1 讲', 4)
    P = [(200, 560), (200, 430), (280.3, 315.3), (429.7, 302.2),
         (484.7, 397.5), (576.5, 422.1)]
    rect(s, 176, 568, 48, 14, fill=BLUE)
    for i in range(len(P) - 1):
        c = BLUE if i % 2 == 0 else MID
        line(s, P[i][0], P[i][1], P[i + 1][0], P[i + 1][1], color=c, w=10 if i < 3 else 8)
    for i, (px, py) in enumerate(P):
        oval(s, px, py, 12, fill=WHITE, linec=BLUE, lw=2.6)
        text(s, px + 17, py - 30, 30, 22, str(i + 1), size=13, color=BLUE,
             bold=True, font=EN, spacing=1.0)
    line(s, P[5][0], P[5][1], P[5][0] + 26, P[5][1] - 14, color=INK, w=4)
    line(s, P[5][0], P[5][1], P[5][0] + 26, P[5][1] + 14, color=INK, w=4)
    label(s, 138, 584, '底座', size=13, color=MUTED, w=90)
    label(s, 620, 452, '末端', size=13, color=MUTED, w=80)

    arrow(s, 646, 330, 872, 330, color=MID, w=2.2)
    label(s, 758, 306, 'q1 … q6', size=16, color=BLUE, font=EN, w=140)
    angs = [90, 55, 5, -60, -25, 30]
    xs = [930, 1090]
    ys = [184, 324, 464]
    for i in range(6):
        cx = xs[i % 2]
        cy = ys[i // 2]
        dial(s, cx, cy, 34, angs[i], color=MID, needle=BLUE, lab='q%d' % (i + 1))
    notes(s, [
        '看图说话，不要念文字。',
        '① 从左到右数：底座、6 个关节、末端执行器。每个关节都由一个电机驱动，电机的转角就是"关节变量"。',
        '"关节"和"电机"要区分：关节是机械转动副，电机是拧动它的东西，而我们真正关心的是转角这个数。',
        '② 右边 6 个表盘就是"关节变量 q1…q6"的直观样子：一根针指向当前角度。',
        '③ 关键洞察：机械臂的"状态"可以用 6 个角度完全描述。6 个数字决定一切，包括手在哪、朝向哪。',
        '对比说明：UR5 是 6 自由度（q1…q6）；宇树 R1 是 7 自由度，多出 1 个表盘。',
        '本页留一个悬念：6 个数字 → 手的位置，这个映射是唯一确定的吗？反过来呢？下一张图回答。',
        '提问设计：让学生指着手臂说出"第 3 个关节转 10 度，末端会往哪动"，先凭直觉答，M3 再用公式验证。',
    ])


def p05():
    s = slide()
    hdr(s, '同一台机械臂，两种描述', 'M1 · 第 1 讲', 5)
    rect(s, 40, 108, 508, 500, fill=LIGHT2, linec=LIGHT, lw=1.4)
    rect(s, 732, 108, 508, 500, fill=LIGHT2, linec=LIGHT, lw=1.4)
    text(s, 64, 132, 460, 32, '关节空间', size=24, color=NAVY, bold=True)
    text(s, 756, 132, 460, 32, '笛卡尔空间', size=24, color=NAVY, bold=True)
    line(s, 64, 176, 524, 176, color=LIGHT, w=1.4)
    line(s, 756, 176, 1216, 176, color=LIGHT, w=1.4)
    dial(s, 160, 300, 52, 90, color=BLUE, needle=BLUE, lab='q1')
    dial(s, 294, 300, 52, 52, color=BLUE, needle=BLUE, lab='q2')
    dial(s, 428, 300, 52, -18, color=BLUE, needle=BLUE, lab='q3')

    ax, ay = 900, 400
    arrow(s, ax - 150, ay, ax + 170, ay, color=INK, w=1.8, hs='sm')
    arrow(s, ax, ay + 150, ax, ay - 170, color=INK, w=1.8, hs='sm')
    label(s, ax + 196, ay + 4, 'x', size=17, color=INK, font=EN, w=50)
    label(s, ax - 4, ay - 200, 'y', size=17, color=INK, font=EN, w=50)
    oval(s, ax + 108, ay - 108, 9, fill=RED)
    line(s, ax, ay, ax + 108, ay - 108, color=RED, w=2.0, dash=MSO_LINE_DASH_STYLE.DASH)
    label(s, ax + 176, ay - 132, '(x, y)', size=16, color=RED, font=EN, w=90)
    label(s, ax + 54, ay + 40, '末端', size=13, color=MUTED, w=70)

    arrow(s, 570, 358, 712, 358, color=BLUE, w=3.0, head='triangle', hs='lg')
    arrow(s, 712, 452, 570, 452, color=MID, w=3.0, head='triangle', hs='lg')
    label(s, 641, 322, '角度 → 位置', size=14, color=BLUE, w=160)
    label(s, 641, 488, '位置 → 角度', size=14, color=MID, w=160)
    notes(s, [
        '本页是整个 M1 的核心概念页，务必讲透"两个空间"的差别。',
        '① 左盘：关节空间。描述方式＝一串角度（q1, q2, …, q6）。它的"坐标轴"是角度，单位是度或弧度。',
        '② 右盘：笛卡尔空间（操作空间）。描述方式＝末端的位置 (x, y, z) 与姿态。坐标轴就是普通的直角坐标。',
        '③ 中间的箭头说明两者的关系：这是同一台机械臂的两种描述方式，可以互相换算，但换算方向难度完全不同。',
        '重点提醒：右盘的红色点才是我们"任务层面"关心的东西（我要抓的那个杯子在哪），',
        '但机器人硬件只能直接控制左盘的角度。所以两个空间之间的换算是整门课的主线。',
        '常见误区：学生容易以为 (x, y) 就能定死手的位置。其实平面上还要朝向，空间中还要姿态（3 个角度），',
        '一共 6 个自由度——这正好解释了为什么常见工业臂是 6 轴。',
        '板书建议：在左盘写 "6 个数 = 角度"，右盘写 "6 个数 = 3 位置 + 3 姿态"。',
    ])


def p06():
    s = slide()
    hdr(s, '两个方向，难度完全不同', 'M1 · 第 1 讲', 6)
    rect(s, 60, 200, 420, 150, fill=LIGHT2, linec=LIGHT, lw=1.6,
         shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.12)
    rect(s, 800, 200, 420, 150, fill=LIGHT2, linec=LIGHT, lw=1.6,
         shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.12)
    text(s, 60, 232, 420, 40, '关节空间', size=24, color=NAVY, bold=True,
         align=PP_ALIGN.CENTER, spacing=1.0)
    text(s, 60, 280, 420, 40, '(q1, q2, …, q6)', size=19, color=SUB, font=EN,
         align=PP_ALIGN.CENTER, spacing=1.0)
    text(s, 800, 232, 420, 40, '笛卡尔空间', size=24, color=NAVY, bold=True,
         align=PP_ALIGN.CENTER, spacing=1.0)
    text(s, 800, 280, 420, 40, '(x, y, z)', size=19, color=SUB, font=EN,
         align=PP_ALIGN.CENTER, spacing=1.0)

    arrow(s, 486, 232, 794, 232, color=BLUE, w=3.4, hs='lg')
    arrow(s, 794, 320, 486, 320, color=RED, w=3.4, hs='lg')
    label(s, 640, 202, '正运动学  FK', size=20, color=BLUE, bold=True, w=260)
    label(s, 640, 352, '逆运动学  IK', size=20, color=RED, bold=True, w=260)
    label(s, 640, 268, '结果唯一', size=15, color=SUB, w=200)
    label(s, 640, 388, '结果常常不止一个', size=15, color=SUB, w=260)

    text(s, 60, 452, 1160, 40, '已知角度 → 算位置', size=22, color=BLUE, font=EN,
         align=PP_ALIGN.CENTER, spacing=1.0)
    text(s, 60, 512, 1160, 40, '已知位置 → 算角度', size=22, color=RED,
         align=PP_ALIGN.CENTER, spacing=1.0)
    line(s, 480, 500, 800, 500, color=LIGHT, w=1.4)
    notes(s, [
        '上箭头 FK（正运动学）：给一串关节角，算出末端在哪。这是"由内向外"，结果是唯一的。',
        '把每个关节的旋转效果一层层叠起来就行——M3 就是教你叠这件事，也是本课最"可算"的部分。',
        '下箭头 IK（逆运动学）：给末端目标位置，反推关节角。这是"由外向内"。',
        '为什么 IK 难？三个原因：',
        '① 可能无解——目标点根本不在可达范围里（M3 会算出这个范围长什么样）。',
        '② 可能多解——同样一个点，"肘向上"和"肘向下"两种姿态都能到；',
        '③ 可能有无数解——7 自由度的宇树 R1 就是这种"冗余"结构，多一个自由度就多一族解。',
        '结论口播："FK 是套公式，IK 是解方程。"这门课的前三讲先把 FK 彻底吃透，IK 留到 M4。',
        '可以现场演示：在仿真里把末端拖到某个点，让学生看关节角在两个解之间跳变。',
    ])


def p07():
    s = slide()
    hdr(s, '两台机器人的“臂展”', 'M1 · 第 1 讲', 7)
    bx0, bx1, by = 200, 1178, 510

    def mx(v):
        return bx0 + (v / 1.10) * (bx1 - bx0)

    # —— UR5 ——
    pic_chain(s, 92, 272, k=0.72, c=BLUE, c2=MID)
    label(s, 92, 344, 'UR5', size=17, color=BLUE, bold=True, font=EN, w=100)
    x1, x2 = mx(0.036), mx(1.028)
    rect(s, x1, 300, x2 - x1, 44, fill=BLUE, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
         radius=0.25)
    line(s, x1, 286, x1, 358, color=BLUE, w=1.6)
    line(s, x2, 286, x2, 358, color=BLUE, w=1.6)
    label(s, (x1 + x2) / 2, 268, '0.036  →  1.028 m', size=17, color=BLUE,
          font=EN, bold=True, w=300)

    # —— R1 ——
    pic_chain(s, 92, 396, k=0.58, c=MID, c2=MID)
    label(s, 92, 452, 'R1', size=17, color=MID, bold=True, font=EN, w=100)
    y1, y2 = mx(0.013), mx(0.542)
    rect(s, y1, 380, y2 - y1, 40, fill=MID, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
         radius=0.28)
    line(s, y1, 368, y1, 424, color=MID, w=1.4)
    line(s, y2, 368, y2, 424, color=MID, w=1.4)
    text(s, y2 + 18, 384, 320, 32, '0.013 → 0.542 m', size=15, color=MID,
         font=EN, bold=True, spacing=1.0)
    line(s, y2, 288, y2, 432, color=RED, w=1.4, dash=MSO_LINE_DASH_STYLE.DASH)
    label(s, y2, 176, 'R1 的极限', size=14, color=RED, w=140)

    # —— 数轴 ——
    arrow(s, bx0 - 44, by, bx1 + 34, by, color=SUB, w=1.8, hs='sm')
    for i in range(6):
        v = i * 0.2
        x = mx(v)
        line(s, x, by, x, by + 10, color=MUTED, w=1.4)
        label(s, x, by + 30, ('%.1f' % v) if i else '0', size=13, color=MUTED,
              font=EN, w=60)
    label(s, (bx0 + bx1) / 2, by + 62, '末端到原点的距离 r / m', size=14,
          color=SUB, w=340)
    text(s, 700, 142, 540, 30, 'R1 的可达范围完全落在 UR5 之内', size=15,
         color=SUB, spacing=1.0)
    notes(s, [
        '本页用真实参数说话，全部数据来自仓库里的 URDF / DH 文件，可复现。',
        '① UR5：末端到基座原点的可达距离 0.036 m – 1.028 m，臂展约 1 米，是典型的中型工业臂。',
        '② 宇树 R1：可达距离 0.013 m – 0.542 m，只有 UR5 的一半左右，属于轻量桌面级。',
        '③ 关键读图结论：R1 的区间【完全被】UR5 的区间包住——不是"差不多"，是严格包含关系。',
        '这意味着 UR5 能到的每一个距离，R1 理论上都能到；反之不成立。',
        '教学takeaway：选型时"臂展"是第一硬约束。如果任务点距离底座 0.8 m，R1 直接出局。',
        '追问一句：为什么近处反而"够不到"？因为第一段连杆自己就有 0.30 m，机械臂收不回原点。',
        '这个"空心"会在 M3 变成一个圆环，学生到时候会有"原来如此"的感觉。',
        'UR5 零位时末端在 (0.817, 0.191, −0.005) m，距底座 0.839 m；R1 零位末端距底座 0.196 m。',
        '这两个数可以用来验算：都在各自的 [min, max] 区间内。',
    ])


def p08():
    s = section('02', '单位圆与“角度坐标”',
                ['sin / cos 就是坐标', '弧度制', 'atan2'], [214, 106, 106], 8, _s2_pict)
    notes(s, [
        '第 2 讲驱动问题：一个角度，凭什么能当成坐标用？',
        '学生的痛点通常不是"不会算 sin"，而是"不知道 sin 是什么"——他们把 sin 记成三角形里的对边比斜边，',
        '一旦脱离直角三角形就懵了。本讲要把它重新定义成"圆上一点的纵坐标"。',
        '路线：复活单位圆（P9）→ 把半径从 1 放大到 L（P10）→ 补上弧度制（P11）→ 解决反解象限问题（P12）。',
        '本讲只有一课时，节奏要快，但单位圆这张图必须让学生自己画一遍。',
    ])


def p09():
    s = slide(NAVY)
    hdr(s, '单位圆就是“坐标表”', 'M2 · 第 2 讲', 9, dark=True)
    ox, oy, R = 620, 372, 230
    line(s, ox - 330, oy, ox + 340, oy, color=ONDK3, w=1.4,
         dash=MSO_LINE_DASH_STYLE.DASH)
    line(s, ox, oy + 250, ox, oy - 260, color=ONDK3, w=1.4,
         dash=MSO_LINE_DASH_STYLE.DASH)
    oval(s, ox, oy, R, linec=MID, lw=3.0)
    label(s, ox - 344, oy - 22, '−1', size=14, color=ONDK3, font=EN, w=56)
    label(s, ox + 350, oy - 22, '+1', size=14, color=ONDK3, font=EN, w=56)
    ang = 52
    tx = ox + R * math.cos(math.radians(ang))
    ty = oy - R * math.sin(math.radians(ang))
    line(s, ox, oy, tx, ty, color=WHITE, w=4.0)
    line(s, tx, ty, tx, oy, color=ONDK2, w=2.0, dash=MSO_LINE_DASH_STYLE.DASH)
    line(s, tx, ty, ox, ty, color=ONDK2, w=2.0, dash=MSO_LINE_DASH_STYLE.DASH)
    arc(s, ox, oy, 82, 0, ang, color=ONDK2, w=2.4)
    oval(s, ox, oy, 6, fill=WHITE)
    oval(s, tx, ty, 11, fill=WHITE)
    label(s, ox + 44, oy - 48, 'θ', size=24, color=ONDK2, font=EN, w=60)
    label(s, tx + 152, ty + 16, 'P (cos θ, sin θ)', size=17, color=WHITE, font=EN, w=280)
    label(s, (tx + ox) / 2, oy + 28, 'cos θ', size=17, color=ONDK2, font=EN, w=140)
    label(s, ox - 68, (ty + oy) / 2, 'sin θ', size=17, color=ONDK2, font=EN, w=140)
    text(s, 60, 596, 1160, 44, 'x = cos θ      y = sin θ', size=30, color=WHITE,
         font=EN, align=PP_ALIGN.CENTER, spacing=1.0)
    notes(s, [
        '先在黑板上画一个半径 1 的圆，圆心在原点。这就是单位圆。',
        '① 从原点出发、与 x 轴正方向成 θ 角的那条半径，它的终点必然落在圆上。',
        '② 这个终点的横坐标就是 cos θ，纵坐标就是 sin θ。',
        '一句话定义：cos 是"水平投影的长度"，sin 是"垂直投影的长度"。',
        '关键突破：这样定义之后，θ 可以取任何值——大于 90° 也行，负角也行，超过 360° 也行。',
        '直角三角形那套定义做不到这一点，单位圆可以。这是学生认知升级的关键一步。',
        '提醒符号规律：θ 在第二象限时 cos 为负（横坐标是负的），但 sin 仍为正。',
        '可以让学生当场做 3 个快速判断：θ=90° 时坐标是多少？（0, 1）θ=180°？（−1, 0）θ=270°？（0, −1）',
        '这四个点要背到条件反射，M2 的 atan2 和 M3 的圆环都会用到。',
        '板书金句："单位圆不是图形，是一张对照表：角度 → 坐标。"',
    ])


def p10():
    s = slide()
    hdr(s, '把半径从 1 放大到 L', 'M2 · 第 2 讲', 10)
    c1x, c1y, r1 = 330, 372, 104
    pic_unit(s, c1x, c1y, r1, c=BLUE, ang=52, lw=2.6)
    label(s, c1x, c1y + 146, '半径 1', size=15, color=BLUE, w=160)
    label(s, c1x + 62, c1y - 84, '(cos θ, sin θ)', size=14, color=SUB, font=EN, w=220)

    arrow(s, 500, 372, 640, 372, color=BLUE, w=3.2, hs='lg')
    label(s, 570, 342, '× L', size=22, color=BLUE, bold=True, font=EN, w=110)

    c2x, c2y, r2 = 930, 372, 230
    oval(s, c2x, c2y, r2, linec=MID, lw=3.0)
    arrow(s, c2x - 270, c2y, c2x + 280, c2y, color=MUTED, w=1.4, hs='sm')
    arrow(s, c2x, c2y + 250, c2x, c2y - 260, color=MUTED, w=1.4, hs='sm')
    ang = 52
    tx = c2x + r2 * math.cos(math.radians(ang))
    ty = c2y - r2 * math.sin(math.radians(ang))
    line(s, c2x, c2y, tx, ty, color=BLUE, w=4.2)
    line(s, tx, ty, tx, c2y, color=MID, w=1.8, dash=MSO_LINE_DASH_STYLE.DASH)
    line(s, tx, ty, c2x, ty, color=MID, w=1.8, dash=MSO_LINE_DASH_STYLE.DASH)
    arc(s, c2x, c2y, 78, 0, ang, color=MID, w=2.4)
    oval(s, c2x, c2y, 6, fill=BLUE)
    oval(s, tx, ty, 10, fill=BLUE)
    label(s, (c2x + tx) / 2 - 14, (c2y + ty) / 2 - 22, 'L', size=20, color=BLUE,
          font=EN, w=50)
    label(s, 1130, 150, '(L·cos θ, L·sin θ)', size=16, color=INK, font=EN, w=280)
    label(s, c2x + 46, c2y - 50, 'θ', size=22, color=MID, font=EN, w=56)
    text(s, 60, 596, 1160, 44, 'x = L · cos θ      y = L · sin θ', size=28,
         color=NAVY, font=EN, align=PP_ALIGN.CENTER, spacing=1.0)
    notes(s, [
        '单位圆只是半径等于 1 的特例。真正的连杆有长度 L，所以要把它放大。',
        '① 半径从 1 变成 L，角度不变，于是点的坐标整体乘 L：横坐标 L·cos θ，纵坐标 L·sin θ。',
        '② 这就是一根长度为 L 的连杆、转过 θ 角之后，末端的位置。',
        '这一步是整门课的"发动机"：M3 的 2R、3R 公式，本质上就是把好几个这样的向量加起来。',
        '务必强调：L 是"连杆长度"，是机械设计定死的常数，学生不需要关心它怎么来的。',
        '类比提示：把连杆想成一根指针，θ 是它转过的角度，L 是它的长度。',
        '常见错误：把 L 乘在角度上，写成 cos(L·θ)。可以当场用反例打破——L 是长度，单位是米，不能进 cos。',
        '课堂小练习：L=0.30 m，θ=60°，让学生口算末端坐标（0.15, 0.2598）。',
        '数值验证：仓库 demos/demo_single_link.py 里 L=0.3，可直接跑出来对照。',
    ])


def p11():
    s = slide()
    hdr(s, '角度制与弧度制', 'M2 · 第 2 讲', 11)
    ox, oy, R = 640, 540, 330
    arc(s, ox, oy, R, 0, 180, color=MID, w=3.0)
    line(s, ox - 380, oy, ox + 380, oy, color=MUTED, w=1.4)
    ticks = [(0, '0°', '0'), (30, '30°', 'π/6'), (45, '45°', 'π/4'),
             (60, '60°', 'π/3'), (90, '90°', 'π/2'), (120, '120°', '2π/3'),
             (135, '135°', '3π/4'), (150, '150°', '5π/6'), (180, '180°', 'π')]
    for a, dg, rd in ticks:
        c = math.cos(math.radians(a))
        sn = math.sin(math.radians(a))
        line(s, ox + (R - 12) * c, oy - (R - 12) * sn,
             ox + (R + 12) * c, oy - (R + 12) * sn, color=MID, w=2.0)
        if a not in (0, 180):
            line(s, ox, oy, ox + (R - 12) * c, oy - (R - 12) * sn,
                 color=LIGHT, w=1.2)
        dx = ox + (R + 46) * c
        dy = oy - (R + 46) * sn
        label(s, dx, dy, dg, size=15, color=INK, font=EN, w=90)
        rx = ox + (R - 66) * c
        ry = oy - (R - 66) * sn
        label(s, rx, ry, rd, size=15, color=BLUE, font=EN, w=90)
    arc(s, ox, oy, R - 108, 0, 180, color=RED, w=2.4)
    label(s, ox, oy - R + 42, '半径 = 1 个半径长', size=15, color=RED, w=260)
    text(s, 40, 108, 1160, 40, '半圆上的弧长，就是弧度数', size=20, color=NAVY,
         align=PP_ALIGN.CENTER, spacing=1.0)
    text(s, 40, 592, 1160, 40, 'θ(弧度) = θ(度) × π / 180', size=24, color=NAVY,
         font=EN, align=PP_ALIGN.CENTER, spacing=1.0)
    notes(s, [
        '一句话说清弧度的定义：在单位圆上，一段弧的长度就等于它所对圆心角的弧度数。',
        '所以"绕半圈"的弧长是 π，对应 180°；"绕四分之一圈"的弧长是 π/2，对应 90°。',
        '为什么编程里要用弧度？因为 sin、cos 的展开式、导数公式在弧度制下才最简洁（sin 的导数是 cos），',
        '计算机内部一律用弧度，Python 的 math.sin(x) 里的 x 必须是弧度，给度数会得到完全错误的结果。',
        '这是学生写代码时最高频的 bug：忘了 math.radians()。本讲之后每次写代码都要检查这一点。',
        '换算口诀：度 → 弧度乘 π/180；弧度 → 度乘 180/π。',
        '课堂快问快答：45° 是多少弧度？90°？180°？360°？',
        '记忆锚点：π/6=30°、π/4=45°、π/3=60°、π/2=90°，这四个要背。',
        '仓库里的 armblocks/blocks/trig.py 有 deg2rad / rad2deg 两个现成函数，M2 的填空会用到。',
    ])


def p12():
    s = slide()
    hdr(s, '反解角度为什么要用 atan2', 'M2 · 第 2 讲', 12)
    ox, oy, L = 560, 372, 196
    line(s, ox - 268, oy, ox + 274, oy, color=MUTED, w=1.4)
    line(s, ox, oy + 260, ox, oy - 262, color=MUTED, w=1.4)
    label(s, ox + 296, oy - 20, 'x', size=16, color=MUTED, font=EN, w=44)
    label(s, ox - 4, oy - 286, 'y', size=16, color=MUTED, font=EN, w=44)
    quad = [(45, '45°', (1, 1), BLUE), (135, '135°', (-1, 1), BLUE),
            (225, '−135°', (-1, -1), RED), (315, '−45°', (1, -1), BLUE)]
    for a, lab, (sx, sy), col in quad:
        tx = ox + L * abs(math.cos(math.radians(a))) * sx
        ty = oy - L * abs(math.sin(math.radians(a))) * sy
        arrow(s, ox, oy, tx, ty, color=col, w=2.4, hs='sm')
        oval(s, tx, ty, 8, fill=col)
        label(s, tx + (34 if sx > 0 else -34), ty - 22, lab, size=16, color=col,
              font=EN, bold=True, w=110)
    line(s, ox, oy, ox - L * 0.707, oy + L * 0.707, color=RED, w=2.6)
    line(s, ox - L * 0.707, oy - L * 0.707, ox - L * 0.707, oy + L * 0.707,
         color=RED, w=1.4, dash=MSO_LINE_DASH_STYLE.DASH)
    text(s, 250, 574, 300, 60, ['arctan 把它俩', '看成同一个角'], size=14,
         color=RED, align=PP_ALIGN.CENTER, spacing=1.3)
    arrow(s, 476, 582, 424, 470, color=RED, w=1.6, hs='sm')
    line(s, 916, 172, 916, 560, color=LIGHT, w=1.4)
    text(s, 960, 214, 300, 60, 'atan2(y, x)', size=30, color=BLUE, bold=True, font=EN)
    text(s, 960, 292, 300, 34, '能分辨四个象限', size=19, color=SUB)
    for i, (a, lab, _q, col) in enumerate(quad):
        yy = 356 + i * 52
        rect(s, 962, yy - 6, 22, 22, fill=col)
        text(s, 998, yy - 8, 200, 30, '→  ' + lab, size=17, color=INK, font=EN)
    notes(s, [
        '问题从哪来：M3 反解要"已知末端坐标 (x, y)，求关节角 θ"，这一步就是反三角函数。',
        '① arctan(y/x) 的返回值只有 (−90°, 90°)，它只看得见右半平面。',
        '② 所以 (1, 1) 和 (−1, −1) 这两个点，arctan 给的都是 45°，无法区分。',
        '③ atan2(y, x) 同时接收 x 和 y 两个参数，因此知道点在哪个象限，返回值范围是 (−180°, 180°]。',
        '结论要背下来：编程里反解角度，一律用 atan2，不要用 arctan。',
        '注意参数顺序：atan2 是 (y, x)，不是 (x, y)。这是第二个高频 bug。',
        '顺便提醒：atan2 返回的是弧度，要显示成度数记得再乘 180/π。',
        '课堂验证：让学生算 atan2(1, −1)。答案是 135°（即 3π/4），而 arctan(1/−1) 给的是 −45°。',
        '仓库 armblocks/blocks/trig.py 的 xy_to_polar 就是留空让学生填 atan2 的地方。',
        '易错点补充：当 x=0 时 arctan 会出现除以零，atan2 没有这个问题——这也是工程上必须用它的一条理由。',
    ])


def p13():
    s = section('03', '平面正运动学：1R → 2R → 3R',
                ['角度累加', '向量相加', '可达圆环'], [112, 112, 112], 13, _s3_pict)
    notes(s, [
        '第 3 讲是前三讲的落点，也是计算量最大的一讲，共两课时。',
        '"1R / 2R / 3R" 的意思是：只有 1 个关节、2 个关节、3 个关节的平面机械臂。',
        '先把最简单的 1R 写对，再加一个关节变成 2R，再加一个变成 3R，然后总结出通式——这是本课的推导方法。',
        '本讲会产出三样东西：① 角度累加公式；② 一个可运行的 fk_2r 函数；③ 对"可达空间为什么是圆环"的理解。',
        '课末做一次完整的"预测—验证"：先猜末端落在哪，再跑代码看有没有猜对。',
    ])


def p14():
    s = slide()
    hdr(s, 'θ2 是从哪里量的？', 'M3 · 第 3 讲', 14)
    ox, oy = 300, 520
    L1, L2 = 240, 190
    a1, a2 = 58, 24
    p1 = (ox + L1 * math.cos(math.radians(a1)), oy - L1 * math.sin(math.radians(a1)))
    p2 = (p1[0] + L2 * math.cos(math.radians(a2)),
          p1[1] - L2 * math.sin(math.radians(a2)))
    line(s, ox, oy, p1[0], p1[1], color=BLUE, w=11)
    line(s, p1[0], p1[1], p2[0], p2[1], color=MID, w=9)
    ex = ox + (L1 + L2) * math.cos(math.radians(a1))
    ey = oy - (L1 + L2) * math.sin(math.radians(a1))
    line(s, p1[0], p1[1], ex, ey, color=MUTED, w=1.8, dash=MSO_LINE_DASH_STYLE.DASH)
    line(s, ox - 40, oy, ox + 330, oy, color=LIGHT, w=1.4)
    arc(s, ox, oy, 88, 0, a1, color=BLUE, w=2.2)
    arc(s, p1[0], p1[1], 74, a2, a1, color=RED, w=2.4)
    arc(s, ox, oy, 150, 0, a1 + a2, color=RED, w=2.0, dash=MSO_LINE_DASH_STYLE.DASH)
    oval(s, ox, oy, 11, fill=BLUE)
    oval(s, p1[0], p1[1], 10, fill=BLUE, linec=WHITE, lw=2.0)
    oval(s, p2[0], p2[1], 10, fill=MID, linec=WHITE, lw=2.0)
    label(s, ox + 104, oy - 26, 'θ1', size=20, color=BLUE, font=EN, w=70)
    label(s, p1[0] + 18, p1[1] - 52, 'θ2', size=20, color=RED, font=EN, w=70)
    label(s, ox + 178, oy - 88, 'θ1 + θ2', size=19, color=RED, font=EN, w=140)

    rect(s, 700, 128, 540, 452, fill=LIGHT2, linec=LIGHT, lw=1.4)
    text(s, 728, 152, 480, 34, '第二段连杆的“绝对角度”', size=20, color=NAVY, bold=True)
    line(s, 728, 198, 1212, 198, color=LIGHT, w=1.4)
    bx, by = 832, 500
    b1 = (bx + 150 * math.cos(math.radians(58)), by - 150 * math.sin(math.radians(58)))
    b2 = (b1[0] + 120 * math.cos(math.radians(58 + 24)),
          b1[1] - 120 * math.sin(math.radians(58 + 24)))
    line(s, bx, by, b1[0], b1[1], color=BLUE, w=8)
    line(s, b1[0], b1[1], b2[0], b2[1], color=MID, w=7)
    arc(s, bx, by, 70, 0, 58, color=BLUE, w=1.8)
    arc(s, bx, by, 118, 0, 82, color=RED, w=1.8, dash=MSO_LINE_DASH_STYLE.DASH)
    oval(s, bx, by, 9, fill=BLUE)
    oval(s, b1[0], b1[1], 8, fill=BLUE, linec=WHITE, lw=1.8)
    oval(s, b2[0], b2[1], 8, fill=MID, linec=WHITE, lw=1.8)
    label(s, bx + 88, by - 22, 'θ1', size=16, color=BLUE, font=EN, w=60)
    label(s, bx + 156, by - 74, 'θ1 + θ2', size=16, color=RED, font=EN, w=130)
    text(s, 728, 548, 480, 34, '求 cos / sin，用的是 θ1 + θ2', size=16,
         color=SUB, align=PP_ALIGN.CENTER)
    notes(s, [
        '这是 M3 最容易错的地方，必须单独用一页讲。',
        '问题：第二段连杆（L2）的转角 θ2 是从哪里量的？',
        '答：θ2 是"相对转角"，从第一段连杆的延长线开始量，不是从 x 轴开始量。',
        '为什么？因为第二段的电机装在第一节连杆的末端，它跟着第一节一起转。',
        '所以第二个关节的"世界角"= θ1 + θ2。',
        '这就是"角度累加"的来源，也是 M3 公式里为什么会出现 (θ1 + θ2) 的原因。',
        '右边的对照图专门用来防止混淆：蓝色弧是从 x 轴量的 θ1，红色虚线弧是从 x 轴量的 θ1+θ2，',
        '而 θ2 只是这两者之差。',
        '常见错误：直接把 θ2 当成世界角写进公式，结果仿真里的手臂永远对不上。',
        '可以让这个错误现场发生一次：用错公式跑一遍，让学生看到手臂歪掉的样子，印象会非常深。',
        '推而广之：第 n 段连杆的世界角 = θ1 + θ2 + … + θn。M3 的通式就建立在这句话上。',
    ])


def p15():
    s = slide(NAVY)
    hdr(s, '把两段位移加起来', 'M3 · 第 3 讲', 15, dark=True)
    ox, oy = 330, 528
    L1, L2, a1, a2 = 268, 208, 55, 22
    p1 = (ox + L1 * math.cos(math.radians(a1)), oy - L1 * math.sin(math.radians(a1)))
    p2 = (p1[0] + L2 * math.cos(math.radians(a2)),
          p1[1] - L2 * math.sin(math.radians(a2)))
    line(s, ox - 60, oy, ox + 470, oy, color=ONDK3, w=1.2,
         dash=MSO_LINE_DASH_STYLE.DASH)
    line(s, ox, oy + 60, ox, oy - 380, color=ONDK3, w=1.2,
         dash=MSO_LINE_DASH_STYLE.DASH)
    polyline(s, [(ox, oy), p1, p2], color=WHITE, w=2.6,
             dash=MSO_LINE_DASH_STYLE.DASH)
    arrow(s, ox, oy, p1[0], p1[1], color=WHITE, w=9, hs='lg')
    arrow(s, p1[0], p1[1], p2[0], p2[1], color=MID, w=8, hs='lg')
    arc(s, ox, oy, 84, 0, a1, color=ONDK2, w=2.2)
    arc(s, ox, oy, 152, 0, a1 + a2, color=ONDK2, w=2.0)
    oval(s, ox, oy, 11, fill=WHITE)
    oval(s, p1[0], p1[1], 10, fill=WHITE, linec=NAVY, lw=2.0)
    oval(s, p2[0], p2[1], 12, fill=RED, linec=WHITE, lw=2.4)
    label(s, ox + 108, oy - 30, 'θ1', size=20, color=ONDK2, font=EN, w=70)
    label(s, ox + 196, oy - 96, 'θ1+θ2', size=18, color=ONDK2, font=EN, w=140)
    label(s, (ox + p1[0]) / 2 - 16, (oy + p1[1]) / 2 + 18, 'a1', size=19,
          color=WHITE, font=EN, w=60)
    label(s, (p1[0] + p2[0]) / 2 + 22, (p1[1] + p2[1]) / 2 - 4, 'a2', size=19,
          color=MID, font=EN, w=60)
    label(s, p2[0] + 196, p2[1] + 12, 'r = a1 + a2', size=20, color=ONDK2,
          font=EN, w=230)
    label(s, p2[0] + 132, p2[1] - 40, '(x, y)', size=17, color=RED, font=EN, w=120)
    text(s, 700, 596, 520, 40, 'x = L1·cos θ1 + L2·cos(θ1+θ2)', size=19,
         color=WHITE, font=EN, align=PP_ALIGN.CENTER, spacing=1.0)
    notes(s, [
        '核心思想一句话：末端不是"一个点算出来的"，而是"两段位移向量加起来"。',
        '① 第一段连杆贡献一个向量 a1，长度 L1，方向 θ1。',
        '② 第二段连杆贡献一个向量 a2，长度 L2，方向是它的世界角 θ1+θ2（上一页刚讲完）。',
        '③ 末端的坐标就是这两个向量的和：r = a1 + a2。',
        '写成坐标形式，就是分别把 x 分量和 y 分量相加：',
        'x = L1·cos θ1 + L2·cos(θ1+θ2)',
        'y = L1·sin θ1 + L2·sin(θ1+θ2)',
        '这就是平面 2R 机械臂的正运动学公式——本课最重要的一个结果。',
        '强调"向量相加"这个词：学生在物理里学过力的合成、位移的合成，这里是同一件事。',
        '三角形法则的直观：从底座出发，沿 a1 走一段，再沿 a2 走一段，终点就是末端。中间那个拐点就是"肘"。',
        '数值印证：L1=0.30、L2=0.22、θ1=35°、θ2=60° 时，末端算出来是 (0.2266, 0.3912)。',
        '这个组数让学生自己按计算器验一遍，比老师演示更有效。',
    ])


def p16():
    s = slide()
    hdr(s, '1R → 2R → 3R：一条通式', 'M3 · 第 3 讲', 16)
    panels = [
        (40, 210, 366, 300, 1, 'x = L·cos θ'),
        (452, 168, 366, 342, 2, 'x = L1·cos θ1\n+ L2·cos(θ1+θ2)'),
        (864, 126, 366, 384, 3, 'x = L1·cos θ1 + L2·cos(θ1+θ2)\n+ L3·cos(θ1+θ2+θ3)'),
    ]
    for (px, py, pw, ph, n, fm) in panels:
        rect(s, px, py, pw, ph, fill=LIGHT2, linec=LIGHT, lw=1.4)
        bx = px + pw / 2.0
        by = py + ph - 96
        angs = [62, 22, -18][:n]
        seg = [104, 88, 74][:n]
        cur = (bx - 40, by)
        line(s, px + 24, by, px + pw - 24, by, color=LIGHT, w=1.2)
        for i in range(n):
            nx = cur[0] + seg[i] * math.cos(math.radians(angs[i]))
            ny = cur[1] - seg[i] * math.sin(math.radians(angs[i]))
            line(s, cur[0], cur[1], nx, ny, color=BLUE if i % 2 == 0 else MID,
                 w=8 if i == 0 else 6)
            oval(s, cur[0], cur[1], 7, fill=BLUE)
            cur = (nx, ny)
        oval(s, cur[0], cur[1], 8, fill=RED)
        text(s, px + 24, py + ph - 76, pw - 48, 60, fm.split('\n'),
             size=13 if n == 3 else 15,
             color=NAVY, font=EN, align=PP_ALIGN.CENTER, spacing=1.45)
        label(s, px + 52, py + 34, '%dR' % n, size=26, color=BLUE, bold=True,
              font=EN, w=90)
    text(s, 40, 546, 1200, 40, 'x = Σ Li · cos(θ1 + … + θi)', size=28, color=NAVY,
         font=EN, align=PP_ALIGN.CENTER, spacing=1.0)
    notes(s, [
        '这一页展示"从特例到通式"的推导路径，学生要跟着走一遍。',
        '① 1R：只有一段连杆，末端就在这个圆的边上，x = L·cos θ。这就是 M2 的结果。',
        '② 2R：加上第二段，用上一页的向量相加，得到两项之和。',
        '③ 3R：再加一段，注意第三段的世界角是 θ1+θ2+θ3，所以第三项里是三个角相加。',
        '规律立刻显现：第 i 段连杆贡献的项是 Li·cos(θ1+θ2+…+θi)。',
        '通式：x = Σ Li·cos(θ1+…+θi)，y 方向同理把 cos 换成 sin。',
        '强调：这不是"背公式"，而是"听规律"。n 段连杆就写 n 项，形式完全一致。',
        '代码实现时这条通式就是一个 for 循环：累加 θ，累加 Li·cos(累加和)。',
        '空间臂（UR5、R1）之所以复杂，是因为多了"绕竖直轴转"和"手腕朝向"这些维度，',
        '但每一维的思路和这里完全一样，只是把平面三角换成三维旋转矩阵。',
        '课堂练习：让学生把 3R 的 y 方向通式也写出来，检验是否真的理解。',
    ])


def p17():
    s = slide()
    hdr(s, '这就是正运动学公式', 'M3 · 第 3 讲', 17)
    # —— 公式卡 ——
    rect(s, 40, 108, 620, 236, fill=LIGHT2, linec=LIGHT, lw=1.4)
    text(s, 68, 132, 564, 44, 'x = L1·cos θ1 + L2·cos(θ1+θ2)',
         size=23, color=NAVY, font=EN, spacing=1.0)
    text(s, 68, 190, 564, 44, 'y = L1·sin θ1 + L2·sin(θ1+θ2)',
         size=23, color=NAVY, font=EN, spacing=1.0)
    line(s, 68, 250, 632, 250, color=LIGHT, w=1.4)
    text(s, 68, 268, 564, 40, '+ L3·cos(θ1+θ2+θ3) …', size=18, color=SUB,
         font=EN, spacing=1.0)

    # —— 右侧标注图：角度逐段累加 ——
    text(s, 940, 112, 300, 28, '角度逐段累加', size=15, color=SUB,
         align=PP_ALIGN.RIGHT, spacing=1.0)
    ox, oy = 790, 352
    segs, angs, acc = [104, 84, 68], [58, 30, -20], 0
    cur = (ox, oy)
    for i in range(3):
        acc += angs[i]
        nx = cur[0] + segs[i] * math.cos(math.radians(acc))
        ny = cur[1] - segs[i] * math.sin(math.radians(acc))
        line(s, cur[0], cur[1], nx, ny, color=[BLUE, MID, MID][i], w=[9, 7, 6][i])
        oval(s, cur[0], cur[1], 8, fill=BLUE)
        cur = (nx, ny)
    oval(s, cur[0], cur[1], 8, fill=RED)
    arc(s, ox, oy, 44, 0, 58, color=BLUE, w=1.6)
    arc(s, ox, oy, 72, 0, 88, color=MID, w=1.5)
    arc(s, ox, oy, 100, 0, 68, color=RED, w=1.5)
    label(s, 952, 318, 'θ1', size=15, color=BLUE, font=EN, w=60)
    label(s, 1010, 286, 'θ1+θ2', size=14, color=MID, font=EN, w=120)
    label(s, 1064, 250, 'θ1+θ2+θ3', size=14, color=RED, font=EN, w=150)

    # —— 底部：可手算校验表 ——
    rows = [('θ1, θ2 = 0°, 0°', '(0.5200, 0.0000)', '两段伸直，最远'),
            ('θ1, θ2 = 0°, 90°', '(0.3000, 0.2200)', '第二段向上折'),
            ('θ1, θ2 = 90°, 0°', '(0.0000, 0.5200)', '整体转过 90°'),
            ('θ1, θ2 = 90°, −90°', '(0.2200, 0.3000)', '折回，末端到 x = 0.22'),
            ('θ1, θ2 = 35°, 60°', '(0.2266, 0.3912)', '一般情形')]
    yy = 372
    for k, (a_, b_, c_) in enumerate(rows):
        if k % 2 == 0:
            rect(s, 40, yy, 1200, 46, fill=LIGHT2)
        text(s, 70, yy + 8, 320, 30, a_, size=15, color=SUB, font=EN, spacing=1.0)
        text(s, 430, yy + 8, 320, 30, b_, size=15, color=NAVY, font=EN, bold=True,
             spacing=1.0)
        text(s, 800, yy + 8, 420, 30, c_, size=14, color=MUTED, spacing=1.0)
        yy += 50
    notes(s, [
        '这一页是 M3 的结论页，也是学生要抄进笔记本的一页。',
        '平面 2R 正运动学：',
        'x = L1·cos θ1 + L2·cos(θ1+θ2)',
        'y = L1·sin θ1 + L2·sin(θ1+θ2)',
        '右侧是五组可手算的校验点，用的是课程里的真实连杆长度 L1 = 0.30 m、L2 = 0.22 m。',
        '建议让学生至少手工验算其中两组，例如：',
        '· θ1 = 0°, θ2 = 90°：第一段指向 x 正方向，末端在 (0.30, 0)；第二段从那里向上转 90°，再到 (0.30, 0.22)。',
        '· θ1 = 0°, θ2 = 180°：两段连杆完全折叠，末端距离原点 0.30 − 0.22 = 0.08 m。',
        '最后这一组数（0.08）非常关键，它就是下一张图"圆环"的内边界。',
        '左下角的示意图标注了三段累加角：θ1、θ1+θ2、θ1+θ2+θ3，用来强化"角度累加"这个主线。',
        '提醒学生：这些数全部来自仓库 demos/demo_planar_2r.py，可以自己跑一遍核对。',
    ])


def p18():
    s = slide(NAVY)
    hdr(s, '可达空间是一个圆环', 'M3 · 第 3 讲', 18, dark=True)
    # —— 主图：真实比例（内 0.08 / 外 0.52） ——
    ox, oy, R = 292, 348, 226
    inner = R * (0.08 / 0.52)
    sh = rect(s, ox - R, oy - R, 2 * R, 2 * R, fill=MID, shape=MSO_SHAPE.DONUT)
    sh.adjustments[0] = (R - inner) / (2.0 * R)
    oval(s, ox, oy, inner, fill=NAVY, linec=WHITE, lw=2.0)
    oval(s, ox, oy, R, linec=WHITE, lw=2.0)
    line(s, ox, oy, ox + R, oy, color=WHITE, w=1.4)
    label(s, ox + R * 0.55, oy - 24, '0.52', size=15, color=WHITE, font=EN, w=90)
    label(s, ox, oy + R + 32, '外圈 L1 + L2 = 0.52 m', size=14, color=ONDK2, w=380)

    # —— 放大镜提示 ——
    zoom_r = R * (0.16 / 0.52)
    zc = oval(s, ox, oy, zoom_r, linec=ONDK2, lw=1.8)
    zc.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    ix, iy, iR = 706, 348, 156
    ii = iR * (0.08 / 0.16)
    pa = (ox + zoom_r * math.cos(math.radians(35)), oy - zoom_r * math.sin(math.radians(35)))
    pb = (ox + zoom_r * math.cos(math.radians(-35)), oy - zoom_r * math.sin(math.radians(-35)))
    qa = (ix + iR * math.cos(math.radians(145)), iy - iR * math.sin(math.radians(145)))
    qb = (ix + iR * math.cos(math.radians(-145)), iy - iR * math.sin(math.radians(-145)))
    line(s, pa[0], pa[1], qa[0], qa[1], color=ONDK3, w=1.2,
         dash=MSO_LINE_DASH_STYLE.DASH)
    line(s, pb[0], pb[1], qb[0], qb[1], color=ONDK3, w=1.2,
         dash=MSO_LINE_DASH_STYLE.DASH)

    # —— 放大视图：只画 r ≤ 0.16 的范围 ——
    sh2 = rect(s, ix - iR, iy - iR, 2 * iR, 2 * iR, fill=MID,
               shape=MSO_SHAPE.DONUT)
    sh2.adjustments[0] = (iR - ii) / (2.0 * iR)
    oval(s, ix, iy, ii, fill=NAVY, linec=RED, lw=2.4)
    oval(s, ix, iy, iR, linec=WHITE, lw=2.0)
    line(s, ix, iy, ix + ii, iy, color=WHITE, w=1.6)
    pic_chain(s, ix, iy - 4, k=0.6, c=WHITE, c2=ONDK)
    label(s, ix + 46, iy + ii - 16, '0.08 m', size=14, color=RED, font=EN,
          bold=True, w=120)
    label(s, ix, iy + iR + 32, '放大：只看 r ≤ 0.16 的范围', size=14, color=ONDK2, w=440)
    label(s, ix - 172, iy + 128, '够不到', size=15, color=RED, w=110)
    arrow(s, ix - 118, iy + 112, ix - 30, iy + 34, color=RED, w=1.6, hs='sm')

    # —— 右侧数字 ——
    text(s, 934, 148, 306, 96, '0.08', size=74, color=WHITE, bold=True, font=EN,
         spacing=1.0)
    text(s, 934, 246, 306, 30, '最小可达距离 / m', size=15, color=ONDK2, spacing=1.0)
    text(s, 934, 272, 306, 30, '|L1 − L2|', size=15, color=ONDK3, font=EN,
         spacing=1.0)
    line(s, 934, 314, 1240, 314, color=NAVY2, w=1.4)
    text(s, 934, 336, 306, 96, '0.52', size=74, color=WHITE, bold=True, font=EN,
         spacing=1.0)
    text(s, 934, 434, 306, 30, '最大可达距离 / m', size=15, color=ONDK2, spacing=1.0)
    text(s, 934, 460, 306, 30, 'L1 + L2', size=15, color=ONDK3, font=EN, spacing=1.0)
    text(s, 934, 524, 306, 60, '区间内任意一点都能到达', size=16, color=ONDK,
         spacing=1.3)
    notes(s, [
        '这是 M3 最有"顿悟感"的一页。',
        '① 外边界：两段连杆完全伸直，末端离原点最远，距离 = L1 + L2 = 0.30 + 0.22 = 0.52 m。',
        '② 内边界：两段连杆完全折叠（θ2 = 180°），末端离原点最近，距离 = L1 − L2 = 0.08 m。',
        '取绝对值，因为如果 L2 > L1，内边界就是 L2 − L1。',
        '③ 结论：可达距离 r 落在 [|L1 − L2|, L1 + L2] 之间——这就是一个圆环（annulus）。',
        '所以圆内那个小洞是永远的"死区"：机械臂再灵活也够不到，因为第一段连杆自己就有 0.30 m 长。',
        '教学takeaway：这就是为什么工业机器人总要装在支架或导轨上——为了把工作空间挪到需要的地方。',
        '和 P7 呼应：UR5 的 0.036–1.028 m、R1 的 0.013–0.542 m，本质都是这个圆环公式在真实机构上的结果，',
        '只是 UR5 是多关节串联，实际的下限由机构和外形（不是简单的 L1−L2）决定，但"有一个够不到的内圈"这一条永远成立。',
        '易错点：学生常以为 θ2 = 180° 时末端在原点，其实不在，距离是 0.08 m。这点必须用公式或代码验证一次。',
    ])


def p19():
    s = slide()
    hdr(s, '扫一遍 θ2，看末端怎么走', 'M3 · 第 3 讲', 19)
    L1, L2 = 0.30, 0.22
    x0, x1, y0, y1 = 240, 1150, 580, 150
    def cx(v):
        return x0 + (v / 180.0) * (x1 - x0)
    def cy(r):
        return 580 - (r - 0.06) * ((580 - 150) / 0.48)
    arrow(s, x0 - 24, 580, x1 + 30, 580, color=SUB, w=1.6, hs='sm')
    arrow(s, x0, 604, x0, 130, color=SUB, w=1.6, hs='sm')
    for t in range(0, 181, 30):
        x = cx(t)
        line(s, x, 580, x, 586, color=MUTED, w=1.2)
        label(s, x, 606, '%d°' % t, size=13, color=MUTED, font=EN, w=70)
    for v in [0.1, 0.2, 0.3, 0.4, 0.5]:
        y = cy(v)
        line(s, 236, y, 240, y, color=MUTED, w=1.2)
        label(s, 199, y, '%.1f' % v, size=13, color=MUTED, font=EN, w=70)
    line(s, x0, cy(0.52), x1 + 20, cy(0.52), color=RED, w=1.4,
         dash=MSO_LINE_DASH_STYLE.DASH)
    line(s, x0, cy(0.08), x1 + 20, cy(0.08), color=RED, w=1.4,
         dash=MSO_LINE_DASH_STYLE.DASH)
    pts = []
    for i in range(0, 181, 2):
        r = math.sqrt(L1 * L1 + L2 * L2 + 2 * L1 * L2 * math.cos(math.radians(i)))
        pts.append((cx(i), cy(r)))
    polyline(s, pts, color=BLUE, w=3.6)
    oval(s, cx(0), cy(0.52), 8, fill=BLUE)
    oval(s, cx(180), cy(0.08), 8, fill=BLUE)
    label(s, cx(0) + 78, cy(0.52) - 26, '0.52 m', size=16, color=RED,
          font=EN, bold=True, w=140)
    label(s, cx(180) - 92, cy(0.08) - 42, '0.08 m', size=16, color=RED,
          font=EN, bold=True, w=140)
    label(s, 1180, 606, 'θ2', size=16, color=SUB, font=EN, w=70)
    label(s, 262, 108, 'r / m', size=15, color=SUB, font=EN, w=120)
    text(s, 760, 112, 440, 30, '曲线与 θ1 无关', size=15, color=BLUE,
         align=PP_ALIGN.RIGHT, spacing=1.0)
    notes(s, [
        '本页把公式变成一条曲线，让学生"看见"运动学。',
        '实验设置：固定 θ1，只让 θ2 从 0° 慢慢转到 180°，记录末端到原点的距离 r。',
        '公式：r = √(L1² + L2² + 2·L1·L2·cos θ2)。',
        '这是余弦定理的直接结果——两段连杆和末端到原点的连线构成一个三角形。',
        '读图要点：',
        '① θ2 = 0°（完全伸直）时 r 最大，0.52 m。',
        '② θ2 = 180°（完全折叠）时 r 最小，0.08 m。',
        '③ 在 0°→180° 这段区间里，r 是严格单调减小的，没有反复。',
        '④ 最重要的一点：这条曲线【只和 θ2 有关，与 θ1 完全无关】。',
        '把 θ1 从 0° 改成 90°，曲线一点变化都没有。因为 r 只取决于两个连杆之间的夹角。',
        '这个发现让学生第一次意识到：旋转整体坐标系不改变末端到原点的距离。',
        '课堂做法：让学生先预测曲线形状（画在纸上），再跑 demo 看结果，对比差异。',
        '可视化提示：在仿真里关掉渲染只看数值，或者把 r 直接打印出来，能更快对上曲线。',
    ])


def p20():
    s = slide()
    hdr(s, '把公式填进积木块', 'M3 · 第 3 讲', 20)
    rect(s, 40, 108, 740, 500, fill=LIGHT2, linec=LIGHT, lw=1.4)
    code = ['def fk_2r(L1, L2, q1, q2):',
            '    x = L1 * ( ? )  +  L2 * ( ? )',
            '    y = L1 * ( ? )  +  L2 * ( ? )',
            '    return x, y']
    cxx = 84
    adv = 0.55 * 18 * 4.0 / 3.0          # Consolas 单字前进宽度（px）
    for i, ln_ in enumerate(code):
        yy = 176 + i * 56
        text(s, cxx, yy, 680, 44, ln_, size=18, color=INK if i < 3 else MUTED,
             font=MONO, spacing=1.0)
    for r_i in (1, 2):
        yy = 176 + r_i * 56 - 6
        for idx in [k for k, ch in enumerate(code[r_i]) if ch == '?']:
            rect(s, cxx + idx * adv - 5, yy, 26, 36, fill=None, linec=RED,
                 lw=1.8, dash=MSO_LINE_DASH_STYLE.DASH)
    rect(s, 84, 448, 640, 1.6, fill=LIGHT)
    text(s, 84, 480, 640, 40, '4 个空 → 4 个三角函数', size=19, color=NAVY, bold=True,
         spacing=1.0)
    line(s, 800, 128, 800, 588, color=LIGHT, w=1.4)
    ox, oy = 1004, 470
    p1 = (ox + 140 * math.cos(math.radians(75)), oy - 140 * math.sin(math.radians(75)))
    p2 = (p1[0] + 118 * math.cos(math.radians(20)), p1[1] - 118 * math.sin(math.radians(20)))
    line(s, ox, oy, p1[0], p1[1], color=BLUE, w=9)
    line(s, p1[0], p1[1], p2[0], p2[1], color=MID, w=7)
    arc(s, ox, oy, 60, 0, 75, color=BLUE, w=1.8)
    arc(s, ox, oy, 98, 0, 95, color=MID, w=1.6)
    oval(s, ox, oy, 9, fill=BLUE)
    oval(s, p1[0], p1[1], 8, fill=BLUE, linec=WHITE, lw=1.8)
    oval(s, p2[0], p2[1], 8, fill=RED, linec=WHITE, lw=1.8)
    label(s, ox + 74, oy - 22, 'q1', size=16, color=BLUE, font=EN, w=60)
    label(s, ox + 118, oy - 62, 'q1+q2', size=15, color=MID, font=EN, w=120)
    label(s, ox, oy - 216, 'q1, q2 从哪量？', size=15, color=SUB, w=300)
    notes(s, [
        '这一页把公式落到代码，是"理论带动实践"的落点。',
        '任务：打开仓库里的 armblocks/blocks/planar.py，找到 fk_2r 函数，把 4 个空填上。',
        '填空提示（不要直接给答案）：',
        '· 第一个空：第一段连杆在 x 方向的投影，用哪个三角函数？自变量是 q1 还是 q1+q2？',
        '· 第二个空：第二段连杆在 x 方向的投影，注意它的角度是累加后的 q1+q2。',
        '· 第三、四个空：y 方向同理，把 cos 换成 sin。',
        '正确结果（教师用）：',
        'x = L1*cos(q1) + L2*cos(q1+q2)',
        'y = L1*sin(q1) + L2*sin(q1+q2)',
        '验收方式：跑 pytest。仓库里有一份只留 TODO 的学生版和一份参考解，',
        '用 ARMBLOCKS_IMPL=solutions pytest -q 跑参考解应该是全过；',
        '用学生版直接跑，会看到 9 个失败——这 9 个失败就是全课的填空清单。',
        '注意坑：Python 的 math.cos 只接受弧度，如果学生想用度数，必须写 math.radians(q1)。',
        '建议先让学生手写一遍，再上机填，手写和上机各算一次能显著减少"抄错的公式"。',
    ])


def p21():
    s = slide(NAVY)
    text(s, 0, 96, 1280, 70, '下一站：逆运动学', size=42, color=WHITE, bold=True,
         align=PP_ALIGN.CENTER, spacing=1.1)
    rect(s, 598, 182, 84, 4, fill=BLUE)
    rows = [('1R', 'x = L · cos θ'),
            ('2R', 'x = L1·cos θ1 + L2·cos(θ1+θ2)'),
            ('nR', 'x = Σ Li · cos(θ1 + … + θi)')]
    y = 232
    for tag, fm in rows:
        rect(s, 200, y, 880, 92, fill=None, linec=NAVY2, lw=1.4,
             shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.12)
        text(s, 228, y, 120, 92, tag, size=26, color=ONDK2, bold=True, font=EN,
             anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
        text(s, 372, y, 680, 92, fm, size=22, color=WHITE, font=EN,
             anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
        y += 110
    text(s, 0, 566, 1280, 40, '已知目标点 (x, y)，反解关节角 —— 会不会无解？会不会多解？',
         size=20, color=ONDK, align=PP_ALIGN.CENTER, spacing=1.0)
    notes(s, [
        '收尾 3 分钟。',
        '回顾前三讲：单位圆给出 x = L·cos θ、y = L·sin θ；向量相加给出 2R 公式；',
        '角度累加给出任意 nR 的通式。这三条就是正运动学的全部主干。',
        '下一讲（M4）要翻转方向：已知末端目标点 (x, y)，反解 θ1 和 θ2。',
        '预告两个悬念，让学生带着问题走：',
        '① 如果目标点落在圆环外面（比如 r = 0.8 m），会怎样？——无解。',
        '② 如果目标点在圆环里面，解是不是唯一的？——不是，"肘向上"和"肘向下"两个解。',
        '这两个问题就是逆运动学的全部难点，也是 M4 要解决的。',
        '课后作业：三份讲义的课后练习做完，并把 5 组校验点的计算过程写在实验报告里。',
    ])


# =====================================================================
def main():
    for f in [p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11,
              p12, p13, p14, p15, p16, p17, p18, p19, p20, p21]:
        f()
    out = '机械臂运动学-前三讲.pptx'
    prs.save(out)
    n = len(prs.slides._sldIdLst)
    n_notes = 0
    for sl in prs.slides:
        try:
            if sl.notes_slide.notes_text_frame.text.strip():
                n_notes += 1
        except Exception:
            pass
    print('saved %s  slides=%d  with_notes=%d' % (out, n, n_notes))


if __name__ == '__main__':
    main()
