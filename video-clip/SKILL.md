# video-clip

Extract clips from YouTube videos using yt-dlp + ffmpeg.

## Description

This skill provides tools to extract specific time segments from YouTube videos without downloading the entire video. It supports both single clip extraction and batch processing from a JSON specification.

## Features

- Smart segment downloading using yt-dlp's --download-sections
- Automatic fallback to full download + trim if segment download fails
- Batch processing support via JSON specification
- Configurable output format (mp4/webm) and resolution (720p/1080p)
- Flexible time format support (HH:MM:SS or seconds)

## Prerequisites

The following binaries must be installed:

- `~/.youtube-venv/bin/yt-dlp` - YouTube video downloader
- `~/.local/bin/ffmpeg` - Video processing tool
- `~/.local/bin/ffprobe` - Video analysis tool

## Installation

Make the scripts executable:

```bash
chmod +x /home/zhugehyuk/2lab.ai/skills/video-clip/scripts/clip-extract.sh
chmod +x /home/zhugehyuk/2lab.ai/skills/video-clip/scripts/batch-clip.sh
```

## Usage

### Single Clip Extraction

Extract a single clip from a YouTube video:

```bash
./scripts/clip-extract.sh <youtube-url> <start_time> <end_time> <output_path> [--format mp4|webm] [--resolution 720|1080]
```

**Arguments:**
- `youtube-url`: Full YouTube URL or video ID
- `start_time`: Start time in HH:MM:SS format or seconds
- `end_time`: End time in HH:MM:SS format or seconds
- `output_path`: Path where the clip should be saved

**Options:**
- `--format mp4|webm`: Output format (default: mp4)
- `--resolution 720|1080`: Video resolution (default: 720)

**Examples:**

```bash
# Extract 15 seconds starting at 5:30
./scripts/clip-extract.sh "https://youtube.com/watch?v=VIDEO_ID" "00:05:30" "00:05:45" "/tmp/clip1.mp4"

# Extract with 1080p resolution
./scripts/clip-extract.sh "https://youtube.com/watch?v=VIDEO_ID" "330" "345" "/tmp/clip1.mp4" --resolution 1080

# Extract as webm format
./scripts/clip-extract.sh "https://youtube.com/watch?v=VIDEO_ID" "01:23:10" "01:23:25" "/tmp/clip2.webm" --format webm
```

### Batch Clip Extraction

Extract multiple clips from the same video:

```bash
./scripts/batch-clip.sh <youtube-url> <clips.json> <output_dir>
```

**Arguments:**
- `youtube-url`: Full YouTube URL or video ID
- `clips.json`: JSON file specifying clips to extract
- `output_dir`: Directory where clips will be saved

**clips.json format:**

```json
[
  {
    "id": "clip1",
    "start": "00:05:30",
    "end": "00:05:45",
    "label": "key quote about space"
  },
  {
    "id": "clip2",
    "start": "01:23:10",
    "end": "01:23:25",
    "label": "prediction about AI"
  }
]
```

**Output:**

The batch script creates:
- Individual clip files: `{output_dir}/{id}.mp4`
- Manifest file: `{output_dir}/manifest.json` with processing results

**Example:**

```bash
./scripts/batch-clip.sh "https://youtube.com/watch?v=VIDEO_ID" clips.json /tmp/my-clips/
```

This creates:
- `/tmp/my-clips/clip1.mp4`
- `/tmp/my-clips/clip2.mp4`
- `/tmp/my-clips/manifest.json`

## Implementation Details

### Download Strategy

1. **Primary method**: Use yt-dlp's `--download-sections` to download only the required segment
2. **Fallback method**: If segment download fails, download full video and trim with ffmpeg

### Format Selection

- **720p**: `-f "bestvideo[height<=720]+bestaudio/best[height<=720]"`
- **1080p**: `-f "bestvideo[height<=1080]+bestaudio/best[height<=1080]"`
- **Merge format**: `--merge-output-format mp4` (or webm as specified)

### Time Format Handling

Both scripts accept times in:
- `HH:MM:SS` format (e.g., "01:23:45")
- Seconds as integer or float (e.g., "330" or "330.5")

## Error Handling

- Missing binaries: Scripts check for required tools and exit with error message
- Invalid time formats: Scripts validate time inputs
- Download failures: Automatic fallback to alternative download method
- Network issues: yt-dlp's built-in retry logic

## Troubleshooting

**"yt-dlp not found"**
- Ensure yt-dlp is installed at `~/.youtube-venv/bin/yt-dlp`

**"ffmpeg not found"**
- Ensure ffmpeg/ffprobe are installed at `~/.local/bin/`

**Segment download fails**
- Script automatically falls back to full download + trim
- Check that the video allows seeking/partial downloads

**Video quality lower than expected**
- Some videos may not have the requested resolution
- yt-dlp automatically selects the best available quality

## Tips

- Use seconds for precise timing (supports decimals)
- Use HH:MM:SS for readability
- 720p is faster to download and process than 1080p
- Batch processing is more efficient than individual downloads for multiple clips from the same video
