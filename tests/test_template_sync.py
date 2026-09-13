"""The distributed template must not drift from what this repository itself runs.

This repository is its own first Corp: the files under `.agents/` and `docs/corp/` are
both the product and the copy in use here. Keeping the two in step had been a manual
step, and a manual step held only by whoever remembers it will eventually be skipped —
which is the same class of failure the mechanism layer exists to remove.

Two files differ on purpose, for different reasons. The entry carries installer
placeholders the template substitutes. The Owner card is project-owned: the template
ships a starting point telling a new project how to write its own, while this repository
ships the card it actually uses. Neither divergence may quietly widen, so each is
asserted against what makes it legitimate.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "skills/cybercorp/assets/corp"

# Substituted at install time: the template holds `{{TOKEN}}`, this repository holds values.
SUBSTITUTED_FILES = {"docs/corp/README.md"}

# Project-owned: the template ships guidance for writing your own, this repository ships
# the one it uses. Contents legitimately differ; the section structure may not.
PROJECT_OWNED_FILES = {"docs/corp/owner-communication.md"}

EXEMPT_FILES = SUBSTITUTED_FILES | PROJECT_OWNED_FILES

PLACEHOLDER = re.compile(r"\{\{[A-Z_]+\}\}")


class TemplateSyncTests(unittest.TestCase):
    def test_every_template_file_exists_in_this_repository(self):
        missing = [
            path.relative_to(TEMPLATE).as_posix()
            for path in sorted(TEMPLATE.rglob("*"))
            if path.is_file() and not (ROOT / path.relative_to(TEMPLATE)).exists()
        ]
        self.assertEqual(missing, [], "template files with no counterpart in this repository")

    def test_shared_files_are_byte_identical(self):
        differing = []
        for path in sorted(TEMPLATE.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(TEMPLATE).as_posix()
            if relative in EXEMPT_FILES:
                continue
            live = ROOT / relative
            if live.exists() and live.read_bytes() != path.read_bytes():
                differing.append(relative)
        self.assertEqual(
            differing, [],
            "template drifted from this repository; copy the repository version into "
            "skills/cybercorp/assets/corp/ or state why the two must differ",
        )

    def test_substituted_files_carry_tokens_only_in_the_template(self):
        for relative in sorted(SUBSTITUTED_FILES):
            template_text = (TEMPLATE / relative).read_text(encoding="utf-8")
            live_text = (ROOT / relative).read_text(encoding="utf-8")
            with self.subTest(file=relative):
                self.assertTrue(
                    PLACEHOLDER.search(template_text),
                    "listed as substituted but carries no {{TOKEN}}; if it no longer needs "
                    "one, move it out of SUBSTITUTED_FILES so drift is caught again",
                )
                self.assertFalse(
                    PLACEHOLDER.search(live_text),
                    "this repository's own copy still contains an unsubstituted placeholder",
                )

    def test_project_owned_files_are_present_on_both_sides(self):
        """The template must ship a starting point, and this repository its own version."""
        for relative in sorted(PROJECT_OWNED_FILES):
            with self.subTest(file=relative):
                for base, label in ((TEMPLATE, "template"), (ROOT, "repository")):
                    text = (base / relative).read_text(encoding="utf-8").strip()
                    self.assertTrue(text, "%s copy is empty" % label)

    def test_headings_match_where_wording_legitimately_differs(self):
        """Structure must not diverge even where the text does."""
        for relative in sorted(EXEMPT_FILES):
            headings = []
            for base in (ROOT, TEMPLATE):
                text = (base / relative).read_text(encoding="utf-8")
                headings.append(re.findall(r"^#{1,3} .*$", text, flags=re.M))
            with self.subTest(file=relative):
                self.assertEqual(
                    headings[0], headings[1],
                    "the entry and its template must expose the same sections, so a reader "
                    "of either can be routed the same way",
                )


if __name__ == "__main__":
    unittest.main()
