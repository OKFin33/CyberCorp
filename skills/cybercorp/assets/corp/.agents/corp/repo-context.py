#!/usr/bin/env python3
"""Read a bounded GitHub observation into a compact JSON context projection."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parents[2]

_ID_RE = re.compile(r"[a-z][a-z0-9-]*")
_SCALAR_RE = re.compile(r"[A-Za-z0-9_./:@-]+")
_STATUSES = {"active", "pending-relocation", "unresolved"}


class RepoContextError(ValueError):
    pass


class Unreachable(RepoContextError):
    """The shared work surface exists but could not be read right now — credentials, network,
    permissions. Unlike a repository that is not a Corp, this says nothing about whether work
    may proceed: suspend the decisions that depend on this read, and let independent work
    continue. Retrying later is meaningful; concluding "not a Corp" from it is not."""

    hint = ("Could not reach the shared work surface. This does not establish that the repository "
            "is not a Corp — it establishes that this read failed. Suspend the decisions that "
            "depend on it; independent work may continue. Check credentials, network and "
            "repository access, then retry.")


class InconsistentObservation(RepoContextError):
    """Repeated reads disagreed. Unlike an unreadable object, this invalidates the
    observation method itself, so it must never be downgraded into a report error."""



# ---------------------------------------------------------------------------
# Canon map parsing (docs/corp/canon-map.yaml narrow format)
# ---------------------------------------------------------------------------

def _parse_scalar(raw):
    if raw == "null":
        return None
    if raw.startswith('"'):
        try:
            value = json.loads(raw)
        except ValueError:
            raise RepoContextError("unsupported Canon map scalar")
        if not isinstance(value, str):
            raise RepoContextError("unsupported Canon map scalar")
        return value
    if _SCALAR_RE.fullmatch(raw):
        return raw
    raise RepoContextError("unsupported Canon map scalar")


def parse_map(text):
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    block_starts = [i for i, line in enumerate(lines) if line == "canonical_targets:"]
    if len(block_starts) != 1:
        raise RepoContextError("one canonical_targets block required")
    start = block_starts[0] + 1
    end = len(lines)
    for i in range(start, len(lines)):
        if re.match(r"^[A-Za-z0-9_-]+:", lines[i]):
            end = i
            break

    entries = []
    current = None
    seen_ids = set()
    for raw_line in lines[start:end]:
        line = raw_line
        stripped = line.strip()
        if stripped == "" or stripped.startswith("#"):
            continue
        id_match = re.match(r"^  - id: (.*)$", line)
        if id_match:
            value = _parse_scalar(id_match.group(1))
            if not isinstance(value, str) or not _ID_RE.fullmatch(value):
                raise RepoContextError("unsupported Canon map scalar")
            if value in seen_ids:
                raise RepoContextError("Canon map entries must have unique IDs and id/target/status")
            seen_ids.add(value)
            current = {"id": value}
            entries.append(current)
            continue
        field_match = re.match(r"^    (target|status|answers): (.*)$", line)
        if field_match:
            if current is None:
                raise RepoContextError("unsupported or duplicate Canon map field")
            key = field_match.group(1)
            if key in current:
                raise RepoContextError("unsupported or duplicate Canon map field")
            current[key] = _parse_scalar(field_match.group(2))
            continue
        raise RepoContextError("unsupported or duplicate Canon map field")

    if not entries:
        raise RepoContextError("Canon map entries must have unique IDs and id/target/status")
    for entry in entries:
        # `answers` says what question this route answers, so an executor can tell which
        # entry it needs without opening several. Optional: routes written before it existed
        # stay valid, and a project adds it where the id alone is not self-evident.
        if set(entry) - {"answers"} != {"id", "target", "status"}:
            raise RepoContextError("Canon map entries must have unique IDs and id/target/status")
        if entry["status"] not in _STATUSES:
            raise RepoContextError("unsupported Canon map status")
    return entries


# ---------------------------------------------------------------------------
# GitHub reading (injectable)
# ---------------------------------------------------------------------------

class GhReader:
    """Reads GitHub via the `gh` CLI. Replace with a test double for offline tests."""

    def __init__(self, root, timeout=45):
        self.root = root
        self.timeout = timeout

    def read(self, endpoint, paginated=False, list_key=None):
        args = ["gh", "api", "--hostname", "github.com", "--method", "GET", endpoint]
        if paginated:
            args.extend(["--paginate", "--slurp"])
        try:
            result = subprocess.run(args, cwd=self.root, capture_output=True, text=True,
                                    timeout=self.timeout)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise Unreachable("gh api failed for %s: %s" % (endpoint, exc))
        if result.returncode != 0:
            raise Unreachable("gh api failed for %s: %s" % (endpoint, result.stderr.strip()))
        try:
            data = json.loads(result.stdout)
        except ValueError:
            raise RepoContextError("gh api returned non-JSON output for %s" % endpoint)
        if paginated:
            if not isinstance(data, list) or not all(isinstance(page, list) for page in data):
                raise RepoContextError("gh api pagination returned an unexpected shape for %s" % endpoint)
            items = [item for page in data for item in page]
        else:
            items = data
        if list_key is not None:
            if not isinstance(items, dict) or list_key not in items:
                raise RepoContextError("gh api response missing %r for %s" % (list_key, endpoint))
            items = items[list_key]
        return items


class _Tracking:
    """Wraps a reader to record whether any paginated (non-atomic) read occurred."""

    def __init__(self, reader):
        self._reader = reader
        self.used_pagination = False

    def read(self, endpoint, paginated=False, list_key=None):
        if paginated:
            self.used_pagination = True
        return self._reader.read(endpoint, paginated=paginated, list_key=list_key)


# ---------------------------------------------------------------------------
# Repository identity
# ---------------------------------------------------------------------------

def infer_repo(root):
    result = subprocess.run(["git", "remote", "get-url", "origin"], cwd=root,
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise RepoContextError(
            "No origin remote, so there is no shared work surface to observe. Every carrier this "
            "mechanism uses — Issues, Pull Requests, Milestones, assignees — lives on the hosted "
            "repository, so a Corp cannot operate without one. If you are a worker: stop and report "
            "that this repository is not a Corp yet. If you are establishing it: create the hosted "
            "repository and its remote first. (git: " + result.stderr.strip() + ")")
    url = result.stdout.strip()
    match = re.search(r"[:/]([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?$", url)
    if not match:
        raise RepoContextError("Could not infer owner/name from origin remote: " + url)
    return match.group(1) + "/" + match.group(2)


# ---------------------------------------------------------------------------
# Canon routing
# ---------------------------------------------------------------------------

def focus_milestone_number(routes, explicit):
    if explicit is not None:
        return explicit
    focus = next((r for r in routes if r["id"] == "current-delivery-focus"), None)
    if focus is None or not focus["declared_active"] or not isinstance(focus["target"], str):
        return None
    match = re.search(r"/milestone/([0-9]+)$", focus["target"])
    if not match:
        return None
    return int(match.group(1))


# ---------------------------------------------------------------------------
# Observation
# ---------------------------------------------------------------------------

def _person(entry):
    return {"number": entry["number"], "title": entry["title"], "state": entry["state"],
            "assignees": [a["login"] for a in entry.get("assignees", [])],
            "labels": [l["name"] for l in entry.get("labels", [])],
            "updated_at": entry.get("updated_at")}


def _read_consistent(reader, endpoint, **kwargs):
    first = reader.read(endpoint, **kwargs)
    second = reader.read(endpoint, **kwargs)
    if first != second:
        raise InconsistentObservation("Observation was inconsistent for %s; rerun" % endpoint)
    return first


def discover_global(reader, repo_path, milestone_number):
    if milestone_number is None:
        raise RepoContextError("No Milestone number available for global discovery")
    issues = _read_consistent(reader, "%s/issues?milestone=%d&state=open&per_page=100" %
                              (repo_path, milestone_number), paginated=True)
    return [dict(_person(i), in_milestone=True) for i in issues if "pull_request" not in i]


def issue_relations(reader, repo_path, number):
    def summaries(endpoint):
        items = _read_consistent(reader, endpoint, paginated=True)
        return [{"number": item["number"], "title": item["title"], "state": item["state"]}
                for item in items]

    return {
        "blocked_by": summaries("%s/issues/%d/dependencies/blocked_by" % (repo_path, number)),
        "blocking": summaries("%s/issues/%d/dependencies/blocking" % (repo_path, number)),
        "sub_issues": summaries("%s/issues/%d/sub_issues" % (repo_path, number)),
    }


def issue_context(reader, repo_path, number):
    issue = _read_consistent(reader, "%s/issues/%d" % (repo_path, number))
    comments = _read_consistent(reader, "%s/issues/%d/comments" % (repo_path, number), paginated=True)
    return {"number": issue["number"], "title": issue["title"], "body": issue.get("body"),
            "state": issue["state"], "assignees": [a["login"] for a in issue.get("assignees", [])],
            "labels": [l["name"] for l in issue.get("labels", [])],
            "updated_at": issue.get("updated_at"),
            "comments": [{"author": c["user"]["login"], "created_at": c["created_at"], "body": c["body"]}
                        for c in comments],
            "relations": issue_relations(reader, repo_path, number)}


_ISSUE_REF = re.compile(r"#(\d+)")


def open_pull_requests(reader, repo_path):
    pulls = _read_consistent(reader, "%s/pulls?state=open&per_page=100" % repo_path, paginated=True)
    summaries = []
    for pull in pulls:
        summaries.append({"number": pull["number"], "title": pull["title"], "state": pull["state"],
                          "head_sha": pull.get("head", {}).get("sha"),
                          "base_sha": pull.get("base", {}).get("sha"),
                          "checks": pull.get("checks") or pull.get("mergeable_state"),
                          # Issue numbers this candidate mentions. A mention is not a link:
                          # it means "check this before taking that Issue", not "that Issue is
                          # closed by this". The same read already returned the body, so this
                          # costs no extra round trip.
                          "mentions_issues": sorted({int(n) for n in _ISSUE_REF.findall(
                              (pull.get("body") or "") + " " + (pull.get("title") or ""))})})
    return summaries


def observe(root, reader, repo=None, issue=None, milestone=None):
    tracked = _Tracking(reader)
    repo_name = repo or infer_repo(root)
    repo_path = "repos/" + repo_name
    default_branch = tracked.read(repo_path)["default_branch"]
    ref = tracked.read("%s/git/ref/heads/%s" % (repo_path, quote(default_branch, safe="")))
    remote_head = ref["object"]["sha"]
    canon_text_response = tracked.read("%s/contents/docs/corp/canon-map.yaml?ref=%s" % (repo_path, remote_head))
    import base64
    canon_text = base64.b64decode(canon_text_response["content"]).decode("utf-8")
    routes = canon_routes_from_text(canon_text)
    milestone_number = focus_milestone_number(routes, milestone)

    report = {"repo": repo_name, "remote_branch": default_branch,
              "remote_head": remote_head, "canon": routes, "errors": []}

    report["focus"] = None
    if milestone_number is not None:
        # Focus is context, not the requested object. A missing or unreadable Milestone must not
        # keep an explicitly requested Issue from being read.
        try:
            focus = _read_consistent(tracked, "%s/milestones/%d" % (repo_path, milestone_number))
        except InconsistentObservation:
            raise
        except RepoContextError as exc:
            report["errors"].append({"scope": "focus", "milestone": milestone_number, "error": str(exc)})
        else:
            report["focus"] = {"number": focus["number"], "title": focus.get("title"),
                               "state": focus.get("state")}

    if issue is not None:
        report["mode"] = "issue"
        report["issue"] = issue_context(tracked, repo_path, issue)
    else:
        report["mode"] = "global"
        report["issues"] = discover_global(tracked, repo_path, milestone_number)
    report["open_pull_requests"] = open_pull_requests(tracked, repo_path)

    # An Issue with an unmerged candidate is not takeable as new work, whether or not anyone
    # remembered to label it: the work may already be delivered and waiting, or in progress
    # elsewhere. Attach it here so choosing work needs one read, not a pass over every PR.
    by_issue = {}
    for pull in report["open_pull_requests"]:
        for number in pull.get("mentions_issues", []):
            by_issue.setdefault(number, []).append(pull["number"])
    for issue_row in report.get("issues", []) or ([report["issue"]] if report.get("issue") else []):
        issue_row["open_candidates"] = sorted(by_issue.get(issue_row["number"], []))

    # This report is assembled from several sequential reads and is never a point-in-time
    # snapshot. The flag reports only whether any read spanned pages, which widens the gap
    # further because GitHub gives no cross-page guarantee.
    report["paginated_reads"] = tracked.used_pagination
    return report


def canon_routes_from_text(text):
    rows = parse_map(text)
    # "declared_active" is what the map says, not a verified fact: nothing here reads the
# target. check.py owns target resolution and reports "remote; not contacted" separately.
    return [dict(row, declared_active=(row["status"] == "active")) for row in rows]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="owner/name; inferred from origin when omitted")
    parser.add_argument("--issue", type=int, help="Issue number; omit for global discovery")
    parser.add_argument("--milestone", type=int, help="Milestone number; else taken from Canon routing")
    args = parser.parse_args(argv)
    root = ROOT
    reader = GhReader(root)
    try:
        report = observe(root, reader, repo=args.repo, issue=args.issue, milestone=args.milestone)
    except (RepoContextError, OSError, ValueError) as exc:
        payload = {"error": str(exc)}
        hint = getattr(exc, "hint", None) or getattr(type(exc), "hint", None)
        if hint:
            payload["what_this_means"] = hint
        print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
