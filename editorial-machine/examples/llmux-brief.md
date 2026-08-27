# llmux landing brief

## Thesis

**The harness is capital. Models are consumables.** The page makes the instability of model supply the opening tension, then proves that llmux keeps one Claude Code harness unchanged while routing its model names across independently managed backends.

## Audience and single job

For developers and agent operators who have accumulated Claude Code conventions, hooks, MCP servers, and subagents. The page's job is to make the architectural bet legible enough that they will install llmux and inspect it themselves.

## Proof object

**Routing ledger.** A `<figure>` naming the fixed path (Claude Code → `localhost:3456` → llmux daemon) above a two-column table that maps each of the five literal `/model` signals documented in the README to the backend group that resolves it. Five signals, four groups, every group demonstrated. It is a real table with a caption and column headers, so a screen reader gets the same mapping; it is not shared with the xfx example (a vertical field diagram) and is not derived from any reference-site DOM.

## Argument order

1. Thesis and real install command — state the bet and offer the reversible action.
2. Routing ledger — prove the core promise before listing capabilities.
3. Why the harness matters — explain what stays put.
4. Request receipts — show that routing is observable rather than magical.
5. Remote topology and Islands — extend the same daemon beyond one terminal.
6. Install/operate — repeat the copyable command and first actions.
7. Candor — state policy dependence, ownership boundary, and non-affiliation before the close.

The order moves from belief → mechanism → evidence → operating shape → boundary. It deliberately avoids a hero/features/pricing template.

## Tokens

Declared once on `:root` in `llmux.html`; no palette literal appears anywhere else in the stylesheet.

- `--canvas: #f4efe3` — warm paper.
- `--canvas-raised: #fbf8f1` — ledger sheets, command surfaces.
- `--ink: #1a1814` — dark brown-black.
- `--ink-muted: #625d52` — utility labels, captions.
- `--rule: #cbc3b3` — hairlines and table borders.
- `--accent: #c3311d` — routing red: install-command rule, ledger arrows, list marks, focus ring.
- `--accent-pressed: #8a2416` — the pressed/hover value of the same accent, not a second accent.
- `--accent-ink: #ffffff` — text on accent.
- Space scale `--space-1 … --space-6` (0.5 / 0.75 / 1 / 1.5 / 2 / 4 rem); `--measure: 68ch`.
- Motion tokens `--dur-tap: 150ms`, `--dur-artifact: 300ms`, `--ease: ease-out`.

Computed contrast (WCAG 2.x relative luminance, not eyeballed):

| Pair | Ratio | Floor |
|---|---|---|
| `--ink` `#1a1814` on `--canvas` `#f4efe3` | **15.45:1** | ≥ 12:1 |
| `--ink-muted` `#625d52` on `--canvas` | 5.71:1 | ≥ 4.5:1 |
| `--accent` `#c3311d` on `--canvas` | 4.85:1 | ≥ 4.5:1 |
| `--accent-ink` `#ffffff` on `--accent` | 5.56:1 | ≥ 4.5:1 |

## Type roles

- Display: Iowan Old Style → Baskerville → Times New Roman. Job: thesis and editorial section statements.
- Body: Avenir Next → Avenir → system UI. Job: explanation and controls.
- Machine: SFMono-Regular → Consolas → Liberation Mono. Job: model names, requests, commands, and receipts.

No remote fonts or font requests. The hierarchy survives offline by construction.

## Motion

**Eight animated elements** — `.hero`, `.routing-ledger`, and six `.section-content` sections — all running the one `reveal-fade` keyframe. Measured page height at 1440×1000 is **4,317px** (browser-measured, `document.documentElement.scrollHeight`), so the density is **1.85 animated elements per 1,000px**: deliberately below the corpus working range of 5.0–15.8, because this is an operator page and the only motion is the first reveal.

Two durations only: `--dur-tap: 150ms` (link colour) and `--dur-artifact: 300ms` (declared for artifact state change). There is no route-state animation and no scripted tap feedback — an earlier draft claimed both; the page now ships **zero JavaScript**, so nothing on it can be motion the reader did not ask for.

`prefers-reduced-motion: reduce` disables animation and transition globally *and* lands `.hero`, `.routing-ledger`, and `.section-content` at `opacity: 1; transform: none`. Killing the animation alone would have left the whole page at its `opacity: 0` start state — that was a real defect in the first draft, and it is now also a validator check (`validate.py` reduced-motion trap).

## Claim ledger

Evidence root: `/Users/zhugehyuk/2lab.ai/llmux/`. Every row was re-read against the source at fix time; nothing on the page is asserted from memory.

| Page claim | Authoritative evidence |
|---|---|
| “Models change every month. Your harness shouldn't.” / harness-is-capital thesis | `README.md:3`, `:13`, `:22` |
| Local Anthropic-compatible proxy for Claude Code; `claude` talks to `localhost:3456` | `README.md:13` |
| Subagents, slash commands, MCP servers, hooks, and CLAUDE.md conventions stay put | `README.md:13` |
| One Rust binary: daemon, live TUI dashboard, login/import, updater, launcher | `README.md:15` |
| Four backend groups (Claude / Codex / Grok / OpenRouter) in one pool, routed by model name | `README.md:16`, `:91-96` |
| The five ledger signals `/model fable`, `/model opus[1m]`, `/model gpt-5.6-sol[1m]`, `/model grok-4.6`, `/model or-ox-alpha` | `README.md:83-89` (verbatim block) |
| Name pattern → backend-group mapping used in the ledger's right column | `README.md:91-96` |
| Multi-account quota-aware scheduling, 429 cooldown parking, Fable weekly ceilings | `README.md:17` |
| Activity feed prints one row per completed request; receipt field names (kind, model + effort, serving account, status, latency, tokens, API-equivalent cost, session-tagged input preview) | `docs/ai-debugger.md:12-16` |
| The four wire legs: Request → Upstream Req → Upstream Resp → Response; bodies/headers/SSE/rate-limit readable | `docs/ai-debugger.md:17-22` |
| Copy as `curl` reconstructs one side, credential values redacted | `docs/ai-debugger.md:23-25` |
| One central daemon; every other machine a pure client that never starts a local daemon and presents its own issued key | `README.md:19`, `docs/remote.md:3-7` |
| Clients are pointed at the daemon explicitly by `--remote host[:port]` or `remote.host` in `~/.config/llmux.json` (no discovery) | `docs/remote.md:9-13` |
| Per-machine multi-tenant client keys, metered per tenant, suspended/rotated independently | `README.md:19`, `docs/remote.md:23-27` |
| In remote mode `login` and `import` are refused — account mutation belongs to the daemon's host | `docs/remote.md:52` |
| Native macOS Islands companion; the KDE port is a source build, not a formula | `README.md:20`, `:36` |
| Stable Homebrew install command `brew install 2lab-ai/tap/llmux` | `README.md:26-28` |
| Rolling preview channel `brew install 2lab-ai/tap/llmux-preview` | `README.md:30-34` |
| Optional companion `brew install 2lab-ai/tap/llmux-islands` | `README.md:36-40` |
| `llmux login` (browser OAuth) and bare `llmux import` (supported local credential stores) | `README.md:53-59` |
| `llmux run` starts/reuses the daemon, then launches `claude` | `README.md:64-69` |
| `llmux server` is the foreground TUI dashboard | `README.md:71-75` |
| One human using their own accounts; no credential pooling, no resale | `README.md:127` |
| Third-party flat-rate subscription-token routing is vendor-policy-dependent, opt-in, keep an API-key fallback; quota-header behaviour may change | `README.md:129-131` |
| Not affiliated with Anthropic, OpenAI, xAI, or OpenRouter | `README.md:132` |
| MIT licence in the footer | `README.md:140-142` |

### Claims deleted in the final fix wave (no source existed)

| Removed claim | Why |
|---|---|
| `/model claude-opus`, `/model claude-sonnet`, `/model claude-haiku`, `/model gpt-4o`, `/model grok-3` as the ledger's signals | Not the documented signals; `README.md:83-89` lists five different literals. Replaced. |
| `llmux dashboard` presented as "the live dashboard in your terminal" | The README documents `llmux server` as the foreground TUI (`README.md:71-75`). `dashboard` exists in the CLI but attaches to an already-running daemon (`src/cli/mod.rs:99-100`), which is not what the page said it did. |
| `llmux import --account <email@example.com>` | No such flag: `ImportArgs` has only `--from` and `--json` (`src/cli/mod.rs:187-196`). |
| `brew tap 2lab-ai/tap` + `brew install llmux@preview` + `brew install llmux-islands` | Wrong formula names; the README ships fully-qualified `2lab-ai/tap/llmux-preview` and `2lab-ai/tap/llmux-islands`. |
| "Per-machine auth keys tied to hardware" | No hardware binding is documented anywhere; keys are issued values (`docs/remote.md:23-27`). |
| "Pure clients: zero shared secrets on client machines" | A client does hold a secret — its own `lmk-…` key (`docs/remote.md:23-27`). The accurate statement is that provider credentials stay in the daemon. |
| "Set your accounts once, and every Claude Code instance on the network knows how to reach the daemon" | Invented auto-discovery; remote mode is explicit configuration (`docs/remote.md:9-13`). |
| Receipt example with `req_024ac9c8f3e8a1b2`, `1240ms`, `342/156` tokens, a timestamp | Fabricated data presented as a captured request. Replaced by a field-name schema carrying a visible "illustrative shape — field names only, no captured request" tag plus a figcaption saying the same. |

## Stated deviation

composition-system.md §5 describes the copyable-command proof pattern as "mono surface, `$` prefix, copy button, real command". This page ships the mono surface, the `$` prefix, and the real command, but **no copy button**, because it ships no JavaScript at all — a clipboard button without script would be a control that does nothing. The command is selectable text. The load-bearing proof object (S4) is the routing ledger, not the command.

## Performance and accessibility receipts

- Standalone HTML; no build step, framework, external image, remote font, analytics, or widget. **Zero external requests, zero bytes of JavaScript.**
- File size: 18KB uncompressed (ceiling 250KB); no inline SVG; inline JS 0KB (ceiling 5KB).
- Exactly one `h1`, ordered headings, one `main`, `aria-labelledby` on every section, skip link first in tab order, `:focus-visible` outline on every interactive element.
- Interactive elements are the skip link and three footer links (padded, focus-visible). No CTA button is invented to satisfy the 44px rule; that rule governs primary interactions, and this page's primary action is a command you copy, not a button.
- Browser-measured, both pages served over loopback HTTP in headless Chromium: at 1440×1000 `scrollWidth == clientWidth == 1440`, height 4,317px; at 390×844 `scrollWidth == clientWidth == 390`, height 5,492px. No body horizontal overflow at either width.
- Reduced-motion and script-blocked renders both measured: 0 of 8 animated elements below `opacity: 0.99` in default, `reduce`, no-JS, `reduce`+no-JS, and both mobile cases.
- Font-block test is vacuously stable: all three stacks are local.
