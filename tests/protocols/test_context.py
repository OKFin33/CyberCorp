"""Public read-only projection behavior with isolated API/Git inputs; no live CI reads."""
import base64
import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from protocols.test_protocols import spec, claim, recovery, comment

SCRIPTS = Path(__file__).resolve().parents[2] / "skills/cybercorp/assets/corp/.agents/corp"
definition = importlib.util.spec_from_file_location("repo_context", SCRIPTS / "repo-context.py")
context = importlib.util.module_from_spec(definition)
definition.loader.exec_module(context)
ROOT = SCRIPTS.parents[1]
REPO = "example/project"
BASE = "a" * 40
API = "repos/" + REPO
AT = "2026-09-05T13:30:00Z"
MAP = """schema_version: 1
canonical_targets:
  - id: current-delivery-focus
    target: "https://github.com/example/project/milestone/1"
    status: active
  - id: product-contract
    target: docs/product/product-contract.md
    status: pending-relocation
  - id: database-migration-chain
    target: null
    status: unresolved
supporting_surfaces: []
"""


class Fake:
    def __init__(self):
        self.calls = []
        self.rows = {
            API + "/git/ref/heads/main": {"object": {"sha": BASE}},
            API + "/contents/docs/corp/canon-map.yaml?ref=" + BASE:
                {"encoding": "base64", "content": base64.b64encode(MAP.encode()).decode()},
            API + "/milestones/1": {"number": 1, "title": "M0", "description": "Mechanism first",
                                    "state": "open"},
            API + "/issues?milestone=1&state=open&per_page=100":
                [{"number": 7, "title": "context", "state": "open", "updated_at": AT},
                 {"number": 8, "title": "pr", "state": "open", "pull_request": {}}],
            API + "/pulls?state=open&per_page=100": [],
            API + "/issues?milestone=1&labels=work%3Acoordination&state=all&per_page=100": [],
        }
        body = "<!-- spec:start -->\nOutcome: context\n<!-- spec:end -->\n"
        self.rows[API + "/issues/7"] = {"number": 7, "title": "context", "body": body,
                                       "state": "open", "updated_at": AT, "comments": 4}
        accepted = {"id": 10, "created_at": "2026-09-05T12:59:00Z",
                    "body": "SPEC_ACCEPTED issue=7 spec_sha256=" + spec.digest_body(body.encode())
                            + " source=https://github.com/example/project/milestone/1"}
        self.rows[API + "/issues/7/comments?per_page=100"] = [
            accepted, claim(11), comment(12, 1, "checkpoint", claim=11, recovery=recovery()),
            comment(13, 2, "release", claim=11, checkpoint=12, reason="waiting")]
        for suffix in ("sub_issues", "dependencies/blocked_by", "dependencies/blocking", "timeline"):
            self.rows[API + "/issues/7/" + suffix + "?per_page=100"] = []

    def read(self, endpoint, paginated=False, list_key=None):
        self.calls.append((endpoint, paginated, list_key))
        value = self.rows[endpoint]
        if isinstance(value, Exception):
            raise value
        return copy.deepcopy(value() if callable(value) else value)


class ProjectionTests(unittest.TestCase):
    def run_context(self, api, issue=None):
        with patch.object(context, "local_state", return_value={"head": BASE, "tracked_dirty": False},
                          create=True):
            return context.collect(api, ROOT, REPO, issue, clock=lambda: AT)

    def test_landing_is_remote_pinned_and_not_a_ready_queue(self):
        api = Fake()
        result = self.run_context(api)
        self.assertEqual(result["status"], "observed")
        self.assertEqual(result["remote_head"], BASE)
        self.assertEqual(result["focus"]["number"], 1)
        self.assertEqual([row["number"] for row in result["work"]], [7])
        self.assertEqual(result["canon"][1]["status"], "pending-relocation")
        self.assertIsNone(result["canon"][2]["target"])
        self.assertFalse(result["atomic_snapshot"])
        self.assertNotIn("ready", result)

    def test_body_goal_link_is_not_native_milestone_membership(self):
        api = Fake()
        api.rows[API + "/issues/7"]["body"] += "\nGoal: https://github.com/example/project/milestone/1"
        api.rows[API + "/issues?milestone=1&state=open&per_page=100"] = []
        self.assertEqual(self.run_context(api)["work"], [])
        api.rows[API + "/issues?milestone=1&state=open&per_page=100"] = [api.rows[API + "/issues/7"]]
        self.assertEqual([row["number"] for row in self.run_context(api)["work"]], [7])

    def test_checkpoint_cli_sources_roundtrip_to_projection(self):
        body = "<!-- spec:start -->\nOutcome: source roundtrip\n<!-- spec:end -->\n"
        sources = ["https://github.com/example/project/milestone/1",
                   "https://github.com/example/project/issues/7#issuecomment-10",
                   "https://github.com/example/project/blob/" + BASE + "/docs/decision.md"]
        for source in sources:
            with self.subTest(source=source):
                result = subprocess.run([sys.executable, "-B", str(SCRIPTS / "spec-checkpoint.py"),
                                         "--checkpoint", "--issue", "7", "--source", source],
                                        input=body, text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                row = {"id": 10, "created_at": AT, "updated_at": AT, "body": result.stdout.strip()}
                projection = context.spec_context({"number": 7, "body": body, "state": "open"},
                                                  [row], REPO)
                self.assertEqual(projection["content_match"], "matched")
                self.assertEqual(projection["matching_records"][0]["source"], source)
                self.assertEqual(projection["sha256"], spec.digest_body(body.encode()))
                self.assertEqual(projection["authority"], "not-evaluated")

    def test_unsupported_checkpoint_sources_fail_before_publication(self):
        body = "<!-- spec:start -->\nOutcome: source rejection\n<!-- spec:end -->\n"
        sources = ["docs/decision.md", "file:///private/decision.md", "github://issues/7", "http://example.com/a",
                   "https://", "https:///missing-host", "https://user:secret@example.com/a",
                   "https://example.com:bad/a", "https://example.com/a b", "https://example.com/\\unsafe",
                   "https://example.com/<wrapped>"]
        for source in sources:
            with self.subTest(source=source):
                result = subprocess.run([sys.executable, "-B", str(SCRIPTS / "spec-checkpoint.py"),
                                         "--checkpoint", "--issue", "7", "--source", source],
                                        input=body, text=True, capture_output=True)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                row = {"id": 10, "created_at": AT, "body": "SPEC_ACCEPTED issue=7 spec_sha256="
                       + spec.digest_body(body.encode()) + " source=" + source}
                projection = context.spec_context({"number": 7, "body": body, "state": "open"}, [row], REPO)
                self.assertEqual(projection["content_match"], "missing")
                self.assertEqual(projection["authority"], "not-evaluated")

    def test_landing_open_pr_has_a_valid_identity_and_head(self):
        api = Fake()
        api.rows[API + "/pulls?state=open&per_page=100"] = [
            {"number": 8, "title": "context", "head": {"sha": "b" * 40}, "base": {"ref": "main"}}]
        result = self.run_context(api)
        self.assertEqual(result["status"], "observed")
        self.assertEqual(result["open_pull_requests"][0]["head"], "b" * 40)

    def test_malformed_landing_pr_fields_fail_closed(self):
        for update in ({"number": 0}, {"number": True}, {"title": None},
                       {"head": {"sha": "not-a-sha"}}, {"head": {"sha": None}},
                       {"base": {"ref": None}}):
            api = Fake()
            api.rows[API + "/pulls?state=open&per_page=100"] = [
                {"number": 8, "title": "context", "head": {"sha": "b" * 40},
                 "base": {"ref": "main"}, **update}]
            with self.subTest(update=update):
                self.assertEqual(self.run_context(api)["status"], "incomplete")

    def test_recovery_reuses_protocol_and_exposes_acceptance_limit(self):
        result = self.run_context(Fake(), 7)
        self.assertEqual(result["status"], "observed")
        selected = result["issue"]
        self.assertEqual(selected["spec"]["content_match"], "matched")
        self.assertEqual(selected["spec"]["authority"], "not-evaluated")
        self.assertIsNone(selected["execution"]["current_claim"])
        self.assertEqual(selected["execution"]["latest_checkpoint"]["id"], 12)
        self.assertEqual(selected["execution"]["latest_checkpoint"]["recovery"]["waiting_on"], ["review"])
        self.assertEqual(len(selected["comment_index"]), 4)

    def test_explicit_issue_does_not_read_global_discovery(self):
        api = Fake()
        for endpoint in ("/milestones/1", "/issues?milestone=1&state=open&per_page=100",
                         "/pulls?state=open&per_page=100"):
            del api.rows[API + endpoint]
        result = self.run_context(api, 7)
        self.assertEqual(result["status"], "observed")
        self.assertEqual(result["scope"], "issue")
        self.assertEqual(result["issue"]["number"], 7)
        for key in ("focus", "work", "open_pull_requests"):
            self.assertNotIn(key, result)
        self.assertFalse(any("/milestones/" in endpoint or "?milestone=" in endpoint
                             or endpoint.endswith("/pulls?state=open&per_page=100")
                             for endpoint, _, _ in api.calls))

    def test_explicit_issue_is_observable_with_closed_or_unavailable_focus(self):
        for value in ({"number": 1, "title": "M0", "state": "closed"},
                      context.ReadError("unrelated discovery unavailable")):
            api = Fake()
            api.rows[API + "/milestones/1"] = value
            result = self.run_context(api, 7)
            self.assertEqual(result["status"], "observed")
            self.assertEqual(result["issue"]["spec"]["authority"], "not-evaluated")
            self.assertNotIn((API + "/milestones/1", False, None), api.calls)

    def test_explicit_issue_does_not_require_an_active_focus_route(self):
        focus = ('  - id: current-delivery-focus\n'
                 '    target: "https://github.com/example/project/milestone/1"\n'
                 '    status: active\n')
        for replacement in ("", focus.replace("status: active", "status: pending-relocation"),
                            focus.replace('"https://github.com/example/project/milestone/1"', "null"),
                            focus.replace("example/project/milestone", "example/other/milestone")):
            api = Fake()
            api.rows[API + "/contents/docs/corp/canon-map.yaml?ref=" + BASE]["content"] = (
                base64.b64encode(MAP.replace(focus, replacement).encode()).decode())
            with self.subTest(replacement=replacement):
                self.assertEqual(self.run_context(api, 7)["status"], "observed")
                self.assertEqual(self.run_context(api)["status"], "incomplete")

    def test_landing_scope_and_discovery_failures_remain_explicit(self):
        self.assertEqual(self.run_context(Fake())["scope"], "landing")
        for endpoint in ("/milestones/1", "/issues?milestone=1&state=open&per_page=100",
                         "/pulls?state=open&per_page=100"):
            api = Fake()
            api.rows[API + endpoint] = context.ReadError("discovery unavailable")
            result = self.run_context(api)
            self.assertEqual(result["status"], "incomplete")
            self.assertTrue(result["errors"])

    def test_explicit_issue_still_requires_its_own_inputs(self):
        for endpoint in ("/git/ref/heads/main", "/contents/docs/corp/canon-map.yaml?ref=" + BASE,
                         "/issues/7", "/issues/7/comments?per_page=100",
                         "/issues/7/sub_issues?per_page=100", "/issues/7/timeline?per_page=100"):
            api = Fake()
            api.rows[API + endpoint] = context.ReadError("required input unavailable")
            result = self.run_context(api, 7)
            self.assertEqual(result["status"], "incomplete")
            self.assertTrue(result["errors"])

    def test_stale_or_quoted_acceptance_not_a_match(self):
        for body in ("SPEC_ACCEPTED issue=7 spec_sha256=" + "0" * 64 + " source=https://example.com",
                     "> SPEC_ACCEPTED issue=7 spec_sha256=" + "0" * 64 + " source=https://example.com"):
            api = Fake()
            api.rows[API + "/issues/7/comments?per_page=100"][0]["body"] = body
            result = self.run_context(api, 7)
            self.assertEqual(result["issue"]["spec"]["content_match"], "missing")
            self.assertEqual(result["issue"]["spec"]["authority"], "not-evaluated")

    def test_invalid_spec_is_not_a_successful_projection(self):
        api = Fake()
        api.rows[API + "/issues/7"]["body"] = "no spec"
        self.assertEqual(self.run_context(api, 7)["status"], "incomplete")

    def test_corrupt_execution_is_not_an_empty_history(self):
        api = Fake()
        api.rows[API + "/issues/7/comments?per_page=100"][1]["body"] = "```agent-event\n{bad\n```"
        self.assertEqual(self.run_context(api, 7)["status"], "incomplete")

    def test_comment_count_mismatch_is_incomplete(self):
        api = Fake()
        api.rows[API + "/issues/7"]["comments"] = 5
        self.assertEqual(self.run_context(api, 7)["status"], "incomplete")

    def test_failed_read_is_not_empty_success(self):
        api = Fake()
        api.rows[API + "/issues/7/dependencies/blocked_by?per_page=100"] = context.ReadError("unavailable")
        result = self.run_context(api, 7)
        self.assertEqual(result["status"], "incomplete")
        self.assertTrue(result["errors"])

    def test_issue_or_main_drift_during_collection_is_incomplete(self):
        for endpoint, changed in [(API + "/issues/7", {"updated_at": "2026-09-05T13:31:00Z"}),
                                  (API + "/git/ref/heads/main", {"object": {"sha": "b" * 40}})]:
            api = Fake()
            original = api.rows[endpoint]
            rows = [original, {**original, **changed}]
            api.rows[endpoint] = lambda: rows.pop(0)
            self.assertEqual(self.run_context(api, 7)["status"], "incomplete")

    def test_closed_dependency_is_not_declared_satisfied(self):
        api = Fake()
        api.rows[API + "/issues/7/dependencies/blocked_by?per_page=100"] = [
            {"number": 3, "title": "cancelled", "state": "closed", "state_reason": "not_planned"}]
        result = self.run_context(api, 7)
        row = result["issue"]["relations"]["blocked_by"][0]
        self.assertEqual(row["state_reason"], "not_planned")
        self.assertNotIn("satisfied", row)

    def test_native_same_repo_pr_reference_pins_actions_and_reviews(self):
        api = Fake()
        api.rows[API + "/issues/7/timeline?per_page=100"] = [
            {"event": "cross-referenced", "source": {"issue": {"number": 9,
             "pull_request": {"url": "https://api.github.com/repos/example/project/pulls/9"}}}}]
        api.rows[API + "/pulls/9"] = {"number": 9, "title": "context", "state": "closed",
              "merged": True, "merge_commit_sha": "c" * 40, "head": {"sha": "b" * 40},
              "base": {"sha": BASE, "ref": "main"}}
        api.rows[API + "/pulls/9/reviews?per_page=100"] = []
        api.rows[API + "/actions/runs?head_sha=" + "b" * 40 + "&per_page=100"] = [
            {"id": 42, "head_sha": "b" * 40, "status": "completed", "conclusion": "success",
             "event": "pull_request", "html_url": "https://github.com/example/project/actions/runs/42"}]
        result = self.run_context(api, 7)
        pr = result["issue"]["pull_requests"][0]
        self.assertEqual(pr["head"], "b" * 40)
        self.assertEqual(pr["association"], "native-cross-reference-only")
        self.assertEqual(pr["actions"][0]["id"], 42)
        self.assertNotIn("approved", pr)

    def test_external_and_body_links_are_not_fetched(self):
        api = Fake()
        api.rows[API + "/issues/7/timeline?per_page=100"] = [
            {"event": "cross-referenced", "source": {"issue": {"number": 9,
             "pull_request": {"url": "https://api.github.com/repos/outsider/project/pulls/9"}}}}]
        api.rows[API + "/issues/7"]["body"] += "https://secrets.invalid\n"
        result = self.run_context(api, 7)
        self.assertEqual(result["status"], "observed")
        self.assertEqual(result["issue"]["pull_requests"], [])
        self.assertTrue(all(endpoint.startswith(API + "/") for endpoint, _, _ in api.calls))

    def test_every_collection_endpoint_is_paginated(self):
        api = Fake()
        self.run_context(api, 7)
        for endpoint, paginated, _ in api.calls:
            if "per_page=100" in endpoint:
                self.assertTrue(paginated, endpoint)

    def test_malformed_or_duplicate_map_entries_fail_in_both_scopes(self):
        for text in (MAP.replace("status: active", "status: unknown-status"),
                     MAP.replace("supporting_surfaces:", MAP.split("canonical_targets:\n")[1]
                                 .split("supporting_surfaces:")[0] + "supporting_surfaces:")):
            with self.assertRaises((context.ReadError, ValueError)):
                context.parse_map(text)
            api = Fake()
            api.rows[API + "/contents/docs/corp/canon-map.yaml?ref=" + BASE]["content"] = (
                base64.b64encode(text.encode()).decode())
            for issue in (None, 7):
                self.assertEqual(self.run_context(api, issue)["status"], "incomplete")



    def test_native_cross_repo_dependency_keeps_real_locator(self):
        api = Fake()
        api.rows[API + "/issues/7/dependencies/blocked_by?per_page=100"] = [
            {"number": 3, "title": "dependency", "state": "open",
             "html_url": "https://github.com/example/another/issues/3"}]
        row = self.run_context(api, 7)["issue"]["relations"]["blocked_by"][0]
        self.assertEqual(row["url"], "https://github.com/example/another/issues/3")

    def test_closed_or_malformed_focus_is_not_current_work(self):
        for update in ({"state": "closed"}, {"number": 99}, {"title": None}):
            api = Fake()
            api.rows[API + "/milestones/1"].update(update)
            self.assertEqual(self.run_context(api)["status"], "incomplete")

    def test_malformed_body_still_returns_incomplete_json_object(self):
        api = Fake()
        api.rows[API + "/issues/7"]["body"] = {"unexpected": "object"}
        self.assertEqual(self.run_context(api, 7)["status"], "incomplete")


    def test_unmerged_pr_does_not_present_actual_merge_commit(self):
        api = Fake()
        api.rows[API + "/pulls/9"] = {"number": 9, "title": "context", "state": "open",
              "merged": False, "merge_commit_sha": "c" * 40, "head": {"sha": "b" * 40},
              "base": {"sha": BASE, "ref": "main"}}
        api.rows[API + "/pulls/9/reviews?per_page=100"] = []
        api.rows[API + "/actions/runs?head_sha=" + "b" * 40 + "&per_page=100"] = []
        self.assertIsNone(context.pull_context(api, API, REPO, 9)["merge_commit"])

    def test_lease_expires_during_read_is_replayed_at_finish(self):
        api = Fake()
        api.rows[API + "/issues/7/comments?per_page=100"] = [claim()]
        api.rows[API + "/issues/7"]["comments"] = 1
        ticks = iter(["2026-09-05T13:05:00Z", "2026-09-05T13:06:00Z", AT])
        with patch.object(context, "local_state", return_value={"head": BASE, "tracked_dirty": False}):
            result = context.collect(api, ROOT, REPO, 7, clock=lambda: next(ticks))
        self.assertEqual(result["status"], "observed")
        self.assertIsNone(result["issue"]["execution"]["current_claim"])
        self.assertEqual(result["issue"]["execution"]["observed_at"], "2026-09-05T13:30:00+00:00")


    def test_malformed_pr_review_and_actions_cannot_be_observed(self):
        for field, value in (("merged", None), ("state", "not-a-state"), ("title", None)):
            api = Fake()
            api.rows[API + "/pulls/9"] = {"number": 9, "title": "context", "state": "open",
                "merged": False, "merge_commit_sha": None, "head": {"sha": "b" * 40},
                "base": {"sha": BASE, "ref": "main"}, field: value}
            api.rows[API + "/pulls/9/reviews?per_page=100"] = []
            api.rows[API + "/actions/runs?head_sha=" + "b" * 40 + "&per_page=100"] = []
            with self.subTest(field=field), self.assertRaises((context.ReadError, ValueError)):
                context.pull_context(api, API, REPO, 9)
        for reviews, actions in (([{}], []), ([], [{"head_sha": "b" * 40}])):
            api = Fake()
            api.rows[API + "/pulls/9"] = {"number": 9, "title": "context", "state": "open",
                "merged": False, "head": {"sha": "b" * 40}, "base": {"sha": BASE, "ref": "main"}}
            api.rows[API + "/pulls/9/reviews?per_page=100"] = reviews
            api.rows[API + "/actions/runs?head_sha=" + "b" * 40 + "&per_page=100"] = actions
            with self.subTest(reviews=reviews, actions=actions), self.assertRaises((context.ReadError, ValueError)):
                context.pull_context(api, API, REPO, 9)

    def test_pending_review_and_in_progress_action_allow_legal_nulls(self):
        api = Fake()
        api.rows[API + "/pulls/9"] = {"number": 9, "title": "context", "state": "open",
             "merged": False, "head": {"sha": "b" * 40}, "base": {"sha": BASE, "ref": "main"}}
        api.rows[API + "/pulls/9/reviews?per_page=100"] = [
            {"id": 5, "state": "PENDING", "commit_id": None, "submitted_at": None, "html_url": None}]
        api.rows[API + "/actions/runs?head_sha=" + "b" * 40 + "&per_page=100"] = [
            {"id": 6, "head_sha": "b" * 40, "event": "pull_request", "status": "in_progress",
             "conclusion": None, "html_url": "https://github.com/example/project/actions/runs/6"}]
        result = context.pull_context(api, API, REPO, 9)
        self.assertIsNone(result["actions"][0]["conclusion"])
        self.assertEqual(result["reviews"][0]["state"], "PENDING")

class TransportTests(unittest.TestCase):
    def test_get_only_and_paginated_arrays(self):
        with patch.object(subprocess, "run", return_value=subprocess.CompletedProcess([], 0, '[[{"id":1}],[{"id":2}]]')) as run:
            result = context.GitHub(ROOT).read(API + "/issues?per_page=100", paginated=True)
            self.assertEqual([row["id"] for row in result], [1, 2])
            args, kwargs = run.call_args
            self.assertIn("GET", args[0])
            self.assertIn("--paginate", args[0])
            self.assertFalse(kwargs.get("shell", False))

    def test_paginated_keyed_actions_response(self):
        with patch.object(subprocess, "run", return_value=subprocess.CompletedProcess([], 0,
                           '[{"workflow_runs":[{"id":1}]},{"workflow_runs":[{"id":2}]}]')):
            result = context.GitHub(ROOT).read(API + "/actions/runs", True, "workflow_runs")
            self.assertEqual([row["id"] for row in result], [1, 2])

    def test_error_does_not_echo_secret_output(self):
        for response in (subprocess.CompletedProcess([], 1, "SECRET-TOKEN", "SECRET-TOKEN"),
                         subprocess.CompletedProcess([], 0, "SECRET-TOKEN")):
            with patch.object(subprocess, "run", return_value=response):
                with self.assertRaises(context.ReadError) as raised:
                    context.GitHub(ROOT).read(API + "/issues")
                self.assertNotIn("SECRET-TOKEN", str(raised.exception))

    def test_malformed_pages_are_not_silently_dropped(self):
        with patch.object(subprocess, "run", return_value=subprocess.CompletedProcess([], 0, '[[],{}]')):
            with self.assertRaises(context.ReadError):
                context.GitHub(ROOT).read(API + "/issues", True)


if __name__ == "__main__":
    unittest.main()
