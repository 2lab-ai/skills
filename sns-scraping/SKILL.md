---
name: sns-scrape
description: >
  SNS thread scraping and timeline extraction skill for Twitter/X and Threads.
  Use this skill when the user wants to scrape someone's Twitter/X timeline,
  Threads posts, collect posts from a specific period, reconstruct threads
  (1/N, 2/N style), search for a person's recent posts on social media,
  or extract and organize social media content by date. Also trigger when
  the user mentions "트위터 긁어", "트윗 모아", "타임라인", "스레드 정리",
  "쓰레드 긁어", "threads.com", or any task involving fetching tweets,
  threads posts, or social media content.
---

# SNS Thread Scraping Skill

## Overview

Scrape Twitter/X and Threads profiles to collect posts over a specified time range, reconstruct threads, and present them organized by date. Works **without login** using a multi-strategy approach.

## Prerequisites

```bash
# Python venv with scrapling
VENV=~/.scrapling-venv
$VENV/bin/python3 -c "from scrapling.fetchers import StealthyFetcher; print('OK')"

# Chromium deps (headless)
export LD_LIBRARY_PATH="$HOME/.local/lib/chromium-deps/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"
```

## Core Strategy: 3-Phase Collection

Twitter's anti-bot measures require a multi-phase approach. **Never rely on a single method.**

### Phase 1: Profile Page Scroll (Quick Scan)

Scrape the user's profile page with patchright (playwright fork) and scroll to collect visible tweets.

**Limitations:**
- Non-logged-in profiles show limited tweets (often <100)
- Tweets are NOT purely chronological — mixed with popular/pinned
- Pinned tweets have old dates; filter them out
- Login walls block infinite scroll after ~6 scrolls

**Use for:** Quick overview, finding recent tweet IDs, checking if user is active.

```python
# See scripts/twitter_profile_scroll.py
from patchright.async_api import async_playwright
# Navigate to https://x.com/{username}
# Wait for article elements
# Scroll and collect
```

### Phase 2: Google Search Discovery (ID Collection)

Use web search to find tweet IDs that the profile page doesn't show.

**Strategy:**
```
site:x.com/{username}/status {year}
site:x.com/{username}/status {month} {year}
"{username}" site:x.com/{username}/status {topic}
```

**Why this works:** Google indexes tweets that Twitter's non-logged-in profile doesn't display. This is the KEY strategy for comprehensive collection.

**Use for:** Finding ALL tweets in a date range, especially recent ones hidden by Twitter's non-logged-in view.

### Phase 3: Individual Tweet Fetch (Full Text)

Visit each tweet URL directly to get the complete text.

**Why individual pages:** Non-logged-in users CAN see individual tweet pages with full text, even when the profile timeline is restricted.

```python
# Navigate to https://x.com/{username}/status/{id}
# Extract: data-testid="tweetText" → full text
# Extract: time[datetime] → ISO date
# Check: reply chain for thread reconstruction
```

## Tweet Parsing Patterns

### Text Extraction
```python
import re

# From page HTML:
text_blocks = re.findall(
    r'data-testid="tweetText"[^>]*>(.*?)</div>', html, re.DOTALL
)
for block in text_blocks:
    text = re.sub(r'<[^>]+>', ' ', block).strip()
    text = re.sub(r'\s+', ' ', text)
    # Decode HTML entities
    text = text.replace('&gt;', '>').replace('&lt;', '<')
    text = text.replace('&amp;', '&').replace('&#x27;', "'")
```

### Date Extraction
```python
# ISO datetime from time elements
times = re.findall(r'<time[^>]*datetime="([^"]+)"', html)
# First time element = tweet's own date
# Second time element (if exists) = quoted tweet's date
```

### Status ID & Link
```python
links = re.findall(r'href="(/{username}/status/(\d+))"', html)
# Filter out /analytics and /photo links
```

### Pinned Tweet Detection
```python
is_pinned = 'Pinned' in article_html[:1000] and 'socialContext' in article_html[:1000]
```

### Reply Detection
```python
is_reply = bool(re.search(r'Replying to', html[:5000]))
```

## Thread Reconstruction

Threads are sequences of self-replies by the same user. To reconstruct:

1. **Collect all tweets** from the user in the time range
2. **Identify reply chains:** tweets that are replies to the same user's other tweets
3. **Group by root tweet:** find the first non-reply tweet, then chain all self-replies
4. **Order within thread:** sort by date ascending
5. **Label:** 1/N, 2/N, ... N/N

**Detection signals:**
- Tweet is a reply to another tweet by the same user
- Multiple tweets posted within minutes of each other
- Topic continuity (same subject)
- Explicit markers: "Thread:", "🧵", "1/", numbers

## Execution Workflow

When the user asks to scrape someone's Twitter:

```
1. IDENTIFY: username, date range, any topic filter
2. PHASE 1: Scroll profile page → collect visible tweet IDs + texts
3. PHASE 2: Google search → find missing tweet IDs
4. MERGE: Deduplicate by status ID
5. PHASE 3: Fetch full text for each tweet individually
6. FILTER: Apply date range cutoff
7. THREADS: Reconstruct thread chains
8. FORMAT: Present by date, threads connected with 1/N labels
```

## Environment Setup

```bash
# Required env var for Chromium headless
export LD_LIBRARY_PATH="$HOME/.local/lib/chromium-deps/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"

# Python interpreter
PYTHON="$HOME/.scrapling-venv/bin/python3"
```

## Error Recovery

| Error | Cause | Fix |
|-------|-------|-----|
| `libnspr4.so not found` | Chromium missing shared libs | Set `LD_LIBRARY_PATH` to `~/.local/lib/chromium-deps/...` |
| 403 on profile | Rate limited or geo-blocked | Wait 30s, retry with different user-agent |
| Empty tweetText | Twitter changed DOM structure | Check for `data-testid` variations, try `span` extraction |
| Login wall on search | Search requires auth | Fall back to Google search (Phase 2) |
| 0 tweets in date range | User inactive or tweets hidden | Expand Google search with topic keywords |
| `bad marshal data` | Corrupt .pyc cache | `find ~/.scrapling-venv -name "*.pyc" -delete` |

## Output Format

Present results as:

```markdown
## 📅 YYYY-MM-DD (요일)

**제목/한줄 요약**
> Full tweet text here...

🔗 [link](https://x.com/username/status/ID)

---

## 📅 YYYY-MM-DD — Thread (1/3)
> First tweet of thread...

## 📅 YYYY-MM-DD — Thread (2/3)
> Continuation...

## 📅 YYYY-MM-DD — Thread (3/3)
> Final tweet...
```

## Threads (threads.com) Support

### Strategy: 2-Phase Collection

Threads has simpler anti-bot than Twitter. No Google search phase needed.

```
1. IDENTIFY: username, date range
2. PHASE 1: Scroll profile → collect post IDs (/@username/post/SHORTCODE)
3. PHASE 2: Visit each post page → extract text from og:description meta tag
4. FILTER: Apply date range
5. THREADS: Group posts within 2-min windows as thread chains
6. FORMAT: Present by date with 1/N labels
```

### Threads Text Extraction

**Use og:description meta tag** (most reliable on individual post pages):

```python
meta_desc = re.search(
    r'<meta[^>]*property="og:description"[^>]*content="([^"]*)"',
    html
)
text = meta_desc.group(1) if meta_desc else ""
```

### Threads-Specific Notes

- No login wall, but scroll depth limited to ~30-40 posts
- Use `wait_until="domcontentloaded"` (not `networkidle`) — Threads is slow to hydrate
- Add 4-5s explicit sleep after page load
- Post shortcodes are Base64-like strings (e.g., `DV5GQKXiSLn`)
- Thread detection: posts by same user within 2 minutes are grouped
- Google indexing of Threads is poor — can't rely on search for discovery

### See Also

- `references/threads.md` — Full Threads DOM patterns and extraction guide
- `scripts/threads_scrape.py` — CLI scraper for Threads

## Supported Platforms

| Platform | Status | Strategy |
|----------|--------|----------|
| Twitter/X | ✅ Full support | Profile scroll + Google search + Individual fetch |
| Threads | ✅ Full support | Profile scroll + Individual fetch (og:description) |
| Instagram | 🚧 Planned | Login required for most content |
| Bluesky | 🚧 Planned | Open API available |
