#!/usr/bin/env python3
"""Deterministic structural/accessibility validator for editorial-machine pages.

Enforces the quality-contract line at
docs/superpowers/specs/2026-08-27-editorial-machine-design.md:69 — the validator rejects a
missing title, description, main, h1, install snippet, reduced-motion handling, skip link,
or horizontal-overflow guard — plus one reduced-motion trap check (see below).

Passing it is necessary, not sufficient; browser QA is the real gate
(editorial-machine/references/composition-system.md:274-275).

Structural checks (title / description / main / h1) are done with `html.parser.HTMLParser`.
The remaining checks (skip link / install snippet / reduced-motion / overflow guard) are
plain text/CSS regex checks against the raw source, per the Task 2 brief. The reduced-motion
trap check parses the stylesheet's block structure, because it has to compare declarations
inside and outside the `prefers-reduced-motion` block.
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


# --- Reduced-motion trap check -------------------------------------------------
#
# composition-system.md:246-248: reduced motion "MUST disable all non-essential
# animation ... while the page stays fully legible and every state stays reachable."
# Killing the animation is only half of it: a reveal that is authored as
# `opacity: 0` + an animation/transition to `opacity: 1` becomes permanently
# invisible once the animation is switched off, so the reduced-motion block has to
# restore the visible state too. That failure is invisible to every other check
# here — the page validates, and renders blank for the reader who asked for less
# motion.

_STYLE_BLOCK_RE = re.compile(r"<style\b[^>]*>(.*?)</style>", re.IGNORECASE | re.DOTALL)
_CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)

_NESTING_AT_RULES = {"@media", "@supports", "@layer", "@container", "@scope"}

_DECL_OPACITY_ZERO_RE = re.compile(
    r"(?:^|[;{])\s*opacity\s*:\s*0(?:\.0+)?\s*(?:!important)?\s*(?:;|$)",
    re.IGNORECASE,
)
_DECL_OPACITY_OTHER_RE = re.compile(
    r"(?:^|[;{])\s*opacity\s*:\s*(?!0(?:\.0+)?\s*(?:!important)?\s*(?:;|$))[^;]+",
    re.IGNORECASE,
)
_DECL_MOTION_RE = re.compile(
    r"(?:^|[;{])\s*(?:animation|transition)(?:-[a-z-]+)?\s*:",
    re.IGNORECASE,
)
_PSEUDO_RE = re.compile(r"::?[a-z-]+(?:\([^)]*\))?", re.IGNORECASE)


def _iter_css_rules(
    css: str, in_reduced: bool = False
) -> "list[tuple[str, str, bool]]":
    """Flatten a stylesheet into `(selector, declarations, inside_reduced_motion)`.

    Brace-matched rather than regexed so that nested at-rules keep their context.
    `@keyframes` bodies are skipped: their `from`/`to` blocks are not style rules.
    """

    rules: list[tuple[str, str, bool]] = []
    index = 0
    length = len(css)

    while index < length:
        open_brace = css.find("{", index)
        if open_brace == -1:
            break

        prelude = css[index:open_brace].strip()

        depth = 1
        cursor = open_brace + 1
        while cursor < length and depth:
            char = css[cursor]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
            cursor += 1
        body = css[open_brace + 1 : cursor - 1]

        if prelude.startswith("@"):
            at_name = prelude.split(None, 1)[0].lower()
            if at_name in _NESTING_AT_RULES:
                reduced = in_reduced or bool(_REDUCED_MOTION_RE.search(prelude))
                rules.extend(_iter_css_rules(body, reduced))
            # @keyframes / @font-face / @import: no style rules to collect.
        elif prelude:
            rules.append((prelude, body, in_reduced))

        index = cursor

    return rules


def _selector_keys(selector_list: str) -> set[str]:
    """Rightmost compound selector of each selector in a list, pseudo-parts removed.

    `.js [data-reveal]:hover` → `[data-reveal]`, so a restoration rule written
    against the element itself still matches a scoped hidden state.
    """

    keys: set[str] = set()
    for selector in selector_list.split(","):
        cleaned = selector.replace(">", " ").replace("+", " ").replace("~", " ")
        parts = cleaned.split()
        if not parts:
            continue
        key = _PSEUDO_RE.sub("", parts[-1]).strip()
        if key:
            keys.add(key)
    return keys


def _reduced_motion_trap_issues(source: str) -> list[str]:
    css = "\n".join(_STYLE_BLOCK_RE.findall(source))
    if not css:
        return []
    css = _CSS_COMMENT_RE.sub(" ", css)

    rules = _iter_css_rules(css)
    if not any(in_reduced for _, _, in_reduced in rules):
        return []  # absence of the block is reported by the earlier check

    motion_is_disabled = any(
        in_reduced and _DECL_MOTION_RE.search(decls) and "none" in decls.lower()
        for _, decls, in_reduced in rules
    )
    if not motion_is_disabled:
        return []

    restored_keys: set[str] = set()
    for selector, decls, in_reduced in rules:
        if in_reduced and _DECL_OPACITY_OTHER_RE.search(decls):
            restored_keys |= _selector_keys(selector)

    issues: list[str] = []
    seen: set[str] = set()
    for selector, decls, in_reduced in rules:
        if in_reduced:
            continue
        if not _DECL_OPACITY_ZERO_RE.search(decls):
            continue
        if not _DECL_MOTION_RE.search(decls):
            continue  # hidden for some other reason; not an animation reveal
        keys = _selector_keys(selector)
        if "*" in restored_keys or (keys & restored_keys):
            continue
        name = selector.strip()
        if name in seen:
            continue
        seen.add(name)
        issues.append(
            f'reduced-motion trap: "{name}" is hidden by default (opacity: 0) and '
            "revealed by animation/transition, but the prefers-reduced-motion "
            "block disables motion without restoring its opacity — the content "
            "stays invisible"
        )

    return issues


def validate_file(path: Path) -> list[str]:
    """Validate one HTML page. Returns a list of human-readable issue strings —
    empty means the deterministic checks pass. Order is stable (title, description,
    main, h1, skip link, install snippet, reduced-motion, overflow guard,
    reduced-motion traps)."""

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

    issues.extend(_reduced_motion_trap_issues(source))

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
