#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

TOTAL_PARTS=4
FFMPEG="${HOME}/.local/bin/ffmpeg"
OUT_DIR="$PROJECT_DIR/out"

export NODE_OPTIONS="--max-old-space-size=4096"

echo "=== STV Video Render Pipeline ==="
echo "Parts: $TOTAL_PARTS"
echo "Heap: 4096MB"
echo "Output: $OUT_DIR"
echo ""

# Render each part sequentially
for i in $(seq 1 $TOTAL_PARTS); do
  echo "========================================="
  echo " RENDERING PART $i / $TOTAL_PARTS"
  echo "========================================="
  node scripts/render-parts.mjs "$i" "$TOTAL_PARTS"

  SIZE=$(du -h "$OUT_DIR/part-${i}.mp4" 2>/dev/null | cut -f1)
  echo "  Part $i complete: $SIZE"
  echo ""
done

echo "========================================="
echo " CONCATENATING ALL PARTS"
echo "========================================="

# Create concat list
CONCAT_LIST="$OUT_DIR/concat-list.txt"
> "$CONCAT_LIST"
for i in $(seq 1 $TOTAL_PARTS); do
  echo "file 'part-${i}.mp4'" >> "$CONCAT_LIST"
done

# Concat with ffmpeg
"$FFMPEG" -y -f concat -safe 0 -i "$CONCAT_LIST" -c copy "$OUT_DIR/stv-traced-development.mp4"

FINAL_SIZE=$(du -h "$OUT_DIR/stv-traced-development.mp4" | cut -f1)
echo ""
echo "========================================="
echo " DONE!"
echo " Output: $OUT_DIR/stv-traced-development.mp4"
echo " Size: $FINAL_SIZE"
echo "========================================="
