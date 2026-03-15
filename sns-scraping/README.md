# sns-scraping

Claude Code skill for scraping Twitter/X and Threads timelines and reconstructing threads.

## What it does

Given a Twitter/X or Threads username and date range, this skill:

1. **Scrolls** the profile page to collect visible post IDs
2. **Searches** Google for IDs not shown on the profile (Twitter only)
3. **Fetches** individual post pages for full text
4. **Reconstructs** threads (self-reply chains → 1/N, 2/N labels)
5. **Presents** everything organized by date

Works **without login** using headless Chromium (patchright/playwright).

## As a Claude Code Skill

```bash
claude install-skill https://github.com/2lab-ai/sns-scraping
```

Then just ask:
- "카파시 트위터 최근 1개월 긁어줘"
- "Scrape @elonmusk's last week of tweets"
- "쓰레드에서 @zhugehyuk 3개월치 긁어줘"
- "Find Karpathy's autoresearch thread"

## Prerequisites

```bash
# Python venv with scrapling
python3 -m venv ~/.scrapling-venv
~/.scrapling-venv/bin/pip install "scrapling[all]"

# Chromium headless browser
~/.scrapling-venv/bin/python3 -c "from scrapling.fetchers import StealthyFetcher; StealthyFetcher.setup()"
```

### Servers without root (Chromium deps)

If Chromium fails with `libnspr4.so not found`, install shared libs manually:

```bash
apt download libnspr4 libnss3 libatk1.0-0 libatk-bridge2.0-0 \
  libcups2 libdrm2 libxkbcommon0 libatspi2.0-0 libxcomposite1 \
  libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2

for f in *.deb; do dpkg-deb -x "$f" ~/.local/lib/chromium-deps/; done

export LD_LIBRARY_PATH="$HOME/.local/lib/chromium-deps/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"
```

## Scripts

### `scripts/twitter_scrape.py` — Twitter/X

```bash
export LD_LIBRARY_PATH="$HOME/.local/lib/chromium-deps/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"
~/.scrapling-venv/bin/python3 scripts/twitter_scrape.py karpathy \
  --days 30 \
  --output tweets.json \
  --markdown timeline.md
```

### `scripts/threads_scrape.py` — Threads

```bash
export LD_LIBRARY_PATH="$HOME/.local/lib/chromium-deps/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"
~/.scrapling-venv/bin/python3 scripts/threads_scrape.py zhugehyuk \
  --days 90 \
  --output posts.json \
  --markdown timeline.md
```

### Options (both scripts)

- `--days N` — Look back N days (Twitter default: 30, Threads default: 90)
- `--output FILE` — Save results as JSON
- `--markdown FILE` — Save results as Markdown
- `--extra-ids ID1 ID2...` — Additional post IDs to fetch

## Structure

```
sns-scraping/
├── SKILL.md               # Skill definition (Anthropic skill-creator format)
├── README.md              # This file
├── references/
│   ├── twitter.md         # Twitter/X scraping playbook & DOM patterns
│   └── threads.md         # Threads scraping playbook & DOM patterns
├── scripts/
│   ├── twitter_scrape.py  # Twitter/X scraper
│   └── threads_scrape.py  # Threads scraper
├── evals/
│   └── evals.json         # Test cases
└── .gitignore
```

## How it works

### Twitter/X (3-Phase Strategy)

| Phase | Method | Gets you |
|-------|--------|----------|
| 1 | Profile page scroll | 50-100 visible tweets (mixed chronological + popular) |
| 2 | Google `site:x.com/user/status` search | Tweet IDs hidden from non-logged-in profile |
| 3 | Individual tweet page visit | Full text for each tweet |

**Key insight:** Twitter's non-logged-in profile shows limited, non-chronological tweets. But individual tweet pages (`/status/ID`) show full text without login. Google indexes tweets that the profile page hides.

### Threads (2-Phase Strategy)

| Phase | Method | Gets you |
|-------|--------|----------|
| 1 | Profile page scroll | 30-40 post IDs (chronological) |
| 2 | Individual post page visit | Full text via `og:description` meta tag |

**Key insight:** Threads has no login wall but limits scroll depth to ~30-40 posts. Individual post pages reliably serve full text in the `og:description` meta tag. Thread detection uses 2-minute temporal proximity grouping.

## License

MIT
