"""Shared local launch inputs; native CLI behavior belongs to each adapter."""
import json
from pathlib import Path


class LaunchError(Exception):
    pass


def directory(value):
    path = Path(value).expanduser().resolve(strict=True)
    if not path.is_dir():
        raise LaunchError("Expected a directory")
    return path


def repository(value):
    path = directory(value)
    if not (path / ".git").exists():
        raise LaunchError("--repo must be the Git root (clone or linked worktree)")
    for name in ("AGENTS.md", "README.md"):
        if not (path / name).is_file():
            raise LaunchError("Repository entry is missing " + name)
    return path


def start_prompt(repo, tag):
    return (f"[corpo:{tag}]\n"
            f"仓库入口：{json.dumps(str(repo), ensure_ascii=False)}\n"
            "进入该仓库，按仓库规则自主开展工作。本次没有 merge 授权。")
