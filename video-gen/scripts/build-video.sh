#!/usr/bin/env bash
set -euo pipefail

# Video Generation Pipeline (Workspace Pattern)
# Usage: ./scripts/build-video.sh <video-config.json> [output.mp4]
#
# Creates a temporary workspace in /tmp, copies skill skeleton,
# runs TTS + Remotion render there, then copies final mp4 to output path.
#
# Environment Variables:
#   VIDEO_GEN_MEDIA_DIR  - Directory containing media files (images, videos)
#                          to copy into workspace's public/media/
#   VIDEO_GEN_HEAP_MB    - Node.js heap size in MB (default: 4096)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
VENV_PYTHON="${HOME}/2lab.ai/.venv/bin/python3"
FFMPEG="${HOME}/.local/bin/ffmpeg"

CONFIG_FILE="${1:?Usage: build-video.sh <config.json> [output.mp4]}"
OUTPUT_FILE="${2:-$(pwd)/video-output.mp4}"

# Make config path absolute
[[ "$CONFIG_FILE" != /* ]] && CONFIG_FILE="$(pwd)/$CONFIG_FILE"
[[ "$OUTPUT_FILE" != /* ]] && OUTPUT_FILE="$(pwd)/$OUTPUT_FILE"

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
  exit 1
fi

# === Create workspace ===
WORKSPACE="/tmp/video-gen-$(date +%s)-$$"
info "=== Video Generation Pipeline ==="
info "Skill:     $SKILL_DIR"
info "Config:    $CONFIG_FILE"
info "Workspace: $WORKSPACE"
info "Output:    $OUTPUT_FILE"
echo ""

info "Setting up workspace..."
mkdir -p "$WORKSPACE/public/tts" "$WORKSPACE/public/fonts" "$WORKSPACE/out"

# Copy source code (lightweight — no generated files)
cp -r "$SKILL_DIR/src" "$WORKSPACE/src"
cp "$SKILL_DIR/package.json" "$WORKSPACE/"
cp "$SKILL_DIR/package-lock.json" "$WORKSPACE/" 2>/dev/null || true
cp "$SKILL_DIR/tsconfig.json" "$WORKSPACE/"
cp "$SKILL_DIR/remotion.config.ts" "$WORKSPACE/" 2>/dev/null || true

# Copy fonts (required for rendering)
cp "$SKILL_DIR/public/fonts/"* "$WORKSPACE/public/fonts/" 2>/dev/null || true

# Copy scripts
cp -r "$SKILL_DIR/scripts" "$WORKSPACE/scripts"

# Symlink node_modules (don't copy 200MB+)
if [ -d "$SKILL_DIR/node_modules" ] || [ -L "$SKILL_DIR/node_modules" ]; then
  ln -sf "$(readlink -f "$SKILL_DIR/node_modules")" "$WORKSPACE/node_modules"
elif [ -d "$SKILL_DIR/node_modules.ci2" ]; then
  ln -sf "$SKILL_DIR/node_modules.ci2" "$WORKSPACE/node_modules"
else
  warn "No node_modules found, running npm install..."
  cd "$WORKSPACE" && npm install 2>&1 | tail -3
fi

# Copy config to workspace
cp "$CONFIG_FILE" "$WORKSPACE/video-config.json"

# Copy media files if VIDEO_GEN_MEDIA_DIR is set
MEDIA_DIR="${VIDEO_GEN_MEDIA_DIR:-}"
if [ -n "$MEDIA_DIR" ] && [ -d "$MEDIA_DIR" ]; then
  mkdir -p "$WORKSPACE/public/media"
  MEDIA_COUNT=$(ls -1 "$MEDIA_DIR"/*.{jpg,jpeg,png,gif,mp4,webm,webp} 2>/dev/null | wc -l || echo 0)
  if [ "$MEDIA_COUNT" -gt 0 ]; then
    cp "$MEDIA_DIR"/*.{jpg,jpeg,png,gif,mp4,webm,webp} "$WORKSPACE/public/media/" 2>/dev/null || true
    success "  Copied $MEDIA_COUNT media files from $MEDIA_DIR"
  else
    warn "  VIDEO_GEN_MEDIA_DIR set but no media files found in $MEDIA_DIR"
  fi
elif [ -n "$MEDIA_DIR" ]; then
  warn "  VIDEO_GEN_MEDIA_DIR=$MEDIA_DIR does not exist"
fi

# Also check if config references media/ paths and auto-detect media dir from config location
if [ -z "$MEDIA_DIR" ]; then
  CONFIG_DIR="$(dirname "$CONFIG_FILE")"
  if [ -d "$CONFIG_DIR/media" ]; then
    mkdir -p "$WORKSPACE/public/media"
    cp "$CONFIG_DIR/media/"* "$WORKSPACE/public/media/" 2>/dev/null || true
    AUTO_COUNT=$(ls -1 "$WORKSPACE/public/media/"* 2>/dev/null | wc -l || echo 0)
    if [ "$AUTO_COUNT" -gt 0 ]; then
      success "  Auto-detected media dir: $CONFIG_DIR/media/ ($AUTO_COUNT files)"
    fi
  fi
fi

# Copy skill's own public/media if exists (fallback)
if [ -d "$SKILL_DIR/public/media" ]; then
  mkdir -p "$WORKSPACE/public/media"
  cp "$SKILL_DIR/public/media/"* "$WORKSPACE/public/media/" 2>/dev/null || true
fi

PUBLIC_DIR="$WORKSPACE/public"
TTS_DIR="$PUBLIC_DIR/tts"

# === Step 1: Generate TTS ===
info "Step 1/3: Generating TTS audio..."
"$VENV_PYTHON" "$WORKSPACE/scripts/generate-tts.py" "$WORKSPACE/video-config.json" "$TTS_DIR"
echo ""

# === Step 2: Verify render data ===
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

# === Step 3: Render with Remotion ===
info "Step 3/3: Rendering video with Remotion..."
cd "$WORKSPACE"

# Add ffmpeg to PATH if it exists in local bin
if [ -f "$FFMPEG" ]; then
  export PATH="${HOME}/.local/bin:$PATH"
fi

# v8 heap memory fix
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

RENDER_OUTPUT="$WORKSPACE/out/render.mp4"

npx remotion render src/Root.tsx VideoComposition "$RENDER_OUTPUT" \
  --codec h264 \
  --image-format jpeg \
  --concurrency 1 \
  --log warn \
  $BROWSER_EXEC

echo ""
if [ -f "$RENDER_OUTPUT" ]; then
  # Copy final output to requested location
  mkdir -p "$(dirname "$OUTPUT_FILE")"
  cp "$RENDER_OUTPUT" "$OUTPUT_FILE"

  FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
  success "=== Done! ==="
  success "Output: $OUTPUT_FILE ($FILE_SIZE)"
  success "Workspace: $WORKSPACE (can be cleaned up)"
else
  error "Render failed - output not found"
  exit 1
fi
