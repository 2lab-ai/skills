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

### 📰 editorial-machine
Builds a standalone product/founder landing page in an editorial composition grammar
(warm-paper canvas, serif-led thesis, one authored proof object per product), synthesized
from char.com, anarlog.so, fastrepl.com, agentpub.dev, and johnjeong.com.
- Fact ledger → thesis + unique proof object → page brief → implementation → validator → browser QA
- Deterministic `scripts/validate.py` gate (title/description/main/h1/skip link/install snippet/reduced-motion/overflow)
- Shares grammar, never a cloned DOM/template, across pages

## Installation

Each skill can be installed independently:

```bash
claude install-skill https://github.com/2lab-ai/skills/scraping
claude install-skill https://github.com/2lab-ai/skills/sns-scraping
claude install-skill https://github.com/2lab-ai/skills/video-gen
claude install-skill https://github.com/2lab-ai/skills/editorial-machine
```

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
