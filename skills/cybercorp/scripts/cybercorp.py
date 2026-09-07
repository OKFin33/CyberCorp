#!/usr/bin/env python3
"""Install a self-contained Corp entry into a new or existing Git repository."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

VERSION = "0.1.0a3"
ASSETS = Path(__file__).resolve().parents[1] / "assets/corp"
MANIFEST = ".agents/corp/install.json"
START = "<!-- cybercorp:entry:start -->"
END = "<!-- cybercorp:entry:end -->"


class InstallError(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise InstallError(label + " must be a nonempty string")
    return value


def relative_path(value):
    nonempty(value, "repository path")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or not path.parts or "\\" in value:
        raise InstallError("Expected a repository-relative path: " + value)
    if ".git" in path.parts:
        raise InstallError("Git internals are not project inputs")
    return path.as_posix()


def owned_path(root, name):
    path = root / relative_path(name)
    for item in [path, *path.parents]:
        if item == root:
            break
        if item.is_symlink():
            raise InstallError("Installation/input path contains a symlink: " + name)
    return path


def read_brief(path, root):
    brief = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(brief, dict):
        raise InstallError("Brief must be a JSON object")
    allowed = {"name", "goal", "scope", "project_ref", "sources", "canon", "github", "milestone"}
    if set(brief) - allowed:
        raise InstallError("Unknown brief fields: " + ", ".join(sorted(set(brief) - allowed)))
    nonempty(brief.get("name"), "name")
    if brief.get("project_ref"):
        ref = relative_path(brief["project_ref"])
        if not owned_path(root, ref).is_file():
            raise InstallError("Existing project owner not found: " + ref)
        if brief.get("goal") or brief.get("scope"):
            raise InstallError("Use project_ref for the existing goal/scope; do not duplicate it in this brief")
    else:
        nonempty(brief.get("goal"), "goal")
        if not isinstance(brief.get("scope"), list) or not brief["scope"]:
            raise InstallError("scope must describe the agreed whole-project scope")
        for item in brief["scope"]:
            nonempty(item, "scope item")
    sources = brief.get("sources", [])
    if not isinstance(sources, list):
        raise InstallError("sources must be a list of repository-relative paths")
    for item in sources:
        if not owned_path(root, relative_path(item)).exists():
            raise InstallError("Source not found in repository: " + item)
    canon = brief.get("canon", [])
    if not isinstance(canon, list):
        raise InstallError("canon must be a list")
    ids = {"project-direction", "current-delivery-focus", "active-change-specs"}
    for item in canon:
        if not isinstance(item, dict) or set(item) != {"id", "target", "status"}:
            raise InstallError("Canon routes need id, target and status")
        if not isinstance(item["id"], str) or not re.fullmatch(r"[a-z][a-z0-9-]*", item["id"]) or item["id"] in ids:
            raise InstallError("Canon route IDs must be unique")
        ids.add(item["id"])
        if item["status"] not in {"active", "pending-relocation", "unresolved"}:
            raise InstallError("Invalid Canon route status")
        if item["target"] is None:
            if item["status"] == "active":
                raise InstallError("An active Canon route needs an existing target")
        else:
            ref = relative_path(item["target"])
            if item["status"] == "active" and not owned_path(root, ref).exists():
                raise InstallError("Active Canon target not found: " + ref)
    repo = brief.get("github")
    if repo is not None and (not isinstance(repo, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9_.-]+", repo)):
        raise InstallError("github must be owner/repository")
    milestone = brief.get("milestone")
    if milestone is not None and (type(milestone) is not int or milestone < 1 or not repo):
        raise InstallError("milestone needs a positive native number and github repository")
    return brief


def entry_block(kind):
    if kind == "AGENTS.md":
        body = ("## Corp entry\n\n"
                "从 [Corp 入口](docs/corp/README.md) 恢复项目目标、共享工作与所需方法。"
                "已有根／路径契约与事实 owner 继续有效；入口不授予额外权限。\n")
    else:
        body = "## Agent collaboration\n\n工作 Agent 从 [Corp 入口](docs/corp/README.md) 进入项目。\n"
    return START + "\n" + body + END + "\n"


def render(brief):
    files = {}
    for path in sorted(ASSETS.rglob("*")):
        if path.is_symlink():
            raise InstallError("Package assets must not contain symlinks")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
            files[path.relative_to(ASSETS).as_posix()] = path.read_bytes()
    project_ref = brief.get("project_ref", "docs/corp/project.md")
    if not brief.get("project_ref"):
        text = "# " + brief["name"] + "\n\n" + brief["goal"] + "\n\n## 约定范围\n\n"
        text += "".join("- " + item + "\n" for item in brief["scope"])
        files[project_ref] = text.encode()
    sources = brief.get("sources", [])
    source_text = "\n".join("- `" + item + "`" for item in sources) if sources else "未指定既有材料；按项目目标识别实际需要的输入。"
    shared_work = ("共享工作仓库由本次输入指定为 `" + brief["github"] + "`；其实际状态和访问仍需原生读取核验。"
                   if brief.get("github") else
                   "尚未指定共享任务仓库，当前只有本地入口。后续按用户授权建立或接入真实共享工作；不要从文件安装推断远端可用。")
    readme = files["docs/corp/README.md"].decode()
    readme = readme.replace("{{PROJECT_REF}}", project_ref).replace("{{SOURCES}}", source_text).replace("{{SHARED_WORK}}", shared_work)
    files["docs/corp/README.md"] = readme.encode()
    focus = (f"https://github.com/{brief['github']}/milestone/{brief['milestone']}"
             if brief.get("milestone") else None)
    entries = [
        {"id": "project-direction", "target": project_ref, "status": "active"},
        {"id": "active-change-specs", "target": f"https://github.com/{brief['github']}/issues" if brief.get("github") else None,
         "status": "active" if brief.get("github") else "unresolved"},
        {"id": "current-delivery-focus", "target": focus, "status": "active" if focus else "unresolved"},
        *brief.get("canon", []),
    ]
    text = "schema_version: 1\ncanonical_targets:\n"
    for item in entries:
        text += f"  - id: {item['id']}\n    target: {json.dumps(item['target'], ensure_ascii=False)}\n    status: {item['status']}\n"
    files["docs/corp/canon-map.yaml"] = text.encode()
    return files


def git_state(root):
    if not root.exists():
        # Inspect the existing parent too: do not create a nested repo by accident.
        parent = root.parent
        while not parent.exists():
            parent = parent.parent
    else:
        parent = root
    result = subprocess.run(["git", "-C", str(parent), "rev-parse", "--show-toplevel"],
                            capture_output=True, text=True)
    if result.returncode == 0:
        if Path(result.stdout.strip()).resolve() != root:
            raise InstallError("Target is inside another Git repository; use its real root")
        return "existing"
    if (root / ".git").exists():
        raise InstallError("Git metadata exists but repository inspection failed")
    return "new"


def install(root, brief, dry_run=False):
    state = git_state(root)
    files = render(brief)
    payload = {name: digest(content) for name, content in files.items()}
    payload.update({"entry:" + name: digest(entry_block(name).encode()) for name in ("AGENTS.md", "README.md")})
    payload_hash = digest(json.dumps(payload, sort_keys=True).encode())
    manifest_path = owned_path(root, MANIFEST)
    input_hash = digest(json.dumps(brief, sort_keys=True, ensure_ascii=False).encode())
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        if (manifest.get("version") != VERSION or manifest.get("brief_sha256") != input_hash
                or manifest.get("payload_sha256") != payload_hash):
            raise InstallError("Corp already installed with different inputs/package; adapt the existing owners instead of overwriting")
        changed = []
        for name, expected in manifest["files"].items():
            path = owned_path(root, name)
            if not path.is_file() or digest(path.read_bytes()) != expected:
                changed.append(name)
        return {"status": "already_installed", "repo": str(root), "preserved_project_edits": changed,
                "ceiling": "Installation metadata only; current project files own subsequent decisions."}
    conflicts = []
    for name, content in files.items():
        path = owned_path(root, name)
        if path.exists() and (not path.is_file() or path.read_bytes() != content):
            conflicts.append(name)
        for parent in path.parents:
            if parent == root:
                break
            if parent.exists() and not parent.is_dir():
                conflicts.append(str(parent.relative_to(root)))
    for name in ("AGENTS.md", "README.md"):
        path = owned_path(root, name)
        if path.exists() and not path.is_file():
            conflicts.append(name)
            continue
        existing = path.read_bytes().decode("utf-8") if path.exists() else ""
        if START in existing or END in existing:
            raise InstallError("Existing Corp entry without matching installation metadata: " + name)
        if existing:
            files[name] = (existing + ("\n" if existing.endswith("\n") else "\n\n") + entry_block(name)).encode()
        else:
            files[name] = (("# " + brief["name"] + "\n\n" if name == "README.md" else "") + entry_block(name)).encode()
    if conflicts:
        raise InstallError("Existing project files need an explicit adaptation; no files written: " + ", ".join(sorted(set(conflicts))))
    manifest = {"version": VERSION, "brief_sha256": input_hash, "payload_sha256": payload_hash,
                "files": {name: digest(content) for name, content in files.items()},
                "authority": "installation provenance only; not task state or readiness"}
    files[MANIFEST] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
    report = {"status": "planned" if dry_run else "installed", "version": VERSION,
              "repo": str(root), "git": state, "files": sorted(files),
              "entry": "docs/corp/README.md",
              "ceiling": "Local installation only; publication, native work setup and independent handoff remain to verify."}
    if dry_run:
        return report
    root.mkdir(parents=True, exist_ok=True)
    if state == "new":
        subprocess.run(["git", "init", "--initial-branch=main", str(root)], check=True,
                       stdout=subprocess.DEVNULL)
    for name, content in files.items():
        path = owned_path(root, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", help="New repository path or existing Git root")
    parser.add_argument("--brief", required=True, help="JSON inputs; see references/brief.md")
    parser.add_argument("--dry-run", action="store_true", help="Inspect the file plan without writes")
    args = parser.parse_args(argv)
    try:
        root = Path(args.repo).expanduser().resolve()
        if root.exists() and not root.is_dir():
            raise InstallError("Repository path is not a directory")
        report = install(root, read_brief(args.brief, root), args.dry_run)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
