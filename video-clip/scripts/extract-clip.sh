#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# extract-clip — Extract a clip from YouTube video by timestamp
#
# Usage:
#   extract-clip.sh <youtube_url> --start MM:SS --end MM:SS [--output file.mp4]
#   extract-clip.sh --local <video.mp4> --start MM:SS --end MM:SS [--output file.mp4]
# ═══════════════════════════════════════════════════════════════
set -euo pipefail

FFMPEG="${HOME}/.local/bin/ffmpeg"
FFPROBE="${HOME}/.local/bin/ffprobe"
YT_DLP="${HOME}/.youtube-venv/bin/yt-dlp"
DOWNLOAD_DIR="/tmp/video-clip-cache"

# Colors
CYAN='\033[0;36m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'
info()  { echo -e "${CYAN}[clip]${NC} $*"; }
ok()    { echo -e "${GREEN}[clip]${NC} $*"; }
err()   { echo -e "${RED}[clip]${NC} $*" >&2; }

# Defaults
SOURCE=""
LOCAL_FILE=""
START=""
END=""
OUTPUT=""
FORMAT="136+bestaudio"  # 720p h264 + best audio
RESIZE=""
NO_AUDIO=false

# Parse args
while [[ $# -gt 0 ]]; do
    case "$1" in
        --local)      LOCAL_FILE="$2"; shift 2 ;;
        --start)      START="$2"; shift 2 ;;
        --end)        END="$2"; shift 2 ;;
        --output)     OUTPUT="$2"; shift 2 ;;
        --format)     FORMAT="$2"; shift 2 ;;
        --resize)     RESIZE="$2"; shift 2 ;;
        --no-audio)   NO_AUDIO=true; shift ;;
        -h|--help)
            echo "Usage: extract-clip.sh <url|--local file.mp4> --start MM:SS --end MM:SS [--output file.mp4]"
            exit 0 ;;
        -*) err "Unknown option: $1"; exit 1 ;;
        *)
            if [[ -z "$SOURCE" ]]; then
                SOURCE="$1"
            fi
            shift ;;
    esac
done

# Validate
if [[ -z "$START" || -z "$END" ]]; then
    err "Both --start and --end are required"
    exit 1
fi

if [[ -z "$SOURCE" && -z "$LOCAL_FILE" ]]; then
    err "Provide a YouTube URL or --local <file>"
    exit 1
fi

# Get or download video
if [[ -n "$LOCAL_FILE" ]]; then
    VIDEO_FILE="$LOCAL_FILE"
    if [[ ! -f "$VIDEO_FILE" ]]; then
        err "Local file not found: $VIDEO_FILE"
        exit 1
    fi
else
    mkdir -p "$DOWNLOAD_DIR"
    # Extract video ID for caching
    VIDEO_ID=$(echo "$SOURCE" | grep -oP '(?:v=|youtu\.be/)[^&?]+' | head -1 | sed 's/v=//')
    VIDEO_FILE="$DOWNLOAD_DIR/${VIDEO_ID}.mp4"

    if [[ -f "$VIDEO_FILE" ]]; then
        info "Using cached download: $VIDEO_FILE"
    else
        info "Downloading video ($FORMAT)..."
        "$YT_DLP" -f "$FORMAT" --merge-output-format mp4 \
            -o "$VIDEO_FILE" "$SOURCE" 2>&1 | tail -5
    fi
fi

# Generate output path if not specified
if [[ -z "$OUTPUT" ]]; then
    SAFE_START=$(echo "$START" | tr ':' '-')
    SAFE_END=$(echo "$END" | tr ':' '-')
    OUTPUT="/tmp/clip_${SAFE_START}_${SAFE_END}.mp4"
fi

# Extract clip
info "Extracting: $START → $END"
info "Source: $VIDEO_FILE"
info "Output: $OUTPUT"

AUDIO_FLAGS=""
if $NO_AUDIO; then
    AUDIO_FLAGS="-an"
else
    AUDIO_FLAGS="-c:a aac -b:a 128k"
fi

RESIZE_FLAGS=""
if [[ -n "$RESIZE" ]]; then
    RESIZE_FLAGS="-vf scale=$RESIZE"
fi

"$FFMPEG" -ss "$START" -to "$END" -i "$VIDEO_FILE" \
    -c:v libx264 -crf 23 -preset fast \
    $AUDIO_FLAGS $RESIZE_FLAGS \
    -movflags +faststart \
    "$OUTPUT" -y 2>/dev/null

if [[ -f "$OUTPUT" ]]; then
    DUR=$("$FFPROBE" -v error -show_entries format=duration -of csv=p=0 "$OUTPUT" 2>/dev/null || echo "?")
    SIZE=$(du -h "$OUTPUT" | cut -f1)
    ok "Done! ${DUR}s / ${SIZE}"
    ok "Output: $OUTPUT"
else
    err "Failed to extract clip"
    exit 1
fi
