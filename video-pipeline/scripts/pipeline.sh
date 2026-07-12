#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
# pipeline.sh — Full video pipeline: Design → TTS → Verify → Render
#
# Orchestrates:
#   Phase 1: UI/UX Pro Max design system generation
#   Phase 2: YAML script → Fish-TTS audio (via video-gen)
#   Phase 3: Scene-by-scene still verification
#   Phase 4: Final Remotion render (only after verification)
#
# Usage:
#   ./scripts/pipeline.sh <script.yaml> [output.mp4]
#
# Options (env vars):
#   SKIP_DESIGN=1      — Skip Phase 1 (design system)
#   SKIP_VERIFY=1      — Skip Phase 3 (verification stills)
#   DESIGN_QUERY="..." — Custom query for design system
#   DESIGN_PROJECT="..." — Project name for design system
#   VIDEO_GEN_DIR="..." — Path to video-gen skill (default: ../video-gen)
# ──────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
SKILLS_DIR="$(dirname "$SKILL_DIR")"
VIDEO_GEN_DIR="${VIDEO_GEN_DIR:-$SKILLS_DIR/video-gen}"
UIUXPRO_DIR="$HOME/2lab.ai/.claude/skills/ui-ux-pro-max"
FFMPEG="${HOME}/.local/bin/ffmpeg"

YAML_FILE="${1:?Usage: pipeline.sh <script.yaml> [output.mp4]}"
OUTPUT_FILE="${2:-$(pwd)/video-output.mp4}"

# Make paths absolute
[[ "$YAML_FILE" != /* ]] && YAML_FILE="$(pwd)/$YAML_FILE"
[[ "$OUTPUT_FILE" != /* ]] && OUTPUT_FILE="$(pwd)/$OUTPUT_FILE"

# Colors
BLUE='\033[34m'; GREEN='\033[32m'; YELLOW='\033[33m'; RED='\033[31m'; CYAN='\033[36m'; NC='\033[0m'
info()    { echo -e "${BLUE}[pipeline]${NC} $1"; }
success() { echo -e "${GREEN}[pipeline]${NC} $1"; }
warn()    { echo -e "${YELLOW}[pipeline]${NC} $1"; }
error()   { echo -e "${RED}[pipeline]${NC} $1"; }
phase()   { echo -e "${CYAN}[pipeline]${NC} ═══ $1 ═══"; }

echo ""
phase "VIDEO PIPELINE v1.0"
info "Script:    $YAML_FILE"
info "Output:    $OUTPUT_FILE"
echo ""

# ── Phase 1: Design System ──────────────────────────────────
if [ "${SKIP_DESIGN:-0}" != "1" ]; then
  phase "Phase 1/4: UI/UX Pro Max Design System"

  QUERY="${DESIGN_QUERY:-$(python3 -c "
import yaml, sys
with open('$YAML_FILE') as f:
    d = yaml.safe_load(f)
title = d.get('title', '')
theme = d.get('theme', '')
print(f'{title} {theme} dark futuristic technology')
")}"
  PROJECT="${DESIGN_PROJECT:-$(python3 -c "
import yaml
with open('$YAML_FILE') as f:
    d = yaml.safe_load(f)
print(d.get('title', 'Video Project'))
")}"

  info "Query: $QUERY"
  info "Project: $PROJECT"

  if [ -f "$UIUXPRO_DIR/scripts/search.py" ]; then
    python3 "$UIUXPRO_DIR/scripts/search.py" "$QUERY" --design-system -p "$PROJECT" 2>&1
    echo ""
    success "Design system generated"
  else
    warn "UI/UX Pro Max not found at $UIUXPRO_DIR"
    warn "Skipping design system generation"
  fi
else
  info "Phase 1: SKIPPED (SKIP_DESIGN=1)"
fi
echo ""

# ── Phase 2: Parse YAML + Fish-TTS ──────────────────────────
phase "Phase 2/4: YAML Parse + Fish-TTS Audio"

WORKSPACE="/tmp/video-pipeline-$(date +%s)-$$"
mkdir -p "$WORKSPACE/public/tts" "$WORKSPACE/public/fonts" "$WORKSPACE/out"

# Copy video-gen source
cp -r "$VIDEO_GEN_DIR/src" "$WORKSPACE/src"
cp "$VIDEO_GEN_DIR/package.json" "$WORKSPACE/"
cp "$VIDEO_GEN_DIR/package-lock.json" "$WORKSPACE/" 2>/dev/null || true
cp "$VIDEO_GEN_DIR/tsconfig.json" "$WORKSPACE/"
cp "$VIDEO_GEN_DIR/remotion.config.ts" "$WORKSPACE/" 2>/dev/null || true
cp -r "$VIDEO_GEN_DIR/scripts" "$WORKSPACE/scripts"
cp "$VIDEO_GEN_DIR/public/fonts/"* "$WORKSPACE/public/fonts/" 2>/dev/null || true

# Symlink node_modules
if [ -d "$VIDEO_GEN_DIR/node_modules" ]; then
  ln -sf "$(readlink -f "$VIDEO_GEN_DIR/node_modules")" "$WORKSPACE/node_modules"
elif [ -d "$VIDEO_GEN_DIR/node_modules.ci2" ]; then
  ln -sf "$VIDEO_GEN_DIR/node_modules.ci2" "$WORKSPACE/node_modules"
fi

# Copy media if exists
YAML_DIR="$(dirname "$YAML_FILE")"
if [ -d "$YAML_DIR/media" ]; then
  mkdir -p "$WORKSPACE/public/media"
  cp "$YAML_DIR/media/"* "$WORKSPACE/public/media/" 2>/dev/null || true
fi

TTS_DIR="$WORKSPACE/public/tts"
CONFIG_JSON="$WORKSPACE/video-config.json"

info "Workspace: $WORKSPACE"
info "Parsing script + generating TTS..."

python3 "$WORKSPACE/scripts/parse-script.py" \
  "$YAML_FILE" "$TTS_DIR" --config-out "$CONFIG_JSON"

if [ ! -f "$CONFIG_JSON" ]; then
  error "video-config.json not generated!"
  exit 1
fi

SCENE_COUNT=$(python3 -c "import json; print(len(json.load(open('$CONFIG_JSON'))['scenes']))")
AUDIO_COUNT=$(ls -1 "$TTS_DIR"/*.mp3 2>/dev/null | wc -l)
success "Scenes: $SCENE_COUNT, Audio files: $AUDIO_COUNT"

# Generate metadata
python3 "$WORKSPACE/scripts/generate-metadata-fish.py" \
  "$CONFIG_JSON" "$TTS_DIR" "$WORKSPACE/public"

success "Phase 2 complete"
echo ""

# ── Phase 3: Scene Verification ──────────────────────────────
VERIFY_DIR="/tmp/scene-verify-$$"

if [ "${SKIP_VERIFY:-0}" != "1" ]; then
  phase "Phase 3/4: Scene-by-Scene Verification"
  info "Rendering still images for each scene..."

  bash "$SKILL_DIR/scripts/verify-scenes.sh" "$WORKSPACE" "$VERIFY_DIR"

  echo ""
  info "══════════════════════════════════════════════════════"
  info "  VERIFICATION CHECKPOINT"
  info "══════════════════════════════════════════════════════"
  info ""
  info "  Still images saved to: $VERIFY_DIR"
  info "  Review each scene-XXX.png before proceeding."
  info ""
  info "  To proceed to final render:"
  info "    WORKSPACE=$WORKSPACE bash $SKILL_DIR/scripts/render-final.sh $OUTPUT_FILE"
  info ""
  info "  Manifest: $VERIFY_DIR/manifest.json"
  info "══════════════════════════════════════════════════════"

  # Save workspace path for render-final.sh
  echo "$WORKSPACE" > "$VERIFY_DIR/.workspace"
  echo "$OUTPUT_FILE" > "$VERIFY_DIR/.output"
else
  info "Phase 3: SKIPPED (SKIP_VERIFY=1)"
fi
echo ""

# ── Phase 4: Final Render ────────────────────────────────────
if [ "${SKIP_VERIFY:-0}" == "1" ]; then
  phase "Phase 4/4: Final Remotion Render"

  cd "$WORKSPACE"
  if [ -f "$FFMPEG" ]; then
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
    success "  Pipeline complete!"
    success "  Output: $OUTPUT_FILE ($FILE_SIZE, ${DURATION}s)"
    success "═══════════════════════════════════════════"
  else
    error "Render failed!"
    exit 1
  fi
else
  info "Phase 4: PAUSED — waiting for verification approval"
  info "After reviewing stills, run render-final.sh"
fi
