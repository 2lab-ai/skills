---
name: loop-video-gen
description: >
  Create a seamless infinite horizontal-scroll loop video (mp4) from a few
  images, stitched side-by-side so the last frame matches the first with no
  visible jump. Camera pans at a constant speed. Renders with Remotion.
  Use when the user asks for a "루프 비디오", "loop video", "무한 루프 스크롤",
  "loop-video-gen", "이미지 이어붙여 영상", "seamless scrolling loop", or an
  endlessly-repeating horizontal-pan ad/banner from still images.
---

# loop-video-gen

Stitch images horizontally and render a **seamless infinite-loop** horizontal
scroll mp4. The composition lays the images out twice in a row and translates
by `(t * pxPerSec) mod totalWidth`, with `durationInFrames` set to exactly one
full loop — so the video's end frame is identical to its start frame. Loops
forever with no seam.

Reference: @heenj_visual style "infinite loop scroll" ad — last frame ties back
to the first, camera pans right→left at constant speed.

## What this does (and does NOT do)

- DOES: constant-speed horizontal pan over your images, mathematically perfect
  seamless loop, configurable resolution/speed/direction.
- DOES NOT: reproduce AI image-to-video + VFX floating objects from the original
  reference. That original used per-object motion/parallax. This is the simplified
  "tile + scroll" version. Be honest with the user about this limit.

## Environment (reuse — do NOT npm install)

- Remotion 4.0.261 + react 18 live in `../video-gen/node_modules`, symlinked here
  as `./node_modules`. Same version, safe.
- Renderer: chromium at `/usr/bin/chromium-browser`, ffmpeg at `~/.local/bin/ffmpeg`.
  Same setup as video-gen.

## Workflow

### 1. Collect images
Gather the still images the user wants in the scroll (any order; they tile
left→right). PNG/JPG/WEBP. For a clean loop they should be similar height; the
composition does `objectFit: cover` to the tile box.

### 2. (Optional) Pre-process with image-gen to reduce tile seams
Seams appear where one image's right edge meets the next image's left edge.
Two ways to mitigate, both via the image-gen skill (`~/2lab.ai/skills/image-gen/SKILL.md`):

- **Background extension / outpaint** so adjacent tiles share a continuous
  backdrop (best for seamlessness).
- **Cutout (누끼)** objects on a transparent bg, then composite over a single
  continuous background tile:
  ```bash
  cd ~/2lab.ai/skills/image-gen
  python gen_image.py -i object.png -o object_cutout.png --background transparent
  ```
  (Cutout enables the "floating object" mode described below.)

### 3. Render
```bash
cd ~/2lab.ai/skills/loop-video-gen
bash scripts/make-loop.sh -i /path/to/imgdir -o out/loop.mp4 \
  --tile-width 1080 --px-per-sec 300 --width 1920 --height 1080 \
  --fps 30 --direction rtl
```
`-i` accepts a directory OR a comma-separated list of files. The script copies
images into `public/loop-images/`, writes `public/loop-props.json`, runs the
Remotion render, and prints the absolute mp4 path to stdout.

### 4. Send to 지혁
```
mcp__send-file__send_document  filePath=<abs mp4>  caption="..."
```

## Parameters

| Flag           | Default   | Meaning |
|----------------|-----------|---------|
| `-i`           | (required)| image dir OR comma-separated files |
| `-o`           | (required)| output mp4 path |
| `--tile-width` | 1080      | per-image tile width (px) |
| `--px-per-sec` | 200       | scroll speed (px/sec) |
| `--width`      | 1920      | video width (1080 for vertical) |
| `--height`     | 1080      | video height (1920 for vertical) |
| `--fps`        | 30        | frames/sec |
| `--direction`  | rtl       | `rtl` = camera pans right→left; `ltr` = opposite |
| `--background` | #000000   | fill behind tiles |

Duration is computed automatically: `durationInFrames = round(tiles*tileWidth / pxPerSec * fps)`
= exactly one loop. Do not try to set duration manually — that breaks seamlessness.

Vertical (Shorts/Reels): `--width 1080 --height 1920`.

## Floating-object mode (optional, advanced)

For the reference's drifting cutouts: cut out objects (`--background transparent`
in image-gen), place them as a second layer over a single continuous background
tile, and give each its own `translateX` derived from the same modulo so it also
wraps seamlessly. Not yet wired into the composition — implement only if asked;
the horizontal-scroll loop is the guaranteed-working core.

## Troubleshooting

- **Visible seam at tile joins** → use image-gen background extension so edges
  match, or pick images with matching/abstract edges. Single repeating tile also
  loops perfectly.
- **Image squished/cropped** → tiles use `objectFit: cover` at `tileWidth × height`.
  Set `--tile-width` to the image's natural aspect for that height, or pre-resize.
- **Render fails / chromium** → confirm `/usr/bin/chromium-browser` exists and the
  `node_modules` symlink points at `../video-gen/node_modules`.
- **Loop not seamless** → never hand-edit duration; it must equal one full loop.

## Files

- `src/LoopScroll.tsx` — the composition (the seamless-scroll math).
- `src/Root.tsx` — registers `LoopScroll`, computes durationInFrames.
- `scripts/make-loop.sh` — CLI wrapper (collect → copy → props.json → render).
- `scripts/render.mjs` — programmatic Remotion render (chromium flags).
- `public/loop-props.json` — generated per run.

## Spirit (ponytail)

Minimal working implementation first. The core scroll loop must render real mp4s.
Don't over-engineer the floating-object mode until it's actually requested.
