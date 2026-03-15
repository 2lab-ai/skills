#!/usr/bin/env bash
set -euo pipefail

# Video Generation Pipeline
# Usage: ./scripts/build-video.sh [video-config.json] [output.mp4]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_PYTHON="${HOME}/2lab.ai/.venv/bin/python3"
FFMPEG="${HOME}/.local/bin/ffmpeg"

CONFIG_FILE="${1:-${PROJECT_DIR}/video-config.json}"
OUTPUT_FILE="${2:-${PROJECT_DIR}/out/video.mp4}"
PUBLIC_DIR="${PROJECT_DIR}/public"
TTS_DIR="${PUBLIC_DIR}/tts"

# Colors
BLUE='\033[34m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
NC='\033[0m'

info()    { echo -e "${BLUE}[video-gen]${NC} $1"; }
success() { echo -e "${GREEN}[video-gen]${NC} $1"; }
warn()    { echo -e "${YELLOW}[video-gen]${NC} $1"; }
error()   { echo -e "${RED}[video-gen]${NC} $1"; }

# Validate
if [ ! -f "$CONFIG_FILE" ]; then
  error "Config not found: $CONFIG_FILE"
  exit 1
fi

if [ ! -f "$VENV_PYTHON" ]; then
  error "Python venv not found at $VENV_PYTHON"
  error "Run: python3 -m venv ~/2lab.ai/.venv && ~/2lab.ai/.venv/bin/pip install edge-tts"
  exit 1
fi

info "=== Video Generation Pipeline ==="
info "Config: $CONFIG_FILE"
info "Output: $OUTPUT_FILE"
echo ""

# Step 1: Generate TTS
info "Step 1/3: Generating TTS audio..."
mkdir -p "$TTS_DIR"
"$VENV_PYTHON" "$SCRIPT_DIR/generate-tts.py" "$CONFIG_FILE" "$TTS_DIR"
echo ""

# Step 2: Verify render data
info "Step 2/3: Verifying render data..."
if [ ! -f "$PUBLIC_DIR/render-config.json" ]; then
  error "render-config.json not generated!"
  exit 1
fi
if [ ! -f "$PUBLIC_DIR/tts-metadata.json" ]; then
  error "tts-metadata.json not generated!"
  exit 1
fi

SCENE_COUNT=$(python3 -c "import json; print(len(json.load(open('$PUBLIC_DIR/render-config.json'))['scenes']))")
AUDIO_COUNT=$(ls -1 "$TTS_DIR"/*.mp3 2>/dev/null | wc -l)
success "  Scenes: $SCENE_COUNT, Audio files: $AUDIO_COUNT"
echo ""

# Step 3: Render with Remotion
info "Step 3/3: Rendering video with Remotion..."
mkdir -p "$(dirname "$OUTPUT_FILE")"

cd "$PROJECT_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
  warn "Installing dependencies first..."
  npm install 2>&1 | tail -3
fi

# Add ffmpeg to PATH if it exists in local bin
if [ -f "$FFMPEG" ]; then
  export PATH="${HOME}/.local/bin:$PATH"
fi

# v8 heap memory fix: default 4GB, override with VIDEO_GEN_HEAP_MB
HEAP_SIZE="${VIDEO_GEN_HEAP_MB:-4096}"
export NODE_OPTIONS="--max-old-space-size=${HEAP_SIZE}"
info "Node heap limit: ${HEAP_SIZE}MB"

BROWSER_EXEC=""
if command -v chromium-browser &>/dev/null; then
  BROWSER_EXEC="--browser-executable $(command -v chromium-browser)"
elif command -v chromium &>/dev/null; then
  BROWSER_EXEC="--browser-executable $(command -v chromium)"
elif command -v google-chrome &>/dev/null; then
  BROWSER_EXEC="--browser-executable $(command -v google-chrome)"
fi

npx remotion render src/Root.tsx VideoComposition "$OUTPUT_FILE" \
  --codec h264 \
  --image-format jpeg \
  --concurrency 1 \
  --log warn \
  $BROWSER_EXEC

echo ""
if [ -f "$OUTPUT_FILE" ]; then
  FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
  success "=== Done! ==="
  success "Output: $OUTPUT_FILE ($FILE_SIZE)"
else
  error "Render failed - output not found"
  exit 1
fi
