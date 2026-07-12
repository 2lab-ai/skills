#!/usr/bin/env python3
"""
parse-script.py — YAML dialogue script → Fish-TTS → video-config.json

Pipeline:
  1. Parse script.yaml (speakers, voices, dialogue lines)
  2. Split long lines into scene-sized chunks
  3. Generate Fish-TTS audio for each chunk (sequential, GPU)
  4. Measure mp3 durations with ffprobe
  5. Auto-assign scene types based on content
  6. Output video-config.json

Usage:
  python3 parse-script.py <script.yaml> <tts_output_dir> [--config-out path]
"""

import json
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path

import yaml

# ── Paths ──────────────────────────────────────────────────
FISH_TTS = os.path.expanduser("~/2lab.ai/skills/fish-tts/scripts/fish-tts.sh")
FFMPEG = os.path.expanduser("~/.local/bin/ffmpeg")
FFPROBE = os.path.expanduser("~/.local/bin/ffprobe")
VALID_VOICES = {"elon", "iu", "karina", "egirl", "cwon"}
VALID_SCENE_TYPES = {
    "hero", "list", "grid", "code", "flow", "chat", "stat",
    "quote", "timeline", "comparison", "emoji", "image", "bigtext",
    "terminal", "tokenPredict", "matrixRain", "progressBar",
    "radar", "countdown", "map", "callout", "splitScreen",
    "typewriter", "pyramid", "reveal", "infographic",
}

# ── Helpers ────────────────────────────────────────────────

def log(msg):
    print(f"\033[36m[parse-script]\033[0m {msg}")

def warn(msg):
    print(f"\033[33m[parse-script]\033[0m WARN: {msg}")

def err(msg):
    print(f"\033[31m[parse-script]\033[0m ERROR: {msg}")
    sys.exit(1)


def get_duration_ms(mp3_path: str) -> int:
    """Get audio duration in ms using ffprobe."""
    try:
        r = subprocess.run(
            [FFPROBE, "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", mp3_path],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode == 0 and r.stdout.strip():
            return int(float(r.stdout.strip()) * 1000)
    except Exception:
        pass
    return 3000  # fallback


def generate_tts(text: str, voice: str, output_wav: str) -> bool:
    """Call Fish-TTS. Returns True on success."""
    try:
        r = subprocess.run(
            ["bash", FISH_TTS, text, "--voice", voice, "--output", output_wav],
            capture_output=True, text=True, timeout=180,
        )
        return r.returncode == 0 and os.path.exists(output_wav)
    except Exception as e:
        warn(f"TTS exception: {e}")
        return False


def wav_to_mp3(wav_path: str, mp3_path: str) -> bool:
    """Convert wav to mp3 with ffmpeg."""
    try:
        r = subprocess.run(
            [FFMPEG, "-i", wav_path, "-codec:a", "libmp3lame", "-b:a", "192k",
             mp3_path, "-y"],
            capture_output=True, text=True, timeout=30,
        )
        if os.path.exists(wav_path):
            os.remove(wav_path)
        return r.returncode == 0 and os.path.exists(mp3_path)
    except Exception:
        return False


def make_silence(mp3_path: str, duration_s: float = 3.0):
    """Create silent mp3 as fallback."""
    subprocess.run(
        [FFMPEG, "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono",
         "-t", str(duration_s), "-codec:a", "libmp3lame", mp3_path, "-y"],
        capture_output=True, timeout=10,
    )


# ── Scene splitting ───────────────────────────────────────

def split_text(text: str, max_chars: int = 150) -> list[str]:
    """Split long text into chunks at sentence boundaries."""
    if len(text) <= max_chars:
        return [text]

    chunks = []
    sentences = re.split(r'(?<=[.!?。])\s*', text)
    buf = ""

    for sent in sentences:
        if not sent.strip():
            continue
        if len(buf) + len(sent) > max_chars and buf:
            chunks.append(buf.strip())
            buf = sent
        else:
            buf = (buf + " " + sent).strip() if buf else sent

    if buf.strip():
        chunks.append(buf.strip())

    return chunks if chunks else [text]


# ── Scene type auto-assignment ────────────────────────────

def detect_scene_type(text: str, speaker: str, is_narrator: bool, idx: int, total: int) -> tuple[str, dict]:
    """Auto-detect scene type and generate data from text content."""

    # Short impactful text → bigtext
    if len(text) <= 25:
        return "bigtext", {
            "text": text,
            "variant": "impact" if idx % 3 == 0 else "gradient",
        }

    # Numbers/stats pattern
    stat_patterns = [
        r'\d+[%배조억만달러원]',
        r'\d+\s*(기가와트|메가와트|킬로와트|테라)',
        r'\d+\s*(년|개월|시간|분|초)\s*(안에|후|만에|내)',
    ]
    for pat in stat_patterns:
        if re.search(pat, text):
            # Extract numbers for stat display
            numbers = re.findall(r'(\d[\d,.]*)\s*([%배조억만달러원기가와트메가테라년개월시간분초]*)', text)
            stats = []
            for val, unit in numbers[:3]:
                stats.append({"label": unit or "수치", "value": val, "unit": unit})
            if stats:
                return "stat", {
                    "title": text[:30] + ("..." if len(text) > 30 else ""),
                    "stats": stats,
                }

    # List patterns
    if re.search(r'(첫째|둘째|셋째|1\.|2\.|3\.)', text):
        items_raw = re.split(r'(?:첫째|둘째|셋째|\d\.)\s*', text)
        items = [i.strip() for i in items_raw if i.strip()]
        if len(items) >= 2:
            return "list", {
                "title": items[0] if len(items[0]) < 30 else "핵심 포인트",
                "items": items[:6],
            }

    # Comparison keywords
    if re.search(r'(vs|반면|하지만|반대로|비해)', text):
        return "comparison", {
            "title": text[:40],
            "left": {"title": "A", "items": [text[:50]]},
            "right": {"title": "B", "items": [text[50:100] if len(text) > 50 else ""]},
        }

    # Non-narrator speaker → quote
    if not is_narrator:
        return "quote", {
            "quote": text,
            "author": speaker,
            "variant": "typewriter" if len(text) > 80 else "large",
        }

    # First/last scenes → hero
    if idx == 0 or idx == total - 1:
        return "hero", {
            "title": text[:40],
            "subtitle": text[40:80] if len(text) > 40 else "",
        }

    # Default narrator → flow or hero
    if len(text) > 100:
        steps = re.split(r'[.!?。]\s*', text)
        steps = [s.strip() for s in steps if s.strip()]
        if len(steps) >= 2:
            return "flow", {
                "title": steps[0][:40],
                "steps": [{"label": s[:50]} for s in steps[:5]],
            }

    return "hero", {
        "title": text[:50],
        "subtitle": text[50:100] if len(text) > 50 else "",
    }


# ── Main pipeline ─────────────────────────────────────────

def main():
    if len(sys.argv) < 3:
        err("Usage: parse-script.py <script.yaml> <tts_dir> [--config-out path]")

    yaml_path = sys.argv[1]
    tts_dir = sys.argv[2]
    config_out = None
    for i, arg in enumerate(sys.argv):
        if arg == "--config-out" and i + 1 < len(sys.argv):
            config_out = sys.argv[i + 1]

    # ── 1. Parse YAML ──
    with open(yaml_path, "r", encoding="utf-8") as f:
        script = yaml.safe_load(f)

    title = script.get("title", "Untitled Video")
    theme = script.get("theme", "default")
    subtitle_variant = script.get("subtitleVariant", "stroke")
    voices_map = script.get("voices", {})
    dialogue = script.get("script", [])

    if not dialogue:
        err("script.yaml has no 'script' entries")

    # Validate voices
    narrator_keys = set()
    for speaker, voice in voices_map.items():
        if voice not in VALID_VOICES:
            err(f"Unknown voice '{voice}' for speaker '{speaker}'. Valid: {VALID_VOICES}")

    # Detect narrator (first speaker listed, or 'narrator')
    narrator_speakers = set()
    for key in voices_map:
        if key.lower() in ("narrator", "나레이터", "해설"):
            narrator_speakers.add(key)
    if not narrator_speakers and voices_map:
        narrator_speakers.add(list(voices_map.keys())[0])

    log(f"Title: {title}")
    log(f"Theme: {theme}")
    log(f"Voices: {voices_map}")
    log(f"Narrators: {narrator_speakers}")
    log(f"Dialogue lines: {len(dialogue)}")

    # ── 2. Split into scenes ──
    os.makedirs(tts_dir, exist_ok=True)
    scenes_raw = []

    for entry in dialogue:
        speaker = entry.get("speaker", "narrator")
        text = entry.get("text", "").strip()
        forced_scene = entry.get("scene")
        forced_data = entry.get("data")
        entrance = entry.get("entrance")

        if not text:
            continue

        voice = voices_map.get(speaker, "iu")
        chunks = split_text(text)

        for chunk in chunks:
            scenes_raw.append({
                "speaker": speaker,
                "voice": voice,
                "text": chunk,
                "forced_scene": forced_scene,
                "forced_data": forced_data,
                "entrance": entrance,
                "is_narrator": speaker in narrator_speakers,
            })

    total_scenes = len(scenes_raw)
    log(f"Total scenes after splitting: {total_scenes}")

    # ── 3. Fish-TTS generation ──
    log(f"Generating TTS ({total_scenes} scenes)...")
    scene_data = []

    for i, raw in enumerate(scenes_raw):
        scene_id = f"s{i+1:03d}-{raw['speaker']}"
        mp3_path = os.path.join(tts_dir, f"{scene_id}.mp3")
        wav_path = f"/tmp/tts_tmp_{scene_id}.wav"

        # Skip existing valid mp3
        if os.path.exists(mp3_path):
            size = os.path.getsize(mp3_path)
            if size > 15000:
                dur = get_duration_ms(mp3_path)
                log(f"  [{i+1}/{total_scenes}] {scene_id}: SKIP ({dur}ms)")
                raw["duration_ms"] = dur
                raw["scene_id"] = scene_id
                scene_data.append(raw)
                continue

        log(f"  [{i+1}/{total_scenes}] {scene_id} ({raw['voice']}): {raw['text'][:50]}...")

        if generate_tts(raw["text"], raw["voice"], wav_path):
            if wav_to_mp3(wav_path, mp3_path):
                size = os.path.getsize(mp3_path)
                if size > 15000:
                    dur = get_duration_ms(mp3_path)
                    log(f"    → OK: {dur}ms")
                    raw["duration_ms"] = dur
                else:
                    warn(f"    → mp3 too small, using silence")
                    make_silence(mp3_path)
                    raw["duration_ms"] = 3000
            else:
                warn(f"    → ffmpeg fail, using silence")
                make_silence(mp3_path)
                raw["duration_ms"] = 3000
        else:
            warn(f"    → TTS fail, using silence")
            make_silence(mp3_path)
            raw["duration_ms"] = 3000

        raw["scene_id"] = scene_id
        scene_data.append(raw)

    # ── 4. Build video-config.json ──
    log("Building video-config.json...")
    scenes = []

    for i, raw in enumerate(scene_data):
        scene_id = raw["scene_id"]
        is_narrator = raw["is_narrator"]

        # Scene type + data
        if raw.get("forced_scene") and raw.get("forced_data"):
            scene_type = raw["forced_scene"]
            data = raw["forced_data"]
        elif raw.get("forced_scene"):
            scene_type = raw["forced_scene"]
            _, data = detect_scene_type(raw["text"], raw["speaker"], is_narrator, i, total_scenes)
        else:
            scene_type, data = detect_scene_type(raw["text"], raw["speaker"], is_narrator, i, total_scenes)

        scene = {
            "id": scene_id,
            "type": scene_type,
            "voice": raw["voice"],
            "narration": raw["text"],
            "data": data,
        }

        if raw.get("entrance"):
            scene["entrance"] = raw["entrance"]

        scenes.append(scene)

    config = {
        "title": title,
        "fps": int(script.get("fps", 30)),
        "width": int(script.get("width", 1920)),
        "height": int(script.get("height", 1080)),
        "theme": theme,
        "subtitleVariant": subtitle_variant,
        "defaultStyle": {
            "background": "#000000",
            "accentColor": "#ff6a00",
            "textColor": "#ffffff",
            "fontFamily": "'Pretendard', 'Noto Sans KR', sans-serif",
        },
        "scenes": scenes,
    }

    out_path = config_out or os.path.join(os.path.dirname(tts_dir), "video-config.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    total_dur = sum(r["duration_ms"] for r in scene_data) / 1000
    log(f"Done! {len(scenes)} scenes, {total_dur:.1f}s total")
    log(f"Config: {out_path}")
    log(f"TTS dir: {tts_dir}")


if __name__ == "__main__":
    main()
