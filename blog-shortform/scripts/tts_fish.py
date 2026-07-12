#!/usr/bin/env python3
"""captions_draft.json → 컷별 mp3 + 통합 voice.mp3 (fish-tts HTTP service 사용).

원본 `tts_elevenlabs.py`의 fish-tts 대체판.
- ElevenLabs REST 대신 soma-voice HTTP API (`http://blade-4090:9999`) 호출
- 화자 A/B는 .env의 FISH_TTS_VOICE_A/B로 매핑 (기본: cwon / elon)
- 결합은 ffmpeg `libmp3lame` 재인코딩 + 고정 무음 gap (concat 클릭/팝 회피)

CLI 계약은 원본과 동일하게 유지:
    python3 tts_fish.py <project_dir>            # captions_draft.json 사용, 전체 + 통합
    python3 tts_fish.py <project_dir> --cut 1    # 특정 컷만 (샘플 확인용)
    python3 tts_fish.py <project_dir> --gap 0.15 # 컷 사이 무음(초). 기본 0.15
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError as e:
    sys.stderr.write(f"[error] 의존성 누락: {e}\n  pip install requests\n")
    sys.exit(2)


SKILL_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = SKILL_DIR / ".env"

DEFAULT_FISH_URL = "http://blade-4090:9999"
DEFAULT_VOICE_A = "cwon"   # 화자 A: 30대 여성, 리드
DEFAULT_VOICE_B = "elon"   # 화자 B: 20대 후반 남성, 리액션 (한국어 학습된 클론)


def load_dotenv_simple(path: Path) -> None:
    """KEY=VALUE 한 줄씩 파싱. # 주석·빈 줄 무시. 따옴표 한 겹 제거."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        v = v.strip()
        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            v = v[1:-1]
        if k and k not in os.environ:
            os.environ[k] = v


def load_env() -> dict:
    """fish-tts 는 API 키가 필요 없으므로 .env 가 없어도 기본값으로 동작."""
    load_dotenv_simple(ENV_PATH)
    env = {
        "FISH_TTS_URL": os.environ.get("FISH_TTS_URL", DEFAULT_FISH_URL).rstrip("/"),
        "FISH_TTS_VOICE_A": os.environ.get("FISH_TTS_VOICE_A", DEFAULT_VOICE_A).strip(),
        "FISH_TTS_VOICE_B": os.environ.get("FISH_TTS_VOICE_B", DEFAULT_VOICE_B).strip(),
        "FISH_TTS_TIMEOUT": float(os.environ.get("FISH_TTS_TIMEOUT", "180")),
    }
    return env


def health_check(base_url: str) -> None:
    try:
        r = requests.get(f"{base_url}/health", timeout=5)
        if r.status_code != 200:
            sys.stderr.write(f"[fish-tts] health 비정상: {r.status_code}\n")
            sys.exit(7)
    except Exception as e:
        sys.stderr.write(
            f"[error] fish-tts 서비스에 접속 실패: {base_url}/health\n"
            f"  {type(e).__name__}: {e}\n"
            "  blade-4090 의 ai.2lab.soma-voice.main.service 가 켜져 있는지 확인하세요:\n"
            "    ssh blade-4090 systemctl --user status ai.2lab.soma-voice.main.service\n"
        )
        sys.exit(7)


def synth_one(text: str, voice_id: str, base_url: str, timeout: float, out_path: Path) -> None:
    """단일 컷을 /api/tts/chunk 로 합성. MP3 192kbps 44.1kHz mono 반환."""
    url = f"{base_url}/api/tts/chunk"
    payload = {"voice": voice_id, "text": text}
    t0 = time.time()
    r = requests.post(url, json=payload, timeout=timeout)
    elapsed = time.time() - t0
    if r.status_code != 200:
        sys.stderr.write(
            f"[fish-tts] {r.status_code} ({elapsed:.1f}s) {r.text[:300]}\n"
        )
        r.raise_for_status()
    out_path.write_bytes(r.content)
    sys.stderr.write(
        f"[fish-tts] ← {out_path.name} ({len(r.content)//1024} KB, {elapsed:.1f}s)\n"
    )


def concat_mp3(parts: list[Path], out_path: Path, gap_sec: float = 0.15) -> None:
    """fish-tts 출력 MP3 를 재인코딩 concat (클릭/팝 회피).

    원본 ElevenLabs 버전은 `ffmpeg -c copy` 였지만, fish-skill SKILL.md 경고대로
    `-c copy` 는 청크 경계에서 클릭이 발생할 수 있으므로 libmp3lame 으로 재인코딩한다.
    """
    if not shutil.which("ffmpeg"):
        sys.stderr.write("[error] ffmpeg 미설치. brew install ffmpeg / apt install ffmpeg\n")
        sys.exit(4)

    work = out_path.parent
    silence = work / "_gap.mp3"
    if gap_sec > 0:
        subprocess.run(
            [
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", "anullsrc=channel_layout=mono:sample_rate=44100",
                "-t", f"{gap_sec}",
                "-c:a", "libmp3lame", "-b:a", "192k",
                str(silence),
            ],
            check=True, capture_output=True,
        )

    listfile = work / "_concat.txt"
    lines: list[str] = []
    for i, p in enumerate(parts):
        lines.append(f"file '{p.as_posix()}'")
        if gap_sec > 0 and i < len(parts) - 1:
            lines.append(f"file '{silence.as_posix()}'")
    listfile.write_text("\n".join(lines), encoding="utf-8")

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", str(listfile),
            "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "44100", "-ac", "1",
            str(out_path),
        ],
        check=True, capture_output=True,
    )

    listfile.unlink(missing_ok=True)
    silence.unlink(missing_ok=True)


def main() -> int:
    p = argparse.ArgumentParser(description="fish-tts → captions_draft.json → mp3")
    p.add_argument("project_dir", help="captions_draft.json이 있는 프로젝트 디렉토리")
    p.add_argument("--cut", type=int, help="특정 컷 번호만 생성 (샘플 확인용)")
    p.add_argument("--gap", type=float, default=0.15, help="컷 사이 무음 길이(초). 기본 0.15")
    p.add_argument("--no-merge", action="store_true", help="cut_NN.mp3만 만들고 voice.mp3는 합치지 않음")
    args = p.parse_args()

    env = load_env()
    health_check(env["FISH_TTS_URL"])

    project = Path(args.project_dir).resolve()
    draft_path = project / "captions_draft.json"
    if not draft_path.exists():
        sys.stderr.write(f"[error] {draft_path} 없음. Phase 1을 먼저 실행하세요.\n")
        return 5

    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    cuts = draft["captions"]
    voice_map = {"A": env["FISH_TTS_VOICE_A"], "B": env["FISH_TTS_VOICE_B"]}

    audio_dir = project / "public" / "audio" / "cuts"
    audio_dir.mkdir(parents=True, exist_ok=True)

    targets = [c for c in cuts if (args.cut is None or c["index"] == args.cut)]
    if not targets:
        sys.stderr.write(f"[error] 컷 #{args.cut} 없음\n")
        return 6

    sys.stderr.write(
        f"[fish-tts] base={env['FISH_TTS_URL']} "
        f"A={voice_map['A']} B={voice_map['B']} "
        f"cuts={len(targets)}/{len(cuts)}\n"
    )

    generated: list[Path] = []
    for c in targets:
        idx = c["index"]
        speaker = c["speaker"]
        text = c["text"]
        if speaker not in voice_map:
            sys.stderr.write(
                f"[error] 컷 #{idx} speaker={speaker!r} 알 수 없음 (A/B만 허용)\n"
            )
            return 8
        voice = voice_map[speaker]
        out = audio_dir / f"cut_{idx:02d}.mp3"
        sys.stderr.write(f"[fish-tts] → #{idx:02d} ({speaker}/{voice}) {len(text)}자\n")
        synth_one(text, voice, env["FISH_TTS_URL"], env["FISH_TTS_TIMEOUT"], out)
        generated.append(out)

    if args.cut is None and not args.no_merge:
        merged = project / "public" / "audio" / "voice.mp3"
        sys.stderr.write(f"[fish-tts] concat (gap={args.gap}s, re-encode 192k) → {merged}\n")
        concat_mp3(generated, merged, gap_sec=args.gap)
        print(json.dumps({"merged": str(merged), "count": len(generated)}, ensure_ascii=False))
    elif args.cut is None:
        print(json.dumps(
            {"cuts": [str(p) for p in generated], "count": len(generated), "merged": None},
            ensure_ascii=False,
        ))
    else:
        print(json.dumps({"sample": str(generated[0])}, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
