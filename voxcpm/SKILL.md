# voxcpm — VoxCPM2 로컬 TTS (Voice Design + Cloning, 48kHz)

OpenBMB VoxCPM2 (2B, tokenizer-free diffusion-AR TTS, 30개 언어, 48kHz studio). 로컬 RTX 4090에서 직접 추론.
fish-tts(원격 HTTP 서비스)의 **로컬 대안/비교용** — 레퍼런스 오디오 없이도 자연어 설명만으로 목소리를 만들고(Voice Design), 짧은 샘플로 클로닝한다.

**Triggers:** "voxcpm", "voice design", "목소리 설계", "TTS 비교", "로컬 TTS", "voice clone"

---

## 🆚 fish-tts와의 차이 (언제 뭘 쓰나)

| | fish-tts | voxcpm |
|---|---|---|
| 형태 | 원격 HTTP 서비스 (`blade-4090:9999`) | 로컬 Python (`~/voxcpm-venv`) |
| 엔진 | Fish Speech S2 Pro (4B) | VoxCPM2 (2B, diffusion-AR) |
| 출력 | MP3 192k / 44.1kHz | WAV / **48kHz** |
| 레퍼런스 없이 생성 | ❌ (voice 등록 필요) | ✅ **Voice Design** (자연어 설명) |
| 클로닝 | reference.mp3+txt 등록 | reference_wav / prompt_wav+text |
| 언어 | 한국어 특화 | 30개 언어 |
| 권장 용도 | 등록된 캐릭터 음성 빠른 생성 | 새 목소리 설계 / 다국어 / 비교 |

둘 다 같은 GPU 계열(4090 16GB). **동시 heavy 추론은 OOM 위험** — 하나씩.

---

## 🚀 환경

- venv: `~/voxcpm-venv` (Python 3.12, torch 2.8+cu129) — fish-speech venv와 **격리**(오염 방지).
- 모델: `openbmb/VoxCPM2` (첫 실행 시 HF에서 자동 다운로드, 이후 캐시). 로컬 디렉토리 지정 시 `--local-dir`.
- 스크립트: `~/2lab.ai/skills/voxcpm/scripts/gen_voice.py`

```bash
# health: import 되는지
~/voxcpm-venv/bin/python -c "import voxcpm, soundfile; print('voxcpm ok')"
```

---

## 🔥 Quick Recipes

### 1. Plain TTS (기본 보이스)
```bash
~/voxcpm-venv/bin/python ~/2lab.ai/skills/voxcpm/scripts/gen_voice.py \
  "안녕하세요. VoxCPM2 한국어 음성 테스트입니다." \
  -o ~/2lab.ai/skills/voxcpm/output/plain.wav
```

### 2. Voice Design (레퍼런스 없이 자연어로 목소리 설계)
```bash
~/voxcpm-venv/bin/python ~/2lab.ai/skills/voxcpm/scripts/gen_voice.py \
  "오빠, 오늘 일정 정리해줄게." \
  --design "20대 여성, 따뜻하고 부드러운 목소리, 약간 미소" \
  -o ~/2lab.ai/skills/voxcpm/output/design_warm.wav
```
설명은 `text` 맨 앞에 `(설명)` 형태로 들어간다 (스크립트가 자동 처리).

### 3. Controllable Cloning (레퍼런스 + 스타일 제어)
```bash
~/voxcpm-venv/bin/python ~/2lab.ai/skills/voxcpm/scripts/gen_voice.py \
  "이건 클로닝된 목소리입니다." \
  --reference-wav /path/to/ref.wav \
  --control "조금 빠르게, 발랄하게" \
  -o ~/2lab.ai/skills/voxcpm/output/clone.wav
```

### 4. Ultimate Cloning (레퍼런스 + 정확한 transcript = 최고 유사도)
fish-tts voices를 그대로 재사용 가능:
```bash
V=cwon  # cwon|elon|iu|karina|egirl
~/voxcpm-venv/bin/python ~/2lab.ai/skills/voxcpm/scripts/gen_voice.py \
  "오빠 안녕. 보이스 클로닝 테스트야." \
  --prompt-wav  ~/2lab.ai/skills/fish-tts/voices/$V/reference.mp3 \
  --prompt-text "$(cat ~/2lab.ai/skills/fish-tts/voices/$V/reference.txt)" \
  -o ~/2lab.ai/skills/voxcpm/output/ultimate_$V.wav
```
> mp3 레퍼런스가 안 먹으면 먼저 wav로: `ffmpeg -i reference.mp3 -ar 16000 ref.wav`
> (VoxCPM2는 16kHz 레퍼런스 입력 → 48kHz 출력)

---

## 파라미터

| 플래그 | 기본 | 설명 |
|---|---|---|
| `text` (positional) | — | 합성할 텍스트 |
| `-o/--output` | out.wav | 출력 wav 경로 |
| `--design` | — | 레퍼런스 없는 보이스 디자인 설명 (괄호 prefix) |
| `--control` | — | 클로닝 시 스타일 제어 (속도/감정, 괄호 prefix) |
| `--reference-wav` | — | controllable cloning 레퍼런스 |
| `--prompt-wav` + `--prompt-text` | — | ultimate cloning (오디오+transcript) |
| `--cfg` | 2.0 | cfg_value (가이던스 강도) |
| `--timesteps` | 10 | inference_timesteps (높을수록 품질↑ 속도↓) |
| `--local-dir` | — | 미리 받은 모델 디렉토리 |

---

## 텔레그램 전송
```bash
# wav → mp3 (선택, 용량↓)
ffmpeg -i out.wav -b:a 192k out.mp3 -y
# mcp__send-file__send_document filePath=.../out.mp3
```
wav 직접 전송도 가능 (`send_document`, 50MB 이하).

---

## ⚠️ 주의 / 트러블슈팅

- **첫 실행 = 모델 다운로드(~수 GB) + 로드(~수십 초).** 이후 캐시. 매 호출마다 모델 재로드되니(스크립트가 1회 1프로세스), 여러 개 생성하면 배치로 묶는 게 효율적 (향후 확장).
- **OOM:** fish-speech 로컬 추론과 동시 실행 금지. 4090 16GB 공유.
- **mp3 레퍼런스 실패:** `ffmpeg -i x.mp3 -ar 16000 x.wav`로 변환 후 사용.
- **품질 낮음:** `--timesteps 20~30`, `--cfg 2.0~3.0` 조정.
- **한국어:** 언어 태그 불필요 (30개 언어 자동 감지).

---

## 한계 (정직)

- fish-tts처럼 HTTP 서비스/async/STT/멀티턴 대화 기능은 **없다** (단일 생성 스크립트).
- 매 호출 모델 재로드 = 배치 비효율. 대량이면 서비스화 필요(향후).
- diffusion-AR이라 fish-tts보다 생성이 느릴 수 있음 (실측은 첫 테스트 후 기록).

## Changelog
- **1.0.0** (2026-06-15): 초기 버전. gen_voice.py (plain/design/clone/ultimate) + fish-tts voices 재사용 ultimate cloning. fish-speech와 격리된 ~/voxcpm-venv.
