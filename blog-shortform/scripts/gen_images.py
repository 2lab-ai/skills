#!/usr/bin/env python3
"""captions.json → 컷별 이미지 (image-gen 스킬 위임, 1024×1536 세로 2:3).

이 fork 는 OpenAI API 키를 쓰지 않는다. 대신 같은 저장소의 image-gen 스킬
(`~/2lab.ai/skills/image-gen/scripts/gen_image.py`) 을 subprocess 로 호출해
ChatGPT/Codex OAuth 세션 기반으로 이미지를 생성한다.

스타일 통일을 위해 컷별 프롬프트에 공통 접미사를 붙인다(캐릭터 일관성 100%는 보장 못 함).
substitute 옵션: 블로그 본문 이미지를 일부 컷에 끼워 다양성을 더한다.

사용 예:
    python3 gen_images.py <project_dir>                 # 전체 컷 생성
    python3 gen_images.py <project_dir> --cut 1         # 컷 1만 (샘플)
    python3 gen_images.py <project_dir> --substitute 3,6,9 --blog-images extracted.json
    python3 gen_images.py <project_dir> --reference-cut 1   # 컷1을 ref로 나머지 i2i
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    import requests
except ImportError as e:
    sys.stderr.write(f"[error] 의존성 누락: {e}\n  pip install requests\n")
    sys.exit(2)


SKILL_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = SKILL_DIR / ".env"

# image-gen 스킬 — Codex OAuth 기반, API 키 불필요
IMAGE_GEN_SCRIPT = Path(
    os.environ.get(
        "IMAGE_GEN_SCRIPT",
        str(Path.home() / "2lab.ai" / "skills" / "image-gen" / "scripts" / "gen_image.py"),
    )
)


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


STYLE_SUFFIX = (
    "flat 2D illustration, soft pastel palette, vertical 9:16 composition, "
    "korean female character Rosa Oh with warm peach tones, "
    "korean male character Joon Park with cool blue tones, "
    "consistent line weight, gentle shading, no text, no captions, no watermark"
)


def load_env() -> dict:
    """fish-tts + image-gen 모두 키가 필요 없으므로 .env 가 없어도 동작.

    .env 가 있으면 IMAGE_SIZE / IMAGE_QUALITY 만 읽음.
    """
    load_dotenv_simple(ENV_PATH)
    return {
        "IMAGE_SIZE": os.environ.get("IMAGE_SIZE", "1024x1536"),
        "IMAGE_QUALITY": os.environ.get("IMAGE_QUALITY", "high"),
    }


def build_prompt(cut: dict) -> str:
    speaker_name = "Rosa Oh" if cut["speaker"] == "A" else "Joon Park"
    scene = cut["text"]
    return (
        f"Scene for a short vertical video, speaker {speaker_name} delivering this line: "
        f"\"{scene}\". Show the speaker as the main subject with a relevant visual metaphor "
        f"of the line in the background. {STYLE_SUFFIX}"
    )


def call_image_gen(
    prompt: str,
    out_path: Path,
    size: str,
    quality: str,
    ref_path: Path | None = None,
) -> None:
    """image-gen 스킬에 위임. ref_path 가 주어지면 i2i 모드."""
    if not IMAGE_GEN_SCRIPT.exists():
        sys.stderr.write(
            f"[error] image-gen 스크립트 없음: {IMAGE_GEN_SCRIPT}\n"
            "  ~/2lab.ai/skills/image-gen/ 가 설치되어 있는지 확인하세요.\n"
        )
        sys.exit(7)

    cmd = [
        sys.executable,
        str(IMAGE_GEN_SCRIPT),
        prompt,
        "-o", str(out_path),
        "--size", size,
        "--quality", quality,
    ]
    if ref_path is not None:
        cmd += ["--input-image", str(ref_path)]

    sys.stderr.write(f"[image-gen] → {out_path.name} (size={size}, q={quality})\n")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(
            f"[error] image-gen 실패 (exit {r.returncode}):\n"
            f"  stdout: {r.stdout[-500:]}\n"
            f"  stderr: {r.stderr[-500:]}\n"
        )
        # Codex token 만료 케이스 안내
        if "token_expired" in r.stdout or "token_expired" in r.stderr:
            sys.stderr.write(
                "  → Codex OAuth 토큰 만료. `codex login` 으로 재로그인하거나\n"
                "    `codex exec --skip-git-repo-check '...'` 를 한 번 호출해 자동 refresh 시도.\n"
            )
        raise RuntimeError(f"image-gen exit={r.returncode}")
    if not out_path.exists() or out_path.stat().st_size < 1000:
        raise RuntimeError(f"image-gen 출력 파일 누락/이상: {out_path}")


def download(url: str) -> bytes:
    return requests.get(url, timeout=30).content


def main() -> int:
    p = argparse.ArgumentParser(description="image-gen 스킬 위임 컷별 이미지 생성")
    p.add_argument("project_dir")
    p.add_argument("--cut", type=int, help="특정 컷만 생성 (샘플)")
    p.add_argument(
        "--substitute",
        default="",
        help="블로그 본문 이미지로 대체할 컷 번호들 (쉼표). 예: 3,6,9",
    )
    p.add_argument("--blog-images", help="블로그 본문 이미지 URL 목록 JSON 경로 (extracted.json 또는 list)")
    p.add_argument("--skip-existing", action="store_true", help="public/images/cut_NN.png가 이미 있으면 재생성하지 않음")
    p.add_argument(
        "--reference-cut",
        type=int,
        help="해당 컷의 PNG를 reference로 사용해 다른 컷을 i2i 생성 (캐릭터 일관성 강화)",
    )
    args = p.parse_args()

    env = load_env()
    project = Path(args.project_dir).resolve()
    captions_path = project / "captions.json"
    if not captions_path.exists():
        sys.stderr.write(
            f"[error] {captions_path} 없음. tts_fish.py + recompute_timing.py를 먼저 실행하세요.\n"
        )
        return 5

    captions = json.loads(captions_path.read_text(encoding="utf-8"))["captions"]
    targets = [c for c in captions if (args.cut is None or c["index"] == args.cut)]

    sub_indices = {int(x) for x in args.substitute.split(",") if x.strip()}
    blog_imgs: list[str] = []
    if sub_indices and args.blog_images:
        bdata = json.loads(Path(args.blog_images).read_text(encoding="utf-8"))
        blog_imgs = bdata["body_images"] if isinstance(bdata, dict) else bdata

    img_dir = project / "public" / "images"
    img_dir.mkdir(parents=True, exist_ok=True)

    ref_path: Path | None = None
    if args.reference_cut is not None:
        ref_path = img_dir / f"cut_{args.reference_cut:02d}.png"
        if not ref_path.exists():
            sys.stderr.write(
                f"[error] reference cut #{args.reference_cut} 없음. "
                f"먼저 `--cut {args.reference_cut}`로 생성하세요.\n"
            )
            return 7

    generated: list[str] = []
    for c in targets:
        out = img_dir / f"cut_{c['index']:02d}.png"
        if args.skip_existing and out.exists():
            sys.stderr.write(f"[skip] #{c['index']} (이미 존재)\n")
            generated.append(str(out))
            continue
        if c["index"] in sub_indices and blog_imgs:
            url = blog_imgs[(c["index"] - 1) % len(blog_imgs)]
            sys.stderr.write(f"[sub] #{c['index']} ← blog image {url[:80]}\n")
            out.write_bytes(download(url))
        elif ref_path is not None and c["index"] != args.reference_cut:
            prompt = build_prompt(c)
            sys.stderr.write(f"[ref-gen] #{c['index']} ({c['speaker']}) ref={ref_path.name}\n")
            call_image_gen(prompt, out, env["IMAGE_SIZE"], env["IMAGE_QUALITY"], ref_path=ref_path)
        else:
            prompt = build_prompt(c)
            sys.stderr.write(f"[gen] #{c['index']} ({c['speaker']}) prompt[:80]={prompt[:80]}…\n")
            call_image_gen(prompt, out, env["IMAGE_SIZE"], env["IMAGE_QUALITY"])
        generated.append(str(out))

    print(json.dumps({"generated": generated, "count": len(generated)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
