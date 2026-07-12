#!/usr/bin/env bash
# make-loop.sh — render a seamless infinite horizontal-scroll loop mp4.
#
# Usage:
#   make-loop.sh -i <imgdir_or_files> -o <out.mp4> [options]
#
# Options:
#   -i  PATH        image dir, OR comma-separated image files (required)
#   -o  PATH        output mp4 path (required)
#   --tile-width N  per-image tile width in px (default 1080)
#   --px-per-sec N  scroll speed px/sec (default 200)
#   --width N       video width  (default 1920)
#   --height N      video height (default 1080)
#   --fps N         frames/sec   (default 30)
#   --direction X   rtl (camera pans right->left, default) | ltr
#
# Prints the absolute output mp4 path to stdout on success.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PUBLIC_IMG="$ROOT/public/loop-images"

INPUT=""
OUT=""
TILE_WIDTH=1080
PX_PER_SEC=200
WIDTH=1920
HEIGHT=1080
FPS=30
DIRECTION="rtl"
BACKGROUND="#000000"

while [[ $# -gt 0 ]]; do
  case "$1" in
    -i) INPUT="$2"; shift 2 ;;
    -o) OUT="$2"; shift 2 ;;
    --tile-width) TILE_WIDTH="$2"; shift 2 ;;
    --px-per-sec) PX_PER_SEC="$2"; shift 2 ;;
    --width) WIDTH="$2"; shift 2 ;;
    --height) HEIGHT="$2"; shift 2 ;;
    --fps) FPS="$2"; shift 2 ;;
    --direction) DIRECTION="$2"; shift 2 ;;
    --background) BACKGROUND="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

[[ -z "$INPUT" ]] && { echo "ERROR: -i required" >&2; exit 1; }
[[ -z "$OUT" ]] && { echo "ERROR: -o required" >&2; exit 1; }

# Collect image files into an array.
declare -a SRC_FILES=()
if [[ -d "$INPUT" ]]; then
  while IFS= read -r f; do SRC_FILES+=("$f"); done < <(
    find "$INPUT" -maxdepth 1 -type f \
      \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.webp' \) \
      | sort
  )
else
  IFS=',' read -ra parts <<< "$INPUT"
  for p in "${parts[@]}"; do
    p="$(echo "$p" | xargs)"   # trim
    [[ -f "$p" ]] && SRC_FILES+=("$p")
  done
fi

[[ ${#SRC_FILES[@]} -eq 0 ]] && { echo "ERROR: no images found in $INPUT" >&2; exit 1; }

# Reset and repopulate public/loop-images.
rm -rf "$PUBLIC_IMG"
mkdir -p "$PUBLIC_IMG"

# Build the JSON images array (relative paths under public/).
IMAGES_JSON="["
idx=0
for f in "${SRC_FILES[@]}"; do
  ext="${f##*.}"
  dest="img_$(printf '%03d' "$idx").${ext}"
  cp "$f" "$PUBLIC_IMG/$dest"
  [[ $idx -gt 0 ]] && IMAGES_JSON+=","
  IMAGES_JSON+="\"loop-images/$dest\""
  idx=$((idx+1))
done
IMAGES_JSON+="]"

PROPS="$ROOT/public/loop-props.json"
cat > "$PROPS" <<EOF
{
  "images": $IMAGES_JSON,
  "tileWidth": $TILE_WIDTH,
  "pxPerSec": $PX_PER_SEC,
  "width": $WIDTH,
  "height": $HEIGHT,
  "fps": $FPS,
  "direction": "$DIRECTION",
  "background": "$BACKGROUND"
}
EOF

# Resolve output to an absolute path.
mkdir -p "$(dirname "$OUT")"
OUT_ABS="$(cd "$(dirname "$OUT")" && pwd)/$(basename "$OUT")"

echo "[make-loop] $idx image(s), ${WIDTH}x${HEIGHT} @ ${FPS}fps, dir=$DIRECTION" >&2
NODE_OPTIONS='--max-old-space-size=4096' node "$ROOT/scripts/render.mjs" "$OUT_ABS" >&2

echo "$OUT_ABS"
