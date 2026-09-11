"""Structural contract tests for the `landing-page` entrypoint skill.

Run: python3 -m unittest discover -s landing-page/tests -v

These are documentation-structure tests, not prose tests. Each one checks a
property the router has to hold for a real request to be routable:

- the entrypoint exists and is named,
- every workflow the router advertises resolves to a file on disk (no phantom
  workflow rows),
- the no-theme default resolves to the editorial-machine workflow,
- both delivery lanes (existing app / standalone) are defined, and an
  unreachable live target is reported rather than silently downgraded,
- the standalone-only rules (validator, no-build/no-framework) carry a lane
  qualifier, so the skill no longer contradicts itself inside a real app.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LANDING = ROOT / "landing-page"
SKILL = LANDING / "SKILL.md"
DEFAULT_WORKFLOW = LANDING / "workflows" / "editorial-machine.md"
THEME_SKILL = ROOT / "editorial-machine" / "SKILL.md"
COMPOSITION = ROOT / "editorial-machine" / "references" / "composition-system.md"
SOURCE_ANALYSIS = ROOT / "editorial-machine" / "references" / "source-analysis.md"
RECEIPT = ROOT / "editorial-machine" / "references" / "2026-09-11-measurements.json"
README = ROOT / "README.md"

LINKED_DOCS = [SKILL, DEFAULT_WORKFLOW, THEME_SKILL, README]

_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
_MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
_HEADING_RE = re.compile(r"^#{1,6}\s+(.*)$")
# A claim that forbids a build system outright. Legitimate for a single-file
# page, fatal if applied to a route inside an existing app.
_NO_BUILD_CLAIM_RE = re.compile(r"no framework|no build step|no bundler", re.IGNORECASE)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def frontmatter(path: Path) -> dict[str, str]:
    match = _FRONTMATTER_RE.search(read(path).lstrip("﻿"))
    if not match:
        return {}
    fields: dict[str, str] = {}
    key = None
    for line in match.group(1).splitlines():
        header = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if header:
            key = header.group(1)
            fields[key] = header.group(2).strip().strip('"')
        elif key and line.strip():
            fields[key] += " " + line.strip()
    return fields


def workflow_step(text: str, label: str) -> str:
    """A bolded numbered workflow step (`5. **Gates by lane.** ...`), up to the
    next top-level numbered step."""
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if start is None:
            if re.match(r"^\d+\.\s+\*\*", line) and label.lower() in line.lower():
                start = index
            continue
        if re.match(r"^\d+\.\s+\*\*", line):
            return "\n".join(lines[start:index])
    return "\n".join(lines[start:]) if start is not None else ""


def block(lines: list[str], index: int) -> str:
    """The markdown block containing `lines[index]`: back up to the nearest
    block start (blank line, heading, list item, or table row)."""
    start = index
    while start > 0 and not re.match(
        r"^\s*$|^#{1,6}\s|^\s*(?:[-*+]|\d+\.)\s|^\s*\|", lines[start]
    ):
        start -= 1
    return "\n".join(lines[start : index + 1])


def section(text: str, heading_pattern: str) -> str:
    """Body of the first heading matching `heading_pattern`, up to the next
    heading of the same or higher level."""
    pattern = re.compile(heading_pattern, re.IGNORECASE)
    lines = text.splitlines()
    start = level = None
    for index, line in enumerate(lines):
        match = _HEADING_RE.match(line)
        if not match:
            continue
        if start is None:
            if pattern.search(match.group(1)):
                start = index
                level = len(line) - len(line.lstrip("#"))
            continue
        if len(line) - len(line.lstrip("#")) <= level:
            return "\n".join(lines[start:index])
    return "\n".join(lines[start:]) if start is not None else ""


class EntrypointTests(unittest.TestCase):
    def test_entrypoint_skill_exists_and_is_named_landing_page(self):
        self.assertTrue(SKILL.is_file(), f"missing entrypoint skill: {SKILL}")
        self.assertEqual(frontmatter(SKILL).get("name"), "landing-page")

    def test_generic_landing_request_belongs_to_the_entrypoint(self):
        entry = frontmatter(SKILL).get("description", "").lower()
        self.assertIn("landing page", entry)
        # The theme skill must hand the generic request back to the router
        # instead of claiming it.
        theme = frontmatter(THEME_SKILL).get("description", "")
        self.assertIn("landing-page", theme.lower())

    def test_entrypoint_description_is_when_plus_args_only(self):
        """A description is a dispatch trigger, not a summary of the body.

        The theme skill's description may name the router — "routed here by
        landing-page" is itself a WHEN condition. This rule is about the
        entrypoint restating its own procedure.
        """
        entry = frontmatter(SKILL).get("description", "").lower()
        self.assertRegex(entry, r"\buse when\b")
        for phrase in [
            r"routes? to",
            r"routing",
            r"defaults? to",
            r"defaulting",
            r"workflow",
            r"\bthen\b",
            r"step \d",
        ]:
            with self.subTest(phrase=phrase):
                self.assertNotRegex(
                    entry,
                    phrase,
                    "the description describes its own procedure; keep it to "
                    "WHEN + ARGS and leave the process in the body",
                )

    def test_every_advertised_workflow_file_exists(self):
        advertised = set(re.findall(r"workflows/[A-Za-z0-9._-]+\.md", read(SKILL)))
        self.assertTrue(advertised, "SKILL.md advertises no workflow files")
        for rel in sorted(advertised):
            with self.subTest(workflow=rel):
                self.assertTrue(
                    (LANDING / rel).is_file(),
                    f"phantom workflow row: {rel} is named but not shipped",
                )

    def test_no_theme_named_defaults_to_editorial_machine_workflow(self):
        routing = section(read(SKILL), r"routing")
        self.assertTrue(routing, "SKILL.md has no routing section")
        default_rows = [
            row
            for row in routing.splitlines()
            if row.lstrip().startswith("|")
            and re.search(r"no theme|not name|unspecified|default", row, re.IGNORECASE)
            and "unregistered" not in row.lower()
            and "unknown" not in row.lower()
        ]
        self.assertTrue(default_rows, f"no default routing row found in:\n{routing}")
        self.assertTrue(
            any("workflows/editorial-machine.md" in row for row in default_rows),
            f"default row does not point at the editorial-machine workflow: {default_rows}",
        )
        self.assertTrue(DEFAULT_WORKFLOW.is_file(), f"missing {DEFAULT_WORKFLOW}")

    def test_unknown_theme_is_not_silently_substituted(self):
        routing = section(read(SKILL), r"routing")
        unknown_rows = [
            row
            for row in routing.splitlines()
            if row.lstrip().startswith("|")
            and re.search(r"unregistered|unknown", row, re.IGNORECASE)
        ]
        self.assertTrue(unknown_rows, f"no unregistered-theme row in:\n{routing}")
        joined = " ".join(unknown_rows).lower()
        self.assertRegex(joined, r"stop|ask", f"unknown theme has no stop rule: {joined}")
        self.assertIn("never silently substitute", joined)

    def test_relative_links_resolve(self):
        for doc in LINKED_DOCS:
            text = read(doc)
            for target in _MD_LINK_RE.findall(text):
                if re.match(r"^(?:[a-z]+:|#|//)", target):
                    continue
                resolved = (doc.parent / target.split("#", 1)[0]).resolve()
                with self.subTest(doc=doc.name, link=target):
                    self.assertTrue(
                        resolved.exists(), f"{doc}: broken link -> {target}"
                    )


class TargetContractTests(unittest.TestCase):
    def test_target_contract_names_every_required_field(self):
        contract = section(read(SKILL), r"target contract")
        self.assertTrue(contract, "SKILL.md has no target contract section")
        for field in [
            "site",
            "repo",
            "route",
            "framework",
            "preserved behavior",
            "delivery url",
        ]:
            with self.subTest(field=field):
                self.assertIn(field, contract.lower())

    def test_both_delivery_lanes_are_defined(self):
        lanes = section(read(SKILL), r"lane")
        self.assertTrue(lanes, "SKILL.md has no lane section")
        lowered = lanes.lower()
        self.assertIn("existing app", lowered)
        self.assertIn("standalone", lowered)

    def test_unreachable_live_target_is_reported_not_downgraded(self):
        lanes = section(read(SKILL), r"lane").lower()
        self.assertIn("unreachable live target", lanes)
        unreachable = lanes[lanes.index("unreachable live target") :]
        self.assertRegex(unreachable, r"\breport\b")
        self.assertRegex(
            unreachable,
            r"do not (?:ship|deliver|substitute)",
            "the unreachable-target rule does not forbid a silent standalone substitute",
        )


class LaneScopeTests(unittest.TestCase):
    """The defect this work fixes: standalone-only rules stated as universal."""

    def test_theme_skill_declares_both_lanes(self):
        text = read(THEME_SKILL).lower()
        self.assertIn("existing-app lane", text)
        self.assertIn("standalone lane", text)

    def test_validator_is_scoped_to_the_standalone_lane(self):
        gates = workflow_step(read(THEME_SKILL), "gates")
        self.assertTrue(gates, "theme skill has no per-lane gate step")
        lowered = gates.lower()
        self.assertIn("validate.py", lowered)
        standalone_clause = lowered[: lowered.index("validate.py")]
        self.assertIn(
            "standalone lane",
            standalone_clause,
            "validate.py is introduced without naming the standalone lane",
        )
        self.assertIn("existing-app lane", lowered)

    def test_validator_is_invoked_by_an_absolute_skill_root_path(self):
        """The skill is not installed inside the target repo, so a CWD-relative
        `editorial-machine/scripts/...` only resolves inside the skills checkout."""
        gates = workflow_step(read(THEME_SKILL), "gates")
        self.assertNotRegex(
            gates,
            r"python3\s+editorial-machine/scripts/validate\.py",
            "validator invoked by a repo-relative path that will not resolve "
            "from the target repo",
        )
        self.assertRegex(
            gates,
            r"python3\s+\"\$\{?EM_ROOT\}?/scripts/validate\.py\"",
            "validator is not invoked through an absolutely-resolved skill root",
        )
        self.assertIn("absolute", gates.lower())

    def test_existing_app_lane_keeps_the_app_stack_and_gates(self):
        text = read(THEME_SKILL).lower()
        app_lane = text[text.index("existing-app lane") :]
        self.assertRegex(app_lane, r"the app'?s own|existing stack|repo'?s own")
        self.assertRegex(app_lane, r"gate")

    def test_no_build_claims_carry_a_lane_qualifier(self):
        lane_word = re.compile(r"standalone|existing-app", re.IGNORECASE)
        for doc in (THEME_SKILL, COMPOSITION):
            lines = read(doc).splitlines()
            heading = ""
            for index, line in enumerate(lines):
                match = _HEADING_RE.match(line)
                if match:
                    heading = match.group(1)
                if not _NO_BUILD_CLAIM_RE.search(line):
                    continue
                context = block(lines, index)
                with self.subTest(doc=doc.name, line=line.strip()[:70]):
                    self.assertTrue(
                        lane_word.search(context) or lane_word.search(heading),
                        f"{doc.name}: unscoped no-build claim under heading "
                        f"{heading!r}: {line.strip()}",
                    )

    def test_existing_app_lane_has_its_own_performance_measures(self):
        app_lane = section(read(COMPOSITION), r"existing-app lane")
        self.assertTrue(app_lane, "composition-system.md has no existing-app lane section")
        lowered = app_lane.lower()
        self.assertIn("transferred", lowered)
        self.assertIn("regression", lowered)
        self.assertNotRegex(
            lowered,
            r"≤\s*5\s*kb",
            "the 5 KB inline-JS ceiling cannot apply to a framework route",
        )


class NonDuplicationTests(unittest.TestCase):
    def test_workflow_cites_the_references_instead_of_restating_them(self):
        text = read(DEFAULT_WORKFLOW)
        self.assertIn("composition-system.md", text)
        self.assertIn("source-analysis.md", text)
        # A copy of the rules, rather than a citation of them, shows up as the
        # reference's own table headers being reproduced here.
        self.assertNotIn("| Token | Role |", text)
        self.assertLess(
            len(text.splitlines()),
            len(read(COMPOSITION).splitlines()),
            "the workflow has grown into a second copy of the composition system",
        )


class EvidenceLedgerTests(unittest.TestCase):
    """The ledger and its receipt must agree, and rules must not be dressed as
    observations."""

    def test_dated_receipt_ships_and_covers_every_site_and_viewport(self):
        self.assertTrue(RECEIPT.is_file(), f"missing measurement receipt: {RECEIPT}")
        records = json.loads(read(RECEIPT))
        seen = {(r["host"], r["width"]) for r in records}
        for host in [
            "char.com",
            "anarlog.so",
            "fastrepl.com",
            "agentpub.dev",
            "johnjeong.com",
        ]:
            for width in (1440, 390):
                with self.subTest(host=host, width=width):
                    self.assertIn((host, width), seen)

    def test_ledger_quotes_the_receipt_it_ships(self):
        records = json.loads(read(RECEIPT))
        update = section(read(SOURCE_ANALYSIS), r"2026-09-11")
        self.assertTrue(update, "source-analysis.md has no dated 2026-09-11 section")
        rows = {
            line.split("|")[1].strip().strip("`"): line
            for line in update.splitlines()
            if line.lstrip().startswith("|")
        }
        for record in records:
            row = rows.get(record["host"])
            self.assertIsNotNone(row, f"no ledger row for {record['host']}")
            if record["scrollWidth"] != record["width"]:
                with self.subTest(host=record["host"], fact="overflow"):
                    self.assertIn(str(record["scrollWidth"]), row)
            if record["headings"]:
                with self.subTest(host=record["host"], width=record["width"]):
                    self.assertIn(record["headings"][0]["size"], row)

    def test_history_is_appended_to_not_rewritten(self):
        text = read(SOURCE_ANALYSIS)
        self.assertIn("Captured: 2026-08-27", text)
        self.assertLess(
            text.index("Captured: 2026-08-27"),
            text.index("2026-09-11"),
            "the dated update must come after the original ledger, not replace it",
        )

    def test_no_third_party_renders_are_committed(self):
        strays = [
            p.name
            for p in (ROOT / "editorial-machine" / "references").iterdir()
            if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
        ]
        self.assertEqual(strays, [], f"screenshot binaries committed: {strays}")

    def test_on_screen_motion_is_not_sold_as_proof_of_liveness(self):
        for doc in (SOURCE_ANALYSIS, COMPOSITION):
            with self.subTest(doc=doc.name):
                lowered = read(doc).lower()
                self.assertNotIn("proves it is running", lowered)
                self.assertNotIn("proof it is not a picture", lowered)

    def test_our_rules_are_not_presented_as_corpus_observations(self):
        invariant = section(read(SOURCE_ANALYSIS), r"what is actually invariant")
        self.assertTrue(invariant, "no invariant section in the ledger")
        for rule, marker in [
            ("12:1", "our own threshold"),
            ("no-external-images", "our"),
            ("two durations", "our own budget"),
        ]:
            with self.subTest(rule=rule):
                self.assertIn(rule, invariant.lower())
                index = invariant.lower().index(rule)
                self.assertIn(
                    marker,
                    invariant.lower()[index : index + 400],
                    f"{rule} is stated without marking it as our decision",
                )

    def test_coverage_check_is_labelled_as_name_presence_only(self):
        coverage = section(read(SOURCE_ANALYSIS), r"coverage")
        self.assertTrue(coverage, "no coverage section")
        lowered = coverage.lower()
        self.assertIn("name presence", lowered)
        self.assertRegex(lowered, r"does not prove|not prove")
        self.assertNotIn("5/5 reference sites covered", coverage)


class ReadmeTests(unittest.TestCase):
    def test_readme_names_entrypoint_default_and_pair_install(self):
        text = read(README)
        lowered = text.lower()
        self.assertIn("landing-page", lowered)
        entry = lowered[lowered.index("landing-page") :]
        self.assertRegex(entry, r"entry ?point")
        self.assertIn("editorial-machine", entry)
        self.assertRegex(
            lowered,
            r"both directories|same skills directory|together",
            "README does not state that the router needs its theme installed alongside it",
        )

    def test_readme_invents_no_install_command_for_the_entrypoint(self):
        for line in read(README).splitlines():
            if "install-skill" in line:
                with self.subTest(line=line.strip()):
                    self.assertNotIn("landing-page", line)


if __name__ == "__main__":
    unittest.main()
