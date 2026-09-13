"""The native Git states the closeout rule's known failures rest on.

The rule that the work, the occupation and the execution site end separately claims
that a merge, a successful delete and a cleaned directory each establish less than an
executor tends to read into them. Those are claims about Git's actual behaviour, so
they are checked here rather than trusted: each test is the counter-example that makes
the corresponding failure shape reproducible offline, on a disposable fixture.
"""

from pathlib import Path
import subprocess
import tempfile
import unittest
from test_creation import git


def run(root, *args):
    """Git without check=True: several of these checks are about the exit status itself."""
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)


class CloseoutFactsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="corpo-closeout-test-")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.remote = self.base / "remote.git"
        self.repo = self.base / "site"
        git(self.base, "init", "--bare", "--initial-branch=main", str(self.remote))
        self.repo.mkdir()
        git(self.repo, "init", "--initial-branch=main")
        git(self.repo, "config", "user.name", "Fixture")
        git(self.repo, "config", "user.email", "fixture@example.invalid")
        (self.repo / ".gitignore").write_text("kept.local\n")
        (self.repo / "result.txt").write_text("shared result\n")
        self.commit("baseline")
        git(self.repo, "remote", "add", "origin", str(self.remote))
        git(self.repo, "push", "origin", "main")

    def commit(self, message):
        git(self.repo, "add", "--all")
        git(self.repo, "commit", "-m", message)
        return git(self.repo, "rev-parse", "HEAD")

    def test_clean_keeps_ignored_content_and_only_x_takes_the_data_worth_keeping(self):
        (self.repo / "kept.local").write_text("private local state\n")
        (self.repo / "scratch.txt").write_text("throwaway\n")
        git(self.repo, "clean", "-fd")
        self.assertFalse((self.repo / "scratch.txt").exists())
        self.assertEqual((self.repo / "kept.local").read_text(), "private local state\n")

        git(self.repo, "clean", "-fdx")
        self.assertFalse((self.repo / "kept.local").exists())

    def test_a_merged_branch_tip_may_carry_commits_the_merge_never_saw(self):
        git(self.repo, "checkout", "-b", "feature")
        (self.repo / "feature.txt").write_text("delivered\n")
        merged = self.commit("delivered part")
        git(self.repo, "checkout", "main")
        git(self.repo, "merge", "--no-ff", "feature", "-m", "integrate feature")
        self.assertEqual(run(self.repo, "merge-base", "--is-ancestor", merged, "main").returncode, 0)

        git(self.repo, "checkout", "feature")
        (self.repo / "feature.txt").write_text("delivered, then edited after the merge\n")
        later = self.commit("work after the merge")
        git(self.repo, "checkout", "main")
        self.assertNotEqual(later, merged)
        self.assertEqual(run(self.repo, "merge-base", "--is-ancestor", later, "main").returncode, 1)
        self.assertEqual(git(self.repo, "branch", "--merged", "main", "--format=%(refname:short)"), "main")

    def test_a_squash_merge_leaves_identical_content_without_ancestry(self):
        git(self.repo, "checkout", "-b", "feature")
        (self.repo / "feature.txt").write_text("delivered\n")
        tip = self.commit("delivered part")
        git(self.repo, "checkout", "main")
        git(self.repo, "merge", "--squash", "feature")
        self.commit("squashed feature")

        self.assertEqual(git(self.repo, "diff", "main", "feature"), "")
        self.assertEqual(run(self.repo, "merge-base", "--is-ancestor", tip, "main").returncode, 1)
        self.assertEqual(run(self.repo, "branch", "-d", "feature").returncode, 1)

    def test_a_successful_delete_reports_the_command_not_the_remaining_state(self):
        git(self.repo, "checkout", "-b", "feature")
        (self.repo / "feature.txt").write_text("only here\n")
        tip = self.commit("unique work")
        git(self.repo, "branch", "spare", "feature")
        git(self.repo, "push", "origin", "feature", "spare")
        git(self.repo, "checkout", "main")

        self.assertEqual(run(self.repo, "push", "origin", "--delete", "feature").returncode, 0)
        refs = git(self.repo, "ls-remote", "--heads", str(self.remote))
        self.assertNotIn("refs/heads/feature", refs)
        # The command succeeded and the ref is gone; the content is not, and would not have
        # been even without the other holder. Only the readback distinguishes the two.
        self.assertIn("refs/heads/spare", refs)
        self.assertEqual(run(self.remote, "cat-file", "-e", tip + "^{commit}").returncode, 0)

        self.assertEqual(run(self.repo, "push", "origin", "--delete", "spare").returncode, 0)
        self.assertNotIn("refs/heads/spare", git(self.repo, "ls-remote", "--heads", str(self.remote)))
        self.assertEqual(run(self.remote, "cat-file", "-e", tip + "^{commit}").returncode, 0)


if __name__ == "__main__":
    unittest.main()
