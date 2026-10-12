# -*- coding: utf-8 -*-
"""
《机械臂运动学》前三讲 讲课 PPT 生成器
设计体系：学术风（蓝白克制 / 证据驱动）
画布：1280 x 720 px  (96 px = 1 in)
版心：页眉 0–76 / 内容区 88–640 / 页脚 656–700
"""
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


# ---------------- 调色板（全部取自学术风预设） ----------------
NAVY = RGBColor(0x0E, 0x3F, 0x8C)
BLUE = RGBColor(0x1E, 0x4F, 0xA8)
MID = RGBColor(0x3D, 0x7B, 0xD9)
LIGHT = RGBColor(0xE8, 0xEF, 0xF8)
INK = RGBColor(0x1A, 0x22, 0x30)
SUB = RGBColor(0x4A, 0x55, 0x68)
MUTED = RGBColor(0x8B, 0x97, 0xA8)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
RED = RGBColor(0xD9, 0x53, 0x4F)
ONDK = RGBColor(0xCF, 0xE0, 0xF5)

CN = 'Microsoft YaHei'
EN = 'Times New Roman'
MONO = 'Consolas'

prs = Presentation()
prs.slide_width = E(1280)
prs.slide_height = E(720)
BLANK = prs.slide_layouts[6]
TOTAL = 21

# 版心常量
CX, CW = 40, 1200          # 内容区 x / 宽
TOP, BOT = 88, 640         # 内容区上下边界


# ---------------- 基础绘制 ----------------
def slide():
    s = prs.slides.add_slide(BLANK)
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, E(1280), E(720))
    bg.fill.solid(); bg.fill.fore_color.rgb = WHITE
    bg.line.fill.background(); bg.shadow.inherit = False
    return s


def rect(s, x, y, w, h, fill=None, line=None, lw=1.0, dash=None,
         shape=MSO_SHAPE.RECTANGLE, radius=None):
    sh = s.shapes.add_shape(shape, E(x), E(y), E(w), E(h))
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid(); sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line; sh.line.width = Pt(lw)
        if dash is not None:
            sh.line.dash_style = dash
    sh.shadow.inherit = False
    if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        sh.adjustments[0] = radius
    return sh


def line(s, x1, y1, x2, y2, color=MID, w=1.5, dash=None):
    cn = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, E(x1), E(y1), E(x2), E(y2))
    cn.line.color.rgb = color
    cn.line.width = Pt(w)
    if dash is not None:
        cn.line.dash_style = dash
    return cn


def polyline(s, pts, color=BLUE, w=2.0, closed=False, fill=None):
    fb = s.shapes.build_freeform(E(pts[0][0]), E(pts[0][1]), scale=1.0)
    fb.add_line_segments([(E(px), E(py)) for px, py in pts[1:]], close=closed)
    sh = fb.convert_to_shape()
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid(); sh.fill.fore_color.rgb = fill
    if color is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = color; sh.line.width = Pt(w)
    sh.shadow.inherit = False
    return sh


def arc_pts(cx, cy, r, a0, a1, n=16):
    import math
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy - r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


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
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    if isinstance(paras, str):
        paras = [paras]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        p.space_after = Pt(space_after)
        runs = para if isinstance(para, list) else [(para, {})]
        for t, st in runs:
            r = p.add_run(); r.text = t
            r.font.size = Pt(st.get('size', size))
            r.font.bold = st.get('bold', bold)
            r.font.color.rgb = st.get('color', color)
            set_font(r, st.get('font', font))
    return tb


def header(s, title, tag, page, left=None):
    rect(s, 0, 0, 1280, 76, fill=BLUE)
    text(s, CX, 0, 880, 76, title, size=32, color=WHITE, bold=True,
         anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(s, 920, 0, 320, 76, tag, size=15, color=ONDK,
         align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(s, CX, 656, 760, 44, left or '机械臂运动学 · 前三讲（高中版）', size=14,
         color=MUTED, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(s, 760, 656, 480, 44, '%02d / %d' % (page, TOTAL), size=14, color=NAVY,
         bold=True, font=EN, align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)


def card(s, x, y, w, h, fill=None, linec=LIGHT):
    return rect(s, x, y, w, h, fill=fill, line=linec, lw=1.0)


def band(s, x, y, w, h, t, size=18, color=NAVY):
    rect(s, x, y, w, h, fill=LIGHT)
    text(s, x + 18, y, w - 36, h, t, size=size, color=color, bold=True,
         anchor=MSO_ANCHOR.MIDDLE, spacing=1.15)


def _cell_borders(cell, color='E8EFF8', w=1.0):
    tcPr = cell._tc.get_or_add_tcPr()
    for tag in ('a:lnL', 'a:lnR', 'a:lnT', 'a:lnB'):
        for old in tcPr.findall(qn(tag)):
            tcPr.remove(old)
    for tag in ('a:lnL', 'a:lnR', 'a:lnT', 'a:lnB'):
        ln = tcPr.makeelement(qn(tag), {'w': str(int(w * 12700)), 'cap': 'flat',
                                        'cmpd': 'sng', 'algn': 'ctr'})
        fill = ln.makeelement(qn('a:solidFill'), {})
        clr = fill.makeelement(qn('a:srgbClr'), {'val': color})
        fill.append(clr); ln.append(fill)
        tcPr.append(ln)


def set_cell(cell, val, size=15, color=INK, bold=False, fill=None,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE, font=CN):
    cell.vertical_anchor = anchor
    cell.margin_left = E(10); cell.margin_right = E(10)
    cell.margin_top = E(2); cell.margin_bottom = E(2)
    if fill is None:
        cell.fill.background()
    else:
        cell.fill.solid(); cell.fill.fore_color.rgb = fill
    tf = cell.text_frame
    tf.word_wrap = True
    paras = val if isinstance(val, list) else [val]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = 1.12
        runs = para if isinstance(para, list) else [(para, {})]
        for t, st in runs:
            r = p.add_run(); r.text = t
            r.font.size = Pt(st.get('size', size))
            r.font.bold = st.get('bold', bold)
            r.font.color.rgb = st.get('color', color)
            set_font(r, st.get('font', font))


def C(t, **kw):
    d = {'text': t}
    d.update(kw)
    return d


def headrow(labels, fill=NAVY, size=16):
    return [C(l, color=WHITE, bold=True, size=size, fill=fill) for l in labels]


def table(s, x, y, w, h, rows, col_w, row_h, size=15, align=PP_ALIGN.LEFT):
    nr, nc = len(rows), len(rows[0])
    gf = s.shapes.add_table(nr, nc, E(x), E(y), E(w), E(h))
    tbl = gf.table
    tbl.first_row = False
    tbl.horz_banding = False
    for j, cw in enumerate(col_w):
        tbl.columns[j].width = E(cw)
    for i, rh in enumerate(row_h):
        tbl.rows[i].height = E(rh)
    for i in range(nr):
        for j in range(nc):
            d = rows[i][j]
            set_cell(tbl.cell(i, j), d['text'],
                     size=d.get('size', size), color=d.get('color', INK),
                     bold=d.get('bold', False), fill=d.get('fill'),
                     align=d.get('align', align), font=d.get('font', CN))
            _cell_borders(tbl.cell(i, j))
    return tbl


# =====================================================================
# P1 · 封面
# =====================================================================
def p01():
    s = slide()
    rect(s, 0, 0, 1280, 720, fill=NAVY)
    text(s, 80, 152, 700, 30, '高中 · 机器人运动学入门课', size=16, color=ONDK)
    text(s, 80, 188, 700, 84, '机械臂运动学', size=58, color=WHITE, bold=True, spacing=1.05)
    text(s, 80, 282, 700, 40, 'Robotic Arm Kinematics with Trigonometry',
         size=24, color=ONDK, font=EN, spacing=1.0)
    rect(s, 80, 344, 96, 4, fill=BLUE)
    text(s, 80, 370, 700, 40, '一门课只讲一件事：机械臂的运动学，本质上就是三角函数。',
         size=21, color=WHITE, spacing=1.3)
    text(s, 80, 434, 640, 150, [
        '适用对象：高中（有三角函数基础 · 会一点 Python）',
        '课时安排：5 课时（M1 两课时 · M2 一课时 · M3 两课时）',
        '配套机型：UR5（主力）· 宇树 R1（对照）',
        '版　　本：v1.0 · 2026 秋季学期'], size=16, color=ONDK, spacing=1.6)
    line(s, 760, 540, 1240, 540, color=MID, w=2)
    line(s, 800, 540, 800, 180, color=MID, w=2)
    line(s, 800, 540, 1140, 310, color=WHITE, w=7)
    rect(s, 790, 530, 20, 20, fill=WHITE, shape=MSO_SHAPE.OVAL)
    rect(s, 1128, 298, 24, 24, fill=BLUE, line=WHITE, lw=4, shape=MSO_SHAPE.OVAL)
    polyline(s, arc_pts(800, 540, 64, 0, 34.1), color=ONDK, w=2.5)
    text(s, 872, 502, 40, 30, 'θ', size=22, color=ONDK, font=EN)
    text(s, 918, 386, 40, 30, 'L', size=20, color=WHITE, font=EN)
    text(s, 1130, 292, 130, 26, '末端 (x, y)', size=16, color=ONDK)
    text(s, 812, 552, 100, 26, '底座', size=16, color=ONDK)


# =====================================================================
# P2 · 目录
# =====================================================================
def p02():
    s = slide()
    header(s, '本讲内容', '目录', 2)
    rect(s, CX, TOP, 352, 552, fill=NAVY)
    text(s, 70, 116, 300, 26, 'CONTENTS', size=18, color=ONDK, font=EN)
    text(s, 70, 150, 300, 110, ['三章', '五课时'], size=38, color=WHITE, bold=True, spacing=1.25)
    rect(s, 70, 272, 72, 3, fill=MID)
    text(s, 70, 300, 300, 170,
         ['每一章只回答一个驱动问题。', '先建立直觉，再推公式，最后写代码验证。'],
         size=16, color=ONDK, spacing=1.75)
    text(s, 70, 580, 300, 30, '机械臂运动学 · 前三讲（高中版）', size=14, color=ONDK)
    items = [
        ('01', '机械臂怎么“知道”手在哪？', '正/逆运动学 · 关节空间与笛卡尔空间 · UR5 与宇树 R1 实物对照', 'P3–P7'),
        ('02', '单位圆与“角度坐标”', 'sin/cos 就是坐标 · 弧度制 · 反解角度为什么必须用 atan2', 'P8–P12'),
        ('03', '平面正运动学：1R → 2R → 3R', '角度累加 · 向量相加 · 可达空间为什么是一个圆环', 'P13–P20'),
    ]
    y = TOP
    for num, t, d, pg in items:
        card(s, 416, y, 824, 173)
        text(s, 428, y, 84, 173, num, size=44, color=BLUE, bold=True, font=EN,
             anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
        rect(s, 526, y + 50, 1, 72, fill=LIGHT)
        text(s, 552, y + 40, 520, 40, t, size=25, color=INK, bold=True, spacing=1.15)
        text(s, 552, y + 88, 520, 50, d, size=15, color=SUB, spacing=1.4)
        text(s, 1120, y, 100, 173, pg, size=16, color=BLUE, bold=True, font=EN,
             align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
        y += 189


# =====================================================================
# 章节扉页
# =====================================================================
def section(num, title, pills, pills_w, page, sub):
    s = slide()
    text(s, 0, 100, 1280, 232, num, size=200, color=LIGHT, bold=True, font=EN,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=0.9)
    text(s, 0, 350, 1280, 70, title, size=46, color=NAVY, bold=True,
         align=PP_ALIGN.CENTER, spacing=1.1)
    rect(s, 598, 436, 84, 4, fill=BLUE)
    total = sum(pills_w) + 18 * (len(pills) - 1)
    x = (1280 - total) / 2.0
    for t, w in zip(pills, pills_w):
        rect(s, x, 472, w, 48, fill=LIGHT, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.18)
        text(s, x, 472, w, 48, t, size=17, color=NAVY, bold=True,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
        x += w + 18
    text(s, 0, 560, 1280, 30, sub, size=16, color=MUTED, align=PP_ALIGN.CENTER)


# =====================================================================
# P4 · M1 驱动问题
# =====================================================================
def p04():
    s = slide()
    header(s, '一台只有关节的机器，凭什么知道自己的手在哪', 'M1 · 驱动问题', 4,
           '第 1 章 · M1　机械臂怎么“知道”手在哪？')
    rect(s, CX, TOP, 372, 552, fill=NAVY)
    text(s, 68, 116, 320, 26, '驱动问题', size=15, color=ONDK)
    text(s, 68, 152, 320, 210,
         '机械臂只有几个“会转的关节”，它怎么知道自己的手在空间的什么地方？',
         size=27, color=WHITE, bold=True, spacing=1.45)
    rect(s, 68, 510, 320, 110, fill=BLUE)
    text(s, 84, 526, 288, 80, ['它没有眼睛。', '唯一能读到的数字，是每个关节当前的角度。'],
         size=16, color=WHITE, spacing=1.55)
    x, w = 436, 804
    for i, (tag, title, desc) in enumerate([
            ('A', '已知角度 → 求位置', '六个关节角都读出来了，末端现在落在哪？这叫正运动学 FK。'),
            ('B', '已知位置 → 求角度', '想让手精准到达某个点，每个关节该转多少度？这叫逆运动学 IK。')]):
        y = TOP + i * 212
        card(s, x, y, w, 200)
        rect(s, x + 24, y + 46, 108, 108, fill=LIGHT)
        text(s, x + 24, y + 46, 108, 108, tag, size=34, color=NAVY, bold=True, font=EN,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
        text(s, x + 154, y + 52, 620, 40, title, size=25, color=INK, bold=True, spacing=1.1)
        text(s, x + 154, y + 102, 620, 60, desc, size=17, color=SUB, spacing=1.5)
    rect(s, x, 516, w, 124, fill=LIGHT)
    text(s, x + 24, 516, w - 48, 124,
         [[('这两个方向相反的问题，恰好是一道纯粹的', {}),
           ('三角几何题', {'bold': True, 'color': NAVY}),
           (' —— 本课程的全部内容都围绕这句话展开。', {})]],
         size=18, color=NAVY, spacing=1.5, anchor=MSO_ANCHOR.MIDDLE)


# =====================================================================
# P5 · 两个空间（HERO）
# =====================================================================
def p05():
    s = slide()
    header(s, '关节空间 ↔ 笛卡尔空间：一次双向翻译', 'M1 · 核心概念', 5,
           '第 1 章 · M1　机械臂怎么“知道”手在哪？')
    card(s, CX, TOP, 682, 552)
    rect(s, 74, 148, 248, 160, fill=LIGHT, line=BLUE, lw=2,
         shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.10)
    text(s, 74, 164, 248, 40, '关节空间', size=26, color=NAVY, bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(s, 74, 208, 248, 32, '(θ₁, θ₂, …, θ₆)', size=19, color=INK, font=EN,
         align=PP_ALIGN.CENTER, spacing=1.0)
    text(s, 74, 248, 248, 30, '电机的“命令”', size=16, color=SUB,
         align=PP_ALIGN.CENTER, spacing=1.0)
    rect(s, 448, 148, 248, 160, fill=LIGHT, line=BLUE, lw=2,
         shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.10)
    text(s, 448, 164, 248, 40, '笛卡尔空间', size=26, color=NAVY, bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(s, 448, 208, 248, 32, '(x, y, z)', size=19, color=INK, font=EN,
         align=PP_ALIGN.CENTER, spacing=1.0)
    text(s, 448, 248, 248, 30, '我们的“目标”', size=16, color=SUB,
         align=PP_ALIGN.CENTER, spacing=1.0)
    line(s, 332, 200, 438, 200, color=BLUE, w=3)
    polyline(s, [(438, 200), (418, 192), (418, 208)], color=BLUE, w=1, closed=True, fill=BLUE)
    text(s, 340, 158, 90, 28, 'FK', size=17, color=BLUE, bold=True, align=PP_ALIGN.CENTER)
    line(s, 438, 252, 332, 252, color=NAVY, w=3)
    polyline(s, [(332, 252), (352, 244), (352, 260)], color=NAVY, w=1, closed=True, fill=NAVY)
    text(s, 340, 262, 90, 28, 'IK', size=17, color=NAVY, bold=True, align=PP_ALIGN.CENTER)
    line(s, 80, 366, 682, 366, color=LIGHT, w=2)
    text(s, 80, 378, 602, 30, '两个空间之间，只有这一次双向翻译 —— 它就是运动学的全部内容',
         size=16, color=SUB, align=PP_ALIGN.CENTER)
    card(s, 80, 432, 270, 60)
    text(s, 80, 432, 270, 60, 'FK：一定有唯一答案', size=16, color=BLUE, bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    card(s, 412, 432, 270, 60)
    text(s, 412, 432, 270, 60, 'IK：可能多解 / 可能无解', size=16, color=NAVY, bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(s, 80, 508, 602, 30, 'FK 好算，IK 难算 —— 原因下一栏讲', size=15, color=MUTED,
         align=PP_ALIGN.CENTER)
    x, w = 746, 494
    card(s, x, TOP, w, 264)
    text(s, x + 22, 110, w - 44, 40, '谁在用哪个空间？', size=24, color=NAVY, bold=True, spacing=1.1)
    text(s, x + 22, 158, w - 44, 170,
         ['电机与伺服驱动器只听得懂角度；而我们人只会说“把手放到桌子上面”。',
          '运动学就是这两种语言之间的翻译官。'],
         size=17, color=SUB, spacing=1.6, space_after=6)
    rect(s, x, 364, w, 276, fill=LIGHT)
    text(s, x + 22, 388, w - 44, 40, '为什么 FK 好算、IK 难算？', size=24, color=NAVY,
         bold=True, spacing=1.1)
    text(s, x + 22, 440, w - 44, 180,
         ['FK 是“顺着走”：角度唯一决定位置。',
          'IK 是“倒着找”：同一个位置常常有好几组关节角都到得了。'],
         size=17, color=SUB, spacing=1.65, space_after=8)


# =====================================================================
# P6 · UR5 与 R1 对照
# =====================================================================
def p06():
    s = slide()
    header(s, '两台真实机械臂：一台“乖”、一台“多一只手”', 'M1 · 实物对照', 6,
           '第 1 章 · M1　机械臂怎么“知道”手在哪？')
    band(s, CX, TOP, 1200, 44, '先看数据：两台机器的规格差异，直接决定了后面公式的难度', size=17)
    rows = [
        headrow(['项目', 'UR5（主力机型）', '宇树 R1 机械臂（对照机型）']),
        [C('出身'), C('丹麦 Universal Robots · 经典工业协作臂'),
         C('杭州宇树科技 · 人形机器人 R1 的机械臂')],
        [C('自由度', fill=LIGHT), C('6', bold=True, color=BLUE), C('7', bold=True, color=BLUE)],
        [C('负载 / 自重'), C('5 kg / 18.4 kg'), C('2 kg / 5.5 kg')],
        [C('名义工作半径', fill=LIGHT), C('850 mm', fill=LIGHT), C('约 650 mm', fill=LIGHT)],
        [C('重复定位精度'), C('±0.1 mm'), C('—')],
        [C('关节轴排布', fill=LIGHT), C('6 个关节全部绕自身 z 轴（z z z z z z）', fill=LIGHT),
         C('混合（-z x y x y -x -z）', fill=LIGHT)],
        [C('末端参考系'), C('tool0（法兰中心）'), C('Link7')],
    ]
    table(s, CX, 144, 1200, 336, rows, [240, 480, 480], [42] * 8, size=15)
    card(s, CX, 492, 593, 148, fill=LIGHT, linec=None)
    text(s, 62, 510, 549, 34, '判断：自由度多一个 ≠ 更强', size=17, color=NAVY, bold=True, spacing=1.1)
    text(s, 62, 548, 549, 84,
         '多出来的那 1 个自由度，换来的是“同一个目标有多种姿势可选”，代价是解空间更难算。',
         size=15, color=SUB, spacing=1.6)
    card(s, 647, 492, 593, 148)
    text(s, 669, 510, 549, 34, '反直觉伏笔（M10 揭开）', size=17, color=NAVY, bold=True, spacing=1.1)
    text(s, 669, 548, 549, 84,
         [[('实测：UR5 最后三轴并', {}), ('不', {'bold': True}),
           ('交于一点（轴 4 与轴 6 平行，相距 94.65 mm）；R1 反而近似交于一点（偏差 5.0 mm）。', {})]],
         size=15, color=SUB, spacing=1.6)


# =====================================================================
# P7 · 零位与可达范围
# =====================================================================
def p07():
    s = slide()
    header(s, '用数字说话：零位在哪，能伸多远', 'M1 · 实测数据', 7,
           '第 1 章 · M1　机械臂怎么“知道”手在哪？')
    card(s, CX, TOP, 742, 552)
    text(s, 64, 112, 700, 30, '末端可达半径（同一根数轴，同一比例）', size=17, color=NAVY, bold=True)
    bx, by, sc = 120, 470, 540
    line(s, bx, by, bx + sc + 60, by, color=BLUE, w=2)
    for i in range(6):
        xx = bx + i * sc / 5.0
        line(s, xx, by, xx, by + 10, color=NAVY, w=2)
        text(s, xx - 30, by + 12, 60, 24, ['0', '0.2', '0.4', '0.6', '0.8', '1.0'][i],
             size=14, color=INK, font=EN, align=PP_ALIGN.CENTER)
    text(s, bx + sc + 66, by - 10, 30, 24, 'm', size=13, color=MUTED)
    ux = bx + 0.036 * sc; uw = (1.028 - 0.036) * sc
    text(s, ux, 276, 560, 26, 'UR5　　0.036 – 1.028 m', size=16, color=BLUE, bold=True)
    rect(s, ux, 306, uw, 44, fill=BLUE)
    rx = bx + 0.013 * sc; rw = (0.542 - 0.013) * sc
    text(s, rx, 370, 560, 26, '宇树 R1　　0.013 – 0.542 m', size=16, color=NAVY, bold=True)
    rect(s, rx, 400, rw, 44, fill=NAVY)
    text(s, 64, 548, 700, 30, 'R1 的整段可达范围，全部落在 UR5 的范围之内', size=15, color=MUTED)
    x, w = 806, 434
    card(s, x, TOP, w, 232)
    text(s, x + 22, 110, w - 44, 40, '零位末端位置（全部关节角 = 0）', size=18, color=NAVY,
         bold=True, spacing=1.1)
    text(s, x + 22, 156, w - 44, 110,
         ['UR5：(0.817, 0.191, −0.005) m，距底座 0.839 m',
          '宇树 R1：(0.003, −0.034, 0.193) m，距底座 0.196 m'],
         size=15, color=SUB, spacing=1.6, space_after=8)
    text(s, x + 22, 272, w - 44, 44, '数据来源：两台机器官方 URDF 模型，由 armblocks 直接实测',
         size=13, color=MUTED, spacing=1.5)
    rect(s, x, 332, w, 308, fill=LIGHT)
    text(s, x + 22, 356, w - 44, 40, '判断：臂展是选型的第一硬约束', size=18, color=NAVY,
         bold=True, spacing=1.1)
    text(s, x + 22, 404, w - 44, 220,
         ['R1 的整段可达范围都被 UR5 包在里面；UR5 能伸到接近 1 米，R1 只能到 0.54 米。',
          '所以“哪个更好”这个问题本身没意义 —— 先看你要够多远。'],
         size=15, color=SUB, spacing=1.75, space_after=10)


# =====================================================================
# P9 · M2 驱动问题
# =====================================================================
def p09():
    s = slide()
    header(s, '转一圈，末端画出什么？', 'M2 · 驱动问题', 9,
           '第 2 章 · M2　单位圆与“角度坐标”')
    rect(s, CX, TOP, 372, 552, fill=NAVY)
    text(s, 68, 116, 320, 26, '驱动问题', size=15, color=ONDK)
    text(s, 68, 152, 320, 210,
         '只知道“一根连杆多长、转了多少度”，怎么算出它末端的坐标？',
         size=27, color=WHITE, bold=True, spacing=1.45)
    rect(s, 68, 510, 320, 110, fill=BLUE)
    text(s, 84, 526, 288, 80,
         [[('要把它变成一行代码：', {})],
          [('polar_to_xy(L, theta)', {'font': EN})]],
         size=16, color=WHITE, spacing=1.55)
    x, w = 436, 804
    band(s, x, TOP, w, 42, '先猜再验：长 0.3 m 的连杆，你猜它末端在哪？')
    rows = [
        headrow(['转过的角度 θ', '0°', '90°', '180°', '270°'], size=16),
        [C('我猜末端的 (x, y)', fill=LIGHT), C('？', color=BLUE, bold=True, fill=LIGHT),
         C('？', color=BLUE, bold=True, fill=LIGHT), C('？', color=BLUE, bold=True, fill=LIGHT),
         C('？', color=BLUE, bold=True, fill=LIGHT)],
        [C('跑完代码后的真值'), C('？'), C('？'), C('？'), C('？')],
        [C('误差 / 差异原因'), C(''), C(''), C(''), C('')],
    ]
    table(s, x, 142, w, 236, rows, [194, 152, 152, 152, 154], [56, 60, 60, 60], size=16,
          align=PP_ALIGN.CENTER)
    rect(s, x, 390, w, 250, fill=LIGHT)
    text(s, x + 22, 414, w - 44, 40, '判断：轨迹是“圆”不是巧合', size=18, color=NAVY,
         bold=True, spacing=1.1)
    text(s, x + 22, 462, w - 44, 160,
         '圆的方程本身就是 sin / cos —— 记住这句话，它就是整门课的世界观起点。',
         size=17, color=SUB, spacing=1.7)


# =====================================================================
# P10 · 单位圆（HERO）
# =====================================================================
def p10():
    import math
    s = slide()
    header(s, '单位圆上，sin 和 cos 就是坐标', 'M2 · 核心概念', 10,
           '第 2 章 · M2　单位圆与“角度坐标”')
    card(s, CX, TOP, 682, 552)
    cx, cy, r = 372, 342, 165
    line(s, cx - r - 45, cy, cx + r + 55, cy, color=MID, w=2)
    line(s, cx, cy - r - 30, cx, cy + r + 45, color=MID, w=2)
    rect(s, cx - r, cy - r, 2 * r, 2 * r, fill=None, line=BLUE, lw=2.5, shape=MSO_SHAPE.OVAL)
    th = math.radians(35)
    px, py = cx + r * math.cos(th), cy - r * math.sin(th)
    line(s, cx, py, px, py, color=ONDK, w=2, dash=MSO_LINE_DASH_STYLE.DASH)
    line(s, px, py, px, cy, color=ONDK, w=2, dash=MSO_LINE_DASH_STYLE.DASH)
    line(s, cx, cy, px, py, color=NAVY, w=3.5)
    polyline(s, arc_pts(cx, cy, 58, 0, 35), color=NAVY, w=3)
    rect(s, cx - 5, cy - 5, 10, 10, fill=NAVY, shape=MSO_SHAPE.OVAL)
    rect(s, px - 8, py - 8, 16, 16, fill=NAVY, shape=MSO_SHAPE.OVAL)
    text(s, px + 14, py - 18, 300, 28, '(cos θ, sin θ)', size=18, color=NAVY, bold=True, font=EN)
    text(s, cx + 22, py + 24, 150, 28, 'cos θ', size=17, color=BLUE, font=EN)
    text(s, px + 12, py + 46, 120, 28, 'sin θ', size=17, color=BLUE, font=EN)
    text(s, cx + 64, py + 62, 40, 30, 'θ', size=19, color=NAVY, font=EN)
    text(s, cx - r, cy + 16, 120, 26, '半径 = 1', size=15, color=MUTED)
    text(s, cx - r - 58, cy - 14, 30, 26, 'x', size=16, color=MID, font=EN)
    text(s, cx - 8, cy - r - 34, 30, 26, 'y', size=16, color=MID, font=EN)
    text(s, 60, 590, 642, 26, '从 x 轴正方向逆时针转过 θ，落点就是 (cos θ, sin θ)',
         size=15, color=MUTED, align=PP_ALIGN.CENTER)
    x, w = 746, 494
    rect(s, x, TOP, w, 160, fill=LIGHT)
    text(s, x + 22, 104, w - 44, 40, '横向 = cos θ，纵向 = sin θ', size=20, color=NAVY,
         bold=True, spacing=1.1)
    text(s, x + 22, 146, w - 44, 90,
         [[('sin / cos 不是“先有三角形再算边长”，而是', {}),
           ('直接给出了一个点的位置', {'bold': True}), ('。', {})]],
         size=16, color=SUB, spacing=1.65)
    card(s, x, 260, w, 186)
    text(s, x + 22, 278, w - 44, 36, '把半径从 1 放大到 L', size=20, color=NAVY, bold=True, spacing=1.1)
    text(s, x + 22, 316, w - 44, 32, '两个坐标同乘 L，就得到连杆末端：', size=16, color=SUB, spacing=1.5)
    text(s, x + 22, 352, w - 44, 80, ['x = L · cos θ', 'y = L · sin θ'],
         size=22, color=NAVY, font=EN, spacing=1.5)
    rect(s, x, 458, w, 182, fill=NAVY)
    text(s, x + 22, 486, w - 44, 70, 'L 决定“能伸多远”，θ 决定“伸向哪边”',
         size=18, color=WHITE, bold=True, spacing=1.4)
    text(s, x + 22, 566, w - 44, 60, '这就是极坐标 (L, θ) 与直角坐标 (x, y) 之间的翻译。',
         size=15, color=ONDK, spacing=1.5)


# =====================================================================
# P11 · 弧度制
# =====================================================================
def p11():
    s = slide()
    header(s, '弧度制：数学里的“天然单位”', 'M2 · 单位换错，全盘皆错', 11,
           '第 2 章 · M2　单位圆与“角度坐标”')
    band(s, CX, TOP, 452, 42, '角度制 ↔ 弧度制')
    rows = [
        headrow(['角度制', '弧度制'], size=18),
        [C('一整圈 · 360°'), C('2π', font=EN, bold=True, color=BLUE, align=PP_ALIGN.CENTER)],
        [C('平角 · 180°', fill=LIGHT),
         C('π', font=EN, bold=True, color=BLUE, fill=LIGHT, align=PP_ALIGN.CENTER)],
        [C('直角 · 90°'), C('π / 2', font=EN, bold=True, color=BLUE, align=PP_ALIGN.CENTER)],
        [C('本讲常用 · 30°', fill=LIGHT),
         C('π / 6 ≈ 0.5236', font=EN, bold=True, color=BLUE, fill=LIGHT, align=PP_ALIGN.CENTER)],
    ]
    table(s, CX, 142, 452, 262, rows, [226, 226], [52, 52, 53, 53, 52], size=17,
          align=PP_ALIGN.CENTER)
    card(s, CX, 416, 452, 224)
    text(s, 62, 434, 408, 32, '换算口诀', size=16, color=NAVY, bold=True, spacing=1.1)
    text(s, 62, 470, 408, 150, ['弧度 = 角度 × π ÷ 180', '角度 = 弧度 × 180 ÷ π'],
         size=16, color=SUB, spacing=1.8)
    x, w = 516, 724
    card(s, x, TOP, w, 148)
    text(s, x, 104, w, 34, '写代码时的标准动作', size=18, color=NAVY, bold=True,
         align=PP_ALIGN.CENTER, spacing=1.1)
    text(s, x, 152, w, 60, 'θ_rad = θ_deg × π / 180', size=30, color=NAVY, font=EN,
         align=PP_ALIGN.CENTER, spacing=1.1)
    rect(s, x, 250, w, 216, fill=LIGHT)
    text(s, x + 22, 270, w - 44, 38, '为什么非要用弧度？', size=19, color=NAVY, bold=True, spacing=1.1)
    text(s, x + 22, 314, w - 44, 140,
         '因为只有弧度制下才有“弧长 = 半径 × 角度”这么干净的关系。角度制下要多带一个 π/180 的尾巴，所有公式都会变脏。',
         size=16, color=SUB, spacing=1.75)
    rect(s, x, 478, w, 162, fill=NAVY)
    text(s, x + 22, 498, w - 44, 38, '判断：Python 只吃弧度', size=18, color=WHITE, bold=True, spacing=1.1)
    text(s, x + 22, 540, w - 44, 90,
         ['math.sin / numpy.cos 接收的都是弧度。写代码前先换算：',
          'np.radians(30) → 0.5236'],
         size=16, color=ONDK, spacing=1.7)


# =====================================================================
# P12 · atan2
# =====================================================================
def p12():
    s = slide()
    header(s, '已知坐标求角度：为什么不能用 arctan', 'M2 · 唯一的坑', 12,
           '第 2 章 · M2　单位圆与“角度坐标”')
    band(s, CX, TOP, 1200, 42, '反解要做两步：长度用勾股定理，角度必须用 atan2')
    rows = [
        headrow(['点', 'y / x 的比值', 'arctan(y/x) 给出', '真实角度']),
        [C('(1, 1)', font=EN, align=PP_ALIGN.CENTER), C('1', font=EN, align=PP_ALIGN.CENTER),
         C('45°', font=EN, align=PP_ALIGN.CENTER),
         C('45°　正确', font=EN, bold=True, color=BLUE, align=PP_ALIGN.CENTER)],
        [C('(−1, −1)', font=EN, fill=LIGHT, align=PP_ALIGN.CENTER),
         C('1', font=EN, fill=LIGHT, align=PP_ALIGN.CENTER),
         C('45°　错误', font=EN, bold=True, color=RED, fill=LIGHT, align=PP_ALIGN.CENTER),
         C('225°（或 −135°）', font=EN, bold=True, color=RED, fill=LIGHT, align=PP_ALIGN.CENTER)],
    ]
    table(s, CX, 142, 1200, 196, rows, [300, 300, 300, 300], [52, 72, 72], size=17,
          align=PP_ALIGN.CENTER)
    card(s, CX, 350, 400, 290)
    text(s, CX, 380, 400, 34, '正确的两步', size=17, color=NAVY, bold=True,
         align=PP_ALIGN.CENTER, spacing=1.1)
    text(s, CX, 430, 400, 50, 'L = √(x² + y²)', size=24, color=BLUE, font=EN,
         align=PP_ALIGN.CENTER, spacing=1.1)
    text(s, CX, 494, 400, 50, 'θ = atan2(y, x)', size=26, color=NAVY, font=EN,
         align=PP_ALIGN.CENTER, spacing=1.1)
    text(s, CX, 574, 400, 30, 'L 用勾股定理，θ 用 atan2', size=15, color=MUTED,
         align=PP_ALIGN.CENTER)
    rect(s, 454, 350, 786, 290, fill=LIGHT)
    text(s, 478, 372, 738, 36, '判断：为什么 atan2 不会错', size=19, color=NAVY, bold=True, spacing=1.1)
    text(s, 478, 418, 738, 170,
         ['arctan 只看 y/x 的比值，比值一样就分不清象限。(1,1) 和 (−1,−1) 的比值都是 1，它只能都返回 45°。',
          'atan2(y, x) 同时看 x 和 y 各自的符号，能自动分辨四个象限，返回值范围 (−π, π]。'],
         size=16, color=SUB, spacing=1.7, space_after=10)
    text(s, 478, 598, 738, 34, '凡是“已知坐标求角度”，一律用 atan2。',
         size=16, color=NAVY, bold=True, spacing=1.1)


# =====================================================================
# P14 · M3 驱动问题
# =====================================================================
def p14():
    s = slide()
    header(s, '第二根连杆的角度，是相对谁的？', 'M3 · 驱动问题', 14,
           '第 3 章 · M3　平面正运动学：1R → 2R → 3R')
    card(s, CX, TOP, 500, 552)
    line(s, 80, 460, 520, 460, color=MID, w=2)
    line(s, 120, 510, 120, 128, color=MID, w=2)
    line(s, 120, 460, 311, 370, color=BLUE, w=7)
    line(s, 311, 370, 372, 205, color=NAVY, w=7)
    line(s, 311, 370, 425, 320, color=ONDK, w=2, dash=MSO_LINE_DASH_STYLE.DASH)
    polyline(s, arc_pts(120, 460, 62, 0, 28), color=NAVY, w=2.5)
    polyline(s, arc_pts(311, 370, 58, 28, 74), color=RED, w=2.5)
    rect(s, 111, 451, 18, 18, fill=BLUE, shape=MSO_SHAPE.OVAL)
    rect(s, 302, 361, 18, 18, fill=BLUE, shape=MSO_SHAPE.OVAL)
    rect(s, 362, 196, 20, 20, fill=NAVY, shape=MSO_SHAPE.OVAL)
    text(s, 188, 428, 50, 28, 'θ₁', size=18, color=NAVY, font=EN)
    text(s, 352, 320, 50, 28, 'θ₂', size=18, color=RED, font=EN)
    text(s, 176, 392, 50, 28, 'L₁', size=16, color=BLUE, font=EN)
    text(s, 348, 272, 50, 28, 'L₂', size=16, color=NAVY, font=EN)
    text(s, 394, 180, 140, 26, '末端 (x, y)', size=15, color=NAVY)
    text(s, 128, 430, 90, 26, '关节 1', size=14, color=MUTED)
    text(s, 200, 346, 90, 26, '关节 2', size=14, color=MUTED)
    text(s, 528, 466, 30, 26, 'x', size=16, color=MID, font=EN)
    text(s, 126, 126, 30, 26, 'y', size=16, color=MID, font=EN)
    text(s, 60, 604, 460, 36, '虚线 = 第一根连杆的延长线，θ₂ 就从这里量起',
         size=14, color=MUTED, align=PP_ALIGN.CENTER)
    x, w = 564, 676
    card(s, x, TOP, w, 176)
    text(s, x + 22, 118, 60, 50, 'A', size=34, color=MUTED, font=EN)
    text(s, x + 92, 112, w - 114, 40, 'θ₂ 是相对地面的（相对 x 轴）',
         size=22, color=INK, bold=True, spacing=1.1)
    text(s, x + 92, 158, w - 114, 60, '这样定义“每个关节各管各的，互不影响”。',
         size=15, color=SUB, spacing=1.5)
    rect(s, x, 282, w, 176, fill=LIGHT)
    text(s, x + 22, 312, 60, 50, 'B', size=34, color=NAVY, font=EN)
    text(s, x + 92, 306, w - 114, 40, 'θ₂ 是相对第一根连杆的',
         size=22, color=NAVY, bold=True, spacing=1.1)
    text(s, x + 92, 352, w - 114, 60, '第二根要“叠加”在第一根已经转过的角度上。',
         size=15, color=SUB, spacing=1.5)
    rect(s, x, 476, w, 164, fill=NAVY)
    text(s, x + 22, 494, w - 44, 36, '判断：答案是 B —— 相对角度', size=18, color=WHITE,
         bold=True, spacing=1.1)
    text(s, x + 22, 536, w - 44, 96,
         ['第二个关节的电机就装在第一根连杆的末端上，它转动时坐标系已经跟着转过了。',
          '所以第二根连杆的绝对方向 = θ₁ + θ₂'],
         size=15, color=ONDK, spacing=1.7)


# =====================================================================
# P15 · 向量相加（HERO）
# =====================================================================
def p15():
    s = slide()
    header(s, '2R 正运动学：两段向量首尾相接', 'M3 · 核心概念', 15,
           '第 3 章 · M3　平面正运动学：1R → 2R → 3R')
    card(s, CX, TOP, 682, 552)
    line(s, 90, 490, 640, 490, color=MID, w=2)
    line(s, 130, 560, 130, 140, color=MID, w=2)
    line(s, 130, 490, 372, 155, color=ONDK, w=2, dash=MSO_LINE_DASH_STYLE.DASH)
    line(s, 336, 342, 440, 282, color=ONDK, w=2, dash=MSO_LINE_DASH_STYLE.DASH)
    line(s, 130, 490, 336, 342, color=BLUE, w=8)
    line(s, 336, 342, 372, 155, color=NAVY, w=8)
    polyline(s, [(372, 155), (382, 182), (360, 180)], color=NAVY, w=1, closed=True, fill=NAVY)
    polyline(s, arc_pts(130, 490, 62, 0, 30), color=NAVY, w=2.5)
    polyline(s, arc_pts(336, 342, 62, 30, 76), color=RED, w=2.5)
    rect(s, 121, 481, 18, 18, fill=BLUE, shape=MSO_SHAPE.OVAL)
    rect(s, 327, 333, 18, 18, fill=BLUE, shape=MSO_SHAPE.OVAL)
    rect(s, 362, 145, 20, 20, fill=NAVY, shape=MSO_SHAPE.OVAL)
    text(s, 196, 458, 50, 28, 'θ₁', size=19, color=NAVY, font=EN)
    text(s, 380, 320, 50, 28, 'θ₂', size=19, color=RED, font=EN)
    text(s, 208, 382, 50, 28, 'L₁', size=17, color=BLUE, font=EN)
    text(s, 396, 258, 50, 28, 'L₂', size=17, color=NAVY, font=EN)
    text(s, 236, 222, 120, 28, '合向量', size=16, color=MID)
    text(s, 386, 166, 150, 26, '末端 (x, y)', size=15, color=NAVY)
    text(s, 144, 514, 90, 26, '原点', size=14, color=MUTED)
    text(s, 226, 396, 90, 26, '关节 2', size=14, color=MUTED)
    text(s, 628, 496, 30, 26, 'x', size=16, color=MID, font=EN)
    text(s, 136, 138, 30, 26, 'y', size=16, color=MID, font=EN)
    text(s, 60, 604, 642, 36, '虚线 = 两段向量之和，也就是末端的真实位置',
         size=14, color=MUTED, align=PP_ALIGN.CENTER)
    x, w = 746, 494
    rect(s, x, TOP, w, 230, fill=LIGHT)
    text(s, x + 22, 108, w - 44, 36, '第一段的末端，就是第二段的起点', size=20, color=NAVY,
         bold=True, spacing=1.15)
    text(s, x + 22, 160, w - 44, 140,
         ['x = L₁cos θ₁ + L₂cos(θ₁+θ₂)', 'y = L₁sin θ₁ + L₂sin(θ₁+θ₂)'],
         size=19, color=NAVY, font=EN, spacing=1.85)
    card(s, x, 332, w, 200)
    text(s, x + 22, 352, w - 44, 34, '唯一的易错点', size=19, color=RED, bold=True, spacing=1.1)
    text(s, x + 22, 394, w - 44, 130,
         [[('第二段里写的是 ', {}), ('cos(θ₁+θ₂)', {'font': EN, 'bold': True}),
           ('，', {}), ('不是', {'bold': True}), (' cos(θ₂)。', {})],
          [('写错这一个括号，整个末端位置就全错了。', {})]],
         size=16, color=SUB, spacing=1.7, space_after=10)
    rect(s, x, 546, w, 94, fill=NAVY)
    text(s, x + 22, 546, w - 44, 94,
         '角度累加 = 复合旋转 —— 这就是后面“变换链”思想的雏形。',
         size=16, color=WHITE, spacing=1.6, anchor=MSO_ANCHOR.MIDDLE)


# =====================================================================
# P16 · 3R / nR
# =====================================================================
def p16():
    s = slide()
    header(s, '从 2R 到 nR：多一段，就多累加一个角', 'M3 · 推广', 16,
           '第 3 章 · M3　平面正运动学：1R → 2R → 3R')
    band(s, CX, TOP, 428, 42, '3R：再套一层')
    card(s, CX, 142, 428, 200)
    text(s, 60, 168, 388, 160,
         ['x = L₁cos θ₁ + L₂cos(θ₁+θ₂)', '　　　+ L₃cos(θ₁+θ₂+θ₃)',
          'y = L₁sin θ₁ + L₂sin(θ₁+θ₂)', '　　　+ L₃sin(θ₁+θ₂+θ₃)'],
         size=16, color=NAVY, font=EN, spacing=1.7)
    rect(s, CX, 356, 428, 284, fill=LIGHT)
    text(s, 62, 380, 384, 38, '规律只有一句话', size=18, color=NAVY, bold=True, spacing=1.1)
    text(s, 62, 428, 384, 200,
         ['第 i 段用的角度是前面所有角度之和：θ₁ + θ₂ + … + θᵢ。',
          '记住这一句，就不需要背 3R、4R、5R 的公式。'],
         size=16, color=SUB, spacing=1.75, space_after=10)
    x = 492
    card(s, x, TOP, 748, 552)
    text(s, x + 22, 110, 704, 36, '写成循环：fk_nR 能算任意多段', size=19, color=NAVY,
         bold=True, spacing=1.1)
    code = ('def fk_nR(lengths, angles):\n'
            '    x = y = 0.0\n'
            '    acc = 0.0            # 累计角度\n'
            '    for L, a in zip(lengths, angles):\n'
            '        acc += a         # ← 累加！\n'
            '        x += L * np.cos(acc)\n'
            '        y += L * np.sin(acc)\n'
            '    return x, y')
    rect(s, x + 22, 156, 704, 300, fill=RGBColor(0xF6, 0xF8, 0xFA), line=LIGHT)
    text(s, x + 42, 176, 664, 260, code.split('\n'), size=17, color=INK, font=MONO, spacing=1.55)
    rect(s, x + 22, 470, 704, 170, fill=NAVY)
    text(s, x + 44, 490, 660, 36, '判断：这十几行已经够用了', size=17, color=WHITE,
         bold=True, spacing=1.1)
    text(s, x + 44, 534, 660, 90,
         '把它从平面搬到三维、把 cos/sin 换成旋转矩阵，就是 M8 的变换链。',
         size=15, color=ONDK, spacing=1.7)


# =====================================================================
# P17 · 可达圆环（HERO）
# =====================================================================
def p17():
    s = slide()
    header(s, '可达空间：为什么是一个圆环', 'M3 · 能力边界', 17,
           '第 3 章 · M3　平面正运动学：1R → 2R → 3R')
    rect(s, CX, TOP, 593, 176, fill=LIGHT)
    text(s, 66, TOP, 300, 176, '0.08', size=96, color=NAVY, bold=True, font=EN,
         anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(s, 366, 110, 250, 36, '内边界 r_min（m）', size=19, color=NAVY, bold=True, spacing=1.1)
    text(s, 366, 154, 250, 80, '两段反向：|L₁ − L₂| = |0.30 − 0.22|',
         size=15, color=SUB, spacing=1.5)
    rect(s, 647, TOP, 593, 176, fill=NAVY)
    text(s, 673, TOP, 300, 176, '0.52', size=96, color=WHITE, bold=True, font=EN,
         anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(s, 973, 110, 250, 36, '外边界 r_max（m）', size=19, color=WHITE, bold=True, spacing=1.1)
    text(s, 973, 154, 250, 80, '两段同向：L₁ + L₂ = 0.30 + 0.22',
         size=15, color=ONDK, spacing=1.5)
    card(s, CX, 276, 640, 286)
    ccx, ccy, ro, ri = 320, 420, 118, 18
    rect(s, ccx - ro, ccy - ro, 2 * ro, 2 * ro, fill=LIGHT, line=BLUE, lw=2.5,
         shape=MSO_SHAPE.OVAL)
    rect(s, ccx - ri, ccy - ri, 2 * ri, 2 * ri, fill=WHITE, line=NAVY, lw=2,
         dash=MSO_LINE_DASH_STYLE.DASH, shape=MSO_SHAPE.OVAL)
    line(s, ccx, ccy, ccx, ccy - ro, color=BLUE, w=2.5)
    line(s, ccx, ccy, ccx + ri, ccy, color=NAVY, w=2.5)
    rect(s, ccx - 5, ccy - 5, 10, 10, fill=NAVY, shape=MSO_SHAPE.OVAL)
    text(s, ccx + 10, ccy - ro - 4, 240, 26, 'r_max = 0.52', size=18, color=BLUE,
         bold=True, font=EN)
    text(s, ccx + 26, ccy - 22, 240, 26, 'r_min = 0.08', size=17, color=NAVY, bold=True, font=EN)
    text(s, ccx - 120, ccy - 84, 240, 26, '末端可达区域', size=16, color=NAVY,
         align=PP_ALIGN.CENTER)
    text(s, 420, 512, 250, 26, '这个环里每一点都到得了', size=15, color=SUB)
    text(s, 60, 544, 600, 26, 'L₁ = 0.30 m　L₂ = 0.22 m　｜　圆环：0.08 ≤ r ≤ 0.52（单位 m）',
         size=15, color=MUTED, align=PP_ALIGN.CENTER)
    card(s, 694, 276, 546, 286)
    text(s, 716, 300, 502, 70, '为什么是“环”，不是“圆”？', size=19, color=NAVY,
         bold=True, spacing=1.2)
    text(s, 716, 348, 502, 200,
         ['两段同向能伸到 0.52 m，两段反向只能缩到 0.08 m —— 中间的距离都取得到。',
          '但最里面那一小圈（r 小于 0.08 m）永远够不到，因为第一段连杆自己就有 0.30 m。'],
         size=16, color=SUB, spacing=1.75, space_after=10)
    rect(s, CX, 574, 1200, 66, fill=LIGHT)
    text(s, 62, 582, 1156, 32, '判断：这两个数就是这台臂的能力边界', size=18, color=NAVY,
         bold=True, spacing=1.1)
    text(s, 62, 614, 1156, 26,
         '外边界由“能不能伸直”决定，内边界由“能不能缩回来”决定 —— 它们只和连杆长度有关，和角度无关。',
         size=16, color=SUB, spacing=1.4)


# =====================================================================
# P18 · fk_2r 骨架
# =====================================================================
def p18():
    s = slide()
    header(s, '动手：把公式写进 fk_2r', 'M3 · 上机任务', 18,
           '第 3 章 · M3　平面正运动学：1R → 2R → 3R')
    band(s, CX, TOP, 1200, 42, '打开 armblocks/blocks/planar.py，补全下面这个函数的两行核心代码')
    card(s, CX, 142, 1200, 296)
    code = ('def fk_2r(L1, L2, q1, q2):\n'
            '    """平面两连杆正运动学：关节角 → 末端坐标\n'
            '\n'
            '    q1 : 第一根连杆与 x 轴的夹角（弧度）\n'
            '    q2 : 第二根连杆相对第一根的夹角（弧度）\n'
            '    """\n'
            '    # TODO(M3): 两段向量相加\n'
            '    x = ________________________________\n'
            '    y = ________________________________\n'
            '    return float(x), float(y)')
    text(s, 70, 164, 1140, 270, code.split('\n'), size=16, color=INK, font=MONO, spacing=1.45)
    notes = [
        ('① 角度要对', '第二段必须用 np.cos(q1 + q2)，而不是 np.cos(q2)。', RED, None),
        ('② 类型要对', '返回 float(x), float(y)，不要返回 numpy 标量，否则测试可能失败。', NAVY, LIGHT),
        ('③ 单位要对', '输入角度是弧度。写测试时记得先 np.radians(30)。', NAVY, None),
    ]
    cw, gap = 390.66, 14
    x = CX
    for title, desc, tc, fill in notes:
        if fill is None:
            card(s, x, 452, cw, 188)
        else:
            rect(s, x, 452, cw, 188, fill=fill)
        text(s, x + 20, 472, cw - 40, 32, title, size=19, color=tc, bold=True, spacing=1.1)
        text(s, x + 20, 512, cw - 40, 110, desc, size=15, color=SUB, spacing=1.7)
        x += cw + gap


# =====================================================================
# P19 · 扫描 θ2
# =====================================================================
def p19():
    s = slide()
    header(s, '预测—验证：扫描 θ₂，看 r 怎么变', 'M3 · 探究实验', 19,
           '第 3 章 · M3　平面正运动学：1R → 2R → 3R')
    band(s, CX, TOP, 1200, 42, '固定 θ₁ = 0°，让 θ₂ 从 0° 扫到 180°：末端到原点的距离 r 会怎么变？')
    card(s, CX, 142, 1200, 280)
    ox, oy, sx, sy = 340, 386, 4.0, 340
    for i in range(5):
        yy = oy - (i + 1) * 34.0
        line(s, ox, yy, ox + 720, yy, color=LIGHT, w=1)
    line(s, ox, oy - 200, ox, oy, color=MID, w=2)
    line(s, ox, oy, ox + 730, oy, color=MID, w=2)
    vals = [0.52, 0.5157, 0.5027, 0.4814, 0.4521, 0.4154, 0.3720,
            0.3229, 0.2691, 0.2123, 0.1552, 0.1044, 0.08]
    pts = [(ox + (i * 15) * sx, oy - v * sy) for i, v in enumerate(vals)]
    line(s, ox, oy - 0.52 * sy, ox + 720, oy - 0.52 * sy, color=BLUE, w=1.5,
         dash=MSO_LINE_DASH_STYLE.DASH)
    line(s, ox, oy - 0.08 * sy, ox + 720, oy - 0.08 * sy, color=NAVY, w=1.5,
         dash=MSO_LINE_DASH_STYLE.DASH)
    polyline(s, pts, color=BLUE, w=4)
    rect(s, pts[0][0] - 6, pts[0][1] - 6, 12, 12, fill=BLUE, shape=MSO_SHAPE.OVAL)
    rect(s, pts[-1][0] - 6, pts[-1][1] - 6, 12, 12, fill=NAVY, shape=MSO_SHAPE.OVAL)
    text(s, pts[0][0] + 14, pts[0][1] - 32, 420, 26, 'r = 0.52（θ₂ = 0°，伸得最远）',
         size=17, color=BLUE, bold=True, font=EN)
    text(s, 820, 168, 420, 26, 'r = 0.08（θ₂ = 180°，缩得最短）',
         size=17, color=NAVY, bold=True, font=EN)
    line(s, 1010, 200, 1050, 344, color=NAVY, w=1.2, dash=MSO_LINE_DASH_STYLE.DASH)
    for i, lb in enumerate(['0°', '30°', '60°', '90°', '120°', '150°', '180°']):
        xx = ox + (i * 30) * sx
        text(s, xx - 40, 392, 80, 24, lb, size=14, color=INK, font=EN, align=PP_ALIGN.CENTER)
    for v, lb in [(0.1, '0.1'), (0.3, '0.3'), (0.5, '0.5')]:
        text(s, ox - 76, oy - v * sy - 12, 66, 24, lb, size=14, color=INK, font=EN,
             align=PP_ALIGN.RIGHT)
    text(s, ox - 76, oy - 0.55 * sy + 4, 66, 24, 'r /m', size=14, color=MUTED,
         align=PP_ALIGN.RIGHT)
    text(s, ox + 736, 392, 40, 24, 'θ₂', size=14, color=INK, font=EN)
    rect(s, CX, 434, 1200, 104, fill=LIGHT)
    text(s, 62, 448, 700, 32, '洞察：r 在 [0°, 180°] 上严格单调减小', size=18, color=NAVY,
         bold=True, spacing=1.1)
    text(s, 62, 484, 700, 44, '第二段先“绕出去”再“收回来”，所以曲线是光滑下滑、没有回升。',
         size=15, color=SUB, spacing=1.5)
    rect(s, 790, 446, 428, 80, fill=NAVY)
    text(s, 810, 446, 388, 80,
         '关键结论：r 只取决于 θ₂ —— 把 θ₁ 改成 90° 再做一次，r 的曲线一模一样。',
         size=15, color=ONDK, spacing=1.6, anchor=MSO_ANCHOR.MIDDLE)
    rows = [
        headrow(['六个可手算的校验点', '(0°, 0°)', '(0°, 90°)', '(90°, 0°)',
                 '(90°, −90°)', '(35°, 60°)', '(0°, 180°)'], size=14),
        [C('末端 (x, y) / m', fill=LIGHT, size=14),
         C('(0.5200, 0.0000)', font=EN, size=14),
         C('(0.3000, 0.2200)', font=EN, size=14),
         C('(0.0000, 0.5200)', font=EN, size=14),
         C('(0.2200, 0.3000)', font=EN, size=14),
         C('(0.2266, 0.3912)', font=EN, size=14),
         C('(0.0800, 0.0000)', font=EN, size=14)],
    ]
    table(s, CX, 550, 1200, 90, rows, [235, 165, 165, 165, 165, 165, 140], [45, 45],
          size=14, align=PP_ALIGN.CENTER)


# =====================================================================
# P20 · 速查卡
# =====================================================================
def p20():
    s = slide()
    header(s, '速查卡：把三节课压缩成一页', '总结', 20)
    rect(s, CX, TOP, 340, 552, fill=NAVY)
    text(s, 70, 116, 290, 26, 'CHEAT SHEET', size=15, color=ONDK, font=EN)
    text(s, 70, 150, 290, 120, ['四条', '速查'], size=34, color=WHITE, bold=True, spacing=1.3)
    rect(s, 70, 288, 70, 3, fill=MID)
    text(s, 70, 316, 290, 190,
         '①② 是概念，③④ 才是新公式。只背公式不理解 ①②，遇到真机就不知道自己在算哪个空间。',
         size=16, color=ONDK, spacing=1.8)
    text(s, 70, 580, 290, 30, 'M1 – M3 · 打地基', size=14, color=ONDK)
    items = [
        ('1', 'FK 与 IK 方向相反',
         [[('FK：关节角 → 末端位置，', {}), ('一定有唯一答案', {'bold': True}),
           ('；IK：末端位置 → 关节角，', {}),
           ('可能多解、可能无解', {'bold': True, 'color': RED}), ('。', {})]], None),
        ('2', '两个空间，两种语言',
         '关节空间用角度（电机听得懂）；笛卡尔空间用坐标（人说得清）。运动学就是这两个空间之间的翻译官。', LIGHT),
        ('3', '一根连杆的翻译公式',
         '正向：x = L·cos θ，y = L·sin θ　　反向：L = hypot(x, y)，θ = atan2(y, x)', None),
        ('4', '多段连杆：角度要累加',
         '第 i 段用 θ₁ + … + θᵢ；可达空间是圆环 |L₁ − L₂| ≤ r ≤ L₁ + L₂（L₁=0.30、L₂=0.22 时是 0.08 ~ 0.52 m）。', None),
    ]
    y = TOP
    for num, title, desc, fill in items:
        if fill is None:
            card(s, 404, y, 836, 130)
        else:
            rect(s, 404, y, 836, 130, fill=fill)
        rect(s, 426, y + 39, 52, 52, fill=LIGHT if fill is None else WHITE)
        text(s, 426, y + 39, 52, 52, num, size=24, color=NAVY, bold=True, font=EN,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
        text(s, 498, y + 22, 720, 36, title, size=21, color=INK, bold=True, spacing=1.1)
        text(s, 498, y + 62, 720, 58, desc, size=15, color=SUB, spacing=1.55)
        y += 142


# =====================================================================
# P21 · 结束页
# =====================================================================
def p21():
    s = slide()
    rect(s, 0, 0, 1280, 720, fill=NAVY)
    text(s, 80, 112, 700, 30, '下一步', size=16, color=ONDK)
    text(s, 80, 146, 700, 76, '从平面，走进三维', size=52, color=WHITE, bold=True, spacing=1.15)
    rect(s, 80, 238, 96, 4, fill=BLUE)
    text(s, 80, 266, 700, 110,
         '平面的 fk_nR 只要把 cos / sin 换成旋转矩阵、把角度累加换成矩阵连乘，就是三维的变换链（M8）。',
         size=18, color=ONDK, spacing=1.8)
    text(s, 80, 386, 700, 130,
         '今天埋下的两个伏笔 —— UR5 不是球形手腕（M10）、一个目标可能有两组解（M4）—— 都会在后面的课里用数据拆开。',
         size=17, color=ONDK, spacing=1.8)
    rect(s, 80, 528, 700, 108, fill=BLUE)
    text(s, 100, 544, 660, 78,
         ['课后立刻能跑：python demos/demo_planar_2r.py',
          '课程代码与讲义：github.com/AlionFan/arm-kinematics-course'],
         size=16, color=WHITE, spacing=1.7)
    ccx, ccy = 1000, 300
    rect(s, ccx - 86, ccy - 166, 172, 60, fill=None, line=MID, lw=2, shape=MSO_SHAPE.OVAL)
    rect(s, ccx - 40, ccy - 180, 80, 28, fill=None, line=MID, lw=2, shape=MSO_SHAPE.OVAL)
    rect(s, ccx - 34, ccy - 124, 68, 68, fill=None, line=MID, lw=2, shape=MSO_SHAPE.OVAL)
    line(s, ccx, ccy - 56, ccx + 48, ccy + 84, color=WHITE, w=7)
    line(s, ccx + 48, ccy + 84, ccx + 128, ccy + 6, color=WHITE, w=7)
    rect(s, ccx - 9, ccy - 65, 18, 18, fill=WHITE, shape=MSO_SHAPE.OVAL)
    rect(s, ccx + 39, ccy + 75, 18, 18, fill=WHITE, shape=MSO_SHAPE.OVAL)
    rect(s, ccx + 118, ccy - 4, 20, 20, fill=BLUE, line=WHITE, lw=4, shape=MSO_SHAPE.OVAL)
    text(s, 740, 548, 520, 30, '平面（2R）→ 三维（6R / 7R）', size=16, color=ONDK,
         align=PP_ALIGN.CENTER)
    text(s, ccx + 144, ccy + 2, 110, 26, '末端', size=15, color=ONDK)


# ---------------- 生成 ----------------
p01(); p02()
section('01', '机械臂怎么“知道”手在哪？',
        ['正运动学 FK · 逆运动学 IK', '关节空间 · 笛卡尔空间', '两台真实机械臂'],
        [330, 290, 250], 3, '第 1 章　对应页码 P3 – P7　｜　2 课时')
p04(); p05(); p06(); p07()
section('02', '单位圆与“角度坐标”',
        ['sin / cos 就是坐标', '弧度制与换算', 'atan2 与象限'],
        [250, 210, 210], 8, '第 2 章　对应页码 P8 – P12　｜　1 课时')
p09(); p10(); p11(); p12()
section('03', '平面正运动学：1R → 2R → 3R',
        ['角度累加 θ₁ + θ₂', '向量相加', '可达空间是圆环'],
        [280, 180, 250], 13, '第 3 章　对应页码 P13 – P20　｜　2 课时')
p14(); p15(); p16(); p17(); p18(); p19(); p20(); p21()

OUT = r'C:\Users\Alion\Documents\国优\ppt\机械臂运动学-前三讲\机械臂运动学-前三讲.pptx'
prs.save(OUT)
print('saved:', OUT, '| slides =', len(prs.slides._sldIdLst))
