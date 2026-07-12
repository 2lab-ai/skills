#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# fish-tts — Simple TTS with voice cloning
#
# Usage:
#   fish-tts "안녕하세요, 오늘 기분이 좋아요!"
#   fish-tts "Hello world" --voice egirl
#   fish-tts "텍스트" --voice egirl --output /tmp/out.wav
#
# Voices are stored in: ~/2lab.ai/fish-tts/voices/<name>/
#   Each voice folder has: reference.mp3 + reference.txt
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

# ── Paths ──
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
FISH_DIR="$HOME/fish-speech"
VENV_PYTHON="$FISH_DIR/.venv/bin/python"
GPU_INFERENCE="$SKILL_DIR/../fish-audio/scripts/gpu-inference.py"
VOICES_DIR="$SKILL_DIR/voices"
OUTPUT_DIR="$SKILL_DIR/output"

# ── Defaults ──
VOICE="egirl"
OUTPUT=""
DEVICE="cuda"
TEMPERATURE="0.7"
TOP_P="0.9"
SEED="42"
MAX_TOKENS="2048"
TEXT=""

# ── Colors ──
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()  { echo -e "${CYAN}[fish-tts]${NC} $*"; }
ok()    { echo -e "${GREEN}[fish-tts]${NC} $*"; }
warn()  { echo -e "${YELLOW}[fish-tts]${NC} $*"; }
err()   { echo -e "${RED}[fish-tts]${NC} $*" >&2; }

# ── Usage ──
usage() {
    cat <<'EOF'
Usage: fish-tts <text> [options]

Arguments:
  <text>                    Text to synthesize (required)

Options:
  --voice <name>            Voice template (default: egirl)
  --output <path>           Output wav path (default: auto-generated)
  --device <cpu|cuda>       Device (default: cuda)
  --temperature <float>     Temperature (default: 0.7)
  --top-p <float>           Top-p (default: 0.9)
  --seed <int>              Seed (default: 42)
  --max-tokens <int>        Max new tokens (default: 2048)
  --list-voices             List available voices
  -h, --help                Show this help

Examples:
  fish-tts "오늘 날씨가 정말 좋네요!"
  fish-tts "Hello world" --voice egirl --output /tmp/hello.wav
  fish-tts --list-voices

Add a new voice:
  mkdir ~/2lab.ai/fish-tts/voices/myvoice
  cp my_audio.mp3 ~/2lab.ai/fish-tts/voices/myvoice/reference.mp3
  echo "음성의 텍스트 내용" > ~/2lab.ai/fish-tts/voices/myvoice/reference.txt
  fish-tts "테스트" --voice myvoice
EOF
    exit 0
}

list_voices() {
    info "Available voices:"
    for d in "$VOICES_DIR"/*/; do
        name="$(basename "$d")"
        mp3="$d/reference.mp3"
        txt="$d/reference.txt"
        if [[ -f "$mp3" && -f "$txt" ]]; then
            dur=$(/home/zhugehyuk/.local/bin/ffprobe -v error -show_entries format=duration -of csv=p=0 "$mp3" 2>/dev/null || echo "?")
            echo -e "  ${GREEN}$name${NC}  (${dur}s)  $txt"
        else
            echo -e "  ${YELLOW}$name${NC}  (incomplete — needs reference.mp3 + reference.txt)"
        fi
    done
    exit 0
}

# ── Parse args ──
while [[ $# -gt 0 ]]; do
    case "$1" in
        --voice)        VOICE="$2"; shift 2 ;;
        --output)       OUTPUT="$2"; shift 2 ;;
        --device)       DEVICE="$2"; shift 2 ;;
        --temperature)  TEMPERATURE="$2"; shift 2 ;;
        --top-p)        TOP_P="$2"; shift 2 ;;
        --seed)         SEED="$2"; shift 2 ;;
        --max-tokens)   MAX_TOKENS="$2"; shift 2 ;;
        --list-voices)  list_voices ;;
        -h|--help)      usage ;;
        -*)             err "Unknown option: $1"; usage ;;
        *)
            if [[ -z "$TEXT" ]]; then
                TEXT="$1"
            else
                TEXT="$TEXT $1"
            fi
            shift ;;
    esac
done

# ── Validate ──
if [[ -z "$TEXT" ]]; then
    err "No text provided!"
    usage
fi

VOICE_DIR="$VOICES_DIR/$VOICE"
REF_AUDIO="$VOICE_DIR/reference.mp3"
REF_TEXT="$VOICE_DIR/reference.txt"

if [[ ! -d "$VOICE_DIR" ]]; then
    err "Voice '$VOICE' not found!"
    info "Available voices:"
    ls -1 "$VOICES_DIR" 2>/dev/null || echo "  (none)"
    exit 1
fi

if [[ ! -f "$REF_AUDIO" ]]; then
    err "Missing: $REF_AUDIO"
    exit 1
fi

if [[ ! -f "$REF_TEXT" ]]; then
    err "Missing: $REF_TEXT"
    exit 1
fi

# ── Output path ──
if [[ -z "$OUTPUT" ]]; then
    TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$OUTPUT_DIR"
    OUTPUT="$OUTPUT_DIR/${VOICE}_${TIMESTAMP}.wav"
fi

# ── Read reference text ──
PROMPT_TEXT="$(cat "$REF_TEXT")"

# ── Select inference script ──
if [[ "$DEVICE" == "cuda" && -f "$GPU_INFERENCE" ]]; then
    SCRIPT="$GPU_INFERENCE"
    info "GPU mode (RTX 4090, max_seq_len=4096)"
else
    SCRIPT="$FISH_DIR/fish_speech/models/text2semantic/inference.py"
    info "CPU mode (slow!)"
fi

# ── Run ──
info "Voice: $VOICE"
info "Text: ${TEXT:0:80}$([ ${#TEXT} -gt 80 ] && echo '...')"
info "Output: $OUTPUT"
echo ""

cd "$FISH_DIR"
"$VENV_PYTHON" "$SCRIPT" \
    --text "<|speaker:0|>$TEXT" \
    --prompt-text "$PROMPT_TEXT" \
    --prompt-audio "$REF_AUDIO" \
    --output "$OUTPUT" \
    --checkpoint-path checkpoints/s2-pro \
    --device "$DEVICE" \
    --temperature "$TEMPERATURE" \
    --top-p "$TOP_P" \
    --seed "$SEED" \
    --max-new-tokens "$MAX_TOKENS"

# ── Result ──
echo ""
if [[ -f "$OUTPUT" ]]; then
    DUR=$(/home/zhugehyuk/.local/bin/ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUTPUT" 2>/dev/null || echo "?")
    SIZE=$(du -h "$OUTPUT" | cut -f1)
    ok "Done! ${DUR}s / ${SIZE}"
    ok "Output: $OUTPUT"
else
    err "Failed — no output file generated"
    exit 1
fi
