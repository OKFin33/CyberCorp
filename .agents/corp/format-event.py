#!/usr/bin/env python3
"""Check a prospective execution event against fetched comments and print its fence."""
import argparse
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("work_state", Path(__file__).with_name("work-state.py"))
work = importlib.util.module_from_spec(spec)
spec.loader.exec_module(work)


def format_event(event, comments, at):
    rows = []
    for page in comments:
        rows.extend(page if isinstance(page, list) else [page])
    # First replay preserves invalid-history failures instead of hiding them with a new event.
    work.replay(rows, at)
    cid = max((row["id"] for row in rows), default=0) + 1
    body = "```agent-event\n" + json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n```"
    report = work.replay(rows + [{"id": cid, "created_at": at, "body": body}], at)
    if any(row["id"] == cid for row in report["rejected_events"]):
        raise ValueError("Prospective event would be rejected against these comments")
    return body


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("event", help="JSON event file")
    parser.add_argument("--comments", required=True, help="Fresh complete native comments JSON")
    parser.add_argument("--at", default=None, help="Observation UTC time; defaults to current time")
    args = parser.parse_args(argv)
    try:
        event = json.loads(Path(args.event).read_text(), object_pairs_hook=work.unique_object)
        comments = json.loads(Path(args.comments).read_text(), object_pairs_hook=work.unique_object)
        print(format_event(event, comments, args.at or datetime.now(timezone.utc).isoformat()))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
