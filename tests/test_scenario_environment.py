import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ScenarioEnvironmentTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="corp-native-fixture-")
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name).resolve() / "project"
        subprocess.run([sys.executable, str(ROOT / "tests/scenarios/preparation_fixture.py"), str(self.repo),
                        "--variant", "prerequisite"], capture_output=True, text=True, check=True)
        self.env = os.environ.copy()
        self.env["PATH"] = str(self.repo / "tools") + os.pathsep + self.env["PATH"]

    def api(self, route, body=None):
        args = ["gh", "api", "repos/fixture/receipt-desk" + route]
        if body is not None:
            args.extend(["--method", body.pop("_method", "POST"), "--input", "-"])
        result = subprocess.run(args, cwd=self.repo, env=self.env,
                                input=json.dumps(body) if body is not None else None,
                                capture_output=True, text=True, check=True)
        return json.loads(result.stdout)

    def test_native_milestones_membership_and_relations_are_actually_retained(self):
        stage = self.api("/milestones", {"title": "Useful result", "description": "Deliver a useful result"})
        self.assertEqual(stage["number"], 2)
        self.api("/issues/8", {"_method": "PATCH", "milestone": 2})
        self.assertEqual([r["number"] for r in self.api("/issues?milestone=2")], [8])
        dependency = self.api("/issues/6")
        self.api("/issues/8/dependencies/blocked_by", {"issue_id": dependency["id"]})
        self.assertEqual([r["number"] for r in self.api("/issues/8/dependencies/blocked_by")], [6])
        self.assertEqual([r["number"] for r in self.api("/issues/6/dependencies/blocking")], [8])
        self.api("/issues/8/sub_issues", {"issue_id": self.api("/issues/9")["id"]})
        self.assertEqual([r["number"] for r in self.api("/issues/8/sub_issues")], [9])
        result = subprocess.run([sys.executable, ".agents/corp/repo-context.py", "--repo", "fixture/receipt-desk", "--issue", "8"],
                                cwd=self.repo, env=self.env, capture_output=True, text=True, check=True)
        observed = json.loads(result.stdout)
        self.assertFalse(observed["errors"])
        self.assertEqual(observed["issue"]["relations"]["blocked_by"][0]["number"], 6)

    def test_reader_follows_real_shared_git_instead_of_initial_cached_sha(self):
        before = self.api("/git/ref/heads/main")["object"]["sha"]
        (self.repo / "result.txt").write_text("A shared result\n")
        for args in (["add", "result.txt"], ["commit", "-m", "A shared fixture result"], ["push", "shared", "main"]):
            subprocess.run(["git", *args], cwd=self.repo, capture_output=True, text=True, check=True)
        after = self.api("/git/ref/heads/main")["object"]["sha"]
        self.assertNotEqual(before, after)
        result = self.api("/contents/result.txt?ref=" + after)
        self.assertEqual(result["encoding"], "base64")


if __name__ == "__main__":
    unittest.main()
