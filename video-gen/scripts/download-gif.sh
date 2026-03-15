#!/usr/bin/env bash
# Download GIF from Tenor by search query, convert to MP4 for Remotion
# Usage: ./download-gif.sh "search term" [output_name] [limit]
#
# Downloads the best matching GIF, converts to looping MP4
# Output goes to public/media/<output_name>.mp4
#
# Examples:
#   ./download-gif.sh "rocket launch"           → public/media/rocket-launch.mp4
#   ./download-gif.sh "coding" my-coding-gif    → public/media/my-coding-gif.mp4
#   ./download-gif.sh "cat typing" cat 3        → shows top 3, picks #1

set -euo pipefail

QUERY="${1:?Usage: download-gif.sh 'search term' [output_name] [limit]}"
OUTPUT_NAME="${2:-$(echo "$QUERY" | tr ' ' '-' | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]//g')}"
LIMIT="${3:-3}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MEDIA_DIR="$PROJECT_DIR/public/media"
mkdir -p "$MEDIA_DIR"

# Tenor v2 API
API_KEY="${TENOR_API_KEY:-AIzaSyAyimkuYQYF_FXVALexPuGQctUWRURdCYQ}"

echo "🔍 Searching Tenor: \"$QUERY\" (top $LIMIT)"

# URL-encode the query
ENCODED_QUERY=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$QUERY'))")

RESPONSE=$(curl -s "https://tenor.googleapis.com/v2/search?q=${ENCODED_QUERY}&key=${API_KEY}&limit=${LIMIT}&media_filter=mp4,gif")

# Extract mp4 URL (prefer mp4 over gif for Remotion)
RESULT=$(python3 -c "
import json, sys

data = json.loads('''$(echo "$RESPONSE" | sed "s/'/\\\\'/g")''')
results = data.get('results', [])

if not results:
    print('ERROR: No results found')
    sys.exit(1)

for i, r in enumerate(results):
    desc = r.get('content_description', 'No description')[:60]
    formats = r.get('media_formats', {})

    # Prefer mp4 format
    mp4 = formats.get('mp4', {}).get('url', '')
    gif = formats.get('gif', {}).get('url', '')
    size_kb = formats.get('mp4', formats.get('gif', {})).get('size', 0) // 1024

    print(f'  {i+1}. {desc} ({size_kb}KB)', file=sys.stderr)

# Pick first result, prefer mp4
best = results[0]
formats = best.get('media_formats', {})
mp4_url = formats.get('mp4', {}).get('url', '')
gif_url = formats.get('gif', {}).get('url', '')

if mp4_url:
    print(f'MP4|{mp4_url}')
elif gif_url:
    print(f'GIF|{gif_url}')
else:
    print('ERROR: No media URL found')
    sys.exit(1)
" 2>&1)

# Check for errors
if echo "$RESULT" | grep -q "^ERROR:"; then
    echo "❌ $RESULT"
    exit 1
fi

# Parse format and URL
MEDIA_LINE=$(echo "$RESULT" | grep -E '^(MP4|GIF)\|')
FORMAT=$(echo "$MEDIA_LINE" | cut -d'|' -f1)
URL=$(echo "$MEDIA_LINE" | cut -d'|' -f2)

OUTPUT_MP4="$MEDIA_DIR/${OUTPUT_NAME}.mp4"
TEMP_FILE="$MEDIA_DIR/${OUTPUT_NAME}.tmp"

echo ""
echo "⬇️  Downloading ($FORMAT): $URL"
curl -sL "$URL" -o "$TEMP_FILE"

if [ "$FORMAT" = "GIF" ]; then
    echo "🔄 Converting GIF → MP4 (looping, Remotion-compatible)..."
    ffmpeg -y -i "$TEMP_FILE" \
        -movflags faststart \
        -pix_fmt yuv420p \
        -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
        -c:v libx264 -preset fast -crf 18 \
        "$OUTPUT_MP4" 2>/dev/null
    rm -f "$TEMP_FILE"
else
    # Already MP4, just ensure compatibility
    ffmpeg -y -i "$TEMP_FILE" \
        -movflags faststart \
        -pix_fmt yuv420p \
        -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
        -c:v libx264 -preset fast -crf 18 \
        "$OUTPUT_MP4" 2>/dev/null
    rm -f "$TEMP_FILE"
fi

FILE_SIZE=$(du -h "$OUTPUT_MP4" | cut -f1)
echo ""
echo "✅ Saved: $OUTPUT_MP4 ($FILE_SIZE)"
echo ""
echo "📋 Use in video-config.json:"
echo "  {\"type\": \"image\", \"data\": {\"src\": \"media/${OUTPUT_NAME}.mp4\", \"title\": \"...\", \"layout\": \"centered\"}}"
