#!/usr/bin/env python3
"""Check local Corp wiring and an explicit Git difference; no network or business tests."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

sys.dont_write_bytecode = True


class CheckError(ValueError):
    pass


def command(root, args, *, input=None, allowed=(0,)):
    result = subprocess.run(args, cwd=root, input=input, text=True, capture_output=True)
    if result.returncode not in allowed:
        raise CheckError(" ".join(args) + "\n" + (result.stderr or result.stdout).strip())
    return result


def git(root, *args):
    return command(root, ["git", *args]).stdout.strip()


def local_target(root, parent, target):
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    path = (parent / unquote(parsed.path)).resolve()
    if not path.is_relative_to(root):
        raise CheckError("Local reference leaves the repository: " + target)
    if not path.exists():
        raise CheckError("Missing local target: " + target)
    return path


def check_structure(root, report):
    scripts = root / ".agents/corp"
    # Reuse the native reader's existing narrow Canon format.
    definition = importlib.util.spec_from_file_location("corp_check_context", scripts / "repo-context.py")
    context = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(context)
    mapping = root / "docs/corp/canon-map.yaml"
    rows = context.parse_map(mapping.read_text(encoding="utf-8"))
    if not any(row["id"] == "current-delivery-focus" for row in rows):
        raise CheckError("Missing required Canon route: current-delivery-focus")
    report["unverified_routes"] = []
    for row in rows:
        target = row["target"]
        if row["status"] != "active":
            report["unverified_routes"].append(row)
        elif not isinstance(target, str) or not target:
            raise CheckError("Active Canon route has no target: " + row["id"])
        elif urlsplit(target).scheme or urlsplit(target).netloc:
            report["unverified_routes"].append({**row, "reason": "remote; not contacted"})
        else:
            local_target(root, root, target)

    entry = root / "docs/corp/README.md"
    if not entry.is_file():
        raise CheckError("Missing Corp entry: docs/corp/README.md")
    documents = list((root / "docs/corp").glob("*.md"))
    # Check methods referenced by the Corp, not unrelated project skills.
    method_refs = set()
    for path in documents:
        method_refs.update(re.findall(r"\.agents/skills/[\w-]+/SKILL\.md", path.read_text(encoding="utf-8")))
    methods = [root / name for name in sorted(method_refs)]
    documents.extend(methods)
    for path in methods:
        text = path.read_text(encoding="utf-8")
        front = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
        if not front or not all(re.search(r"(?m)^" + key + r":\s*\S", front[1])
                                for key in ("name", "description")):
            raise CheckError("Missing skill front matter: " + path.relative_to(root).as_posix())
    checked_links = 0
    for path in documents:
        text = path.read_text(encoding="utf-8")
        for destination in re.findall(r"\[[^\]\n]+\]\(([^)\n]+)\)", text):
            target = re.match(r"\s*(?:<([^>]+)>|(\S+?))(?:\s+[\"'].*[\"'])?\s*$", destination)
            if not target:
                raise CheckError("Unsupported local link syntax in " + path.relative_to(root).as_posix())
            local_target(root, path.parent, target[1] or target[2])
            checked_links += 1
        for target in set(re.findall(r"(?<![\w./])(?:docs/corp|\.agents/(?:corp|skills))/[\w./-]+", text)):
            local_target(root, root, target.rstrip("."))
            checked_links += 1
    for name in ("AGENTS.md", "README.md"):
        text = (root / name).read_text(encoding="utf-8")
        if "docs/corp/README.md" not in text:
            raise CheckError("Missing Corp entry reference in " + name)
    helpers = list(scripts.glob("*.py"))
    for path in helpers:
        compile(path.read_bytes(), path.relative_to(root).as_posix(), "exec")
    command(root, [sys.executable, str(scripts / "spec-checkpoint.py"), "--self-test"])
    report["structure"] = {"documents": len(documents), "methods": len(methods),
                           "references": checked_links, "python_helpers": len(helpers),
                           "spec_self_check": "passed"}


def resolve_commit(root, value):
    if not isinstance(value, str) or not value or value.startswith("-"):
        raise CheckError("A nonempty Git commit/ref is required")
    result = command(root, ["git", "rev-parse", "--verify", "--end-of-options", value + "^{commit}"],
                     allowed=(0, 1, 128))
    if result.returncode:
        raise CheckError("Required Git baseline is unavailable: " + value)
    return result.stdout.strip()


def git_difference(root, explicit_base, report):
    if Path(git(root, "rev-parse", "--show-toplevel")).resolve() != root:
        raise CheckError("Run the installed helper from its actual repository root")
    probe = command(root, ["git", "rev-parse", "--verify", "--quiet", "HEAD"], allowed=(0, 1))
    head = probe.stdout.strip() or None
    report["git"] = {"head": head}
    dirty = bool(command(root, ["git", "status", "--porcelain", "--untracked-files=normal"]).stdout)
    report["git"]["dirty"] = dirty
    event = os.environ.get("GITHUB_EVENT_NAME")
    event_data = {}
    if event:
        event_path = os.environ.get("GITHUB_EVENT_PATH")
        if not event_path:
            raise CheckError("GITHUB_EVENT_PATH is required for a CI event")
        event_data = json.loads(Path(event_path).read_text(encoding="utf-8"))
        if not isinstance(event_data, dict):
            raise CheckError("CI event must be an object")
    evidence = {key: os.environ[key] for key in ("GITHUB_EVENT_NAME", "GITHUB_SHA", "GITHUB_REF",
                "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_JOB", "GITHUB_ACTION",
                "GITHUB_REPOSITORY", "GITHUB_SERVER_URL") if os.environ.get(key)}
    report["git"]["ci"] = evidence
    if event == "pull_request":
        pull = event_data.get("pull_request")
        if not isinstance(pull, dict) or not all(isinstance(pull.get(key, {}), dict) for key in ("base", "head")):
            raise CheckError("Malformed pull_request version evidence")
        evidence["pr_head"] = pull.get("head", {}).get("sha")
        evidence["pr_base"] = pull.get("base", {}).get("sha")
    if explicit_base is not None:
        base, source = explicit_base, "explicit --base"
    elif event == "pull_request":
        base, source = evidence["pr_base"], "pull_request.base.sha"
    elif event == "push":
        base, source = event_data.get("before"), "push.before"
        if isinstance(base, str) and re.fullmatch(r"0{40}", base):
            base = "empty"
    elif event == "workflow_dispatch":
        if not head:
            raise CheckError("A manual CI run requires a checked-out commit")
        parents = re.findall(r"(?m)^parent ([0-9a-f]{40})$", git(root, "cat-file", "-p", head))
        base, source = (parents[0] if parents else "empty"), "manual previous commit (initial: whole tree)"
    elif event:
        raise CheckError("Unsupported CI event; provide --base explicitly: " + event)
    else:
        base, source = (head or "empty"), "local HEAD plus working tree (initial: whole tree)"
    report["git"].update(requested_base=base, base_source=source)
    if not base:
        raise CheckError("Required Git baseline is missing: " + source)
    resolved = (command(root, ["git", "hash-object", "-t", "tree", "--stdin"], input="").stdout.strip()
                if base == "empty" else resolve_commit(root, base))
    tracked = command(root, ["git", "diff", "--name-only", "-z", resolved, "--"]).stdout
    untracked = command(root, ["git", "ls-files", "--others", "--exclude-standard", "-z"]).stdout
    difference = {"head": head, "base": resolved, "base_source": source,
                  "range": ("empty tree" if base == "empty" else resolved) + " -> working tree",
                  "tracked_changes": [x for x in tracked.split("\0") if x],
                  "untracked": [x for x in untracked.split("\0") if x], "ci": evidence}
    difference["dirty"] = dirty
    return difference


def check_difference(root, difference):
    command(root, ["git", "diff", "--check", difference["base"], "--"])
    for name in difference["untracked"]:
        # --no-index sets bit 1 for differences and bit 2 for whitespace failures.
        command(root, ["git", "diff", "--no-index", "--check", "--", os.devnull, name], allowed=(0, 1))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="Git baseline, or 'empty' for the whole initial tree")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    report = {"status": "failed", "command": ["python3", ".agents/corp/check.py", *(argv if argv is not None else sys.argv[1:])],
              "python": sys.version.split()[0], "scope": "Local Corp wiring and Git difference; no network or business tests",
              "errors": []}
    try:
        report["git"] = git_difference(root, args.base, report)
        check_difference(root, report["git"])
        check_structure(root, report)
        report["status"] = "passed"
    except (OSError, ValueError, SyntaxError) as exc:
        report["errors"].append(str(exc))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
