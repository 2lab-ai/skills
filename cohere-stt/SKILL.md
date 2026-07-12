---
name: cohere-stt
description: Speech-to-Text using Cohere Transcribe (2B, Apache 2.0)
triggers:
  - 음성 인식
  - STT
  - 음성을 텍스트로
  - transcribe
  - speech to text
---

# Cohere STT - Speech-to-Text Skill

음성 파일을 텍스트로 변환하는 스킬. Cohere Transcribe (2B params) 모델 사용.
Open ASR Leaderboard 1위, 한국어 포함 14개 언어 지원.

## Quick Start

### Single File
```bash
bash ~/2lab.ai/skills/cohere-stt/scripts/cohere-stt.sh /path/to/audio.wav --language ko
```

### Multiple Files (Batch)
```bash
bash ~/2lab.ai/skills/cohere-stt/scripts/cohere-stt.sh file1.wav file2.mp3 file3.ogg --language ko --json
```

### JSON Output
```bash
bash ~/2lab.ai/skills/cohere-stt/scripts/cohere-stt.sh audio.wav --json --language ko
```

## Architecture

```
Audio File (WAV/MP3/OGG/FLAC)
  → Cohere Transcribe (2B Conformer + Transformer Decoder)
  → Text Output

Pipeline:
1. Audio → 16kHz mono resample (automatic)
2. Mel-spectrogram extraction
3. Conformer encoder (majority of 2B params)
4. Lightweight Transformer decoder → text tokens
```

## Parameters

| Flag | Default | Description |
|------|---------|-------------|
| `--language`, `-l` | `ko` | ISO 639-1 code: en,de,fr,it,es,pt,el,nl,pl,ar,vi,zh,ja,ko |
| `--device`, `-d` | `auto` | `auto`, `cuda:0`, `cpu` |
| `--batch-size`, `-b` | `16` | GPU batch size |
| `--compile` | off | torch.compile for faster throughput (warmup cost) |
| `--no-punctuation` | off | Remove punctuation from output |
| `--json`, `-j` | off | Output as JSON with stats |
| `--output`, `-o` | stdout | Save to file |

## Supported Languages (14)

| Code | Language | Code | Language |
|------|----------|------|----------|
| en | English | el | Greek |
| de | German | nl | Dutch |
| fr | French | pl | Polish |
| it | Italian | ar | Arabic |
| es | Spanish | vi | Vietnamese |
| pt | Portuguese | zh | Chinese |
| ja | Japanese | **ko** | **Korean** |

## API Server (for soma integration)

```bash
# Start API server (OpenAI Whisper-compatible endpoint)
~/.cohere-stt-venv/bin/python ~/2lab.ai/skills/cohere-stt/scripts/transcribe_api.py --port 8787

# Test
curl -X POST http://localhost:8787/v1/audio/transcriptions \
  -F "file=@audio.ogg" \
  -F "language=ko"
```

## Benchmark

```bash
# Run full benchmark (generate 100 TTS samples + transcribe + evaluate)
~/.cohere-stt-venv/bin/python ~/2lab.ai/skills/cohere-stt/scripts/benchmark.py --all

# Individual steps
~/.cohere-stt-venv/bin/python ~/2lab.ai/skills/cohere-stt/scripts/benchmark.py --generate
~/.cohere-stt-venv/bin/python ~/2lab.ai/skills/cohere-stt/scripts/benchmark.py --transcribe
~/.cohere-stt-venv/bin/python ~/2lab.ai/skills/cohere-stt/scripts/benchmark.py --evaluate
```

## Performance

- **WER**: 5.42 avg on Open ASR Leaderboard (English)
- **Speed**: RTFx up to 3x (3 seconds of audio processed in 1 second)
- **Model Load**: ~10-15s on RTX 4090
- **Memory**: ~6-8GB VRAM (2B params, fp32)
- **Long audio**: Auto-chunked at 35s segments with overlap

## Constraints & Gotchas

1. **No auto language detection** — must specify `--language`
2. **Single language per call** — no code-switching support
3. **Eager transcription** — transcribes non-speech sounds (use VAD pre-filter for noisy audio)
4. **No timestamps** — output is plain text only (no word-level timing)
5. **No speaker diarization** — single-speaker transcription
6. **First `--compile` call is slow** — subsequent calls benefit from torch.compile cache
7. **GPU memory** — ~6-8GB VRAM required; reduce batch_size if OOM

## File Structure

```
cohere-stt/
├── SKILL.md                    # This file
├── scripts/
│   ├── cohere-stt.sh           # Shell wrapper (entry point)
│   ├── inference.py            # Main inference script
│   ├── transcribe_api.py       # HTTP API server (OpenAI-compatible)
│   └── benchmark.py            # TTS→STT benchmark tool
├── examples/                   # Example audio files
└── output/                     # Benchmark results
    ├── benchmark/              # Generated TTS samples
    ├── benchmark_samples.json  # Sample metadata
    └── benchmark_results.json  # Evaluation results
```

## Dependencies

- **Python venv**: `~/.cohere-stt-venv/`
- **Model**: `CohereLabs/cohere-transcribe-03-2026` (auto-downloaded from HuggingFace)
- **Packages**: transformers>=4.56, torch, huggingface_hub, soundfile, librosa, sentencepiece, protobuf
- **GPU**: NVIDIA GPU with CUDA (RTX 4090 Laptop tested)
- **License**: Apache 2.0

## Model Card

- **Publisher**: Cohere Labs
- **Release**: March 26, 2026
- **Parameters**: 2B
- **Architecture**: Conformer encoder + Transformer decoder
- **Training Data**: 500K hours curated audio-transcript pairs
- **HuggingFace**: https://huggingface.co/CohereLabs/cohere-transcribe-03-2026
