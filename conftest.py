# -*- coding: utf-8 -*-
"""pytest 配置：把仓库根目录加入 import 路径。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
