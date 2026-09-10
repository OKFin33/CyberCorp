#!/usr/bin/env python3
"""Run CyberCorp's local wiring/difference check, then its repository tests."""
from pathlib import Path
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parents[1]
    for command in ([sys.executable, ".agents/corp/check.py", *sys.argv[1:]],
                    [sys.executable, "-m", "unittest", "discover", "-s", "tests"]):
        print("+ " + " ".join(command), flush=True)
        result = subprocess.run(command, cwd=root)
        if result.returncode:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
