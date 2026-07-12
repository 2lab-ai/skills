#!/usr/bin/env python3
"""
Fish-TTS 오디오에서 faster-whisper로 자막 타이밍을 추출하고
tts-metadata.json + render-config.json을 재생성하는 스크립트.

Usage:
  python sync_subtitles.py --book 16
  python sync_subtitles.py --book 17
"""

import argparse
import json
import os
import subprocess
from pathlib import Path

from faster_whisper import WhisperModel


def get_audio_duration_ms(filepath):
    """ffprobe로 오디오 길이(ms) 구하기"""
    result = subprocess.run(
        ["/home/zhugehyuk/.local/bin/ffprobe", "-v", "quiet", "-show_entries",
         "format=duration", "-of", "csv=p=0", str(filepath)],
        capture_output=True, text=True
    )
    return int(float(result.stdout.strip()) * 1000)


def convert_wav_to_mp3(wav_path, mp3_path):
    """WAV를 MP3로 변환"""
    subprocess.run(
        ["/home/zhugehyuk/.local/bin/ffmpeg", "-y", "-i", str(wav_path),
         "-codec:a", "libmp3lame", "-q:a", "4", str(mp3_path)],
        capture_output=True
    )


def transcribe_with_timing(model, audio_path):
    """faster-whisper로 세그먼트별 타이밍 추출"""
    segments, info = model.transcribe(
        str(audio_path),
        language="ko",
        beam_size=5,
        word_timestamps=True,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=300),
    )

    subtitles = []
    for segment in segments:
        text = segment.text.strip()
        if not text:
            continue
        start_ms = int(segment.start * 1000)
        end_ms = int(segment.end * 1000)
        subtitles.append({
            "text": text,
            "startMs": start_ms,
            "endMs": end_ms
        })

    return subtitles


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", type=int, required=True, choices=[16, 17])
    parser.add_argument("--model-size", default="large-v3", help="Whisper model size")
    args = parser.parse_args()

    book = args.book

    # Paths
    audio_dir = Path("/tmp/docent/audio")
    config_path = Path(f"/tmp/docent/book{book}/video-config.json")

    # Book 16: workspace from first render
    if book == 16:
        workspace = Path("/tmp/video-gen-1774430524-774840")
        wav_files = sorted(audio_dir.glob(f"D{book}*.wav"))  # D16a-D16i
    else:
        workspace = Path("/tmp/video-gen-1774432116-784491")
        wav_files = sorted(audio_dir.glob(f"D{book}*.wav"))  # D17a-D17h

    tts_dir = workspace / "public" / "tts"

    print(f"=== Book {book} 자막 동기화 ===")
    print(f"WAV files: {len(wav_files)}")
    print(f"Workspace: {workspace}")

    # Load video config
    with open(config_path) as f:
        config = json.load(f)

    scenes = config["scenes"]

    # Load whisper model
    print(f"\n[1/4] Loading Whisper model ({args.model_size})...")
    model = WhisperModel(args.model_size, device="cpu", compute_type="int8")

    # Scene mapping: scene[0] is cover (short, no WAV), scenes[1:] map to WAV files
    # Cover scene: just use its narration text with simple timing
    cover_scene = scenes[0]
    cover_mp3 = tts_dir / f"{cover_scene['id']}.mp3"

    tts_metadata = []

    # Handle cover scene
    if cover_mp3.exists():
        cover_dur = get_audio_duration_ms(cover_mp3)
    else:
        cover_dur = int(cover_scene.get("durationInSeconds", 4) * 1000)

    tts_metadata.append({
        "sceneId": cover_scene["id"],
        "audioFile": f"{cover_scene['id']}.mp3",
        "durationMs": cover_dur,
        "subtitles": [{
            "text": cover_scene["narration"],
            "startMs": 50,
            "endMs": cover_dur - 50
        }]
    })
    print(f"\n  Cover: {cover_scene['id']} → {cover_dur}ms")

    # Process each WAV file with whisper
    print(f"\n[2/4] Whisper 자막 추출 중...")
    for i, wav_file in enumerate(wav_files):
        scene = scenes[i + 1]  # Skip cover scene
        scene_id = scene["id"]
        mp3_name = f"{scene_id}.mp3"
        mp3_path = tts_dir / mp3_name

        print(f"\n  [{i+1}/{len(wav_files)}] {wav_file.name} → {scene_id}")

        # Convert WAV to MP3 and copy to tts dir (replacing edge-tts version)
        convert_wav_to_mp3(wav_file, mp3_path)

        # Get duration
        duration_ms = get_audio_duration_ms(mp3_path)
        print(f"    Duration: {duration_ms/1000:.1f}s")

        # Transcribe with whisper
        subtitles = transcribe_with_timing(model, wav_file)
        print(f"    Subtitles: {len(subtitles)} segments")

        # Show first few
        for sub in subtitles[:3]:
            print(f"      [{sub['startMs']/1000:.1f}s-{sub['endMs']/1000:.1f}s] {sub['text'][:50]}...")
        if len(subtitles) > 3:
            print(f"      ... +{len(subtitles)-3} more")

        tts_metadata.append({
            "sceneId": scene_id,
            "audioFile": mp3_name,
            "durationMs": duration_ms,
            "subtitles": subtitles
        })

    # Write tts-metadata.json
    print(f"\n[3/4] tts-metadata.json 저장...")
    metadata_path = workspace / "public" / "tts-metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(tts_metadata, f, ensure_ascii=False, indent=2)
    print(f"  → {metadata_path}")

    # Update render-config.json with correct durations
    print(f"\n[4/4] render-config.json 업데이트...")
    render_config_path = workspace / "public" / "render-config.json"
    with open(render_config_path) as f:
        render_config = json.load(f)

    # If render_config is a dict with scenes key
    if isinstance(render_config, dict) and "scenes" in render_config:
        rc_scenes = render_config["scenes"]
    else:
        rc_scenes = render_config

    # Update scene durations from tts_metadata
    metadata_by_id = {m["sceneId"]: m for m in tts_metadata}
    total_frames = 0

    if isinstance(rc_scenes, list):
        for rc_scene in rc_scenes:
            sid = rc_scene.get("id") or rc_scene.get("sceneId", "")
            if sid in metadata_by_id:
                dur_ms = metadata_by_id[sid]["durationMs"]
                frames = int(dur_ms / 1000 * config["fps"]) + 30  # +30 for transition
                rc_scene["durationInFrames"] = frames
                total_frames += frames
                print(f"  {sid}: {dur_ms}ms → {frames} frames")

    if isinstance(render_config, dict):
        render_config["totalDurationInFrames"] = total_frames

    with open(render_config_path, "w") as f:
        json.dump(render_config, f, ensure_ascii=False, indent=2)

    print(f"\n  Total: {total_frames} frames ({total_frames/config['fps']:.1f}s)")
    print(f"\n=== 완료! Remotion 재렌더링 준비됨 ===")
    print(f"  Workspace: {workspace}")


if __name__ == "__main__":
    main()
