#!/usr/bin/env python3
"""Deterministic structural/accessibility validator for editorial-machine pages.

Enforces the closing rule of docs/superpowers/specs/2026-08-27-editorial-machine-design.md
§"Quality contract": "Validator rejects missing title, description, main, h1, install
snippet, reduced-motion handling, skip link, or horizontal-overflow guards."

This is necessary, not sufficient — see editorial-machine/references/composition-system.md
§9 ("Passing the validator is necessary, not sufficient — browser QA is the real gate").

Structural checks (title / description / main / h1) are done with `html.parser.HTMLParser`.
The remaining checks (skip link / install snippet / reduced-motion / overflow guard) are
plain text/CSS regex checks against the raw source, per the Task 2 brief.
"""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

# --- Structural scan ---------------------------------------------------------


class _PageParser(HTMLParser):
    """Single-pass, order-preserving structural scan.

    Deliberately tolerant of malformed/unbalanced markup (typical of hand-authored
    landing pages) — it never requires balanced nesting to extract the facts below.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_text = ""
        self.meta_description: str | None = None  # None = tag absent
        self.main_count = 0
        self.h1_count = 0
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._observe(tag, dict(attrs))

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self._observe(tag, dict(attrs))

    def _observe(self, tag: str, attrs: dict[str, str | None]) -> None:
        if tag == "title":
            self._in_title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "main":
            self.main_count += 1
        elif tag == "meta" and (attrs.get("name") or "").lower() == "description":
            self.meta_description = attrs.get("content") or ""

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_text += data


# --- Text/CSS regex checks ----------------------------------------------------

# An anchor with a same-page href whose visible text names it as a skip link.
# composition-system.md §9.4: "A skip link as the first focusable element, visible
# on focus." A full first-focusable-element proof needs a live DOM/tab-order check
# (browser QA, Task 5); this is the deterministic subset.
_SKIP_LINK_RE = re.compile(
    r"""<a\b[^>]*href=["']#[^"']*["'][^>]*>[^<]*\bskip\b""",
    re.IGNORECASE,
)

# A code/pre/kbd surface whose content opens with a "$ " shell-prompt command —
# composition-system.md §5 "Copyable command": "Mono surface, `$` prefix, copy
# button, real command."
_INSTALL_SNIPPET_RE = re.compile(
    r"<(?:code|pre|kbd)\b[^>]*>\s*\$\s+\S",
    re.IGNORECASE,
)

# composition-system.md §8: "`prefers-reduced-motion: reduce` MUST disable all
# non-essential animation."
_REDUCED_MOTION_RE = re.compile(
    r"@media[^{]*prefers-reduced-motion\s*:\s*reduce",
    re.IGNORECASE,
)

# composition-system.md §7: "No horizontal scroll on <body> at either width. Guard
# it: ... the fix is max-width:100%, min-width:0 on flex/grid children, and
# overflow-x:auto scoped to the wide element."
_OVERFLOW_GUARD_RE = re.compile(
    r"overflow-x\s*:\s*(?:hidden|auto|scroll)|max-width\s*:\s*100%",
    re.IGNORECASE,
)


def validate_file(path: Path) -> list[str]:
    """Validate one HTML page. Returns a list of human-readable issue strings —
    empty means the deterministic checks pass. Order is stable (title, description,
    main, h1, skip link, install snippet, reduced-motion, overflow guard)."""

    source = Path(path).read_text(encoding="utf-8")

    parser = _PageParser()
    parser.feed(source)

    issues: list[str] = []

    if not parser.title_text.strip():
        issues.append("missing or empty <title>")

    if parser.meta_description is None or not parser.meta_description.strip():
        issues.append('missing or empty <meta name="description" content="...">')

    if parser.main_count == 0:
        issues.append("missing <main> landmark")

    if parser.h1_count != 1:
        issues.append(f"exactly one <h1> is required, found {parser.h1_count}")

    if not _SKIP_LINK_RE.search(source):
        issues.append(
            'missing skip link (an <a href="#..."> whose text names it as a '
            '"skip" link, visible on focus)'
        )

    if not _INSTALL_SNIPPET_RE.search(source):
        issues.append(
            "missing install snippet (a <code>/<pre>/<kbd> block beginning with "
            'a "$ " command)'
        )

    if not _REDUCED_MOTION_RE.search(source):
        issues.append(
            "missing prefers-reduced-motion handling "
            "(@media (prefers-reduced-motion: reduce) rule)"
        )

    if not _OVERFLOW_GUARD_RE.search(source):
        issues.append(
            "missing horizontal-overflow guard (overflow-x: hidden/auto/scroll "
            "or max-width: 100% rule)"
        )

    return issues


# --- CLI -----------------------------------------------------------------------


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: validate.py <page.html> [<page.html> ...]", file=sys.stderr)
        return 2

    exit_code = 0
    for arg in argv:
        path = Path(arg)
        issues = validate_file(path)
        if issues:
            exit_code = 1
            print(f"{path}: {len(issues)} issue(s)")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"{path}: OK")

    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
