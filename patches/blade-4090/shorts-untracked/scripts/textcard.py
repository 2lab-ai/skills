#!/usr/bin/env python3
"""
Text Card Video Generator — simple text-on-dark square videos.

Style: Substack article reader / quote card
- Dark background (#0A0A0E)
- White text with accent word highlighting
- Source/title at top
- 1:1 square format (1080x1080)
- Word-by-word karaoke-style highlighting

Usage:
    # From a draft JSON
    python scripts/textcard.py --draft ~/.verticals/drafts/123.json

    # Direct text input
    python scripts/textcard.py --text "Your script here" --source "TECHCRUNCH.COM" --title "Article Title"

    # With Fish TTS
    python scripts/textcard.py --draft draft.json --tts fish --voice cwon

    # With Edge TTS
    python scripts/textcard.py --draft draft.json --tts edge
"""

import argparse
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Error: Pillow required. pip install Pillow")
    sys.exit(1)

# ─────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────
WIDTH = 1080
HEIGHT = 1080
FPS = 30

# Colors
BG_COLOR = (10, 10, 14)          # #0A0A0E
TEXT_COLOR = (255, 255, 255)      # White
ACCENT_COLOR = (200, 80, 80)     # #C85050 coral
SOURCE_COLOR = (102, 102, 102)   # #666666 gray
DIM_COLOR = (140, 140, 140)      # Dimmed text for inactive words

# Font paths (priority order)
FONT_CANDIDATES_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-Bold.ttf",
]
FONT_CANDIDATES_REGULAR = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-Regular.ttf",
]

# Typography
MAIN_FONT_SIZE = 58
SOURCE_FONT_SIZE = 22
TITLE_FONT_SIZE = 20
LINE_SPACING = 1.5   # multiplier
MAX_CHARS_PER_LINE = 28
WORDS_PER_GROUP = 4

# Layout
SOURCE_MARGIN_TOP = 50
SOURCE_MARGIN_LEFT = 60
TEXT_MARGIN_X = 80

# Fish TTS config
FISH_SPEECH_DIR = Path.home() / "fish-speech"
FISH_TTS_VOICES = Path.home() / "2lab.ai" / "skills" / "fish-tts" / "voices"
MERGE_SCRIPT = Path.home() / "2lab.ai" / "soul" / "np1" / "data" / "docent-books" / "scripts" / "merge_smooth.py"

# Output
MEDIA_DIR = Path.home() / ".verticals" / "media"


def _find_font(candidates):
    """Find first available font from candidates list."""
    for path in candidates:
        if Path(path).exists():
            return path
    return None


def _load_fonts():
    """Load font objects."""
    bold_path = _find_font(FONT_CANDIDATES_BOLD)
    regular_path = _find_font(FONT_CANDIDATES_REGULAR)

    if not bold_path:
        print("Warning: No bold font found, using default")
        return {
            "main": ImageFont.load_default(),
            "source": ImageFont.load_default(),
            "title": ImageFont.load_default(),
        }

    return {
        "main": ImageFont.truetype(bold_path, MAIN_FONT_SIZE),
        "accent": ImageFont.truetype(bold_path, int(MAIN_FONT_SIZE * 1.1)),
        "source": ImageFont.truetype(regular_path or bold_path, SOURCE_FONT_SIZE),
        "title": ImageFont.truetype(regular_path or bold_path, TITLE_FONT_SIZE),
    }


# ─────────────────────────────────────────────────────
# Frame Rendering
# ─────────────────────────────────────────────────────

def render_text_frame(
    words: list[str],
    active_idx: int = -1,
    source: str = "",
    title: str = "",
    accent_color: tuple = ACCENT_COLOR,
    fonts: dict = None,
) -> Image.Image:
    """Render a single text card frame.

    Args:
        words: List of words to display
        active_idx: Index of the highlighted word (-1 = none)
        source: Source URL/name shown at top
        title: Article title shown below source
        accent_color: RGB tuple for highlighted word
        fonts: Dict of loaded fonts
    """
    if fonts is None:
        fonts = _load_fonts()

    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # ── Source info at top ──
    y_cursor = SOURCE_MARGIN_TOP
    if source:
        draw.text(
            (SOURCE_MARGIN_LEFT, y_cursor),
            source.upper(),
            fill=SOURCE_COLOR,
            font=fonts["source"],
        )
        y_cursor += SOURCE_FONT_SIZE + 8
    if title:
        # Truncate long titles
        if len(title) > 50:
            title = title[:47] + "..."
        draw.text(
            (SOURCE_MARGIN_LEFT, y_cursor),
            title,
            fill=SOURCE_COLOR,
            font=fonts["title"],
        )

    # ── Main text — centered ──
    # Word-wrap into lines
    lines = []
    current_line = []
    current_len = 0

    for i, word in enumerate(words):
        word_len = len(word) + 1
        if current_len + word_len > MAX_CHARS_PER_LINE and current_line:
            lines.append(current_line)
            current_line = [(i, word)]
            current_len = word_len
        else:
            current_line.append((i, word))
            current_len += word_len

    if current_line:
        lines.append(current_line)

    # Calculate vertical centering
    line_height = int(MAIN_FONT_SIZE * LINE_SPACING)
    total_text_height = len(lines) * line_height
    start_y = (HEIGHT - total_text_height) // 2

    # Draw each line
    for line_idx, line_words in enumerate(lines):
        y = start_y + line_idx * line_height

        # Calculate line width for horizontal centering
        line_text = " ".join(w for _, w in line_words)
        bbox = draw.textbbox((0, 0), line_text, font=fonts["main"])
        line_width = bbox[2] - bbox[0]
        x = (WIDTH - line_width) // 2

        # Draw word by word
        for word_idx, word in line_words:
            if word_idx == active_idx:
                # Active word — accent color, slightly larger
                color = accent_color
                font = fonts.get("accent", fonts["main"])
                # Adjust y for larger font
                y_adj = y - int(MAIN_FONT_SIZE * 0.05)
                draw.text((x, y_adj), word, fill=color, font=font)
                word_bbox = draw.textbbox((x, y_adj), word, font=font)
            else:
                color = TEXT_COLOR
                draw.text((x, y), word, fill=color, font=fonts["main"])
                word_bbox = draw.textbbox((x, y), word, font=fonts["main"])

            # Move x to next word position (use main font for consistent spacing)
            space_bbox = draw.textbbox((0, 0), " ", font=fonts["main"])
            space_width = space_bbox[2] - space_bbox[0]
            main_bbox = draw.textbbox((x, y), word, font=fonts["main"])
            x = main_bbox[2] + space_width

    return img


def render_group_frames(
    words: list[str],
    word_timestamps: list[dict],
    source: str = "",
    title: str = "",
    accent_color: tuple = ACCENT_COLOR,
    group_size: int = WORDS_PER_GROUP,
    out_dir: Path = None,
) -> list[dict]:
    """Render frames for each word group with per-word highlighting.

    Returns list of {"frame_path": Path, "start": float, "end": float, "active_word_idx": int}
    """
    fonts = _load_fonts()
    frames_info = []

    # Group words
    groups = []
    for i in range(0, len(word_timestamps), group_size):
        groups.append(word_timestamps[i:i + group_size])

    for g_idx, group in enumerate(groups):
        group_words = [w["word"] for w in group]
        group_word_indices = list(range(len(group_words)))

        for w_idx, word_data in enumerate(group):
            frame = render_text_frame(
                words=group_words,
                active_idx=w_idx,
                source=source,
                title=title,
                accent_color=accent_color,
                fonts=fonts,
            )

            frame_path = out_dir / f"frame_{g_idx:04d}_{w_idx:02d}.png"
            frame.save(frame_path)

            frames_info.append({
                "frame_path": frame_path,
                "start": word_data["start"],
                "end": word_data["end"],
                "group_idx": g_idx,
                "word_idx": w_idx,
            })

    return frames_info


# ─────────────────────────────────────────────────────
# TTS
# ─────────────────────────────────────────────────────

def generate_tts_fish(text: str, output_path: Path, voice: str = "cwon") -> Path:
    """Generate voiceover using Fish TTS."""
    voice_dir = FISH_TTS_VOICES / voice
    ref_audio = voice_dir / "reference.mp3"
    ref_text_file = voice_dir / "reference.txt"

    if not ref_audio.exists():
        raise FileNotFoundError(f"Fish TTS voice not found: {voice_dir}")

    ref_text = ref_text_file.read_text().strip() if ref_text_file.exists() else ""

    # Split into chunks (~300 chars max)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = ""
    for s in sentences:
        if len(current) + len(s) > 300 and current:
            chunks.append(current.strip())
            current = s
        else:
            current = (current + " " + s).strip()
    if current:
        chunks.append(current.strip())

    if not chunks:
        chunks = [text]

    print(f"  Fish TTS: {len(chunks)} chunks, voice={voice}")

    chunk_files = []
    for i, chunk in enumerate(chunks):
        chunk_out = output_path.parent / f"tts_chunk_{i}.wav"
        cmd = [
            str(FISH_SPEECH_DIR / ".venv" / "bin" / "python"),
            str(Path.home() / "2lab.ai" / "skills" / "fish-audio" / "scripts" / "gpu-inference.py"),
            "--text", f"<|speaker:0|>{chunk}",
            "--prompt-text", ref_text,
            "--prompt-audio", str(ref_audio),
            "--output", str(chunk_out),
            "--checkpoint-path", "checkpoints/s2-pro",
            "--device", "cuda",
            "--temperature", "0.7",
            "--top-p", "0.9",
            "--seed", "42",
            "--max-new-tokens", "2048",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(FISH_SPEECH_DIR), timeout=120)
        if result.returncode != 0:
            print(f"  Warning: chunk {i} failed: {result.stderr[:200]}")
            continue

        if chunk_out.exists():
            chunk_files.append(str(chunk_out))
            print(f"  ✓ Chunk {i+1}/{len(chunks)}")

    if not chunk_files:
        raise RuntimeError("All Fish TTS chunks failed")

    # Merge chunks
    if len(chunk_files) == 1:
        # Convert single wav to output
        subprocess.run([
            "ffmpeg", "-i", chunk_files[0], "-y", str(output_path),
        ], capture_output=True, timeout=30)
    else:
        merge_cmd = [
            "python3", str(MERGE_SCRIPT),
            *chunk_files,
            "-o", str(output_path),
            "--silence-min", "0.4",
            "--silence-max", "0.7",
            "--fade-ms", "20",
            "--seed", "42",
        ]
        subprocess.run(merge_cmd, capture_output=True, timeout=60)

    if not output_path.exists():
        raise RuntimeError(f"TTS output not created: {output_path}")

    print(f"  ✓ Voiceover: {output_path}")
    return output_path


def generate_tts_edge(text: str, output_path: Path, voice: str = "en-US-GuyNeural") -> Path:
    """Generate voiceover using Edge TTS."""
    import asyncio

    async def _run():
        import edge_tts
        comm = edge_tts.Communicate(text, voice)
        await comm.save(str(output_path))

    asyncio.run(_run())
    print(f"  ✓ Voiceover (Edge TTS): {output_path}")
    return output_path


# ─────────────────────────────────────────────────────
# Whisper
# ─────────────────────────────────────────────────────

def get_word_timestamps(audio_path: Path, lang: str = "en") -> list[dict]:
    """Get word-level timestamps via Whisper."""
    print("  Running Whisper for word timestamps...")

    # Use CPU to avoid GPU memory conflicts with Fish TTS
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = ""

    script = f"""
import whisper
import json

model = whisper.load_model("base", device="cpu")
result = model.transcribe("{audio_path}", language="{lang[:2]}", word_timestamps=True)

words = []
for seg in result.get("segments", []):
    for w in seg.get("words", []):
        words.append({{"word": w["word"].strip(), "start": w["start"], "end": w["end"]}})

print(json.dumps(words))
"""

    # Try shorts venv first, then fish-speech venv
    venvs = [
        Path.home() / "2lab.ai" / "skills" / "shorts" / ".venv" / "bin" / "python",
        FISH_SPEECH_DIR / ".venv" / "bin" / "python",
    ]

    for venv_python in venvs:
        if not venv_python.exists():
            continue
        result = subprocess.run(
            [str(venv_python), "-c", script],
            capture_output=True, text=True, env=env, timeout=120,
        )
        if result.returncode == 0 and result.stdout.strip():
            words = json.loads(result.stdout.strip())
            print(f"  ✓ {len(words)} word timestamps")
            return words

    print("  Warning: Whisper failed, falling back to estimated timestamps")
    return _estimate_timestamps(audio_path)


def _estimate_timestamps(audio_path: Path) -> list[dict]:
    """Estimate word timestamps from audio duration (fallback)."""
    # Get audio duration
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(audio_path)],
        capture_output=True, text=True,
    )
    duration = float(result.stdout.strip())

    # We don't have the text... return empty
    return []


# ─────────────────────────────────────────────────────
# Video Assembly
# ─────────────────────────────────────────────────────

def assemble_textcard_video(
    frames_info: list[dict],
    voiceover: Path,
    output: Path,
    music_path: Path = None,
) -> Path:
    """Assemble text card video from rendered frames + voiceover.

    Creates a video where each frame is shown for its word duration,
    synced with the voiceover audio.
    """
    print("  Assembling video...")

    work_dir = output.parent

    # Get total duration from voiceover
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(voiceover)],
        capture_output=True, text=True,
    )
    total_duration = float(result.stdout.strip())

    # Create concat file with durations
    concat_file = work_dir / "concat_frames.txt"
    lines = []

    for i, fi in enumerate(frames_info):
        # Calculate duration for this frame
        if i + 1 < len(frames_info):
            dur = frames_info[i + 1]["start"] - fi["start"]
        else:
            dur = fi["end"] - fi["start"]

        dur = max(dur, 0.05)  # minimum 50ms
        lines.append(f"file '{fi['frame_path']}'")
        lines.append(f"duration {dur:.4f}")

    # Add last frame again (ffmpeg concat demuxer requirement)
    if frames_info:
        lines.append(f"file '{frames_info[-1]['frame_path']}'")

    concat_file.write_text("\n".join(lines))

    # Step 1: Create video from frames
    frames_video = work_dir / "frames_video.mp4"
    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-vf", f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=0A0A0E",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-r", str(FPS),
        str(frames_video), "-y", "-loglevel", "warning",
    ], timeout=120)

    # Step 2: Merge video + audio
    if music_path and Path(music_path).exists():
        # With background music (ducked)
        subprocess.run([
            "ffmpeg",
            "-i", str(frames_video),
            "-i", str(voiceover),
            "-stream_loop", "-1", "-i", str(music_path),
            "-filter_complex",
            f"[2:a]aloop=loop=-1:size=2e+09,atrim=0:{total_duration},volume=0.08[music];"
            f"[1:a][music]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "aac",
            "-shortest",
            str(output), "-y", "-loglevel", "warning",
        ], timeout=120)
    else:
        # Voice only
        subprocess.run([
            "ffmpeg",
            "-i", str(frames_video),
            "-i", str(voiceover),
            "-c:v", "copy", "-c:a", "aac",
            "-shortest",
            str(output), "-y", "-loglevel", "warning",
        ], timeout=120)

    if output.exists():
        size_mb = output.stat().st_size / (1024 * 1024)
        print(f"  ✓ Video assembled: {output} ({size_mb:.1f} MB)")
    else:
        raise RuntimeError(f"Video assembly failed: {output}")

    return output


# ─────────────────────────────────────────────────────
# Main Pipeline
# ─────────────────────────────────────────────────────

def run_textcard_pipeline(
    text: str,
    source: str = "",
    title: str = "",
    tts_provider: str = "edge",
    tts_voice: str = None,
    lang: str = "en",
    accent_color: tuple = ACCENT_COLOR,
    output_path: Path = None,
    music_path: Path = None,
    group_size: int = WORDS_PER_GROUP,
):
    """Full text card video pipeline.

    1. Generate voiceover (Fish TTS or Edge TTS)
    2. Get word timestamps (Whisper)
    3. Render frames (Pillow)
    4. Assemble video (ffmpeg)
    """
    # Setup work directory
    work_dir = Path(tempfile.mkdtemp(prefix="textcard_"))
    print(f"\n  ═══ Text Card Pipeline ═══")
    print(f"  Work dir: {work_dir}")
    print(f"  TTS: {tts_provider} | Lang: {lang}")
    print(f"  Source: {source or '(none)'}")
    print(f"  Text: {text[:80]}...")

    # 1. Generate voiceover
    print("\n  [1/4] Generating voiceover...")
    vo_path = work_dir / "voiceover.wav"

    if tts_provider == "fish":
        voice = tts_voice or "cwon"
        vo_path = generate_tts_fish(text, vo_path, voice=voice)
    else:
        voice = tts_voice or "en-US-GuyNeural"
        vo_mp3 = work_dir / "voiceover.mp3"
        generate_tts_edge(text, vo_mp3, voice=voice)
        # Convert to WAV for Whisper
        subprocess.run([
            "ffmpeg", "-i", str(vo_mp3), "-ar", "16000", "-ac", "1",
            str(vo_path), "-y", "-loglevel", "quiet",
        ], timeout=30)

    # 2. Word timestamps
    print("\n  [2/4] Getting word timestamps...")
    word_timestamps = get_word_timestamps(vo_path, lang=lang)

    if not word_timestamps:
        # Fallback: estimate from text + duration
        print("  Warning: No word timestamps, using even distribution")
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(vo_path)],
            capture_output=True, text=True,
        )
        duration = float(result.stdout.strip())
        words = text.split()
        per_word = duration / len(words)
        word_timestamps = [
            {"word": w, "start": i * per_word, "end": (i + 1) * per_word}
            for i, w in enumerate(words)
        ]

    # 3. Render frames
    print(f"\n  [3/4] Rendering {len(word_timestamps)} word frames...")
    frames_dir = work_dir / "frames"
    frames_dir.mkdir()

    frames_info = render_group_frames(
        words=[w["word"] for w in word_timestamps],
        word_timestamps=word_timestamps,
        source=source,
        title=title,
        accent_color=accent_color,
        group_size=group_size,
        out_dir=frames_dir,
    )
    print(f"  ✓ {len(frames_info)} frames rendered")

    # 4. Assemble video
    print("\n  [4/4] Assembling video...")
    if output_path is None:
        MEDIA_DIR.mkdir(parents=True, exist_ok=True)
        output_path = MEDIA_DIR / "textcard_latest.mp4"

    # Use wav or find the mp3
    vo_for_assembly = vo_path
    vo_mp3 = work_dir / "voiceover.mp3"
    if vo_mp3.exists():
        vo_for_assembly = vo_mp3
    elif vo_path.suffix == ".wav":
        # Convert wav to mp3 for final assembly
        vo_mp3_out = work_dir / "voiceover_final.mp3"
        subprocess.run([
            "ffmpeg", "-i", str(vo_path), "-codec:a", "libmp3lame", "-b:a", "192k",
            str(vo_mp3_out), "-y", "-loglevel", "quiet",
        ], timeout=30)
        if vo_mp3_out.exists():
            vo_for_assembly = vo_mp3_out

    result = assemble_textcard_video(
        frames_info=frames_info,
        voiceover=vo_for_assembly,
        output=output_path,
        music_path=music_path,
    )

    print(f"\n  ═══ Done! ═══")
    print(f"  Output: {result}")
    return result


# ─────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Text Card Video Generator — square text-on-dark videos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Input source
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--draft", help="Path to draft JSON file")
    input_group.add_argument("--text", help="Direct script text")

    # Metadata
    parser.add_argument("--source", default="", help="Source name (e.g., TECHCRUNCH.COM)")
    parser.add_argument("--title", default="", help="Article/video title")

    # TTS
    parser.add_argument("--tts", default="edge", choices=["edge", "fish"],
                        help="TTS provider (default: edge)")
    parser.add_argument("--voice", default=None,
                        help="Voice name (edge: en-US-GuyNeural, fish: cwon)")
    parser.add_argument("--lang", default="en", help="Language code")

    # Style
    parser.add_argument("--accent-color", default="#C85050",
                        help="Accent color hex (default: #C85050)")
    parser.add_argument("--group-size", type=int, default=WORDS_PER_GROUP,
                        help=f"Words per group (default: {WORDS_PER_GROUP})")

    # Output
    parser.add_argument("--output", "-o", default=None, help="Output video path")
    parser.add_argument("--music", default=None, help="Background music path")

    args = parser.parse_args()

    # Parse input
    if args.draft:
        draft = json.loads(Path(args.draft).read_text())
        text = draft.get("script", "")
        source = args.source or draft.get("source", "")
        title = args.title or draft.get("youtube_title", draft.get("title", ""))
    else:
        text = args.text
        source = args.source
        title = args.title

    if not text:
        print("Error: No script text found")
        sys.exit(1)

    # Parse accent color
    hc = args.accent_color.lstrip("#")
    accent_color = tuple(int(hc[i:i+2], 16) for i in (0, 2, 4))

    # Output path
    output_path = Path(args.output) if args.output else None

    run_textcard_pipeline(
        text=text,
        source=source,
        title=title,
        tts_provider=args.tts,
        tts_voice=args.voice,
        lang=args.lang,
        accent_color=accent_color,
        output_path=output_path,
        music_path=Path(args.music) if args.music else None,
        group_size=args.group_size,
    )


if __name__ == "__main__":
    main()
