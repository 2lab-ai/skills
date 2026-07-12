# Whisper transcription swap

This fork replaces the upstream ElevenLabs Scribe transcription layer with
local `openai-whisper`. The rest of the video-use pipeline is untouched.

## Files

| File | Role |
|------|------|
| `transcribe.py` | **Active.** Whisper-based, Scribe-compatible JSON output. |
| `transcribe_scribe.py` | Original ElevenLabs Scribe version (preserved, unused). |
| `transcribe_batch.py` | Upstream batch runner. Imports `transcribe` — works as-is. |
| `pack_transcripts.py` | Upstream packer. Consumes the Scribe-shaped JSON. Works as-is. |
| `timeline_view.py` | Upstream composite renderer. Reads word-level timestamps. Works as-is. |

## Why

- ElevenLabs Scribe = paid per-call API. Whisper = local, free, GPU-accelerated.
- `cwon-text-cards` already uses Whisper for word-level timestamps, so the
  pipeline is consistent across skills.
- No `ELEVENLABS_API_KEY` needed. `.env` can stay empty.

## Output schema (unchanged)

Emitted JSON at `<edit_dir>/transcripts/<video_stem>.json`:

```json
{
  "words": [
    {"type": "word",    "text": "Hello", "start": 0.00, "end": 0.42, "speaker_id": "speaker_0"},
    {"type": "spacing", "text": " ",     "start": 0.94, "end": 1.60},
    ...
  ],
  "language_code": "en",
  "text": "full flattened transcript",
  "model": "whisper-base"
}
```

- `spacing` entries are synthesized from gaps between Whisper words so
  `pack_transcripts.py`'s silence-based phrase breaking keeps functioning.
- `speaker_id` is always `"speaker_0"` — Whisper does not diarize.
- `--num-speakers` CLI flag is accepted and ignored (kept for signature compat
  with the batch runner).

## Configuration

### Model
Default: **`large-v3-turbo`** (809M params, ~5× faster than `large-v3` with
near-identical quality — the sweet spot for real footage on a modern GPU).

Override per-call:
```bash
python helpers/transcribe.py video.mp4 --model small
WHISPER_MODEL=large-v3 python helpers/transcribe.py video.mp4
```

Trade-offs:
- `tiny/base` — fast but mangles proper nouns.
- `small/medium` — decent for talking-head content.
- `large-v3-turbo` (default) — best quality/speed ratio on GPU.
- `large-v3` — highest quality, ~5× slower, more VRAM.

### Device
Auto-detects CUDA. Force via env:
```bash
WHISPER_DEVICE=cpu python helpers/transcribe.py video.mp4
```

### Language
Auto-detected. Force via `--language`:
```bash
python helpers/transcribe.py video.mp4 --language ko
python helpers/transcribe.py video.mp4 --language en
```

## Known issues

- **Triton JIT warning**: `fatal error: Python.h: No such file or directory`.
  Cosmetic — Whisper falls back to a slower DTW implementation. To silence:
  `sudo apt install python3-dev` (or `python3.12-dev`). ~5% speed loss without it.
- **No diarization**: if you need speaker separation, run `pyannote.audio`
  separately and merge into the `speaker_id` field post-hoc.
- **No audio events**: Scribe tags `(laughter)`, `(applause)`, `(sigh)`.
  Whisper does not. Downstream `pack_transcripts.py` handles absence gracefully.
- **Proper noun accuracy**: `base` model misheard "ElevenLabs" as "11lbs" in
  a smoke test. Upgrade to `small` or add `--language en --initial_prompt`
  hints if this bites.

## Revert to ElevenLabs

```bash
cd /home/zhugehyuk/2lab.ai/skills/video-use/helpers
mv transcribe.py transcribe_whisper.py
mv transcribe_scribe.py transcribe.py
# then put ELEVENLABS_API_KEY=... in ../.env
```

## Smoke test (verified 2026-04-20)

```bash
cd /home/zhugehyuk/2lab.ai/skills/video-use
.venv/bin/python helpers/transcribe.py /tmp/video-use-test/test.mp4 --model base
.venv/bin/python helpers/pack_transcripts.py --edit-dir /tmp/video-use-test/edit
.venv/bin/python helpers/timeline_view.py /tmp/video-use-test/test.mp4 0 10 \
  -o /tmp/video-use-test/edit/timeline.png
```

All three stages completed end-to-end on a 10.2s synthetic clip: 26 words,
3 phrases packed on silence gaps, 3336×540 timeline composite rendered.
