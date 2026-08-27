# Source Analysis — the editorial landing corpus

Evidence ledger for the `editorial-machine` skill. This file records **what was measured**, not
what the style "feels like". The synthesis that page builders actually follow lives in
[`composition-system.md`](composition-system.md); this file exists so that every rule over there can
be traced back to a site and a number.

Captured: 2026-08-27.

---

## 1. Corpus boundary

The Threads author introduced exactly five sites as his own examples (`제가 만든 것들 예시`):

| # | Site | Role |
|---|---|---|
| 1 | `char.com` | Flagship product landing |
| 2 | `anarlog.so` | Second product landing (privacy/OSS positioning) |
| 3 | `fastrepl.com` | Studio index |
| 4 | `agentpub.dev` | Developer-tool launch page |
| 5 | `johnjeong.com` | Founder's personal page |

Every other link in that thread is a **commenter's submission** posted for critique. Those are not
the author's work, so mixing them in would blend an unrelated design language into the synthesis.
They are excluded from this ledger and from the composition system. Cost if that ruling is wrong:
the skill loses variation it could have learned from. That is the cheaper error.

**The corpus is closed.** Do not widen it while running the skill. If a future site is added, add it
here with the same evidence grades first, then re-derive the synthesis.

---

## 2. Evidence grades

Every claim below carries one of four grades. Nothing is stated without one.

| Grade | Meaning |
|---|---|
| **[computed]** | Read out of the live DOM/CSSOM (`getComputedStyle`, `scrollHeight`, element counts) during the capture run. |
| **[fetched]** | Read out of the served HTML on 2026-08-27 via `curl` (`<title>`, `<meta name="description">`). Re-derived directly for this ledger. |
| **[capture]** | Read off the persisted screenshots in the capture set (§3), including pixel sampling. Re-derived directly for this ledger. |
| **[inferred]** | A reading, a design intent, or a generalization. Not measured. Never cite an inferred item as proof. |

`[computed]` values were produced by an earlier browser capture run and are consumed here as
recorded. They were **not** re-derived by this ledger; where a `[capture]` observation disagrees with
a `[computed]` one, both are kept and the conflict is stated (§9) rather than silently resolved.

---

## 3. Capture set and its limits

Ten screenshots exist:

```
agentpub-desktop.jpg   agentpub-mobile.jpg
anarlog-desktop.jpg    anarlog-mobile.jpg
char-desktop.jpg       char-mobile.jpg
fastrepl-desktop.jpg   fastrepl-mobile.jpg
johnjeong-desktop.jpg  johnjeong-mobile.jpg
```

All five sites are covered, anarlog included. Two limits apply to all of them:

1. **Every capture is 1292×924 px** — including the files named `*-mobile.jpg`. There is no
   narrow-viewport render in the set. [capture]
2. **Three "mobile" files are byte-identical to their desktop twin** (`char`, `agentpub`,
   `johnjeong` — matching SHA-256). The other two (`anarlog`, `fastrepl`) differ by 15 and 40 bytes,
   which is emoji/icon re-rasterization at the same layout, not a different layout. [capture]

**Therefore mobile behavior is NOT OBSERVED for any of the five sites.** Every responsive rule in
`composition-system.md` is `[inferred]` from desktop structure plus general responsive practice, and
is marked as such there. Do not let the skill claim "matches the reference on mobile" — there is no
reference on mobile.

3. Each capture is **viewport-only, above the fold** — not a full-page render. Section ordering
   below therefore comes from `[computed]` DOM order, not from the images. [capture]

---

## 4. Site ledgers

### 4.1 char.com

| Field | Value | Grade |
|---|---|---|
| Title | `Char — AI notepad that gets things done.` | [fetched] |
| Description | `Char knows you, thinks together with you, and works for you.` | [fetched] |
| Canvas | `#ffffff` body background; sampled `#ffffff` at three points | [computed] + [capture] |
| Body text | `oklch(0.3 0.0197 81.53)` — warm near-black, ≈ `#332d23` | [computed] |
| Text contrast | 13.63:1 against white — passes AA and AAA | derived |
| Body face | Geist | [computed] |
| Display face | Besley, 56 px / weight 500, measured at a 920 CSS-px viewport | [computed] |
| Other faces loaded | SF Pro, Geist Mono, Instrument Serif, Patrick Hand, Reenie Beanie | [computed] |
| Page length | 10,660 px — the longest page in the corpus by 2× | [computed] |
| Motion | 0.15 s for interaction feedback; 0.30 s for artifact/state transitions | [computed] |
| Section order | thesis → product proof → agent → context → privacy → CTA | [computed] |

Above-the-fold, in order: centered `{char}` wordmark; a `Backed by Y Combinator` credibility line;
a two-line serif hero (`AI notepad that gets things done.`) set far larger than anything else on the
page; a single dark pill CTA (`Join private beta →`); then a macOS-chrome app window showing a real
dated note. A handwritten arrow and the marginal note `apple notes on steroids!` point at that
window from outside the content column. [capture]

Signature techniques:

1. **Five type families, three jobs.** Besley narrates, Geist/SF Pro carries UI copy, Geist Mono
   carries machine surfaces, and the two handwriting faces (Patrick Hand, Reenie Beanie) are used
   only as margin annotation. The count looks reckless; the *role separation* is what makes it work.
2. **Product screenshot as the hero's evidence**, placed immediately under the CTA, not in a
   features grid halfway down.
3. **Handwritten margin annotation as the comparison claim.** The "apple notes on steroids" pitch is
   deliberately not body copy — it reads as someone's aside, which lowers its burden of proof while
   still landing. [inferred]
4. **Two-speed motion budget**: 0.15 s is "you touched it", 0.30 s is "the artifact changed". Nothing
   ambient. [computed]

Mobile behavior: not observed (§3).

---

### 4.2 anarlog.so

| Field | Value | Grade |
|---|---|---|
| Title | `AI notepad for private meetings.` | [fetched] |
| Description | `Anarlog is the open-source, privacy-first, local-first alternative to Granola AI…` | [fetched] |
| Canvas | `#f2f1ef` warm off-white | [computed] |
| Canvas, as rendered | `#ffffff` sampled at three points in the hero region — see §9 | [capture] |
| Body text | Black | [computed] |
| Text contrast | 18.60:1 against `#f2f1ef` — the highest in the corpus | derived |
| Body face | System stack | [computed] |
| Display face | Caveat, 72 px / weight 600 — the largest hero in the corpus | [computed] |
| Other faces loaded | Georgia/Times; Reenie Beanie, Patrick Hand | [computed] |
| Page length | 5,178 px | [computed] |
| Motion | 82 animated or transitioned elements — 15.8 per 1,000 px, the densest in the corpus | [computed] |
| Section order | privacy → local-first → open-source → pricing → founder letter | [computed] |

Above-the-fold, in order: `anarlog` wordmark in a geometric-round display face; a two-line
handwriting-script hero (`The AI notepad for private meetings.`) at roughly a third of the viewport
height; a two-line plain-system subhead doing the actual explaining; a black `Download for Apple
Silicon` button with an attached dropdown chevron for other builds; then a macOS-chrome window
showing a real note with a live audio waveform. [capture]

Signature techniques:

1. **Script hero, system subhead.** The hero carries none of the information — it carries the
   personality. Every fact is in the neutral system-font line under it. Removing the hero would not
   remove a single fact.
2. **The section order is the argument.** Privacy → local-first → open-source → pricing → founder
   letter puts three verifiable properties ahead of the ask, and closes with the person behind it.
   The pricing section is deliberately not first and not last. [inferred]
3. **Split primary CTA** — one obvious default (Apple Silicon) plus a chevron for the minority path,
   so the common case is one click and the rare case is still reachable. [capture]
4. **Founder letter as the closing proof object**, in place of a testimonial wall. [computed]

Mobile behavior: not observed (§3).

---

### 4.3 fastrepl.com

| Field | Value | Grade |
|---|---|---|
| Title | `Fastrepl` | [fetched] |
| Description | `Fastrepl is a small software studio between Seoul and San Francisco, designing interfaces…` | [fetched] |
| Canvas | `#faf8f6` warm paper | [computed] |
| Canvas, as rendered | `#f0efed` / `#f1f0ee` sampled — see §9 | [capture] |
| Body text | `#111111` | [computed] |
| Text contrast | 17.82:1 | derived |
| Body face | Goudy Bookletter — an old-style serif, used for *body*, not for display | [computed] |
| Headings | **No `<h1>` on the page at all** | [computed] |
| Page length | 1,044 px — near single-screen | [computed] |
| Motion | 16 transitioned elements (15.3 per 1,000 px) | [computed] |
| Content | paired SF/Seoul imagery, trust roster, two large project links, terse footer | [computed] |

Above-the-fold, in order: a small hand-drawn leaf glyph as the mark; a three-item text nav
(`Jobs Email GitHub`); a two-sentence studio statement with 🇰🇷 Seoul / 🇺🇸 San Francisco set inline
with dotted underlines; a `Trusted by …` roster of twelve underlined names — funds and individuals
mixed in one flat run of prose, not a logo wall; a centered `Currently working on` label; then two
large white cards (`{char}`, `anarlog`) each with a one-line description. A fine film grain is
visible over the whole canvas. [capture]

Signature techniques:

1. **Serif as body, no display tier.** With no `<h1>` and no oversized hero, the page has essentially
   one type size. Hierarchy is produced by position and whitespace alone.
2. **Trust roster as running prose.** Underlined links inside a sentence instead of a grayscale logo
   grid — cheaper to build, harder to fake, and it scans as a person listing people. [inferred]
3. **Two products as the entire body.** The studio's proof is the two things it shipped, rendered as
   large cards with their own wordmarks intact.
4. **Terse footer.** No newsletter, no sitemap.
5. **Grain overlay** on the canvas, which is why the rendered color reads cooler than the declared
   `#faf8f6` (§9). [capture]

Mobile behavior: not observed (§3).

---

### 4.4 agentpub.dev

| Field | Value | Grade |
|---|---|---|
| Title | `AgentPub` | [fetched] |
| Description | `AgentPub teaches agents to answer with crisp business summaries and clean linked reports.` | [fetched] |
| Canvas | `#faf8f6` — same token as fastrepl.com | [computed] |
| Canvas, as rendered | `#f2f1ef` / `#ecebe9` sampled — see §9 | [capture] |
| Body text | `#111111` | [computed] |
| Text contrast | 17.82:1 | derived |
| Body face | Goudy Bookletter at 15 px | [computed] |
| Display | `h1` at 96 px / weight 400 — a **6.4× ratio** over body | [computed] |
| Machine surfaces | Mono | [computed] |
| Page length | 1,810 px | [computed] |
| Motion | 9 transitioned elements (5.0 per 1,000 px) — the sparsest in the corpus | [computed] |
| Content | before/after response transformation, linked reports, repeated install command | [computed] |

Above-the-fold, in order: an attribution line `Fastrepl presents` with the studio name linked; the
96 px serif wordmark `AgentPub`; a one-sentence serif subhead; a rounded mono command surface
`$ curl -fsSL https://agentpub.dev/install.sh | sh` with a copy-to-clipboard button; then the proof
object — two side-by-side chat transcripts under the labels `You don't read all this, right?` and
`AgentPub makes the useful part obvious.` The left transcript is a wall of prose, the right is a
short lede plus bullets. Same user question in both. [capture]

Signature techniques:

1. **Install command above the fold, as a first-class UI object** — a real surface with a copy
   button, not a code block buried in a docs link. Repeated later in the page. [computed]
2. **Before/after with the input held constant.** Both columns start from the identical bubble
   (`what is our runway?`); only the answer differs. That is what makes it read as a demonstration
   rather than as marketing. This is the corpus's clearest proof-object pattern.
3. **Extreme display-to-body ratio with a light weight.** 96 px at weight 400 — scale carries the
   emphasis, so the weight does not have to.
4. **Sub-branding by attribution.** `Fastrepl presents` inherits the studio's credibility instead of
   rebuilding it. [inferred]
5. **Lowest motion density in the corpus.** A developer tool page earns trust by holding still.
   [inferred]

Mobile behavior: not observed (§3).

---

### 4.5 johnjeong.com

| Field | Value | Grade |
|---|---|---|
| Title | `John Jeong` | [fetched] |
| Description | `Co-founder @ Fastrepl. Notes on software, work, and things I care about.` | [fetched] |
| Canvas | `body` is transparent over a white page | [computed] |
| Body text | `#1a1a1a` | [computed] |
| Text contrast | 17.40:1 against white | derived |
| Body face | System stack | [computed] |
| Display | Instrument Serif, `h1` at 36 px / weight 400 — the smallest hero in the corpus | [computed] |
| Machine surfaces | Mono, including an inline email composer | [computed] |
| Page length | 896 px — the shortest in the corpus | [computed] |
| Motion | 8 transitioned elements (8.9 per 1,000 px) | [computed] |
| Content | compact personal editorial page | [computed] |

Above-the-fold, in order: `John Jeong` as an italic serif nameplate; `Co-founder @ Fastrepl.` with
the studio linked; a five-item mono tab nav (`About Essays Inspirations Lessons Gallery`) where the
active tab is marked by an underline **and** by a darker weight; three short system-font paragraphs,
with `{char}` embedded in its own wordmark inside the prose; an `h2` section
`Things I'm working on and interested in` with four bullets; and a `Find me in` row of four
monochrome outline icons. Content starts at roughly the left third — the column is left-aligned, not
centered. [capture]

Signature techniques:

1. **Left-aligned single column** — the only site in the corpus that does not center its opening.
   Personal register, not product register. [capture]
2. **Serif for the name and for section heads only.** Everything else is the system font. The serif
   marks "this is a person's voice"; the system font marks "this is information".
3. **Active-state redundancy** in the nav: underline plus weight, never color alone. [capture]
4. **Cross-linking as identity.** Fastrepl and `{char}` both appear as links inside the first three
   sentences, wearing their own type. The personal page and the product pages form one graph.
5. **Mono email composer** as the contact affordance instead of a form. [computed]

Mobile behavior: not observed (§3).

---

## 5. Cross-corpus measurements

| Site | Canvas | Text | Contrast | Body face | Hero | Page px | Motion/1000px |
|---|---|---|---|---|---|---|---|
| char.com | `#ffffff` | `oklch(0.3 0.0197 81.53)` | 13.63:1 | Geist | Besley 56/500 | 10,660 | two-speed budget |
| anarlog.so | `#f2f1ef` | black | 18.60:1 | system | Caveat 72/600 | 5,178 | 15.8 |
| fastrepl.com | `#faf8f6` | `#111` | 17.82:1 | Goudy Bookletter | *(no h1)* | 1,044 | 15.3 |
| agentpub.dev | `#faf8f6` | `#111` | 17.82:1 | Goudy Bookletter 15px | 96/400 | 1,810 | 5.0 |
| johnjeong.com | transparent/white | `#1a1a1a` | 17.40:1 | system | Instrument Serif 36/400 | 896 | 8.9 |

### What is actually invariant

1. **Very high text contrast — 13.6:1 to 18.6:1 across all five.** Every site clears WCAG AAA for
   body text with room to spare. The "warm editorial" feeling comes from *hue* (`#faf8f6`,
   `#f2f1ef`, warm-black `#332d23`), never from lowering contrast. This is the single most
   transferable finding in the corpus, and the easiest one to get wrong by imitating the mood
   instead of the numbers.
2. **Near-white warm-neutral canvas, near-black text.** No site uses a mid-tone canvas or a dark
   theme. Range of canvas lightness across the corpus: `#f2f1ef` → `#ffffff`.
3. **Serif or script carries character; system or mono carries information.** Which family sits in
   which slot varies; the *split* does not.
4. **No stock photography anywhere.** Proof is a real UI window, a real transcript, or a real
   command. [capture]
5. **The proof object appears above or immediately below the fold**, never after a features grid.
6. **Concrete transformation over adjectives.** agentpub's identical-question before/after is the
   purest instance; char's dated note and anarlog's live waveform are the same move.
7. **Explicit boundaries as credibility.** anarlog names privacy/local-first/open-source before
   pricing; fastrepl's roster names individuals who can be checked.
8. **Motion is discrete and short.** Two speeds on char (0.15 s / 0.30 s); single-digit transition
   counts on the short pages.

### What varies — and therefore must be a decision, not a default

| Axis | Range observed | Read |
|---|---|---|
| Page length | 896 px → 10,660 px (**11.9×**) | Length tracks how much has to be proven, not house style. |
| Hero size | none at all (fastrepl) → 96 px (agentpub) | A hero is optional. |
| Display/body ratio | ~1× (fastrepl) → 6.4× (agentpub) | |
| Hero weight | 400 (agentpub, johnjeong) → 600 (anarlog) | Big-and-light and small-and-heavy both appear. |
| Motion density | 5.0 → 15.8 per 1,000 px | Developer tools sit low, consumer apps sit high. [inferred] |
| Alignment | centered (4 sites) → left (johnjeong) | Centered = product; left = person. [inferred] |
| Body face | system, Geist, Goudy Bookletter | |
| Handwriting | heavy (char, anarlog) → absent (agentpub, johnjeong) | Never load-bearing where present. |

**These five pages are not one template.** fastrepl has no `h1`; agentpub's is 96 px. char is 10,660
px; johnjeong is 896 px. Any output that looks like all five at once has copied the surface and
missed the method.

---

## 6. Proof-object catalogue

The reusable part. Each was observed in at least one site.

| Pattern | Seen at | Shape |
|---|---|---|
| Framed app window | char, anarlog | macOS chrome + **real dated/named content**, never lorem |
| Held-constant before/after | agentpub | Identical input, two outputs, labeled by the reader's question |
| Copyable command surface | agentpub | `$` prefix, mono, copy button, repeated later in the page |
| Live-state indicator | anarlog | Audio waveform inside the window — proves it is running |
| Named-people trust roster | fastrepl | Underlined links in running prose, not a logo grid |
| Shipped-work cards | fastrepl | Each product in its own wordmark |
| Founder letter | anarlog | Closes the page in first person |
| Handwritten margin note | char | Outside the column, annotates the proof object |
| Inline contact composer | johnjeong | Mono, in place of a form |

---

## 7. Anti-copy boundary

The skill reproduces **method**, never assets.

Forbidden: reusing any of these wordmarks or glyphs; hotlinking or re-hosting any source image;
copying a page's DOM/CSS; reproducing a site's exact palette *and* type stack *and* section order
together; using another company's trust roster.

Required instead: derive canvas/ink/accent for the product at hand; author proof objects in
HTML/CSS/SVG from that product's real evidence; let section order follow the product's argument.

The specific fonts named here (Besley, Caveat, Goudy Bookletter, Instrument Serif, Geist) are
**evidence of a role structure**, not a shopping list. Reproduce the split; pick the faces.

---

## 8. Not observed

Do not assert any of the following — nothing in the capture set or the computed evidence supports
them:

- Any narrow-viewport / mobile layout, for any of the five sites (§3).
- Breakpoint values, container widths, or fluid type ramps.
- Scroll-triggered behavior, easing curves, or `prefers-reduced-motion` handling.
- Focus-visible styling, skip links, tab order, or any keyboard-accessibility property.
- Touch-target sizes.
- Full-page renders below the fold — section order is from DOM order, not from the images.
- Accent-color usage. No site in this corpus was measured for a signature accent; the "one rationed
  accent" rule in the design spec is a *design decision for our pages*, not an observation here.
- Frameworks, build tooling, or hosting.
- char.com's motion element count (only its durations were recorded).
- Anything about the commenters' sites.

---

## 9. Tensions

Unresolved conflicts between evidence sources. Kept open on purpose.

**T1 — anarlog canvas: `#f2f1ef` [computed] vs `#ffffff` [capture].** Pixel sampling of
`anarlog-desktop.jpg` returns pure white at all three sampled points, while the computed body
background is `#f2f1ef`. Most likely the hero section paints its own white band over a warm body
canvas, and the capture is viewport-only. Unresolved, because no full-page render exists to check.
Treat anarlog as "warm off-white body, possibly white hero band" and do not cite either value as
settled.

**T2 — fastrepl/agentpub canvas: `#faf8f6` [computed] vs `#f0efed`/`#f2f1ef` [capture].** The
rendered pixels read ~10 units darker and less warm than the declared background. A film grain is
plainly visible over the canvas in both captures, which would do exactly this; JPEG compression
alone would not account for a shift this size. Reading: the declared token is the *base*, and a
texture overlay sits on top of it. Reproduce that as base color + overlay, not as a single flat
darker color.

**T3 — char hero at "920 CSS px viewport" vs the 1292 px capture width.** The computed hero metrics
were taken at a different viewport than the screenshots. `Besley 56px/500` is therefore valid at
920 px only; whether it scales at other widths is not observed.

---

## 10. Coverage

Sites required: `char.com`, `anarlog.so`, `fastrepl.com`, `agentpub.dev`, `johnjeong.com`.

```bash
python3 - <<'PY'
from pathlib import Path
p=Path('editorial-machine/references/source-analysis.md').read_text()
for host in ['char.com','anarlog.so','fastrepl.com','agentpub.dev','johnjeong.com']:
    assert host in p, host
print('5/5 reference sites covered')
PY
```
