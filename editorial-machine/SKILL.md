---
name: editorial-machine
description: Use when the user asks to build a product, project, or personal landing page in the editorial style researched from char.com, anarlog.so, fastrepl.com, agentpub.dev, and johnjeong.com — a warm-paper canvas, serif-led thesis, one authored proof object, one rationed accent. Triggers on requests for a "landing page", "product page", "launch page", "founder page", or an explicit ask to build a page "in that style" (e.g. for llmux, xfx, or a personal site).
---

# editorial-machine

Builds one standalone HTML landing page per product, in the composition *grammar*
synthesized from five reference sites — never a shared template, never a cloned DOM.

## Required reading (before drafting anything)

Read both in full, not skimmed:

1. [`references/source-analysis.md`](references/source-analysis.md) — the evidence
   ledger. Every claim about the reference corpus is graded `[computed]`/`[fetched]`/
   `[capture]`/`[inferred]`; the anti-copy boundary (§7) and "not observed" list (§8)
   bound what you may assert.
2. [`references/composition-system.md`](references/composition-system.md) — the
   MUST/SHOULD/MAY rules a page is checked against: token contract (§2), section
   grammar (§4), proof-object catalogue (§5), responsive/motion/accessibility rules
   (§7–9), the performance floor (§10), anti-copy guardrails (§11), and the pre-ship
   checklist (§12).

Everything below is the workflow; the rules themselves live in those two files —
do not duplicate them here, cite them.

## Workflow

1. **Fact ledger.** Collect every factual claim about the product this page is for
   (README, changelog, source, install docs) and record a source location for each.
   **Never invent a metric.** This is the single correction the writing-skills RED
   baseline demanded most — invented numbers (`50K API calls`, `99.9% uptime`) are a
   hard failure, not a style choice.
2. **Thesis + proof object.** Pick one belief or tension (composition-system.md §1,
   §6) and one proof object unique to this product (composition-system.md §5,
   source-analysis.md §6). Two pages built by this skill MUST NOT share a proof
   object, a DOM shape, or a palette+type+order triple (source-analysis.md §7).
3. **Page brief.** Write a short brief recording: the thesis, the proof object and
   its construction, the section order and the reason for it, the tokens (canvas /
   ink / accent, with the computed `--ink`-on-`--canvas` contrast ratio — not
   eyeballed), the type roles, the motion count/density, and a source line for every
   factual claim from step 1. This brief is what an external reviewer checks the page
   against — it is not optional paperwork.
4. **Implementation.** Standalone HTML/CSS/JS, no framework or build step. Tokens
   from composition-system.md §2, section grammar §4. No cloned DOM/template — not
   from a reference site, and not from another page this skill previously produced.
5. **Validator.**
   ```bash
   python3 editorial-machine/scripts/validate.py <page.html>
   ```
   Zero issues required. It deterministically rejects a missing `<title>`,
   `<meta name="description">`, `<main>`, exactly-one `<h1>`, skip link, install
   snippet, `prefers-reduced-motion` handling, and horizontal-overflow guard —
   plus the **reduced-motion trap**: an element left at `opacity: 0` whose only
   route to visible is an animation the reduced-motion block switches off.
   **Passing the validator is necessary, not sufficient.**
6. **Browser QA.** Real renders, not a hypothetical review:
   - Desktop (1440×1000) and mobile (390×844): no `<body>` horizontal scroll,
     nothing clipped, hierarchy intact.
   - Keyboard: tab order reaches every action; every interactive element shows a
     visible `:focus-visible` state; skip link is reachable and visible on focus.
   - Contrast: `--ink` on `--canvas` ≥ 12:1, computed, not eyeballed.
   - `prefers-reduced-motion: reduce` emulated in the browser: non-essential motion
     stops, every state stays reachable, and **every revealed element is still
     visible** — check computed `opacity`, not the screenshot alone.
   - Script blocked (`--disable-javascript` or a context with JS off): the page
     still renders its content. A reveal may be hidden by script, never by default.
   Capture both viewport receipts per page — one screenshot is not readiness.
7. **Fix loop.** Any validator issue or QA failure sends you back to step 4. Re-run
   the validator and re-check QA until both are clean before calling the page done.
   Readiness is the named receipts above, not self-opinion.

## Output contract

- One standalone `.html` file per page — no build step, no external image hosting.
- The page brief (markdown) from step 3, alongside the page.
- The validator command and its output, captured verbatim.
- Two browser receipts per page (desktop + mobile), not one side-by-side screenshot.

## Hard rules

- Every factual claim traces to a source in the page brief. No invented metrics.
- No cloned DOM, no shared section template, no text-swapped page across products.
  Share the grammar; never the structure (composition-system.md §11).
- Exactly one accent per page; never the sole signal for any state; absent from body
  copy (composition-system.md §2.2).
- `prefers-reduced-motion: reduce` disables all non-essential animation.
- Skip link, focus-visible on every interactive element, 44×44px primary targets,
  exactly one `<h1>`, `<title>` + description, one `<main>` landmark.
- No stock photography. Proof objects are authored HTML/CSS/SVG from this product's
  own real evidence (source-analysis.md §6, composition-system.md §5).
