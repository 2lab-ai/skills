# Composition system — mono-instrument

Rules for a monochrome, instrument-grade developer-tool page. Every rule names the reaction-ledger rows
it rests on (`reaction-ledger.md`). A rule without rows is taste and does not belong here — the contract
test `tests/test_ledger_contract.py` fails on it.

Worked example: the 2lab.ai homepage (github.com/icedac/2lab.ai, 2026-09-29).

## 1. Palette

- **MUST** use no chromatic hue in the page's own palette; build hierarchy from size, weight and inversion (ink fill with canvas text). Rows: A5, A8, A14, B1, S4.
- **MUST** keep body text at 4.5:1 or better and never set body copy grey-on-grey; secondary text stays at 7:1 in the dark theme. Rows: S20, S21, S15.
- **MUST** follow the operating-system colour scheme and offer a manual toggle. Rows: H19, S16, S17, R11.
- **NEVER** use gradients, glassmorphism, glows or rainbow status colour as decoration. Rows: B5, H3, B14.

## 2. Type

- **MUST** set commands, model ids, file paths, tables, flags and keyboard hints in monospace. Rows: S18, S19, B4, H1.
- **MUST** set running prose in a proportional face; monospace body text is the most repeated legibility complaint. Rows: B4, H1, H2, S18, R15, R8.
- **NEVER** use letter-spaced all-caps monospace labels as a house style, `//` decorations, or the stock generated-design faces (Inter, JetBrains Mono). Rows: H3, B5, R12, R13.
- **SHOULD** choose the mono by developer reaction first, then filter by byte budget and licence (a subset you make of an OFL font with a Reserved Font Name would not normally keep the name; the RFN holder's own subsets do). Rows: B3, T10, A13, T11, T16, T17, T18.
- **SHOULD** self-host fonts with the framework's font pipeline so they load with no third-party request, and verify its layout-shift claim with the comparison below. Rows: T11, S7.
- **MUST** compare CLS with and without each webfont before choosing it, against the ≤0.1 threshold (S7); a framework's no-layout-shift claim (T11) is a promise to verify, not a measurement — a prose face that swaps in and rewraps a paragraph moves everything below it. Rows: S7, T11.

## 3. Composition

- **MUST** state in the first screen, in plain words, what each product is. Rows: H12, B13, H9.
- **MUST** keep a conventional page structure (top navigation, one-line definition, products, links) and put the distinctiveness into type, detail and interaction. Rows: S3, H21, H22, H23.
- **SHOULD** give the page one operable proof object built from the product's own documented behaviour, labelled as such, instead of an abstract animation. Rows: B10, H12, H14, B3, R16, R6.
- **SHOULD** present specifications as dense tables or trees in monospace. Rows: B4, H23, B1.
- **MUST** make every clickable element look clickable without hue: underline, border, fill or weight, plus visible focus and pressed states. Rows: S22, A4, R17.
- **MUST** delete product claims the code or documentation cannot back (speed, security, scale) — in inherited sections too — rather than disclaiming them; no hype taglines, and headings that say what the section is. Rows: B5, B13.
- **NEVER** let a fixed element (easter-egg trigger, chat bubble, floating bar) cover content or tap targets at any width; below the width where its corner is empty margin, move it into the gutter or into the page flow. Rows: B18.

## 4. Motion

- **MUST** use motion only to answer input or show a state change — a single, non-repeating pulse on load may mark the initial state — and keep it inside the figure it explains; the bounded proof-object demo below is the only self-starting exception. Rows: H9, H18, B6, S23.
- **MUST** keep durations short: press ≈100–120 ms, state 150–200 ms, movement ≤300 ms; nothing the user has to wait for. Rows: S10, B6, S11.
- **NEVER** hijack or smooth the scroll, fade or reveal content on scroll, use parallax, hide the header on scroll, or show a preloader or scroll-triggered counters. Rows: H15, H16, H17, H8, S12, T8, B16, H25, R1, R2, R4, R19, H13.
- **NEVER** run looping or always-on animation, custom cursors, pulsing or blinking status dots, or a WebGL scene as the page itself. Rows: B9, H10, B17, B5, T13, R18.
- **MAY** add a 1 px reading-progress line driven by CSS scroll-driven animation, as a progressive enhancement only. Rows: H16, T3.
- **MUST** honour `prefers-reduced-motion`: movement stops, colour and opacity feedback stays, every element stays visible. Rows: S13, S14, H18, S11, H14.
- **MAY** run one self-starting demo of the proof object — optional, a judgment call under mixed evidence — only if it is bounded: it starts in the first viewport and never on scroll, runs once per visit for 5 s or less in total, stops on the first input, never loops, never runs under `prefers-reduced-motion: reduce`, and keeps any live region quiet while it runs; each movement in it keeps the durations above. Rows: B6, H14, B9, H15, H16, B8, S25.

## 5. Responsiveness and performance

- **MUST** answer every input with a visible change within 100 ms and keep INP at or under 200 ms. Rows: S6, S7, S8, B11, H20.
- **MUST** keep mobile LCP at or under 2.5 s and CLS at or under 0.1, measured before and after with the same Lighthouse version. Rows: S7, S9.
- **MUST** render complete content with JavaScript disabled; interaction is an enhancement. Rows: H8, B8, S1.
- **SHOULD** remove render-blocking round trips (inline critical CSS) and redirects on the entry URL before adding any effect. Rows: S9, H22, H23.

## 6. Platform features (2026)

- **SHOULD** use Baseline features for state swaps and entries: same-document View Transitions, `@starting-style`, `text-wrap: balance`, the Popover API. Rows: T1, T4, T5, T6.
- **NEVER** ship experimental framework flags that throw on stable builds, or Chrome-only prefetching, in core UX. Rows: T15, T14.

## Checklist (standalone lane: check mechanically; app lane: check in the browser)

- [ ] `<title>`, meta description, one `<h1>`, one `<main>`, a skip link.
- [ ] No chromatic colour in the page palette; computed contrast recorded.
- [ ] Mono only on machine-read strings; prose proportional.
- [ ] Every motion listed with trigger, duration and purpose; reduced-motion capture shows everything visible.
- [ ] Time-axis evidence (frame diff or GIF) for each motion.
- [ ] Content renders with JavaScript disabled.
- [ ] Lighthouse mobile + desktop before/after, same version.
- [ ] No horizontal overflow at 390 px.
- [ ] No fixed element over content at 390 px, 768 px and 1024 px.
