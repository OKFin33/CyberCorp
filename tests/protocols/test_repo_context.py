import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / ".agents/corp/repo-context.py"

spec = importlib.util.spec_from_file_location("repo_context", HELPER)
repo_context = importlib.util.module_from_spec(spec)
spec.loader.exec_module(repo_context)


VALID_MAP = (
    "schema_version: 1\n"
    "canonical_targets:\n"
    "  - id: project-direction\n"
    "    target: \"docs/product.md\"\n"
    "    status: active\n"
    "  - id: current-delivery-focus\n"
    "    target: \"https://github.com/o/r/milestone/4\"\n"
    "    status: active\n"
    "  - id: pending-thing\n"
    "    target: null\n"
    "    status: unresolved\n"
)


class ParseMapTests(unittest.TestCase):
    def test_valid_map_parses_in_order_with_expected_fields(self):
        rows = repo_context.parse_map(VALID_MAP)
        self.assertEqual([r["id"] for r in rows], ["project-direction", "current-delivery-focus", "pending-thing"])
        self.assertEqual(rows[0]["target"], "docs/product.md")
        self.assertEqual(rows[0]["status"], "active")
        self.assertIsNone(rows[2]["target"])

    def test_missing_canonical_targets_block_is_an_error(self):
        with self.assertRaisesRegex(ValueError, "one canonical_targets block required"):
            repo_context.parse_map("schema_version: 1\nsomething: else\n")

    def test_duplicated_canonical_targets_block_is_an_error(self):
        doubled = VALID_MAP + "canonical_targets:\n  - id: another\n    target: null\n    status: unresolved\n"
        with self.assertRaisesRegex(ValueError, "one canonical_targets block required"):
            repo_context.parse_map(doubled)

    def test_block_ends_at_next_top_level_key(self):
        text = VALID_MAP + "unrelated_top_level: 1\n  - id: ignored\n"
        rows = repo_context.parse_map(text)
        self.assertEqual(len(rows), 3)

    def test_comments_and_blank_lines_are_ignored(self):
        text = ("canonical_targets:\n"
               "  # a comment\n"
               "\n"
               "  - id: alpha\n"
               "    target: \"a.md\"\n"
               "    status: active\n")
        rows = repo_context.parse_map(text)
        self.assertEqual(rows, [{"id": "alpha", "target": "a.md", "status": "active"}])

    def test_id_line_must_match_exact_indentation_and_pattern(self):
        with self.assertRaisesRegex(ValueError, "unsupported Canon map scalar"):
            repo_context.parse_map("canonical_targets:\n  - id: Not-Lowercase\n    target: null\n    status: unresolved\n")

    def test_field_line_before_any_id_is_an_error(self):
        with self.assertRaisesRegex(ValueError, "unsupported or duplicate Canon map field"):
            repo_context.parse_map("canonical_targets:\n    target: \"a.md\"\n  - id: alpha\n    status: active\n")

    def test_duplicate_field_within_entry_is_an_error(self):
        text = ("canonical_targets:\n  - id: alpha\n    target: \"a.md\"\n"
               "    target: \"b.md\"\n    status: active\n")
        with self.assertRaisesRegex(ValueError, "unsupported or duplicate Canon map field"):
            repo_context.parse_map(text)

    def test_unrecognized_line_shape_is_an_error(self):
        text = "canonical_targets:\n  - id: alpha\n  bogus line\n    target: null\n    status: unresolved\n"
        with self.assertRaisesRegex(ValueError, "unsupported or duplicate Canon map field"):
            repo_context.parse_map(text)

    def test_duplicate_id_across_entries_is_an_error(self):
        text = ("canonical_targets:\n"
               "  - id: alpha\n    target: null\n    status: unresolved\n"
               "  - id: alpha\n    target: null\n    status: unresolved\n")
        with self.assertRaisesRegex(ValueError, "unique IDs"):
            repo_context.parse_map(text)

    def test_entry_missing_a_required_key_is_an_error(self):
        text = "canonical_targets:\n  - id: alpha\n    target: null\n"
        with self.assertRaisesRegex(ValueError, "unique IDs and id/target/status"):
            repo_context.parse_map(text)

    def test_zero_entries_is_an_error(self):
        with self.assertRaisesRegex(ValueError, "unique IDs and id/target/status"):
            repo_context.parse_map("canonical_targets:\n")

    def test_invalid_status_is_an_error(self):
        text = "canonical_targets:\n  - id: alpha\n    target: null\n    status: bogus\n"
        with self.assertRaisesRegex(ValueError, "unsupported Canon map status"):
            repo_context.parse_map(text)

    def test_null_literal_scalar_is_none(self):
        rows = repo_context.parse_map("canonical_targets:\n  - id: a\n    target: null\n    status: unresolved\n")
        self.assertIsNone(rows[0]["target"])

    def test_quoted_json_string_scalar_is_decoded(self):
        rows = repo_context.parse_map('canonical_targets:\n  - id: a\n    target: "has space.md"\n    status: active\n')
        self.assertEqual(rows[0]["target"], "has space.md")

    def test_malformed_quoted_scalar_is_an_error(self):
        text = 'canonical_targets:\n  - id: a\n    target: "unterminated\n    status: active\n'
        with self.assertRaisesRegex(ValueError, "unsupported Canon map scalar"):
            repo_context.parse_map(text)

    def test_bare_scalar_must_match_restricted_charset(self):
        text = "canonical_targets:\n  - id: a\n    target: has space.md\n    status: active\n"
        with self.assertRaisesRegex(ValueError, "unsupported Canon map scalar"):
            repo_context.parse_map(text)

    def test_bare_scalar_url_is_accepted(self):
        rows = repo_context.parse_map(
            "canonical_targets:\n  - id: a\n    target: https://github.com/o/r/issues\n    status: active\n")
        self.assertEqual(rows[0]["target"], "https://github.com/o/r/issues")

    def test_error_type_is_a_value_error_subclass(self):
        self.assertTrue(issubclass(repo_context.RepoContextError, ValueError))


class FakeReader:
    """Offline stand-in for GhReader; endpoints map to canned values or exception factories."""

    def __init__(self, routes):
        self.routes = routes
        self.calls = []

    def read(self, endpoint, paginated=False, list_key=None):
        self.calls.append((endpoint, paginated, list_key))
        value = self.routes[endpoint]
        if callable(value):
            value = value()
        if isinstance(value, Exception):
            raise value
        if paginated:
            return [item for page in value for item in page]
        if list_key is not None:
            return value[list_key]
        return value


import base64

CANON_TEXT = VALID_MAP


def base_routes(sha="a" * 40, branch="develop"):
    return {
        "repos/o/r": {"default_branch": branch},
        "repos/o/r/git/ref/heads/%s" % branch: {"object": {"sha": sha}},
        "repos/o/r/contents/docs/corp/canon-map.yaml?ref=%s" % sha:
            {"encoding": "base64", "content": base64.b64encode(CANON_TEXT.encode()).decode()},
        "repos/o/r/milestones/4": {"number": 4, "title": "Focus", "state": "open"},
        "repos/o/r/pulls?state=open&per_page=100": [[]],
    }


class ObserveGlobalTests(unittest.TestCase):
    def test_global_discovery_lists_open_issues_in_the_milestone(self):
        routes = base_routes()
        routes["repos/o/r/issues?milestone=4&state=open&per_page=100"] = [[
            {"number": 7, "title": "Do the thing", "state": "open",
             "assignees": [{"login": "alice"}], "labels": [{"name": "work"}],
             "updated_at": "2026-01-01T00:00:00Z"},
        ]]
        reader = FakeReader(routes)
        report = repo_context.observe(ROOT, reader, repo="o/r")
        self.assertEqual(report["mode"], "global")
        self.assertEqual(report["focus"]["number"], 4)
        self.assertEqual(len(report["issues"]), 1)
        issue = report["issues"][0]
        self.assertEqual(issue["number"], 7)
        self.assertEqual(issue["assignees"], ["alice"])
        self.assertEqual(issue["labels"], ["work"])
        self.assertTrue(issue["in_milestone"])

    def test_pull_requests_pull_head_and_base_sha_are_included(self):
        routes = base_routes()
        routes["repos/o/r/issues?milestone=4&state=open&per_page=100"] = [[]]
        routes["repos/o/r/pulls?state=open&per_page=100"] = [[
            {"number": 9, "title": "Candidate", "state": "open",
             "head": {"sha": "b" * 40}, "base": {"sha": "a" * 40}, "mergeable_state": "clean"},
        ]]
        reader = FakeReader(routes)
        report = repo_context.observe(ROOT, reader, repo="o/r")
        self.assertEqual(len(report["open_pull_requests"]), 1)
        pr = report["open_pull_requests"][0]
        self.assertEqual(pr["head_sha"], "b" * 40)
        self.assertEqual(pr["base_sha"], "a" * 40)

    def test_canon_routes_are_included_with_non_active_marked_unverified(self):
        routes = base_routes()
        routes["repos/o/r/issues?milestone=4&state=open&per_page=100"] = [[]]
        reader = FakeReader(routes)
        report = repo_context.observe(ROOT, reader, repo="o/r")
        by_id = {r["id"]: r for r in report["canon"]}
        self.assertTrue(by_id["project-direction"]["verified"])
        self.assertFalse(by_id["pending-thing"]["verified"])

    def test_atomic_snapshot_is_false_when_any_paginated_read_occurred(self):
        routes = base_routes()
        routes["repos/o/r/issues?milestone=4&state=open&per_page=100"] = [[]]
        reader = FakeReader(routes)
        report = repo_context.observe(ROOT, reader, repo="o/r")
        self.assertFalse(report["atomic_snapshot"])

    def test_report_includes_an_empty_errors_list_on_success(self):
        routes = base_routes()
        routes["repos/o/r/issues?milestone=4&state=open&per_page=100"] = [[]]
        reader = FakeReader(routes)
        report = repo_context.observe(ROOT, reader, repo="o/r")
        self.assertEqual(report["errors"], [])


class ObserveIssueTests(unittest.TestCase):
    def _issue_routes(self):
        routes = base_routes()
        routes["repos/o/r/issues/11"] = {"number": 11, "title": "Fix X", "body": "<!-- spec:start -->\nY\n<!-- spec:end -->",
                                         "state": "open", "assignees": [{"login": "bob"}],
                                         "labels": [{"name": "bug"}], "updated_at": "2026-02-02T00:00:00Z"}
        routes["repos/o/r/issues/11/comments"] = [[
            {"user": {"login": "carol"}, "created_at": "2026-02-03T00:00:00Z", "body": "SPEC_ACCEPTED issue=11 ..."},
        ]]
        routes["repos/o/r/issues/11/dependencies/blocked_by"] = [[]]
        routes["repos/o/r/issues/11/dependencies/blocking"] = [[]]
        routes["repos/o/r/issues/11/sub_issues"] = [[]]
        return routes

    def test_single_issue_context_includes_body_and_comments(self):
        reader = FakeReader(self._issue_routes())
        report = repo_context.observe(ROOT, reader, repo="o/r", issue=11)
        self.assertEqual(report["mode"], "issue")
        self.assertEqual(report["issue"]["number"], 11)
        self.assertEqual(report["issue"]["body"], "<!-- spec:start -->\nY\n<!-- spec:end -->")
        self.assertEqual(len(report["issue"]["comments"]), 1)
        self.assertEqual(report["issue"]["comments"][0]["author"], "carol")

    def test_issue_relations_are_reported(self):
        routes = self._issue_routes()
        routes["repos/o/r/issues/11/dependencies/blocked_by"] = [[
            {"number": 6, "title": "Dependency", "state": "open"},
        ]]
        reader = FakeReader(routes)
        report = repo_context.observe(ROOT, reader, repo="o/r", issue=11)
        self.assertEqual(report["issue"]["relations"]["blocked_by"][0]["number"], 6)
        self.assertEqual(report["issue"]["relations"]["blocking"], [])
        self.assertEqual(report["issue"]["relations"]["sub_issues"], [])

    def test_explicit_milestone_option_overrides_canon_routing(self):
        routes = self._issue_routes()
        routes["repos/o/r/milestones/9"] = {"number": 9, "title": "Other", "state": "open"}
        reader = FakeReader(routes)
        report = repo_context.observe(ROOT, reader, repo="o/r", issue=11, milestone=9)
        self.assertEqual(report["focus"]["number"], 9)

    def test_report_includes_an_empty_errors_list_on_success(self):
        reader = FakeReader(self._issue_routes())
        report = repo_context.observe(ROOT, reader, repo="o/r", issue=11)
        self.assertEqual(report["errors"], [])

    def test_no_active_focus_route_and_no_explicit_milestone_yields_none_focus(self):
        text = "canonical_targets:\n  - id: current-delivery-focus\n    target: null\n    status: unresolved\n"
        routes = {
            "repos/o/r": {"default_branch": "main"},
            "repos/o/r/git/ref/heads/main": {"object": {"sha": "c" * 40}},
            "repos/o/r/contents/docs/corp/canon-map.yaml?ref=%s" % ("c" * 40):
                {"encoding": "base64", "content": base64.b64encode(text.encode()).decode()},
            "repos/o/r/issues?milestone=None&state=open&per_page=100": [[]],
            "repos/o/r/pulls?state=open&per_page=100": [[]],
        }
        reader = FakeReader(routes)
        with self.assertRaises(repo_context.RepoContextError):
            repo_context.observe(ROOT, reader, repo="o/r")


class ConsistencyTests(unittest.TestCase):
    def test_inconsistent_repeated_read_raises(self):
        routes = base_routes()
        counter = {"n": 0}

        def flaky():
            counter["n"] += 1
            return {"number": 4, "title": "Focus", "state": "open" if counter["n"] == 1 else "closed"}

        routes["repos/o/r/milestones/4"] = flaky
        routes["repos/o/r/issues?milestone=4&state=open&per_page=100"] = [[]]
        reader = FakeReader(routes)
        with self.assertRaisesRegex(repo_context.RepoContextError, "Observation was inconsistent"):
            repo_context.observe(ROOT, reader, repo="o/r")

    def test_stable_repeated_read_does_not_raise(self):
        routes = base_routes()
        routes["repos/o/r/issues?milestone=4&state=open&per_page=100"] = [[]]
        reader = FakeReader(routes)
        report = repo_context.observe(ROOT, reader, repo="o/r")
        self.assertEqual(report["focus"]["number"], 4)


class GhReaderFailureTests(unittest.TestCase):
    def test_nonzero_exit_from_gh_raises_repo_context_error(self):
        import subprocess
        import sys
        reader = repo_context.GhReader(ROOT)
        fake_gh = ROOT / "tests/protocols/_fixtures_missing_gh_should_not_exist"
        original_run = subprocess.run

        def failing_run(args, **kwargs):
            return original_run([sys.executable, "-c", "import sys; sys.exit(1)"], **kwargs)

        subprocess.run = failing_run
        try:
            with self.assertRaises(repo_context.RepoContextError):
                reader.read("repos/o/r")
        finally:
            subprocess.run = original_run
        self.assertFalse(fake_gh.exists())

    def test_non_json_stdout_raises_repo_context_error(self):
        import subprocess
        import sys
        reader = repo_context.GhReader(ROOT)
        original_run = subprocess.run

        def not_json_run(args, **kwargs):
            return original_run([sys.executable, "-c", "print('not json')"], **kwargs)

        subprocess.run = not_json_run
        try:
            with self.assertRaises(repo_context.RepoContextError):
                reader.read("repos/o/r")
        finally:
            subprocess.run = original_run

    def test_gh_not_found_raises_repo_context_error(self):
        reader = repo_context.GhReader(ROOT)
        import subprocess
        original_run = subprocess.run

        def missing_binary(args, **kwargs):
            raise FileNotFoundError("gh not found")

        subprocess.run = missing_binary
        try:
            with self.assertRaises(repo_context.RepoContextError):
                reader.read("repos/o/r")
        finally:
            subprocess.run = original_run

    def test_malformed_pagination_shape_raises(self):
        routes = {"repos/o/r/issues": {"not": "a list of pages"}}
        # Bypass FakeReader's flattening by calling GhReader-style validation directly via
        # a minimal reader double that returns the raw (invalid) shape for a paginated read.
        reader = repo_context.GhReader(ROOT)
        import subprocess
        import sys
        original_run = subprocess.run

        def bad_shape_run(args, **kwargs):
            return original_run([sys.executable, "-c", "import json; print(json.dumps({'not': 'pages'}))"], **kwargs)

        subprocess.run = bad_shape_run
        try:
            with self.assertRaises(repo_context.RepoContextError):
                reader.read("repos/o/r/issues", paginated=True)
        finally:
            subprocess.run = original_run


if __name__ == "__main__":
    unittest.main()
