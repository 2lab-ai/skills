#!/usr/bin/env bash
# finalize.sh — 원본 video + dubbed_audio.wav 를 mux 해서 6_final/dubbed_video.mp4
# 사용법: finalize.sh <project_dir>
set -euo pipefail

PROJECT_DIR="${1:?usage: finalize.sh <project_dir>}"

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
if [ -f "$SKILL_DIR/.env" ]; then
  set -a; . "$SKILL_DIR/.env"; set +a
fi

FFMPEG="${FFMPEG_BIN:-$(command -v ffmpeg || echo "$HOME/.local/bin/ffmpeg")}"
if [ ! -x "$FFMPEG" ]; then
  echo "[error] ffmpeg 없음: $FFMPEG" >&2
  exit 4
fi

VIDEO="$PROJECT_DIR/1_source/video.mp4"
DUB_WAV="$PROJECT_DIR/5_intermediate/dubbed_audio.wav"
OUT_DIR="$PROJECT_DIR/6_final"
OUT_MP4="$OUT_DIR/dubbed_video.mp4"

for f in "$VIDEO" "$DUB_WAV"; do
  if [ ! -f "$f" ]; then
    echo "[error] 필수 파일 없음: $f" >&2
    exit 4
  fi
done

mkdir -p "$OUT_DIR"

echo "[mux] $VIDEO + $DUB_WAV → $OUT_MP4"
"$FFMPEG" -loglevel error -y \
  -i "$VIDEO" \
  -i "$DUB_WAV" \
  -map 0:v:0 -map 1:a:0 \
  -c:v copy \
  -c:a aac -b:a 192k -ar 44100 -ac 2 \
  -shortest \
  -movflags +faststart \
  "$OUT_MP4"

ls -la "$OUT_MP4"
echo "[ok] dubbed_video → $OUT_MP4"
