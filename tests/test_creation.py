import base64
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/cybercorp"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


creator = load("creator", SKILL / "scripts/cybercorp.py")
context = load("created_context", SKILL / "assets/corp/.agents/corp/repo-context.py")


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout.strip()


class CreationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="cybercorp-test-")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.repo = self.base / "project with spaces;$(false)"
        self.brief = {"name": "Photo Index", "goal": "Find user-owned photos by their captions.",
                      "scope": ["Import a folder", "Edit captions", "Search local captions"]}

    def existing(self):
        self.repo.mkdir()
        git(self.repo, "init", "--initial-branch=main")

    def test_new_project_is_runnable_without_creator_after_transport(self):
        portable = self.base / "portable-skill"
        shutil.copytree(SKILL, portable, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        brief = self.base / "brief.json"
        brief.write_text(json.dumps(self.brief))
        result = subprocess.run([sys.executable, str(portable / "scripts/cybercorp.py"), str(self.repo),
                                 "--brief", str(brief)], cwd=self.base, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "installed")
        shutil.rmtree(portable)
        self.assertEqual(git(self.repo, "rev-parse", "--show-toplevel"), str(self.repo))
        helper = self.repo / ".agents/corp/spec-checkpoint.py"
        body = self.base / "issue.md"
        body.write_text("<!-- spec:start -->\nOutcome: searchable captions\n<!-- spec:end -->\n")
        result = subprocess.run([sys.executable, str(helper), str(body)], cwd=self.repo,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(result.stdout.strip(), r"^[0-9a-f]{64}$")
        self.assertFalse((self.repo / ".agents/skills/corpo-launcher").exists())
        self.assertFalse((self.repo / "brief.json").exists())

    def test_existing_root_bytes_and_application_files_are_preserved(self):
        self.existing()
        originals = {"README.md": b"# Existing app\r\n\r\nKeep exact text.\r\n",
                     "AGENTS.md": b"Do not change the product contract.\n",
                     "app.py": b"print('working')\n", "private.local": b"local scratch"}
        for name, data in originals.items():
            (self.repo / name).write_bytes(data)
        git(self.repo, "add", "app.py")
        staged = git(self.repo, "diff", "--cached")
        creator.install(self.repo, self.brief)
        for name in ("README.md", "AGENTS.md"):
            self.assertTrue((self.repo / name).read_bytes().startswith(originals[name]))
        for name in ("app.py", "private.local"):
            self.assertEqual((self.repo / name).read_bytes(), originals[name])
        self.assertEqual(git(self.repo, "diff", "--cached"), staged)

    def test_existing_goal_owner_is_reused_without_second_goal(self):
        self.existing()
        (self.repo / "product.md").write_text("# Accepted project\nLocal captions only.\n")
        brief = {"name": "Photo Index", "project_ref": "product.md",
                 "canon": [{"id": "storage", "target": None, "status": "unresolved"}]}
        path = self.base / "brief.json"
        path.write_text(json.dumps(brief))
        creator.install(self.repo, creator.read_brief(path, self.repo))
        self.assertFalse((self.repo / "docs/corp/project.md").exists())
        rows = context.parse_map((self.repo / "docs/corp/canon-map.yaml").read_text())
        self.assertEqual(rows[0]["target"], "product.md")
        self.assertEqual(rows[-1]["status"], "unresolved")

    def test_dry_run_has_no_filesystem_writes(self):
        before = list(self.base.iterdir())
        result = creator.install(self.repo, self.brief, dry_run=True)
        self.assertEqual(result["status"], "planned")
        self.assertEqual(list(self.base.iterdir()), before)

    def test_all_collisions_checked_before_git_init_or_root_edit(self):
        target = self.repo / "docs/corp/claim-protocol.md"
        target.parent.mkdir(parents=True)
        target.write_text("existing contract")
        before = {p.relative_to(self.repo): p.read_bytes() for p in self.repo.rglob("*") if p.is_file()}
        with self.assertRaises(creator.InstallError):
            creator.install(self.repo, self.brief)
        self.assertFalse((self.repo / ".git").exists())
        after = {p.relative_to(self.repo): p.read_bytes() for p in self.repo.rglob("*") if p.is_file()}
        self.assertEqual(after, before)

    def test_reinstall_preserves_project_owned_edits(self):
        creator.install(self.repo, self.brief)
        file = self.repo / ".agents/skills/work-corp/SKILL.md"
        file.write_text(file.read_text() + "\nA project-specific refinement.\n")
        body = file.read_bytes()
        result = creator.install(self.repo, self.brief)
        self.assertEqual(result["status"], "already_installed")
        self.assertIn(".agents/skills/work-corp/SKILL.md", result["preserved_project_edits"])
        self.assertEqual(file.read_bytes(), body)
        self.assertEqual((self.repo / "AGENTS.md").read_text().count(creator.START), 1)

    def test_changed_input_cannot_overwrite_existing_goal(self):
        creator.install(self.repo, self.brief)
        before = (self.repo / "docs/corp/project.md").read_bytes()
        with self.assertRaises(creator.InstallError):
            creator.install(self.repo, {**self.brief, "goal": "A different goal"})
        self.assertEqual((self.repo / "docs/corp/project.md").read_bytes(), before)

    def test_changed_package_with_same_version_does_not_claim_current_installation(self):
        creator.install(self.repo, self.brief)
        old = (self.repo / ".agents/corp/repo-context.py").read_bytes()
        changed = self.base / "changed-assets"
        shutil.copytree(creator.ASSETS, changed)
        helper = changed / ".agents/corp/repo-context.py"
        helper.write_text(helper.read_text() + "\n# Updated implementation\n")
        with patch.object(creator, "ASSETS", changed), self.assertRaises(creator.InstallError):
            creator.install(self.repo, self.brief)
        self.assertEqual((self.repo / ".agents/corp/repo-context.py").read_bytes(), old)

    def test_symlink_or_parent_file_cannot_redirect_installation(self):
        self.repo.mkdir()
        elsewhere = self.base / "elsewhere"
        elsewhere.mkdir()
        (self.repo / ".agents").symlink_to(elsewhere, target_is_directory=True)
        with self.assertRaises(creator.InstallError):
            creator.install(self.repo, self.brief)
        self.assertEqual(list(elsewhere.iterdir()), [])
        (self.repo / ".agents").unlink()
        (self.repo / ".agents").write_text("original")
        with self.assertRaises(creator.InstallError):
            creator.install(self.repo, self.brief)
        self.assertEqual((self.repo / ".agents").read_text(), "original")

    def test_nested_repository_is_not_created_implicitly(self):
        self.existing()
        nested = self.repo / "child"
        with self.assertRaises(creator.InstallError):
            creator.install(nested, self.brief)
        self.assertFalse(nested.exists())

    def test_missing_or_external_inputs_are_not_active_canon(self):
        self.existing()
        path = self.base / "brief.json"
        for extra in ({"sources": ["../outside"]}, {"sources": ["/private/file"]},
                      {"canon": [{"id": "missing", "target": "missing.md", "status": "active"}]},
                      {"canon": [{"id": "missing", "target": None, "status": "active"}]}):
            path.write_text(json.dumps({**self.brief, **extra}))
            with self.subTest(extra=extra), self.assertRaises(creator.InstallError):
                creator.read_brief(path, self.repo)

    def test_native_focus_is_optional_and_not_fabricated(self):
        creator.install(self.repo, self.brief)
        rows = context.parse_map((self.repo / "docs/corp/canon-map.yaml").read_text())
        focus = next(row for row in rows if row["id"] == "current-delivery-focus")
        self.assertIsNone(focus["target"])
        self.assertEqual(focus["status"], "unresolved")
        work = next(row for row in rows if row["id"] == "active-change-specs")
        self.assertIsNone(work["target"])
        self.assertEqual(work["status"], "unresolved")

    def test_supplied_shared_repository_is_routed_without_creating_it(self):
        creator.install(self.repo, {**self.brief, "github": "sample/photo-index"})
        rows = context.parse_map((self.repo / "docs/corp/canon-map.yaml").read_text())
        work = next(row for row in rows if row["id"] == "active-change-specs")
        self.assertEqual(work["target"], "https://github.com/sample/photo-index/issues")
        self.assertEqual(work["status"], "active")
        self.assertEqual(git(self.repo, "remote"), "")

    def test_generated_context_cli_reads_native_default_branch_after_creator_leaves(self):
        creator.install(self.repo, {**self.brief, "github": "sample/photo-index", "milestone": 4})
        git(self.repo, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "--allow-empty", "-m", "fixture")
        git(self.repo, "remote", "add", "origin", "https://github.com/sample/photo-index.git")
        sha = "b" * 40
        prefix = "repos/sample/photo-index"
        routes = {
            prefix: {"default_branch": "develop"},
            prefix + "/git/ref/heads/develop": {"object": {"sha": sha}},
            prefix + "/contents/docs/corp/canon-map.yaml?ref=" + sha:
                {"encoding": "base64", "content": base64.b64encode((self.repo / "docs/corp/canon-map.yaml").read_bytes()).decode()},
            prefix + "/milestones/4": {"number": 4, "title": "Local photo search", "state": "open"},
            prefix + "/issues?milestone=4&state=open&per_page=100": [[]],
            prefix + "/pulls?state=open&per_page=100": [[]],
            prefix + "/issues?milestone=4&labels=work%3Acoordination&state=all&per_page=100": [[]],
        }
        route_file = self.base / "routes.json"
        route_file.write_text(json.dumps(routes))
        bindir = self.base / "bin"
        bindir.mkdir()
        fake = bindir / "gh"
        fake.write_text("#!" + sys.executable + "\nimport json,os,sys\n"
                        "endpoint=sys.argv[sys.argv.index('GET')+1]\n"
                        "routes=json.load(open(os.environ['CORP_FIXTURE_ROUTES']))\n"
                        "print(json.dumps(routes[endpoint]))\n")
        fake.chmod(0o700)
        env = {**os.environ, "PATH": str(bindir) + os.pathsep + os.environ["PATH"],
               "CORP_FIXTURE_ROUTES": str(route_file)}
        result = subprocess.run([sys.executable, str(self.repo / ".agents/corp/repo-context.py")],
                                cwd=self.repo, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["remote_branch"], "develop")
        self.assertEqual(report["remote_head"], sha)
        self.assertEqual(report["focus"]["number"], 4)
        self.assertFalse(report["atomic_snapshot"])


if __name__ == "__main__":
    unittest.main()
