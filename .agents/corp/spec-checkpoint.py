#!/usr/bin/env python3
"""Hash the unique normative Spec area of a GitHub Issue body (no network)."""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

START = "<!-- spec:start -->"
END = "<!-- spec:end -->"
SHA256_RE = re.compile(r"[0-9a-f]{64}")


def valid_source(value: str) -> bool:
    """Shared record syntax only; does not prove reachability or decision authority."""
    if (not isinstance(value, str) or not value.startswith("https://")
            or re.search(r'[\s<>"`\\\x00-\x1f\x7f]', value)):
        return False
    try:
        parts = urlsplit(value)
        parts.port  # Validate malformed/out-of-range ports without connecting.
        return bool(parts.hostname) and parts.username is None and parts.password is None
    except ValueError:
        return False


def normalize_body(raw: bytes) -> bytes:
    text = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip(" \t") for line in text.split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return ("\n".join(lines) + "\n").encode("utf-8") if lines else b""


def spec_area(raw: bytes) -> bytes:
    text = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    if text.count(START) != 1 or text.count(END) != 1:
        raise ValueError("expected exactly one spec:start and one spec:end marker")
    lines = text.split("\n")
    if START not in lines or END not in lines:
        raise ValueError("Spec markers must occupy their own lines")
    start, end = lines.index(START), lines.index(END)
    if start >= end:
        raise ValueError("Spec markers are out of order")
    result = normalize_body("\n".join(lines[start + 1:end]).encode("utf-8"))
    if not result.strip():
        raise ValueError("Spec area is empty")
    return result


def digest_body(raw: bytes) -> str:
    return hashlib.sha256(spec_area(raw)).hexdigest()


def self_test() -> None:
    a = f"{START}\nOutcome: one\n{END}\n".encode()
    b = f"Progress outside\n{START}\r\nOutcome: one  \r\n{END}\r\n".encode()
    assert digest_body(a) == digest_body(b)
    assert digest_body(a) != digest_body(a.replace(b"one", b"two"))
    for invalid in (b"", f"{START}\n{END}".encode(), a + a):
        try:
            digest_body(invalid)
        except ValueError:
            continue
        raise AssertionError("invalid Spec accepted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="-", help="UTF-8 Issue body file or stdin")
    parser.add_argument("--check", metavar="SHA256")
    parser.add_argument("--checkpoint", action="store_true")
    parser.add_argument("--issue", type=int)
    parser.add_argument("--source", help="shared decision locator")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("Spec checkpoint self-test passed.")
        return 0
    try:
        raw = sys.stdin.buffer.read() if args.path == "-" else Path(args.path).read_bytes()
        digest = digest_body(raw)
        if args.check is not None:
            if not SHA256_RE.fullmatch(args.check):
                raise ValueError("--check must be 64 lowercase hexadecimal characters")
            if digest != args.check:
                print(f"ERROR: Spec hash mismatch (actual {digest})", file=sys.stderr)
                return 1
        if args.checkpoint:
            if args.issue is None or args.issue < 1:
                raise ValueError("--checkpoint requires a positive --issue")
            if not valid_source(args.source):
                raise ValueError("--checkpoint requires a shared HTTPS --source without credentials or unsafe characters")
            print(f"SPEC_ACCEPTED issue={args.issue} spec_sha256={digest} source={args.source}")
        else:
            print(digest)
        return 0
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
