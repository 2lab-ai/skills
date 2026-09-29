"""Contract tests for the mono-instrument theme.

Run: python3 -m unittest discover -s mono-instrument/tests -v

The theme's one non-negotiable is that design decisions come from measured public
reactions, not from the author's taste. These tests make that mechanical:

- every rule in composition-system.md cites at least one ledger row id,
- every cited id exists in reaction-ledger.md (no phantom evidence),
- every ledger row carries a link and a numeric reaction signal,
- the ledger states its capture date and its method, so staleness is checkable.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
LEDGER = ROOT / "references" / "reaction-ledger.md"
COMPOSITION = ROOT / "references" / "composition-system.md"

# Ledger row ids look like A5, H12, R3, B7, T4, S9 (source family letter + number).
ROW_ID = re.compile(r"\b([AHRBTS]\d{1,3})\b")
# A rule line in composition-system.md: "- **MUST** ..." / "- **SHOULD** ..." / "- **NEVER** ...".
RULE = re.compile(r"^\s*-\s+\*\*(MUST|SHOULD|NEVER|MAY)\*\*(.*)$")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def ledger_rows() -> dict[str, str]:
    """Map row id -> the full table row, for rows whose first cell is an id."""
    rows: dict[str, str] = {}
    for line in read(LEDGER).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 4 and re.fullmatch(r"[AHRBTS]\d{1,3}", cells[0]):
            rows[cells[0]] = line
    return rows


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

    def test_every_ledger_row_has_a_link_and_a_number(self):
        for row_id, line in ledger_rows().items():
            with self.subTest(row=row_id):
                self.assertRegex(line, r"https?://", f"{row_id} has no link")
                self.assertRegex(line, r"\d", f"{row_id} carries no numeric signal")


class CompositionTests(unittest.TestCase):
    def test_composition_has_rules(self):
        rules = [l for l in read(COMPOSITION).splitlines() if RULE.match(l)]
        self.assertGreaterEqual(len(rules), 10, "composition-system.md has too few rules")

    def test_every_rule_cites_a_ledger_row(self):
        for line in read(COMPOSITION).splitlines():
            if not RULE.match(line):
                continue
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


class SkillTests(unittest.TestCase):
    def test_skill_points_generic_requests_back_to_the_router(self):
        text = read(SKILL)
        self.assertIn("landing-page", text)
        self.assertRegex(text, r"(?i)generic .*landing-page, not here")

    def test_skill_forbids_decisions_without_ledger_rows(self):
        self.assertRegex(read(SKILL), r"(?i)no decision without a ledger row")


if __name__ == "__main__":
    unittest.main()
