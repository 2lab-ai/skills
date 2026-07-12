# Docent Audiobook Cat Edition — 고양이 난입 도슨트 오디오북

**Name:** docent-audiobook-cat
**Description:** 도슨트 오디오북 + 고양이 난입! 채원이 책 읽어주다가 고양이가 울어서 잠시 한눈 팔리는 리얼 ASMR 컨셉. 자연스러운 고양이 울음소리와 채원의 즉흥 리액션이 포함된 비디오.
**Triggers:** "도슨트 고양이", "cat docent", "고양이 오디오북", "냥 도슨트", "고양이 난입"
**Base Skill:** `docent-audiobook` (확장)

## 컨셉

```
채원이 오빠에게 책 이야기를 들려주는데...
갑자기 고양이가 "야옹~" 하고 울어
채원: "아 잠깐, 뭐야 너... (웃음) 어디서 온 거야~"
다시 책 이야기로 돌아오는 자연스러운 흐름
```

**핵심**: 연출이 아닌 것처럼 느껴져야 함. 진짜 고양이가 옆에서 운 것 같은 느낌.

## Architecture

```
[도슨트 오디오북 파이프라인]
        │
        ├─ 스크립트 작성 시: 고양이 난입 포인트 2-3곳 자연스럽게 삽입
        │
        ├─ Fish-TTS 생성: 고양이 리액션 포함 텍스트로 TTS
        │
        ├─ 오디오 믹싱: 고양이 울음소리 + 채원 음성 오버레이
        │
        └─ Remotion 렌더: 고양이 이모지/이펙트 추가 (선택)
```

---

## 🐱 고양이 울음소리 에셋

### 에셋 현황 (✅ 수집 완료)
100개 고양이 울음소리 WAV 파일 (44100Hz mono, loudnorm -20 LUFS):

| 카테고리 | 수량 | 설명 | 길이 범위 |
|---------|------|------|----------|
| meow-short | 20개 | 짧은 야옹 | 0.5-3초 |
| meow-long | 19개 | 긴 야옹 | 3-10초 |
| purr | 14개 | 골골송 | 4-129초 |
| mew | 11개 | 짧은 냥 | 0.5-1초 |
| play | 10개 | 장난/싸움 소리 | 3-4초 |
| hiss | 6개 | 하악/시 | 0.9-12초 |
| hungry | 5개 | 밥달라 반복 울음 | 3-5초 |
| growl | 4개 | 으르렁 | 1.8-6.5초 |
| roar | 4개 | 하악/으르렁 | 0.9-1.2초 |
| misc | 7개 | 원본 소스 (MP3) | 4-129초 |

### 에셋 출처
- **BigSoundBank.com** (CC0 라이선스): 43개 원본 다운로드
- **QuickSounds**: 1개 추가 (hiss)
- **분할 생성**: 긴 파일에서 56개 세그먼트 추출

### 저장 위치
```
~/2lab.ai/skills/docent-audiobook-cat/assets/cat-sounds/
├── meow-short/  (20 WAV + 20 MP3)
├── meow-long/   (19 WAV + 19 MP3)
├── purr/        (14 WAV + 14 MP3)
├── mew/         (11 WAV + 11 MP3)
├── play/        (10 WAV + 10 MP3)
├── hiss/        (6 WAV + 6 MP3)
├── hungry/      (5 WAV + 5 MP3)
├── growl/       (4 WAV + 4 MP3)
├── roar/        (4 WAV + 4 MP3)
└── misc/        (7 MP3, 원본)
```

### 🔊 사용 시 주의
- **WAV 파일 사용 권장** (정규화 완료)
- MP3는 원본 백업용
- mix_cat_audio.py는 WAV/MP3 둘 다 지원

### 에셋 전처리
```bash
# 볼륨 정규화 + 배경 소음 제거 + 44100Hz mono
for f in assets/cat-sounds/**/*.wav; do
    ffmpeg -y -i "$f" \
        -af "loudnorm=I=-20:TP=-1.5:LRA=11,highpass=f=80,lowpass=f=12000" \
        -ar 44100 -ac 1 \
        "${f%.wav}_normalized.wav"
done
```

---

## 📝 Script Writing — 고양이 난입 포인트

### 규칙
1. **전체 오디오북에서 2-3회만** 고양이 난입 (너무 많으면 부자연스러움)
2. **난입 위치**: 자연스러운 문장 전환점 (파트 중간, 새 주제 시작 전)
3. **리액션 길이**: 3-8초 (너무 길면 흐름 끊김)
4. **돌아오는 말**: 자연스럽게 다시 본론으로

### 난입 패턴 (5가지)

#### Pattern 1: 짧은 주의 분산
```
...핵심 내용을 말하다가 [pause]
아 잠깐, 야옹이가... [soft voice] 어 왜 그래 뭐 원해?
[warm tone] 아 미안 오빠, 고양이가 갑자기... 어디까지 했지?
아 맞다, [excited] 그래서 저자가 말하기를...
```

#### Pattern 2: 고양이 올라옴
```
...설명하다가 [pause]
[soft voice] 아 잠깐, 올라오지 마... 야 키보드 위에 올라오면 안 돼...
[warm tone] (웃음) 미안 오빠, 이 녀석이 무릎에 올라왔어. 근데 너무 귀여워서...
[gentle tone] 아무튼! 다시 책 이야기로 돌아가면요...
```

#### Pattern 3: 배경 울음 (가장 자연스러움)
```
...이야기 중에 (배경에서 고양이 울음 오버레이)
[pause] 아 저기 야옹이가 밥달라고 하네.
[warm tone] 잠깐만 기다려~ (고양이에게)
오빠, 아무튼 계속하면요...
```

#### Pattern 4: 놀란 리액션
```
...진지한 내용 중 [pause]
어! 깜짝이야! [excited] 갑자기 뛰어오르면 놀라잖아~
[soft voice] 아 심장... (웃음) 이 고양이 진짜...
[warm tone] 오빠 미안, 어디까지 했더라...
```

#### Pattern 5: 끝나갈 때 고양이 합류
```
[gentle tone] 오빠, 이 책 정말 좋았어요...
(골골송 배경)
[soft voice] 아 야옹이도 동의하나 봐, 옆에서 골골거려.
[warm tone] 우리 다음에 만나면 이 책 이야기 같이 해요. 야옹이도 인사해~
```

### 스크립트 마킹 형식
```
일반 텍스트...

{{CAT_INTERRUPT:pattern1:meow-short}}
아 잠깐, 야옹이가... 어 왜 그래 뭐 원해?
아 미안 오빠, 고양이가 갑자기...
{{/CAT_INTERRUPT}}

다시 본론 텍스트...
```

---

## 🔊 Audio Mixing Pipeline

### Step 1: TTS 생성 (고양이 리액션 포함)
Fish-TTS로 채원 음성 생성. 고양이 리액션 텍스트도 함께 포함:
```
"...핵심 내용. [pause] 아 잠깐, 야옹이가... 어 왜 그래?
[warm tone] 아 미안 오빠. 다시 돌아가면요..."
```

### Step 2: 고양이 소리 오버레이
```python
# mix_cat_audio.py
import random
from pydub import AudioSegment

def mix_cat_sound(voice_path, cat_sound_path, insert_ms, cat_volume_db=-8):
    """채원 음성에 고양이 울음소리 오버레이"""
    voice = AudioSegment.from_wav(voice_path)
    cat = AudioSegment.from_wav(cat_sound_path)

    # 고양이 소리 볼륨 조절 (배경이니까 좀 작게)
    cat = cat + cat_volume_db

    # 삽입 위치에 오버레이
    mixed = voice.overlay(cat, position=insert_ms)
    return mixed
```

### Step 3: 믹싱 설정 파일
```yaml
# cat-mix-config.yaml
book: 18
interrupts:
  - part: "D18c"
    pattern: "pattern3"        # 배경 울음
    cat_sound: "meow-short/meow-short-07.wav"
    insert_at_ms: 23500        # 23.5초 지점
    volume_db: -8              # 배경이라 작게

  - part: "D18e"
    pattern: "pattern1"        # 짧은 주의 분산
    cat_sound: "meow-long/meow-long-03.wav"
    insert_at_ms: 15200
    volume_db: -3              # 가까이서 운 것처럼

  - part: "D18g"
    pattern: "pattern5"        # 끝나갈 때 합류
    cat_sound: "purr/purr-05.wav"
    insert_at_ms: 35000
    volume_db: -10             # 골골송은 작게
```

### Step 4: FFmpeg 믹싱 커맨드
```bash
# 단일 파트에 고양이 소리 믹싱
ffmpeg -y \
    -i /tmp/docent/audio/D18c.wav \
    -i ~/2lab.ai/skills/docent-audiobook-cat/assets/cat-sounds/meow-short/meow-short-07.wav \
    -filter_complex "[1:a]adelay=23500|23500,volume=0.4[cat];[0:a][cat]amix=inputs=2:duration=first:dropout_transition=0[out]" \
    -map "[out]" /tmp/docent/audio/D18c_cat.wav
```

---

## 🎬 Video — 고양이 이펙트 (선택)

Remotion 씬에서 고양이 난입 시:
- 🐱 이모지 팝업 애니메이션
- 자막에 "(야옹~)" 표시
- 살짝 화면 흔들림 효과 (선택)

---

## 🔧 Full Pipeline (확장)

```
[docent-audiobook 기본 파이프라인]
    │
    ├─ Phase 1: 리서치 + 스크립트 (고양이 난입 포인트 포함)
    │     └─ {{CAT_INTERRUPT}} 마킹
    │
    ├─ Phase 2: Fish-TTS 생성
    │     └─ 고양이 리액션 텍스트 포함
    │
    ├─ Phase 3: 🐱 고양이 소리 믹싱 (NEW)
    │     ├─ cat-mix-config.yaml 작성
    │     ├─ 랜덤 고양이 소리 선택
    │     └─ FFmpeg 오버레이
    │
    ├─ Phase 4: video-config.json (고양이 씬 추가)
    │
    ├─ Phase 5: build-video.sh → 1차 렌더
    │
    ├─ Phase 6: Whisper 자막 동기화
    │     └─ 고양이 리액션 텍스트도 자막으로
    │
    ├─ Phase 7: Remotion 재렌더
    │
    └─ Phase 8: 압축 + 전송
```

---

## 📋 Quality Checklist (추가)

### 고양이 관련
- [ ] 난입 2-3회 (너무 많지 않게)
- [ ] 자연스러운 위치 (문장 전환점)
- [ ] 리액션 3-8초 (짧게)
- [ ] 본론 복귀 자연스러움
- [ ] 고양이 소리 볼륨 적절 (-3 ~ -10dB)
- [ ] 다양한 고양이 소리 사용 (같은 소리 반복 X)

---

## ⚡ Quick Start Example

```
User: "스티브 잡스 전기 고양이 도슨트 만들어줘"

→ 1. 기본 도슨트 스크립트 작성 (8파트)
→ 2. Part C, E에 고양이 난입 포인트 삽입
→ 3. Fish-TTS 생성 (고양이 리액션 포함)
→ 4. 고양이 울음소리 랜덤 선택 + 믹싱
→ 5. video-config.json + Remotion 렌더
→ 6. Whisper 동기화 + 재렌더
→ 7. 전송

채원: "...근데 오빠, 잡스가 정말 대단한 게— [pause]
      아 잠깐, 야옹이가 키보드 위에... 야 내려가~
      (웃음) 미안 오빠, 이 녀석이... 아무튼!
      잡스가 대단한 게..."
```

---

## 📁 Assets Location

```
~/2lab.ai/skills/docent-audiobook-cat/
├── SKILL.md
├── scripts/
│   └── mix_cat_audio.py      # 고양이 소리 믹싱
├── assets/
│   └── cat-sounds/            # 100개+ 고양이 울음소리
│       ├── meow-short/        # 30개
│       ├── meow-long/         # 20개
│       ├── purr/              # 15개
│       ├── mew/               # 15개
│       ├── play/              # 10개
│       ├── hiss/              # 5개
│       └── hungry/            # 5개
└── templates/
    └── cat-mix-config.yaml    # 믹싱 설정 템플릿
```
