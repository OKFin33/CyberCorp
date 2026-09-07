#!/usr/bin/env python3
"""Start any user-configured CLI with explicit argv; no native session assumptions."""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import uuid

from launch_input import LaunchError, directory, repository, start_prompt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("start",))
    parser.add_argument("--repo", required=True)
    parser.add_argument("--cwd")
    parser.add_argument("--dry-run", action="store_true", help="Print the command without starting the CLI")
    # The explicit -- boundary leaves all runtime flags, including --help, to that CLI.
    raw = sys.argv[1:] if argv is None else argv
    if "--" not in raw:
        parser.error("Supply the native CLI command after --; use {prompt} as one whole argument")
    boundary = raw.index("--")
    args = parser.parse_args(raw[:boundary])
    command = raw[boundary + 1:]
    if len(command) < 2 or "{prompt}" not in command[1:]:
        parser.error("The command needs an executable and a whole {prompt} argument")
    try:
        repo = repository(args.repo)
        cwd = directory(args.cwd) if args.cwd else repo
        executable = shutil.which(command[0])
        if not executable:
            raise LaunchError("CLI not found; the user owns installation and login: " + command[0])
        executable = str(Path(executable).resolve())
        tag = str(uuid.uuid4())
        values = {"{repo}": str(repo), "{cwd}": str(cwd), "{prompt}": start_prompt(repo, tag)}
        command = [executable, *[values.get(arg, arg) for arg in command[1:]]]
        if args.dry_run:
            print(json.dumps({"status": "planned", "cwd": str(cwd), "argv": command,
                              "launch_tag": tag, "session_id": None,
                              "ceiling": "Command plan only; CLI support, login, tools and native sessions remain user-configured."},
                             ensure_ascii=False, indent=2))
            return 0
        os.chdir(cwd)
        os.execv(executable, command)
    except (LaunchError, OSError, ValueError) as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
