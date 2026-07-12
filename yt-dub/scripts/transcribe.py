#!/usr/bin/env python3
"""
transcribe.py — faster-whisper 로 word-level STT
사용법: transcribe.py <project_dir> [--model large-v3] [--language auto] [--device cuda]

입력:  <project_dir>/1_source/audio.mp3
출력:  <project_dir>/2_transcript/words.json     (machine)
       <project_dir>/2_transcript/segments.json  (utterance grouping)
       <project_dir>/2_transcript/transcript.md  (번역 입력용)
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
    ap.add_argument("--model", default=os.environ.get("FW_MODEL", "large-v3"))
    ap.add_argument("--language", default=None, help="auto-detect 이면 비워둠")
    ap.add_argument("--device", default=os.environ.get("FW_DEVICE", "cuda"))
    ap.add_argument("--compute-type", default=os.environ.get("FW_COMPUTE_TYPE", "float16"))
    ap.add_argument("--no-vad", action="store_true")
    args = ap.parse_args()

    skill_dir = Path(__file__).resolve().parent.parent
    load_env(skill_dir)

    audio = args.project_dir / "1_source" / "audio.mp3"
    if not audio.exists():
        print(f"[error] audio 없음: {audio}", file=sys.stderr)
        return 4

    out_dir = args.project_dir / "2_transcript"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[whisper] loading {args.model} on {args.device} ({args.compute_type})")
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("[error] faster-whisper 설치 필요: ~/2lab.ai/.venv/bin/pip install faster-whisper", file=sys.stderr)
        return 4

    vad = not args.no_vad and os.environ.get("FW_VAD", "true").lower() == "true"

    try:
        model = WhisperModel(args.model, device=args.device, compute_type=args.compute_type)
    except Exception as e:
        print(f"[whisper] {args.device} 실패 → cpu 폴백: {e}", file=sys.stderr)
        model = WhisperModel(args.model, device="cpu", compute_type="int8")

    print(f"[whisper] transcribe {audio} (vad={vad}, language={args.language or 'auto'})")
    segments_iter, info = model.transcribe(
        str(audio),
        language=args.language,
        word_timestamps=True,
        vad_filter=vad,
        vad_parameters={"min_silence_duration_ms": 400} if vad else None,
        beam_size=5,
    )
    print(f"[whisper] detected language={info.language} (prob={info.language_probability:.2f})")

    words: list[dict] = []
    segments: list[dict] = []
    full_text_parts: list[str] = []

    for seg in segments_iter:
        seg_words = []
        for w in (seg.words or []):
            wd = {
                "word": w.word.strip(),
                "start_ms": int(round(w.start * 1000)),
                "end_ms": int(round(w.end * 1000)),
                "prob": float(getattr(w, "probability", 0.0) or 0.0),
            }
            if not wd["word"]:
                continue
            words.append(wd)
            seg_words.append(wd)

        text = seg.text.strip()
        if not text:
            continue
        segments.append({
            "i": len(segments),
            "start_ms": int(round(seg.start * 1000)),
            "end_ms": int(round(seg.end * 1000)),
            "text": text,
            "word_count": len(seg_words),
        })
        full_text_parts.append(text)

    print(f"[whisper] words={len(words)}, segments={len(segments)}")

    (out_dir / "words.json").write_text(json.dumps({
        "language": info.language,
        "language_probability": info.language_probability,
        "duration": info.duration,
        "model": args.model,
        "words": words,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    (out_dir / "segments.json").write_text(json.dumps({
        "language": info.language,
        "duration": info.duration,
        "segments": segments,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    # transcript.md — 번역기에게 줄 입력
    lines = [
        f"# Transcript",
        f"- language: {info.language} (prob {info.language_probability:.2f})",
        f"- duration: {info.duration:.1f}s",
        f"- segments: {len(segments)}",
        "",
    ]
    for s in segments:
        t0 = s["start_ms"] / 1000
        t1 = s["end_ms"] / 1000
        lines.append(f"[{s['i']:03d}] {t0:.2f}–{t1:.2f}  {s['text']}")
    (out_dir / "transcript.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"[ok] transcript → {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
