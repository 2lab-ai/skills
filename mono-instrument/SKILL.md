---
name: mono-instrument
description: Use when the mono-instrument theme is explicitly named, or when a landing-page request asks for a monochrome, monospace-forward, highly responsive developer-tool page ("모노", "mono", "monochrome", "terminal-grade", "instrument panel"). A generic "landing page"/"product page" request starts at landing-page, not here.
---

# mono-instrument

A theme workflow behind [`landing-page`](../landing-page/SKILL.md). It builds a page in a
monochrome, instrument-panel grammar for developer tools: black/white/grey only, type that
reads like a well-set terminal, one live proof object the visitor can operate, and motion
that answers input instead of decorating the scroll.

What makes this theme different from a taste-driven one: **every visual decision must cite
a row of the reaction ledger** — measured public reactions (Hacker News points and comment
tallies, Reddit upvotes, award jury scores, developer-survey percentages, controlled
studies). A decision with no ledger row is the author's taste and does not ship.

## Lanes

The target contract and lane come from [`landing-page/SKILL.md`](../landing-page/SKILL.md)
§1–§2.

- **Existing-app lane** — the page is a route inside a real app or site repo. It is built in
  the app's own stack, ships through the app's own build, and is checked by the app's own
  gates.
- **Standalone lane** — the page is a self-contained `.html` file with no host app.

If no lane was established, go back to `landing-page/SKILL.md` before writing markup.

## Required reading (before drafting anything)

1. [`references/reaction-ledger.md`](references/reaction-ledger.md) — the evidence: what
   developer and design audiences rewarded and punished, each row with its population, its
   number, its link and its date. Population weighting and known conflicts are stated there.
2. [`references/composition-system.md`](references/composition-system.md) — the MUST/SHOULD
   rules derived from the ledger. Every rule carries the ledger rows it rests on.

The rules live in those two files — cite them, do not restate them here.

## Workflow

1. **Target contract + lane** — from `landing-page/SKILL.md`.
2. **Ledger freshness.** Read the ledger's capture date. If it is older than six months, or
   the page's audience is not developers, re-run the research fan-out described in
   `reaction-ledger.md` §Method (one agent per source family) before designing. Never
   replace a stale row with an opinion.
3. **Fact ledger.** Every product claim gets a source location (README, changelog, source).
   **Never invent a metric** — no request counts, latencies, uptimes or user numbers that
   the product does not publish.
4. **Page brief.** Record: the proof object and what the visitor can do with it, the tokens
   with the *computed* ink-on-canvas contrast, the type roles, the motion inventory (each
   motion: trigger, duration, what it tells the visitor), the performance budget, and a
   **decision → ledger row** table. A row-less decision is removed or justified as a
   stated deviation.
5. **Implementation.** Tokens and rules from `composition-system.md`.
   - *Existing-app lane:* the app's framework, router, component and styling system. Add no
     runtime dependency the page brief does not name and justify.
   - *Standalone lane:* one self-contained HTML/CSS/JS file.
6. **Gates by lane.**
   - *Existing-app lane:* the app's own build, lint, type-check and test commands, plus its
     CI, unmodified. Quote their output.
   - *Standalone lane:* the deterministic checks in `composition-system.md` §Checklist
     (title, description, one `<h1>`, `<main>`, skip link, reduced-motion handling, no
     chromatic colour outside the declared exceptions, no horizontal overflow).
   - Both lanes: performance measured with the same Lighthouse version before and after,
     mobile and desktop.
7. **Browser QA at the delivery URL.** Desktop 1440×1000 and mobile 390×844; keyboard pass
   with visible focus; `prefers-reduced-motion: reduce` emulated (every element still
   visible, no motion that moves layout); JavaScript disabled (content still renders);
   light and dark themes; and **time-axis evidence** for every motion in the inventory —
   consecutive frames with a pixel diff, not a single still.
8. **Fix loop.** Any failed gate or QA item returns to step 5.

## Output contract

- The page brief with its decision → ledger row table.
- Desktop and mobile receipts, light and dark, plus the reduced-motion capture.
- The motion evidence (frame diff or GIF) for each inventoried motion.
- Before/after Lighthouse numbers from the same engine version.
- Existing-app lane: files changed, the route served, the app's gate output verbatim, and
  the delivery URL actually loaded.

## Hard rules

- No decision without a ledger row; no metric without a product source.
- Monochrome means no chromatic hue in the page's own palette. Status colour inside an
  embedded product UI is allowed only where the ledger records it as information, and never
  as decoration.
- Motion answers input or explains the product. No scroll-hijacking, no smooth-scroll
  library, no custom cursor, no preloader — see the ledger rows that punished them.
- `prefers-reduced-motion: reduce` keeps every state reachable and every element visible.
- Skip link, visible `:focus-visible`, 44×44px primary targets, exactly one `<h1>`, one
  `<main>`.
