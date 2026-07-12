#!/usr/bin/env bash
# photo-restyle wrapper around image-gen/gen_image.py
# Auto-attaches every reference image in a directory (or a list of files)
# as --input-image and forwards the rest to the Codex image-to-image script.
#
# Usage:
#   restyle.sh -p "PROMPT" -r REF_DIR_OR_FILE [-r MORE_REFS ...] -o OUT.png \
#              [--size 1024x1536] [--quality high]
#
#   -p  prompt (required)
#   -r  reference: a directory (all images inside used) OR a single image file.
#       Repeatable. At least one required.
#   -o  output path (default: /tmp/restyle_<ts>.png)
#   --size / --quality / --background / --size etc. forwarded verbatim to gen_image.py
#
# Exit: 0 ok, 1 bad args, 2 no reference images found, >0 gen_image.py failure.

set -euo pipefail

GEN="$HOME/2lab.ai/skills/image-gen/scripts/gen_image.py"
PROMPT=""
OUT=""
REFS=()
PASSTHRU=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    -p|--prompt) PROMPT="$2"; shift 2 ;;
    -o|--output) OUT="$2"; shift 2 ;;
    -r|--ref) REFS+=("$2"); shift 2 ;;
    --size|--quality|--background|--action|--model|--events)
      PASSTHRU+=("$1" "$2"); shift 2 ;;
    -h|--help)
      sed -n '2,20p' "$0"; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$PROMPT" ]]; then echo "ERROR: -p PROMPT required" >&2; exit 1; fi
if [[ ${#REFS[@]} -eq 0 ]]; then echo "ERROR: at least one -r REF required" >&2; exit 1; fi
if [[ ! -f "$GEN" ]]; then echo "ERROR: gen_image.py not found at $GEN" >&2; exit 1; fi
if [[ -z "$OUT" ]]; then OUT="/tmp/restyle_$(date +%s).png"; fi

# Collect reference image files from dirs/files.
IMG_ARGS=()
shopt -s nullglob nocaseglob
for ref in "${REFS[@]}"; do
  if [[ -d "$ref" ]]; then
    for f in "$ref"/*.{png,jpg,jpeg,webp,gif}; do
      IMG_ARGS+=(--input-image "$f")
    done
  elif [[ -f "$ref" ]]; then
    IMG_ARGS+=(--input-image "$ref")
  else
    echo "WARN: reference not found, skipping: $ref" >&2
  fi
done
shopt -u nullglob nocaseglob

if [[ ${#IMG_ARGS[@]} -eq 0 ]]; then
  echo "ERROR: no reference images found in: ${REFS[*]}" >&2
  exit 2
fi

echo "[photo-restyle] refs=$(( ${#IMG_ARGS[@]} / 2 )) out=$OUT" >&2

python3 "$GEN" "$PROMPT" "${IMG_ARGS[@]}" -o "$OUT" "${PASSTHRU[@]}"
echo "$OUT"
