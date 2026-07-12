#!/usr/bin/env python3
"""
place_timeline.py — 각 utt mp3 길이 ↔ 원본 슬롯 길이 비교, atempo 계산 후 dubbed_audio.wav 생성
사용법: place_timeline.py <project_dir>

입력:  <project_dir>/3_translation/sentences.json
       <project_dir>/4_synth/utt-NNN.mp3
       <project_dir>/1_source/audio.mp3 (총 길이 측정용)
출력:  <project_dir>/5_intermediate/placement.json
       <project_dir>/5_intermediate/dubbed_audio.wav  (44.1k mono PCM s16)
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


SR = 44100


def load_env(skill_dir: Path) -> None:
    env = skill_dir / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


def probe_ms(ffprobe: str, path: Path) -> int:
    out = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return int(round(float(out) * 1000))


def decode_to_mono_f32(ffmpeg: str, path: Path):
    """decode any audio to mono float32 PCM @ SR via ffmpeg."""
    import numpy as np
    cmd = [ffmpeg, "-loglevel", "error", "-i", str(path),
           "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype="<f4")


def apply_atempo(ffmpeg: str, src: Path, dst: Path, tempo: float) -> None:
    """atempo only supports 0.5..2.0 per filter — chain when needed."""
    factors: list[float] = []
    t = tempo
    while t > 2.0:
        factors.append(2.0)
        t /= 2.0
    while t < 0.5:
        factors.append(0.5)
        t /= 0.5
    factors.append(t)
    filt = ",".join(f"atempo={f:.4f}" for f in factors)
    subprocess.run(
        [ffmpeg, "-loglevel", "error", "-y", "-i", str(src),
         "-filter:a", filt, "-ac", "1", "-ar", str(SR),
         "-c:a", "pcm_f32le", str(dst)],
        check=True,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project_dir", type=Path)
    args = ap.parse_args()

    skill_dir = Path(__file__).resolve().parent.parent
    load_env(skill_dir)

    ffmpeg = os.environ.get("FFMPEG_BIN") or os.path.expanduser("~/.local/bin/ffmpeg")
    if not os.path.isfile(ffmpeg):
        from shutil import which
        ffmpeg = which("ffmpeg") or ffmpeg
    ffprobe = os.environ.get("FFPROBE_BIN") or ffmpeg.replace("ffmpeg", "ffprobe")
    if not os.path.isfile(ffprobe):
        from shutil import which
        ffprobe = which("ffprobe") or ffprobe

    try:
        import numpy as np
        import soundfile as sf
    except ImportError:
        print("[error] numpy + soundfile 필요", file=sys.stderr)
        return 4

    sent_path = args.project_dir / "3_translation" / "sentences.json"
    sentences = json.loads(sent_path.read_text(encoding="utf-8"))["sentences"]

    synth_dir = args.project_dir / "4_synth"
    inter_dir = args.project_dir / "5_intermediate"
    inter_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = inter_dir / "_tmp"
    tmp_dir.mkdir(exist_ok=True)

    atempo_max = float(os.environ.get("ATEMPO_MAX", "1.6"))
    atempo_min = float(os.environ.get("ATEMPO_MIN", "1.0"))
    trail_ms = int(os.environ.get("TRAIL_MS", "120"))

    # 총 길이 = 원본 오디오 길이
    src_audio = args.project_dir / "1_source" / "audio.mp3"
    total_ms = probe_ms(ffprobe, src_audio) + 500
    total_samples = int(total_ms / 1000 * SR)
    track = np.zeros(total_samples, dtype="<f4")

    placement: list[dict] = []
    print(f"[place] target track = {total_ms/1000:.1f}s ({total_samples} samples)")

    prev_end_ms = 0
    for s in sentences:
        i = s["i"]
        mp3 = synth_dir / f"utt-{i:03d}.mp3"
        if not mp3.exists():
            print(f"[skip] utt {i} missing mp3", file=sys.stderr)
            continue

        slot_start = max(s["start_ms"], prev_end_ms)  # 겹침 방지
        next_slot_start = s["end_ms"] + trail_ms
        slot_len_ms = max(200, next_slot_start - slot_start)

        synth_ms = probe_ms(ffprobe, mp3)
        tempo = 1.0
        if synth_ms > slot_len_ms:
            tempo = min(atempo_max, synth_ms / slot_len_ms)
        tempo = max(atempo_min, tempo)

        if abs(tempo - 1.0) > 0.01:
            tempo_wav = tmp_dir / f"utt-{i:03d}.wav"
            apply_atempo(ffmpeg, mp3, tempo_wav, tempo)
            audio = decode_to_mono_f32(ffmpeg, tempo_wav)
        else:
            audio = decode_to_mono_f32(ffmpeg, mp3)

        audio_ms = int(round(len(audio) / SR * 1000))

        start_sample = int(slot_start / 1000 * SR)
        end_sample = min(total_samples, start_sample + len(audio))
        n = end_sample - start_sample
        if n > 0:
            track[start_sample:end_sample] += audio[:n]

        placement.append({
            "i": i,
            "slot_start_ms": slot_start,
            "slot_len_ms": slot_len_ms,
            "synth_ms_raw": synth_ms,
            "tempo": round(tempo, 3),
            "audio_ms_final": audio_ms,
            "voice": None,
        })
        prev_end_ms = slot_start + audio_ms

    # soft clip (-1..1)
    np.clip(track, -1.0, 1.0, out=track)

    # write 16-bit PCM mono 44.1k
    out_wav = inter_dir / "dubbed_audio.wav"
    sf.write(str(out_wav), track, SR, subtype="PCM_16")

    (inter_dir / "placement.json").write_text(json.dumps({
        "sr": SR,
        "duration_ms": total_ms,
        "atempo_max": atempo_max,
        "atempo_min": atempo_min,
        "trail_ms": trail_ms,
        "placement": placement,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    # cleanup tmp
    for f in tmp_dir.glob("*.wav"):
        f.unlink()
    try:
        tmp_dir.rmdir()
    except OSError:
        pass

    print(f"[ok] dubbed_audio.wav  ({len(placement)} utts, max tempo applied) → {out_wav}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
