# Composition System — the rules a page must follow

The mandatory half of the `editorial-machine` skill. [`source-analysis.md`](source-analysis.md)
records what was measured; this file turns it into rules a page builder can be held to.

**MUST** = a page is wrong without it. **SHOULD** = deviate only with a stated reason in the page
brief. **MAY** = a choice.

Every rule is tagged with its warrant: **[evidence]** = derived from a measurement in the ledger;
**[decision]** = our own standard, adopted for quality reasons and *not* observed in the corpus.
Do not let a `[decision]` rule be described to anyone as "how the reference sites do it".

---

## 1. The one-paragraph method

Lead with a belief, prove it with a working artifact, and name what the thing does not do. Type
splits into two jobs — one family carries the voice, another carries the machine. The canvas is warm
and near-white, the ink is near-black, contrast stays brutal, and one accent is rationed. Length is
whatever the argument needs, from one screen to eleven. Motion happens only when something changed.

If a page can be summarized as "hero, three feature cards, pricing, footer", it has failed this
system regardless of how it looks.

---

## 2. Token contract

Author these as CSS custom properties on `:root`. Names are a contract — `SKILL.md`, the validator,
and both example pages depend on them.

### 2.1 Color

| Token | Role | Constraint |
|---|---|---|
| `--canvas` | Page background | Warm near-white. Lightness between `#f2f1ef` and `#ffffff`. **[evidence]** |
| `--canvas-raised` | Cards, framed windows, panels | Within ~4% lightness of `--canvas`; separate with a rule or a soft shadow, not with a big value jump. **[evidence]** |
| `--ink` | Body and heading text | Near-black. MAY be hue-tinted (char ships `oklch(0.3 0.0197 81.53)` ≈ `#332d23`). **[evidence]** |
| `--ink-muted` | Captions, labels, metadata | ≥ 4.5:1 on `--canvas`. **[decision]** |
| `--rule` | Hairlines, borders, dividers | Low chroma, low contrast. Decorative only — never the sole carrier of meaning. **[decision]** |
| `--accent` | One product signal | See §2.2. **[decision]** |
| `--accent-ink` | Text placed on `--accent` | ≥ 4.5:1 against `--accent`. **[decision]** |

**Contrast floor (MUST) [evidence]:** `--ink` on `--canvas` ≥ **12:1**. The corpus measured 13.63:1,
17.40:1, 17.82:1, 17.82:1, and 18.60:1 — not one site traded contrast for warmth. Warmth is
delivered by *hue*, never by moving the two values toward each other. Compute the ratio and record
it in the page brief; do not eyeball it.

Dark canvases, mid-tone canvases, and gradient canvases are **out of system**. Zero of five.
**[evidence]**

### 2.2 The accent rule **[decision]**

No site in the corpus was measured for a signature accent — this rule is ours, from the design spec,
not an observation.

- Exactly **one** accent per page. Two accents means the page has no accent.
- It MAY appear on: the primary CTA, one live-state indicator, one emphasis mark. That is the whole
  budget.
- It MUST NOT be the only signal for any state. Pair it with weight, underline, icon, or text —
  johnjeong's active nav tab uses underline **and** weight, which is the pattern to copy.
  **[evidence]**
- It MUST NOT appear in body copy.

### 2.3 Texture **[evidence]**

fastrepl and agentpub render ~10 lightness units darker than their declared `#faf8f6` because a fine
grain sits over the canvas (ledger T2). If you want that, implement it as **base color + a separate
overlay layer** — a repeating SVG/`radial-gradient` noise at very low opacity, `pointer-events:none`,
behind content. Do not bake it into a single flatter hex; you lose the token and you lose the
texture.

### 2.4 Type

| Token | Role | Notes |
|---|---|---|
| `--font-display` | Thesis, section heads. The voice. | Serif or script. Besley / Caveat / Goudy Bookletter / Instrument Serif all appear. **[evidence]** |
| `--font-body` | Reading copy | System stack, Geist, or an old-style serif. **[evidence]** |
| `--font-mono` | Commands, receipts, logs, IDs, code | Non-negotiable for anything a machine emitted. **[evidence]** |
| `--font-hand` | Margin annotation only | OPTIONAL. See §3.4. **[evidence]** |

Every family MUST declare a real local fallback stack. Google Fonts MAY be linked; the page must
stay legible and correctly proportioned if that link fails. **[decision]**

Four families is the ceiling. char loads more, but only because each has a distinct job — if you
cannot name the job in one word, you do not get the family. **[evidence]**

### 2.5 Space, measure, motion

| Token | Value | Warrant |
|---|---|---|
| `--measure` | 60–75ch for reading columns | **[decision]** |
| `--space-*` | One ratio-based scale; section gaps drawn from it | **[decision]** |
| `--dur-tap` | `150ms` — interaction feedback | char, measured **[evidence]** |
| `--dur-artifact` | `300ms` — a thing on screen changed state | char, measured **[evidence]** |
| `--ease` | One shared easing curve for both | **[decision]** — no curve was observed |

Two durations. Not three.

---

## 3. Typography roles

### 3.1 The split (MUST) **[evidence]**

Voice type and machine type never trade places. Commands, transcripts, file paths, versions, and
logs are mono. Thesis and section heads are display. Explanation is body.

Sharpest instance: anarlog's hero is a 72 px script that carries **zero information** — every fact
sits in the plain system-font subhead beneath it. Deleting the hero would delete no facts. If your
hero is load-bearing prose, it is not a hero, it is a paragraph in a large size.

### 3.2 Hierarchy by scale and position, not by weight **[evidence]**

agentpub sets `h1` at 96 px / **weight 400** — a 6.4× jump over 15 px body, at book weight. fastrepl
has no `h1` at all and produces hierarchy purely from position and whitespace.

- Display/body ratio: anywhere from ~1× to ~6.4× is in-corpus. Pick one and hold it.
- Prefer scale, whitespace, and position over bold. Reaching for weight 700 usually means the scale
  is too timid.
- Heading levels MUST descend in order (`h1` → `h2` → `h3`), with no skips. **[decision]**

### 3.3 Deliberate deviation: the `h1` **[decision]**

fastrepl ships **no `h1`**. Our validator rejects that. We are knowingly stricter than the corpus,
because a landing page with no `h1` is hostile to screen readers and to search. Every page this skill
produces has exactly one `h1`. Where visual design wants no visible hero, put the `h1` in the
wordmark or the nameplate — do not hide it with `display:none`.

### 3.4 Handwriting **[evidence]**

- MAY be used for margin annotation, an arrow label, or a stamp. `char` does exactly one of these,
  outside the content column.
- MUST NOT carry a fact that appears nowhere else.
- MUST NOT be used for a heading, a CTA, a label, or body copy.
- Two of five sites use none at all. Absence is in-system.

---

## 4. Section grammar

A page is a sequence of named moves. Not all are required; the **order** is.

| # | Section | Status | Job |
|---|---|---|---|
| S0 | Mark + minimal nav | SHOULD | Wordmark, ≤ 4 text links. No mega-menu. **[evidence]** |
| S1 | **Thesis** | MUST | The belief or tension, in the reader's words. Not a feature. |
| S2 | Lede | SHOULD | 1–2 plain-language sentences carrying the actual facts. **[evidence]** |
| S3 | **Primary action** | MUST | One dominant action. A split default+alternates control is in-system (anarlog). **[evidence]** |
| S4 | **Proof object** | MUST | §5. Above or immediately below the fold. **[evidence]** |
| S5 | Mechanism | SHOULD | How it works, once, concretely. |
| S6 | Verifiable properties | SHOULD | Privacy / local-first / open-source / limits — things a reader can check. **[evidence]** |
| S7 | Install or access | MUST for tools | Real, copyable command. **[evidence]** |
| S8 | Candor | MUST | §6. |
| S9 | Close | SHOULD | Founder letter, contact, or repeat CTA. **[evidence]** |

Rules:

- **S4 MUST NOT come after a features grid.** All five sites put the artifact first. **[evidence]**
- **No features grid at all** unless the product genuinely is a list of parallel capabilities. Zero
  of five sites open with one.
- Order encodes the argument. anarlog runs privacy → local-first → open-source → **pricing** →
  founder letter: three checkable properties before the ask, a person after it. Choose your order
  for the same kind of reason and write that reason in the page brief. **[evidence]**
- Length follows the argument: 896 px to 10,660 px is all in-system, an 11.9× spread. Do not pad a
  short honest page to look substantial, and do not compress a page that has a lot to prove.
  **[evidence]**

Each section is a `<section>` with an accessible name (`aria-labelledby` pointing at its heading).
**[decision]**

---

## 5. Proof objects

**A page needs at least one, authored in HTML/CSS/SVG from the product's real evidence.** No stock
photography — zero instances across the corpus. No externally hosted images. **[evidence]**

| Pattern | Use when | Construction |
|---|---|---|
| **Held-constant before/after** | Output quality is the claim | Identical input in both columns; only the output differs. Label each column with the reader's own question (`You don't read all this, right?`). Strongest pattern in the corpus. **[evidence]** |
| **Framed app window** | There is a real UI | Chrome + **real dated, named content**. char shows a specific August 27 note; anarlog shows a live waveform. Lorem or `Feature One` kills it. **[evidence]** |
| **Copyable command** | It installs from a terminal | Mono surface, `$` prefix, copy button, real command. Above the fold, repeated at S7. **[evidence]** |
| **Live-state indicator** | It runs continuously | A waveform, a counter, a pulse — proof it is not a picture. **[evidence]** |
| **Named-people roster** | Credibility is borrowed | Underlined links in running prose. Never a grayscale logo grid. **[evidence]** |
| **Shipped-work cards** | The proof is other work | Each item in its own wordmark. **[evidence]** |
| **Capability boundary table** | The claim is smallness/auditability | Enumerate what exists and what does not, in the same table. **[decision]** |

The proof object MUST be reachable as text: a screen-reader user gets the same evidence, via real
markup or a described equivalent. A `<figure>` + `<figcaption>` stating what it demonstrates is the
default. **[decision]**

---

## 6. Copy model

- **Thesis before inventory.** Open on the tension. char: *"AI notepad that gets things done."* —
  the complaint about notepads that don't, inverted. **[evidence]**
- **Facts live in plain type.** Display type is for character (§3.1).
- **Concrete beats superlative.** `8.1 months at the current burn` beats "powerful insights". Every
  number on the page maps to a source in the page brief. **[decision]**
- **Candor is a section, not a footnote (S8).** Name the boundary — what it doesn't do, what it
  can't see, what's still experimental. anarlog leads with privacy/local-first/open-source *because*
  those are checkable. **[evidence]**
- **First person for the close.** anarlog's founder letter; johnjeong's whole page. **[evidence]**
- **No invented social proof.** Names in a roster must be real and public. **[decision]**

Register follows subject: centered layout for a product, left-aligned single column for a person —
johnjeong is the only left-aligned page in the corpus and the only personal one. **[evidence]**

---

## 7. Responsive rules — all `[decision]`

**The corpus contains no mobile evidence.** All ten captures are 1292×924, and three "mobile" files
are byte-identical to their desktop twin (ledger §3). Nothing below is imitation; it is our own
standard, and the skill MUST NOT claim reference parity on mobile.

- Support **390×844** and **1440×1000** as the two gate viewports.
- **No horizontal scroll on `<body>` at either width.** Guard it: `overflow-x:hidden` on the
  container is the last resort, not the fix — the fix is `max-width:100%`, `min-width:0` on flex/grid
  children, and `overflow-x:auto` scoped to the wide element (tables, command lines, transcripts).
- One-column below ~720px. Multi-column proof objects (the before/after) stack, **keeping the input
  visible in both** — the comparison is the point.
- Fluid type via `clamp()`. A 96 px hero MUST come down; pick the mobile end deliberately and record
  both ends in the brief.
- Long unbreakable strings (install commands, URLs) get `overflow-wrap:anywhere` or a scoped
  horizontal scroll container. This is the most common source of mobile overflow.
- Reading measure holds at every width: `min(--measure, 100% - 2*gutter)`.
- Primary interactive targets ≥ **44×44 px**, including on desktop.

---

## 8. Motion rules

- **Two durations only:** `--dur-tap` 150 ms for "you touched it", `--dur-artifact` 300 ms for "the
  artifact changed". char's measured budget. **[evidence]**
- **Motion must explain something.** Reveal, state change, or evidence movement. No ambient drift, no
  parallax for its own sake, no decorative loops. **[evidence]** — nothing ambient was measured.
- **Density budget:** 5.0–15.8 animated elements per 1,000 px of page height across the corpus.
  Developer-tool pages sit at the low end (agentpub: 5.0, the sparsest). Count yours and put the
  number in the brief. **[evidence]**
- **`prefers-reduced-motion: reduce` MUST disable all non-essential animation** — transitions,
  transforms, autoplay — while the page stays fully legible and every state stays reachable.
  **[decision]**; no reduced-motion handling was observed in the corpus.
- Never animate `width`/`height`/`top`/`left` for reveals; use `opacity` and `transform`.
  **[decision]**
- Nothing may move on a loop near text. **[decision]**

---

## 9. Accessibility floor — all `[decision]`

None of this was observed in the corpus. It is required anyway; aesthetic direction never overrides
it.

1. `<title>` and `<meta name="description">` present and specific.
2. Landmarks: one `<main>`, plus `<header>`/`<nav>`/`<footer>` as used. Sections named (§4).
3. Exactly one `<h1>`; no skipped heading levels (§3.3).
4. A **skip link** as the first focusable element, visible on focus.
5. Visible `:focus-visible` on every interactive element. Never `outline:none` without a replacement.
6. Body text ≥ 12:1 on canvas (§2.1); all other text ≥ 4.5:1; large text ≥ 3:1.
7. Color is never the sole signal (§2.2).
8. Interactive targets ≥ 44×44 px.
9. Real `<button>`/`<a>` elements. A copy-to-clipboard control is a `<button>` with an accessible
   name and a status message on success.
10. Decorative layers (grain, glyphs, arrows) are `aria-hidden="true"` and `pointer-events:none`.
11. `<html lang>` set.
12. Keyboard reaches every action, in visual order.

Deterministic subset is enforced by `scripts/validate.py`. Passing the validator is necessary, not
sufficient — browser QA (Task 5) is the real gate.

---

## 10. Anti-copy guardrails **[decision]**

Reproduce the method. Never the artifact.

**MUST NOT:** reuse any source wordmark, glyph, or logo; hotlink or re-host any source image; copy a
page's DOM or CSS; ship a page that carries one source's palette **and** type stack **and** section
order together; reuse another company's trust roster; imply endorsement.

**MUST:** derive canvas/ink/accent for the product at hand; author every proof object from that
product's own evidence; let section order follow that product's argument; cite a source in the page
brief for every factual claim.

The fonts named in the ledger are evidence of a **role structure**, not a shopping list. Two pages
from this skill should share grammar and diverge in hierarchy, accent, proof object, and cadence —
if they look like siblings of one template, the skill has been used as a theme and the output is
wrong.

---

## 11. Pre-ship checklist

- [ ] Thesis (S1) is a belief or tension, not a feature list.
- [ ] Proof object (S4) is real, authored, above/near the fold, and text-reachable.
- [ ] Candor section (S8) names a real boundary.
- [ ] `--ink` on `--canvas` ≥ 12:1, ratio computed and recorded in the brief.
- [ ] One accent, never the sole signal, absent from body copy.
- [ ] ≤ 4 type families, each with a nameable job and a real fallback stack.
- [ ] Exactly one `h1`; heading levels descend without skips.
- [ ] Two motion durations; density counted and recorded; reduced-motion honored.
- [ ] 390×844 and 1440×1000: no body horizontal scroll, nothing clipped, hierarchy intact.
- [ ] Skip link, focus-visible, 44px targets, landmarks, `lang`, title, description.
- [ ] Every factual claim traced to a source line in the page brief.
- [ ] No copied asset, palette+type+order triple, or borrowed roster.
