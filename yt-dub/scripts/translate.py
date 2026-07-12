#!/usr/bin/env python3
"""
translate.py — Codex/Gemini/Claude 서브에이전트로 segments → 한국어 문장 번역
사용법: translate.py <project_dir> [--engine codex|gemini|claude] [--target-lang ko]

입력:  <project_dir>/2_transcript/segments.json
출력:  <project_dir>/3_translation/sentences.json
       [{i, en, ko, start_ms, end_ms}, ...]
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


CODEX_BIN_CANDIDATES = [
    os.path.expanduser("~/2lab.ai/soma/node_modules/.bin/codex"),
    "/usr/local/bin/codex",
    "codex",
]
GEMINI_BIN_CANDIDATES = [
    os.path.expanduser("~/.local/bin/gemini"),
    "/usr/local/bin/gemini",
    "gemini",
]
CLAUDE_BIN_CANDIDATES = [
    os.path.expanduser("~/.local/bin/claude"),
    "/usr/local/bin/claude",
    "claude",
]


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


def which(candidates: list[str]) -> str | None:
    for c in candidates:
        if os.path.isabs(c):
            if os.path.isfile(c) and os.access(c, os.X_OK):
                return c
        else:
            from shutil import which as _which
            p = _which(c)
            if p:
                return p
    return None


def build_prompt(segments: list[dict], target_lang: str) -> str:
    lang_name = {"ko": "Korean", "ja": "Japanese", "en": "English"}.get(target_lang, target_lang)
    seg_lines = [f"[{s['i']:03d}] {s['text']}" for s in segments]
    return f"""You are a professional dubbing translator.

TASK: Translate every line below into NATURAL, spoken {lang_name} suitable for re-dubbing the original video.

CONSTRAINTS:
- Output MUST be a single JSON array, no other text, no markdown fences.
- Each item: {{"i": <int>, "ko": "<{target_lang}>"}}
- Preserve line order; do NOT merge or split lines.
- Match the original line's speech length when possible (don't translate too long — it must fit the same time slot).
- Use natural conversational tone, not literal translation.
- Keep proper nouns (names, brands, places) as-is unless a well-known {lang_name} equivalent exists.

INPUT LINES (English → {lang_name}):
{chr(10).join(seg_lines)}

OUTPUT (JSON array only):"""


def run_codex(prompt: str, codex_bin: str) -> str:
    model = os.environ.get("CODEX_MODEL", "gpt-5.2")
    proc = subprocess.run(
        [codex_bin, "exec", "--skip-git-repo-check", "-m", model, "-"],
        input=prompt,
        text=True,
        capture_output=True,
        timeout=600,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"codex exec failed: {proc.stderr[:500]}")
    return proc.stdout


def run_gemini(prompt: str, gemini_bin: str) -> str:
    proc = subprocess.run(
        [gemini_bin, "-p", prompt],
        text=True,
        capture_output=True,
        timeout=600,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"gemini failed: {proc.stderr[:500]}")
    return proc.stdout


def run_claude(prompt: str, claude_bin: str) -> str:
    proc = subprocess.run(
        [claude_bin, "-p", prompt],
        text=True,
        capture_output=True,
        timeout=600,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"claude failed: {proc.stderr[:500]}")
    return proc.stdout


def extract_json_array(raw: str) -> list[dict]:
    # remove markdown fences
    s = raw.strip()
    fence = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", s, re.DOTALL)
    if fence:
        s = fence.group(1)
    # find first [ ... ] block
    if not s.startswith("["):
        m = re.search(r"\[.*\]", s, re.DOTALL)
        if m:
            s = m.group(0)
    return json.loads(s)


def chunk_segments(segments: list[dict], max_chars: int = 4500) -> list[list[dict]]:
    chunks: list[list[dict]] = [[]]
    size = 0
    for s in segments:
        sz = len(s["text"]) + 16
        if size + sz > max_chars and chunks[-1]:
            chunks.append([])
            size = 0
        chunks[-1].append(s)
        size += sz
    return [c for c in chunks if c]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project_dir", type=Path)
    ap.add_argument("--engine", default=os.environ.get("TRANSLATE_ENGINE", "codex"))
    ap.add_argument("--target-lang", default=os.environ.get("TRANSLATE_TARGET_LANG", "ko"))
    args = ap.parse_args()

    skill_dir = Path(__file__).resolve().parent.parent
    load_env(skill_dir)

    seg_path = args.project_dir / "2_transcript" / "segments.json"
    if not seg_path.exists():
        print(f"[error] segments.json 없음: {seg_path}", file=sys.stderr)
        return 4

    data = json.loads(seg_path.read_text(encoding="utf-8"))
    segments = data["segments"]
    print(f"[translate] segments={len(segments)} engine={args.engine} target={args.target_lang}")

    runners = {
        "codex": (CODEX_BIN_CANDIDATES, run_codex),
        "gemini": (GEMINI_BIN_CANDIDATES, run_gemini),
        "claude": (CLAUDE_BIN_CANDIDATES, run_claude),
    }
    cands, runner = runners[args.engine]
    bin_path = which(cands)
    if not bin_path:
        print(f"[error] {args.engine} CLI 없음", file=sys.stderr)
        return 4

    chunks = chunk_segments(segments, max_chars=4500)
    print(f"[translate] {len(chunks)} chunks via {args.engine}@{bin_path}")

    out_dir = args.project_dir / "3_translation"
    out_dir.mkdir(parents=True, exist_ok=True)

    translations: dict[int, str] = {}
    for ci, chunk in enumerate(chunks):
        prompt = build_prompt(chunk, args.target_lang)
        print(f"[translate] chunk {ci+1}/{len(chunks)} ({len(chunk)} segs)")
        for attempt in range(3):
            try:
                raw = runner(prompt, bin_path)
                items = extract_json_array(raw)
                for it in items:
                    i = int(it["i"])
                    ko = (it.get("ko") or it.get("text") or "").strip()
                    if ko:
                        translations[i] = ko
                break
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"[translate] chunk {ci+1} parse fail attempt {attempt+1}: {e}", file=sys.stderr)
                if attempt == 2:
                    raise

    sentences = []
    missing = 0
    for s in segments:
        i = s["i"]
        ko = translations.get(i, "")
        if not ko:
            missing += 1
            print(f"[warn] missing translation for [{i}]: {s['text']}", file=sys.stderr)
            ko = s["text"]
        sentences.append({
            "i": i,
            "en": s["text"],
            "ko": ko,
            "start_ms": s["start_ms"],
            "end_ms": s["end_ms"],
        })

    (out_dir / "sentences.json").write_text(json.dumps({
        "engine": args.engine,
        "target_lang": args.target_lang,
        "source_language": data.get("language"),
        "total": len(sentences),
        "missing": missing,
        "sentences": sentences,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[ok] {len(sentences)} sentences (missing={missing}) → {out_dir / 'sentences.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
