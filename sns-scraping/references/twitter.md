# Twitter/X Scraping Playbook

## Architecture

Twitter (x.com) is a React SPA with aggressive anti-bot protection. Content is rendered client-side via JavaScript. Static HTTP fetchers (curl, requests) get empty shells.

### What Works Without Login

| Resource | Accessible | Notes |
|----------|-----------|-------|
| Profile page (`/username`) | ✅ Partial | Shows ~50-100 tweets, mixed order, login wall after scrolling |
| Individual tweets (`/username/status/ID`) | ✅ Full | Full text visible, including long posts |
| Search (`/search?q=...`) | ❌ | Redirects to login |
| Lists | ❌ | Requires auth |
| Replies tab | ❌ | Limited without login |

### DOM Structure (as of 2026-03)

Twitter uses CSS Modules with hashed class names. **Never rely on class names.** Use `data-testid` attributes instead.

```
article[role="article"]          → Tweet container
  [data-testid="tweetText"]      → Tweet text content
  time[datetime]                 → ISO timestamp
  a[href*="/status/"]            → Status link
  [data-testid="socialContext"]  → "Pinned", "Retweeted", etc.
  [data-testid="Tweet-User-Avatar"]  → User avatar
  [data-testid="tweet-text-show-more-link"]  → Expand long text
```

### Tweet Text Extraction

The `tweetText` div contains nested spans with individual characters/words. Extract by stripping all HTML tags:

```python
text_blocks = re.findall(
    r'data-testid="tweetText"[^>]*>(.*?)</div>',
    html, re.DOTALL
)
text = re.sub(r'<[^>]+>', ' ', text_blocks[0]).strip()
text = re.sub(r'\s+', ' ', text)
```

**HTML entities to decode:**
- `&gt;` → `>`
- `&lt;` → `<`
- `&amp;` → `&`
- `&#x27;` → `'`
- `&quot;` → `"`

### Multiple tweetText Blocks

When visiting a single tweet page, you may get multiple `tweetText` blocks:
- **Block 0:** The main tweet text
- **Block 1:** Quoted tweet text (if quote-tweeting)
- **Block 2+:** Reply chain tweets below

### Date Parsing

```python
# ISO format: 2026-03-07T19:53:00.000Z
times = re.findall(r'<time[^>]*datetime="([^"]+)"', html)
dt = datetime.fromisoformat(times[0].replace('Z', '+00:00'))
```

Multiple `time` elements in an article:
- First: tweet's own timestamp
- Second: quoted tweet's timestamp (if quote tweet)

## Profile Page Scrolling

### Browser Setup

```python
from patchright.async_api import async_playwright

browser = await p.chromium.launch(headless=True)
context = await browser.new_context(
    viewport={"width": 1920, "height": 4000},  # Tall viewport = more initial content
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
               "AppleWebKit/537.36 (KHTML, like Gecko) "
               "Chrome/131.0.0.0 Safari/537.36"
)
```

### Scroll Strategy

```python
for scroll_i in range(max_scrolls):
    html = await page.content()
    # Parse articles...

    # Aggressive scroll
    await page.evaluate("window.scrollBy(0, 5000)")
    await asyncio.sleep(2.5)

    # Check for login wall
    login_block = await page.query_selector('[data-testid="LoginForm"]')
    if login_block:
        break
```

### Known Issues

1. **Pinned tweets have old dates** — Always filter by `is_pinned` flag
2. **Tweets are NOT chronological** — Twitter shows a mix of popular + recent
3. **Login wall** — Appears after ~6 scrolls, blocks further content
4. **Profile may show 0 recent tweets** — Use Google search (Phase 2) to compensate

## Google Search Strategy

The most reliable way to find tweet IDs for a specific period:

### Search Queries

```
# Basic: all tweets from user in a year
site:x.com/{username}/status {year}

# Specific month
site:x.com/{username}/status {month_name} {year}

# Topic-filtered
"{username}" site:x.com/{username}/status {topic} {year}

# With date restriction (Google tools)
site:x.com/{username}/status after:{YYYY-MM-DD} before:{YYYY-MM-DD}
```

### Extracting Tweet IDs from Search Results

Google results contain URLs like `https://x.com/karpathy/status/2030371219518931079`. Extract the numeric ID.

### Why Google Works Better

- Google indexes tweets that Twitter's non-logged-in profile doesn't show
- Google's cache captures tweets even if user deletes them
- Google results include tweet title text for quick filtering

## Individual Tweet Fetching

### Full Text Access

Individual tweet pages (`/username/status/ID`) show complete text without login.

```python
await page.goto(f"https://x.com/{username}/status/{tweet_id}",
                wait_until="networkidle", timeout=20000)
await asyncio.sleep(2)

# Click "Show more" for long posts
try:
    show_more = await page.query_selector(
        '[data-testid="tweet-text-show-more-link"]'
    )
    if show_more:
        await show_more.click()
        await asyncio.sleep(1)
except:
    pass
```

### Rate Limiting

- Add 0.8-1.5s delay between fetches
- Twitter may return 429 after ~50 rapid requests
- If rate limited, wait 30s and resume

## Thread Detection

### Self-Reply Pattern

A thread is a chain of tweets where the user replies to their own previous tweet.

**Signals:**
1. Reply indicator: `Replying to @{same_username}`
2. Temporal proximity: tweets posted within minutes
3. Explicit markers: "Thread:", "🧵", "1/N", "2/N"
4. Topical continuity

### Reconstruction Algorithm

```python
def reconstruct_threads(tweets):
    """Group tweets into threads based on self-reply chains."""
    threads = {}
    standalone = []

    for tweet in sorted(tweets, key=lambda t: t['date']):
        if tweet['is_reply'] and tweet['reply_to'] == username:
            # Find which thread this belongs to
            # Check if it replies to a known tweet ID
            parent_id = tweet.get('in_reply_to_status_id')
            if parent_id in threads:
                threads[parent_id].append(tweet)
            else:
                # Start new thread group
                threads[tweet['id']] = [tweet]
        else:
            standalone.append(tweet)

    return standalone, threads
```

### Practical Approach

Since non-logged-in view doesn't always show reply metadata, use heuristics:
1. Same user, same day, posted within 10 minutes of each other
2. Check if the tweet page shows "Replying to @self"
3. Group by topic similarity

## Known Limitations

1. **Cannot get 100% of tweets** without login — some will be missed
2. **Google indexing lag** — Very recent tweets (< 24h) may not be indexed
3. **Rate limits** — Both Twitter and Google have rate limits
4. **DOM changes** — Twitter frequently updates its DOM; `data-testid` attributes are the most stable selectors
5. **Long posts** — X Premium posts can be very long; may need "Show more" click
6. **Media-only tweets** — Tweets with only images/video and no text will have empty tweetText

## Tested Accounts (2026-03)

| Account | Result | Notes |
|---------|--------|-------|
| @karpathy | ✅ 17+ tweets/month | Active poster, long threads, mix of original + quotes |
| Profiles with few tweets | ✅ | Easier — profile page may show all |
| Protected accounts | ❌ | Cannot access without following |
| Suspended accounts | ❌ | 404 |
