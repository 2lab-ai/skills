#!/usr/bin/env bash
# download.sh — yt-dlp 로 원본 비디오 + 오디오 추출
# 사용법: download.sh <project_dir> <URL>
set -euo pipefail

PROJECT_DIR="${1:?usage: download.sh <project_dir> <URL>}"
URL="${2:?missing URL}"

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
if [ -f "$SKILL_DIR/.env" ]; then
  set -a; . "$SKILL_DIR/.env"; set +a
fi

YTDLP="${YTDLP_BIN:-$(command -v yt-dlp || echo "$HOME/.local/bin/yt-dlp")}"
if [ ! -x "$YTDLP" ]; then
  echo "[error] yt-dlp 없음: $YTDLP" >&2
  exit 4
fi

OUT_DIR="$PROJECT_DIR/1_source"
mkdir -p "$OUT_DIR"

echo "[yt-dlp] → $OUT_DIR"
"$YTDLP" \
  --no-playlist \
  --no-warnings \
  -f "bv*[height<=1080]+ba/b" \
  --merge-output-format mp4 \
  --extract-audio \
  --audio-format mp3 \
  --audio-quality 192K \
  --keep-video \
  -o "$OUT_DIR/full.%(ext)s" \
  "$URL"

# 결과 파일을 video.mp4 / audio.mp3 로 표준화
if [ -f "$OUT_DIR/full.mp4" ]; then
  mv -n "$OUT_DIR/full.mp4" "$OUT_DIR/video.mp4"
elif [ -f "$OUT_DIR/full.mkv" ]; then
  # ffmpeg 로 mp4 변환
  ffmpeg -loglevel error -y -i "$OUT_DIR/full.mkv" -c copy "$OUT_DIR/video.mp4"
fi

if [ -f "$OUT_DIR/full.mp3" ]; then
  mv -n "$OUT_DIR/full.mp3" "$OUT_DIR/audio.mp3"
fi

# 메타데이터 저장
"$YTDLP" --skip-download --print-json --no-warnings "$URL" > "$OUT_DIR/info.json" 2>/dev/null || true

ls -la "$OUT_DIR"
echo "[ok] download → $OUT_DIR"
