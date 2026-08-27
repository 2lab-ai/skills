# xfx landing page brief

## Thesis

**Small enough to audit.** xfx is a deliberately bounded terminal coding agent whose omissions are part of the product contract, not future features disguised as stubs.

Audience: developers who want a useful agent loop they can inspect, constrain, and account for. Page job: explain the bounded loop and earn enough trust for the reader to install xfx.

## Unique proof object

A **bounded-loop field diagram** holds one turn constant and exposes each irreversible boundary:

`prompt → streamed answer → tool request → permission gate → local action → one terminal event`

The diagram is a vertical inspection record, not the horizontal provider-routing ledger used by the llmux example. Each row names the authority involved and the evidence left behind. The capability boundary appears in the same visual language: eight shipped tools and six shell commands are printed beside named absences.

## Section order and reason

1. Field-manual masthead and thesis.
2. Bounded-loop proof object — show the control boundary before listing capabilities.
3. Capability manifest — what exists and what does not, side by side.
4. Permission modes — because local execution risk is the first operational question.
5. Session and diagnostics record — show what remains inspectable after a turn.
6. llmux backend — only after the agent loop is understood.
7. Install and run — the ask follows the proof.
8. Safety/non-goals — the boundary is a full section, never footnote copy.

This is intentionally unlike the llmux page: field-sheet rather than essay, vertical process rather than routing lanes, safety green rather than routing red, system/mono typography rather than display-led broadsheet, and a capability boundary before install.

## Tokens and typography

- `--canvas: #f3f4f0` — cool paper gray, distinct from llmux's warm paper.
- `--canvas-raised: #fafbf8`
- `--ink: #101613`
- `--ink-muted: #4a554e`
- `--rule: #c8cec8`
- `--accent: #1f6b3d` — safety green, used only for status, primary install action, and one diagram line.
- `--accent-ink: #ffffff`
- Computed `#101613` on `#f3f4f0`: approximately **16.6:1**, above the 12:1 house floor.
- Display: `Iowan Old Style`, `Palatino Linotype`, Palatino, serif — reserved for thesis and section heads.
- Body: `-apple-system`, BlinkMacSystemFont, `Segoe UI`, sans-serif — factual reading copy.
- Utility: `ui-monospace`, `SFMono-Regular`, Menlo, Consolas, monospace — every command, status, boundary, and field label.
- No remote fonts; the page has zero font-origin requests and survives offline unchanged.

## Motion

Two durations only: `150ms` interaction feedback and `300ms` artifact reveal. Eight reveal targets are authored; the exact density depends on browser-measured final page height and belongs in Task 5 receipts. Reduced-motion removes transforms and transitions while preserving every state.

## Claim ledger

| Page claim | Authoritative source |
|---|---|
| xfx is an unofficial experimental Rust port of `vercel-labs/fx`, not affiliated with Vercel | `/Users/zhugehyuk/2lab.ai/xfx/README.md:1-4` |
| It streams answers through Vercel AI Gateway or local llmux and may read/change files and run a bounded command set | `README.md:6-10` |
| v0.1 is a behavioral port of the load-bearing loop, not full parity | `README.md:12-19` |
| The binary/profile/project names are isolated from upstream fx | `README.md:21-23` |
| Supported status is experimental; Linux/macOS, x86_64/aarch64, no Windows | `README.md:25-39` |
| `ask` runs one bounded multi-step turn and emits exactly one terminal event; `--json` is JSONL | `README.md:42-47` |
| Bare xfx is a line-oriented shell with six commands and preserves scrollback | `README.md:46-47` |
| Eight shipped tools are `list_files`, `glob_files`, `grep_files`, `read_file`, `write_file`, `edit_file`, `create_folder`, `terminal` | `README.md:48-48` |
| Permission modes are ask, auto, and yolo | `README.md:49-49` |
| Sessions are append-only under `~/.xfx/sessions/<id>/`, resumable, and `--no-save` writes nothing | `README.md:50-50` |
| AGENTS.md context is bounded and refreshed every turn | `README.md:51-51` |
| `status` and `doctor` work without credentials and without creating anything | `README.md:52-52` |
| Named absences error rather than quietly no-op | `README.md:54-68` |
| No OS sandbox; permission modes govern what starts, not what a child process can do | `README.md:72-79` |
| ask requires a real terminal for every change/command and fails closed in pipes/CI | `README.md:80-82` |
| auto admits bounded reversible writes and a narrow reporting command grammar | `README.md:83-87` |
| yolo skips checks and warns on stderr | `README.md:88-89` |
| Approvals are scoped by tool, absolute target, and session | `README.md:90-93` |
| Tool-returned file contents and command output are stored verbatim in owner-only plaintext session logs; use `--no-save` when needed | `README.md:94-102` |
| File tools structurally refuse `.git` and `.xfx` in every mode | `README.md:103-105` |
| Stable Homebrew install command is `brew install 2lab-ai/tap/xfx` | `README.md:107-120` |
| Preview install is `brew install 2lab-ai/tap/xfx-preview` | `README.md:127-143` |
| Full gate and native smoke evidence are documented | `README.md:199-226` |
| xfx config precedence and five consumed keys are explicit | `README.md:272-288` |
| Two backends exist: Gateway and local llmux | `README.md:290-301` |
| `xfx setup llmux` probes loopback llmux and records the selected backend/model | `README.md:297-311` |
| llmux backend is keyless loopback only; remote hosts are refused | `README.md:313-324` |
| Runtime data flow is cli → config → agent → tools/permission → session → output | `README.md:326-333` |
| Advertisement requires handler, test, and implemented ledger row in the same change | `README.md:348-353` |

## Performance and accessibility notes

Standalone HTML, no framework, script CDN, external image, webfont, analytics, or widget. All diagrams are authored HTML. Wide command rows scroll locally, never the body. One main, one h1, ordered headings, skip link, visible focus, 44px primary actions, text-reachable proof object, and reduced-motion fallback are required. Task 5 must record final bytes, requests, desktop/mobile scroll widths, focus order, and screenshots.