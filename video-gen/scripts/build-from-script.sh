#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
# build-from-script.sh — YAML script → Fish-TTS → Remotion → MP4
#
# Full pipeline: one command, one YAML, one video.
#
# Usage:
#   ./scripts/build-from-script.sh <script.yaml> [output.mp4]
#
# Environment Variables:
#   VIDEO_GEN_HEAP_MB  — Node.js heap size in MB (default: 8192)
#   VIDEO_GEN_MEDIA_DIR — Media directory for images/clips
# ──────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
FFMPEG="${HOME}/.local/bin/ffmpeg"

YAML_FILE="${1:?Usage: build-from-script.sh <script.yaml> [output.mp4]}"
OUTPUT_FILE="${2:-$(pwd)/video-output.mp4}"

# Make paths absolute
[[ "$YAML_FILE" != /* ]] && YAML_FILE="$(pwd)/$YAML_FILE"
[[ "$OUTPUT_FILE" != /* ]] && OUTPUT_FILE="$(pwd)/$OUTPUT_FILE"

# Colors
BLUE='\033[34m'; GREEN='\033[32m'; YELLOW='\033[33m'; RED='\033[31m'; NC='\033[0m'
info()    { echo -e "${BLUE}[video-gen]${NC} $1"; }
success() { echo -e "${GREEN}[video-gen]${NC} $1"; }
warn()    { echo -e "${YELLOW}[video-gen]${NC} $1"; }
error()   { echo -e "${RED}[video-gen]${NC} $1"; }

# Validate
if [ ! -f "$YAML_FILE" ]; then
  error "Script not found: $YAML_FILE"
  exit 1
fi

# ── Workspace ──────────────────────────────────────────────
WORKSPACE="/tmp/video-gen-$(date +%s)-$$"
info "═══════════════════════════════════════════"
info "  Fish-TTS Video Pipeline"
info "═══════════════════════════════════════════"
info "Script:    $YAML_FILE"
info "Workspace: $WORKSPACE"
info "Output:    $OUTPUT_FILE"
echo ""

info "Setting up workspace..."
mkdir -p "$WORKSPACE/public/tts" "$WORKSPACE/public/fonts" "$WORKSPACE/out"

# Copy source
cp -r "$SKILL_DIR/src" "$WORKSPACE/src"
cp "$SKILL_DIR/package.json" "$WORKSPACE/"
cp "$SKILL_DIR/package-lock.json" "$WORKSPACE/" 2>/dev/null || true
cp "$SKILL_DIR/tsconfig.json" "$WORKSPACE/"
cp "$SKILL_DIR/remotion.config.ts" "$WORKSPACE/" 2>/dev/null || true
cp -r "$SKILL_DIR/scripts" "$WORKSPACE/scripts"
cp "$SKILL_DIR/public/fonts/"* "$WORKSPACE/public/fonts/" 2>/dev/null || true

# Symlink node_modules
if [ -d "$SKILL_DIR/node_modules" ]; then
  ln -sf "$(readlink -f "$SKILL_DIR/node_modules")" "$WORKSPACE/node_modules"
elif [ -d "$SKILL_DIR/node_modules.ci2" ]; then
  ln -sf "$SKILL_DIR/node_modules.ci2" "$WORKSPACE/node_modules"
else
  warn "No node_modules found, running npm install..."
  cd "$WORKSPACE" && npm install 2>&1 | tail -3
fi

# Copy media
MEDIA_DIR="${VIDEO_GEN_MEDIA_DIR:-}"
if [ -n "$MEDIA_DIR" ] && [ -d "$MEDIA_DIR" ]; then
  mkdir -p "$WORKSPACE/public/media"
  cp "$MEDIA_DIR"/*.{jpg,jpeg,png,gif,mp4,webm,webp} "$WORKSPACE/public/media/" 2>/dev/null || true
  success "  Copied media from $MEDIA_DIR"
fi

# Also check config dir for media
YAML_DIR="$(dirname "$YAML_FILE")"
if [ -z "$MEDIA_DIR" ] && [ -d "$YAML_DIR/media" ]; then
  mkdir -p "$WORKSPACE/public/media"
  cp "$YAML_DIR/media/"* "$WORKSPACE/public/media/" 2>/dev/null || true
fi

TTS_DIR="$WORKSPACE/public/tts"
CONFIG_JSON="$WORKSPACE/video-config.json"

# ── Step 1/3: Parse YAML + Fish-TTS ────────────────────────
info "Step 1/3: Parsing script + generating Fish-TTS audio..."
python3 "$WORKSPACE/scripts/parse-script.py" \
  "$YAML_FILE" "$TTS_DIR" --config-out "$CONFIG_JSON"
echo ""

if [ ! -f "$CONFIG_JSON" ]; then
  error "video-config.json not generated!"
  exit 1
fi

SCENE_COUNT=$(python3 -c "import json; print(len(json.load(open('$CONFIG_JSON'))['scenes']))")
AUDIO_COUNT=$(ls -1 "$TTS_DIR"/*.mp3 2>/dev/null | wc -l)
success "  Scenes: $SCENE_COUNT, Audio files: $AUDIO_COUNT"

# ── Step 2/3: Generate metadata ────────────────────────────
info "Step 2/3: Generating render metadata..."
python3 "$WORKSPACE/scripts/generate-metadata-fish.py" \
  "$CONFIG_JSON" "$TTS_DIR" "$WORKSPACE/public"
echo ""

if [ ! -f "$WORKSPACE/public/tts-metadata.json" ]; then
  error "tts-metadata.json not generated!"
  exit 1
fi
if [ ! -f "$WORKSPACE/public/render-config.json" ]; then
  error "render-config.json not generated!"
  exit 1
fi

# ── Step 3/3: Remotion render ──────────────────────────────
info "Step 3/3: Rendering video with Remotion..."
cd "$WORKSPACE"

if [ -f "$FFMPEG" ]; then
  export PATH="${HOME}/.local/bin:$PATH"
fi

HEAP_SIZE="${VIDEO_GEN_HEAP_MB:-8192}"
export NODE_OPTIONS="--max-old-space-size=${HEAP_SIZE}"
info "  Node heap: ${HEAP_SIZE}MB"

BROWSER_EXEC=""
if command -v chromium-browser &>/dev/null; then
  BROWSER_EXEC="--browser-executable $(command -v chromium-browser)"
elif command -v chromium &>/dev/null; then
  BROWSER_EXEC="--browser-executable $(command -v chromium)"
elif command -v google-chrome &>/dev/null; then
  BROWSER_EXEC="--browser-executable $(command -v google-chrome)"
fi

RENDER_OUTPUT="$WORKSPACE/out/render.mp4"

npx remotion render src/Root.tsx VideoComposition "$RENDER_OUTPUT" \
  --codec h264 \
  --image-format jpeg \
  --concurrency 1 \
  --log warn \
  $BROWSER_EXEC

echo ""
if [ -f "$RENDER_OUTPUT" ]; then
  mkdir -p "$(dirname "$OUTPUT_FILE")"
  cp "$RENDER_OUTPUT" "$OUTPUT_FILE"

  FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
  DURATION=$("$HOME/.local/bin/ffprobe" -v error -show_entries format=duration -of csv=p=0 "$OUTPUT_FILE" 2>/dev/null || echo "?")

  success "═══════════════════════════════════════════"
  success "  Done!"
  success "  Output: $OUTPUT_FILE ($FILE_SIZE, ${DURATION}s)"
  success "  Workspace: $WORKSPACE"
  success "═══════════════════════════════════════════"
else
  error "Render failed!"
  exit 1
fi
