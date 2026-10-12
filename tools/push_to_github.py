#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通过 GitHub REST API 把本仓库推送到 GitHub。

背景：本机沙箱代理只放通 api.github.com，github.com 的 git/OAuth 通道被拦截，
因此无法使用 `git push` 或 `gh auth login`，改用 Git Data API 逐文件推送。

用法：
    set GITHUB_TOKEN=ghp_xxx            # Windows cmd
    $env:GITHUB_TOKEN="ghp_xxx"         # PowerShell
    export GITHUB_TOKEN=ghp_xxx         # bash

    python tools/push_to_github.py --owner AlionFan --repo arm-kinematics-course
    python tools/push_to_github.py --dry-run      # 只列出将要推送的文件，不联网

注意：GitHub 仓库名只允许 ASCII 字母/数字/`.`/`-`/`_`，中文名会被压成 `-`，
所以仓库名用英文 slug，中文标题放在 description 里。

凭据要求：classic PAT，勾选 repo 权限（或 fine-grained token 勾选
Administration: Read and write + Contents: Read and write）。
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.github.com"
REPO_ROOT = Path(__file__).resolve().parent.parent


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
def api_request(method: str, path: str, token: str, payload: dict | None = None):
    """发一个 GitHub API 请求，返回 (status, 解析后的 json 或原始文本)。

    注意：仓库名可能含中文，HTTP 层要求 URL 为 ASCII，
    因此对 path 做百分号编码（保留 '/' 分隔符）。
    """
    if path.startswith("http"):
        url = path
    else:
        url = API + urllib.parse.quote(path, safe="/:?&=#%")
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "armblocks-push")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, (json.loads(body) if body else None)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, body
    except Exception as e:  # noqa: BLE001
        return 0, str(e)


# --------------------------------------------------------------------------- #
# 读取 git 索引（自动尊重 .gitignore）
# --------------------------------------------------------------------------- #
def list_tracked_files() -> list[tuple[str, str]]:
    """返回 [(mode, path), ...]，mode 为 '100644' / '100755' / '120000'。

    使用 -z 避免中文路径被 git 转义，路径统一用正斜杠（git 索引原生格式）。
    """
    out = subprocess.run(
        ["git", "-c", "core.quotepath=false", "ls-files", "-s", "-z"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=True,
    ).stdout

    files: list[tuple[str, str]] = []
    for entry in out.split(b"\x00"):
        if not entry:
            continue
        meta, path = entry.split(b"\t", 1)
        mode = meta.split(b" ")[0].decode("ascii")
        files.append((mode, path.decode("utf-8")))
    return sorted(files, key=lambda t: t[1])


def repo_header() -> dict:
    """取本地 HEAD 提交的作者/提交信息，保持与本地提交一致。"""
    def git(*args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()

    name = git("config", "user.name")
    email = git("config", "user.email")
    message = git("log", "-1", "--format=%B")
    return {"name": name, "email": email, "message": message}


# --------------------------------------------------------------------------- #
# 推送
# --------------------------------------------------------------------------- #
def head_sha(owner: str, repo: str, branch: str, token: str) -> str | None:
    """返回分支尖端 commit sha；空仓库或分支不存在时返回 None。"""
    status, body = api_request("GET", f"/repos/{owner}/{repo}/git/ref/heads/{branch}", token)
    if status == 200 and isinstance(body, dict):
        return body["object"]["sha"]
    return None


def ensure_initial_commit(owner: str, repo: str, branch: str, token: str) -> str | None:
    """空仓库无法直接 POST blobs（会 409 Git Repository is empty）。

    先用 Contents API 落一个占位文件，从而产生首个 commit 与目标分支；
    占位文件不进入最终 tree，故最终仓库内容依然干净。
    """
    sha = head_sha(owner, repo, branch, token)
    if sha:
        return sha
    content = base64.b64encode(b"init\n").decode("ascii")
    status, body = api_request(
        "PUT",
        f"/repos/{owner}/{repo}/contents/.gitkeep",
        token,
        {"message": "chore: 初始化仓库", "content": content, "branch": branch},
    )
    if status not in (200, 201):
        raise RuntimeError(f"初始化空仓库失败 ({status}): {body}")
    print(f"  仓库为空 → 已创建占位提交，分支 {branch}")
    return head_sha(owner, repo, branch, token)


def ensure_repo(owner: str, repo: str, token: str, description: str, private: bool) -> bool:
    status, body = api_request("GET", f"/repos/{owner}/{repo}", token)
    if status == 200:
        print(f"  仓库已存在：{body['html_url']}")
        return True
    if status != 404:
        print(f"  ! 检查仓库失败 ({status}): {body}")
        return False

    status, body = api_request(
        "POST",
        "/user/repos",
        token,
        {
            "name": repo,
            "description": description,
            "private": private,
            "has_issues": True,
            "has_wiki": False,
            "auto_init": False,
        },
    )
    if status in (200, 201):
        print(f"  仓库已创建：{body['html_url']}")
        return True
    print(f"  ! 创建仓库失败 ({status}): {body}")
    return False


def upload_blobs(files: list[tuple[str, str]], owner: str, repo: str, token: str) -> list[dict]:
    tree = []
    blob_path = f"/repos/{owner}/{repo}/git/blobs"
    for i, (mode, relpath) in enumerate(files, 1):
        abspath = REPO_ROOT / relpath
        raw = abspath.read_bytes()
        if mode == "120000":  # 符号链接：内容是链接目标
            content = raw.decode("utf-8")
        else:
            content = base64.b64encode(raw).decode("ascii")

        status, body = api_request(
            "POST", blob_path, token, {"content": content, "encoding": "base64"}
        )
        if status not in (200, 201):
            raise RuntimeError(f"blob 上传失败 [{relpath}] ({status}): {body}")
        size = len(raw)
        print(f"  [{i:>2}/{len(files)}] {relpath}  ({size:,} B)")
        tree.append({"path": relpath, "mode": mode, "type": "blob", "sha": body["sha"]})
    return tree


def main() -> int:
    ap = argparse.ArgumentParser(description="用 GitHub REST API 推送本仓库")
    ap.add_argument("--owner", default="AlionFan", help="GitHub 用户名/组织名")
    ap.add_argument("--repo", default="arm-kinematics-course", help="仓库名（ASCII slug）")
    ap.add_argument(
        "--description",
        default="面向高中生的机械臂运动学课程：以三角函数为主线，含宇树 R1 七轴臂模型与"
        "积木式仿真框架（数学核心留空给学生填写）",
    )
    ap.add_argument("--private", action="store_true", help="创建为私有仓库")
    ap.add_argument("--branch", default="main", help="推送到的分支名")
    ap.add_argument("--dry-run", action="store_true", help="只列出文件，不联网")
    args = ap.parse_args()

    files = list_tracked_files()
    total = sum((REPO_ROOT / p).stat().st_size for _, p in files if (REPO_ROOT / p).is_file())
    print(f"仓库根目录：{REPO_ROOT}")
    print(f"待推送文件：{len(files)} 个，共 {total:,} 字节（{total / 1048576:.2f} MB）")
    print()

    if args.dry_run:
        for mode, relpath in files:
            flag = "BIN" if (REPO_ROOT / relpath).read_bytes()[:1] == b"\x00" else "   "
            print(f"  {flag} {mode}  {relpath}")
        print("\n[dry-run] 未联网、未做任何改动。")
        return 0

    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        print("! 缺少环境变量 GITHUB_TOKEN", file=sys.stderr)
        return 2

    print("1) 校验凭据…")
    status, user = api_request("GET", "/user", token)
    if status != 200:
        print(f"  ! 凭据无效 ({status}): {user}", file=sys.stderr)
        return 3
    print(f"  已认证为 {user['login']}（{user.get('name') or '未设置昵称'}）")

    print(f"\n2) 准备仓库 {args.owner}/{args.repo} …")
    if not ensure_repo(args.owner, args.repo, token, args.description, args.private):
        return 4
    owner = user["login"] if args.owner == user["login"] else args.owner

    print(f"\n3) 确保存在初始提交（空仓库需要）…")
    parent = ensure_initial_commit(owner, args.repo, args.branch, token)
    if parent:
        print(f"  parent commit = {parent[:7]}")

    print(f"\n4) 上传 {len(files)} 个 blob …")
    tree_entries = upload_blobs(files, owner, args.repo, token)

    print("\n5) 创建 tree …")
    status, tree = api_request(
        "POST", f"/repos/{owner}/{args.repo}/git/trees", token, {"tree": tree_entries}
    )
    if status not in (200, 201):
        print(f"  ! tree 创建失败 ({status}): {tree}", file=sys.stderr)
        return 5
    print(f"  tree sha = {tree['sha']}")

    print("\n6) 创建 commit …")
    header = repo_header()
    commit_payload = {
        "message": header["message"],
        "tree": tree["sha"],
        "author": {"name": header["name"], "email": header["email"]},
        "committer": {"name": header["name"], "email": header["email"]},
    }
    if parent:
        commit_payload["parents"] = [parent]
    status, commit = api_request(
        "POST",
        f"/repos/{owner}/{args.repo}/git/commits",
        token,
        commit_payload,
    )
    if status not in (200, 201):
        print(f"  ! commit 创建失败 ({status}): {commit}", file=sys.stderr)
        return 6
    print(f"  commit sha = {commit['sha']}")

    print(f"\n7) 写入分支 {args.branch} …")
    if head_sha(owner, args.repo, args.branch, token):  # 分支已存在 → 强制更新
        status, ref = api_request(
            "PATCH", f"/repos/{owner}/{args.repo}/git/refs/heads/{args.branch}", token,
            {"sha": commit["sha"], "force": True},
        )
    else:
        status, ref = api_request(
            "POST", f"/repos/{owner}/{args.repo}/git/refs", token,
            {"ref": f"refs/heads/{args.branch}", "sha": commit["sha"]},
        )
    if status not in (200, 201):
        print(f"  ! 分支写入失败 ({status}): {ref}", file=sys.stderr)
        return 7

    # 把默认分支设为刚推送的分支
    api_request("PATCH", f"/repos/{owner}/{args.repo}", token, {"default_branch": args.branch})

    print(f"\n✅ 推送完成：https://github.com/{owner}/{args.repo}")
    print(f"   分支 {args.branch} @ {commit['sha'][:7]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
