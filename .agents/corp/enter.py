#!/usr/bin/env python3
"""Observe a remote baseline and optionally create an independent working tree."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import uuid


class EntryError(ValueError):
    pass


def git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                            text=True, timeout=45)
    if result.returncode:
        raise EntryError("Git operation failed: " + args[0] + "; inspect the repository/network locally")
    return result.stdout.strip()


def enter(root, destination=None, remote="origin", branch=None, dry_run=False):
    root = Path(root).expanduser().resolve(strict=True)
    if Path(git(root, "rev-parse", "--show-toplevel")).resolve() != root:
        raise EntryError("Use the actual Git root")
    if remote not in git(root, "remote").splitlines():
        raise EntryError("Select an existing named Git remote")
    # Use its URL for both reads and fetch, so a later config edit cannot switch repositories.
    url = git(root, "remote", "get-url", remote)
    if not branch:
        refs = git(root, "ls-remote", "--symref", url, "HEAD")
        matches = re.findall(r"^ref: refs/heads/(.+)\tHEAD$", refs, re.M)
        if len(matches) != 1:
            raise EntryError("Remote default branch is unresolved; specify the actual --branch")
        branch = matches[0]
    git(root, "check-ref-format", "--branch", branch)
    refs = git(root, "ls-remote", url, "refs/heads/" + branch)
    match = re.fullmatch(r"([0-9a-f]{40})\trefs/heads/" + re.escape(branch), refs)
    if not match:
        raise EntryError("Remote branch did not resolve to a unique Git SHA")
    sha = match[1]
    before_head = git(root, "rev-parse", "HEAD")
    before_status = git(root, "status", "--porcelain=v1", "--untracked-files=all")
    result = {"status": "observed", "repo": str(root), "remote": remote,
              "remote_branch": branch, "remote_commit": sha,
              "local_head": before_head, "local_changes": bool(before_status),
              "ceiling": "Pinned remote observation; original checkout is not updated. Task inputs and runtime rule reload remain separate."}
    if not destination:
        return result
    destination = Path(destination).expanduser().absolute()
    if destination.exists() or destination.is_symlink():
        raise EntryError("Worktree destination already exists")
    destination = destination.resolve()
    if destination == root or root in destination.parents:
        raise EntryError("Put the new worktree outside the original checkout")
    result.update(status="planned", checkout=str(destination))
    if dry_run:
        return result
    git(root, "fetch", "--no-write-fetch-head", url, sha)
    if git(root, "rev-parse", sha + "^{commit}") != sha:
        raise EntryError("Fetched object did not match the pinned commit")
    work_branch = "corpo/" + uuid.uuid4().hex[:12]
    git(root, "worktree", "add", "-b", work_branch, str(destination), sha)
    if git(destination, "rev-parse", "HEAD") != sha:
        raise EntryError("Created checkout did not match pinned commit; inspect the new checkout")
    if git(root, "rev-parse", "HEAD") != before_head or git(root, "status", "--porcelain=v1", "--untracked-files=all") != before_status:
        raise EntryError("Original checkout changed during entry; reconcile concurrent changes before working")
    result.update(status="checkout_created", branch=work_branch,
                  entry=str(destination / "AGENTS.md"),
                  next="Read the new checkout's root/path rules in the worker runtime, then verify the actual task and execution rights.")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--worktree", help="New independent checkout destination; omit for read-only observation")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--branch", help="Remote branch; defaults to its native HEAD")
    parser.add_argument("--dry-run", action="store_true", help="Read the live remote and plan; no fetch or worktree writes")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(enter(args.repo, args.worktree, args.remote, args.branch, args.dry_run),
                         ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
