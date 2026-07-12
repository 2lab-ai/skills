#!/usr/bin/env bash
set -euo pipefail

# Extract Still Images from Video
# Usage: ./scripts/extract-stills.sh <input_video> [output_dir] [options]
#
# Options:
#   --count N        Number of evenly-spaced stills (default: 10)
#   --timestamps T   Comma-separated timestamps (e.g., "00:01:30,00:05:00,00:10:22")
#   --interval S     Extract every S seconds (e.g., 30 = every 30s)
#   --quality Q      JPEG quality 1-100 (default: 95)
#   --thumbnail      Also generate a 16:9 thumbnail (1280x720)
#
# Examples:
#   # Extract 10 evenly-spaced stills
#   bash extract-stills.sh /tmp/video.mp4 /tmp/stills --count 10
#
#   # Extract at specific timestamps
#   bash extract-stills.sh /tmp/video.mp4 /tmp/stills --timestamps "00:01:30,00:05:00"
#
#   # Extract every 60 seconds
#   bash extract-stills.sh /tmp/video.mp4 /tmp/stills --interval 60
#
#   # Generate thumbnail from best frame
#   bash extract-stills.sh /tmp/video.mp4 /tmp/stills --thumbnail

FFMPEG="${HOME}/.local/bin/ffmpeg"
FFPROBE="${HOME}/.local/bin/ffprobe"

# Fallback to system ffmpeg/ffprobe
command -v "$FFMPEG" &>/dev/null || FFMPEG="ffmpeg"
command -v "$FFPROBE" &>/dev/null || FFPROBE="ffprobe"

# Colors
BLUE='\033[34m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
NC='\033[0m'

info()    { echo -e "${BLUE}[extract-stills]${NC} $1"; }
success() { echo -e "${GREEN}[extract-stills]${NC} $1"; }
warn()    { echo -e "${YELLOW}[extract-stills]${NC} $1"; }
error()   { echo -e "${RED}[extract-stills]${NC} $1"; }

# === Parse args ===
INPUT_VIDEO="${1:?Usage: extract-stills.sh <input_video> [output_dir] [options]}"
shift

OUTPUT_DIR="${1:-/tmp/video-stills}"
# Check if second arg is an option flag
if [[ "${OUTPUT_DIR}" == --* ]]; then
  OUTPUT_DIR="/tmp/video-stills"
else
  shift || true
fi

COUNT=10
TIMESTAMPS=""
INTERVAL=""
QUALITY=95
THUMBNAIL=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --count)     COUNT="$2"; shift 2 ;;
    --timestamps) TIMESTAMPS="$2"; shift 2 ;;
    --interval)  INTERVAL="$2"; shift 2 ;;
    --quality)   QUALITY="$2"; shift 2 ;;
    --thumbnail) THUMBNAIL=true; shift ;;
    *) error "Unknown option: $1"; exit 1 ;;
  esac
done

# Validate input
if [ ! -f "$INPUT_VIDEO" ]; then
  error "Video not found: $INPUT_VIDEO"
  exit 1
fi

# Make paths absolute
[[ "$INPUT_VIDEO" != /* ]] && INPUT_VIDEO="$(pwd)/$INPUT_VIDEO"
[[ "$OUTPUT_DIR" != /* ]] && OUTPUT_DIR="$(pwd)/$OUTPUT_DIR"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Get video duration
DURATION=$("$FFPROBE" -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 "$INPUT_VIDEO" 2>/dev/null)
DURATION_INT=$(printf "%.0f" "$DURATION")

info "=== Still Image Extraction ==="
info "Input:    $INPUT_VIDEO"
info "Output:   $OUTPUT_DIR"
info "Duration: ${DURATION_INT}s ($(printf '%02d:%02d:%02d' $((DURATION_INT/3600)) $((DURATION_INT%3600/60)) $((DURATION_INT%60))))"
echo ""

EXTRACTED=0

# === Mode 1: Specific timestamps ===
if [ -n "$TIMESTAMPS" ]; then
  info "Mode: Specific timestamps"
  IFS=',' read -ra TS_ARRAY <<< "$TIMESTAMPS"
  for i in "${!TS_ARRAY[@]}"; do
    ts="${TS_ARRAY[$i]}"
    ts_clean=$(echo "$ts" | tr -d ' ')
    idx=$(printf "%03d" $((i + 1)))
    outfile="$OUTPUT_DIR/still_${idx}_${ts_clean//:/}.jpg"

    info "  Extracting frame at $ts_clean..."
    "$FFMPEG" -ss "$ts_clean" -i "$INPUT_VIDEO" \
      -vframes 1 -q:v $((100 - QUALITY + 2)) \
      -y "$outfile" 2>/dev/null

    if [ -f "$outfile" ]; then
      EXTRACTED=$((EXTRACTED + 1))
      success "  -> $outfile"
    fi
  done

# === Mode 2: Every N seconds ===
elif [ -n "$INTERVAL" ]; then
  info "Mode: Every ${INTERVAL}s"
  t=0
  idx=1
  while (( t < DURATION_INT )); do
    ts=$(printf '%02d:%02d:%02d' $((t/3600)) $((t%3600/60)) $((t%60)))
    outfile="$OUTPUT_DIR/still_$(printf '%03d' $idx)_${t}s.jpg"

    "$FFMPEG" -ss "$t" -i "$INPUT_VIDEO" \
      -vframes 1 -q:v $((100 - QUALITY + 2)) \
      -y "$outfile" 2>/dev/null

    if [ -f "$outfile" ]; then
      EXTRACTED=$((EXTRACTED + 1))
      info "  [$idx] ${ts} -> $(basename "$outfile")"
    fi

    t=$((t + INTERVAL))
    idx=$((idx + 1))
  done

# === Mode 3: Evenly-spaced (default) ===
else
  info "Mode: $COUNT evenly-spaced stills"
  # Skip first/last 2% to avoid black frames
  START_OFFSET=$(echo "$DURATION * 0.02" | bc -l 2>/dev/null || echo "2")
  END_OFFSET=$(echo "$DURATION * 0.98" | bc -l 2>/dev/null || echo "$((DURATION_INT - 2))")
  SPAN=$(echo "$END_OFFSET - $START_OFFSET" | bc -l 2>/dev/null || echo "$((DURATION_INT - 4))")

  for i in $(seq 0 $((COUNT - 1))); do
    if [ "$COUNT" -eq 1 ]; then
      t=$(echo "$DURATION / 2" | bc -l 2>/dev/null || echo "$((DURATION_INT / 2))")
    else
      t=$(echo "$START_OFFSET + ($SPAN * $i / ($COUNT - 1))" | bc -l 2>/dev/null || echo "$((2 + (DURATION_INT - 4) * i / (COUNT - 1)))")
    fi
    t_int=$(printf "%.0f" "$t")
    ts=$(printf '%02d:%02d:%02d' $((t_int/3600)) $((t_int%3600/60)) $((t_int%60)))

    idx=$(printf '%03d' $((i + 1)))
    outfile="$OUTPUT_DIR/still_${idx}_${t_int}s.jpg"

    "$FFMPEG" -ss "$t_int" -i "$INPUT_VIDEO" \
      -vframes 1 -q:v $((100 - QUALITY + 2)) \
      -y "$outfile" 2>/dev/null

    if [ -f "$outfile" ]; then
      EXTRACTED=$((EXTRACTED + 1))
      info "  [$((i+1))/$COUNT] ${ts} -> $(basename "$outfile")"
    fi
  done
fi

echo ""

# === Thumbnail generation ===
if [ "$THUMBNAIL" = true ]; then
  info "Generating thumbnail..."
  # Pick frame at 1/3 of duration (usually a good representative frame)
  THUMB_TIME=$((DURATION_INT / 3))
  THUMB_FILE="$OUTPUT_DIR/thumbnail.jpg"

  "$FFMPEG" -ss "$THUMB_TIME" -i "$INPUT_VIDEO" \
    -vframes 1 -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2" \
    -q:v 2 -y "$THUMB_FILE" 2>/dev/null

  if [ -f "$THUMB_FILE" ]; then
    success "Thumbnail: $THUMB_FILE (1280x720)"
  fi
  echo ""
fi

# === Generate manifest (JSON) ===
MANIFEST="$OUTPUT_DIR/manifest.json"
info "Writing manifest..."

{
  echo "{"
  echo "  \"source_video\": \"$INPUT_VIDEO\","
  echo "  \"duration_seconds\": $DURATION_INT,"
  echo "  \"extraction_date\": \"$(date -Iseconds)\","
  echo "  \"quality\": $QUALITY,"
  echo "  \"stills\": ["

  first=true
  for f in "$OUTPUT_DIR"/still_*.jpg; do
    [ -f "$f" ] || continue
    fname=$(basename "$f")

    # Extract timestamp from filename
    ts_sec=$(echo "$fname" | grep -oP '\d+(?=s\.jpg)' || echo "0")

    if [ "$first" = true ]; then
      first=false
    else
      echo ","
    fi
    printf '    {"file": "%s", "timestamp_sec": %s, "path": "%s"}' "$fname" "$ts_sec" "$f"
  done

  echo ""
  echo "  ]"
  echo "}"
} > "$MANIFEST"

success "Manifest: $MANIFEST"
echo ""

# === Summary ===
success "=== Extraction Complete ==="
success "Extracted: $EXTRACTED stills"
success "Directory: $OUTPUT_DIR"
echo ""

# List files with sizes
ls -lh "$OUTPUT_DIR"/*.jpg 2>/dev/null | awk '{printf "  %-40s %s\n", $NF, $5}'
echo ""

# Output JSON-compatible result for programmatic use
echo "---RESULT_JSON---"
echo "{\"output_dir\": \"$OUTPUT_DIR\", \"count\": $EXTRACTED, \"manifest\": \"$MANIFEST\"}"
