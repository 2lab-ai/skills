# Video Clip Examples

This directory contains example files for using the video-clip skill.

## Quick Start

### 1. Single Clip Extraction

Extract a 15-second clip from a YouTube video:

```bash
cd /home/zhugehyuk/2lab.ai/skills/video-clip

./scripts/clip-extract.sh \
  "https://youtube.com/watch?v=dQw4w9WgXcQ" \
  "00:00:10" \
  "00:00:25" \
  "/tmp/my-clip.mp4"
```

### 2. Batch Clip Extraction

Extract multiple clips using the example JSON file:

```bash
cd /home/zhugehyuk/2lab.ai/skills/video-clip

./scripts/batch-clip.sh \
  "https://youtube.com/watch?v=dQw4w9WgXcQ" \
  examples/clips-example.json \
  /tmp/my-clips/
```

This will create:
- `/tmp/my-clips/clip1.mp4`
- `/tmp/my-clips/clip2.mp4`
- `/tmp/my-clips/clip3.mp4`
- `/tmp/my-clips/manifest.json`

### 3. High-Quality 1080p Extraction

```bash
./scripts/clip-extract.sh \
  "https://youtube.com/watch?v=dQw4w9WgXcQ" \
  "00:01:00" \
  "00:01:30" \
  "/tmp/hq-clip.mp4" \
  --resolution 1080
```

### 4. WebM Format

```bash
./scripts/clip-extract.sh \
  "https://youtube.com/watch?v=dQw4w9WgXcQ" \
  "60" \
  "90" \
  "/tmp/web-clip.webm" \
  --format webm
```

## Creating Your Own clips.json

Copy and modify `clips-example.json`:

```json
[
  {
    "id": "intro",
    "start": "00:00:00",
    "end": "00:00:30",
    "label": "Opening sequence"
  },
  {
    "id": "main-point",
    "start": "00:05:15",
    "end": "00:06:00",
    "label": "Main argument"
  },
  {
    "id": "conclusion",
    "start": "920",
    "end": "975",
    "label": "Final thoughts (using seconds)"
  }
]
```

## Tips

1. **Time Formats**: Use either `HH:MM:SS` or seconds (can include decimals like `90.5`)
2. **Resolution**: 720p is faster and smaller; use 1080p only when quality matters
3. **Format**: Use mp4 for compatibility, webm for web usage
4. **Batch Processing**: More efficient than individual downloads when extracting multiple clips from the same video
5. **Segment Download**: The script tries to download only the needed segment first, then falls back to full download if needed

## Checking Prerequisites

Make sure the required tools are installed:

```bash
ls -lh ~/.youtube-venv/bin/yt-dlp
ls -lh ~/.local/bin/ffmpeg
ls -lh ~/.local/bin/ffprobe
```

If any are missing, refer to the main SKILL.md for installation instructions.
