#!/usr/bin/env bash
# dub.sh — yt-dub end-to-end 오케스트레이터
# 사용법: dub.sh <YOUTUBE_URL> [--project-id <id>] [--engine codex|gemini|claude] [--model large-v3] [--device cuda] [--max-seconds N] [--resume]
set -euo pipefail

URL=""
PROJECT_ID=""
ENGINE=""
MODEL=""
DEVICE=""
MAX_SECONDS=""
RESUME=0

while [ $# -gt 0 ]; do
  case "$1" in
    --project-id) PROJECT_ID="$2"; shift 2;;
    --engine)     ENGINE="$2"; shift 2;;
    --model)      MODEL="$2"; shift 2;;
    --device)     DEVICE="$2"; shift 2;;
    --max-seconds) MAX_SECONDS="$2"; shift 2;;
    --resume)     RESUME=1; shift;;
    -h|--help)
      sed -n '1,3p' "$0"; exit 0;;
    *)
      if [ -z "$URL" ]; then URL="$1"; else echo "[error] 알 수 없는 인자: $1" >&2; exit 2; fi
      shift;;
  esac
done

if [ -z "$URL" ]; then
  echo "usage: dub.sh <YOUTUBE_URL> [...]" >&2
  exit 2
fi

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
if [ -f "$SKILL_DIR/.env" ]; then
  set -a; . "$SKILL_DIR/.env"; set +a
fi

PROJECTS_DIR="${YT_DUB_PROJECTS_DIR:-$HOME/yt-dub-projects}"
mkdir -p "$PROJECTS_DIR"

# project_id 결정: URL 의 v= 파라미터 또는 timestamp
if [ -z "$PROJECT_ID" ]; then
  PROJECT_ID="$(echo "$URL" | sed -nE 's#.*[?&]v=([A-Za-z0-9_-]+).*#\1#p')"
  if [ -z "$PROJECT_ID" ]; then
    PROJECT_ID="$(echo "$URL" | sed -nE 's#.*youtu\.be/([A-Za-z0-9_-]+).*#\1#p')"
  fi
  if [ -z "$PROJECT_ID" ]; then
    PROJECT_ID="$(date +%Y%m%d_%H%M%S)"
  fi
fi

PROJECT_DIR="$PROJECTS_DIR/$PROJECT_ID"
mkdir -p "$PROJECT_DIR"
echo "[dub] project = $PROJECT_DIR"

PY="${YT_DUB_PYTHON:-$HOME/2lab.ai/.venv/bin/python3}"
if [ ! -x "$PY" ]; then PY="$(command -v python3)"; fi

# CUDA libs for faster-whisper (ctranslate2 needs cublas + cudnn from pip site-packages)
VENV_NV="$HOME/2lab.ai/.venv/lib/python3.12/site-packages/nvidia"
if [ -d "$VENV_NV/cublas/lib" ]; then
  export LD_LIBRARY_PATH="$VENV_NV/cublas/lib:$VENV_NV/cudnn/lib:${LD_LIBRARY_PATH:-}"
fi

# ── 1. 다운로드 ────────────────────────────────────────────────────────
if [ "$RESUME" -eq 0 ] || [ ! -f "$PROJECT_DIR/1_source/video.mp4" ]; then
  bash "$SKILL_DIR/scripts/download.sh" "$PROJECT_DIR" "$URL"
else
  echo "[resume] 1_source 건너뜀"
fi

# --max-seconds 트림 (디버그용)
if [ -n "$MAX_SECONDS" ]; then
  echo "[trim] $MAX_SECONDS s"
  FFMPEG="${FFMPEG_BIN:-$(command -v ffmpeg || echo "$HOME/.local/bin/ffmpeg")}"
  for f in video.mp4 audio.mp3; do
    src="$PROJECT_DIR/1_source/$f"
    bak="$PROJECT_DIR/1_source/full.$f"
    [ -f "$src" ] || continue
    if [ ! -f "$bak" ]; then mv "$src" "$bak"; fi
    "$FFMPEG" -loglevel error -y -i "$bak" -t "$MAX_SECONDS" -c copy "$src"
  done
fi

# ── 2. STT ────────────────────────────────────────────────────────────
if [ "$RESUME" -eq 0 ] || [ ! -f "$PROJECT_DIR/2_transcript/segments.json" ]; then
  TR_ARGS=()
  [ -n "$MODEL"  ] && TR_ARGS+=(--model "$MODEL")
  [ -n "$DEVICE" ] && TR_ARGS+=(--device "$DEVICE")
  "$PY" "$SKILL_DIR/scripts/transcribe.py" "$PROJECT_DIR" "${TR_ARGS[@]}"
else
  echo "[resume] 2_transcript 건너뜀"
fi

# ── 3. 번역 ───────────────────────────────────────────────────────────
if [ "$RESUME" -eq 0 ] || [ ! -f "$PROJECT_DIR/3_translation/sentences.json" ]; then
  T_ARGS=()
  [ -n "$ENGINE" ] && T_ARGS+=(--engine "$ENGINE")
  "$PY" "$SKILL_DIR/scripts/translate.py" "$PROJECT_DIR" "${T_ARGS[@]}"
else
  echo "[resume] 3_translation 건너뜀"
fi

# ── 4. 화자 분석 ──────────────────────────────────────────────────────
if [ "$RESUME" -eq 0 ] || [ ! -f "$PROJECT_DIR/4_synth/speakers.json" ]; then
  "$PY" "$SKILL_DIR/scripts/analyze_speakers.py" "$PROJECT_DIR"
else
  echo "[resume] speakers 건너뜀"
fi

# ── 5. TTS ────────────────────────────────────────────────────────────
SYN_ARGS=()
[ "$RESUME" -eq 1 ] && SYN_ARGS+=(--resume)
"$PY" "$SKILL_DIR/scripts/synthesize.py" "$PROJECT_DIR" "${SYN_ARGS[@]}"

# ── 6. 타임라인 배치 ───────────────────────────────────────────────────
"$PY" "$SKILL_DIR/scripts/place_timeline.py" "$PROJECT_DIR"

# ── 7. mux ────────────────────────────────────────────────────────────
bash "$SKILL_DIR/scripts/finalize.sh" "$PROJECT_DIR"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  ✓ 더빙 완료"
echo "  → $PROJECT_DIR/6_final/dubbed_video.mp4"
echo "═══════════════════════════════════════════════════════════"
