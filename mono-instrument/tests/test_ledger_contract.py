"""Contract tests for the mono-instrument theme.

Run: python3 -m unittest discover -s mono-instrument/tests -v

The theme's rules must come from ledger rows, not from the author's taste. These tests check
the plumbing of that promise:

- the ledger states its capture date and its method, so staleness is checkable;
- ledger rows exist, from several source families, and every row links its source with a
  well-formed https URL in its link cell (a host with a dot, no whitespace; syntax only,
  nothing is fetched);
- every reaction row (A, H, R, B, and S rows tagged as a measurement) carries a number (at
  least one digit) in its signal cell, or the Method's `unverified` marker;
- fact rows (T, and S rows tagged [STD], [GUIDE] or [QUAL]) are exempt from the number and rest
  on their primary link; every S row carries one of the known class tags;
- every rule in composition-system.md cites at least one row, every cited row exists, and no
  rule rests only on rows that are `unverified` or break the row contract;
- SKILL.md ships no decision without a ledger row and offers no escape clause for one.

Passing means the citations resolve; it does not certify that a cited row supports its rule.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
LEDGER = ROOT / "references" / "reaction-ledger.md"
COMPOSITION = ROOT / "references" / "composition-system.md"

# Ledger row ids look like A5, H12, R3, B7, T4, S9 (source family letter + number).
ROW_ID = re.compile(r"\b([AHRBTS]\d{1,3})\b")
# A rule line in composition-system.md: "- **MUST** ..." / "- **SHOULD** ..." / "- **NEVER** ...".
RULE = re.compile(r"^\s*-\s+\*\*(MUST|SHOULD|NEVER|MAY)\*\*(.*)$")

# Every ledger table has the same six cells: id | source | signal | finding | link | date.
ID, SOURCE, SIGNAL, FINDING, LINK, DATE = range(6)
# Families whose every row records a measured reaction: awards, HN, Reddit, benchmark sites.
REACTION_FAMILIES = set("AHRB")
# S rows end their source cell with a class tag, e.g. "Mansfield, Legge & Bane [LAB]".
S_TAG = re.compile(r"\[([A-Z]+)\]$")
MEASURED_S_TAGS = {"LAB", "ONLINE", "OBS", "REP", "CRAWL", "POLL"}
FACT_S_TAGS = {"STD", "GUIDE", "QUAL"}
# The Method's marker for a figure the research could not see on a loaded page.
UNVERIFIED = "unverified"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def split_cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def ledger_rows() -> dict[str, list[str]]:
    """Map row id -> the row's cells, for table rows whose first cell is an id."""
    rows: dict[str, list[str]] = {}
    for line in read(LEDGER).splitlines():
        cells = split_cells(line)
        if re.fullmatch(r"[AHRBTS]\d{1,3}", cells[0]):
            rows[cells[0]] = cells
    return rows


def rule_lines() -> list[str]:
    return [line for line in read(COMPOSITION).splitlines() if RULE.match(line)]


def link_problem(link: str) -> str | None:
    """Why a link cell is not a usable https URL, or None if it is. Syntax only: nothing is fetched."""
    if not link or re.search(r"\s", link):
        return f"link cell {link!r} is empty or contains whitespace"
    try:
        parts = urlsplit(link)
        host = parts.hostname or ""
        parts.port  # urlsplit checks the port only when it is read: non-integer or >65535 raises
    except ValueError:
        return f"link cell {link!r} does not parse as a URL"
    if parts.scheme != "https":
        return f"link cell {link!r} is not an https URL"
    # A host with a dot between non-empty labels, e.g. news.ycombinator.com; not localhost.
    if not re.fullmatch(r"[^.]+(?:\.[^.]+)+", host):
        return f"link cell {link!r} names no host with a dot"
    return None


def row_problems(cells: list[str]) -> list[str]:
    """What keeps one ledger row from meeting the contract; an empty list means it meets it.

    Only the signal cell counts as the number: digits in the id, finding, link or date
    do not measure the reaction.
    """
    if len(cells) != 6:
        return [f"has {len(cells)} cells; expected id | source | signal | finding | link | date"]
    problems = []
    bad_link = link_problem(cells[LINK])
    if bad_link:
        problems.append(bad_link)
    family = cells[ID][0]
    if family == "S":
        tag = S_TAG.search(cells[SOURCE])
        known = MEASURED_S_TAGS | FACT_S_TAGS
        if tag is None or tag.group(1) not in known:
            problems.append(f"S row source cell must end with a class tag, one of {sorted(known)}")
            return problems
        measured = tag.group(1) in MEASURED_S_TAGS
    else:
        measured = family in REACTION_FAMILIES
    signal = cells[SIGNAL]
    if measured and signal != UNVERIFIED and not re.search(r"\d", signal):
        problems.append(f"signal cell {signal!r} has no number and is not {UNVERIFIED!r}")
    return problems


def verified_citations(rule_line: str, rows: dict[str, list[str]]) -> list[str]:
    """Row ids a rule cites that exist, meet the row contract and are not marked `unverified`."""
    return [
        r
        for r in ROW_ID.findall(rule_line)
        if r in rows and rows[r][SIGNAL] != UNVERIFIED and not row_problems(rows[r])
    ]


class LedgerTests(unittest.TestCase):
    def test_ledger_declares_capture_date_and_method(self):
        text = read(LEDGER)
        self.assertRegex(text, r"[Cc]aptured[^\n]*20\d\d-\d\d-\d\d")
        self.assertRegex(text, r"(?m)^#+\s+Method")

    def test_ledger_has_rows_from_several_source_families(self):
        families = {row_id[0] for row_id in ledger_rows()}
        self.assertGreaterEqual(
            len(families), 4, f"ledger draws on too few source families: {sorted(families)}"
        )

    def test_every_ledger_row_meets_the_row_contract(self):
        rows = ledger_rows()
        self.assertTrue(rows, "the ledger has no rows")
        for row_id, cells in rows.items():
            with self.subTest(row=row_id):
                self.assertEqual(row_problems(cells), [])


class RowContractTests(unittest.TestCase):
    """row_problems() on synthetic rows, so the checker is shown to reject bad rows."""

    def problems(self, line: str) -> list[str]:
        return row_problems(split_cells(line))

    def test_reaction_row_without_a_number_in_its_signal_cell_fails(self):
        # Digits sit in the id, the finding, the URL and the date; none in the signal cell.
        line = "| H99 | a thread | many / lots | top 12: 9 critical | https://news.ycombinator.com/item?id=12345 | 2026-09-29 |"
        self.assertTrue(self.problems(line))

    def test_measured_s_row_without_a_number_in_its_signal_cell_fails(self):
        line = "| S99 | a lab study [LAB] | several | read 5% faster | https://doi.org/10.1145/12345 | 2014 |"
        self.assertTrue(self.problems(line))

    def test_std_row_without_a_link_fails(self):
        for line in (
            "| S98 | a web standard [STD] | p75 real users | CLS ≤0.1 | see web.dev | current |",
            # A URL in the finding cell is not the row's link.
            "| S98 | a web standard [STD] | p75 real users | CLS ≤0.1 per https://web.dev | see above | current |",
        ):
            with self.subTest(line=line):
                self.assertTrue(self.problems(line))

    def test_t_row_without_a_link_fails(self):
        for line in (
            "| T99 | a framework feature | stable | no layout shift | nextjs.org docs | current |",
            "| T99 | a framework feature | stable | no shift, https://nextjs.org/docs | see above | current |",
        ):
            with self.subTest(line=line):
                self.assertTrue(self.problems(line))

    def test_s_row_without_a_known_class_tag_fails(self):
        for line in (
            "| S97 | a review of studies | 12 studies | light mode reads better | https://example.org/r | 2020 |",
            "| S96 | a blog post [BLOG] | 1,200 readers | 60% agree | https://example.org/b | 2026 |",
        ):
            with self.subTest(line=line):
                self.assertTrue(self.problems(line))

    def test_well_formed_rows_pass(self):
        for line in (
            "| H98 | a thread | 381 / 241 | top 16: 8 agree | https://news.ycombinator.com/item?id=1 | 2026-09-27 |",
            "| S95 | a web standard [STD] | — | CLS ≤0.1 | https://web.dev/articles/x | current |",
            "| T98 | a framework feature | stable | no external request | https://nextjs.org/docs/x | current |",
            "| S94 | a lab study [LAB] | unverified | appeal judged within 50 ms | https://doi.org/10.1/x | 2006 |",
        ):
            with self.subTest(line=line):
                self.assertEqual(self.problems(line), [])

    def test_rule_resting_on_unverified_rows_alone_has_no_verified_citation(self):
        rows = {
            "S94": split_cells("| S94 | a lab study [LAB] | unverified | x | https://doi.org/10.1/x | 2006 |"),
            "H98": split_cells("| H98 | a thread | 381 / 241 | x | https://news.ycombinator.com/item?id=1 | 2026 |"),
        }
        self.assertEqual(verified_citations("- **MUST** x. Rows: S94.", rows), [])
        self.assertEqual(verified_citations("- **MUST** x. Rows: S94, H98.", rows), ["H98"])

    def test_row_with_an_unusable_https_link_fails(self):
        # Each starts with "https://" yet is unusable: no host, a space, no dot in the host, or a
        # port that is not an integer in 0-65535.
        for link in (
            "https://",
            "https:// example.com",
            "https://localhost/docs",
            "https://example.com:invalid",
            "https://example.com:99999",
        ):
            line = f"| T97 | a framework feature | stable | no external request | {link} | current |"
            with self.subTest(link=link):
                self.assertTrue(self.problems(line))

    def test_rule_citing_only_a_row_with_an_unusable_link_has_no_verified_citation(self):
        for link in ("https://", "https://example.com:invalid", "https://example.com:99999"):
            rows = {"T97": split_cells(f"| T97 | a framework feature | stable | x | {link} | current |")}
            with self.subTest(link=link):
                self.assertEqual(verified_citations("- **MUST** x. Rows: T97.", rows), [])


class CompositionTests(unittest.TestCase):
    def test_composition_has_rules(self):
        self.assertGreaterEqual(len(rule_lines()), 10, "composition-system.md has too few rules")

    def test_every_rule_cites_a_ledger_row(self):
        for line in rule_lines():
            with self.subTest(rule=line.strip()[:90]):
                self.assertTrue(
                    ROW_ID.search(line),
                    "rule cites no ledger row — a rule without evidence is taste, not a rule",
                )

    def test_every_cited_row_exists_in_the_ledger(self):
        known = set(ledger_rows())
        cited = set(ROW_ID.findall(read(COMPOSITION)))
        missing = sorted(cited - known)
        self.assertEqual(missing, [], f"composition cites rows the ledger does not have: {missing}")

    def test_no_rule_rests_on_unverified_rows_alone(self):
        rows = ledger_rows()
        for line in rule_lines():
            with self.subTest(rule=line.strip()[:90]):
                self.assertTrue(
                    verified_citations(line, rows),
                    "rule cites only rows marked unverified (or none that exist)",
                )


class SkillTests(unittest.TestCase):
    def test_skill_points_generic_requests_back_to_the_router(self):
        text = read(SKILL)
        self.assertIn("landing-page", text)
        self.assertRegex(text, r"(?i)generic .*landing-page, not here")

    def test_skill_forbids_decisions_without_ledger_rows(self):
        self.assertRegex(read(SKILL), r"(?i)no decision without a ledger row")

    def test_skill_page_brief_has_no_escape_for_row_less_decisions(self):
        text = read(SKILL)
        self.assertIsNone(
            re.search(r"(?i)\bdeviation", text), "SKILL.md lets a row-less decision ship as a deviation"
        )
        self.assertTrue(
            re.search(
                r"(?is)no supporting row does not ship.*research the missing row.*drop\s+the\s+decision",
                text,
            ),
            "SKILL.md must say a row-less decision does not ship: research the row or drop the decision",
        )


if __name__ == "__main__":
    unittest.main()
