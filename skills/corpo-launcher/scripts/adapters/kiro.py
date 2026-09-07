#!/usr/bin/env python3
"""Thin Kiro launch adapter. Repository and Kiro remain the state owners."""
import argparse
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import uuid


from launch_input import LaunchError, directory, repository, start_prompt


def executable(value):
    result = shutil.which(value)
    if not result:
        raise LaunchError("kiro-cli executable not found; install/login using Kiro's normal setup")
    return str(Path(result).resolve(strict=True))


def native_sessions(cli, cwd):
    try:
        result = subprocess.run(
            [cli, "chat", "--list-sessions", "--format", "json"],
            cwd=cwd, capture_output=True, text=True, timeout=30, check=False,
        )
    except subprocess.TimeoutExpired:
        raise LaunchError("Native session discovery timed out; no launch/retry performed")
    if result.returncode:
        raise LaunchError("Native session discovery failed; inspect Kiro locally (output withheld)")
    try:
        envelopes = json.loads(result.stdout)
    except (ValueError, TypeError):
        raise LaunchError("Unexpected native session JSON; refusing to guess")
    if not isinstance(envelopes, list):
        raise LaunchError("Unexpected native session envelope")
    selected = []
    seen = set()
    matched_cwd = False
    for envelope in envelopes:
        if not isinstance(envelope, dict) or not isinstance(envelope.get("cwd"), str):
            raise LaunchError("Malformed native cwd envelope")
        if Path(envelope["cwd"]).expanduser().resolve() != cwd:
            continue
        matched_cwd = True
        if envelope.get("complete") is not True or not isinstance(envelope.get("sessions"), list):
            raise LaunchError("Incomplete native session list; refusing to infer identity")
        for item in envelope["sessions"]:
            if not isinstance(item, dict):
                raise LaunchError("Malformed native session")
            sid, title = item.get("sessionId"), item.get("title")
            if not isinstance(sid, str) or not sid or not isinstance(title, str):
                raise LaunchError("Malformed native session identity")
            if sid in seen:
                raise LaunchError("Ambiguous duplicate native session identity")
            seen.add(sid)
            selected.append({k: item.get(k) for k in (
                "sessionId", "title", "source", "updatedAt", "messageCount"
            )})
    if not matched_cwd:
        raise LaunchError("Native listing did not establish completeness for this cwd")
    return selected


def plan(args):
    cli = executable(args.kiro)
    repo = repository(args.repo) if args.command == "start" else None
    cwd = directory(args.cwd) if args.cwd else repo
    if cwd is None:
        raise LaunchError("--cwd is required for resume")
    if args.background and args.tools != "all":
        raise LaunchError("Background mode needs explicit --tools all; otherwise use an interactive terminal")
    if args.session and (args.session.startswith("-") or not re.fullmatch(r"[A-Za-z0-9_-]+", args.session)):
        raise LaunchError("Invalid session ID")
    tag = str(uuid.uuid4()) if repo else None
    argv = [cli, "chat"]
    if repo:
        argv += ["--agent", args.agent]
    else:
        argv += ["--resume-id", args.session]
    argv += ["--model", args.model]
    if args.tools == "all":
        argv += ["--trust-all-tools"]
    if args.background:
        argv += ["--no-interactive"]
    prompt = start_prompt(repo, tag) if repo else (
        "继续此会话原任务。先依仓库核对当前事实与执行权，不将旧缓存当作当前事实。"
        "本次工具确认方式不扩大项目或外部影响授权；本次没有 merge 授权。"
    )
    argv.append(prompt)
    return cli, cwd, argv, tag


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2), flush=True)


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("start", "resume"):
        q = sub.add_parser(name)
        q.add_argument("--kiro", default="kiro-cli", help="Installed executable name or path")
        q.add_argument("--cwd", help="Launch cwd; defaults to --repo for start")
        q.add_argument("--model", default="claude-opus-5", help="Explicit request; never silently falls back")
        q.add_argument("--tools", choices=("ask", "all"), default="ask")
        q.add_argument("--background", action="store_true", help="Detach with private local output; requires --tools all")
        q.add_argument("--dry-run", action="store_true", help="Print argv without model launch or session discovery")
        if name == "start":
            q.add_argument("--repo", required=True)
            q.add_argument("--agent", default="kiro_default")
            q.set_defaults(session=None)
        else:
            q.add_argument("--session", required=True)
            q.set_defaults(repo=None, agent=None)
    q = sub.add_parser("sessions", help="Read native cwd-scoped session metadata, not conversation contents")
    q.add_argument("--kiro", default="kiro-cli")
    q.add_argument("--cwd", required=True)
    q.add_argument("--match", help="Exact launch_tag returned by start; does not select newest session")
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "sessions":
            cwd = directory(args.cwd)
            sessions = native_sessions(executable(args.kiro), cwd)
            if args.match:
                tag = str(uuid.UUID(args.match))
                prefix = f"[corpo:{tag}]"
                sessions = [s for s in sessions if s["title"].startswith(prefix)]
                status = "unique_match" if len(sessions) == 1 else "unresolved"
            else:
                status = "native_listing"
            emit({"status": status, "cwd": str(cwd), "sessions": sessions})
            return 0 if status != "unresolved" else 2
        cli, cwd, command, tag = plan(args)
        report = {
            "status": "planned", "cwd": str(cwd), "requested_model": args.model,
            "tool_approval": args.tools, "launch_tag": tag,
            "session_id": args.session, "argv": command,
            "ceiling": "Launch parameters only; not model verification, execution rights, or work acceptance",
        }
        if args.dry_run:
            emit(report)
            return 0
        if not args.background and not (sys.stdin.isatty() and sys.stdout.isatty()):
            raise LaunchError("Interactive mode requires a terminal; do not silently enable automatic approval")
        if args.command == "resume":
            sessions = native_sessions(cli, cwd)
            if sum(s["sessionId"] == args.session for s in sessions) != 1:
                raise LaunchError("Resume session not uniquely present in this cwd; refusing to launch")
        if not args.background:
            report["status"] = "interactive_handoff"
            emit(report)
            os.chdir(cwd)
            os.execv(cli, command)
        output_dir = Path(tempfile.mkdtemp(prefix="kiro-corpo-"))
        log = output_dir / "output.log"
        try:
            fd = os.open(log, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "wb") as stream:
                child = subprocess.Popen(command, cwd=cwd, stdin=subprocess.DEVNULL,
                                         stdout=stream, stderr=subprocess.STDOUT,
                                         start_new_session=True)
        except OSError:
            raise LaunchError(f"Spawn failed; diagnostics directory retained at {output_dir}; no retry")
        report.pop("argv")
        report.update(status="process_spawned", pid=child.pid, output_log=str(log))
        listing = [sys.executable, str(Path(__file__).resolve()), "sessions", "--cwd", str(cwd), "--kiro", cli]
        if tag:
            listing += ["--match", tag]
        report["locate_command"] = shlex.join(listing)
        report["ceiling"] = "Process created only. Inspect its log and native session metadata before claiming startup/work success."
        emit(report)
        return 0
    except (LaunchError, OSError, ValueError) as exc:
        emit({"status": "error", "message": str(exc)})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
