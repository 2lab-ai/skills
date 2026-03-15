#!/usr/bin/env python3
"""
Threads (threads.com) Timeline Scraper.

2-Phase approach:
  Phase 1: Profile page scroll (collect post IDs)
  Phase 2: Individual post page fetch (full text via og:description)

Usage:
  python3 threads_scrape.py <username> [--days 90] [--output posts.json]

Requires:
  - ~/.scrapling-venv with patchright installed
  - LD_LIBRARY_PATH set for Chromium deps
"""

import asyncio
import argparse
import json
import re
import sys
from collections import OrderedDict
from datetime import datetime, timedelta


# ── Helpers ──────────────────────────────────────────────────────────────────

def decode_entities(text: str) -> str:
    """Decode HTML entities."""
    for old, new in [
        ('&gt;', '>'), ('&lt;', '<'), ('&amp;', '&'),
        ('&#x27;', "'"), ('&quot;', '"'), ('&#39;', "'"),
        ('\\n', '\n'),
    ]:
        text = text.replace(old, new)
    return text


# ── Phase 1: Profile Scroll ─────────────────────────────────────────────────

async def phase1_profile_scroll(username: str, max_scrolls: int = 80) -> list[str]:
    """Scroll the profile page and collect all visible post IDs."""
    from patchright.async_api import async_playwright

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

        url = f'https://www.threads.com/@{username}'
        print(f'[Phase 1] Navigating to {url}')
        await page.goto(url, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(5)

        all_ids = OrderedDict()
        no_new_count = 0

        for scroll_i in range(max_scrolls):
            html = await page.content()

            # Collect post IDs (exclude /media links)
            pattern = rf'href="/@{re.escape(username)}/post/([A-Za-z0-9_-]+)"'
            post_ids = re.findall(pattern, html)

            new_count = 0
            for pid in post_ids:
                if pid not in all_ids:
                    all_ids[pid] = True
                    new_count += 1

            if new_count > 0:
                print(f'  Scroll {scroll_i + 1}: {len(all_ids)} posts (+{new_count})')
                no_new_count = 0
            else:
                no_new_count += 1
                if no_new_count >= 5 and scroll_i > 5:
                    print(f'  No new posts for {no_new_count} scrolls, stopping')
                    break

            await page.evaluate('window.scrollBy(0, 2000)')
            await asyncio.sleep(2)

        await browser.close()

    result = list(all_ids.keys())
    print(f'[Phase 1] Collected {len(result)} unique post IDs')
    return result


# ── Phase 2: Individual Post Fetch ───────────────────────────────────────────

async def phase2_fetch_posts(
    username: str, post_ids: list[str], delay: float = 1.5
) -> list[dict]:
    """Fetch full text for each post by visiting its individual page."""
    from patchright.async_api import async_playwright

    results = []

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

        for i, pid in enumerate(post_ids):
            url = f'https://www.threads.com/@{username}/post/{pid}'
            print(f'  [{i + 1}/{len(post_ids)}] {pid}...', end=' ')

            success = False
            for attempt in range(2):  # Retry once on failure
                try:
                    await page.goto(
                        url,
                        wait_until='domcontentloaded',
                        timeout=30000,
                    )
                    await asyncio.sleep(4 if attempt == 0 else 6)

                    html = await page.content()

                    # Extract from og:description (most reliable)
                    meta_desc = re.search(
                        r'<meta[^>]*property="og:description"[^>]*content="([^"]*)"',
                        html,
                    )
                    text = decode_entities(meta_desc.group(1)) if meta_desc else ''

                    # Extract datetime
                    times = re.findall(
                        r'<time[^>]*datetime="([^"]+)"', html
                    )

                    if text or times:
                        results.append({
                            'id': pid,
                            'url': url,
                            'date': times[0] if times else 'unknown',
                            'text': text,
                        })
                        dt_str = times[0][:10] if times else '?'
                        print(f'OK [{dt_str}] {text[:80]}...')
                        success = True
                        break
                    elif attempt == 0:
                        print('empty, retrying...', end=' ')
                    else:
                        print('EMPTY')

                except Exception as e:
                    if attempt == 0:
                        print(f'err, retrying...', end=' ')
                    else:
                        print(f'FAIL: {e}')

            if not success and not any(r['id'] == pid for r in results):
                results.append({
                    'id': pid,
                    'url': url,
                    'date': 'unknown',
                    'text': '',
                    'error': 'failed after 2 attempts',
                })

            await asyncio.sleep(delay)

        await browser.close()

    ok_count = sum(1 for r in results if r.get('text'))
    print(f'[Phase 2] Fetched {ok_count}/{len(post_ids)} posts with text')
    return results


# ── Thread Reconstruction ────────────────────────────────────────────────────

def reconstruct_threads(posts: list[dict]) -> list[dict]:
    """
    Group posts into threads based on temporal proximity.
    Posts by the same user within 2 minutes are grouped.
    """
    if not posts:
        return posts

    sorted_posts = sorted(posts, key=lambda p: p['date'])
    used = set()
    result = []

    for i, post in enumerate(sorted_posts):
        if post['id'] in used:
            continue

        thread = [post]
        used.add(post['id'])

        if post['date'] == 'unknown':
            post['thread_label'] = None
            result.append(post)
            continue

        try:
            post_dt = datetime.fromisoformat(
                post['date'].replace('Z', '+00:00')
            )
        except Exception:
            post['thread_label'] = None
            result.append(post)
            continue

        # Look for subsequent posts within 2 min of last in thread
        for j in range(i + 1, len(sorted_posts)):
            candidate = sorted_posts[j]
            if candidate['id'] in used or candidate['date'] == 'unknown':
                continue

            try:
                c_dt = datetime.fromisoformat(
                    candidate['date'].replace('Z', '+00:00')
                )
                last_dt = datetime.fromisoformat(
                    thread[-1]['date'].replace('Z', '+00:00')
                )

                if (c_dt - last_dt).total_seconds() < 120:  # 2 min
                    thread.append(candidate)
                    used.add(candidate['id'])
                else:
                    break  # Gap too large, stop threading
            except Exception:
                break

        # Label thread
        if len(thread) > 1:
            for idx, t in enumerate(thread):
                t['thread_label'] = f'{idx + 1}/{len(thread)}'
                t['thread_id'] = thread[0]['id']
        else:
            post['thread_label'] = None
            post['thread_id'] = None

        result.extend(thread)

    return result


# ── Output Formatting ────────────────────────────────────────────────────────

def format_markdown(posts: list[dict], username: str) -> str:
    """Format posts as a dated markdown document."""
    lines = [
        f'# @{username} Threads Timeline',
        '',
        f'Period: {posts[0]["date"][:10]} ~ {posts[-1]["date"][:10]}',
        f'Total: {len(posts)} posts',
        '',
        '---',
        '',
    ]

    current_date = None

    for post in posts:
        if post['date'] == 'unknown':
            continue

        date_str = post['date'][:10]
        try:
            dt = datetime.fromisoformat(post['date'].replace('Z', '+00:00'))
            day_name = dt.strftime('%a')
            time_str = dt.strftime('%H:%M')
        except Exception:
            day_name = '?'
            time_str = '?'

        if date_str != current_date:
            current_date = date_str
            lines.append(f'## 📅 {date_str} ({day_name})')
            lines.append('')

        thread_tag = ''
        if post.get('thread_label'):
            thread_tag = f' — Thread ({post["thread_label"]})'

        lines.append(f'### {time_str}{thread_tag}')
        lines.append('')

        text = post['text']
        if text:
            # Indent as blockquote
            for line in text.split('\n'):
                lines.append(f'> {line}')
        else:
            lines.append('> *(media only)*')

        lines.append('')
        lines.append(f'🔗 [{post["url"]}]({post["url"]})')
        lines.append('')
        lines.append('---')
        lines.append('')

    return '\n'.join(lines)


# ── Main ─────────────────────────────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(description='Threads Timeline Scraper')
    parser.add_argument('username', help='Threads username (without @)')
    parser.add_argument('--days', type=int, default=90,
                        help='Number of days to look back (default: 90)')
    parser.add_argument('--output', default=None,
                        help='Output JSON file path')
    parser.add_argument('--markdown', default=None,
                        help='Output Markdown file path')
    parser.add_argument('--extra-ids', nargs='*', default=[],
                        help='Additional post IDs to fetch')
    args = parser.parse_args()

    username = args.username.lstrip('@')
    cutoff = datetime.now() - timedelta(days=args.days)

    print(f'=== Threads Scraper: @{username} ===')
    print(f'Date range: {cutoff.date()} ~ {datetime.now().date()}')
    print()

    # Phase 1: Profile scroll
    post_ids = await phase1_profile_scroll(username)

    # Add extra IDs
    for eid in args.extra_ids:
        if eid not in post_ids:
            post_ids.append(eid)

    # Phase 2: Fetch all posts
    print()
    posts = await phase2_fetch_posts(username, post_ids)
    print()

    # Filter by date range
    filtered = []
    for post in posts:
        if post['date'] == 'unknown' or not post.get('text'):
            continue
        try:
            dt = datetime.fromisoformat(
                post['date'].replace('Z', '+00:00')
            ).replace(tzinfo=None)
            if dt >= cutoff:
                post['date_parsed'] = dt.isoformat()
                filtered.append(post)
        except Exception:
            pass

    filtered.sort(key=lambda p: p['date'])

    # Reconstruct threads
    filtered = reconstruct_threads(filtered)

    print(f'=== Results: {len(filtered)} posts in last {args.days} days ===')

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
