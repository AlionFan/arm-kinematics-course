#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_unitree_model.py
从 unitreerobotics/unitree_ros 仓库拉取宇树 R1 七轴机械臂（r1_7a_description）的
URDF 与网格文件，保存到本地 models/r1_7a/。

用法：
    python tools/fetch_unitree_model.py

依赖：标准库（urllib）。GitHub API 匿名访问限速 60 次/小时。
"""
import base64
import json
import os
import sys
import urllib.request

API = "https://api.github.com"
REPO = "unitreerobotics/unitree_ros"
BRANCH = "master"
SRC_DIR = "robots/r1_7a_description"
DST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "r1_7a")


def _get(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "unitree-model-fetcher",
        "Accept": "application/vnd.github+json",
    })
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def main():
    print(f"[*] 列出 {REPO}:{BRANCH} 目录树 ...")
    tree = _get(f"{API}/repos/{REPO}/git/trees/{BRANCH}?recursive=1")
    prefix = SRC_DIR + "/"
    files = [n for n in tree["tree"]
             if n["type"] == "blob" and n["path"].startswith(prefix)]
    if not files:
        print("[!] 未找到目标目录，请检查仓库结构。")
        sys.exit(1)
    print(f"[*] 共 {len(files)} 个文件待下载。")

    for n in files:
        rel = n["path"][len(prefix):]
        out = os.path.join(DST_DIR, rel)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        if os.path.exists(out) and os.path.getsize(out) == n.get("size", -1):
            print(f"    = 跳过（已存在）{rel}")
            continue
        blob = _get(f"{API}/repos/{REPO}/git/blobs/{n['sha']}")
        raw = base64.b64decode(blob["content"])
        with open(out, "wb") as f:
            f.write(raw)
        print(f"    + {rel}  ({len(raw):,} bytes)")

    print(f"[√] 完成，模型位于：{DST_DIR}")


if __name__ == "__main__":
    main()
