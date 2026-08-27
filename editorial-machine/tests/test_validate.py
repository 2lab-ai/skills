"""Tests for editorial-machine's deterministic HTML validator.

Run: python3 -m unittest editorial-machine/tests/test_validate.py -v

Fixtures are built in-memory (no tracked fixture files) and written to temp files
because `validate_file` reads from a filesystem path, per the Task 2 interface.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from validate import validate_file  # noqa: E402

# A page missing every required category: title, meta description, main, h1,
# skip link, install snippet, reduced-motion handling, overflow guard.
INVALID_HTML = """<!doctype html>
<html>
<body>
<p>No title, no meta description, no main, no h1, no skip link,
no install snippet, no reduced-motion handling, no overflow guard.</p>
</body>
</html>
"""

# A page that satisfies every required category exactly once.
VALID_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Editorial Machine — fixture page</title>
<meta name="description" content="A minimal fixture that satisfies every validate.py requirement.">
<style>
@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition: none !important; }
}
.command { overflow-x: auto; max-width: 100%; }
</style>
</head>
<body>
<a class="skip-link" href="#main">Skip to main content</a>
<header><a href="/">editorial-machine</a></header>
<main id="main">
  <h1>The harness is capital</h1>
  <section aria-labelledby="install-heading">
    <h2 id="install-heading">Install</h2>
    <pre class="command"><code>$ curl -fsSL https://example.com/install.sh | sh</code></pre>
  </section>
</main>
</body>
</html>
"""


# A page whose reveal elements are hidden by default (`opacity: 0`) and made
# visible only by an animation, while the reduced-motion block kills the
# animation without restoring the visible state. Under
# `prefers-reduced-motion: reduce` the content never appears.
REVEAL_TRAP_HTML = VALID_HTML.replace(
    ".command { overflow-x: auto; max-width: 100%; }",
    """.command { overflow-x: auto; max-width: 100%; }
.reveal { opacity: 0; animation: fade 600ms ease-out forwards; }
@keyframes fade { from { opacity: 0 } to { opacity: 1 } }""",
).replace("<main id=\"main\">", '<main id="main" class="reveal">')

# The same page, with the reduced-motion block restoring the visible state.
REVEAL_RESTORED_HTML = REVEAL_TRAP_HTML.replace(
    "* { animation: none !important; transition: none !important; }",
    """* { animation: none !important; transition: none !important; }
  .reveal { opacity: 1; transform: none; }""",
)

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"


def _write(content: str) -> Path:
    fd = tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", delete=False, encoding="utf-8"
    )
    fd.write(content)
    fd.close()
    return Path(fd.name)


class ValidateFileTests(unittest.TestCase):
    def _validate(self, content: str) -> list[str]:
        path = _write(content)
        self.addCleanup(path.unlink)
        return validate_file(path)

    def test_minimal_invalid_page_reports_every_required_category(self):
        issues = self._validate(INVALID_HTML)
        joined = "\n".join(issues).lower()
        for keyword in [
            "title",
            "description",
            "main",
            "h1",
            "skip link",
            "install",
            "reduced-motion",
            "overflow",
        ]:
            self.assertIn(
                keyword, joined, f"expected an issue mentioning {keyword!r}: {issues}"
            )
        self.assertGreaterEqual(len(issues), 8, issues)

    def test_valid_fixture_passes_with_zero_issues(self):
        self.assertEqual(self._validate(VALID_HTML), [])

    def test_missing_title_is_flagged_alone(self):
        html = re.sub(r"<title>.*?</title>\n?", "", VALID_HTML)
        issues = self._validate(html)
        self.assertEqual(len(issues), 1, issues)
        self.assertIn("title", issues[0].lower())

    def test_missing_meta_description_is_flagged_alone(self):
        html = re.sub(r'<meta name="description"[^>]*>\n?', "", VALID_HTML)
        issues = self._validate(html)
        self.assertEqual(len(issues), 1, issues)
        self.assertIn("description", issues[0].lower())

    def test_missing_main_landmark_is_flagged_alone(self):
        html = re.sub(r"<main[^>]*>", "", VALID_HTML)
        html = html.replace("</main>", "")
        issues = self._validate(html)
        self.assertEqual(len(issues), 1, issues)
        self.assertIn("main", issues[0].lower())

    def test_missing_h1_is_flagged_alone(self):
        html = re.sub(r"<h1>.*?</h1>\n?", "", VALID_HTML)
        issues = self._validate(html)
        self.assertEqual(len(issues), 1, issues)
        self.assertIn("h1", issues[0].lower())

    def test_extra_h1_is_flagged_alone(self):
        html = VALID_HTML.replace(
            "<h1>The harness is capital</h1>",
            "<h1>The harness is capital</h1><h1>A second hero</h1>",
        )
        issues = self._validate(html)
        self.assertEqual(len(issues), 1, issues)
        self.assertIn("h1", issues[0].lower())

    def test_missing_skip_link_is_flagged_alone(self):
        html = re.sub(r'<a class="skip-link"[^>]*>.*?</a>\n?', "", VALID_HTML)
        issues = self._validate(html)
        self.assertEqual(len(issues), 1, issues)
        self.assertIn("skip link", issues[0].lower())

    def test_missing_install_snippet_is_flagged_alone(self):
        html = re.sub(
            r'<pre class="command">.*?</pre>\n?', "", VALID_HTML, flags=re.S
        )
        issues = self._validate(html)
        self.assertEqual(len(issues), 1, issues)
        self.assertIn("install", issues[0].lower())

    def test_missing_reduced_motion_handling_is_flagged_alone(self):
        html = re.sub(
            r"@media \(prefers-reduced-motion: reduce\) \{.*?\}\n?",
            "",
            VALID_HTML,
            flags=re.S,
        )
        issues = self._validate(html)
        self.assertEqual(len(issues), 1, issues)
        self.assertIn("reduced-motion", issues[0].lower())

    def test_missing_overflow_guard_is_flagged_alone(self):
        html = VALID_HTML.replace(
            ".command { overflow-x: auto; max-width: 100%; }", ".command {}"
        )
        issues = self._validate(html)
        self.assertEqual(len(issues), 1, issues)
        self.assertIn("overflow", issues[0].lower())

    def test_reduced_motion_that_hides_content_is_flagged_alone(self):
        issues = self._validate(REVEAL_TRAP_HTML)
        self.assertEqual(len(issues), 1, issues)
        joined = issues[0].lower()
        self.assertIn("reduced-motion", joined)
        self.assertIn("opacity", joined)
        self.assertIn(".reveal", issues[0])

    def test_reduced_motion_that_restores_visible_state_passes(self):
        self.assertEqual(self._validate(REVEAL_RESTORED_HTML), [])

    def test_shipped_example_pages_pass(self):
        for name in ("llmux.html", "xfx.html"):
            page = EXAMPLES_DIR / name
            with self.subTest(page=name):
                self.assertTrue(page.is_file(), f"missing example page: {page}")
                self.assertEqual(validate_file(page), [])

    def test_cli_exits_nonzero_on_issues_and_zero_when_clean(self):
        invalid_path = _write(INVALID_HTML)
        self.addCleanup(invalid_path.unlink)
        valid_path = _write(VALID_HTML)
        self.addCleanup(valid_path.unlink)

        validate_script = SCRIPTS_DIR / "validate.py"

        result = subprocess.run(
            [sys.executable, str(validate_script), str(invalid_path)],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

        result = subprocess.run(
            [sys.executable, str(validate_script), str(valid_path)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
