#!/usr/bin/env python3
"""Hash the spec region of a GitHub Issue body to pin what was accepted (S1)."""
import argparse
import hashlib
import re
import sys
from urllib.parse import urlsplit

START = "<!-- spec:start -->"
END = "<!-- spec:end -->"

_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_FORBIDDEN_SOURCE_CHARS = re.compile(r"[\s<>\"`\\]|[\x00-\x1f\x7f]")


class SpecCheckpointError(ValueError):
    pass


def _to_text(data):
    if isinstance(data, bytes):
        data = data.decode("utf-8")
    return data.replace("\r\n", "\n").replace("\r", "\n")


def extract_spec_area(data):
    text = _to_text(data)
    if text.count(START) != 1 or text.count(END) != 1:
        raise SpecCheckpointError("expected exactly one spec:start and one spec:end marker")
    lines = text.split("\n")
    start_indexes = [i for i, line in enumerate(lines) if line == START]
    end_indexes = [i for i, line in enumerate(lines) if line == END]
    if len(start_indexes) != 1 or len(end_indexes) != 1:
        raise SpecCheckpointError("Spec markers must occupy their own lines")
    start_index, end_index = start_indexes[0], end_indexes[0]
    if start_index >= end_index:
        raise SpecCheckpointError("Spec markers are out of order")
    area_lines = lines[start_index + 1:end_index]
    normalized = normalize_spec_area(area_lines)
    if not normalized.decode("utf-8").strip():
        raise SpecCheckpointError("Spec area is empty")
    return normalized


def normalize_spec_area(lines):
    stripped = [line.rstrip(" \t") for line in lines]
    while stripped and stripped[-1] == "":
        stripped.pop()
    if not stripped:
        return b""
    return ("\n".join(stripped) + "\n").encode("utf-8")


def spec_hash(data):
    return hashlib.sha256(extract_spec_area(data)).hexdigest()


def validate_source(source):
    if not isinstance(source, str) or not source.startswith("https://"):
        raise SpecCheckpointError("Invalid --source: must be an https:// URL")
    if _FORBIDDEN_SOURCE_CHARS.search(source):
        raise SpecCheckpointError("Invalid --source: contains forbidden characters")
    try:
        parsed = urlsplit(source)
    except ValueError:
        raise SpecCheckpointError("Invalid --source: could not be parsed")
    if not parsed.hostname:
        raise SpecCheckpointError("Invalid --source: missing hostname")
    if parsed.username or parsed.password:
        raise SpecCheckpointError("Invalid --source: must not carry credentials")
    try:
        parsed.port
    except ValueError:
        raise SpecCheckpointError("Invalid --source: invalid port")
    return source


def read_input(path):
    if path == "-":
        return sys.stdin.buffer.read()
    with open(path, "rb") as handle:
        return handle.read()


def self_test():
    body = "before\n" + START + "\nOutcome: X\nBoundary: Y\n" + END + "\nafter\n"
    digest = spec_hash(body)
    if spec_hash(body.replace("\n", "\r\n")) != digest:
        raise AssertionError("CRLF input changed the hash")
    trailing_ws = body.replace("Outcome: X", "Outcome: X   \t")
    if spec_hash(trailing_ws) != digest:
        raise AssertionError("trailing whitespace changed the hash")
    trailing_blank = body.replace(END, "\n\n\n" + END)
    if spec_hash(trailing_blank) != digest:
        raise AssertionError("trailing blank lines changed the hash")
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise AssertionError("hash is not a lowercase hex sha256")

    def expect_error(bad, message):
        try:
            spec_hash(bad)
        except SpecCheckpointError as exc:
            if message not in str(exc):
                raise AssertionError("wrong error for %r: %s" % (bad, exc))
        else:
            raise AssertionError("expected error for %r" % (bad,))

    expect_error("no markers here", "expected exactly one spec:start and one spec:end marker")
    expect_error(START + "\nA\n" + END + "\n" + START + "\nB\n" + END,
                "expected exactly one spec:start and one spec:end marker")
    expect_error(END + "\nA\n" + START, "Spec markers are out of order")
    expect_error("prefix " + START + "\nA\n" + END, "Spec markers must occupy their own lines")
    expect_error(START + "\nA\n" + END + " suffix", "Spec markers must occupy their own lines")
    expect_error(START + "\n" + END, "Spec area is empty")
    expect_error(START + "\n   \n\t\n" + END, "Spec area is empty")

    if validate_source("https://github.com/o/r/issues/1") != "https://github.com/o/r/issues/1":
        raise AssertionError("valid source was rejected")
    for bad_source in ("http://github.com/o/r", "https://user:pass@github.com/o/r",
                       "https://github.com/o r", "not-a-url", "https://"):
        try:
            validate_source(bad_source)
        except SpecCheckpointError:
            pass
        else:
            raise AssertionError("expected rejection for source %r" % (bad_source,))
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", help="File path, or - for stdin")
    parser.add_argument("--check", metavar="SHA256")
    parser.add_argument("--checkpoint", action="store_true")
    parser.add_argument("--issue", type=int)
    parser.add_argument("--source")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    try:
        if args.self_test:
            self_test()
            print("Spec checkpoint self-test passed.")
            return 0

        if args.path is None:
            data = read_input("-")
        else:
            data = read_input(args.path)
        actual = spec_hash(data)

        if args.checkpoint:
            if args.issue is None or args.issue <= 0:
                raise SpecCheckpointError("--checkpoint requires a positive --issue")
            source = validate_source(args.source)
            print("SPEC_ACCEPTED issue=%d spec_sha256=%s source=%s" % (args.issue, actual, source))
            return 0

        if args.check is not None:
            if not _SHA256_RE.fullmatch(args.check):
                raise SpecCheckpointError("--check value must be a 64-character lowercase hex sha256")
            if args.check != actual:
                print("ERROR: Spec hash mismatch (actual %s)" % actual, file=sys.stderr)
                return 1
            print(actual)
            return 0

        print(actual)
        return 0
    except (OSError, UnicodeError, ValueError) as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
