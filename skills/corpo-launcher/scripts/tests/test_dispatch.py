import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "corpo.py"


class DispatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.repo = self.root / "repo with spaces;$(false)"
        self.repo.mkdir()
        (self.repo / ".git").mkdir()
        for name in ("AGENTS.md", "README.md"):
            (self.repo / name).write_text("Local fixture\n")
        self.cli = self.root / "native.py"
        self.cli.write_text("import json,os,sys\nprint(json.dumps({'cwd':os.getcwd(),'argv':sys.argv[1:]}))\n")

    def run_cli(self, *args, script=SCRIPT):
        return subprocess.run([sys.executable, str(script), *map(str, args)],
                              cwd=self.root, capture_output=True, text=True)

    def test_two_native_command_shapes_keep_exact_arguments_and_cwd(self):
        for flags in (["chat", "--prompt", "{prompt}"], ["exec", "{prompt}", "--model", "chosen"]):
            with self.subTest(flags=flags):
                r = self.run_cli("--runtime", "cli", "start", "--repo", self.repo,
                                 "--", sys.executable, self.cli, *flags, "literal;$(false)", "{repo}")
                self.assertEqual(r.returncode, 0, r.stderr)
                result = json.loads(r.stdout)
                self.assertEqual(result["cwd"], str(self.repo))
                self.assertEqual(result["argv"][-2:], ["literal;$(false)", str(self.repo)])
                prompt = result["argv"][flags.index("{prompt}")]
                self.assertEqual(len(prompt.splitlines()), 3)
                self.assertIn(json.dumps(str(self.repo), ensure_ascii=False), prompt)

    def test_generic_dry_run_does_not_execute_native_command(self):
        marker = self.root / "executed"
        self.cli.write_text("from pathlib import Path\nPath(" + repr(str(marker)) + ").touch()\n")
        r = self.run_cli("--runtime", "cli", "start", "--repo", self.repo, "--dry-run",
                         "--", sys.executable, self.cli, "{prompt}")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["status"], "planned")
        self.assertFalse(marker.exists())

    def test_custom_adapter_receives_args_and_propagates_exit_code(self):
        self.cli.write_text(self.cli.read_text() + "sys.exit(7)\n")
        r = self.run_cli("--adapter", self.cli, "resume", "--session", "one", "--help")
        self.assertEqual(r.returncode, 7)
        self.assertEqual(json.loads(r.stdout)["argv"], ["resume", "--session", "one", "--help"])

    def test_transported_kiro_example_uses_its_native_arguments(self):
        copied = self.root / "copied-launcher"
        shutil.copytree(SCRIPT.parent, copied, ignore=shutil.ignore_patterns("__pycache__"))
        r = self.run_cli("--runtime", "kiro", "start", "--repo", self.repo, "--kiro", sys.executable,
                         "--model", "user-model", "--dry-run", script=copied / "corpo.py")
        self.assertEqual(r.returncode, 0, r.stderr)
        result = json.loads(r.stdout)
        self.assertEqual(result["argv"][1:6], ["chat", "--agent", "kiro_default", "--model", "user-model"])

    def test_relative_executable_survives_launch_directory_change(self):
        executable = self.root / "native-cli"
        executable.write_text("#!" + sys.executable + "\n" + self.cli.read_text())
        executable.chmod(0o700)
        r = self.run_cli("--runtime", "cli", "start", "--repo", self.repo,
                         "--", "./native-cli", "{prompt}")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["cwd"], str(self.repo))


if __name__ == "__main__":
    unittest.main()
