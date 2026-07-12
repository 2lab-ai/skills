#!/usr/bin/env python3
"""
synthesize.py — fish-tts 로 각 utterance MP3 합성 (cwon=여 / elon=남)
사용법: synthesize.py <project_dir> [--resume]

입력:  <project_dir>/3_translation/sentences.json
       <project_dir>/4_synth/speakers.json
출력:  <project_dir>/4_synth/utt-NNN.mp3
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path
from urllib import request, error


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


def tts_chunk(base_url: str, voice: str, text: str, timeout: int) -> bytes:
    """fish-tts /api/tts/chunk endpoint — returns mp3 bytes."""
    import json as _json
    body = _json.dumps({"speaker": voice, "text": text}).encode("utf-8")
    url = base_url.rstrip("/") + "/api/tts/chunk"
    req = request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project_dir", type=Path)
    ap.add_argument("--resume", action="store_true", help="이미 합성된 utt 는 건너뜀")
    ap.add_argument("--retries", type=int, default=2)
    args = ap.parse_args()

    skill_dir = Path(__file__).resolve().parent.parent
    load_env(skill_dir)

    sent_path = args.project_dir / "3_translation" / "sentences.json"
    spk_path = args.project_dir / "4_synth" / "speakers.json"
    for p in (sent_path, spk_path):
        if not p.exists():
            print(f"[error] 없음: {p}", file=sys.stderr)
            return 4

    sentences = {s["i"]: s for s in json.loads(sent_path.read_text(encoding="utf-8"))["sentences"]}
    speakers = {u["i"]: u for u in json.loads(spk_path.read_text(encoding="utf-8"))["utterances"]}

    base_url = os.environ.get("FISH_TTS_URL", "http://blade-4090:9999")
    timeout = int(os.environ.get("FISH_TTS_TIMEOUT", "180"))

    out_dir = args.project_dir / "4_synth"
    out_dir.mkdir(parents=True, exist_ok=True)

    total = len(sentences)
    print(f"[tts] {total} utterances → {base_url}")

    failures: list[int] = []
    for idx, i in enumerate(sorted(sentences.keys())):
        s = sentences[i]
        spk = speakers.get(i, {"voice": os.environ.get("FISH_TTS_VOICE_FEMALE", "cwon")})
        voice = spk["voice"]
        text = s["ko"].strip()
        if not text:
            print(f"[skip] utt {i} empty")
            continue

        target = out_dir / f"utt-{i:03d}.mp3"
        if args.resume and target.exists() and target.stat().st_size > 200:
            continue

        ok = False
        for attempt in range(args.retries + 1):
            try:
                t0 = time.time()
                blob = tts_chunk(base_url, voice, text, timeout)
                if len(blob) < 200:
                    raise RuntimeError(f"too small: {len(blob)}B")
                target.write_bytes(blob)
                dur = time.time() - t0
                print(f"[tts] {idx+1}/{total} utt-{i:03d} voice={voice} chars={len(text)} {dur:.1f}s → {target.name}")
                ok = True
                break
            except (error.URLError, error.HTTPError, TimeoutError, RuntimeError) as e:
                print(f"[tts] utt {i} attempt {attempt+1} fail: {e}", file=sys.stderr)
                time.sleep(2 ** attempt)
        if not ok:
            failures.append(i)

    if failures:
        print(f"[warn] failed utterances: {failures}", file=sys.stderr)
        return 2
    print(f"[ok] synth → {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
