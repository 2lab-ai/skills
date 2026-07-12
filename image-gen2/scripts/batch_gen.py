#!/usr/bin/env python3
"""image-gen2: batch image generation pipeline (LLM-free prompts + verify + retry).

Ported from the @zarvan_kim Threads pipeline. Four principles:
  1. ZERO runtime LLM calls — prompts = template + subject string substitution.
  2. Concurrent generation via ThreadPoolExecutor (default 4, conservative quota).
  3. Two-stage cheap-first verification — stage 1 machine check (existence +
     resolution + PNG integrity + min size). Stage 2 vision check is OPTIONAL
     (--vision-check) and currently a TODO stub.
  4. Retry: attempts 1-2 use the original prompt, attempt 3 appends a short
     safety/clarity suffix. Final failures go to failed.jsonl.

Engine reused as-is (no new tooling): image-gen/scripts/gen_image.py
(Codex/ChatGPT OAuth, no API key). Verification uses `identify` (imagemagick).
"""
import argparse
import json
import re
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prompt_builder import build_jobs, load_subjects, load_template  # noqa: E402

GEN_IMAGE = (
    Path("~/2lab.ai/skills/image-gen/scripts/gen_image.py").expanduser()
)
DEFAULT_RETRY_SUFFIX = (
    " Clean, well-composed, safe-for-work, single clear subject, "
    "no text or watermarks."
)

_print_lock = threading.Lock()
_last_quota = {"line": None}


def log(msg: str) -> None:
    with _print_lock:
        print(msg, flush=True)


def parse_size(size: str) -> tuple[int, int]:
    m = re.match(r"^(\d+)x(\d+)$", size.strip())
    if not m:
        raise ValueError(f"Bad --size: {size!r} (expected WxH e.g. 1024x1024)")
    return int(m.group(1)), int(m.group(2))


def identify_dims(path: Path) -> tuple[int, int] | None:
    """Return (w, h) via imagemagick `identify`, or None on failure."""
    try:
        out = subprocess.run(
            ["identify", "-format", "%w %h", str(path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0:
        return None
    parts = out.stdout.strip().split()
    if len(parts) != 2:
        return None
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return None


def machine_verify(
    path: Path,
    want: tuple[int, int],
    min_bytes: int,
    aspect_tol: float = 0.05,
    min_dim: int = 512,
) -> tuple[bool, str]:
    """Stage-1 cheap verification. Returns (ok, reason).

    NOTE: the Codex backend does not strictly honor the requested --size for
    every model/plan (e.g. a 1024x1024 request can come back as 1254x1254).
    So instead of demanding an exact pixel match we verify:
      - file exists and exceeds min_bytes (PNG not empty/corrupt)
      - `identify` parses it (integrity)
      - aspect ratio matches the requested size within aspect_tol
      - both dimensions >= min_dim (not a degenerate thumbnail)
    """
    if not path.exists():
        return False, "file missing"
    size = path.stat().st_size
    if size < min_bytes:
        return False, f"too small ({size} < {min_bytes} bytes)"
    dims = identify_dims(path)
    if dims is None:
        return False, "identify failed (corrupt PNG?)"
    w, h = dims
    if w < min_dim or h < min_dim:
        return False, f"dimension too small ({w}x{h}, min {min_dim})"
    want_ar = want[0] / want[1]
    got_ar = w / h
    if abs(got_ar - want_ar) / want_ar > aspect_tol:
        return False, (
            f"aspect {w}x{h} ({got_ar:.3f}) != requested "
            f"{want[0]}x{want[1]} ({want_ar:.3f})"
        )
    return True, f"ok ({w}x{h})"


def vision_verify(path: Path, subject: str, prompt: str) -> tuple[bool, str]:
    """Stage-2 vision verification. OPTIONAL — currently a stub.

    TODO: send the generated image + a yes/no judging prompt to a Codex/gpt
    vision call ("does this image depict {subject} per the prompt?") and parse
    the verdict. Only invoked for images that PASS stage 1 but are suspect, or
    via --vision-check on all outputs. Not implemented in MVP — returns pass so
    the core machine-verify + retry path is the source of truth.
    """
    return True, "vision-check TODO (stub: auto-pass)"


def gen_once(prompt: str, out_path: Path, size: str, quality: str) -> tuple[bool, str]:
    """Call gen_image.py once. Returns (exit_ok, stderr_tail). Captures quota."""
    cmd = [
        "python3",
        str(GEN_IMAGE),
        prompt,
        "-o",
        str(out_path),
        "--size",
        size,
        "--quality",
        quality,
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        return False, "gen_image.py timeout (600s)"
    # Capture latest quota line from stderr (last matching line).
    for line in proc.stderr.splitlines():
        if line.startswith("[Codex"):
            _last_quota["line"] = line.strip()
    tail = proc.stderr.strip().splitlines()[-3:] if proc.stderr.strip() else []
    return proc.returncode == 0, " | ".join(tail)


def run_job(
    job: tuple[str, str, str], args, want: tuple[int, int]
) -> dict:
    """Generate + verify + retry one job. Returns a result dict."""
    subject, prompt, filename = job
    out_path = Path(args.out_dir).expanduser() / filename
    attempts: list[dict] = []
    last_error = ""

    for attempt in range(1, args.retries + 1):
        use_prompt = prompt
        if attempt >= 3:
            use_prompt = prompt + args.retry_suffix

        gen_ok, gen_err = gen_once(use_prompt, out_path, args.size, args.quality)
        if not gen_ok:
            last_error = f"gen failed: {gen_err}"
            attempts.append({"attempt": attempt, "stage": "gen", "error": last_error})
            continue

        ok, reason = machine_verify(out_path, want, args.min_bytes)
        if not ok:
            last_error = f"machine-verify failed: {reason}"
            attempts.append(
                {"attempt": attempt, "stage": "machine", "error": last_error}
            )
            # remove bad output so it doesn't masquerade as success
            try:
                out_path.unlink()
            except FileNotFoundError:
                pass
            continue

        if args.vision_check:
            vok, vreason = vision_verify(out_path, subject, use_prompt)
            if not vok:
                last_error = f"vision-verify failed: {vreason}"
                attempts.append(
                    {"attempt": attempt, "stage": "vision", "error": last_error}
                )
                continue

        return {
            "subject": subject,
            "filename": filename,
            "path": str(out_path),
            "ok": True,
            "attempts": attempt,
        }

    return {
        "subject": subject,
        "filename": filename,
        "path": str(out_path),
        "ok": False,
        "attempts": args.retries,
        "prompt": prompt,
        "attempt_log": attempts,
        "last_error": last_error,
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="image-gen2 batch runner (LLM-free prompts, verify + retry)"
    )
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--template", help="Template string with {subject} placeholder")
    g.add_argument("--template-file", help="Path to template file")
    ap.add_argument("--subjects", required=True, help="csv/json/txt subject list")
    ap.add_argument("--out-dir", required=True, help="Output directory for PNGs")
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--size", default="1024x1024")
    ap.add_argument("--quality", default="high", choices=("auto", "low", "medium", "high"))
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--retry-suffix", default=DEFAULT_RETRY_SUFFIX)
    ap.add_argument("--min-bytes", type=int, default=5120, help="Min PNG size (default 5KB)")
    ap.add_argument(
        "--vision-check",
        action="store_true",
        help="Enable stage-2 vision verification (currently a TODO stub).",
    )
    args = ap.parse_args()

    if not GEN_IMAGE.exists():
        sys.exit(f"Engine missing: {GEN_IMAGE}")

    want = parse_size(args.size)
    template = load_template(args.template, args.template_file)
    subjects = load_subjects(args.subjects)
    if not subjects:
        sys.exit("No subjects loaded.")
    jobs = build_jobs(template, subjects)

    out_dir = Path(args.out_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    failed_path = out_dir / "failed.jsonl"
    if failed_path.exists():
        failed_path.unlink()

    total = len(jobs)
    log(f"image-gen2: {total} jobs | concurrency={args.concurrency} | "
        f"size={args.size} quality={args.quality} retries={args.retries}")

    results: list[dict] = []
    done = 0
    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futures = {ex.submit(run_job, job, args, want): job for job in jobs}
        for fut in as_completed(futures):
            res = fut.result()
            results.append(res)
            done += 1
            mark = "OK " if res["ok"] else "FAIL"
            log(f"[{done}/{total}] {mark} {res['filename']} "
                f"(attempts={res['attempts']})"
                + ("" if res["ok"] else f" — {res.get('last_error','')}"))

    succeeded = [r for r in results if r["ok"]]
    failed = [r for r in results if not r["ok"]]

    if failed:
        with failed_path.open("w", encoding="utf-8") as f:
            for r in failed:
                f.write(json.dumps({
                    "subject": r["subject"],
                    "prompt": r["prompt"],
                    "attempts": r["attempts"],
                    "last_error": r["last_error"],
                    "attempt_log": r["attempt_log"],
                }, ensure_ascii=False) + "\n")

    log("\n=== SUMMARY ===")
    log(f"Success: {len(succeeded)}/{total}")
    log(f"Failed:  {len(failed)}/{total}")
    log(f"Out dir: {out_dir}")
    if failed:
        log(f"Failures logged: {failed_path}")
    log(f"Codex quota (last): {_last_quota['line'] or 'n/a'}")

    return 0 if not failed else 2


if __name__ == "__main__":
    raise SystemExit(main())
