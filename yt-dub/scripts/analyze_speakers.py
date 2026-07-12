#!/usr/bin/env python3
"""
analyze_speakers.py — utterance 별 median f0 로 화자 성별 추정
사용법: analyze_speakers.py <project_dir>

입력:  <project_dir>/1_source/audio.mp3
       <project_dir>/3_translation/sentences.json
출력:  <project_dir>/4_synth/speakers.json
       [{i, gender, voice, median_f0, voiced_ratio}, ...]
"""
import argparse
import json
import os
import sys
from pathlib import Path


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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project_dir", type=Path)
    ap.add_argument("--sr", type=int, default=16000)
    args = ap.parse_args()

    skill_dir = Path(__file__).resolve().parent.parent
    load_env(skill_dir)

    audio = args.project_dir / "1_source" / "audio.mp3"
    sentences_path = args.project_dir / "3_translation" / "sentences.json"
    if not audio.exists():
        print(f"[error] audio 없음: {audio}", file=sys.stderr)
        return 4
    if not sentences_path.exists():
        print(f"[error] sentences.json 없음: {sentences_path}", file=sys.stderr)
        return 4

    try:
        import librosa
        import numpy as np
    except ImportError:
        print("[error] librosa 필요: ~/2lab.ai/.venv/bin/pip install librosa soundfile numpy", file=sys.stderr)
        return 4

    boundary = float(os.environ.get("PITCH_BOUNDARY_HZ", "165"))
    fmin = float(os.environ.get("PITCH_FMIN", "80"))
    fmax = float(os.environ.get("PITCH_FMAX", "400"))
    female_voice = os.environ.get("FISH_TTS_VOICE_FEMALE", "cwon")
    male_voice = os.environ.get("FISH_TTS_VOICE_MALE", "elon")

    print(f"[pitch] loading audio @ {args.sr}Hz mono")
    y, sr = librosa.load(str(audio), sr=args.sr, mono=True)

    data = json.loads(sentences_path.read_text(encoding="utf-8"))
    sentences = data["sentences"]

    out: list[dict] = []
    last_gender = "female"  # default if no voiced frames

    for s in sentences:
        i = s["i"]
        t0 = max(0.0, s["start_ms"] / 1000.0)
        t1 = max(t0 + 0.02, s["end_ms"] / 1000.0)
        a = int(t0 * sr)
        b = min(len(y), int(t1 * sr))
        clip = y[a:b]

        gender = last_gender
        median_f0 = 0.0
        voiced_ratio = 0.0

        if len(clip) >= int(0.1 * sr):
            try:
                f0, voiced_flag, _ = librosa.pyin(
                    clip,
                    fmin=fmin,
                    fmax=fmax,
                    sr=sr,
                    frame_length=2048,
                    hop_length=256,
                )
                voiced = f0[~np_isnan(f0)] if f0 is not None else None
                if voiced is not None and len(f0) > 0:
                    voiced_ratio = float(np.mean(voiced_flag)) if voiced_flag is not None else 0.0
                    valid = f0[np.isfinite(f0)]
                    if valid.size >= 5 and voiced_ratio >= 0.15:
                        median_f0 = float(np.median(valid))
                        gender = "female" if median_f0 >= boundary else "male"
            except Exception as e:
                print(f"[warn] utt {i} pitch fail: {e}", file=sys.stderr)

        voice = female_voice if gender == "female" else male_voice
        out.append({
            "i": i,
            "gender": gender,
            "voice": voice,
            "median_f0": round(median_f0, 1),
            "voiced_ratio": round(voiced_ratio, 3),
            "start_ms": s["start_ms"],
            "end_ms": s["end_ms"],
        })
        last_gender = gender

    counts = {"female": sum(1 for x in out if x["gender"] == "female"),
              "male":   sum(1 for x in out if x["gender"] == "male")}
    print(f"[pitch] female={counts['female']} male={counts['male']} boundary={boundary}Hz")

    out_dir = args.project_dir / "4_synth"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "speakers.json").write_text(json.dumps({
        "boundary_hz": boundary,
        "female_voice": female_voice,
        "male_voice": male_voice,
        "counts": counts,
        "utterances": out,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] speakers → {out_dir / 'speakers.json'}")
    return 0


def np_isnan(a):
    import numpy as np
    return np.isnan(a)


if __name__ == "__main__":
    sys.exit(main())
