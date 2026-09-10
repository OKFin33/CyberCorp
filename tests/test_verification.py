import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "skills/cybercorp"
definition = importlib.util.spec_from_file_location("verification_creator", PACKAGE / "scripts/cybercorp.py")
creator = importlib.util.module_from_spec(definition)
definition.loader.exec_module(creator)


class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="corp-verification-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.repo = self.base / "project with spaces"
        creator.install(self.repo, {"name": "Local catalog", "goal": "Find owned items",
                                    "scope": ["Import", "Search"]})
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GITHUB_")}
        self.env["PYTHONDONTWRITEBYTECODE"] = "1"

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, capture_output=True,
                              text=True, check=True).stdout.strip()

    def commit(self, message):
        self.git("add", ".")
        self.git("commit", "-m", message)
        return self.git("rev-parse", "HEAD")

    def check(self, *args, event=None, payload=None, expect=0):
        env = self.env.copy()
        if event:
            event_file = self.base / "event.json"
            event_file.write_text(json.dumps(payload), encoding="utf-8")
            env.update(GITHUB_EVENT_NAME=event, GITHUB_EVENT_PATH=str(event_file),
                       GITHUB_RUN_ID="123", GITHUB_RUN_ATTEMPT="2", GITHUB_JOB="checks")
        result = subprocess.run([sys.executable, str(self.repo / ".agents/corp/check.py"), *args],
                                cwd=self.base, env=env, text=True, capture_output=True)
        self.assertEqual(result.returncode, expect, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "passed" if expect == 0 else "failed")
        return report

    def test_unborn_project_checks_locally_without_network_or_readiness_claim(self):
        report = self.check()
        self.assertIsNone(report["git"]["head"])
        self.assertTrue(report["git"]["range"].startswith("empty tree"))
        self.assertEqual({r["id"] for r in report["unverified_routes"]},
                         {"active-change-specs", "current-delivery-focus"})
        self.assertEqual(report["structure"]["spec_self_check"], "passed")

    def test_check_survives_transport_and_creator_removal(self):
        portable = self.base / "portable"
        shutil.copytree(PACKAGE, portable, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        target = self.base / "transported"
        brief = self.base / "brief.json"
        brief.write_text(json.dumps({"name": "Transport", "goal": "A result", "scope": ["A result"]}))
        subprocess.run([sys.executable, str(portable / "scripts/cybercorp.py"), str(target),
                        "--brief", str(brief)], capture_output=True, text=True, check=True)
        shutil.rmtree(portable)
        result = subprocess.run([sys.executable, str(target / ".agents/corp/check.py")],
                                cwd=self.base, env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_real_staged_unstaged_and_untracked_differences_are_checked(self):
        (self.repo / "tracked.txt").write_text("original\n")
        head = self.commit("baseline")
        (self.repo / "tracked.txt").write_text("staged\n")
        self.git("add", "tracked.txt")
        (self.repo / "tracked.txt").write_text("unstaged  \n")
        report = self.check(expect=1)
        self.assertEqual(report["git"]["base"], head)
        self.assertEqual(report["git"]["tracked_changes"], ["tracked.txt"])
        self.assertIn("trailing whitespace", report["errors"][0])
        (self.repo / "tracked.txt").write_text("fixed\n")
        (self.repo / "new file.txt").write_text("new  \n")
        report = self.check(expect=1)
        self.assertIn("new file.txt", report["git"]["untracked"])
        (self.repo / "new file.txt").write_text("new\n")
        self.assertTrue(self.check()["git"]["dirty"])

    def test_pr_uses_event_base_and_records_distinct_merge_checkout(self):
        base = self.commit("baseline")
        self.git("checkout", "-b", "feature")
        (self.repo / "feature.txt").write_text("feature\n")
        head = self.commit("feature")
        self.git("checkout", "main")
        (self.repo / "other.txt").write_text("main change\n")
        self.commit("base advanced")
        self.git("merge", "--no-ff", "feature", "-m", "Synthetic merge checkout")
        actual = self.git("rev-parse", "HEAD")
        report = self.check(event="pull_request", payload={"pull_request": {
            "base": {"sha": base}, "head": {"sha": head}}})
        self.assertEqual(report["git"]["base"], base)
        self.assertEqual(report["git"]["head"], actual)
        self.assertNotEqual(actual, report["git"]["ci"]["pr_head"])
        self.assertEqual(report["git"]["ci"]["GITHUB_RUN_ATTEMPT"], "2")
        self.assertEqual(set(report["git"]["tracked_changes"]), {"feature.txt", "other.txt"})

    def test_missing_or_unavailable_required_baseline_fails_instead_of_empty_success(self):
        head = self.commit("baseline")
        for payload in ({}, {"before": "f" * 40}):
            with self.subTest(payload=payload):
                report = self.check(event="push", payload=payload, expect=1)
                self.assertIn("baseline", report["errors"][0])
                self.assertEqual(report["git"]["head"], head)
                self.assertEqual(report["git"]["requested_base"], payload.get("before"))
                self.assertEqual(report["git"]["ci"]["GITHUB_JOB"], "checks")
        report = self.check(event="pull_request", payload={"pull_request": {
            "head": {"sha": self.git("rev-parse", "HEAD")}}}, expect=1)
        self.assertIn("baseline", report["errors"][0])

    def test_push_uses_before_and_initial_push_checks_whole_tree(self):
        base = self.commit("baseline")
        (self.repo / "result.txt").write_text("result\n")
        self.commit("new result")
        report = self.check(event="push", payload={"before": base})
        self.assertEqual(report["git"]["tracked_changes"], ["result.txt"])
        report = self.check(event="push", payload={"before": "0" * 40})
        self.assertIn("docs/corp/README.md", report["git"]["tracked_changes"])

    def test_manual_previous_commit_and_explicit_reproduction(self):
        initial = self.commit("baseline")
        report = self.check(event="workflow_dispatch", payload={})
        self.assertTrue(report["git"]["range"].startswith("empty tree"))
        (self.repo / "new.txt").write_text("new\n")
        self.commit("new")
        report = self.check(event="workflow_dispatch", payload={})
        self.assertEqual(report["git"]["base"], initial)
        reproduced = self.check("--base", initial)
        self.assertEqual(reproduced["git"]["tracked_changes"], report["git"]["tracked_changes"])

    def test_shallow_manual_history_cannot_masquerade_as_initial_commit(self):
        self.commit("baseline")
        (self.repo / "new.txt").write_text("new\n")
        self.commit("new")
        clone = self.base / "shallow"
        subprocess.run(["git", "clone", "--depth=1", self.repo.as_uri(), str(clone)],
                       capture_output=True, text=True, check=True)
        self.repo = clone
        report = self.check(event="workflow_dispatch", payload={}, expect=1)
        self.assertIn("unavailable", report["errors"][0])

    def test_broken_method_link_can_be_located_fixed_and_rechecked(self):
        self.commit("baseline")
        path = self.repo / "docs/corp/development-loop.md"
        original = path.read_text()
        path.write_text(original.replace("(verification.md)", "(missing-method.md)"))
        report = self.check(expect=1)
        self.assertIn("missing-method.md", report["errors"][0])
        path.write_text(original)
        self.check()

    def test_missing_active_canon_and_invalid_helper_fail(self):
        path = self.repo / "docs/corp/project.md"
        original = path.read_text()
        path.unlink()
        self.assertIn("docs/corp/project.md", self.check(expect=1)["errors"][0])
        path.write_text(original)
        helper = self.repo / ".agents/corp/enter.py"
        helper.write_text("def broken(:\n")
        self.assertIn("enter.py", self.check(expect=1)["errors"][0])

    def test_missing_native_focus_route_fails_but_unresolved_route_is_valid(self):
        path = self.repo / "docs/corp/canon-map.yaml"
        original = path.read_text()
        self.assertIn("current-delivery-focus", {r["id"] for r in self.check()["unverified_routes"]})
        lines = original.splitlines(keepends=True)
        start = lines.index("  - id: current-delivery-focus\n")
        path.write_text("".join(lines[:start] + lines[start + 3:]))
        self.assertIn("current-delivery-focus", self.check(expect=1)["errors"][0])
        path.write_text(original)
        self.check()

    def test_custom_card_path_is_followed_without_requiring_default_card(self):
        default = self.repo / "docs/corp/owner-communication.md"
        destination = self.repo / "owner.md"
        default.rename(destination)
        communication = self.repo / "docs/corp/communication.md"
        communication.write_text(communication.read_text().replace("(owner-communication.md)", "(../../owner.md)"))
        self.check()

    def test_unrelated_project_skill_is_outside_corp_method_check(self):
        path = self.repo / ".agents/skills/unrelated/SKILL.md"
        path.parent.mkdir()
        path.write_text("Project-owned unrelated notes without skill front matter.\n")
        self.assertEqual(self.check()["structure"]["methods"], 3)

    def test_angle_link_and_title_in_project_owned_card(self):
        target = self.repo / "owner context.md"
        target.write_text("# Owner context\n")
        card = self.repo / "docs/corp/owner-communication.md"
        card.write_text('# Owner\nRead [context](<../../owner context.md> "Context").\n')
        self.check()

    def test_malformed_event_is_a_structured_failure(self):
        self.commit("baseline")
        for payload in ({"pull_request": None}, {"pull_request": {"base": []}}):
            with self.subTest(payload=payload):
                self.assertIn("Malformed", self.check(event="pull_request", payload=payload, expect=1)["errors"][0])


if __name__ == "__main__":
    unittest.main()
