#!/usr/bin/env python3
"""
generate-metadata-fish.py — Generate tts-metadata.json from existing Fish-TTS mp3 files.

Unlike generate-tts.py (edge-tts), this does NOT generate audio.
It reads existing mp3 files, measures durations, and creates subtitle cues
by splitting narration text into timed chunks.

Usage:
  python3 generate-metadata-fish.py <video-config.json> <tts_dir> [public_dir]
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

FFPROBE = os.path.expanduser("~/.local/bin/ffprobe")


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
    return 3000


def split_to_subtitle_cues(narration: str, duration_ms: int) -> list[dict]:
    """Split narration into timed subtitle cues (~30-40 chars each)."""
    if not narration:
        return []

    # Split at sentence endings
    sentences = []
    current = ""
    for char in narration:
        current += char
        if char in ".!?。" and len(current) > 8:
            sentences.append(current.strip())
            current = ""
    if current.strip():
        sentences.append(current.strip())

    # Further split long sentences at commas/spaces
    chunks = []
    for sent in sentences:
        if len(sent) <= 40:
            chunks.append(sent)
        else:
            words = sent.replace(",", ", ").split(" ")
            buf = ""
            for w in words:
                if len(buf) + len(w) > 35 and buf:
                    chunks.append(buf.strip())
                    buf = w
                else:
                    buf = (buf + " " + w).strip()
            if buf:
                chunks.append(buf.strip())

    if not chunks:
        chunks = [narration]

    # Distribute time evenly
    cues = []
    time_per = duration_ms / len(chunks)
    for i, text in enumerate(chunks):
        cues.append({
            "text": text,
            "startMs": int(i * time_per),
            "endMs": int((i + 1) * time_per),
        })

    return cues


def main():
    if len(sys.argv) < 3:
        print("Usage: generate-metadata-fish.py <video-config.json> <tts_dir> [public_dir]")
        sys.exit(1)

    config_path = sys.argv[1]
    tts_dir = sys.argv[2]
    public_dir = sys.argv[3] if len(sys.argv) > 3 else str(Path(tts_dir).parent)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    scenes = config.get("scenes", [])
    print(f"[metadata-fish] Processing {len(scenes)} scenes...")

    tts_results = []
    total_ms = 0

    for i, scene in enumerate(scenes):
        scene_id = scene["id"]
        narration = scene.get("narration", "")
        mp3_path = os.path.join(tts_dir, f"{scene_id}.mp3")

        if os.path.exists(mp3_path):
            duration_ms = get_duration_ms(mp3_path)
        else:
            # Estimate: ~5 chars/sec for Korean
            duration_ms = max(3000, len(narration) * 200)
            print(f"  WARN: {scene_id}.mp3 not found, estimating {duration_ms}ms")

        subtitles = split_to_subtitle_cues(narration, duration_ms)

        tts_results.append({
            "sceneId": scene_id,
            "audioFile": f"{scene_id}.mp3",
            "durationMs": duration_ms,
            "subtitles": subtitles,
        })
        total_ms += duration_ms

    # Write tts-metadata.json
    meta_path = os.path.join(public_dir, "tts-metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(tts_results, f, ensure_ascii=False, indent=2)

    # Write render-config.json (copy of config for Remotion)
    render_path = os.path.join(public_dir, "render-config.json")
    with open(render_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"[metadata-fish] Done!")
    print(f"  Total: {total_ms/1000:.1f}s ({total_ms/1000/60:.1f}min)")
    print(f"  tts-metadata: {meta_path}")
    print(f"  render-config: {render_path}")


if __name__ == "__main__":
    main()
