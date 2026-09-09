#!/usr/bin/env python3
"""Replay append-only Issue execution comments. A projection, not an atomic lock."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

EVENT_START = re.compile(r"^```agent-event[ \t]*$", re.M)
FENCE = re.compile(r"^```agent-event[ \t]*\n(.*?)\n```[ \t]*$", re.M | re.S)
SHA = re.compile(r"[0-9a-f]{40}")
KINDS = {"claim", "renew", "checkpoint", "release"}


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError("timestamp must be an ISO-8601 string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty string")


def positive(value, label):
    if type(value) is not int or value < 1:
        raise ValueError(f"{label} must be a positive integer")


def strings(value, label, allow_empty=True):
    if not isinstance(value, list) or (not allow_empty and not value):
        raise ValueError(f"{label} must be a list")
    for item in value:
        nonempty(item, label)


def validate_recovery(value):
    if not isinstance(value, dict):
        raise ValueError("recovery must be an object")
    required = {"commit", "branch", "artifacts", "done", "checks", "remaining", "next", "waiting_on"}
    if not required <= value.keys():
        raise ValueError("recovery is missing required fields")
    commit, branch = value["commit"], value["branch"]
    if commit is not None:
        if not isinstance(commit, str) or not SHA.fullmatch(commit):
            raise ValueError("recovery commit must be a full lowercase Git SHA or null")
        nonempty(branch, "recovery branch")
    elif branch is not None:
        nonempty(branch, "recovery branch")
    for key in ("done", "remaining", "next"):
        nonempty(value[key], key)
    for key in ("artifacts", "checks", "waiting_on"):
        strings(value[key], key)
    for locator in value["artifacts"]:
        if not locator.startswith("https://"):
            raise ValueError("recovery artifacts must be shared HTTPS locators, not local paths")


def events_from_comments(data):
    if not isinstance(data, list):
        raise ValueError("comments must be an array or an array of pages")
    comments = []
    for entry in data:
        comments.extend(entry if isinstance(entry, list) else [entry])
    events, seen = [], set()
    for comment in comments:
        if not isinstance(comment, dict):
            raise ValueError("each comment must be an object")
        cid = comment.get("id")
        positive(cid, "comment id")
        if cid in seen:
            raise ValueError(f"duplicate comment id: {cid}")
        seen.add(cid)
        body = comment.get("body")
        if not isinstance(body, str):
            raise ValueError("comment body must be a string")
        body = body.replace("\r\n", "\n").replace("\r", "\n")
        starts = EVENT_START.findall(body)
        if not starts:
            continue
        matches = FENCE.findall(body)
        if len(starts) != 1 or len(matches) != 1:
            raise ValueError(f"comment {cid}: malformed or multiple agent-event fences")
        event = json.loads(matches[0], object_pairs_hook=unique_object)
        if not isinstance(event, dict) or event.get("event") not in KINDS:
            raise ValueError(f"comment {cid}: invalid event kind")
        nonempty(event.get("instance"), "instance")
        created = timestamp(comment.get("created_at"))
        # Edits destroy the ordering/evidence contract; do not silently replay them.
        if comment.get("updated_at") and timestamp(comment["updated_at"]) != created:
            raise ValueError(f"comment {cid}: machine event was edited")
        events.append((cid, created, event))
    return sorted(events, key=lambda row: row[0])


def replay(data, at):
    now = timestamp(at)
    holder = None
    latest = None
    rejected = []
    previous_time = None
    for cid, created, event in events_from_comments(data):
        if previous_time is not None and created < previous_time:
            raise ValueError("server comment order and timestamps disagree")
        previous_time = created
        if created > now:
            raise ValueError("observation time precedes a supplied event")
        if holder and created >= timestamp(holder["lease_until"]):
            holder = None
        kind = event["event"]
        if kind == "claim":
            if "workgroup" in event:
                nonempty(event["workgroup"], "workgroup")
            nonempty(event.get("base_commit"), "base_commit")
            if not SHA.fullmatch(event["base_commit"]):
                raise ValueError("base_commit must be a full lowercase Git SHA")
            if event.get("branch") is not None:
                nonempty(event["branch"], "branch")
            strings(event.get("scope"), "scope", allow_empty=False)
            expiry = timestamp(event.get("lease_until"))
            if expiry <= created:
                raise ValueError("claim must expire after its server creation time")
            if holder:
                rejected.append({"id": cid, "reason": "already-held"})
            else:
                holder = {**event, "id": cid, "created_at": created.isoformat()}
            continue
        positive(event.get("claim"), "claim reference")
        if not holder or event["claim"] != holder["id"] or event["instance"] != holder["instance"]:
            rejected.append({"id": cid, "reason": "stale-or-nonholder"})
            continue
        if kind == "renew":
            expiry = timestamp(event.get("lease_until"))
            if expiry <= timestamp(holder["lease_until"]):
                rejected.append({"id": cid, "reason": "renewal-not-extended"})
                continue
            holder = {**holder, "lease_until": event["lease_until"]}
        elif kind == "checkpoint":
            validate_recovery(event.get("recovery"))
            latest = {"id": cid, "claim": holder["id"], "instance": event["instance"],
                      "created_at": created.isoformat(), "recovery": event["recovery"]}
        elif kind == "release":
            positive(event.get("checkpoint"), "checkpoint reference")
            nonempty(event.get("reason"), "release reason")
            if not latest or latest["claim"] != holder["id"] or latest["id"] != event["checkpoint"]:
                raise ValueError("release must reference this claim's latest valid checkpoint")
            holder = None
    if holder and now >= timestamp(holder["lease_until"]):
        holder = None
    return {"observed_at": now.isoformat(), "current_claim": holder, "latest_checkpoint": latest,
            "rejected_events": rejected,
            "ceiling": "projection-only; verify freshness, completeness and shared artifacts before writing"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="REST comments JSON file or - for stdin")
    parser.add_argument("--at", required=True, help="trusted observation time including timezone")
    args = parser.parse_args()
    try:
        text = sys.stdin.read() if args.path == "-" else Path(args.path).read_text(encoding="utf-8")
        data = json.loads(text, object_pairs_hook=unique_object)
        print(json.dumps(replay(data, args.at), ensure_ascii=False, indent=2))
        return 0
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
