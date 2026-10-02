# Reaction ledger — mono-instrument theme

Captured 2026-09-29 by a six-unit research fan-out (one agent per source family). Every row is a page or
API response the unit actually loaded; the orchestrator re-fetched 42 of the cited numbers from source
before use (HN Algolia items API, Arctic Shift ids API, web-features 3.40.0, NN/g) and all 42 matched.

Rows are evidence of **how people reacted**, never of what the author likes. A theme rule that cannot
cite a row here does not ship (see `composition-system.md`).

## Method

- One research agent per source family: A awards, B benchmark sites, H Hacker News, T web-tech
  reception, S controlled studies, R Reddit. Each returns rows with a link. Reaction rows (A, H, R,
  B, and S rows tagged [LAB], [ONLINE], [OBS], [REP], [CRAWL] or [POLL]) also carry a number in the
  signal cell; fact rows (T, and S rows tagged [STD], [GUIDE] or [QUAL]) rest on their primary link.
- Numbers are never invented: a figure the agent could not see on a loaded page is `unverified`.
- The orchestrator spot-checks numbers against the source before a row is used.
- **Population weighting:** for developer-tool pages, H/B/T rows outrank A rows when they conflict;
  S rows decide perceptual questions (timing, contrast, legibility).
- Conflicts are written up in **Tensions**, never resolved silently.
- Re-run the fan-out when this ledger is older than six months or the audience changes.

## A — Design awards and curation

Population: designers / award juries.

| id | item | signal | notes | link | date |
|---|---|---|---|---|---|
| A1 | Awwwards annual winners | SOTY Lando Norris 43 votes, Users' Choice 596; Developer SOTY Messenger 54 | both immersive 3D; neither mono nor dev-tool | https://www.awwwards.com/annual-awards/winners | 2025 |
| A2 | Awwwards Sites of the Year list | 15 top-tier entries 2021–25 | 0 dev tools / AI labs | https://www.awwwards.com/websites/sites_of_the_year/ | 2021–25 |
| A3 | Lando Norris | SOTD 8.18 (D8.12 U7.9 C8.71); Dev 7.58 (Anim 8.60, A11y 7.00); community 8.86 | #111112 + #D2FF00; WebGL/GSAP | https://www.awwwards.com/sites/lando-norris | 2025-11-17 |
| A4 | Igloo Inc | SOTD 7.92; Dev 7.66 (Anim **9.60**, A11y 6.60, Markup 6.40); community 8.55 | near-mono cool greys; 3D, transitions | https://www.awwwards.com/sites/igloo-inc | 2024-07-23 |
| A5 | basement studio | SOTD+Dev 7.42; Dev 7.61 (Anim 7.80); users **8.54** (+1.12 over jury) | pure #000/#fff, Geist Mono, Next.js | https://www.awwwards.com/sites/basement-studio-3 | 2025-04-25 |
| A6 | Next.js Conf (basement) | SOTD+Dev 7.40; Anim 8.00; users 8.20 | Geist Mono, 3D | https://www.awwwards.com/sites/next-js-conf-1 | 2024-09-16 |
| A7 | Vercel Ship 2025 (in-house) | Honorable Mention only; juror votes 6.80–9.00 | Geist Mono + IBM Plex Mono | https://www.awwwards.com/sites/vercel-ship-2025 | 2025-05-22 |
| A8 | NEVERHACK | SOTD+Dev 7.38; Dev 7.78 (SEO 8.20, Markup 8.00, A11y 7.20) | #0E0E0E/#FFF; glitch, 3D hero, scroll-triggered cards, page transitions | https://www.awwwards.com/sites/neverhack | 2025-06-03 |
| A9 | OPTIKKA (AI product) | SOTD+Dev 7.30; Anim 8.40, WPO 8.00 | colorful + mono accent; interactive "How it works" | https://www.awwwards.com/sites/optikka | 2025-06-17 |
| A10 | Type Dither | Nominee only; juror votes 4.60–8.00, mean 6.52 | dither as the concept → split jury | https://www.awwwards.com/sites/type-dither | 2024-03-21 |
| A11 | tag: JetBrains Mono | 31 sites: 3 SOTD, 16 HM, 11 none | common accent font, rarely top | https://www.awwwards.com/websites/JetBrains%20Mono/ | 2021–25 |
| A12 | tag: Geist Mono | 16 sites: 4 SOTD, 5 HM, 7 none | dev-ecosystem cluster | https://www.awwwards.com/websites/Geist%20Mono/ | 2024-09–2025-06 |
| A13 | tag: IBM Plex Mono | p1 31 sites: 11 SOTD, 11 HM | heavy 2025 use as label/accent | https://www.awwwards.com/websites/IBM%20Plex%20Mono/ | 2025-05–08 |
| A14 | collection: Black and White Websites | 68 items; p1 26 SOTD, 1 SOTM | loaded pages 2017–21 | https://www.awwwards.com/awwwards_collections/collections/black-and-white-websites/ | 2017–21 |
| A15 | listing: artificial-intelligence | 26 items: 2 SOTD (2024), 8 HM, 16 none | no AI lab at award level | https://www.awwwards.com/websites/artificial-intelligence/ | –2026 |
| A16 | CSSDA WOTY 2025 | Dropbox Brand 9.03; Exat Typeface Best UI 8.83 | type-driven specimen won Best UI; no dev tool top 10 | https://www.cssdesignawards.com/blog/2025-website-of-the-year-winners/430/ | 2026-02 |
| A18 | HN "scrolljacking" stories | Tell HN never enjoyed scrolljacking 44 pts/10c; Ask HN block scroll-jacking 44 pts/15c | developer hostility | https://hn.algolia.com/api/v1/search?query=scrolljacking&tags=story&hitsPerPage=10 | 2017–2025 |

## R — Reddit (archive snapshots)

Population: web developers, web designers, UX practitioners, r/ClaudeAI. reddit.com returned 403 from the
research host; numbers are Arctic Shift archive snapshots.

| id | post | upvotes / comments | tally & gist | link | date |
|---|---|---|---|---|---|
| R1 | r/webdev: good use of scroll jacking? | 439 / 57 | top 12: 9 critical — (301) leave my scroll alone, (90) unusably slow on phone | https://www.reddit.com/r/webdev/comments/1oibmx3/ | 2025-10-28 |
| R2 | r/webdev: every "beautiful" Three.js scroll-me site | 569 / 101 | top 12: 7 critical — (542) a video that needs human labour to advance; (68) 3D fine, the hijack is the problem | https://www.reddit.com/r/webdev/comments/1uvnzo6/ | 2026-07-13 |
| R3 | r/webdev: why more sites scroll-jack lately | 97 / 33 | top 12: 11 critical — (91) AI-made, too many animations; (9) scroll-linked ≠ scroll-jacking | https://www.reddit.com/r/webdev/comments/1vvdyqq/ | 2026-08-22 |
| R4 | r/webdev: how is this site so smooth? (Lenis site) | 165 / 77 | top 10: 7 critical — stutter, not smooth, hard to consume | https://www.reddit.com/r/webdev/comments/1l3weej/ | 2025-06-05 |
| R5 | r/web_design: eyes exhausted by award-site animation | 66 / 30 | top 12: 9 agree; (16) McMaster-Carr is the best site | https://www.reddit.com/r/web_design/comments/1uipon6/ | 2026-06-29 |
| R6 | r/webdev: text-based agent "thinking" animation | 387 / 47 | top 12: 5 positive — watching the reasoning stream makes waits feel shorter | https://www.reddit.com/r/webdev/comments/1tetzlb/ | 2026-05-16 |
| R7 | r/webdev: ASCII portal with hand tracking | 713 / 40 | top 8: 5 positive, 0 critical — ASCII as an effect | https://www.reddit.com/r/webdev/comments/1lsaixb/ | 2025-07-05 |
| R8 | r/web_design: "best terminal-inspired portfolio" | 32 / 24 | top 12: 8 critical — (30) recruiter nightmare, (7) accessibility nightmare | https://www.reddit.com/r/web_design/comments/1mlkhte/ | 2025-08-09 |
| R9 | r/webdev: exploration of monospace design | 14 / 6 | 3 of 3 critical — inputs, buttons and grid indistinguishable | https://www.reddit.com/r/webdev/comments/1fp5cyt/ | 2024-09-25 |
| R10 | r/web_design: "Monochrome problem" | 4 / 13 | top 10: 2 like the grey look (17), 5 suggest one semantic accent — weak signal | https://www.reddit.com/r/web_design/comments/1wlsx2c/ | 2026-09-20 |
| R11 | r/webdev: does anyone use dark/light toggles? | 110 / 227 | top 10: 4 pro-dark (307, 269), 4 follow the OS or offer light/dark/system | https://www.reddit.com/r/webdev/comments/1ky0ipe/ | 2025-05-29 |
| R12 | r/ClaudeAI: dead giveaways of AI-slop websites | 2,445 / 189 | (373) purple-blue gradients, bento, rounded boxes, gradient-text hero; (67) black bg + neon/lime + Inter + left-border cards | https://www.reddit.com/r/ClaudeAI/comments/1s6mm8o/ | 2026-03-29 |
| R13 | r/UXDesign: Inter-everywhere meme | 837 / 95 | (147) every project ends on Inter; alternatives named incl. IBM Plex Sans (16) | https://www.reddit.com/r/UXDesign/comments/1ncb5ys/ | 2025-09-09 |
| R14 | r/web_design: showoff personal site | 58 / 24 | top 8: 5 critical — (22) WCAG?, (22) beautiful but can't read or navigate | https://www.reddit.com/r/web_design/comments/1wqll0m/ | 2026-09-26 |
| R15 | r/web_design: terminal-styled résumé | 403 / 96 | top 10: 5 critical — (207) binned in job hunts, (71) pretty but unreadable | https://www.reddit.com/r/web_design/comments/elar9i/ | 2020-01-07 |
| R16 | r/web_design: terminal code mockups as images | 634 / 94 | (148) can't copy-paste code shown as an image | https://www.reddit.com/r/web_design/comments/jdwiz5/ | 2020-10-19 |
| R17 | r/web_design: animated SVG buttons | 1,507 / 116 | top 10: 8 positive, 4 conditional on real `<button>` elements (167) | https://www.reddit.com/r/web_design/comments/j7ay0g/ | 2020-10-08 |
| R18 | r/webdev: custom cursor showcase | 2,001 / 236 | top 10: critical 1,613 pts vs supportive 573 — (1,007) "I hate it" | https://www.reddit.com/r/webdev/comments/vql26g/ | 2022-07-03 |
| R19 | r/webdev: please stop fake smooth-scrolling | 841 / 207 | top 10: 5 critical — (268) OS and browser scroll physics differ | https://www.reddit.com/r/webdev/comments/6avsu1/ | 2017-05-13 |
| R20 | r/web_design: Awwwards satire | 1,034 / 90 | (362) award sites are couture — unusable but inspiring; (104) judges reward painful navigation | https://www.reddit.com/r/web_design/comments/xcszr8/ | 2022-09-13 |
| R21 | r/web_design: Berkshire Hathaway site "beautiful" | 974 / 157 | top 10: 6 positive — plain, simple, effective | https://www.reddit.com/r/web_design/comments/hpacyk/ | 2020-07-11 |

## B — Benchmark developer-tool and AI-lab sites

Population: developers on HN + design Twitter.

| id | item | signal | praised / criticized | link | date |
|---|---|---|---|---|---|
| B1 | PlanetScale mono/markdown site (thread by marketing lead) | X 2,227 likes, 424,085 views; self-reported signups +103%, qualified inbound +57% vs prior 4 mo (no control) | + text-first, engineer-direct, no fluff; − readability complaints → added TOC, spacing, size | https://x.com/hollylawly/status/1897332070571250144 | 2025-03-05 |
| B2 | Vercel Geist (Sans + Mono) launch | X 2,657 likes, 684,261 views; HN only 36 pts / 16 c | + precise letter details, sans pairs with mono; weak HN pickup | https://x.com/vercel/status/1717980331989491992 | 2023-10-27 |
| B3 | Monaspace (GitHub Next) | HN 651 pts / 199 c; 19,674 stars | + texture healing, demo page | https://news.ycombinator.com/item?id=38210574 | 2023-11-09 |
| B4 | The Monospace Web | HN 612 pts / 152 c; top-7: 3 critical, 1 mixed, 2 positive | + tree/table CSS; − mono body text less legible, tight leading, walls of text on phones | https://news.ycombinator.com/item?id=41370020 | 2024-08-27 |
| B5 | "Tells of a Slop UI" | HN 381 pts / 241 c | − gradients, rainbow colour, pulsing badges, rounded "fingernail" cards, emoji, misaligned ASCII/SVG, Inter/JetBrains Mono with `//`, redundant text, glassmorphism, hype taglines | https://news.ycombinator.com/item?id=49867038 | 2026-09-27 |
| B6 | "Purposeful animations" (emilkowal.ski) | HN 546 pts / 134 c | + purposeful motion; − make it faster (300 ms already slow), remove waits, provide off switch; the two comments quoting the article's first-viewport Linear explainer both criticise it (plays while you read, doesn't explain, can't be rewound: 45142494, 45154668) | https://news.ycombinator.com/item?id=45139088 | 2025-09-05 |
| B7 | craft micro-interaction libraries | sonner 13,017 ★, cmdk 12,994 ★, vaul 8,629 ★ | wide adoption of interaction craft | https://github.com/emilkowalski/sonner | 2026-09-29 |
| B8 | Ghostty 1.0 site | HN 2,319 pts; 18 site comments, 9 sampled: 2 +, 6 − | + ASCII ghost animation drove a download; − JS-only, no noscript, mobile confusion, pitch unclear | https://news.ycombinator.com/item?id=42517447 | 2024-12-26 |
| B9 | Oxide homepage | HN 876 pts / 256 c | + aesthetics; − never-stopping scroll animations kept ~2.5 CPU cores busy | https://news.ycombinator.com/item?id=27294471 | 2021-05-26 |
| B10 | Oxide in-browser console demo | HN 149 pts / 111 c | + design language of the live console demo | https://news.ycombinator.com/item?id=39804052 | 2024-03-24 |
| B11 | Zed 1.0 | HN 2,153 pts; only site comment: "one of the best looking and most responsive websites" | + responsiveness = design quality | https://news.ycombinator.com/item?id=47949027 | 2026-04-29 |
| B12 | Teenage Engineering EP-1320 page | HN 880 pts; 3/3 design comments positive | + unique yet usable | https://news.ycombinator.com/item?id=41176831 | 2024-08-06 |
| B13 | Linear.app new homepage | HN 212 pts / 125 c | − headline never says what the product is | https://news.ycombinator.com/item?id=33199304 | 2022-10-14 |
| B14 | "The Linear effect" + co-founder sameness fear | 68 likes; co-founder post 740 likes / 120,899 views | − dark UI + blurred gradients + glow became a template | https://rectangle.substack.com/p/the-linear-effect | 2023-01 / 2025-12 |
| B15 | "Where's the AI design Renaissance?" | HN 104 pts / 83 c | − LLM design converges on median; LLMs output Linear clones | https://news.ycombinator.com/item?id=45602996 | 2025-10-16 |
| B16 | HN comments: scrolljacking | 43 + 42 mentions since 2024-09; 6/6 sampled negative | − one said it alone deters them from the product | https://hn.algolia.com/api/v1/search?query=%22scrolljacking%22&tags=comment&numericFilters=created_at_i%3E1725148800 | 2024-09–2026-09 |
| B17 | HN comments: custom cursor | 8 mentions; 2/2 site samples negative | − needs JS, links hard to follow | https://hn.algolia.com/api/v1/search?query=%22custom%20cursor%22&tags=comment&numericFilters=created_at_i%3E1725148800 | 2024-09–2026-09 |
| B18 | "Invisible Details of Interaction Design" (rauno.me) | HN 160 pts; top-5 comments skeptical | − low contrast, floating bar covers text, don't animate taps | https://news.ycombinator.com/item?id=36669249 | 2023-07-10 |

## H — Hacker News threads and comment tallies

Population: developers (weighted highest for developer-tool pages).

| id | thread | points / comments | tally & gist | link | date |
|---|---|---|---|---|---|
| H1 | The Monospace Web | 612 / 152 | top 18: +7 −6 ±1; readability raised by 5/18 (tight leading, phones) | https://news.ycombinator.com/item?id=41370020 | 2024-08-27 |
| H2 | "monospace hard to read" comments since 2024-09 | 16 comments | 5/5 on-topic negative, mostly phones | https://hn.algolia.com/api/v1/search?query=monospace%20hard%20to%20read&tags=comment&typoTolerance=false&numericFilters=created_at_i%3E1725148800 | 2024-09–2026-09 |
| H3 | Tells of a Slop UI | 381 / 241 | top 16: 8 agree; monospace mentions 3/3 negative; tell = "all caps with letter-spacing ALWAYS… monospace" | https://news.ycombinator.com/item?id=49867038 | 2026-09-27 |
| H4 | Every vibe-coded website is the same page | 207 / 117 | top 12: 5 agree generic, 0 defend | https://news.ycombinator.com/item?id=45622944 | 2025-10-17 |
| H5 | WebTUI (browser pretending to be a terminal) | 321 / 153 | #1 comment (92 replies) questions terminal nostalgia | https://news.ycombinator.com/item?id=43668250 | 2025-04-12 |
| H6 | Personal site redesigned as a TTY | 271 / 120 | top 18: 6 ask for click navigation or plain version | https://news.ycombinator.com/item?id=43867211 | 2025-05-02 |
| H7 | terminal.shop (real SSH product) | 904 / 407 | real terminal-native product wins | https://news.ycombinator.com/item?id=40227208 | 2024-05-01 |
| H8 | Ruby website redesigned | 427 / 194 | top 18: 7 praise visuals, 10 attack build (preloader %, scroll-triggered counters, JS-only code samples, heavy images) | https://news.ycombinator.com/item?id=46342859 | 2025-12-21 |
| H9 | New YC homepage | 298 / 157 | top 16: +7 −2; praised clear claim, real photos, hover-triggered video | https://news.ycombinator.com/item?id=46735644 | 2026-01-23 |
| H10 | Bruno Simon 3D portfolio | 777 / 188 | top 17: +9 −3; as a homepage: slow, tab freeze (15 replies), fans (39 replies) | https://news.ycombinator.com/item?id=46206531 | 2025-12-09 |
| H11 | ASCII characters are not pixels | 1353 / 149 | top 11: +6 −1; ASCII as technique loved | https://news.ycombinator.com/item?id=46657122 | 2026-01-17 |
| H12 | Ghostty 1.0 (homepage comments) | 2319 / 681 | ~15 critical of the ASCII hero (never says it's a terminal); 4 praise the page (42519478 "the landing page is just fantastic"; 42519514 downloaded because of the animation; see B8) | https://news.ycombinator.com/item?id=42517447 | 2024-12-26 |
| H13 | Claude Opus 5.5 launch page | 1806 / 1129 | 3 critical of parallax/scroll hero, 0 praise | https://news.ycombinator.com/item?id=49803892 | 2026-09-22 |
| H14 | NEO Emacs animated landing | 51 / 77 | − lost interest: page "filled with useless animations in spite of" prefers-reduced-motion; the author only repointed an existing demo link | https://news.ycombinator.com/item?id=49702779 | 2026-09-14 |
| H15 | Death to Scroll Fade | 412 / 210 | top 14: 10 against scroll animation (fade-in, parallax, hide-on-scroll header), 0 defend; 2 motion sickness | https://news.ycombinator.com/item?id=47426932 | 2026-03-18 |
| H16 | Scroll-Driven Animations showcase | 62 / 56 | top 10: −7 +2 (+ = scroll progress bar, NYT long-form) | https://news.ycombinator.com/item?id=42989635 | 2025-02-09 |
| H17 | scrolljacking / scroll hijacking comments since 2024-09 | 43 / 72 comments | 7/7 and 4/4 on-topic samples negative | https://hn.algolia.com/api/v1/search?query=scrolljacking&tags=comment&typoTolerance=false&numericFilters=created_at_i%3E1725148800 | 2024-09–2026-09 |
| H18 | Josh Comeau whimsical animations page | 143 / 38 | top 10: +6 −1; praised that effects turn off under reduced motion | https://news.ycombinator.com/item?id=43171079 | 2025-02-25 |
| H19 | Please don't force dark mode | 274 / 256 | top 15: follow system 5, prefer light 3, defend dark 2, fix low contrast 2 | https://news.ycombinator.com/item?id=42762054 | 2025-01-19 |
| H20 | How's Linear so fast? | 497 / 236 | top 12: 4 say it doesn't feel fast — HN checks speed claims | https://news.ycombinator.com/item?id=48437609 | 2026-06-07 |
| H21 | Bring Back Idiomatic Design | 694 / 369 | top 12: 10 agree (standard controls, words over icons, visible scrollbars) | https://news.ycombinator.com/item?id=47738827 | 2026-04-12 |
| H22 | Thank you for not redesigning HN | 1831 / 390 | top 8: +6 — speed and convention are house values | https://news.ycombinator.com/item?id=20854214 | 2019-09-01 |
| H23 | McMaster-Carr best e-commerce site | 1402 / 491 | top 10: +7 — fast, dense, conventional | https://news.ycombinator.com/item?id=32976978 | 2022-09-25 |
| H24 | Dithering Part 1 (scroll explainer) | 461 / 96 | "beautiful" ×3; 2 say harder to read; text over crawling dither strains eyes | https://news.ycombinator.com/item?id=45750954 | 2025-10-29 |
| H25 | IBM Plex launch page (font thread) | 240 / 170 | top 10: 9 attack the scroll-jacked launch page ("scroll-o-death"), 1 praises the font — a scrolljacking row, not font praise | https://news.ycombinator.com/item?id=16701009 | 2018-03-28 |
| H26 | Mona Sans and Hubot Sans | 180 / 70 | top 10: lukewarm — "too grotesk", I/l ambiguity, "plenty of free fonts already" | https://news.ycombinator.com/item?id=33834118 | 2022-12-02 |

## T — Web-platform support and developer reception

Population: State of CSS/HTML/JS respondents, HN.

| id | tech | support (web-features 3.40.0, 2026-09-24) | reception | link | date |
|---|---|---|---|---|---|
| T1 | Same-document View Transitions (`document.startViewTransition`) | Baseline low 2025-10-14 (Chrome 111, Firefox 144, Safari 18) | State of CSS usage 20.95% → 27.14%; HN Chrome-111 thread 173 pts / 127 c, mixed — top reply: heavy use causes dizziness | https://news.ycombinator.com/item?id=35091423 | 2023–2026 |
| T2 | React `<ViewTransition>` on Next 15.5 | experimental channel only (`unstable_`); stable React 19.0.0 installed exports none (checked locally) | — | https://nextjs.org/docs/app/guides/view-transitions | 2026-08-25 |
| T3 | CSS scroll-driven animations | Limited: Chrome 115, Safari 26, Firefox none | usage 13.62% → 17.69%; demo-site HN thread 62 pts / 56 c, top comments report nausea | https://news.ycombinator.com/item?id=42989635 | 2025-02-09 |
| T4 | `@starting-style` | Baseline low 2024-08-06 | no dedicated thread | https://cdn.jsdelivr.net/npm/web-features@3.40.0/data.json | 2024 |
| T5 | text-wrap balance / pretty | balance Baseline 2024-05-13; pretty Limited (no Firefox, degrades to normal wrap) | usage 49.51% / 41.73%; HN pretty 364 pts / 153 c positive | https://news.ycombinator.com/item?id=43622703 | 2025-04-08 |
| T6 | Popover API | Baseline low 2025-01-27 | HN 385 pts / 158 c; State of HTML usage 20.67% | https://news.ycombinator.com/item?id=40317740 | 2024-05-10 |
| T7 | Anchor positioning | Limited (core keys in Chrome/Firefox 147/Safari 26) | #1 favourite and #1 avoided-for-support (121 answers) in State of CSS 2026 | https://2026.stateofcss.com/en-US/features/ | 2026 |
| T8 | Lenis smooth scroll | JS library | launch 22 pts vs 50 comments; top comments: breaks swipe-back, spins fans | https://news.ycombinator.com/item?id=33622411 | 2022-11-16 |
| T9 | HN comment volume on scroll hijacking | — | "scroll hijacking" 352, "scrolljacking" 301 comment mentions (volume, not sentiment) | https://hn.algolia.com/api/v1/search?query=scrolljacking&tags=comment | 2026-09-29 |
| T10 | Mono fonts on HN | — | Monaspace 651, JetBrains Mono 506, Berkeley Mono 355, Commit Mono 231, Departure Mono 185, Geist 36 (skeptical: yet another dev font, 0 vs O) | https://news.ycombinator.com/item?id=22053998 | 2020–2024 |
| T11 | next/font self-hosting | stable | no layout shift, no external request | https://nextjs.org/docs/app/getting-started/fonts | current |
| T12 | Motion (framer-motion 12, installed) | JS; WAAPI mini animate 2.3 kb | motion 25.4 M/wk + framer-motion 53.4 M/wk; animating non-transform/opacity hits main thread | https://motion.dev/docs/performance | 2026 |
| T13 | Dither/ASCII shaders | WebGL | Ditherpunk 1,290 pts; R3F 3D portfolio 80 pts with fan-noise + "can't tell what's clickable" | https://news.ycombinator.com/item?id=25633483 | 2021 / 2025 |
| T14 | Speculation Rules | Limited (Chrome only) | usage 4.03%, never heard 72.99%; HN 104 pts with pushback (wasted load, battery) | https://news.ycombinator.com/item?id=44747241 | 2025-07-31 |
| T15 | Next 15.5 experimental PPR / cacheComponents | throw CanaryOnlyError on stable | — | https://cdn.jsdelivr.net/npm/next@15.5.26/dist/shared/lib/canary-only.js | 2026 |
| T16 | SIL Open Font License 1.1 — FAQ (Reserved Font Name) | licence text | a subset is a Modified Version and would not normally keep a Reserved Font Name (FAQ 2.6); 2.7 allows a Functional-Equivalence exception | https://openfontlicense.org/ofl-faq/ | current |
| T17 | IBM Plex — OFL with Reserved Font Name "Plex"; subsets published by the RFN holder | licence text | the RFN holder ships its own latin subsets (e.g. IBMPlexMono-Regular-Latin1.woff2, 17,544 B in @ibm/plex-mono 2.5.0), so using those subsets keeps the name | https://cdn.jsdelivr.net/npm/@ibm/plex-mono@2.5.0/LICENSE.txt | 2026-06-11 |
| T18 | Monaspace — OFL with Reserved Font Name "Monaspace" and its subfamily names; no subsets in its v1.400 repo or release | licence text; repo and release files at v1.400 | the LICENSE reserves "Monaspace" plus "Argon", "Neon", "Xenon", "Radon" and "Krypton"; MonaspaceNeon-Regular.woff2 (static) is 199,508 B and Monaspace Neon Var.woff2 510,832 B; the web fonts in the repo and the release zips are static, variable and Nerd Font builds, with no subset files | https://github.com/githubnext/monaspace/blob/v1.400/LICENSE | 2026-03-28 |

## S — Controlled studies and large surveys

Population: general users (lab, online, representative).

| id | study [class] | n | finding | link | year |
|---|---|---|---|---|---|
| S1 | Lindgaard et al. 50 ms [LAB] | unverified | appeal judged within 50 ms; 50 ms ratings track 500 ms ratings | https://www.tandfonline.com/doi/abs/10.1080/01449290500330448 | 2006 |
| S2 | Lindgaard et al. appeal vs trust vs usability [LAB] | unverified | at 50 ms all three "largely driven by visual appeal" | https://doi.org/10.1145/1959022.1959023 | 2011 |
| S3 | Tuch et al. complexity × prototypicality [LAB] | 59 + 82 | low complexity + high prototypicality most beautiful within 17 ms; atypical layouts judged unattractive | https://research.google.com/pubs/archive/38315.pdf | 2012 |
| S4 | Reinecke & Gajos, preferences worldwide [ONLINE] | ~40,000 people, 2.4 M ratings | higher education generally lowers preference for colourfulness | https://doi.org/10.1145/2556288.2557052 | 2014 |
| S5 | Fogg et al. web credibility [ONLINE] | 2,684 | "design look" = most frequent credibility cue, 46.1% of comments | https://doi.org/10.1145/997078.997097 | 2003 |
| S6 | Nielsen response limits [GUIDE] | — | 0.1 s instantaneous / 1 s flow / 10 s attention | https://www.nngroup.com/articles/response-times-3-important-limits/ | 1993 |
| S7 | Core Web Vitals thresholds [STD] | p75 real users | INP ≤200 ms good; LCP ≤2.5 s; CLS ≤0.1; causality lost >200 ms | https://web.dev/articles/defining-core-web-vitals-thresholds | current |
| S8 | RAIL [GUIDE] | — | respond ≤100 ms; handlers <50 ms; frame work ≤10 ms | https://web.dev/articles/rail | current |
| S9 | Deloitte "Milliseconds Make Millions" [OBS] | 37 brands, >30 M sessions | per 0.1 s mobile speed gain: retail conv +8.4%, travel conv +10.1% | https://www.deloitte.com/ie/en/services/consulting/research/milliseconds-make-millions.html | 2020 |
| S10 | NN/g animation duration [GUIDE] | — | most UI animation 100–500 ms; simple feedback ~100 ms; too long far more common than too short | https://www.nngroup.com/articles/animation-duration/ | — |
| S11 | Apple HIG Motion [GUIDE] | — | brevity and precision; make motion optional; gratuitous motion can cause discomfort | https://developer.apple.com/design/human-interface-guidelines/motion | current |
| S12 | NN/g "Scrolljacking 101" [QUAL] | not reported | threats to control, discoverability, efficiency, task success | https://www.nngroup.com/articles/scrolljacking-101/ | 2023 |
| S13 | Agrawal et al. vestibular dysfunction [REP] | 5,086 adults 40+ | 35.4% vestibular dysfunction (balance test) | https://pubmed.ncbi.nlm.nih.gov/19468085/ | 2009 |
| S14 | Web Almanac accessibility [CRAWL] | unverified | prefers-reduced-motion used by 49% desktop / 50% mobile sites | https://almanac.httparchive.org/en/2024/accessibility | 2024 |
| S15 | Piepenbrock et al. polarity × size [LAB] | unverified | dark-on-light advantage grows as text gets smaller; avoid small light-on-dark text | https://pubmed.ncbi.nlm.nih.gov/25141597/ | 2014 |
| S16 | NN/g dark vs light review [GUIDE] | review | normal vision performs better in light mode; offer both | https://www.nngroup.com/articles/dark-mode/ | 2020 |
| S17 | Android Authority reader poll [POLL] | 3,110 votes | 73% keep dark mode always on | https://www.androidauthority.com/dark-mode-survey-results-3682352/ | 2026 |
| S18 | Mansfield, Legge & Bane font effects [LAB] | 50 + 42 | proportional read 5% faster (normal vision); fixed-width better near smallest readable size (Times up to 50% slower there) | https://pubmed.ncbi.nlm.nih.gov/8675391/ | 1996 |
| S19 | "Good fonts for dyslexia" [LAB] | 48 | sans, monospaced, roman improved reading over serif/proportional/italic | https://doi.org/10.1145/2513383.2513447 | 2013 |
| S20 | WCAG 2.2 SC 1.4.3 / 1.4.8 [STD] | — | text ≥4.5:1 (large ≥3:1); blocks ≤80 chars (CJK ≤40) | https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html | current |
| S21 | NN/g low-contrast text [GUIDE] | — | low-contrast minimalism hurts legibility and discoverability | https://www.nngroup.com/articles/low-contrast/ | — |
| S22 | NN/g flat UI eyetracking [LAB] | 71 | weak clickable cues: +22% time, +25% fixations | https://www.nngroup.com/articles/flat-ui-less-attention-cause-uncertainty/ | — |
| S23 | Heer & Robertson animated transitions [LAB] | unverified | animated transitions can significantly improve graphical perception | https://doi.org/10.1109/tvcg.2007.70539 | 2007 |
| S24 | Skeleton screens A/B [LAB] | unverified | no statistically significant perceived-speed gain | https://doi.org/10.1145/3232078.3232086 | 2018 |

## Tensions

- **Motion — designers vs developers.** Award juries score motion craft highest (A4 animations 9.60, A3 8.60),
  while the developer rows punish four kinds of motion: tied to scroll (H15 10 of 14 against, H16 7 of 10, H13),
  never stopping (B9), ignoring reduced motion (H14) and making the reader wait (B6). H10's 3D homepage is
  mixed (+9 −3; the negatives: slow to load, a frozen tab, spinning fans). For developer-tool pages the
  theme follows the developer rows: motion answers input, stays inside a figure, never loops.
  No row tests a bounded, first-viewport, reduced-motion-respecting demo of the proof object. The closest
  direct evidence, B6's two comments on a first-viewport autoplay explainer, is negative, and H14 punishes
  animation that ignores reduced motion. Among the developer rows here, B8 is the one positive autoplay case, and
  it is mixed: an ASCII animation drove a download, but 6 of its 9 sampled site comments were negative. R6 (a
  "thinking" animation during a wait) and R7 (an ASCII effect driven by hand tracking) reward motion driven by a
  state or by input. Adding such a demo is a judgment call; record it as one.
- **Dark vs light.** Self-selected polls prefer dark (S17 73%), a controlled study and a review find light
  more legible (S15, S16), developers ask to follow the system setting (H19). The theme follows the OS and
  offers a toggle.
- **Monospace.** Mono fonts are the strongest positive in the developer rows (B1, B2, B3, T10) and the most
  consistent legibility complaint when used for body text (B4, H1, H2); by 2026 stock mono plus terminal
  decoration reads as generated (B5, H3). Mono is structure (commands, ids, data, labels), prose is proportional.
- **Best mono by reaction vs budget.** Monaspace leads the developer reaction rows (B3, T10), but it reserves
  its names and its v1.400 repo and release ship no subsets, only static, variable and Nerd Font webfonts (Neon:
  199,508 B static Regular, 510,832 B variable; T18), and a subset you make would not normally keep a Reserved
  Font Name (T16). The award-evidence runner-up (A13 IBM Plex Mono) reserves its name too, but the RFN holder
  publishes its own latin subsets, so a page that ships those subsets keeps the name (T17).
- **One accent or none.** A small Reddit thread suggests one semantic accent for an all-grey site (R10,
  4 points — weak); award and benchmark rows reward pure black-and-white (A5, A8, B1). The theme keeps zero hue
  and uses inversion (an ink-filled object) as its single emphasis.
- **Mono = professional is untested.** No controlled study compares monochrome and colour for perceived
  professionalism (S-unit gap). The palette decision rests on audience reactions (A5, A8, B1) and indirect
  evidence (S4), not on a direct experiment.
