# fish-tts — Voice Cloning TTS + STT (soma-voice HTTP service)

Fish Speech S2 Pro (4B, GPU) + Cohere STT, served as systemd user service on blade-4090.
Text in → cloned voice MP3 out. Audio in → Korean transcript out.

**Triggers:** "TTS", "음성 생성", "말해줘", "fish-tts", "soma-voice", "STT", "받아쓰기"

---

## 🚀 Service Endpoint (PRIMARY PATH)

**Base URL:** `http://blade-4090:9999`
**Service:** `ai.2lab.soma-voice.main.service` (systemd user, auto-restart)
**Binary:** `/opt/soma-voice/main/target/release/soma-voice`
**Status check:** `systemctl --user status ai.2lab.soma-voice.main.service`

> ✅ **Use HTTP API for everything.** Direct Python (`gpu-inference.py`) is fallback only.

### Health Check (always start here)
```bash
curl -s http://blade-4090:9999/health
# {"status":"ok"}
```

---

## Available Voices

```bash
curl -s http://blade-4090:9999/api/voices
```

| ID | Aliases | Description |
|----|---------|-------------|
| `cwon` ⭐ | `cown`, `chaewon` | Female, 김채원 (LESSERAFIM) — 기본 비서 음성 |
| `elon` | – | Male, Elon-style (Korean 37s ref) |
| `karina` | – | Female, aespa Karina (Korean 43s ref) |
| `iu` | – | Female, IU (Korean 47s ref) |
| `egirl` | – | Female, default e-girl (Korean 22s ref) |

Resolve alias: `GET /api/voices/{id-or-alias}` → returns canonical id.

Voice files: `~/2lab.ai/skills/fish-tts/voices/<id>/reference.{mp3,txt}`

---

## 🔥 Quick Recipes

### 1. Single chunk (sync, simplest)
```bash
curl -sS -m 240 -o out.mp3 \
  -X POST http://blade-4090:9999/api/tts/chunk \
  -H "Content-Type: application/json" \
  -d '{"voice":"cwon","text":"안녕 오빠. 오늘 일정 정리해줄게."}'
# → MP3 192kbps 44.1kHz mono, ID3v2.4
```
Alias route: `POST /api/tts-chunk` (same body, same response).

### 2. Multi-speaker dialogue (sync)
```bash
curl -sS -m 300 -o dialogue.mp3 \
  -X POST http://blade-4090:9999/api/tts \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "sync",
    "turns": [
      {"voice": "cwon",  "text": "오빠 안녕. 멀티 보이스 테스트야."},
      {"voice": "elon",  "text": "Yes, this is the multi speaker test."}
    ]
  }'
```
⚠️ **Field name is `turns`, NOT `speakers`** (422 if you use `speakers`).

### 3. Async job (long text, fire-and-forget)
```bash
# Submit → returns 202 with job_id + URLs
curl -sS -X POST http://blade-4090:9999/api/tts \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "async",
    "turns": [{"voice":"chaewon","text":"긴 텍스트 처리용 비동기 작업."}]
  }'
# {"job_id":"...uuid...","result_url":"/api/jobs/.../result","status_url":"/api/jobs/..."}

# Poll status (3s interval recommended)
curl -s http://blade-4090:9999/api/jobs/$JOB_ID
# {"status":"pending"} → "running" → "succeeded" / "failed"

# Fetch MP3 when succeeded
curl -sS -o async.mp3 http://blade-4090:9999/api/jobs/$JOB_ID/result
# 202 = still processing, 200 = ready, 404 = unknown job
```

### 4. STT (Korean transcription via Cohere proxy)
```bash
curl -sS -m 180 \
  -X POST http://blade-4090:9999/api/stt \
  -F "file=@input.mp3" \
  -F "language=ko"
# {"text":"비동기 작업도 정상 동작해.","task":"transcribe","language":"ko","duration":1.34}
```

### 5. Register new voice
```bash
curl -sS -X POST http://blade-4090:9999/api/new-voice \
  -F "voice_id=newvoice" \
  -F "reference_audio=@sample.mp3" \
  -F "reference_text=참조 텍스트 정확하게"
# (also accepts /api/voices same payload)
```

---

## API Reference

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness |
| GET | `/api/voices` | List all voices + aliases |
| GET | `/api/voices/{id}` | Voice metadata (alias-aware) |
| POST | `/api/voices` | Register new voice (multipart) |
| POST | `/api/new-voice` | Alias for above |
| POST | `/api/tts/chunk` | Single sync chunk → MP3 |
| POST | `/api/tts-chunk` | Alias |
| POST | `/api/tts` | Multi-turn, `mode: sync\|async` |
| GET | `/api/jobs/{id}` | Job status JSON |
| GET | `/api/jobs/{id}/result` | Job MP3 (202 if running, 200 if ready) |
| POST | `/api/stt` | Cohere STT proxy (multipart: file, language) |

### Job status lifecycle
```
pending → running → succeeded
                 ↘ failed (check .error field)
```

### Error codes
| Code | Meaning | Example |
|------|---------|---------|
| 400 | Validation error | `{"error":"text is empty"}` / `{"error":"missing voice_id"}` |
| 404 | Resource not found | `{"error":"job not found"}` |
| 422 | JSON deserialization | `missing field 'turns'` |
| 500 | Server error | `{"error":"voice 'X' not found in ..."}` |

---

## ⏱ Performance (RTX 4090 Laptop 16GB)

**Verified 2026-05-12 from live service:**

| Operation | Cold start | Warm |
|-----------|-----------|------|
| `/api/tts/chunk` short (~10 char) | ~48s (model load) | ~5-10s |
| `/api/tts/chunk` medium (~30 char) | – | ~25s |
| `/api/tts` sync 2 speakers (~60 char) | ~94s | ~50s |
| `/api/tts` async submit | <1s (202) | <1s |
| Async actual processing | – | ~50-60s/turn |
| `/api/stt` (Cohere upstream) | ~40s | ~5-10s |
| Model first-load | ~45s | once per service lifetime |

**Resource peak (during heavy TTS):**
- Memory peak: **27.8GB RSS** (host has 31GB total — tight!)
- VRAM: ~4.7GB / 16GB at idle, ~15GB during inference
- Service idle RAM: ~4-11MB (model unloaded between requests)

⚠️ **Don't run concurrent heavy TTS** — OOM risk. Service auto-restarts but loses queue.

---

## ⚠️ Long Text Handling (CRITICAL)

**Max ~500 chars per single chunk.** Beyond that → quality degrades + OOM risk.

### Strategy: chunker v2 + async submission + merge_smooth

```bash
# 1. Split text with chunker v2 (sentence-aware, tone-marker aware)
python3 ~/2lab.ai/soul/np1/data/docent-books/scripts/chunk_text.py \
  --file long_input.txt --max-chars 400 --min-chars 80 \
  > chunks.txt

# 2. Submit each chunk as async job, poll, collect MP3s
# (see batch-tts.sh — already updated to use HTTP API)

# 3. Merge with merge_smooth.py (random 0.4-0.8s silence + 30ms crossfade)
python3 ~/2lab.ai/soul/np1/data/docent-books/scripts/merge_smooth.py \
  chunk_001.mp3 chunk_002.mp3 chunk_003.mp3 \
  -o final.mp3 --silence-min 0.4 --silence-max 0.8 --fade-ms 30
```

### Split criteria

| Text length | Method |
|-------------|--------|
| ≤200 chars | `/api/tts/chunk` directly |
| 200-500 chars | chunker v2 → 2-3 chunks → multi-turn sync |
| 500+ chars | chunker v2 → async jobs in parallel → merge_smooth |
| Docent book / audiobook | `batch-tts.sh` (full pipeline) |

### chunker v2 features
- Sentence boundary detection (마침표+공백, `."`, 한국어 종결어미)
- Quote-aware (`"불가능은 없다."` never split mid-quote)
- Tone markers (`[warm tone]`) used as natural split points
- Auto-merge short chunks (<80 chars)
- 125 tests passing, avg 99.8/100

### merge_smooth.py requirements

❌ **NEVER use `ffmpeg -c copy concat`** — produces clicks/pops at chunk boundaries.
✅ **ALWAYS use merge_smooth.py** — re-encodes with crossfade + random silence.

---

## Inline Tags (Emotion Control)

Place tag **before** the text it affects. Tags embedded in `text` field of any TTS call.

```json
{"voice":"cwon","text":"안녕. [whispering] 이건 비밀이야. [pause] [excited] 그런데 있잖아!"}
```

| Tag | Effect |
|-----|--------|
| `[pause]` / `[long pause]` | Silence |
| `[sigh]` / `[gasp]` / `[exhale]` | Breathing |
| `[laughing]` / `[chuckling]` / `[giggle]` | Laughter |
| `[whispering]` / `[soft voice]` / `[low voice]` | Quiet |
| `[loud voice]` / `[shouting]` | Loud |
| `[excited]` / `[angry]` / `[sad]` | Emotion |
| `[emphasis]` | Stress next word |
| `[warm tone]` / `[gentle tone]` | Free-form style |

Free-form: `[speaking slowly, almost hesitant]`, `[playful and teasing]`, etc.

> ✅ **HTTP service handles brackets correctly.** The old shell-wrapper bracket bug is gone — no more "Voice not found" errors from `[pause]`.

---

## 🛠 Fallback: Direct Python (when service is down)

Only use this if `curl http://blade-4090:9999/health` fails.

```bash
cd ~/fish-speech && .venv/bin/python \
  ~/2lab.ai/skills/fish-audio/scripts/gpu-inference.py \
  --text '<|speaker:0|>YOUR TEXT' \
  --prompt-text "$(cat ~/2lab.ai/skills/fish-tts/voices/cwon/reference.txt)" \
  --prompt-audio ~/2lab.ai/skills/fish-tts/voices/cwon/reference.mp3 \
  --output /tmp/out.wav \
  --checkpoint-path checkpoints/s2-pro \
  --device cuda --temperature 0.7 --top-p 0.9 --seed 42 \
  --max-new-tokens 2048
```

Constraints (Python path):
- MUST `cd ~/fish-speech` (model uses relative checkpoint paths)
- Text prefix `<|speaker:0|>` required
- Output is WAV (44.1kHz mono) — convert: `ffmpeg -i out.wav -b:a 192k out.mp3`
- First run loads model (~45s)

---

## 🔧 Service Operations

### Status
```bash
systemctl --user status ai.2lab.soma-voice.main.service --no-pager
journalctl --user -u ai.2lab.soma-voice.main.service -n 50 --no-pager
```

### Restart (if OOM or stuck)
```bash
systemctl --user restart ai.2lab.soma-voice.main.service
# Wait ~5s, then re-test /health
```

### Deployment paths
```
/opt/soma-voice/main/                           ← deployed binary + voices
/opt/soma-voice/main/.local/bin/ffmpeg          ← project-local ffmpeg
/opt/soma-voice/main/.local/bin/ffprobe         ← project-local ffprobe
/opt/soma-voice/main/jobs/{job_id}/             ← async job artifacts
~/.config/systemd/user/ai.2lab.soma-voice.main.service
```

### Voice resolution order
Server searches voices in this order:
1. `/opt/soma-voice/main/voices/`
2. `/home/zhugehyuk/2lab.ai/skills/fish-tts/voices/`

To add a voice: drop into `~/2lab.ai/skills/fish-tts/voices/<name>/` (no service restart needed).

---

## 📂 File Structure

```
~/2lab.ai/skills/fish-tts/
├── SKILL.md                    ← this file
├── scripts/fish-tts.sh         ← legacy shell wrapper (deprecated, use HTTP)
├── voices/{cwon,elon,karina,iu,egirl}/
│   ├── reference.mp3
│   └── reference.txt
└── output/                     ← legacy local outputs

/opt/soma-voice/main/           ← live service deployment
├── target/release/soma-voice   ← compiled binary
├── voices/                     ← optional override voices
├── jobs/{job_id}/              ← async job artifacts (chunks + result.mp3)
└── .local/bin/{ffmpeg,ffprobe}

~/2lab.ai/soul/np1/data/docent-books/scripts/
├── batch-tts.sh                ← batch pipeline (split → async TTS → merge)
├── chunker.py                  ← text chunker v2 engine
├── chunk_text.py               ← CLI wrapper
├── merge_smooth.py             ← audio merger (re-encode + crossfade)
└── test_chunker.py             ← 125 tests
```

---

## 🧪 E2E Test Results (2026-05-12 verified)

| Test | Result | Notes |
|------|--------|-------|
| GET /health | ✅ 200 `{"status":"ok"}` | |
| GET /api/voices | ✅ 5 voices listed | cwon, egirl, elon, iu, karina |
| GET /api/voices/cown | ✅ resolves → cwon | alias works |
| GET /api/voices/chaewon | ✅ resolves → cwon | alias works |
| POST /api/tts/chunk (cold) | ✅ 200, 23KB, 0.94s audio | 48s elapsed (model load) |
| POST /api/tts sync 2-turn | ✅ 200, 140KB, 5.83s audio | 94s elapsed |
| POST /api/tts async submit | ✅ 202 + job_id + URLs | |
| Async polling lifecycle | ✅ pending → running → succeeded | ~90s total |
| GET /api/jobs/{id}/result | ✅ 200 MP3 / 202 if running | |
| POST /api/stt (round-trip) | ✅ Perfect transcription | Cohere upstream |
| POST /api/tts-chunk empty | ✅ 400 `{"error":"text is empty"}` | |
| POST /api/new-voice no field | ✅ 400 `{"error":"missing voice_id"}` | |
| Unknown voice | ✅ 500 with searched paths | |
| Bad job_id | ✅ 404 `{"error":"job not found"}` | |

---

## Dependencies

- **soma-voice (Rust)**: `/opt/soma-voice/main/target/release/soma-voice` (compiled)
- **Fish Speech S2 Pro**: `~/fish-speech/` (model + Python venv)
- **GPU wrapper**: `~/2lab.ai/skills/fish-audio/scripts/gpu-inference.py`
- **PyTorch**: 2.8.0+cu129
- **ffmpeg/ffprobe**: `/opt/soma-voice/main/.local/bin/` (service uses these)
- **Cohere STT**: External API (Korean ASR)
- **Python 3**: chunker.py, merge_smooth.py
