#!/usr/bin/env python3
"""Extract full transcript from a YouTube video.

Usage:
    python extract_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID" [lang]
    python extract_transcript.py VIDEO_ID [lang]

Language priority: ko → en → first available (or specify explicitly)
Output: JSON with transcript text, timestamps, and metadata.
"""
import sys
import json
import re


def extract_video_id(url_or_id: str) -> str:
    """Extract video ID from various YouTube URL formats."""
    patterns = [
        r'(?:v=|/v/|youtu\.be/|/embed/|/shorts/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$',
    ]
    for p in patterns:
        m = re.search(p, url_or_id)
        if m:
            return m.group(1)
    return url_or_id


def get_transcript_api(video_id: str, lang: str = None) -> dict:
    """Try youtube-transcript-api first (fast, no browser)."""
    from youtube_transcript_api import YouTubeTranscriptApi

    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list_transcripts(video_id)

        # Build language priority
        if lang:
            lang_priority = [lang, 'ko', 'en']
        else:
            lang_priority = ['ko', 'en']

        transcript = None
        used_lang = None
        is_generated = False

        # Try manual transcripts first
        for try_lang in lang_priority:
            try:
                t = transcript_list.find_transcript([try_lang])
                transcript = t
                used_lang = try_lang
                is_generated = t.is_generated
                break
            except Exception:
                continue

        # If no manual, try generated
        if not transcript:
            for try_lang in lang_priority:
                try:
                    t = transcript_list.find_generated_transcript([try_lang])
                    transcript = t
                    used_lang = try_lang
                    is_generated = True
                    break
                except Exception:
                    continue

        # Last resort: any available
        if not transcript:
            for t in transcript_list:
                transcript = t
                used_lang = t.language_code
                is_generated = t.is_generated
                break

        if not transcript:
            return None

        snippets = transcript.fetch()

        entries = []
        full_text_parts = []
        for s in snippets:
            text = s.get('text', str(s)) if isinstance(s, dict) else str(s)
            # Handle FetchedTranscriptSnippet objects
            if hasattr(s, 'text'):
                text = s.text
                start = s.start
                duration = s.duration
            elif isinstance(s, dict):
                text = s.get('text', '')
                start = s.get('start', 0)
                duration = s.get('duration', 0)
            else:
                text = str(s)
                start = 0
                duration = 0

            entries.append({
                'text': text,
                'start': round(start, 2),
                'duration': round(duration, 2),
            })
            full_text_parts.append(text)

        return {
            'video_id': video_id,
            'language': used_lang,
            'is_generated': is_generated,
            'method': 'youtube-transcript-api',
            'segments': entries,
            'full_text': ' '.join(full_text_parts),
            'segment_count': len(entries),
        }

    except Exception as e:
        print(f"[transcript-api] Failed: {e}", file=sys.stderr)
        return None


def get_transcript_ytdlp(video_id: str, lang: str = None) -> dict:
    """Fallback: use yt-dlp to download subtitles."""
    import subprocess
    import tempfile
    import os

    url = f"https://www.youtube.com/watch?v={video_id}"

    with tempfile.TemporaryDirectory() as tmpdir:
        out_template = os.path.join(tmpdir, "subs")

        # Try auto-subs first, then manual
        for sub_flag in ['--write-auto-subs', '--write-subs']:
            cmd = [
                sys.executable.replace('extract_transcript.py', '').rstrip('/') + '/../bin/yt-dlp'
                if 'venv' not in sys.executable else
                os.path.join(os.path.dirname(sys.executable), 'yt-dlp'),
                '--skip-download',
                sub_flag,
                '--sub-format', 'json3',
                '--sub-langs', lang or 'ko,en',
                '-o', out_template,
                url,
            ]
            try:
                subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            except Exception:
                continue

            # Find subtitle file
            for f in os.listdir(tmpdir):
                if f.endswith('.json3'):
                    with open(os.path.join(tmpdir, f), 'r') as fh:
                        data = json.load(fh)

                    # Parse json3 format
                    entries = []
                    full_text_parts = []
                    for event in data.get('events', []):
                        segs = event.get('segs', [])
                        text = ''.join(s.get('utf8', '') for s in segs).strip()
                        if text and text != '\n':
                            start_ms = event.get('tStartMs', 0)
                            dur_ms = event.get('dDurationMs', 0)
                            entries.append({
                                'text': text,
                                'start': round(start_ms / 1000, 2),
                                'duration': round(dur_ms / 1000, 2),
                            })
                            full_text_parts.append(text)

                    detected_lang = 'unknown'
                    lang_match = re.search(r'\.(\w{2})\.json3$', f)
                    if lang_match:
                        detected_lang = lang_match.group(1)

                    return {
                        'video_id': video_id,
                        'language': detected_lang,
                        'is_generated': 'auto' in sub_flag,
                        'method': 'yt-dlp',
                        'segments': entries,
                        'full_text': ' '.join(full_text_parts),
                        'segment_count': len(entries),
                    }

    return None


def get_video_metadata(video_id: str) -> dict:
    """Get basic video metadata via yt-dlp."""
    import subprocess
    import os

    ytdlp_path = os.path.join(os.path.dirname(sys.executable), 'yt-dlp')
    url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        result = subprocess.run(
            [ytdlp_path, '--dump-json', '--skip-download', url],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return {
                'title': data.get('title', ''),
                'channel': data.get('channel', data.get('uploader', '')),
                'duration': data.get('duration', 0),
                'upload_date': data.get('upload_date', ''),
                'view_count': data.get('view_count', 0),
                'description': data.get('description', '')[:500],
            }
    except Exception as e:
        print(f"[metadata] Failed: {e}", file=sys.stderr)

    return {}


def main():
    if len(sys.argv) < 2:
        print("Usage: extract_transcript.py URL_OR_VIDEO_ID [lang]", file=sys.stderr)
        sys.exit(1)

    url_or_id = sys.argv[1]
    lang = sys.argv[2] if len(sys.argv) > 2 else None

    video_id = extract_video_id(url_or_id)
    print(f"[info] Video ID: {video_id}", file=sys.stderr)

    # Get metadata
    metadata = get_video_metadata(video_id)
    if metadata:
        print(f"[info] Title: {metadata.get('title', 'N/A')}", file=sys.stderr)

    # Try transcript-api first
    result = get_transcript_api(video_id, lang)

    # Fallback to yt-dlp
    if not result:
        print("[info] Falling back to yt-dlp...", file=sys.stderr)
        result = get_transcript_ytdlp(video_id, lang)

    if not result:
        print(json.dumps({
            'error': 'No transcript available for this video',
            'video_id': video_id,
            'metadata': metadata,
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    # Merge metadata
    result['metadata'] = metadata
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
