from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from test_creation import git, load

ROOT = Path(__file__).resolve().parents[1]
HELPERS = ROOT / "skills/cybercorp/assets/corp/.agents/corp"
entry = load("entry", HELPERS / "enter.py")


class EntryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="corpo-entry-test-")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.remote = self.base / "remote.git"
        self.source = self.base / "source"
        self.local = self.base / "local"
        self.source.mkdir()
        git(self.base, "init", "--bare", "--initial-branch=develop", str(self.remote))
        git(self.source, "init", "--initial-branch=develop")
        git(self.source, "config", "user.name", "Fixture")
        git(self.source, "config", "user.email", "fixture@example.invalid")
        (self.source / "AGENTS.md").write_text("Initial instructions\n")
        (self.source / ".gitignore").write_text("ignored.local\n")
        git(self.source, "add", ".")
        git(self.source, "commit", "-m", "initial fixture")
        git(self.source, "remote", "add", "origin", str(self.remote))
        git(self.source, "push", "origin", "develop")
        git(self.base, "clone", str(self.remote), str(self.local))
        (self.source / "AGENTS.md").write_text("New current instructions\n")
        git(self.source, "add", ".")
        git(self.source, "commit", "-m", "new rule fixture")
        git(self.source, "push", "origin", "develop")
        self.sha = git(self.source, "rev-parse", "HEAD")

    def test_actual_worktree_gets_fixed_remote_rules_and_preserves_all_local_work(self):
        (self.local / "AGENTS.md").write_text("Private local edits\n")
        git(self.local, "add", "AGENTS.md")
        (self.local / "AGENTS.md").write_text("More unstaged local edits\n")
        (self.local / "untracked.txt").write_text("keep me")
        (self.local / "ignored.local").write_text("private local state")
        head = git(self.local, "rev-parse", "HEAD")
        status = git(self.local, "status", "--porcelain=v1", "--untracked-files=all")
        staged = git(self.local, "diff", "--cached")
        fetch_head = self.local / ".git/FETCH_HEAD"
        fetch_head.write_text("existing fetch scratch\n")
        destination = self.base / "new worker;$(false)"
        result = entry.enter(self.local, destination)
        self.assertEqual(result["status"], "checkout_created")
        self.assertEqual(result["remote_branch"], "develop")
        self.assertEqual(git(destination, "rev-parse", "HEAD"), self.sha)
        self.assertEqual((destination / "AGENTS.md").read_text(), "New current instructions\n")
        self.assertEqual(git(self.local, "rev-parse", "HEAD"), head)
        self.assertEqual(git(self.local, "status", "--porcelain=v1", "--untracked-files=all"), status)
        self.assertEqual(git(self.local, "diff", "--cached"), staged)
        self.assertEqual(fetch_head.read_text(), "existing fetch scratch\n")
        self.assertEqual((self.local / "ignored.local").read_text(), "private local state")

    def test_observe_and_dry_run_do_not_fetch_or_create_worktree(self):
        before = git(self.local, "worktree", "list", "--porcelain")
        self.assertEqual(entry.enter(self.local)["status"], "observed")
        result = entry.enter(self.local, self.base / "planned", dry_run=True)
        self.assertEqual(result["status"], "planned")
        self.assertFalse((self.base / "planned").exists())
        self.assertEqual(git(self.local, "worktree", "list", "--porcelain"), before)
        self.assertNotEqual(git(self.local, "rev-parse", "origin/develop"), self.sha)

    def test_remote_advance_during_fetch_does_not_change_the_selected_baseline(self):
        original = entry.git
        advanced = False

        def concurrent(root, *args):
            nonlocal advanced
            if args[0] == "fetch" and not advanced:
                advanced = True
                (self.source / "later.txt").write_text("a later remote change")
                git(self.source, "add", ".")
                git(self.source, "commit", "-m", "concurrent fixture")
                git(self.source, "push", "origin", "develop")
            return original(root, *args)

        with patch.object(entry, "git", side_effect=concurrent):
            result = entry.enter(self.local, self.base / "pinned")
        self.assertEqual(result["remote_commit"], self.sha)
        self.assertEqual(git(self.base / "pinned", "rev-parse", "HEAD"), self.sha)
        self.assertNotEqual(git(self.source, "rev-parse", "HEAD"), self.sha)

    def test_existing_or_nested_destination_is_preserved(self):
        target = self.base / "foreign"
        target.mkdir()
        (target / "keep").write_text("owned elsewhere")
        for dest in (target, self.local / "nested"):
            with self.subTest(dest=dest), self.assertRaises(entry.EntryError):
                entry.enter(self.local, dest)
        self.assertEqual((target / "keep").read_text(), "owned elsewhere")
        self.assertFalse((self.local / "nested").exists())

    def test_unavailable_remote_is_not_old_cache_success(self):
        git(self.local, "remote", "set-url", "origin", str(self.base / "missing.git"))
        with self.assertRaises(entry.EntryError):
            entry.enter(self.local, self.base / "never-created")
        self.assertFalse((self.base / "never-created").exists())


if __name__ == "__main__":
    unittest.main()
