# Fish Audio S2 — Voice Cloning TTS Skill

**Name:** fish-audio
**Description:** Fish Speech S2 Pro 기반 음성 클로닝 TTS. 소스 음성의 목소리로 타겟 텍스트를 읽어주는 음성 생성.
**Triggers:** "음성 클로닝", "voice clone", "목소리 복제", "TTS", "fish speech", "fish audio", "음성 생성"

## Architecture

```
[소스.wav + 소스.txt] → Fish Speech S2 Pro (4B) → [타겟.txt → 타겟.wav]
                         ↑
                   Reference voice        Target speech output
                   (10~30초 음성)          (클로닝된 음성)
```

## Requirements

- **Model:** fishaudio/s2-pro (4B params) — HuggingFace
- **Checkpoints:** `~/fish-speech/checkpoints/s2-pro/`
- **Python venv:** `~/fish-speech/.venv/`
- **GPU:** RTX 4090 Laptop 16GB VRAM (✅ 현재 설치됨)
- **RAM:** 32GB+ (CPU 폴백 시)

## Installation

```bash
# 1. Clone repo (이미 완료)
git clone https://github.com/fishaudio/fish-speech.git ~/fish-speech

# 2. Create venv & install
cd ~/fish-speech
python3.12 -m venv .venv
.venv/bin/pip install torch==2.8.0 torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cu129
.venv/bin/pip install -e .

# 3. Download model
.venv/bin/huggingface-cli download fishaudio/s2-pro --local-dir checkpoints/s2-pro
```

## Usage

### Quick (wrapper script)

```bash
# Voice cloning: source voice → target text → output wav
bash ~/2lab.ai/skills/fish-audio/scripts/voice-clone.sh \
  --source-audio /path/to/source.wav \
  --source-text "소스 음성의 텍스트 내용" \
  --target-text "타겟으로 생성할 텍스트" \
  --output /path/to/output.wav

# Options
  --device cuda|cuda         (default: cuda — RTX 4090 자동감지)
  --temperature 0.7         (default: 0.7, 낮을수록 안정적)
  --top-p 0.9              (default: 0.9)
  --seed 42                (default: 42, reproducibility)
```

### Direct CLI (fish-speech native)

```bash
cd ~/fish-speech

# 통합 명령 (audio → encode → generate → decode → wav)
.venv/bin/python fish_speech/models/text2semantic/inference.py \
  --text "<|speaker:0|>생성할 텍스트" \
  --prompt-text "소스 음성의 텍스트" \
  --prompt-audio /path/to/source.wav \
  --output /path/to/output.wav \
  --checkpoint-path checkpoints/s2-pro \
  --device cuda \
  --temperature 0.7 \
  --top-p 0.9 \
  --seed 42
```

### 3-Step Manual Pipeline

```bash
cd ~/fish-speech

# Step 1: 소스 음성 → VQ 토큰 추출
.venv/bin/python fish_speech/models/dac/inference.py \
  -i source.wav \
  -o source_codes.wav \
  --checkpoint-path checkpoints/s2-pro/codec.pth \
  --device cuda

# Step 2: 텍스트 → 시맨틱 토큰 생성 (소스 VQ 토큰 참조)
.venv/bin/python fish_speech/models/text2semantic/inference.py \
  --text "<|speaker:0|>타겟 텍스트" \
  --prompt-text "소스 텍스트" \
  --prompt-tokens source_codes.npy \
  --checkpoint-path checkpoints/s2-pro \
  --device cuda

# Step 3: 시맨틱 토큰 → 오디오 디코딩
.venv/bin/python fish_speech/models/dac/inference.py \
  -i output/codes_0.npy \
  -o output.wav \
  --checkpoint-path checkpoints/s2-pro/codec.pth \
  --device cuda
```

## Parameters

| Param | Default | Description |
|-------|---------|-------------|
| `--temperature` | 0.7 | 낮을수록 안정적, 높을수록 표현력 (0.1~1.5) |
| `--top-p` | 0.9 | 확률 임계값 (0.5~1.0) |
| `--top-k` | 30 | Top-K 샘플링 |
| `--seed` | 42 | 재현성을 위한 시드 |
| `--chunk-length` | 300 | 텍스트 청크 크기 (bytes) |
| `--max-new-tokens` | 0 | 최대 생성 토큰 (0=무제한) |
| `--half` | false | float16 사용 (bfloat16 미지원 GPU) |

## Speaker Tags

multi-speaker 생성 시 `<|speaker:N|>` 태그 사용:

```
<|speaker:0|>안녕하세요. 저는 첫 번째 화자입니다.
<|speaker:1|>네, 저는 두 번째 화자입니다.
```

## Inline Control Tags

```
[laugh]     웃음
[whisper]   속삭임
[breath]    숨소리
```

## Performance

| Device | Model Load | 1초 음성 생성 | 비고 |
|--------|-----------|-------------|------|
| **RTX 4090 Laptop 16GB** | **~31s** | **~2.3s** | **✅ 현재 서버 실측 (9.43 tok/s)** |
| H200 GPU | ~10s | ~0.2s | RTF 0.195 |
| A100 GPU | ~15s | ~0.5s | 최적 |
| CPU (32 core) | ~30s | ~3.5min | 실측: "안녕하세요" 1.0s = 210초 |

### CPU 모드 주의사항

1. **max_seq_len 필수 조정**: 기본 32768은 KV 캐시 할당에서 OOM/무한대기. Python API에서 `model.config.max_seq_len = 4096` 으로 줄여야 함
2. **코덱 인코딩 느림**: reference audio 인코딩만 ~10분 소요 (DAC 1.8GB 모델)
3. **토큰 생성**: ~1.1 tokens/sec (GPU 대비 ~500배 느림)
4. **권장**: 짧은 텍스트(1~2문장) 먼저 테스트, 긴 텍스트는 GPU 필수
5. **메모리**: 4B 모델 + 코덱 = ~12GB RAM 사용

## Tips

- 소스 음성은 **10~30초**가 최적 (너무 짧으면 품질 저하, 너무 길면 메모리 초과)
- 소스 텍스트는 음성 내용과 **정확히 일치**해야 최고 품질
- CPU 모드에서는 짧은 텍스트(1~2문장)부터 테스트 권장
- `--seed` 고정으로 동일 결과 재현 가능
- 한국어/영어/중국어/일본어 등 50개 언어 지원

## File Structure

```
~/2lab.ai/skills/fish-audio/
├── SKILL.md                      # 이 파일
├── scripts/
│   ├── voice-clone.sh            # 래퍼 스크립트
│   └── gpu-inference.py          # GPU 최적화 래퍼 (max_seq_len=4096 패치)
└── references/

~/fish-speech/                    # 소스 코드
├── checkpoints/s2-pro/           # 모델 가중치
├── fish_speech/                  # 패키지
│   └── models/
│       ├── dac/inference.py      # 코덱 (인코딩/디코딩)
│       └── text2semantic/inference.py  # 텍스트→음성 생성
└── .venv/                        # Python 환경
```

## Error Handling

- `CUDA out of memory`: `--device cpu` 사용 또는 텍스트 줄이기
- `Model not found`: `huggingface-cli download fishaudio/s2-pro --local-dir checkpoints/s2-pro`
- `pyaudio error`: inference에는 불필요, 무시 가능
- `bfloat16 not supported`: `--half` 플래그 추가
