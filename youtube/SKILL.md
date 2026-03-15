---
name: youtube
description: Extract transcripts, subtitles, and metadata from YouTube videos. Use this skill whenever a user shares a YouTube URL or asks to extract scripts, subtitles, transcripts, or captions from a video. Also triggers on keywords like 유튜브, 스크립트, 자막, 트랜스크립트, or any youtube.com / youtu.be link.
---

# YouTube — Transcript & Subtitle Extraction

Extract full transcripts from YouTube videos with timestamps, using `youtube-transcript-api` (fast) with `yt-dlp` fallback.

## Environment

- **Python**: `~/.youtube-venv/bin/python3`
- **Dependencies**: `youtube-transcript-api`, `yt-dlp`
- **No Chromium needed** — pure API/CLI based

## Quick Usage

```bash
# Full transcript extraction
~/.youtube-venv/bin/python3 /home/zhugehyuk/2lab.ai/tools/youtube/scripts/extract_transcript.py "YOUTUBE_URL" [lang]

# Examples
~/.youtube-venv/bin/python3 .../extract_transcript.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
~/.youtube-venv/bin/python3 .../extract_transcript.py "https://youtu.be/dQw4w9WgXcQ" ko
~/.youtube-venv/bin/python3 .../extract_transcript.py "dQw4w9WgXcQ" en
```

## Output Format

JSON with:
- `video_id`: YouTube video ID
- `metadata`: title, channel, duration, views, upload date
- `language`: detected language code (ko, en, etc.)
- `is_generated`: whether subtitles are auto-generated
- `full_text`: complete transcript as single string
- `segments`: array of `{text, start, duration}` with timestamps
- `segment_count`: number of segments

## Language Priority

1. Specified language (if provided via CLI arg)
2. Korean (`ko`)
3. English (`en`)
4. Any available language

Manual (human-written) subtitles are preferred over auto-generated.

## Supported URL Formats

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://www.youtube.com/shorts/VIDEO_ID`
- Raw video ID (11 characters)

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| No transcript available | Video has no captions | Nothing to do — video has no subs |
| Subtitles disabled | Creator disabled captions | Try yt-dlp fallback (auto-generated) |
| Video unavailable | Private/deleted/region-locked | Cannot extract |
| Network timeout | Slow connection | Retry with longer timeout |

## Presenting Results

- For short transcripts (< 50 segments): show full text inline
- For long transcripts: show full_text as a clean block, optionally with key timestamps
- Always show metadata (title, channel, duration) at the top
- If user asks for summary, use the full_text to generate one
