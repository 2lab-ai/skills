#!/usr/bin/env python3
"""
Clumsy MS Paint shorts generator.

Pipeline:
  1. base sketch  : codex image-gen text-to-image (pencil doodle of subject)
  2. clumsy redraw: codex image-gen image-to-image (the base) with "draw it pathetically" prompt
  3. voiceover    : edge-tts narration
  4. assemble     : 9:16 vertical short - title card -> base -> wipe -> clumsy -> side-by-side -> punchline

Usage:
  python clumsy.py --subject "a cat" --topic "a cat"
  python clumsy.py --subject "the Eiffel tower" --topic "the Eiffel Tower" --output /tmp/clumsy_eiffel.mp4
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Error: Pillow required. pip install Pillow", file=sys.stderr)
    sys.exit(1)

# Layout
W, H = 1080, 1920
FPS = 30

GEN_IMAGE = Path.home() / "2lab.ai/skills/image-gen/scripts/gen_image.py"

REDRAW_PROMPT = (
    "Redraw the attached image in the most clumsy, scribbly, and utterly pathetic "
    "way possible. Use a white background, and make it look like it was drawn in "
    "MS Paint with a mouse. It should be vaguely similar but also not really, kind "
    "of matching but also off in a confusing, awkward way, with that low-quality "
    "pixel-by-pixel feel that really emphasizes how ridiculously bad it is. "
    "Actually, you know what, whatever, just draw it however you want."
)

BASE_PROMPT_TPL = (
    "A simple recognizable pencil sketch of {subject} on plain white paper, "
    "childlike doodle style, soft graphite lines, plain white background, "
    "casual notebook sketch, nothing fancy."
)


# ---------- font helpers ----------
FONT_BOLD_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
]


def _font(size: int) -> ImageFont.FreeTypeFont:
    for p in FONT_BOLD_CANDIDATES:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, **kw)


# ---------- image generation ----------
def gen_base(subject: str, out: Path):
    prompt = BASE_PROMPT_TPL.format(subject=subject)
    print(f"[1/4] base sketch -> {out.name}", file=sys.stderr)
    run([
        sys.executable, str(GEN_IMAGE), prompt,
        "--size", "1024x1024", "--quality", "medium",
        "-o", str(out),
    ])


def gen_clumsy(base: Path, out: Path):
    print(f"[2/4] clumsy redraw -> {out.name}", file=sys.stderr)
    run([
        sys.executable, str(GEN_IMAGE), REDRAW_PROMPT,
        "--input-image", str(base),
        "--size", "1024x1024", "--quality", "high",
        "-o", str(out),
    ])


# ---------- card composition ----------
def fit_square_on_white(square_img: Path, out: Path, label: str | None = None,
                        sublabel: str | None = None):
    """Place a 1:1 image centered on a 1080x1920 white card, with optional handwritten labels."""
    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    img = Image.open(square_img).convert("RGB")
    img = img.resize((900, 900), Image.LANCZOS)
    canvas.paste(img, ((W - 900) // 2, 460))
    draw = ImageDraw.Draw(canvas)
    if label:
        f = _font(78)
        bbox = draw.textbbox((0, 0), label, font=f)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, 240), label, font=f, fill=(0, 0, 0))
    if sublabel:
        f = _font(48)
        bbox = draw.textbbox((0, 0), sublabel, font=f)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, 1420), sublabel, font=f, fill=(180, 0, 0))
    canvas.save(out)


def title_card(text: str, out: Path, accent: str = "#FF0000"):
    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    f = _font(140)
    lines = text.split("\n")
    total_h = sum(_font(140).getbbox(l)[3] for l in lines) + 20 * (len(lines) - 1)
    y = (H - total_h) // 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=f)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, y), line, font=f, fill=(0, 0, 0))
        y += bbox[3] + 20
    # crude red squiggle "underline"
    # convert hex -> rgb tuple
    accent_rgb = tuple(int(accent.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    for i in range(40):
        x0 = 200 + i * 18
        y0 = y + 30 + (i % 2) * 14
        draw.line([(x0, y0), (x0 + 18, y0 + 8)], fill=accent_rgb, width=6)
    canvas.save(out)


def side_by_side(base: Path, clumsy: Path, out: Path):
    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    a = Image.open(base).convert("RGB").resize((900, 900), Image.LANCZOS)
    b = Image.open(clumsy).convert("RGB").resize((900, 900), Image.LANCZOS)
    canvas.paste(a, ((W - 900) // 2, 250))
    canvas.paste(b, ((W - 900) // 2, 1180))
    draw = ImageDraw.Draw(canvas)
    f_label = _font(64)
    draw.text((90, 170), "expectation", font=f_label, fill=(0, 130, 0))
    draw.text((90, 1100), "reality", font=f_label, fill=(200, 0, 0))
    f_vs = _font(120)
    bbox = draw.textbbox((0, 0), "VS", font=f_vs)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, 1075), "VS", font=f_vs, fill=(0, 0, 0))
    canvas.save(out)


# ---------- video helpers ----------
def img_to_clip(img: Path, out: Path, duration: float, effect: str = "still"):
    """Make an mp4 clip from a still image with optional zoom."""
    if effect == "zoom":
        vf = (
            f"scale={int(W*1.08)}:{int(H*1.08)},"
            f"zoompan=z='1.08-0.08*on/{int(duration*FPS)}':"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={int(duration*FPS)}:s={W}x{H}:fps={FPS}"
        )
    else:
        vf = f"scale={W}:{H},fps={FPS}"
    run([
        "ffmpeg", "-y", "-loop", "1", "-i", str(img),
        "-vf", vf, "-t", str(duration), "-r", str(FPS),
        "-pix_fmt", "yuv420p", "-loglevel", "error",
        str(out),
    ])


def concat_clips(clips: list[Path], out: Path):
    listfile = out.parent / "concat.txt"
    listfile.write_text("\n".join(f"file '{c.resolve()}'" for c in clips))
    run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
        "-c", "copy", "-loglevel", "error",
        str(out),
    ])


def synth_voice(text: str, out: Path, voice: str = "en-US-GuyNeural"):
    print(f"[3/4] tts -> {out.name}", file=sys.stderr)
    edge_tts_bin = Path.home() / "2lab.ai/skills/shorts/.venv/bin/edge-tts"
    binary = str(edge_tts_bin) if edge_tts_bin.exists() else "edge-tts"
    run([binary, "--voice", voice, "--text", text, "--write-media", str(out)])


def mux_audio(video: Path, audio: Path, out: Path):
    run([
        "ffmpeg", "-y", "-i", str(video), "-i", str(audio),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-loglevel", "error",
        str(out),
    ])


# ---------- main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", required=True, help="thing to draw, e.g. 'a cat'")
    ap.add_argument("--topic", default=None, help="display topic in title card")
    ap.add_argument("--output", default="/tmp/clumsy-test/clumsy_short.mp4")
    ap.add_argument("--workdir", default=None)
    ap.add_argument("--voice", default="en-US-GuyNeural")
    ap.add_argument("--skip-base", action="store_true",
                    help="reuse existing base.png in workdir")
    ap.add_argument("--skip-clumsy", action="store_true",
                    help="reuse existing clumsy.png in workdir")
    args = ap.parse_args()

    topic = args.topic or args.subject
    workdir = Path(args.workdir) if args.workdir else Path(tempfile.mkdtemp(prefix="clumsy_"))
    workdir.mkdir(parents=True, exist_ok=True)
    print(f"workdir: {workdir}", file=sys.stderr)

    base = workdir / "base.png"
    clumsy = workdir / "clumsy.png"

    if not args.skip_base or not base.exists():
        gen_base(args.subject, base)
    if not args.skip_clumsy or not clumsy.exists():
        gen_clumsy(base, clumsy)

    # composed cards
    title_png = workdir / "title.png"
    base_card = workdir / "card_base.png"
    clumsy_card = workdir / "card_clumsy.png"
    sxs_card = workdir / "card_sxs.png"
    punch_card = workdir / "card_punch.png"

    title_card(f"i tried\nto draw\n{topic}", title_png)
    fit_square_on_white(base, base_card,
                        label="step 1: try to draw it",
                        sublabel="pencil sketch")
    fit_square_on_white(clumsy, clumsy_card,
                        label="step 2: redraw it... badly",
                        sublabel="(MS paint, mouse only)")
    side_by_side(base, clumsy, sxs_card)
    title_card("roast me\nin the\ncomments", punch_card)

    # narration
    voice_text = (
        f"I tried to draw {topic}. "
        "First, a normal pencil sketch. Fine. "
        "Then I redrew it in MS Paint, with a mouse. "
        "It went poorly. "
        "Roast me in the comments."
    )
    voice_mp3 = workdir / "voice.mp3"
    synth_voice(voice_text, voice_mp3, args.voice)

    # clips (durations chosen to sum ~16s, which fits a typical 100-word voiceover)
    clips_dir = workdir / "clips"
    clips_dir.mkdir(exist_ok=True)
    plan = [
        (title_png, 2.0, "still"),
        (base_card, 3.0, "zoom"),
        (clumsy_card, 4.0, "zoom"),
        (sxs_card, 4.0, "still"),
        (punch_card, 2.0, "still"),
    ]
    clip_paths = []
    for i, (img, dur, eff) in enumerate(plan):
        out = clips_dir / f"clip_{i}.mp4"
        img_to_clip(img, out, dur, eff)
        clip_paths.append(out)

    silent = workdir / "silent.mp4"
    concat_clips(clip_paths, silent)

    print(f"[4/4] mux audio -> {args.output}", file=sys.stderr)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    mux_audio(silent, voice_mp3, Path(args.output))
    print(f"\nDone: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
