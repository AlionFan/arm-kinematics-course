# -*- coding: utf-8 -*-
"""
绘图样式（平台层）
==================
统一设置中文字体与负号显示，避免图上出现"豆腐块"。
"""
from __future__ import annotations

import matplotlib

_CJK_CANDIDATES = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC",
                   "Source Han Sans SC", "PingFang SC", "WenQuanYi Zen Hei"]


def use_cjk_font() -> str | None:
    """把 matplotlib 的默认字体切到可用的中文字体，返回选中的字体名。"""
    from matplotlib import font_manager
    available = {f.name for f in font_manager.fontManager.ttflist}
    chosen = next((n for n in _CJK_CANDIDATES if n in available), None)
    matplotlib.rcParams["font.sans-serif"] = ([chosen] if chosen else []) + ["DejaVu Sans"]
    matplotlib.rcParams["axes.unicode_minus"] = False
    return chosen
