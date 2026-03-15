#!/usr/bin/env python3
"""
Twitter/X Timeline Scraper — Comprehensive tweet collection.

3-Phase approach:
  Phase 1: Profile page scroll (quick scan)
  Phase 2: Google search for tweet ID discovery
  Phase 3: Individual tweet page fetch (full text)

Usage:
  python3 twitter_scrape.py <username> [--days 30] [--output tweets.json]

Requires:
  - ~/.scrapling-venv with scrapling[all] installed
  - LD_LIBRARY_PATH set for Chromium deps
"""

import asyncio
import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path


# ── Helpers ──────────────────────────────────────────────────────────────────

def clean_text(html_fragment: str) -> str:
    """Strip HTML tags and decode entities from a tweetText innerHTML."""
    t = re.sub(r'<[^>]+>', ' ', html_fragment).strip()
    t = re.sub(r'\s+', ' ', t)
    for old, new in [
        ('&gt;', '>'), ('&lt;', '<'), ('&amp;', '&'),
        ('&#x27;', "'"), ('&quot;', '"'), ('&#39;', "'"),
    ]:
        t = t.replace(old, new)
    return t


def parse_articles(html: str, username: str) -> list[dict]:
    """Extract tweets from article elements in page HTML."""
    articles = re.findall(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)
    tweets = []

    for art in articles:
        # Status ID
        link_match = re.search(
            rf'href="(/{re.escape(username)}/status/(\d+))"', art, re.IGNORECASE
        )
        if not link_match:
            continue
        status_id = link_match.group(2)

        # Datetime
        time_matches = re.findall(r'<time[^>]*datetime="([^"]+)"', art)
        if not time_matches:
            continue

        # Text
        text_blocks = re.findall(
            r'data-testid="tweetText"[^>]*>(.*?)</div>', art, re.DOTALL
        )
        texts = [clean_text(tb) for tb in text_blocks if clean_text(tb)]
        if not texts:
            continue

        # Flags
        is_pinned = 'Pinned' in art[:1000] and 'socialContext' in art[:1000]
        is_retweet = bool(re.search(r'reposted', art[:500], re.IGNORECASE))

        tweets.append({
            'id': status_id,
            'date': time_matches[0],
            'text': texts[0],
            'quoted_text': texts[1] if len(texts) > 1 else None,
            'url': f'https://x.com/{username}/status/{status_id}',
            'is_pinned': is_pinned,
            'is_retweet': is_retweet,
        })

    return tweets


# ── Phase 1: Profile Scroll ─────────────────────────────────────────────────

async def phase1_profile_scroll(username: str, max_scrolls: int = 30) -> dict:
    """Scroll the profile page and collect visible tweets."""
    from patchright.async_api import async_playwright

    collected = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 4000},
            user_agent=(
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/131.0.0.0 Safari/537.36'
            ),
        )
        page = await context.new_page()

        url = f'https://x.com/{username}'
        print(f'[Phase 1] Navigating to {url}')
        await page.goto(url, wait_until='networkidle', timeout=30000)

        try:
            await page.wait_for_selector('article', timeout=15000)
        except Exception:
            print('[Phase 1] No articles found — profile may be empty or blocked')
            await browser.close()
            return collected

        await asyncio.sleep(3)

        no_new_count = 0
        for scroll_i in range(max_scrolls):
            html = await page.content()
            tweets = parse_articles(html, username)

            new_count = 0
            for tw in tweets:
                if tw['id'] not in collected and not tw['is_pinned']:
                    collected[tw['id']] = tw
                    new_count += 1

            if new_count > 0:
                print(f'  Scroll {scroll_i + 1}: {len(collected)} total (+{new_count})')
                no_new_count = 0
            else:
                no_new_count += 1
                if no_new_count >= 4:
                    print(f'  No new tweets for {no_new_count} scrolls, stopping')
                    break

            await page.evaluate('window.scrollBy(0, 5000)')
            await asyncio.sleep(2.5)

            # Login wall check
            login_block = await page.query_selector('[data-testid="LoginForm"]')
            if login_block and scroll_i > 3:
                print('  Login wall detected, stopping scroll')
                break

        await browser.close()

    print(f'[Phase 1] Collected {len(collected)} tweets from profile')
    return collected


# ── Phase 3: Individual Tweet Fetch ──────────────────────────────────────────

async def phase3_fetch_individual(
    username: str, tweet_ids: list[str], delay: float = 1.0
) -> dict:
    """Fetch full text for each tweet by visiting its individual page."""
    from patchright.async_api import async_playwright

    results = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 4000},
            user_agent=(
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/131.0.0.0 Safari/537.36'
            ),
        )
        page = await context.new_page()

        for i, tid in enumerate(tweet_ids):
            url = f'https://x.com/{username}/status/{tid}'
            print(f'  [{i + 1}/{len(tweet_ids)}] Fetching {tid}...', end=' ')

            try:
                await page.goto(url, wait_until='networkidle', timeout=20000)
                await asyncio.sleep(2)

                # Expand long posts
                try:
                    show_more = await page.query_selector(
                        '[data-testid="tweet-text-show-more-link"]'
                    )
                    if show_more:
                        await show_more.click()
                        await asyncio.sleep(1)
                except Exception:
                    pass

                html = await page.content()

                # Extract text
                text_blocks = re.findall(
                    r'data-testid="tweetText"[^>]*>(.*?)</div>', html, re.DOTALL
                )
                texts = [clean_text(tb) for tb in text_blocks if clean_text(tb)]

                # Extract date
                time_matches = re.findall(r'<time[^>]*datetime="([^"]+)"', html)

                # Reply detection
                is_reply = bool(re.search(r'Replying to', html[:5000]))

                if texts and time_matches:
                    results[tid] = {
                        'id': tid,
                        'date': time_matches[0],
                        'text': texts[0],
                        'quoted_text': texts[1] if len(texts) > 1 else None,
                        'url': f'https://x.com/{username}/status/{tid}',
                        'is_reply': is_reply,
                        'is_pinned': False,
                        'is_retweet': False,
                    }
                    print(f'OK [{time_matches[0][:10]}]')
                else:
                    print('EMPTY')

            except Exception as e:
                print(f'ERROR: {e}')

            await asyncio.sleep(delay)

        await browser.close()

    print(f'[Phase 3] Fetched {len(results)}/{len(tweet_ids)} tweets')
    return results


# ── Thread Reconstruction ────────────────────────────────────────────────────

def reconstruct_threads(tweets: list[dict]) -> list[dict]:
    """
    Group self-reply chains into threads.

    Uses heuristic: same user, same day, posted within 15 minutes.
    Labels threads with 1/N, 2/N, etc.
    """
    if not tweets:
        return tweets

    sorted_tweets = sorted(tweets, key=lambda t: t['date'])
    used = set()
    result = []

    for i, tw in enumerate(sorted_tweets):
        if tw['id'] in used:
            continue

        # Check if this starts a thread
        thread = [tw]
        used.add(tw['id'])

        tw_dt = datetime.fromisoformat(tw['date'].replace('Z', '+00:00'))

        # Look for subsequent tweets within 15 min windows
        for j in range(i + 1, len(sorted_tweets)):
            candidate = sorted_tweets[j]
            if candidate['id'] in used:
                continue

            c_dt = datetime.fromisoformat(
                candidate['date'].replace('Z', '+00:00')
            )

            # Same day, within 15 min of LAST tweet in thread
            last_dt = datetime.fromisoformat(
                thread[-1]['date'].replace('Z', '+00:00')
            )

            if (c_dt - last_dt).total_seconds() < 900:  # 15 min
                if candidate.get('is_reply', False):
                    thread.append(candidate)
                    used.add(candidate['id'])

        # Label thread
        if len(thread) > 1:
            for idx, t in enumerate(thread):
                t['thread_label'] = f'{idx + 1}/{len(thread)}'
                t['thread_id'] = thread[0]['id']
        else:
            tw['thread_label'] = None
            tw['thread_id'] = None

        result.extend(thread)

    return result


# ── Output Formatting ────────────────────────────────────────────────────────

def format_markdown(tweets: list[dict], username: str) -> str:
    """Format tweets as a dated markdown document."""
    lines = [
        f'# @{username} Twitter Timeline',
        f'',
        f'Period: {tweets[0]["date"][:10]} ~ {tweets[-1]["date"][:10]}',
        f'Total: {len(tweets)} tweets',
        f'',
        '---',
        '',
    ]

    current_date = None

    for tw in tweets:
        date_str = tw['date'][:10]
        dt = datetime.fromisoformat(tw['date'].replace('Z', '+00:00'))
        day_name = dt.strftime('%a')
        time_str = dt.strftime('%H:%M')

        if date_str != current_date:
            current_date = date_str
            lines.append(f'## 📅 {date_str} ({day_name})')
            lines.append('')

        # Thread label
        thread_tag = ''
        if tw.get('thread_label'):
            thread_tag = f' — Thread ({tw["thread_label"]})'

        reply_tag = ' [Reply]' if tw.get('is_reply') else ''

        lines.append(f'### {time_str}{thread_tag}{reply_tag}')
        lines.append('')
        lines.append(f'> {tw["text"]}')

        if tw.get('quoted_text'):
            lines.append(f'>')
            lines.append(f'> 📎 Quoted: {tw["quoted_text"][:200]}...')

        lines.append(f'')
        lines.append(f'🔗 [{tw["url"]}]({tw["url"]})')
        lines.append('')
        lines.append('---')
        lines.append('')

    return '\n'.join(lines)


# ── Main ─────────────────────────────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(description='Twitter/X Timeline Scraper')
    parser.add_argument('username', help='Twitter username (without @)')
    parser.add_argument('--days', type=int, default=30,
                        help='Number of days to look back (default: 30)')
    parser.add_argument('--output', default=None,
                        help='Output JSON file path')
    parser.add_argument('--markdown', default=None,
                        help='Output Markdown file path')
    parser.add_argument('--extra-ids', nargs='*', default=[],
                        help='Additional tweet IDs to fetch')
    parser.add_argument('--skip-profile', action='store_true',
                        help='Skip Phase 1 profile scrolling')
    args = parser.parse_args()

    username = args.username.lstrip('@')
    cutoff = datetime.now() - timedelta(days=args.days)

    print(f'=== Twitter Scraper: @{username} ===')
    print(f'Date range: {cutoff.date()} ~ {datetime.now().date()}')
    print()

    # Phase 1: Profile scroll
    all_tweets = {}
    if not args.skip_profile:
        profile_tweets = await phase1_profile_scroll(username)
        all_tweets.update(profile_tweets)
        print()

    # Add extra IDs if provided
    extra_ids = [tid for tid in args.extra_ids if tid not in all_tweets]

    if extra_ids:
        print(f'[Phase 3] Fetching {len(extra_ids)} additional tweet IDs')
        extra_tweets = await phase3_fetch_individual(username, extra_ids)
        all_tweets.update(extra_tweets)
        print()

    # Filter by date range
    filtered = []
    for tw in all_tweets.values():
        try:
            dt = datetime.fromisoformat(
                tw['date'].replace('Z', '+00:00')
            ).replace(tzinfo=None)
            if dt >= cutoff:
                tw['date_parsed'] = dt.isoformat()
                filtered.append(tw)
        except Exception:
            pass

    filtered.sort(key=lambda t: t['date'])

    # Reconstruct threads
    filtered = reconstruct_threads(filtered)

    print(f'=== Results: {len(filtered)} tweets in last {args.days} days ===')

    # Output JSON
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(filtered, f, ensure_ascii=False, indent=2)
        print(f'Saved JSON: {args.output}')

    # Output Markdown
    if filtered:
        md = format_markdown(filtered, username)
        if args.markdown:
            with open(args.markdown, 'w') as f:
                f.write(md)
            print(f'Saved Markdown: {args.markdown}')
        else:
            print()
            print(md)

    return filtered


if __name__ == '__main__':
    asyncio.run(main())
