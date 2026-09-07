import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "adapters/kiro.py"
spec = importlib.util.spec_from_file_location("kiro_corpo", SCRIPT)
corpo = importlib.util.module_from_spec(spec)
with patch.object(sys, "path", [str(SCRIPT.parent), *sys.path]):
    spec.loader.exec_module(corpo)


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.repo = self.root / "repo with spaces;$(false)"
        self.repo.mkdir()
        (self.repo / ".git").mkdir()
        for name in ("AGENTS.md", "README.md"):
            (self.repo / name).write_text("Disposable test fixture.\n")
        self.cli = self.root / "fake-kiro"
        self.cli.write_text(
            "#!" + sys.executable + "\n"
            "import json,os,sys\n"
            "if '--list-sessions' in sys.argv:\n"
            " print(os.environ.get('CORPO_TEST_SESSIONS', '[]'))\n"
            "else:\n"
            " print(json.dumps({'argv':sys.argv[1:], 'cwd':os.getcwd()}),flush=True)\n"
        )
        self.cli.chmod(0o700)

    def start_args(self, *extra):
        return ["start", "--kiro", str(self.cli), "--repo", str(self.repo), *extra]

    def invoke(self, args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = corpo.main(args)
        return code, json.loads(output.getvalue())

    def listing(self, sessions, **extra):
        return [{"cwd": str(self.root), "sessions": sessions, "complete": True, **extra}]

    def session(self, sid="one", title="test"):
        return {"sessionId": sid, "title": title, "source": "classic"}

    def native(self, payload):
        with patch.dict(os.environ, {"CORPO_TEST_SESSIONS": json.dumps(payload)}):
            return corpo.native_sessions(str(self.cli), self.root)

    def test_dry_run_never_spawns_or_discovers(self):
        with patch.object(corpo.subprocess, "Popen", side_effect=AssertionError), \
             patch.object(corpo, "native_sessions", side_effect=AssertionError):
            code, result = self.invoke(self.start_args("--dry-run"))
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "planned")
        self.assertNotIn("--trust-all-tools", result["argv"])
        self.assertEqual(result["cwd"], str(self.repo))
        self.assertIn(str(self.repo), result["argv"][-1])

    def test_start_prompt_is_exactly_the_latest_three_lines(self):
        tag = "71bb04d6-8aec-4f93-a42f-2b46422f1647"
        self.assertEqual(corpo.start_prompt(self.repo, tag),
                         f"[corpo:{tag}]\n仓库入口：" + json.dumps(str(self.repo), ensure_ascii=False) +
                         "\n进入该仓库，按仓库规则自主开展工作。本次没有 merge 授权。")

    def test_background_requires_explicit_trust(self):
        with patch.object(corpo.subprocess, "Popen", side_effect=AssertionError):
            code, result = self.invoke(self.start_args("--background"))
        self.assertEqual(code, 2)
        self.assertIn("--tools all", result["message"])

    def test_non_tty_does_not_auto_trust(self):
        with patch.object(corpo.sys.stdin, "isatty", return_value=False), \
             patch.object(corpo.subprocess, "Popen", side_effect=AssertionError):
            code, result = self.invoke(self.start_args())
        self.assertEqual(code, 2)
        self.assertIn("terminal", result["message"])

    def test_missing_entry_rejected(self):
        (self.repo / "AGENTS.md").unlink()
        code, result = self.invoke(self.start_args("--dry-run"))
        self.assertEqual(code, 2)
        self.assertIn("AGENTS.md", result["message"])

    def test_linked_worktree_git_file_accepted(self):
        (self.repo / ".git").rmdir()
        (self.repo / ".git").write_text("gitdir: test\n")
        self.assertEqual(corpo.repository(self.repo), self.repo)

    def test_executable_becomes_absolute(self):
        with patch.object(corpo.shutil, "which", return_value=os.path.relpath(self.cli)):
            self.assertEqual(corpo.executable("fake"), str(self.cli))

    def test_background_real_subprocess_no_shell_and_private_log(self):
        children = []
        original = subprocess.Popen

        def capture(*args, **kwargs):
            child = original(*args, **kwargs)
            children.append(child)
            return child

        diagnostics = self.root / "private-diagnostics"
        diagnostics.mkdir(mode=0o700)
        with patch.object(corpo.tempfile, "mkdtemp", return_value=str(diagnostics)), \
             patch.object(corpo.subprocess, "Popen", side_effect=capture):
            code, result = self.invoke(self.start_args(
                "--cwd", str(self.root), "--model", "explicit-model",
                "--tools", "all", "--background"))
        self.assertEqual(code, 0)
        self.assertEqual(children[0].wait(timeout=5), 0)
        self.assertEqual(result["status"], "process_spawned")
        self.assertIsNone(result["session_id"])
        log = Path(result["output_log"])
        self.assertEqual(log.stat().st_mode & 0o777, 0o600)
        actual = json.loads(log.read_text())
        self.assertEqual(actual["cwd"], str(self.root))
        self.assertEqual(actual["argv"][:5], ["chat", "--agent", "kiro_default", "--model", "explicit-model"])
        self.assertIn("--trust-all-tools", actual["argv"])
        self.assertIn("--no-interactive", actual["argv"])
        self.assertTrue(actual["argv"][-1].startswith("[corpo:" + result["launch_tag"] + "]"))
        self.assertIn(str(self.repo), actual["argv"][-1])
        self.assertNotIn("argv", result)

    def test_native_listing_is_cwd_scoped(self):
        other = {"cwd": str(self.repo), "sessions": [self.session("wrong")], "complete": True}
        result = self.native([other, *self.listing([self.session()])])
        self.assertEqual([item["sessionId"] for item in result], ["one"])

    def test_empty_complete_listing(self):
        self.assertEqual(self.native(self.listing([])), [])

    def test_partial_wrong_cwd_or_duplicate_rejected(self):
        for payload in (
            [], self.listing([], complete=False),
            self.listing([self.session(), self.session()]),
            [{"cwd": str(self.repo), "sessions": [], "complete": True}],
            {"sessions": []}, self.listing([{}]),
        ):
            with self.subTest(payload=payload), self.assertRaises(corpo.LaunchError):
                self.native(payload)

    def test_native_error_does_not_expose_output(self):
        result = subprocess.CompletedProcess([], 1, "PRIVATE", "PRIVATE")
        with patch.object(corpo.subprocess, "run", return_value=result):
            with self.assertRaises(corpo.LaunchError) as error:
                corpo.native_sessions(str(self.cli), self.root)
        self.assertNotIn("PRIVATE", str(error.exception))

    def test_match_never_falls_back_to_newest(self):
        tag = "71bb04d6-8aec-4f93-a42f-2b46422f1647"
        args = ["sessions", "--kiro", str(self.cli), "--cwd", str(self.root), "--match", tag]
        for titles, expected in ((["renamed"], "unresolved"),
                                 ([f"[corpo:{tag}] test"], "unique_match"),
                                 ([f"[corpo:{tag}] one", f"[corpo:{tag}] two"], "unresolved")):
            payload = self.listing([self.session(str(i), title) for i, title in enumerate(titles)])
            with patch.dict(os.environ, {"CORPO_TEST_SESSIONS": json.dumps(payload)}):
                code, result = self.invoke(args)
            self.assertEqual(result["status"], expected)
            self.assertEqual(code, 0 if expected == "unique_match" else 2)

    def test_resume_requires_exact_session_in_cwd(self):
        args = ["resume", "--kiro", str(self.cli), "--cwd", str(self.root),
                "--session", "wrong", "--tools", "all", "--background"]
        with patch.object(corpo, "native_sessions", return_value=[self.session()]), \
             patch.object(corpo.subprocess, "Popen", side_effect=AssertionError):
            code, result = self.invoke(args)
        self.assertEqual(code, 2)
        self.assertIn("not uniquely present", result["message"])

    def test_resume_plan_keeps_session_and_model(self):
        args = ["resume", "--kiro", str(self.cli), "--cwd", str(self.root),
                "--session", "known-id", "--model", "explicit", "--dry-run"]
        code, result = self.invoke(args)
        self.assertEqual(code, 0)
        self.assertIn("--resume-id", result["argv"])
        self.assertIn("known-id", result["argv"])
        self.assertNotIn("--agent", result["argv"])
        self.assertIsNone(result["launch_tag"])

    def test_verified_resume_reaches_the_native_cli_with_original_identity(self):
        args = ["resume", "--kiro", str(self.cli), "--cwd", str(self.root),
                "--session", "known-id", "--model", "explicit", "--tools", "all", "--background"]
        children = []
        original = subprocess.Popen

        def capture(*args, **kwargs):
            child = original(*args, **kwargs)
            children.append(child)
            return child

        diagnostics = self.root / "resume-output"
        diagnostics.mkdir(mode=0o700)
        payload = self.listing([self.session("known-id")])
        with patch.dict(os.environ, {"CORPO_TEST_SESSIONS": json.dumps(payload)}), \
             patch.object(corpo.tempfile, "mkdtemp", return_value=str(diagnostics)), \
             patch.object(corpo.subprocess, "Popen", side_effect=capture):
            code, result = self.invoke(args)
        self.assertEqual(code, 0)
        worker = children[-1]
        self.assertEqual(worker.wait(timeout=5), 0)
        actual = json.loads(Path(result["output_log"]).read_text())
        self.assertEqual(actual["argv"][:5], ["chat", "--resume-id", "known-id", "--model", "explicit"])
        self.assertEqual(actual["cwd"], str(self.root))
        self.assertNotIn("--agent", actual["argv"])

    def test_interactive_handoff_executes_without_background(self):
        with patch.object(corpo.sys.stdin, "isatty", return_value=True), \
             patch.object(corpo.os, "chdir") as chdir, \
             patch.object(corpo.os, "execv", side_effect=SystemExit(0)) as execute:
            output = io.StringIO()
            output.isatty = lambda: True
            with contextlib.redirect_stdout(output), self.assertRaises(SystemExit):
                corpo.main(self.start_args())
        chdir.assert_called_once_with(self.repo)
        self.assertEqual(execute.call_args.args[0], str(self.cli))
        self.assertNotIn("--no-interactive", execute.call_args.args[1])
        self.assertEqual(json.loads(output.getvalue())["status"], "interactive_handoff")

    def test_invalid_resume_id_rejected_before_discovery(self):
        args = ["resume", "--kiro", str(self.cli), "--cwd", str(self.root),
                "--session=--untrusted", "--dry-run"]
        with patch.object(corpo, "native_sessions", side_effect=AssertionError):
            code, result = self.invoke(args)
        self.assertEqual(code, 2)
        self.assertIn("Invalid session ID", result["message"])

    def test_discovery_timeout_and_invalid_json_rejected(self):
        with patch.object(corpo.subprocess, "run", side_effect=subprocess.TimeoutExpired("fake", 30)):
            with self.assertRaises(corpo.LaunchError):
                corpo.native_sessions(str(self.cli), self.root)
        result = subprocess.CompletedProcess([], 0, "not-json", "")
        with patch.object(corpo.subprocess, "run", return_value=result):
            with self.assertRaises(corpo.LaunchError):
                corpo.native_sessions(str(self.cli), self.root)


if __name__ == "__main__":
    unittest.main()
