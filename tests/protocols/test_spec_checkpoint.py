import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / ".agents/corp/spec-checkpoint.py"

spec = importlib.util.spec_from_file_location("spec_checkpoint", HELPER)
spec_checkpoint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(spec_checkpoint)


def run(args, input_bytes=None):
    return subprocess.run([sys.executable, str(HELPER), *args], input=input_bytes,
                          capture_output=True)


class NormalizationTests(unittest.TestCase):
    """Hash stability and error branches, in-process against the module."""

    BODY = "before\n<!-- spec:start -->\nOutcome: X\nBoundary: Y\n<!-- spec:end -->\nafter\n"

    def test_hash_is_stable_and_is_lowercase_hex_sha256(self):
        digest = spec_checkpoint.spec_hash(self.BODY)
        self.assertRegex(digest, r"^[0-9a-f]{64}$")
        self.assertEqual(spec_checkpoint.spec_hash(self.BODY), digest)

    def test_crlf_and_lone_cr_produce_the_same_hash_as_lf(self):
        digest = spec_checkpoint.spec_hash(self.BODY)
        self.assertEqual(spec_checkpoint.spec_hash(self.BODY.replace("\n", "\r\n")), digest)
        self.assertEqual(spec_checkpoint.spec_hash(self.BODY.replace("\n", "\r")), digest)

    def test_trailing_whitespace_on_a_line_does_not_affect_hash(self):
        digest = spec_checkpoint.spec_hash(self.BODY)
        noisy = self.BODY.replace("Outcome: X", "Outcome: X   \t  ")
        self.assertEqual(spec_checkpoint.spec_hash(noisy), digest)

    def test_leading_whitespace_on_a_line_does_affect_hash(self):
        digest = spec_checkpoint.spec_hash(self.BODY)
        noisy = self.BODY.replace("Outcome: X", "   Outcome: X")
        self.assertNotEqual(spec_checkpoint.spec_hash(noisy), digest)

    def test_trailing_blank_lines_before_end_marker_do_not_affect_hash(self):
        digest = spec_checkpoint.spec_hash(self.BODY)
        noisy = self.BODY.replace("<!-- spec:end -->", "\n\n   \n<!-- spec:end -->")
        self.assertEqual(spec_checkpoint.spec_hash(noisy), digest)

    def test_bytes_input_is_accepted_and_utf8_decoded(self):
        digest = spec_checkpoint.spec_hash(self.BODY)
        self.assertEqual(spec_checkpoint.spec_hash(self.BODY.encode("utf-8")), digest)

    def test_non_utf8_bytes_raise_unicode_error(self):
        with self.assertRaises(UnicodeError):
            spec_checkpoint.spec_hash(b"\xff\xfe" + self.BODY.encode("utf-8"))

    def test_missing_markers_is_an_error(self):
        with self.assertRaisesRegex(spec_checkpoint.SpecCheckpointError,
                                    "expected exactly one spec:start and one spec:end marker"):
            spec_checkpoint.spec_hash("no markers at all\n")

    def test_only_one_marker_present_is_an_error(self):
        with self.assertRaisesRegex(spec_checkpoint.SpecCheckpointError,
                                    "expected exactly one spec:start and one spec:end marker"):
            spec_checkpoint.spec_hash("<!-- spec:start -->\nbody\n")

    def test_duplicated_markers_is_an_error(self):
        doubled = self.BODY + "<!-- spec:start -->\nmore\n<!-- spec:end -->\n"
        with self.assertRaisesRegex(spec_checkpoint.SpecCheckpointError,
                                    "expected exactly one spec:start and one spec:end marker"):
            spec_checkpoint.spec_hash(doubled)

    def test_markers_out_of_order_is_an_error(self):
        reversed_body = "<!-- spec:end -->\nbody\n<!-- spec:start -->\n"
        with self.assertRaisesRegex(spec_checkpoint.SpecCheckpointError, "Spec markers are out of order"):
            spec_checkpoint.spec_hash(reversed_body)

    def test_marker_not_occupying_its_own_line_is_an_error(self):
        with self.assertRaisesRegex(spec_checkpoint.SpecCheckpointError, "own lines"):
            spec_checkpoint.spec_hash("prefix <!-- spec:start -->\nbody\n<!-- spec:end -->\n")
        with self.assertRaisesRegex(spec_checkpoint.SpecCheckpointError, "own lines"):
            spec_checkpoint.spec_hash("<!-- spec:start -->\nbody\n<!-- spec:end --> suffix\n")

    def test_empty_spec_area_is_an_error(self):
        with self.assertRaisesRegex(spec_checkpoint.SpecCheckpointError, "Spec area is empty"):
            spec_checkpoint.spec_hash("<!-- spec:start -->\n<!-- spec:end -->\n")

    def test_whitespace_only_spec_area_is_an_error(self):
        with self.assertRaisesRegex(spec_checkpoint.SpecCheckpointError, "Spec area is empty"):
            spec_checkpoint.spec_hash("<!-- spec:start -->\n   \n\t\n\n<!-- spec:end -->\n")


class SourceValidationTests(unittest.TestCase):
    def test_valid_https_source_is_accepted(self):
        source = "https://github.com/owner/repo/issues/1"
        self.assertEqual(spec_checkpoint.validate_source(source), source)

    def test_valid_source_with_port_is_accepted(self):
        source = "https://github.example.com:8443/owner/repo"
        self.assertEqual(spec_checkpoint.validate_source(source), source)

    def test_non_https_scheme_is_rejected(self):
        with self.assertRaises(spec_checkpoint.SpecCheckpointError):
            spec_checkpoint.validate_source("http://github.com/owner/repo")

    def test_non_string_is_rejected(self):
        with self.assertRaises(spec_checkpoint.SpecCheckpointError):
            spec_checkpoint.validate_source(None)

    def test_source_with_whitespace_is_rejected(self):
        with self.assertRaises(spec_checkpoint.SpecCheckpointError):
            spec_checkpoint.validate_source("https://github.com/owner/repo issues")

    def test_source_with_angle_brackets_or_quotes_or_backtick_or_backslash_is_rejected(self):
        for bad in ("https://x.com/<a>", 'https://x.com/"a"', "https://x.com/`a`", "https://x.com/\\a"):
            with self.subTest(bad=bad), self.assertRaises(spec_checkpoint.SpecCheckpointError):
                spec_checkpoint.validate_source(bad)

    def test_source_with_control_character_is_rejected(self):
        with self.assertRaises(spec_checkpoint.SpecCheckpointError):
            spec_checkpoint.validate_source("https://x.com/\x01a")

    def test_source_without_hostname_is_rejected(self):
        with self.assertRaises(spec_checkpoint.SpecCheckpointError):
            spec_checkpoint.validate_source("https://")

    def test_source_with_credentials_is_rejected(self):
        with self.assertRaises(spec_checkpoint.SpecCheckpointError):
            spec_checkpoint.validate_source("https://user@github.com/owner/repo")
        with self.assertRaises(spec_checkpoint.SpecCheckpointError):
            spec_checkpoint.validate_source("https://user:pass@github.com/owner/repo")

    def test_source_with_invalid_port_is_rejected(self):
        with self.assertRaises(spec_checkpoint.SpecCheckpointError):
            spec_checkpoint.validate_source("https://github.com:notaport/owner/repo")


class CliTests(unittest.TestCase):
    """End-to-end via subprocess: exit codes and exact output formats."""

    BODY = "<!-- spec:start -->\nOutcome: ship it\n<!-- spec:end -->\n"

    def digest(self):
        return spec_checkpoint.spec_hash(self.BODY)

    def test_no_options_prints_hash_and_exits_zero(self):
        result = run(["-"], input_bytes=self.BODY.encode())
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.decode().strip(), self.digest())

    def test_reads_from_a_real_file_path(self, ):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as handle:
            handle.write(self.BODY)
            path = handle.name
        try:
            result = run([path])
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout.decode().strip(), self.digest())
        finally:
            Path(path).unlink()

    def test_check_matching_hash_exits_zero(self):
        result = run(["-", "--check", self.digest()], input_bytes=self.BODY.encode())
        self.assertEqual(result.returncode, 0)

    def test_check_mismatched_hash_exits_one_with_stderr_message(self):
        wrong = "0" * 64
        result = run(["-", "--check", wrong], input_bytes=self.BODY.encode())
        self.assertEqual(result.returncode, 1)
        self.assertIn(("ERROR: Spec hash mismatch (actual %s)" % self.digest()), result.stderr.decode())

    def test_check_value_not_matching_sha256_shape_is_an_error(self):
        result = run(["-", "--check", "not-a-hash"], input_bytes=self.BODY.encode())
        self.assertEqual(result.returncode, 2)
        self.assertTrue(result.stderr.decode().startswith("ERROR: "))

    def test_checkpoint_prints_exact_single_line_format(self):
        result = run(["-", "--checkpoint", "--issue", "42",
                      "--source", "https://github.com/o/r/issues/42"], input_bytes=self.BODY.encode())
        self.assertEqual(result.returncode, 0)
        expected = "SPEC_ACCEPTED issue=42 spec_sha256=%s source=https://github.com/o/r/issues/42\n" % self.digest()
        self.assertEqual(result.stdout.decode(), expected)

    def test_checkpoint_without_issue_is_an_error(self):
        result = run(["-", "--checkpoint", "--source", "https://github.com/o/r/issues/1"],
                    input_bytes=self.BODY.encode())
        self.assertEqual(result.returncode, 2)

    def test_checkpoint_with_non_positive_issue_is_an_error(self):
        result = run(["-", "--checkpoint", "--issue", "0",
                      "--source", "https://github.com/o/r/issues/1"], input_bytes=self.BODY.encode())
        self.assertEqual(result.returncode, 2)

    def test_checkpoint_without_source_is_an_error(self):
        result = run(["-", "--checkpoint", "--issue", "1"], input_bytes=self.BODY.encode())
        self.assertEqual(result.returncode, 2)

    def test_checkpoint_with_invalid_source_is_an_error(self):
        result = run(["-", "--checkpoint", "--issue", "1", "--source", "not-a-url"],
                    input_bytes=self.BODY.encode())
        self.assertEqual(result.returncode, 2)

    def test_missing_file_is_an_error_exit_two(self):
        result = run(["/nonexistent/path/does-not-exist.md"])
        self.assertEqual(result.returncode, 2)
        self.assertTrue(result.stderr.decode().startswith("ERROR: "))

    def test_missing_or_malformed_input_is_exit_two(self):
        result = run(["-"], input_bytes=b"no markers here")
        self.assertEqual(result.returncode, 2)
        self.assertTrue(result.stderr.decode().startswith("ERROR: "))

    def test_self_test_flag_prints_confirmation_and_exits_zero(self):
        result = run(["--self-test"])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.decode(), "Spec checkpoint self-test passed.\n")


if __name__ == "__main__":
    unittest.main()
