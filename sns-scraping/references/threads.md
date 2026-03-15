# Threads (threads.com) Scraping Playbook

## Architecture

Threads is a Meta/Instagram text-based social platform. It's a React SPA with no public API. Works without login for public profiles.

### What Works Without Login

| Resource | Accessible | Notes |
|----------|-----------|-------|
| Profile page (`/@username`) | ✅ | Shows recent posts, limited scroll depth |
| Individual posts (`/@username/post/ID`) | ✅ | Full text via og:description meta tag |
| Search | ❌ | Requires login |
| Replies | ❌ | Limited without login |

## DOM Structure (as of 2026-03)

Threads does NOT use `<article>` tags like Twitter. Key differences:

- **No `data-testid` attributes** — Must use other selectors
- **Post links:** `/@username/post/{shortcode}` format (Instagram-like shortcodes)
- **Time elements:** Standard `<time datetime="ISO">display</time>`
- **Text:** In `<span>` elements with class-based styling (hashed CSS modules)
- **og:description meta tag** has the full post text (most reliable extraction method)

### Post Link Pattern

```
/@username/post/DV5GQKXiSLn     ← Post shortcode (Base64-like)
/@username/post/DV5GQKXiSLn/media  ← Media attachment (skip these)
```

### Text Extraction Strategy

**Best method: og:description meta tag** (works on individual post pages)

```python
meta_desc = re.search(
    r'<meta[^>]*property="og:description"[^>]*content="([^"]*)"',
    html
)
text = meta_desc.group(1) if meta_desc else ""
# Decode HTML entities
text = text.replace('&gt;', '>').replace('&lt;', '<')
text = text.replace('&amp;', '&').replace('&#x27;', "'")
```

**Alternative: span elements** (on profile page, less reliable)

```python
spans = re.findall(r'<span[^>]*>([^<]{15,})</span>', html)
# Filter out UI text (Follow, Reply, Like, etc.)
```

### Date Extraction

```python
times = re.findall(r'<time[^>]*datetime="([^"]+)"', html)
# ISO format: 2026-03-15T04:45:00.000Z
```

## Profile Page Scrolling

### Behavior

- Profile loads with ~10-15 posts initially
- Scrolling loads more, but limited depth
- No login wall (unlike Twitter), but simply stops loading more posts
- Viewport height matters — use `4000` for more initial content
- Maximum ~30-40 posts visible without login

### Post ID Collection

```python
post_links = re.findall(
    r'href="/@{username}/post/([A-Za-z0-9_-]+)"',
    html
)
# Deduplicate (same post appears in multiple link elements)
unique_ids = list(dict.fromkeys(post_links))
```

### Scroll Code

```python
all_post_ids = OrderedDict()
for scroll_i in range(max_scrolls):
    html = await page.content()
    links = re.findall(r'href="/@username/post/([A-Za-z0-9_-]+)"', html)
    for pid in links:
        if pid not in all_post_ids:
            all_post_ids[pid] = True

    await page.evaluate("window.scrollBy(0, 2000)")
    await asyncio.sleep(2)
```

## Individual Post Fetching

### Strategy

Visit each post URL individually to get full text via og:description.

```python
url = f"https://www.threads.com/@{username}/post/{post_id}"
await page.goto(url, wait_until="domcontentloaded", timeout=30000)
await asyncio.sleep(5)  # Threads is slow to hydrate

html = await page.content()

# Extract from meta tags (most reliable)
meta_desc = re.search(
    r'<meta[^>]*property="og:description"[^>]*content="([^"]*)"', html
)
```

### Timeout Handling

Threads pages sometimes timeout on `networkidle`. Use `domcontentloaded` with explicit sleep:

```python
# BAD: often times out
await page.goto(url, wait_until="networkidle", timeout=20000)

# GOOD: more reliable
await page.goto(url, wait_until="domcontentloaded", timeout=30000)
await asyncio.sleep(5)
```

### Rate Limiting

- 1-1.5s delay between fetches
- Some posts may timeout; retry once with domcontentloaded
- No 429 responses observed, but occasional timeouts

## Thread Detection

### Pattern

Threads uses the same self-reply mechanism as Twitter. Threads are sequences of posts by the same user posted within minutes.

**Detection signals:**
1. Same author, same minute (or within 1-2 minutes)
2. Post shortcodes are sequentially close (not always reliable)
3. Content continuity (same topic, numbered, "Thread 1/N")

### Grouping Algorithm

```python
# Sort by datetime
# Group posts with < 2 minute gap
# Label as thread 1/N, 2/N, etc.
```

### Observed Thread Patterns (from @zhugehyuk)

| Thread | Posts | Topic |
|--------|-------|-------|
| MiroFish | 4 posts | 20살 대학생의 ABM 시뮬레이터 |
| 개 암 mRNA 백신 | 4 posts | Paul Conyngham, ChatGPT + AlphaFold |
| 쿠팡 스크래핑 | 4 posts | Scrapling 스킬, 쿠팡 검색 |
| Symphony 실패 | 2 posts | OpenAI Symphony 실험 |
| 임베딩 유사도 | 2 posts | 지금/now/հիմা 벡터 공간 |
| Claude Shannon | 2 posts | 창의적 사고 1952년 |

## Google Search for Discovery

Threads posts are poorly indexed by Google. Limited effectiveness:

```
site:threads.com/@username
```

Returns very few results. Profile page scrolling + individual fetch is the primary strategy.

## Known Limitations

1. **Scroll depth limited** — ~30-40 posts max without login
2. **Google indexing poor** — Can't rely on search for comprehensive discovery
3. **No public API** — All data via HTML scraping
4. **Slow hydration** — Pages need 3-5s after domcontentloaded to populate
5. **og:description truncation** — Very long posts may be truncated in meta tag
6. **Media-only posts** — Posts with only images have empty og:description

## Comparison with Twitter/X

| Feature | Twitter/X | Threads |
|---------|-----------|---------|
| Profile scroll depth | 50-100+ | 30-40 |
| Individual post access | ✅ Full text | ✅ Via og:description |
| Google indexing | Good | Poor |
| Login wall | After ~6 scrolls | No wall, just stops loading |
| DOM stability | data-testid (stable) | CSS classes (unstable) |
| Text extraction | tweetText div | og:description meta |
| Thread detection | Reply metadata | Time proximity heuristic |
| Rate limiting | Moderate | Light |
