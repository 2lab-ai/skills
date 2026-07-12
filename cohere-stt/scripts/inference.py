#!/usr/bin/env python3
"""
Cohere Transcribe STT Inference Script
Model: CohereLabs/cohere-transcribe-03-2026 (2B params, Apache 2.0)
Supports: 14 languages including Korean, English, Japanese, Chinese
"""

import argparse
import json
import os
import sys
import time


def load_model(device: str = "auto", compile: bool = False):
    """Load model and processor. Returns (model, processor, device_str)."""
    import torch
    from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq

    model_id = "CohereLabs/cohere-transcribe-03-2026"

    if device == "auto":
        device_str = "cuda:0" if torch.cuda.is_available() else "cpu"
    else:
        device_str = device

    print(f"[cohere-stt] Loading model on {device_str}...", file=sys.stderr)
    t0 = time.time()

    processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, trust_remote_code=True
    ).to(device_str)
    model.eval()

    elapsed = time.time() - t0
    print(f"[cohere-stt] Model loaded in {elapsed:.1f}s", file=sys.stderr)

    return model, processor, device_str


def transcribe_files(
    model,
    processor,
    audio_files: list[str],
    language: str = "ko",
    batch_size: int = 16,
    compile: bool = False,
    punctuation: bool = True,
) -> list[dict]:
    """Transcribe a list of audio files. Returns list of {file, text, duration_s, elapsed_s}."""
    import librosa

    results = []

    t0 = time.time()
    texts = model.transcribe(
        processor=processor,
        audio_files=audio_files,
        language=language,
        batch_size=batch_size,
        compile=compile,
        punctuation=punctuation,
    )
    total_elapsed = time.time() - t0

    # Get individual durations
    for i, (fpath, text) in enumerate(zip(audio_files, texts)):
        try:
            duration = librosa.get_duration(filename=fpath)
        except Exception:
            duration = 0.0

        results.append({
            "file": fpath,
            "text": text,
            "duration_s": round(duration, 2),
        })

    return results, total_elapsed


def transcribe_single(
    model,
    processor,
    audio_path: str,
    language: str = "ko",
    compile: bool = False,
    punctuation: bool = True,
) -> str:
    """Transcribe a single audio file. Returns text string."""
    texts = model.transcribe(
        processor=processor,
        audio_files=[audio_path],
        language=language,
        compile=compile,
        punctuation=punctuation,
    )
    return texts[0]


def main():
    parser = argparse.ArgumentParser(description="Cohere Transcribe STT")
    parser.add_argument("audio", nargs="+", help="Audio file path(s)")
    parser.add_argument(
        "--language", "-l", default="ko",
        help="ISO 639-1 language code (default: ko). Supported: en,de,fr,it,es,pt,el,nl,pl,ar,vi,zh,ja,ko"
    )
    parser.add_argument(
        "--device", "-d", default="auto",
        help="Device: auto, cuda:0, cpu (default: auto)"
    )
    parser.add_argument(
        "--batch-size", "-b", type=int, default=16,
        help="Batch size for inference (default: 16)"
    )
    parser.add_argument(
        "--compile", action="store_true",
        help="Use torch.compile for faster throughput (first call has warmup cost)"
    )
    parser.add_argument(
        "--no-punctuation", action="store_true",
        help="Disable punctuation in output"
    )
    parser.add_argument(
        "--json", "-j", action="store_true",
        help="Output results as JSON"
    )
    parser.add_argument(
        "--output", "-o", default=None,
        help="Output file path (default: stdout)"
    )

    args = parser.parse_args()

    # Validate files exist
    for f in args.audio:
        if not os.path.isfile(f):
            print(f"Error: File not found: {f}", file=sys.stderr)
            sys.exit(1)

    # Load model
    model, processor, device_str = load_model(device=args.device, compile=args.compile)

    # Transcribe
    results, total_elapsed = transcribe_files(
        model,
        processor,
        args.audio,
        language=args.language,
        batch_size=args.batch_size,
        compile=args.compile,
        punctuation=not args.no_punctuation,
    )

    # Calculate stats
    total_audio_s = sum(r["duration_s"] for r in results)
    rtfx = total_audio_s / total_elapsed if total_elapsed > 0 else 0

    # Output
    if args.json:
        output = {
            "results": results,
            "stats": {
                "total_files": len(results),
                "total_audio_s": round(total_audio_s, 2),
                "total_elapsed_s": round(total_elapsed, 2),
                "rtfx": round(rtfx, 1),
                "device": device_str,
                "language": args.language,
            },
        }
        text = json.dumps(output, ensure_ascii=False, indent=2)
    else:
        lines = []
        for r in results:
            if len(args.audio) > 1:
                lines.append(f"[{os.path.basename(r['file'])}] {r['text']}")
            else:
                lines.append(r["text"])
        lines.append("")
        lines.append(
            f"# {len(results)} files, {total_audio_s:.1f}s audio, "
            f"{total_elapsed:.1f}s processing, RTFx={rtfx:.1f}, "
            f"device={device_str}"
        )
        text = "\n".join(lines)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"[cohere-stt] Output written to {args.output}", file=sys.stderr)
    else:
        print(text)


if __name__ == "__main__":
    main()
