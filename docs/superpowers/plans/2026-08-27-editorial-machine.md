# Editorial Machine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a reusable evidence-led editorial landing-page skill and prove it with responsive llmux and xfx product pages.

**Architecture:** A top-level `editorial-machine` skill separates observed reference evidence, reusable composition rules, deterministic validation, and product-specific examples. Each example is standalone HTML generated from a claim ledger, sharing design principles without sharing a rigid template.

**Tech Stack:** Markdown skill manifests, Python 3 standard-library validator/tests, standalone semantic HTML/CSS/vanilla JS, browser screenshot QA.

**Spec:** `docs/superpowers/specs/2026-08-27-editorial-machine-design.md`

## Global Constraints

- Analyze all five author examples: char.com, anarlog.so, fastrepl.com, agentpub.dev, johnjeong.com.
- Name the skill `editorial-machine`.
- Keep observed facts distinct from inference.
- Do not copy source assets or byte-level layouts.
- Pages must render without a build step and without external image hosts.
- Support 390×844 and 1440×1000 with no body horizontal scroll.
- Include semantic landmarks, focus-visible styles, a skip link, and reduced-motion handling.
- Ground every llmux/xfx factual claim in its project README.

---

### Task 1: Evidence ledger and composition reference

**Files:**
- Create: `editorial-machine/references/source-analysis.md`
- Create: `editorial-machine/references/composition-system.md`

**Interfaces:**
- Consumes: captured DOM/computed-style evidence and `docs/superpowers/specs/2026-08-27-editorial-machine-design.md`.
- Produces: the observed/inferred evidence and mandatory composition rules read by `SKILL.md` and page builders.

- [ ] **Step 1: Write the corpus ledger**

Record each URL, title, computed body/display fonts and colors, page length, content order, motion evidence, signature techniques, and mobile behavior. Mark unavailable information explicitly.

- [ ] **Step 2: Write the synthesis**

Define semantic tokens, typography roles, narrative section grammar, proof-object patterns, responsive rules, motion rules, accessibility constraints, and anti-copy guardrails.

- [ ] **Step 3: Verify source coverage**

Run:
```bash
python3 - <<'PY'
from pathlib import Path
p=Path('editorial-machine/references/source-analysis.md').read_text()
for host in ['char.com','anarlog.so','fastrepl.com','agentpub.dev','johnjeong.com']:
    assert host in p, host
print('5/5 reference sites covered')
PY
```
Expected: `5/5 reference sites covered`.

### Task 2: Skill contract and RED validator tests

**Files:**
- Create: `editorial-machine/SKILL.md`
- Create: `editorial-machine/scripts/validate.py`
- Create: `editorial-machine/tests/test_validate.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: `references/source-analysis.md`, `references/composition-system.md`.
- Produces: `validate_file(path: Path) -> list[str]` and the complete runtime workflow.

- [ ] **Step 1: Write failing tests**

Cover a minimal invalid page missing title/meta/main/h1/skip link/install snippet/reduced-motion/overflow guard, and a valid fixture containing each requirement.

- [ ] **Step 2: Run tests to establish RED**

Run: `python3 -m unittest editorial-machine/tests/test_validate.py -v`
Expected: FAIL because `validate_file` does not exist.

- [ ] **Step 3: Implement minimal validator**

Use `html.parser.HTMLParser` plus text/CSS checks. Return stable human-readable issue strings and exit nonzero from the CLI when any issue exists.

- [ ] **Step 4: Write SKILL.md**

Frontmatter description triggers on requests to create a product/site landing in the researched editorial style. Workflow: fact ledger → thesis → proof object → page brief → implementation → validator → browser QA → fix loop. Include required reads and output contract.

- [ ] **Step 5: Register skill in README**

Add a concise entry and installation command matching existing repository structure.

- [ ] **Step 6: Run tests GREEN**

Run: `python3 -m unittest editorial-machine/tests/test_validate.py -v`
Expected: all tests pass.

### Task 3: llmux landing proof

**Files:**
- Create: `editorial-machine/examples/llmux-brief.md`
- Create: `editorial-machine/examples/llmux.html`

**Interfaces:**
- Consumes: llmux README claims and the composition system.
- Produces: self-contained responsive llmux page passing `validate.py`.

- [ ] **Step 1: Write the claim ledger and page brief**

Map headline, routing lanes, account scheduling, DevTools receipts, remote topology, Islands, install commands, and compliance caveats to exact README line ranges.

- [ ] **Step 2: Implement semantic page**

Use the “harness is capital” thesis, warm paper/dark ink palette, routing-red signal, custom CSS routing diagram, terminal install block, and candid boundary section.

- [ ] **Step 3: Validate structure**

Run: `python3 editorial-machine/scripts/validate.py editorial-machine/examples/llmux.html`
Expected: `PASS editorial-machine/examples/llmux.html`.

### Task 4: xfx landing proof

**Files:**
- Create: `editorial-machine/examples/xfx-brief.md`
- Create: `editorial-machine/examples/xfx.html`

**Interfaces:**
- Consumes: xfx README claims and the composition system.
- Produces: self-contained responsive xfx page passing `validate.py`.

- [ ] **Step 1: Write the claim ledger and page brief**

Map the experimental scope, eight tools, six commands, permission modes, sessions, diagnostics, llmux backend, install commands, and explicit non-goals to exact README line ranges.

- [ ] **Step 2: Implement semantic page**

Use the “small enough to audit” thesis, field-manual grid, safety-green signal, bounded-loop proof object, permission-mode comparison, install block, and explicit absences.

- [ ] **Step 3: Validate structure**

Run: `python3 editorial-machine/scripts/validate.py editorial-machine/examples/xfx.html`
Expected: `PASS editorial-machine/examples/xfx.html`.

### Task 5: Browser QA and receipts

**Files:**
- Create in session scratchpad only: `editorial-machine/receipts/*.png`, `browser-qa.json`.
- Modify if defects found: the relevant example HTML or composition references.

**Interfaces:**
- Consumes: both example pages served over local HTTP.
- Produces: four viewport screenshots and measured DOM QA results.

- [ ] **Step 1: Start local server**

Run: `python3 -m http.server 8767 --directory .`
Expected: server listens on loopback.

- [ ] **Step 2: Capture desktop/mobile**

For each page at 1440×1000 and 390×844, capture a screenshot and run DOM measurements for scroll width, landmarks, heading order, focusables, and reduced-motion CSS.

- [ ] **Step 3: Fix every visual/structural defect**

No clipping, overlap, illegible copy, broken controls, horizontal body scroll, or indistinguishable hierarchy may remain.

- [ ] **Step 4: Rerun automated gate**

Run:
```bash
python3 -m unittest discover -s editorial-machine/tests -v
python3 editorial-machine/scripts/validate.py editorial-machine/examples/llmux.html editorial-machine/examples/xfx.html
```
Expected: tests pass and both pages PASS.

### Task 6: External review, receipt report, and commit

**Files:**
- Create: session scratchpad `editorial-machine-receipt.html`.
- Modify: only files implicated by verified review findings.

**Interfaces:**
- Consumes: complete diff, test output, browser captures, user clause matrix.
- Produces: independently reviewed changes, final gate receipts, one conventional commit.

- [ ] **Step 1: Dispatch code/design review**

Ask a reviewer to inspect the entire branch against the spec, skill authoring quality, claim grounding, accessibility, responsive CSS, and over-engineering. Findings require file:line and a concrete failure scenario.

- [ ] **Step 2: Apply verified findings**

Reject unsupported opinions; patch confirmed defects and rerun the relevant test/browser receipt.

- [ ] **Step 3: Create receipt report**

Build a single HTML report with AS-IS, source evidence, synthesis, files, test output, screenshots, QA method, and residual boundaries.

- [ ] **Step 4: Run final gate**

Run:
```bash
python3 -m unittest discover -s editorial-machine/tests -v
python3 editorial-machine/scripts/validate.py editorial-machine/examples/llmux.html editorial-machine/examples/xfx.html
git diff --check
git status --short
```
Expected: all tests/pages pass, no whitespace errors, only intended files changed.

- [ ] **Step 5: Commit**

```bash
git add README.md docs/superpowers editorial-machine
git commit -m "feat: add editorial landing page skill" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```
