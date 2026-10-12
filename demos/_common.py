# -*- coding: utf-8 -*-
"""demo 公共工具：选实现、存图/显示。"""
import argparse
import sys

sys.path.insert(0, __file__.rsplit("demos", 1)[0].rstrip("\\/"))

import matplotlib
from armblocks.plotstyle import use_cjk_font

use_cjk_font()


def parse_args(desc):
    p = argparse.ArgumentParser(description=desc)
    p.add_argument("--impl", choices=["solutions", "blocks"], default="solutions",
                   help="用参考答案还是用你自己的积木驱动（默认 solutions）")
    p.add_argument("--save", default=None,
                   help="把图保存到指定文件（不弹窗，适合无界面环境）")
    return p.parse_args()


def rotations(argv=None):
    """返回要使用的旋转积木模块。"""
    args = parse_args("rotations") if argv is None else argv
    if args.impl == "blocks":
        from armblocks import blocks
        return blocks.rotations
    from armblocks import solutions
    return solutions.rotations


def finish(fig, save):
    if save:
        fig.savefig(save, dpi=140, bbox_inches="tight")
        print(f"[√] 图已保存：{save}")
    else:
        import matplotlib.pyplot as plt
        plt.show()
