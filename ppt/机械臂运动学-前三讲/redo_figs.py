# -*- coding: utf-8 -*-
"""重做配图插入：改用 <img> + 独立说明段（转换器对 <figure> 支持不佳）。"""
import os
import re

from PIL import Image

ROOT = 'C:/Users/Alion/Documents/国优'
FIGDIR = os.path.join(ROOT, 'ppt', '机械臂运动学-前三讲', 'figures')
DPI = (210, 210)          # 1280px / 210dpi ≈ 15.5 cm，正好落在 A4 版心内
W_ATTR = '590'            # 590px ≈ 15.6 cm

CSS_NEW = """
  img.fig { display: block; }
  p.fig-cap { font-size: var(--fs-small); color: var(--color-muted); text-align: center; padding-top: var(--spacing-tight); }
"""


def fig_block(name, alt, cap):
    return ('    <img class="fig" src="figures/%s.png" alt="%s" width="%s">\n'
            '    <p class="fig-cap">%s</p>\n' % (name, alt, W_ATTR, cap))


JOBS = [
    dict(html='output/a724c3af-6ad5-4fe7-a7c6-b1d02aed9f8f/stage2/formatted-M1.html',
         anchor='<p>先不动笔，只动手：拖动一个关节，看看末端（机械臂的“手”）会怎样移动。</p>',
         mode='after', figs=[('fig_m1_joint_chain', 'p01.png',
                              '机械臂关节链示意图：底座、6 个关节与末端执行器，右侧为 6 个关节角表盘',
                              '图 1　机械臂的“状态”由 6 个关节角完全确定')]),
    dict(html='output/80ecd120-50fd-4ce6-8243-28712190277c/stage2/formatted-M2.html',
         anchor='落点 = ( cos θ , sin θ )</pre>',
         mode='after', figs=[('fig_m2_unit_circle', 'p02.png',
                              '单位圆示意图：从原点转过 θ 角的半径，落点横坐标为 cos θ、纵坐标为 sin θ',
                              '图 1　单位圆：落点的横坐标就是 cos θ，纵坐标就是 sin θ')]),
    dict(html='output/a3cc3ec1-1910-476b-98af-ccf9b7546917/stage2/formatted-M3.html',
         anchor='<h3>（三）3R：再套一层</h3>', mode='before',
         figs=[('fig_m3_vector_sum', 'p03.png',
                '平面 2R 机械臂向量相加示意图：a1、a2 两段位移首尾相接，末端 r 等于 a1 加 a2',
                '图 1　2R 机械臂：末端 = 两段位移向量首尾相接')],
         extra=dict(cap_marker='表 4-1', name='fig_m3_annulus', src='p04.png',
                    alt='可达空间圆环示意图：外圈半径 0.52 米、内圈半径 0.08 米，右侧为局部放大视图',
                    cap='图 2　可达空间是一个圆环：内边界 0.08 m，外边界 0.52 m')),
]


def patch_css(html):
    if '--fig-max-width' not in html:
        m = re.search(r'(:root\s*\{)(.*?)(\n\s*\})', html, re.S)
        if m:
            html = html[:m.end(2)] + '\n    --fig-max-width: 100%;' + html[m.end(2):]
    html = re.sub(r'\n\s*figure\.fig[^\n]*\n', '\n', html)
    if 'p.fig-cap' not in html:
        html = html.replace('</style>', CSS_NEW + '\n</style>', 1)
    return html


def main():
    # 1) 给配图写入 DPI，保证任何嵌入路径下的物理尺寸都合适
    for _, src in [(n, s) for job in JOBS for (n, s, _a, _c) in job['figs']] + [('x', 'p04.png')]:
        p = os.path.join(FIGDIR, src)
        im = Image.open(p)
        im.save(p, dpi=DPI)
    print('dpi patched on figure pngs')

    for job in JOBS:
        path = os.path.join(ROOT, job['html'])
        html = open(path, encoding='utf-8').read()
        html = re.sub(r'\s*<figure class="fig">[\s\S]*?</figure>\n', '\n', html)
        if job['anchor'] not in html:
            raise SystemExit('anchor missing: %s' % job['html'])
        for name, _src, alt, cap in job['figs']:
            blk = fig_block(name, alt, cap)
            if name + '.png' in html:
                continue
            if job['mode'] == 'after':
                html = html.replace(job['anchor'], job['anchor'] + '\n' + blk, 1)
            else:
                html = html.replace(job['anchor'], blk + job['anchor'], 1)
        ex = job.get('extra')
        if ex and ex['name'] + '.png' not in html:
            i = html.find(ex['cap_marker'])
            j = html.find('</table>', i) + len('</table>')
            blk = fig_block(ex['name'], ex['alt'], ex['cap'])
            html = html[:j] + '\n' + blk + html[j:]
        html = patch_css(html)
        open(path, 'w', encoding='utf-8').write(html)
        print('patched', job['html'],
              '| figures =', html.count('class="fig"'))


if __name__ == '__main__':
    main()
