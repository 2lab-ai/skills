# 2lab.ai Skills

Claude Code skills collection for autonomous task execution.

## Skills

### 🌐 scraping
General-purpose web scraping skill using [Scrapling](https://github.com/D4Vinci/Scrapling).
- Coupang product search & price comparison
- Pharmacy price scraping (Orthomol, etc.)
- Any website with anti-bot measures

### 📱 sns-scraping
Twitter/X and Threads timeline scraping with thread reconstruction.
- Twitter: 3-phase (profile scroll → Google search → individual fetch)
- Threads: 2-phase (profile scroll → individual fetch via og:description)
- Thread reconstruction with 1/N labeling
- Works without login

### 🎬 video-gen
Remotion-based video generation skill.
- Multi-scene composition (Hero, Chat, Code, Flow, Grid, List, Stat)
- TTS integration
- Configurable via JSON

### 🧭 landing-page — **the entrypoint for landing pages**
Start every landing/product/launch/founder page request here. It pins the target contract
(site, repo + path, route, framework, preserved behavior, delivery URL), picks the delivery
lane, and routes to a theme workflow.
- Lanes: **existing app** (built in the app's own stack, gated by the app's own build/lint/test)
  vs **standalone** (one self-contained HTML file, gated by the editorial validator)
- Theme routing: named theme → its workflow; **no theme named → `editorial-machine`, the default**;
  unregistered theme → stop and ask, never a silent substitution
- A live target this repo cannot reach is reported, not downgraded to a standalone file

### 📰 editorial-machine — the default theme
The theme workflow `landing-page` routes to when no theme is named: an editorial composition
grammar (warm-paper canvas, serif-led thesis, one authored proof object per product), synthesized
from char.com, anarlog.so, fastrepl.com, agentpub.dev, and johnjeong.com.
- Fact ledger → thesis + unique proof object → page brief → implementation → per-lane gates → browser QA
- Deterministic `scripts/validate.py` gate, **standalone lane only**
  (title/description/main/h1/skip link/install snippet/reduced-motion/overflow)
- Shares grammar, never a cloned DOM/template, across pages

## Installation

Most skills can be installed independently:

```bash
claude install-skill https://github.com/2lab-ai/skills/scraping
claude install-skill https://github.com/2lab-ai/skills/sns-scraping
claude install-skill https://github.com/2lab-ai/skills/video-gen
```

**Landing pages are the exception:** `landing-page` resolves its theme assets by relative path,
so the router and its themes must live in the **same skills directory**. Copy both directories
together — `cp -R landing-page editorial-machine ~/.claude/skills/` — or clone this repository
and point your skills directory at it. `landing-page` installed alone cannot build anything.

## Prerequisites

### scraping & sns-scraping
```bash
python3 -m venv ~/.scrapling-venv
~/.scrapling-venv/bin/pip install "scrapling[all]"
~/.scrapling-venv/bin/python3 -c "from scrapling.fetchers import StealthyFetcher; StealthyFetcher.setup()"

# Chromium deps (servers without root)
export LD_LIBRARY_PATH="$HOME/.local/lib/chromium-deps/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"
```

### video-gen
```bash
cd video-gen && npm install
```

## License

MIT
