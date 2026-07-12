#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
# render-final.sh — Final render after verification approval
#
# Usage:
#   WORKSPACE=/tmp/video-pipeline-xxx bash render-final.sh [output.mp4]
#   OR
#   bash render-final.sh [output.mp4] [workspace_dir]
# ──────────────────────────────────────────────────────────────
set -euo pipefail

BLUE='\033[34m'; GREEN='\033[32m'; RED='\033[31m'; CYAN='\033[36m'; NC='\033[0m'
info()    { echo -e "${BLUE}[render]${NC} $1"; }
success() { echo -e "${GREEN}[render]${NC} $1"; }
error()   { echo -e "${RED}[render]${NC} $1"; }

OUTPUT_FILE="${1:-video-output.mp4}"
WORKSPACE="${2:-${WORKSPACE:-}}"

# Try to find workspace from verify dir
if [ -z "$WORKSPACE" ]; then
  for vdir in /tmp/scene-verify-*; do
    if [ -f "$vdir/.workspace" ]; then
      WORKSPACE=$(cat "$vdir/.workspace")
      break
    fi
  done
fi

if [ -z "$WORKSPACE" ] || [ ! -d "$WORKSPACE" ]; then
  error "Workspace not found. Set WORKSPACE env var or pass as argument."
  exit 1
fi

[[ "$OUTPUT_FILE" != /* ]] && OUTPUT_FILE="$(pwd)/$OUTPUT_FILE"

info "Workspace: $WORKSPACE"
info "Output:    $OUTPUT_FILE"

cd "$WORKSPACE"

if [ -f "$HOME/.local/bin/ffmpeg" ]; then
  export PATH="${HOME}/.local/bin:$PATH"
fi

HEAP_SIZE="${VIDEO_GEN_HEAP_MB:-8192}"
export NODE_OPTIONS="--max-old-space-size=${HEAP_SIZE}"

BROWSER_EXEC=""
if command -v chromium-browser &>/dev/null; then
  BROWSER_EXEC="--browser-executable $(command -v chromium-browser)"
elif command -v chromium &>/dev/null; then
  BROWSER_EXEC="--browser-executable $(command -v chromium)"
elif command -v google-chrome &>/dev/null; then
  BROWSER_EXEC="--browser-executable $(command -v google-chrome)"
fi

RENDER_OUTPUT="$WORKSPACE/out/render.mp4"

info "Rendering final video..."
npx remotion render src/Root.tsx VideoComposition "$RENDER_OUTPUT" \
  --codec h264 \
  --image-format jpeg \
  --concurrency 1 \
  --log warn \
  $BROWSER_EXEC

if [ -f "$RENDER_OUTPUT" ]; then
  mkdir -p "$(dirname "$OUTPUT_FILE")"
  cp "$RENDER_OUTPUT" "$OUTPUT_FILE"
  FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
  DURATION=$("$HOME/.local/bin/ffprobe" -v error -show_entries format=duration -of csv=p=0 "$OUTPUT_FILE" 2>/dev/null || echo "?")

  success "═══════════════════════════════════════════"
  success "  Done!"
  success "  Output: $OUTPUT_FILE ($FILE_SIZE, ${DURATION}s)"
  success "═══════════════════════════════════════════"
else
  error "Render failed!"
  exit 1
fi
