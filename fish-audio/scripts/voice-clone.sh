#!/usr/bin/env bash
set -euo pipefail

# Fish Audio S2 — Voice Cloning Wrapper
# Usage: voice-clone.sh --source-audio <wav> --source-text <text> --target-text <text> --output <wav>
#
# Wraps the fish-speech inference pipeline into a single command.

FISH_DIR="${HOME}/fish-speech"
VENV_PYTHON="${FISH_DIR}/.venv/bin/python"
CHECKPOINT="${FISH_DIR}/checkpoints/s2-pro"
INFERENCE_SCRIPT_ORIG="${FISH_DIR}/fish_speech/models/text2semantic/inference.py"
GPU_INFERENCE_SCRIPT="$(dirname "$0")/gpu-inference.py"

# Colors
BLUE='\033[34m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
NC='\033[0m'

info()    { echo -e "${BLUE}[fish-audio]${NC} $1"; }
success() { echo -e "${GREEN}[fish-audio]${NC} $1"; }
warn()    { echo -e "${YELLOW}[fish-audio]${NC} $1"; }
error()   { echo -e "${RED}[fish-audio]${NC} $1"; }

# Defaults
SOURCE_AUDIO=""
SOURCE_TEXT=""
TARGET_TEXT=""
OUTPUT=""
DEVICE=""
TEMPERATURE=0.7
TOP_P=0.9
TOP_K=30
SEED=42
CHUNK_LENGTH=300
MAX_NEW_TOKENS=0

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --source-audio) SOURCE_AUDIO="$2"; shift 2 ;;
    --source-text)  SOURCE_TEXT="$2"; shift 2 ;;
    --target-text)  TARGET_TEXT="$2"; shift 2 ;;
    --output|-o)    OUTPUT="$2"; shift 2 ;;
    --device)       DEVICE="$2"; shift 2 ;;
    --temperature)  TEMPERATURE="$2"; shift 2 ;;
    --top-p)        TOP_P="$2"; shift 2 ;;
    --top-k)        TOP_K="$2"; shift 2 ;;
    --seed)         SEED="$2"; shift 2 ;;
    --chunk-length) CHUNK_LENGTH="$2"; shift 2 ;;
    --max-new-tokens) MAX_NEW_TOKENS="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: voice-clone.sh --source-audio <wav> --source-text <text> --target-text <text> --output <wav>"
      echo ""
      echo "Required:"
      echo "  --source-audio   Source audio file (10-30s WAV/MP3)"
      echo "  --source-text    Text content of source audio"
      echo "  --target-text    Text to generate in cloned voice"
      echo "  --output         Output WAV file path"
      echo ""
      echo "Optional:"
      echo "  --device         cpu or cuda (auto-detect)"
      echo "  --temperature    Sampling temp (default: 0.7)"
      echo "  --top-p          Top-p sampling (default: 0.9)"
      echo "  --seed           Random seed (default: 42)"
      exit 0
      ;;
    *) error "Unknown option: $1"; exit 1 ;;
  esac
done

# Validate required args
if [ -z "$SOURCE_AUDIO" ]; then error "Missing --source-audio"; exit 1; fi
if [ -z "$SOURCE_TEXT" ];  then error "Missing --source-text"; exit 1; fi
if [ -z "$TARGET_TEXT" ];  then error "Missing --target-text"; exit 1; fi
if [ -z "$OUTPUT" ];       then error "Missing --output"; exit 1; fi

# Validate files
if [ ! -f "$SOURCE_AUDIO" ]; then error "Source audio not found: $SOURCE_AUDIO"; exit 1; fi
if [ ! -f "$VENV_PYTHON" ]; then error "Python venv not found: $VENV_PYTHON"; exit 1; fi
if [ ! -d "$CHECKPOINT" ]; then error "Checkpoint not found: $CHECKPOINT (run: huggingface-cli download fishaudio/s2-pro --local-dir $CHECKPOINT)"; exit 1; fi

# Make paths absolute
[[ "$SOURCE_AUDIO" != /* ]] && SOURCE_AUDIO="$(pwd)/$SOURCE_AUDIO"
[[ "$OUTPUT" != /* ]] && OUTPUT="$(pwd)/$OUTPUT"

# Auto-detect device
if [ -z "$DEVICE" ]; then
  if "$VENV_PYTHON" -c "import torch; print(torch.cuda.is_available())" 2>/dev/null | grep -q "True"; then
    DEVICE="cuda"
  else
    DEVICE="cpu"
  fi
fi

info "=== Fish Audio S2 — Voice Cloning ==="
info "Source audio: $SOURCE_AUDIO"
info "Source text:  ${SOURCE_TEXT:0:80}..."
info "Target text:  ${TARGET_TEXT:0:80}..."
info "Output:       $OUTPUT"
info "Device:       $DEVICE"
info "Temperature:  $TEMPERATURE"
info "Seed:         $SEED"
echo ""

# Create output directory
mkdir -p "$(dirname "$OUTPUT")"

# Create temp dir for intermediate files
WORKDIR=$(mktemp -d /tmp/fish-audio-XXXXXX)
info "Workspace: $WORKDIR"

# Prepare target text with speaker tag if not present
TAGGED_TARGET="$TARGET_TEXT"
if ! echo "$TARGET_TEXT" | grep -q '<|speaker:'; then
  TAGGED_TARGET="<|speaker:0|>${TARGET_TEXT}"
fi

# Convert source to WAV if needed (ensure 16-bit PCM for compatibility)
SOURCE_WAV="$SOURCE_AUDIO"
if [[ "$SOURCE_AUDIO" != *.wav ]]; then
  info "Converting source audio to WAV..."
  FFMPEG="${HOME}/.local/bin/ffmpeg"
  command -v "$FFMPEG" &>/dev/null || FFMPEG="ffmpeg"
  SOURCE_WAV="$WORKDIR/source.wav"
  "$FFMPEG" -i "$SOURCE_AUDIO" -ar 44100 -ac 1 -y "$SOURCE_WAV" 2>/dev/null
  success "Converted to: $SOURCE_WAV"
fi

# Run inference
info "Starting inference..."
START_TIME=$(date +%s)

cd "$FISH_DIR"

# Use GPU-optimized wrapper if device is cuda (patches max_seq_len for 16GB VRAM)
if [ "$DEVICE" = "cuda" ] && [ -f "$GPU_INFERENCE_SCRIPT" ]; then
  ACTIVE_SCRIPT="$GPU_INFERENCE_SCRIPT"
  info "Using GPU-optimized inference (max_seq_len=4096)"
else
  ACTIVE_SCRIPT="$INFERENCE_SCRIPT_ORIG"
fi

"$VENV_PYTHON" "$ACTIVE_SCRIPT" \
  --text "$TAGGED_TARGET" \
  --prompt-text "$SOURCE_TEXT" \
  --prompt-audio "$SOURCE_WAV" \
  --output "$OUTPUT" \
  --checkpoint-path "$CHECKPOINT" \
  --device "$DEVICE" \
  --temperature "$TEMPERATURE" \
  --top-p "$TOP_P" \
  --top-k "$TOP_K" \
  --seed "$SEED" \
  --chunk-length "$CHUNK_LENGTH" \
  --max-new-tokens "$MAX_NEW_TOKENS" \
  --output-dir "$WORKDIR" \
  2>&1

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo ""
if [ -f "$OUTPUT" ]; then
  FILE_SIZE=$(du -h "$OUTPUT" | cut -f1)
  DURATION=$("${HOME}/.local/bin/ffprobe" -v error -show_entries format=duration \
    -of default=noprint_wrappers=1:nokey=1 "$OUTPUT" 2>/dev/null || echo "unknown")

  success "=== Voice Cloning Complete ==="
  success "Output:   $OUTPUT ($FILE_SIZE)"
  success "Duration: ${DURATION}s"
  success "Time:     ${ELAPSED}s"
  success "Workspace: $WORKDIR"

  echo ""
  echo "---RESULT_JSON---"
  echo "{\"output\": \"$OUTPUT\", \"duration_sec\": \"$DURATION\", \"elapsed_sec\": $ELAPSED, \"device\": \"$DEVICE\"}"
else
  error "Inference failed — no output file generated"
  error "Check logs above for errors"
  error "Workspace: $WORKDIR"
  exit 1
fi
