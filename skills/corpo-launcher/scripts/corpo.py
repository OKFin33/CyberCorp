#!/usr/bin/env python3
"""Dispatch to a CLI adapter; the user owns each runtime integration."""
import argparse
import os
from pathlib import Path
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--runtime", choices=("cli", "kiro"), help="Bundled CLI bridge or Kiro example")
    selection.add_argument("--adapter", type=Path, help="User-owned Python adapter; executed as local code")
    parser.add_argument("arguments", nargs=argparse.REMAINDER, help="Arguments passed unchanged to the adapter")
    args = parser.parse_args(argv)
    adapter = (args.adapter.expanduser().resolve() if args.adapter else
               Path(__file__).resolve().parent / "adapters" / (args.runtime + ".py"))
    if not adapter.is_file():
        parser.error("Adapter not found: " + str(adapter))
    # Preserve the terminal, environment, native exit status and exact argument boundaries.
    os.execv(sys.executable, [sys.executable, str(adapter), *args.arguments])


if __name__ == "__main__":
    main()
