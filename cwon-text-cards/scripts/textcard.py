#!/usr/bin/env python3
"""
Text Card Video Generator v3 — Substack reader style + Docent Book support.

Reference style:
- Dark background (#0D0D11)
- LEFT-aligned text, positioned in lower-center area
- Current word highlighted in coral/red, read=white, unread=gray
- Source + title at top-left in gray
- 1:1 square format (1080x1080)
- Segment-based pages with sentence-boundary splitting

Features:
- --cover-image: Book cover as opening frame (configurable duration)
- --audio: Use pre-rendered audio (skip TTS, go straight to Whisper)
- --parts-dir: Load multi-part text files (D26a.txt, D26b.txt, ...)
- Tone marker auto-stripping for docent voice-letter format

Usage:
    python scripts/textcard.py --text "Your script" --source "SOURCE.COM" --tts fish --voice cwon
    python scripts/textcard.py --draft ~/.verticals/drafts/123.json --tts fish --lang ko
    python scripts/textcard.py --audio voiceover.mp3 --text "Script" --cover-image cover.jpg
    python scripts/textcard.py --audio book.mp3 --parts-dir parts/ --parts D26a D26b D26c --cover-image cover.jpg
"""

import argparse
import glob
import json
import math
import os
import re
import subprocess
import sys
import tempfile
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
BG_COLOR = (13, 13, 17)           # #0D0D11
TEXT_COLOR = (255, 255, 255)       # White
ACCENT_COLOR = (200, 80, 80)      # #C85050 coral
SOURCE_COLOR = (120, 120, 120)    # #787878 gray

# Font paths — priority: NanumGothic (Korean+English) > DejaVu (English only)
FONT_BOLD = [
    str(Path.home() / ".local/share/fonts/NanumGothic-Regular.ttf"),  # Regular works, Bold files broken
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
FONT_REGULAR = [
    str(Path.home() / ".local/share/fonts/NanumGothic-Regular.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

# Typography
MAIN_FONT_SIZE = 28
SOURCE_FONT_SIZE = 18
TITLE_FONT_SIZE = 15
LINE_SPACING = 1.7

# Layout — left-aligned
TEXT_MARGIN_LEFT = 60
TEXT_MARGIN_RIGHT = 60
SOURCE_MARGIN_TOP = 40
SOURCE_MARGIN_LEFT = 60
# Text area
TEXT_AREA_TOP_RATIO = 0.30
TEXT_AREA_BOTTOM_RATIO = 0.82

# Words per segment (sentence-based pages)
SEGMENT_MAX_WORDS = 20

# Fish TTS config
FISH_SPEECH_DIR = Path.home() / "fish-speech"
FISH_TTS_VOICES = Path.home() / "2lab.ai" / "skills" / "fish-tts" / "voices"
MERGE_SCRIPT = Path.home() / "2lab.ai" / "soul" / "np1" / "data" / "docent-books" / "scripts" / "merge_smooth.py"
MEDIA_DIR = Path.home() / ".verticals" / "media"


def _find_font(candidates):
    for p in candidates:
        if Path(p).exists():
            return p
    return None


def _load_fonts():
    bold = _find_font(FONT_BOLD)
    regular = _find_font(FONT_REGULAR)
    if not bold:
        print("Warning: No bold font found")
        return {"main": ImageFont.load_default(), "source": ImageFont.load_default(), "title": ImageFont.load_default()}
    return {
        "main": ImageFont.truetype(bold, MAIN_FONT_SIZE),
        "source": ImageFont.truetype(regular or bold, SOURCE_FONT_SIZE),
        "title": ImageFont.truetype(regular or bold, TITLE_FONT_SIZE),
    }


# ─────────────────────────────────────────────────────
# Tone marker stripping (for docent voice-letter format)
# ─────────────────────────────────────────────────────

def _strip_tone_markers(text: str) -> str:
    """Remove tone markers like [warm tone], [long pause], [excited tone], etc.
    These are TTS inflection cues, not meant for display.
    """
    cleaned = re.sub(r'\[[\w\s]+?\]', '', text)
    # Clean up extra whitespace
    cleaned = re.sub(r'  +', ' ', cleaned).strip()
    return cleaned


def align_timestamps_to_original(word_timestamps: list[dict], original_text: str) -> list[dict]:
    """Replace Whisper-recognized words with original text words, keeping timestamps.

    Uses character-count-based proportional mapping for better sync accuracy.
    Korean syllable count correlates more closely with speech duration than word count.

    Strategy:
    1. Build cumulative character position for both Whisper words and original words
    2. For each original word, find the Whisper timestamp at matching character ratio
    3. Anchor start of audio precisely (first word starts at Whisper's first timestamp)
    """
    original_words = original_text.split()
    N = len(word_timestamps)
    M = len(original_words)

    if N == 0 or M == 0:
        return word_timestamps

    # Build cumulative character positions for Whisper words
    whisper_char_cumsum = []  # cumulative char count BEFORE each whisper word
    total_w_chars = 0
    for w in word_timestamps:
        whisper_char_cumsum.append(total_w_chars)
        total_w_chars += len(w["word"])

    # Build cumulative character positions for original words
    orig_char_cumsum = []  # cumulative char count BEFORE each original word
    total_o_chars = 0
    for w in original_words:
        orig_char_cumsum.append(total_o_chars)
        total_o_chars += len(w)

    if total_w_chars == 0 or total_o_chars == 0:
        return word_timestamps

    audio_start = word_timestamps[0]["start"]
    audio_end = word_timestamps[-1]["end"]
    audio_duration = audio_end - audio_start

    def char_ratio_to_time(ratio: float) -> float:
        """Convert a character ratio (0.0~1.0) to audio time using Whisper anchors."""
        # Find the two Whisper words that bracket this ratio position
        target_chars = ratio * total_w_chars
        # Binary search for the right Whisper word
        lo, hi = 0, N - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if whisper_char_cumsum[mid] <= target_chars:
                lo = mid
            else:
                hi = mid - 1
        # lo = index of Whisper word whose cumulative position is <= target
        w = word_timestamps[lo]
        # Interpolate within this word's time span
        word_start_chars = whisper_char_cumsum[lo]
        word_len = len(w["word"])
        if word_len > 0:
            frac = (target_chars - word_start_chars) / word_len
            frac = max(0.0, min(1.0, frac))
        else:
            frac = 0.0
        return w["start"] + frac * (w["end"] - w["start"])

    aligned = []
    for i in range(M):
        ratio_start = orig_char_cumsum[i] / total_o_chars
        ratio_end = (orig_char_cumsum[i] + len(original_words[i])) / total_o_chars

        start = char_ratio_to_time(ratio_start)
        end = char_ratio_to_time(ratio_end)

        # Ensure minimum duration per word
        if end <= start:
            end = start + 0.05

        aligned.append({
            "word": original_words[i],
            "start": start,
            "end": end,
        })

    # Anchor: first word starts at actual audio start
    if aligned:
        aligned[0]["start"] = audio_start
        # Last word ends at actual audio end
        aligned[-1]["end"] = audio_end

    print(f"  ✓ Aligned {M} original words to {N} Whisper timestamps (char-based)")
    return aligned


# ─────────────────────────────────────────────────────
# Cover image rendering
# ─────────────────────────────────────────────────────

def render_cover_frames(
    cover_image_path: Path,
    duration_seconds: float = 4.0,
    source: str = "",
    title: str = "",
    out_dir: Path = None,
    start_frame_idx: int = 0,
) -> list[dict]:
    """Render cover image frames for the opening of a docent book video.

    - Loads cover image, centers it on 1080x1080 canvas with dark bg
    - Adds source + title text at top-left
    - Returns frames_info list compatible with assemble_video()
    """
    fonts = _load_fonts()
    cover = Image.open(cover_image_path).convert("RGB")

    # Scale cover to fit in center area (with padding)
    cover_area_w = WIDTH - 160  # 80px padding each side
    cover_area_h = int(HEIGHT * 0.65)  # 65% of height for cover
    cover_area_top = int(HEIGHT * 0.18)

    # Maintain aspect ratio
    ratio = min(cover_area_w / cover.width, cover_area_h / cover.height)
    new_w = int(cover.width * ratio)
    new_h = int(cover.height * ratio)
    cover_resized = cover.resize((new_w, new_h), Image.LANCZOS)

    # Create canvas
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Paste cover centered
    paste_x = (WIDTH - new_w) // 2
    paste_y = cover_area_top + (cover_area_h - new_h) // 2
    img.paste(cover_resized, (paste_x, paste_y))

    # Source + title at top
    y_cursor = SOURCE_MARGIN_TOP
    if source:
        draw.text((SOURCE_MARGIN_LEFT, y_cursor), source.upper(), fill=SOURCE_COLOR, font=fonts["source"])
        y_cursor += SOURCE_FONT_SIZE + 5
    if title:
        t = title[:65] + "..." if len(title) > 65 else title
        draw.text((SOURCE_MARGIN_LEFT, y_cursor), t, fill=SOURCE_COLOR, font=fonts["title"])

    # Save single frame, repeat via duration
    frame_path = out_dir / f"frame_{start_frame_idx:05d}.png"
    img.save(frame_path)

    num_frames = int(duration_seconds * FPS)
    frames_info = []
    per_frame = duration_seconds / num_frames
    for i in range(num_frames):
        frames_info.append({
            "frame_path": frame_path,  # all point to same image
            "start": i * per_frame,
            "end": (i + 1) * per_frame,
        })

    print(f"  ✓ Cover: {num_frames} frames ({duration_seconds}s)")
    return frames_info


# ─────────────────────────────────────────────────────
# Multi-part text loading
# ─────────────────────────────────────────────────────

def load_parts_text(parts_dir: Path, part_ids: list[str]) -> str:
    """Load and concatenate multi-part voice letter text files.

    Args:
        parts_dir: Directory containing part files (e.g., parts/)
        part_ids: List of part IDs (e.g., ["D26a", "D26b", "D26c"])

    Returns concatenated text with tone markers stripped.
    """
    all_text = []
    for pid in part_ids:
        part_file = parts_dir / f"{pid}.txt"
        if not part_file.exists():
            print(f"  Warning: Part file not found: {part_file}")
            continue
        raw = part_file.read_text().strip()
        cleaned = _strip_tone_markers(raw)
        all_text.append(cleaned)
        print(f"  ✓ Loaded {pid}: {len(cleaned)} chars")

    combined = " ".join(all_text)
    print(f"  Total text: {len(combined)} chars from {len(all_text)} parts")
    return combined


def load_broll_images(broll_dir: Path) -> list[Path]:
    """Load b-roll images from directory, sorted by filename."""
    if not broll_dir or not broll_dir.exists():
        return []

    extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
    images = sorted([
        p for p in broll_dir.iterdir()
        if p.suffix.lower() in extensions
    ])
    if images:
        print(f"  ✓ Found {len(images)} b-roll images in {broll_dir}")
    return images


# ─────────────────────────────────────────────────────
# Word wrapping for CJK + Latin
# ─────────────────────────────────────────────────────

def _is_cjk(ch):
    """Check if character is CJK (Korean/Chinese/Japanese)."""
    cp = ord(ch)
    return (
        (0xAC00 <= cp <= 0xD7AF) or  # Hangul Syllables
        (0x3040 <= cp <= 0x309F) or  # Hiragana
        (0x30A0 <= cp <= 0x30FF) or  # Katakana
        (0x4E00 <= cp <= 0x9FFF) or  # CJK Unified
        (0x1100 <= cp <= 0x11FF) or  # Hangul Jamo
        (0x3130 <= cp <= 0x318F)     # Hangul Compatibility Jamo
    )


def _wrap_text(draw, words, font, max_width):
    """Wrap words into lines that fit within max_width.
    Handles both CJK and Latin text properly.
    """
    lines = []
    current_words = []
    current_width = 0
    space_w = draw.textbbox((0,0), " ", font=font)[2]

    for word in words:
        word_w = draw.textbbox((0,0), word, font=font)[2]
        test_width = current_width + (space_w if current_words else 0) + word_w

        if test_width > max_width and current_words:
            lines.append(current_words)
            current_words = [word]
            current_width = word_w
        else:
            current_words.append(word)
            current_width = test_width

    if current_words:
        lines.append(current_words)

    return lines


# ─────────────────────────────────────────────────────
# Segmentation — split words into sentence-based pages
# ─────────────────────────────────────────────────────

DIM_COLOR = (100, 100, 100)  # Gray for unread words

def _split_into_segments(word_timestamps: list[dict], max_words: int = SEGMENT_MAX_WORDS) -> list[list[int]]:
    """Split word indices into segments (sentence-based pages).

    Tries to break at sentence boundaries (., !, ?, 다, 요, 죠).
    Falls back to max_words if no boundary found.
    Returns list of [start_idx, end_idx] pairs.
    """
    segments = []
    i = 0
    n = len(word_timestamps)

    while i < n:
        end = min(i + max_words, n)

        if end < n:
            # Look backwards for a sentence boundary
            best_break = -1
            for j in range(end - 1, max(i + 5, i + max_words // 3) - 1, -1):
                word = word_timestamps[j]["word"]
                # Sentence-ending punctuation
                if word.endswith(('.', '!', '?', '。')) or \
                   word.endswith((',')) and j > i + 8:
                    best_break = j + 1
                    break
                # Korean sentence endings
                if any(word.endswith(s) for s in ('다.', '요.', '죠.', '다,', '요,', '에요', '해요', '거든요', '이에요')):
                    best_break = j + 1
                    break
            if best_break > i:
                end = best_break

        segments.append((i, end))
        i = end

    return segments


# ─────────────────────────────────────────────────────
# Frame rendering v3 — fixed segment, read/unread states
# ─────────────────────────────────────────────────────

def render_segment_frame(
    segment_words: list[str],
    active_idx_in_segment: int,
    source: str = "",
    title: str = "",
    accent_color: tuple = ACCENT_COLOR,
    fonts: dict = None,
    broll_image: Image.Image = None,
) -> Image.Image:
    """Render a segment frame with read/unread/active word states.

    - Words before active_idx: WHITE (already read)
    - Word at active_idx: ACCENT COLOR (currently reading)
    - Words after active_idx: DIM GRAY (not yet read)

    If broll_image is provided:
    - Image displayed in center area (12%~60% height)
    - Text moves to bottom area (68%~92% height)
    """
    if fonts is None:
        fonts = _load_fonts()

    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # ── Source + title at top-left ──
    y_cursor = SOURCE_MARGIN_TOP
    if source:
        draw.text((SOURCE_MARGIN_LEFT, y_cursor), source.upper(), fill=SOURCE_COLOR, font=fonts["source"])
        y_cursor += SOURCE_FONT_SIZE + 5
    if title:
        t = title[:65] + "..." if len(title) > 65 else title
        draw.text((SOURCE_MARGIN_LEFT, y_cursor), t, fill=SOURCE_COLOR, font=fonts["title"])

    # ── B-roll image (if provided) ──
    if broll_image is not None:
        # Image area: 12% ~ 60% of height, centered horizontally
        img_area_top = int(HEIGHT * 0.12)
        img_area_h = int(HEIGHT * 0.48)
        img_area_w = WIDTH - 120  # 60px padding each side
        # Scale while maintaining aspect ratio
        ratio = min(img_area_w / broll_image.width, img_area_h / broll_image.height)
        broll_w = int(broll_image.width * ratio)
        broll_h = int(broll_image.height * ratio)
        broll_resized = broll_image.resize((broll_w, broll_h), Image.LANCZOS)
        paste_x = (WIDTH - broll_w) // 2
        paste_y = img_area_top + (img_area_h - broll_h) // 2
        img.paste(broll_resized, (paste_x, paste_y))

        # Text area shifts to bottom
        text_top_ratio = 0.68
        text_bottom_ratio = 0.94
    else:
        # Default text area
        text_top_ratio = TEXT_AREA_TOP_RATIO
        text_bottom_ratio = TEXT_AREA_BOTTOM_RATIO

    # ── Word-wrap into lines ──
    max_text_width = WIDTH - TEXT_MARGIN_LEFT - TEXT_MARGIN_RIGHT
    lines = _wrap_text(draw, segment_words, fonts["main"], max_text_width)

    # ── Vertical position ──
    line_height = int(MAIN_FONT_SIZE * LINE_SPACING)
    total_height = len(lines) * line_height
    text_area_top = int(HEIGHT * text_top_ratio)
    text_area_bottom = int(HEIGHT * text_bottom_ratio)
    text_area_height = text_area_bottom - text_area_top
    start_y = text_area_top + (text_area_height - total_height) // 2

    # ── Draw each line, left-aligned ──
    word_counter = 0
    space_w = draw.textbbox((0, 0), " ", font=fonts["main"])[2]

    for line_words in lines:
        y = start_y
        x = TEXT_MARGIN_LEFT

        for word in line_words:
            if word_counter < active_idx_in_segment:
                color = TEXT_COLOR      # Already read → white
            elif word_counter == active_idx_in_segment:
                color = accent_color    # Currently reading → accent
            else:
                color = DIM_COLOR       # Not yet read → gray

            draw.text((x, y), word, fill=color, font=fonts["main"])
            word_w = draw.textbbox((x, y), word, font=fonts["main"])[2] - x
            x += word_w + space_w
            word_counter += 1

        start_y += line_height

    return img


# ─────────────────────────────────────────────────────
# Frame generation — segment-based pages
# ─────────────────────────────────────────────────────

def render_all_frames(
    word_timestamps: list[dict],
    source: str = "",
    title: str = "",
    accent_color: tuple = ACCENT_COLOR,
    out_dir: Path = None,
    start_frame_idx: int = 0,
    broll_images: list[Path] = None,
) -> list[dict]:
    """Render frames with fixed segments and word-level state tracking.

    Each segment stays on screen until all its words are spoken,
    then transitions to the next segment.

    If broll_images provided, distributes them evenly across segments.
    """
    fonts = _load_fonts()
    all_words = [w["word"] for w in word_timestamps]
    segments = _split_into_segments(word_timestamps)

    # Pre-load b-roll images and assign to segments
    loaded_brolls = {}  # segment_index → PIL Image
    if broll_images:
        num_segs = len(segments)
        num_imgs = len(broll_images)
        for img_idx, img_path in enumerate(broll_images):
            seg_start_range = int(img_idx * num_segs / num_imgs)
            seg_end_range = int((img_idx + 1) * num_segs / num_imgs)
            try:
                pil_img = Image.open(img_path).convert("RGB")
                for s_idx in range(seg_start_range, seg_end_range):
                    loaded_brolls[s_idx] = pil_img
                print(f"  ✓ B-roll {img_path.name} → segments {seg_start_range}-{seg_end_range - 1}")
            except Exception as e:
                print(f"  Warning: Failed to load b-roll {img_path}: {e}")

    frames_info = []
    frame_idx = start_frame_idx

    for seg_idx, (seg_start, seg_end) in enumerate(segments):
        segment_words = all_words[seg_start:seg_end]
        seg_timestamps = word_timestamps[seg_start:seg_end]
        seg_broll = loaded_brolls.get(seg_idx)

        for w_idx in range(len(segment_words)):
            frame = render_segment_frame(
                segment_words=segment_words,
                active_idx_in_segment=w_idx,
                source=source,
                title=title,
                accent_color=accent_color,
                fonts=fonts,
                broll_image=seg_broll,
            )
            path = out_dir / f"frame_{frame_idx:05d}.png"
            frame.save(path)
            frames_info.append({
                "frame_path": path,
                "start": seg_timestamps[w_idx]["start"],
                "end": seg_timestamps[w_idx]["end"],
            })
            frame_idx += 1

    return frames_info


# ─────────────────────────────────────────────────────
# TTS — Fish TTS
# ─────────────────────────────────────────────────────

def generate_tts_fish(text: str, output_path: Path, voice: str = "cwon") -> Path:
    voice_dir = FISH_TTS_VOICES / voice
    ref_audio = voice_dir / "reference.mp3"
    ref_text_file = voice_dir / "reference.txt"

    if not ref_audio.exists():
        raise FileNotFoundError(f"Fish TTS voice not found: {voice_dir}")

    ref_text = ref_text_file.read_text().strip() if ref_text_file.exists() else ""

    # Split into chunks (~300 chars max for Korean, ~400 for English)
    # For Korean, split on sentence-ending particles + periods
    if any(_is_cjk(c) for c in text):
        # Korean: split on 다/요/죠/니다 + period or question mark
        sentences = re.split(r'(?<=[.!?。])\s*', text)
    else:
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
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(FISH_SPEECH_DIR), timeout=180)
        if result.returncode != 0:
            print(f"  Warning: chunk {i} failed: {result.stderr[:200]}")
            continue
        if chunk_out.exists():
            chunk_files.append(str(chunk_out))
            print(f"  ✓ Chunk {i+1}/{len(chunks)}")

    if not chunk_files:
        raise RuntimeError("All Fish TTS chunks failed")

    if len(chunk_files) == 1:
        subprocess.run(["ffmpeg", "-i", chunk_files[0], "-y", str(output_path)], capture_output=True, timeout=30)
    else:
        subprocess.run([
            "python3", str(MERGE_SCRIPT), *chunk_files,
            "-o", str(output_path),
            "--silence-min", "0.4", "--silence-max", "0.7",
            "--fade-ms", "20", "--seed", "42",
        ], capture_output=True, timeout=60)

    if not output_path.exists():
        raise RuntimeError(f"TTS output not created: {output_path}")
    print(f"  ✓ Voiceover: {output_path}")
    return output_path


def generate_tts_edge(text: str, output_path: Path, voice: str = "en-US-GuyNeural") -> Path:
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
    print("  Running Whisper for word timestamps...")
    env = os.environ.copy()
    # Use GPU if available, fallback to CPU
    script = f"""
import torch, whisper, json
_dev = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("base", device=_dev)
result = model.transcribe("{audio_path}", language="{lang[:2]}", word_timestamps=True)
words = []
for seg in result.get("segments", []):
    for w in seg.get("words", []):
        words.append({{"word": w["word"].strip(), "start": w["start"], "end": w["end"]}})
print(json.dumps(words, ensure_ascii=False))
"""
    venvs = [
        Path.home() / "2lab.ai" / "skills" / "shorts" / ".venv" / "bin" / "python",
        FISH_SPEECH_DIR / ".venv" / "bin" / "python",
    ]
    for venv_python in venvs:
        if not venv_python.exists():
            continue
        result = subprocess.run(
            [str(venv_python), "-c", script],
            capture_output=True, text=True, env=env, timeout=3600,
        )
        if result.returncode == 0 and result.stdout.strip():
            words = json.loads(result.stdout.strip())
            print(f"  ✓ {len(words)} word timestamps")
            return words

    print("  Warning: Whisper failed, using estimated timestamps")
    return []


# ─────────────────────────────────────────────────────
# Video Assembly
# ─────────────────────────────────────────────────────

def assemble_video(frames_info: list[dict], voiceover: Path, output: Path, music_path: Path = None) -> Path:
    print("  Assembling video...")
    work_dir = output.parent if output.parent.exists() else Path(tempfile.mkdtemp())

    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(voiceover)],
        capture_output=True, text=True,
    )
    total_duration = float(result.stdout.strip())

    # Concat file
    concat_file = work_dir / "concat_frames.txt"
    lines = []
    for i, fi in enumerate(frames_info):
        if i + 1 < len(frames_info):
            dur = frames_info[i + 1]["start"] - fi["start"]
        else:
            dur = fi["end"] - fi["start"]
        dur = max(dur, 0.03)
        lines.append(f"file '{fi['frame_path']}'")
        lines.append(f"duration {dur:.4f}")
    if frames_info:
        lines.append(f"file '{frames_info[-1]['frame_path']}'")
    concat_file.write_text("\n".join(lines))

    frames_video = work_dir / "frames_video.mp4"
    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-vf", f"scale={WIDTH}:{HEIGHT}",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p", "-r", str(FPS),
        str(frames_video), "-y", "-loglevel", "warning",
    ], timeout=180)

    # Get frames video duration for explicit trim
    fv_result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(frames_video)],
        capture_output=True, text=True,
    )
    frames_duration = float(fv_result.stdout.strip()) if fv_result.stdout.strip() else total_duration

    if music_path and Path(music_path).exists():
        subprocess.run([
            "ffmpeg", "-i", str(frames_video), "-i", str(voiceover),
            "-stream_loop", "-1", "-i", str(music_path),
            "-filter_complex",
            f"[2:a]aloop=loop=-1:size=2e+09,atrim=0:{total_duration},volume=0.08[music];"
            f"[1:a][music]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac",
            "-t", str(frames_duration),
            str(output), "-y", "-loglevel", "warning",
        ], timeout=600)
    else:
        subprocess.run([
            "ffmpeg", "-i", str(frames_video), "-i", str(voiceover),
            "-c:v", "copy", "-c:a", "aac",
            "-t", str(frames_duration),
            str(output), "-y", "-loglevel", "warning",
        ], timeout=600)

    if output.exists():
        size_mb = output.stat().st_size / (1024 * 1024)
        print(f"  ✓ Video: {output} ({size_mb:.1f} MB)")
    else:
        raise RuntimeError(f"Assembly failed: {output}")
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
    audio_path: Path = None,
    cover_image: Path = None,
    cover_duration: float = 4.0,
    broll_dir: Path = None,
):
    work_dir = Path(tempfile.mkdtemp(prefix="textcard_"))
    has_audio = audio_path and Path(audio_path).exists()
    has_cover = cover_image and Path(cover_image).exists()
    steps = 4 if not has_audio else 3
    step_names = []
    if has_cover:
        steps += 1

    print(f"\n  ═══ Text Card v3 ═══")
    print(f"  Work: {work_dir}")
    if has_audio:
        print(f"  Audio: {audio_path} (pre-rendered, skip TTS)")
    else:
        print(f"  TTS: {tts_provider} | Lang: {lang}")
    if has_cover:
        print(f"  Cover: {cover_image} ({cover_duration}s)")
    print(f"  Text: {text[:80]}...")

    step_num = 0

    # 1. Voiceover (skip if --audio provided)
    if has_audio:
        vo_path = work_dir / "voiceover.wav"
        audio_ext = Path(audio_path).suffix.lower()
        if audio_ext in (".mp3", ".m4a", ".aac", ".ogg"):
            # Convert to wav for Whisper
            step_num += 1
            print(f"\n  [{step_num}/{steps}] Converting audio to WAV for Whisper...")
            subprocess.run([
                "ffmpeg", "-i", str(audio_path), "-ar", "16000", "-ac", "1",
                str(vo_path), "-y", "-loglevel", "quiet"
            ], timeout=120)
        else:
            import shutil
            shutil.copy2(str(audio_path), str(vo_path))
        vo_for_assembly = Path(audio_path)  # Use original for assembly (better quality)
    else:
        step_num += 1
        print(f"\n  [{step_num}/{steps}] Voiceover...")
        vo_path = work_dir / "voiceover.wav"
        if tts_provider == "fish":
            generate_tts_fish(text, vo_path, voice=tts_voice or "cwon")
        else:
            vo_mp3 = work_dir / "voiceover.mp3"
            generate_tts_edge(text, vo_mp3, voice=tts_voice or "en-US-GuyNeural")
            subprocess.run(["ffmpeg", "-i", str(vo_mp3), "-ar", "16000", "-ac", "1", str(vo_path), "-y", "-loglevel", "quiet"], timeout=30)
        vo_for_assembly = None  # Will be set later

    # 2. Timestamps
    step_num += 1
    print(f"\n  [{step_num}/{steps}] Timestamps...")
    word_timestamps = get_word_timestamps(vo_path, lang=lang)
    if word_timestamps:
        # Align Whisper timestamps to original text words
        # Whisper STT may produce different words (phonetic), so we use
        # the original script text for display while keeping Whisper's timing
        word_timestamps = align_timestamps_to_original(word_timestamps, text)
    else:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(vo_path)],
            capture_output=True, text=True,
        )
        duration = float(result.stdout.strip())
        # Strip tone markers from display text for fallback timestamps
        display_text = _strip_tone_markers(text)
        words = display_text.split()
        per_word = duration / max(len(words), 1)
        word_timestamps = [{"word": w, "start": i * per_word, "end": (i + 1) * per_word} for i, w in enumerate(words)]

    # 2.5. Load b-roll images (if provided)
    broll_images = load_broll_images(Path(broll_dir)) if broll_dir else []

    # 3. Cover frames (if provided)
    cover_frames = []
    if has_cover:
        step_num += 1
        print(f"\n  [{step_num}/{steps}] Cover image...")
        frames_dir = work_dir / "frames"
        frames_dir.mkdir(exist_ok=True)
        cover_frames = render_cover_frames(
            cover_image_path=Path(cover_image),
            duration_seconds=cover_duration,
            source=source, title=title,
            out_dir=frames_dir,
            start_frame_idx=0,
        )

    # 4. Render text frames
    step_num += 1
    print(f"\n  [{step_num}/{steps}] Rendering {len(word_timestamps)} text frames...")
    frames_dir = work_dir / "frames"
    frames_dir.mkdir(exist_ok=True)
    text_frame_start = len(cover_frames)  # offset for frame numbering

    # Offset word timestamps if cover exists
    if cover_frames:
        cover_end = cover_duration
        for wt in word_timestamps:
            wt["start"] += cover_end
            wt["end"] += cover_end

    frames_info = render_all_frames(
        word_timestamps=word_timestamps,
        source=source, title=title,
        accent_color=accent_color,
        out_dir=frames_dir,
        start_frame_idx=text_frame_start,
        broll_images=broll_images if broll_images else None,
    )
    print(f"  ✓ {len(frames_info)} text frames")

    # Combine cover + text frames
    all_frames = cover_frames + frames_info
    print(f"  Total frames: {len(all_frames)}")

    # 5. Assemble
    step_num += 1
    print(f"\n  [{step_num}/{steps}] Assembly...")
    if output_path is None:
        MEDIA_DIR.mkdir(parents=True, exist_ok=True)
        output_path = MEDIA_DIR / "textcard_latest.mp4"

    if vo_for_assembly is None:
        if vo_path.suffix == ".wav":
            vo_mp3_out = work_dir / "voiceover_final.mp3"
            subprocess.run(["ffmpeg", "-i", str(vo_path), "-codec:a", "libmp3lame", "-b:a", "192k", str(vo_mp3_out), "-y", "-loglevel", "quiet"], timeout=30)
            vo_for_assembly = vo_mp3_out if vo_mp3_out.exists() else vo_path
        else:
            vo_for_assembly = vo_path

    # If we have cover, we need to add silence at the beginning of the audio
    if has_cover:
        audio_with_silence = work_dir / "audio_with_cover_silence.mp3"
        subprocess.run([
            "ffmpeg",
            "-f", "lavfi", "-t", str(cover_duration),
            "-i", f"anullsrc=channel_layout=stereo:sample_rate=44100",
            "-i", str(vo_for_assembly),
            "-filter_complex", f"[0:a][1:a]concat=n=2:v=0:a=1[out]",
            "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "192k",
            str(audio_with_silence), "-y", "-loglevel", "warning",
        ], timeout=120)
        if audio_with_silence.exists():
            vo_for_assembly = audio_with_silence

    result = assemble_video(all_frames, vo_for_assembly, output_path, music_path)
    print(f"\n  ═══ Done! ═══\n  Output: {result}")
    return result


# ─────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Text Card Video v3")
    inp = parser.add_mutually_exclusive_group(required=False)
    inp.add_argument("--draft", help="Draft JSON path")
    inp.add_argument("--text", help="Direct script text")

    parser.add_argument("--source", default="")
    parser.add_argument("--title", default="")
    parser.add_argument("--tts", default="edge", choices=["edge", "fish"])
    parser.add_argument("--voice", default=None)
    parser.add_argument("--lang", default="en")
    parser.add_argument("--accent-color", default="#C85050")
    parser.add_argument("--output", "-o", default=None)
    parser.add_argument("--music", default=None)

    # v3: New flags for docent book integration
    parser.add_argument("--audio", default=None, help="Pre-rendered audio file (skip TTS)")
    parser.add_argument("--cover-image", default=None, help="Cover image for opening frame")
    parser.add_argument("--cover-duration", type=float, default=4.0, help="Cover display duration in seconds")
    parser.add_argument("--parts-dir", default=None, help="Directory containing part text files")
    parser.add_argument("--parts", nargs="+", default=None, help="Part IDs to load (e.g., D26a D26b D26c)")
    parser.add_argument("--broll-dir", default=None, help="Directory containing b-roll images (jpg/png). Images are distributed evenly across segments.")

    args = parser.parse_args()

    # Load text from various sources
    text = None
    if args.parts_dir and args.parts:
        text = load_parts_text(Path(args.parts_dir), args.parts)
        source = args.source
        title = args.title
    elif args.draft:
        draft = json.loads(Path(args.draft).read_text())
        text = draft.get("script", "")
        source = args.source or draft.get("source", "")
        title = args.title or draft.get("youtube_title", draft.get("title", ""))
    elif args.text:
        text = args.text
        source = args.source
        title = args.title
    else:
        print("Error: Provide --text, --draft, or --parts-dir + --parts")
        sys.exit(1)

    if not text:
        print("Error: No text"); sys.exit(1)

    # Strip tone markers from display text (keep for TTS if generating)
    display_text = _strip_tone_markers(text)

    hc = args.accent_color.lstrip("#")
    accent = tuple(int(hc[i:i+2], 16) for i in (0, 2, 4))

    # If --audio is provided, use display_text for rendering
    # If TTS is needed, use original text (with tone markers for Fish TTS)
    tts_text = text if not args.audio else display_text

    run_textcard_pipeline(
        text=display_text if args.audio else tts_text,
        source=source, title=title,
        tts_provider=args.tts, tts_voice=args.voice, lang=args.lang,
        accent_color=accent,
        output_path=Path(args.output) if args.output else None,
        music_path=Path(args.music) if args.music else None,
        audio_path=Path(args.audio) if args.audio else None,
        cover_image=Path(args.cover_image) if args.cover_image else None,
        cover_duration=args.cover_duration,
        broll_dir=Path(args.broll_dir) if args.broll_dir else None,
    )


if __name__ == "__main__":
    main()
