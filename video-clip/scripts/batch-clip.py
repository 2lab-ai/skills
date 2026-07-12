#!/usr/bin/env python3
"""
Batch clip extraction from a video file.

Usage:
  python3 batch-clip.py --video /path/to/video.mp4 --clips clips.json --output-dir /tmp/clips/

clips.json format:
[
  {"id": "clip01", "start": "01:23:45", "end": "01:24:30", "description": "..."},
  {"id": "clip02", "start": "02:10:00", "end": "02:10:15", "description": "..."}
]
"""
import json
import os
import subprocess
import sys
import argparse
from pathlib import Path

FFMPEG = os.path.expanduser("~/.local/bin/ffmpeg")
FFPROBE = os.path.expanduser("~/.local/bin/ffprobe")


def extract_clip(video_path: str, start: str, end: str, output_path: str,
                 resize: str = None, no_audio: bool = False) -> dict:
    """Extract a single clip from video."""
    cmd = [FFMPEG, "-ss", start, "-to", end, "-i", video_path]

    # Video codec
    cmd.extend(["-c:v", "libx264", "-crf", "23", "-preset", "fast"])

    # Audio
    if no_audio:
        cmd.append("-an")
    else:
        cmd.extend(["-c:a", "aac", "-b:a", "128k"])

    # Resize
    if resize:
        cmd.extend(["-vf", f"scale={resize}"])

    cmd.extend(["-movflags", "+faststart", output_path, "-y"])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    if result.returncode != 0 or not os.path.exists(output_path):
        return {"success": False, "error": result.stderr[:200]}

    # Get duration
    probe = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", output_path],
        capture_output=True, text=True
    )
    duration = float(probe.stdout.strip()) if probe.returncode == 0 else 0

    size = os.path.getsize(output_path)
    return {
        "success": True,
        "path": output_path,
        "duration_sec": round(duration, 2),
        "size_bytes": size
    }


def main():
    parser = argparse.ArgumentParser(description="Batch clip extraction")
    parser.add_argument("--video", required=True, help="Source video file")
    parser.add_argument("--clips", required=True, help="JSON file with clip definitions")
    parser.add_argument("--output-dir", required=True, help="Output directory for clips")
    parser.add_argument("--resize", default=None, help="Resize output (e.g. 1920:1080)")
    parser.add_argument("--no-audio", action="store_true", help="Strip audio")
    parser.add_argument("--format", default="mp4", help="Output format extension")
    args = parser.parse_args()

    if not os.path.exists(args.video):
        print(f"Error: Video not found: {args.video}")
        sys.exit(1)

    with open(args.clips) as f:
        clips = json.load(f)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[batch-clip] Source: {args.video}")
    print(f"[batch-clip] Clips: {len(clips)}")
    print(f"[batch-clip] Output: {output_dir}")
    print()

    results = []
    for i, clip in enumerate(clips):
        clip_id = clip.get("id", f"clip_{i:03d}")
        start = clip["start"]
        end = clip["end"]
        desc = clip.get("description", "")
        output_path = str(output_dir / f"{clip_id}.{args.format}")

        print(f"  [{i+1}/{len(clips)}] {clip_id}: {start} → {end} ({desc[:50]})")

        result = extract_clip(
            args.video, start, end, output_path,
            resize=args.resize, no_audio=args.no_audio
        )
        result["id"] = clip_id
        result["start"] = start
        result["end"] = end
        results.append(result)

        if result["success"]:
            print(f"         -> OK: {result['duration_sec']}s, {result['size_bytes']/1024:.0f}KB")
        else:
            print(f"         -> FAILED: {result.get('error', 'unknown')[:100]}")

    # Write results
    results_path = output_dir / "clip-results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    success_count = sum(1 for r in results if r["success"])
    total_duration = sum(r.get("duration_sec", 0) for r in results if r["success"])

    print()
    print(f"[batch-clip] Done! {success_count}/{len(clips)} clips extracted")
    print(f"[batch-clip] Total duration: {total_duration:.1f}s")
    print(f"[batch-clip] Results: {results_path}")


if __name__ == "__main__":
    main()
