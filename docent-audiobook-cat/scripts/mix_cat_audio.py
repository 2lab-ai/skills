#!/usr/bin/env python3
"""
고양이 울음소리를 도슨트 오디오에 자연스럽게 믹싱하는 스크립트.

Usage:
  python mix_cat_audio.py --config cat-mix-config.yaml --audio-dir /tmp/docent/audio
"""

import argparse
import random
import subprocess
import yaml
from pathlib import Path


CAT_SOUNDS_DIR = Path(__file__).parent.parent / "assets" / "cat-sounds"


def get_duration_ms(filepath):
    """오디오 파일 길이(ms) 구하기"""
    result = subprocess.run(
        ["/home/zhugehyuk/.local/bin/ffprobe", "-v", "quiet",
         "-show_entries", "format=duration", "-of", "csv=p=0", str(filepath)],
        capture_output=True, text=True
    )
    return int(float(result.stdout.strip()) * 1000)


def pick_random_cat_sound(category="meow-short"):
    """카테고리에서 랜덤 고양이 소리 선택"""
    cat_dir = CAT_SOUNDS_DIR / category
    if not cat_dir.exists():
        # fallback: 전체에서 선택
        all_sounds = list(CAT_SOUNDS_DIR.rglob("*.wav")) + list(CAT_SOUNDS_DIR.rglob("*.mp3"))
        if not all_sounds:
            return None
        return random.choice(all_sounds)

    sounds = list(cat_dir.glob("*.wav")) + list(cat_dir.glob("*.mp3"))
    if not sounds:
        return None
    return random.choice(sounds)


def mix_cat_into_part(part_wav, cat_sound, insert_at_ms, volume_db=-6, output_path=None):
    """
    파트 오디오에 고양이 소리를 오버레이 믹싱.

    Args:
        part_wav: 원본 파트 WAV 경로
        cat_sound: 고양이 소리 파일 경로
        insert_at_ms: 삽입 위치 (밀리초)
        volume_db: 고양이 소리 볼륨 조절 (dB, 음수=작게)
        output_path: 출력 경로 (None이면 원본 덮어쓰기)
    """
    if output_path is None:
        output_path = str(part_wav).replace(".wav", "_cat.wav")

    # volume dB to ffmpeg volume factor
    volume_factor = 10 ** (volume_db / 20)

    # delay in ms (stereo: left|right)
    delay = f"{insert_at_ms}|{insert_at_ms}"

    cmd = [
        "/home/zhugehyuk/.local/bin/ffmpeg", "-y",
        "-i", str(part_wav),
        "-i", str(cat_sound),
        "-filter_complex",
        f"[1:a]adelay={delay},volume={volume_factor:.3f}[cat];"
        f"[0:a][cat]amix=inputs=2:duration=first:dropout_transition=0[out]",
        "-map", "[out]",
        "-ar", "44100",
        str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr[-200:]}")
        return False

    return True


def main():
    parser = argparse.ArgumentParser(description="고양이 소리 믹싱")
    parser.add_argument("--config", required=True, help="cat-mix-config.yaml 경로")
    parser.add_argument("--audio-dir", default="/tmp/docent/audio", help="오디오 디렉토리")
    parser.add_argument("--dry-run", action="store_true", help="실행 안 하고 계획만 출력")
    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    audio_dir = Path(args.audio_dir)
    book = config.get("book", "??")

    print(f"=== Book {book} 고양이 믹싱 ===")
    print(f"Audio dir: {audio_dir}")
    print(f"Interrupts: {len(config.get('interrupts', []))}")

    for i, interrupt in enumerate(config.get("interrupts", [])):
        part_id = interrupt["part"]
        pattern = interrupt.get("pattern", "pattern1")
        cat_category = interrupt.get("cat_category", "meow-short")
        cat_sound_file = interrupt.get("cat_sound")
        insert_at_ms = interrupt["insert_at_ms"]
        volume_db = interrupt.get("volume_db", -6)

        part_wav = audio_dir / f"{part_id}.wav"
        if not part_wav.exists():
            print(f"\n  [{i+1}] SKIP: {part_wav} not found")
            continue

        # 고양이 소리 선택
        if cat_sound_file:
            cat_path = CAT_SOUNDS_DIR / cat_sound_file
            if not cat_path.exists():
                cat_path = pick_random_cat_sound(cat_category)
        else:
            cat_path = pick_random_cat_sound(cat_category)

        if not cat_path:
            print(f"\n  [{i+1}] SKIP: No cat sounds found for {cat_category}")
            continue

        part_dur = get_duration_ms(part_wav)
        cat_dur = get_duration_ms(cat_path)
        output = audio_dir / f"{part_id}_cat.wav"

        print(f"\n  [{i+1}] {part_id} ({part_dur/1000:.1f}s)")
        print(f"      Pattern: {pattern}")
        print(f"      Cat: {cat_path.name} ({cat_dur/1000:.1f}s)")
        print(f"      Insert at: {insert_at_ms/1000:.1f}s")
        print(f"      Volume: {volume_db}dB")
        print(f"      Output: {output}")

        if args.dry_run:
            print("      (dry run, skipping)")
            continue

        success = mix_cat_into_part(part_wav, cat_path, insert_at_ms, volume_db, output)
        if success:
            print(f"      ✅ Mixed!")
        else:
            print(f"      ❌ Failed")

    print(f"\n=== 완료! ===")
    if not args.dry_run:
        print("고양이 믹싱된 파일: *_cat.wav")
        print("이 파일들을 합본에 사용하세요.")


if __name__ == "__main__":
    main()
