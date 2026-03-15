#!/usr/bin/env python3
"""
Generate TTS audio and subtitle metadata from video-config.json.
Uses edge-tts (Microsoft Edge TTS engine) for Korean voice synthesis.

Usage:
  python3 scripts/generate-tts.py [config_path] [output_dir]

Defaults:
  config_path = video-config.json
  output_dir  = public/tts
"""

import asyncio
import json
import os
import sys
from pathlib import Path

import edge_tts

# Korean voices available:
# - ko-KR-HyunsuMultilingualNeural (Male, natural)
# - ko-KR-InJoonNeural (Male)
# - ko-KR-SunHiNeural (Female)
DEFAULT_VOICE = "ko-KR-HyunsuMultilingualNeural"
DEFAULT_RATE = "+0%"
DEFAULT_PITCH = "+0Hz"


async def generate_scene_tts(
    scene_id: str,
    narration: str,
    output_dir: Path,
    voice: str = DEFAULT_VOICE,
    rate: str = DEFAULT_RATE,
) -> dict:
    """Generate TTS audio + subtitle cues for a single scene."""

    audio_filename = f"{scene_id}.mp3"
    audio_path = output_dir / audio_filename
    subtitle_cues = []

    communicate = edge_tts.Communicate(
        text=narration,
        voice=voice,
        rate=rate,
        pitch=DEFAULT_PITCH,
    )

    # Collect audio chunks and subtitle boundaries
    audio_chunks = []
    boundary_events = []

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_chunks.append(chunk["data"])
        elif chunk["type"] == "SentenceBoundary":
            # Korean returns SentenceBoundary (not WordBoundary)
            boundary_events.append({
                "text": chunk["text"],
                "offset": chunk["offset"],       # in 100ns ticks
                "duration": chunk["duration"],    # in 100ns ticks
            })
        elif chunk["type"] == "WordBoundary":
            # Some voices may still emit word boundaries
            boundary_events.append({
                "text": chunk["text"],
                "offset": chunk["offset"],
                "duration": chunk["duration"],
            })

    # Write audio file
    with open(audio_path, "wb") as f:
        for chunk in audio_chunks:
            f.write(chunk)

    # Get actual audio duration using ffprobe if available
    duration_ms = 0
    try:
        import subprocess
        ffprobe_paths = [
            os.path.expanduser("~/.local/bin/ffprobe"),
            "ffprobe",
        ]
        ffprobe_cmd = None
        for p in ffprobe_paths:
            if os.path.isfile(p) or os.path.isfile(f"/usr/bin/{p}"):
                ffprobe_cmd = p
                break

        if ffprobe_cmd:
            result = subprocess.run(
                [ffprobe_cmd, "-v", "error", "-show_entries",
                 "format=duration", "-of", "csv=p=0", str(audio_path)],
                capture_output=True, text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                duration_ms = int(float(result.stdout.strip()) * 1000)
    except Exception:
        pass

    # Build subtitle cues from boundary events
    # 100ns ticks → milliseconds: divide by 10_000
    if boundary_events:
        # Merge word boundaries into sentence-level cues if they're too granular
        merged_cues = []
        current_text = ""
        current_start = None
        current_end = 0

        for evt in boundary_events:
            start_ms = evt["offset"] // 10_000
            end_ms = (evt["offset"] + evt["duration"]) // 10_000

            if current_start is None:
                current_start = start_ms

            # If this is a sentence boundary or accumulated text is long enough
            text = evt["text"]
            if len(current_text) + len(text) > 60 and current_text:
                merged_cues.append({
                    "text": current_text.strip(),
                    "startMs": current_start,
                    "endMs": current_end,
                })
                current_text = text
                current_start = start_ms
            else:
                if current_text:
                    current_text += " "
                current_text += text

            current_end = end_ms

        # Don't forget the last cue
        if current_text.strip():
            merged_cues.append({
                "text": current_text.strip(),
                "startMs": current_start or 0,
                "endMs": current_end,
            })

        subtitle_cues = merged_cues

    # Fallback duration: estimate from text length if ffprobe failed
    if duration_ms == 0:
        if boundary_events:
            last_evt = boundary_events[-1]
            duration_ms = (last_evt["offset"] + last_evt["duration"]) // 10_000 + 200
        else:
            # Rough estimate: ~5 chars/sec for Korean
            duration_ms = max(3000, len(narration) * 200)

    return {
        "sceneId": scene_id,
        "audioFile": audio_filename,
        "durationMs": duration_ms,
        "subtitles": subtitle_cues,
    }


async def main():
    # Parse args
    config_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("video-config.json")
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("public/tts")

    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)

    # Load config
    with open(config_path) as f:
        config = json.load(f)

    # Ensure output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[TTS] Generating audio for {len(config['scenes'])} scenes...")
    print(f"[TTS] Voice: {DEFAULT_VOICE}")
    print(f"[TTS] Output: {output_dir}")
    print()

    # Generate TTS for each scene
    tts_results = []
    for i, scene in enumerate(config["scenes"]):
        scene_id = scene["id"]
        narration = scene["narration"]
        print(f"  [{i+1}/{len(config['scenes'])}] {scene_id}: {narration[:50]}...")

        result = await generate_scene_tts(scene_id, narration, output_dir)
        tts_results.append(result)

        print(f"         → {result['durationMs']}ms, {len(result['subtitles'])} subtitle cues")

    # Write metadata
    metadata_path = output_dir.parent / "tts-metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(tts_results, f, ensure_ascii=False, indent=2)

    # Also write render-config (copy of video config for Remotion)
    render_config_path = output_dir.parent / "render-config.json"
    with open(render_config_path, "w") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    total_duration = sum(r["durationMs"] for r in tts_results)
    print()
    print(f"[TTS] Done! Total audio: {total_duration/1000:.1f}s")
    print(f"[TTS] Metadata: {metadata_path}")
    print(f"[TTS] Render config: {render_config_path}")


if __name__ == "__main__":
    asyncio.run(main())
