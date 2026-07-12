"""Patchright-based X/Twitter search — no API keys needed.

Strategy: DuckDuckGo search for site:x.com tweets, then scrape individual tweet pages.
X search requires login, Google has CAPTCHA, DDG works reliably.
"""

import asyncio
import re
import sys
import urllib.parse
from typing import Any, Dict, List, Optional


def _log(msg: str):
    sys.stderr.write(f"[patchright_x] {msg}\n")
    sys.stderr.flush()


DEPTH_CONFIG = {
    "quick": 10,
    "default": 25,
    "deep": 50,
}


def _find_chromium() -> Optional[str]:
    """Find a working chromium binary."""
    import shutil
    for candidate in [
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
        "/usr/bin/google-chrome",
    ]:
        if shutil.which(candidate):
            return candidate
    return None


def _parse_metric(s: str) -> int:
    """Parse engagement metric string like '1.2K' to int."""
    s = s.strip().upper()
    multiplier = 1
    if s.endswith("K"):
        multiplier = 1000
        s = s[:-1]
    elif s.endswith("M"):
        multiplier = 1000000
        s = s[:-1]
    elif s.endswith("B"):
        multiplier = 1000000000
        s = s[:-1]
    try:
        return int(float(s) * multiplier)
    except ValueError:
        return 0


async def _ddg_find_tweets(
    query: str,
    from_date: str,
    to_date: str,
    max_results: int = 25,
) -> List[str]:
    """Use DuckDuckGo HTML to find X/Twitter tweet URLs for a topic.

    DDG doesn't have CAPTCHA issues like Google.
    Returns list of tweet URLs (https://x.com/user/status/ID).
    """
    from patchright.async_api import async_playwright

    # DDG HTML search — reliable, no CAPTCHA
    year = from_date[:4]
    search_q = urllib.parse.quote(f"site:x.com {query} {year}")
    ddg_url = f"https://html.duckduckgo.com/html/?q={search_q}"

    _log(f"DDG search: site:x.com {query}")

    chromium_path = _find_chromium()
    tweet_urls = []

    async with async_playwright() as p:
        launch_kwargs = {"headless": True}
        if chromium_path:
            launch_kwargs["executable_path"] = chromium_path

        browser = await p.chromium.launch(**launch_kwargs)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()

        try:
            await page.goto(ddg_url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(3000)

            seen = set()
            # Blacklist handles that are bots or irrelevant
            blacklist = {"i", "search", "intent", "hashtag", "grok"}

            # DDG HTML results have class "result__a"
            result_links = await page.query_selector_all("a.result__a")
            for link in result_links:
                try:
                    href = await link.get_attribute("href")
                    if not href:
                        continue
                    # DDG wraps URLs: //duckduckgo.com/l/?uddg=https%3A%2F%2Fx.com%2F...
                    decoded = urllib.parse.unquote(href)
                    m = re.search(r'https?://(?:x\.com|twitter\.com)/(\w+)/status/(\d+)', decoded)
                    if m and m.group(1).lower() not in blacklist:
                        url = f"https://x.com/{m.group(1)}/status/{m.group(2)}"
                        if url not in seen:
                            seen.add(url)
                            tweet_urls.append(url)
                except Exception:
                    continue

            # Try next page if needed
            if len(tweet_urls) < max_results:
                try:
                    next_btn = await page.query_selector('input[value="Next"]')
                    if next_btn:
                        await next_btn.click()
                        await page.wait_for_timeout(3000)
                        result_links = await page.query_selector_all("a.result__a")
                        for link in result_links:
                            try:
                                href = await link.get_attribute("href")
                                if not href:
                                    continue
                                decoded = urllib.parse.unquote(href)
                                m = re.search(r'https?://(?:x\.com|twitter\.com)/(\w+)/status/(\d+)', decoded)
                                if m and m.group(1).lower() not in blacklist:
                                    url = f"https://x.com/{m.group(1)}/status/{m.group(2)}"
                                    if url not in seen:
                                        seen.add(url)
                                        tweet_urls.append(url)
                            except Exception:
                                continue
                except Exception:
                    pass

        except Exception as e:
            _log(f"DDG search error: {e}")
        finally:
            await browser.close()

    _log(f"Found {len(tweet_urls)} tweet URLs from DDG")
    return tweet_urls[:max_results]


async def _scrape_tweet_page(page, url: str) -> Optional[Dict[str, Any]]:
    """Scrape a single tweet page for text, author, date, engagement."""
    try:
        await page.goto(url, wait_until="networkidle", timeout=20000)
        await page.wait_for_timeout(3000)

        # Get tweet text
        text_el = await page.query_selector('article[data-testid="tweet"] [data-testid="tweetText"]')
        if not text_el:
            return None
        text = await text_el.inner_text()
        if not text or len(text.strip()) < 5:
            return None

        # Get author
        m = re.search(r'x\.com/(\w+)/status/(\d+)', url)
        author = m.group(1) if m else "unknown"

        # Get date
        article = await page.query_selector('article[data-testid="tweet"]')
        date_str = None
        if article:
            time_el = await article.query_selector("time")
            if time_el:
                dt_attr = await time_el.get_attribute("datetime")
                if dt_attr:
                    date_str = dt_attr[:10]

        # Get engagement
        engagement = {"likes": 0, "reposts": 0, "replies": 0, "quotes": 0}
        if article:
            groups = await article.query_selector_all('[role="group"]')
            for group in groups:
                group_text = await group.inner_text()
                numbers = re.findall(r'(\d+(?:\.\d+)?[KMB]?)', group_text)
                for idx, num_str in enumerate(numbers):
                    val = _parse_metric(num_str)
                    if idx == 0:
                        engagement["replies"] = val
                    elif idx == 1:
                        engagement["reposts"] = val
                    elif idx == 2:
                        engagement["likes"] = val

        return {
            "text": text.strip(),
            "url": url,
            "author_handle": author,
            "date": date_str,
            "engagement": engagement,
            "why_relevant": "Found via DDG site:x.com search",
            "relevance": 0.8,
        }

    except Exception as e:
        _log(f"  Error scraping {url}: {e}")
        return None


async def _scrape_tweets_batch(tweet_urls: List[str]) -> List[Dict[str, Any]]:
    """Scrape multiple tweet pages sequentially."""
    from patchright.async_api import async_playwright

    chromium_path = _find_chromium()
    items = []

    async with async_playwright() as p:
        launch_kwargs = {"headless": True}
        if chromium_path:
            launch_kwargs["executable_path"] = chromium_path

        browser = await p.chromium.launch(**launch_kwargs)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()

        for i, url in enumerate(tweet_urls):
            _log(f"  [{i+1}/{len(tweet_urls)}] Scraping {url}")
            item = await _scrape_tweet_page(page, url)
            if item:
                items.append(item)
            await asyncio.sleep(1.5)  # Rate limit

        await browser.close()

    _log(f"Scraped {len(items)}/{len(tweet_urls)} tweets successfully")
    return items


def search_x(
    topic: str,
    from_date: str,
    to_date: str,
    depth: str = "default",
    **kwargs,
) -> Dict[str, Any]:
    """Search X using DDG + patchright scraping.

    Compatible with xai_x.search_x interface.
    Returns dict with 'items' key.
    """
    max_items = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])

    try:
        # Phase 1: Find tweet URLs via DuckDuckGo
        tweet_urls = asyncio.run(
            _ddg_find_tweets(topic, from_date, to_date, max_results=max_items)
        )

        if not tweet_urls:
            _log("No tweets found via DDG, returning empty")
            return {"items": []}

        # Phase 2: Scrape individual tweet pages
        items = asyncio.run(_scrape_tweets_batch(tweet_urls))
        return {"items": items}

    except Exception as e:
        _log(f"search_x error: {e}")
        return {"error": str(e), "items": []}


def parse_x_response(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse patchright scrape response to standard x_items format.

    Compatible with xai_x.parse_x_response interface.
    """
    items = []
    raw_items = response.get("items", [])

    for raw in raw_items:
        item = {
            "text": raw.get("text", ""),
            "url": raw.get("url", ""),
            "author_handle": raw.get("author_handle", "unknown"),
            "date": raw.get("date"),
            "engagement": raw.get("engagement", {}),
            "why_relevant": raw.get("why_relevant", ""),
            "relevance": raw.get("relevance", 0.5),
        }
        if item["text"]:
            items.append(item)

    return items
