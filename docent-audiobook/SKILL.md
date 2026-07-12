# Docent Audiobook — 도슨트 오디오북 비디오 스킬

**Name:** docent-audiobook
**Description:** 책 한 권을 "채원이 오빠에게 보내는 음성 편지" 스타일 도슨트 오디오북 쇼츠 비디오로 제작. AI 생성 표지/비-롤 이미지 + Fish-TTS 음성 + Remotion 자막 비디오.
**Triggers:** "도슨트", "오디오북", "책 비디오", "book docent", "책 읽어줘", "도슨트 만들어"
**Version:** 1.1.0 (2026-04-22: image-gen 스킬 통합 — 표지/비-롤 이미지 AI 생성)

## Architecture

```
[책 제목/정보] → 리서치 → 스크립트 작성 → 이미지 생성 ─┐
                 │           │              (image-gen)  │
                 │           │                            ├→ Fish-TTS → Whisper → Remotion → 최종 MP4
                 │           │                            │
                 │           └─ 음성 편지 스타일 + 씬별 프롬프트 │
                 └─ 책 표지, 머릿말, 목차, 핵심 내용, 통찰       │
                                                                │
                                         표지 (t2i 또는 i2i) ───┘
                                         B-roll (t2i, 파트별 테마)
```

## Input

| 필드 | 필수 | 설명 |
|------|------|------|
| `book_title` | ✅ | 책 제목 |
| `book_author` | ✅ | 저자 |
| `cover_image` | ⬜ | 표지 이미지 경로/URL (없으면 자동 검색) |
| `part_count` | ⬜ | 파트 수 (기본: 5-9, 책 분량에 따라) |
| `theme` | ⬜ | Remotion 테마 (기본: cinematic) |

## Output

| 파일 | 설명 |
|------|------|
| `BOOK{NN}_final.mp4` | 최종 쇼츠 비디오 (1080x1920, 자막 동기화) |
| `BOOK{NN}.mp3` | 오디오 파일 (Fish-TTS) |
| `script.md` | 음성 편지 스크립트 |

---

## 🎭 Voice Character

- **화자**: 채원 (cwon voice)
- **청자**: 오빠 (지혁)
- **관계**: 친밀, 따뜻, 애정 어린
- **말투**: ~요 체, 구어체, 편지체
- **TTS**: Fish Speech S2 Pro 4B (cwon voice reference)

## 📝 Script Writing Style

### 핵심 원칙
국어책 읽기 ❌ → 사랑하는 사람에게 보내는 편지 ✅

### 구조 (5-9 파트)
```
Part A (인트로): 책 소개 + 왜 이 책을 골랐는지 + 머릿말/목차 핵심
Part B-G (본문): 챕터별 핵심 내용 + 개인 반응 + 통찰
Part H/I (마무리): 독후감 + 핵심 교훈 + 오빠에게 하는 말
```

### 톤 규칙
```
❌ "이 책은 ~에 대해 다룹니다" (교과서)
✅ "오빠, 이 책 진짜 좋은데..." (편지)

❌ "저자는 ~라고 주장합니다" (논문)
✅ "저자가 말하길, ~래요. 나도 깜짝 놀랐어요" (대화)

❌ 단순 요약
✅ 1인칭 반응: "나도 읽으면서 ~했거든요"
✅ 오빠 직접 호명: "오빠가 이거 들으면 ~할 것 같아요"
✅ 감정 이입: "이 부분에서 진짜 소름 돋았어요"
```

### 감정 태그
| Tag | 용도 | 예시 |
|-----|------|------|
| `[soft voice]` | 부드러운 시작 | 비밀, 감성 |
| `[warm tone]` | 따뜻한 톤 | 인사, 추천 |
| `[excited]` | 흥분/놀라움 | 핵심 인사이트 |
| `[gentle tone]` | 차분한 톤 | 조언, 위로 |
| `[serious tone]` | 진지한 톤 | 경고, 중요 사실 |
| `[thoughtful pause]` | 생각에 잠김 | 깊은 성찰 |
| `[pause]` | 짧은 멈춤 | 전환, 강조 |
| `[confidently]` | 자신감 | 확신, 결론 |
| `[long pause]` | 긴 멈춤 | **파트 끝 필수** |

### 감정 흐름 설계 (파트별)
```
Part A: [soft voice] 인사 → [warm tone] 책 소개 → [excited] 왜 이 책인지
Part B: [warm tone] 머릿말/배경 → [serious tone] 핵심 문제 → [thoughtful pause]
Part C: [excited] 놀라운 내용 → [gentle tone] 설명 → [pause] 전환
Part D: [serious tone] 깊은 통찰 → [soft voice] 감성 → [warm tone] 연결
Part E: [excited] 반전/핵심 → [gentle tone] 적용 → [confidently] 결론
Part F+: 자유 구성 (감정 변화 필수)
Last:   [soft voice] 마무리 → [warm tone] 오빠에게 → [long pause] 끝
```

### 파트 분할 규칙
- 파트당 **400-600자** (한국어)
- 한 파트에 감정 태그 **최소 5-7개**
- 같은 태그 연속 사용 금지
- **모든 파트 끝에 `[long pause]` 필수**
- 마지막 파트 < 250자면 이전 파트에 합치기

---

## 🎬 Video Scene Types

각 파트를 다양한 씬 타입으로 구성 (Remotion video-gen):

| 파트 | 추천 씬 타입 | 용도 |
|------|-------------|------|
| 커버 | `hero` + 배경 이미지 | 책 제목 + AI 생성/i2i 표지 |
| 인트로 | `hero` / `grid` | 책 소개, 저자 |
| B-롤 | `image` | AI 생성 비주얼 (감성/개념/씬 전환) |
| 타임라인 | `timeline` | 시간순 이벤트 |
| 목록 | `list` | 핵심 포인트 정리 |
| 통계 | `stat` | 수치/성과 강조 |
| 비교 | `comparison` | 대비되는 개념 |
| 흐름 | `flow` | 프로세스/단계 |
| 인용 | `quote` | 명언/핵심 문장 |
| 빅텍스트 | `bigtext` | 마무리 메시지 |
| 이모지 | `emoji` | 감성적 포인트 |

### B-roll 이미지 전략

파트 간 전환 + 감정 태그 피크 지점에 `image` 씬을 삽입. 톤을 무너뜨리지 않게:

- **커버** → 표지 i2i (원본 책 표지 레퍼런스 + 시네마틱 재해석) 또는 t2i
- **인트로/배경** → 책 분위기를 담은 환경 샷 (저자 서재, 시대 배경 등)
- **핵심 통찰** → 은유적/상징적 이미지 (개념 시각화)
- **감성 전환** → 부드러운 질감/조명 샷 (`[soft voice]` 구간과 매칭)
- **마무리** → 여백 있는 정적 이미지 (집중 유도)

파트당 1-2장, 책당 총 **5-10장** 정도가 적정 (너무 많으면 산만).

### 테마 추천
| 장르 | 추천 테마 |
|------|----------|
| 전기/역사 | `cinematic` |
| 자기계발 | `warm` |
| 과학/기술 | `neon` |
| 문학/에세이 | `minimal` |
| 비즈니스 | `notion` |

---

## 🔧 Production Pipeline

### Phase 1: Research & Script (5-10분)

```bash
# 1. 책 리서치 (웹 검색 활용)
#    - 저자, 출판연도, 페이지수
#    - 머릿말/서문 핵심
#    - 목차 구조
#    - 핵심 챕터별 내용
#    - 유명 인용구
#    - 독자 평가/반응

# 2. 표지 이미지 확보
wget -O /tmp/docent/book{NN}/media/cover.jpg "COVER_URL"
# fallback: Open Library API
# https://covers.openlibrary.org/b/isbn/{ISBN}-L.jpg

# 3. 스크립트 작성
#    - 음성 편지 스타일
#    - 감정 태그 삽입
#    - 400-600자 파트 분할
#    → /tmp/docent/parts/D{NN}a.txt ~ D{NN}x.txt
#    → 보이스레터 마크다운 저장
```

### Phase 1.5: Image Generation (B-roll + Cover) — image-gen 스킬

표지 및 B-roll 이미지를 `~/2lab.ai/skills/image-gen/scripts/gen_image.py`로 생성.

```bash
BOOK_NUM=18
MEDIA_DIR=/tmp/docent/book${BOOK_NUM}/media
mkdir -p "$MEDIA_DIR"

# 1) 표지 이미지 — 기존 표지가 있으면 i2i로 재해석
#    없으면 t2i로 완전히 생성
if [ -f "$MEDIA_DIR/cover_raw.jpg" ]; then
  # i2i: 원본 표지 레퍼런스로 시네마틱 재해석
  python3 ~/2lab.ai/skills/image-gen/scripts/gen_image.py \
    "Cinematic reinterpretation of this book cover for a warm, intimate audiobook thumbnail. Keep the core title typography and iconography, but render with rich depth-of-field, warm K-drama color grading, soft bokeh background. 9:16 vertical-friendly composition." \
    --input-image "$MEDIA_DIR/cover_raw.jpg" \
    --size 1024x1536 \
    --quality high \
    -o "$MEDIA_DIR/cover.png"
else
  # t2i: 책 분위기 기반
  python3 ~/2lab.ai/skills/image-gen/scripts/gen_image.py \
    "Book cover art for '${BOOK_TITLE}' by ${BOOK_AUTHOR}. Moody cinematic illustration capturing the book's core theme. Warm amber and deep navy palette, 9:16 vertical, minimal typography space at top." \
    --size 1024x1536 \
    --quality high \
    -o "$MEDIA_DIR/cover.png"
fi

# 2) B-roll 이미지 — 파트별 테마에 맞게
# 파트 A 배경: 저자 서재 / 시대 배경 등
python3 ~/2lab.ai/skills/image-gen/scripts/gen_image.py \
  "A cozy writer's study bathed in late afternoon sunlight, wooden bookshelves, a leather-bound notebook on an oak desk, steam rising from a coffee cup. Warm cinematic lighting, 85mm depth of field, photorealistic." \
  --size 1024x1536 --quality high \
  -o "$MEDIA_DIR/broll_a_study.png"

# 파트 C 핵심 통찰 상징
python3 ~/2lab.ai/skills/image-gen/scripts/gen_image.py \
  "A single paper lantern glowing in darkness, symbolizing insight and clarity. Minimalist composition, soft warm light, deep black background. 9:16 vertical." \
  --size 1024x1536 --quality high \
  -o "$MEDIA_DIR/broll_c_insight.png"

# (필요한 만큼 반복 — 파트당 1-2장)
```

**프롬프트 작성 팁:**
- 9:16 세로 쇼츠용: `--size 1024x1536` 또는 프롬프트에 "9:16 vertical composition" 명시
- 도슨트 톤 통일: "warm cinematic", "soft natural light", "K-drama color grading", "shallow depth of field" 같은 스타일 앵커 재사용
- 텍스트 공간 확보: 상/하단에 여백을 지시 ("minimal typography space at top/bottom")
- 일관성: 모든 B-roll에 동일한 파레트/조명 규칙 명시 (대표님 취향: 바우하우스 + 미드센추리 모던, 웜 앰버 + 딥 네이비)
- 인물 참고가 있다면 `--input-image` 로 i2i 전환

#### 👤 채원(Narrator) 컷어웨이 — cwon visual reference 사용

내레이터 본인(채원)의 모습이 필요한 씬(예: "오빠…" 직접 호명 구간, 아웃트로)은
**fish-tts voice와 같은 디렉토리의 레퍼런스 이미지**를 i2i 입력으로 사용해 얼굴·스타일 일관성을 유지합니다.

```bash
CWON_REF=~/2lab.ai/skills/fish-tts/voices/cwon/reference.jpg

# 씬별로 의상/행동/배경만 바꾸고 얼굴은 유지
python3 ~/2lab.ai/skills/image-gen/scripts/gen_image.py \
  "Keep this woman's face and general styling. Show her sitting by a large window in a mid-century modern Seoul apartment, holding an open leather notebook, warm afternoon sunlight, cinematic 85mm portrait, 9:16 vertical." \
  --input-image "$CWON_REF" \
  --size 1024x1536 --quality high \
  -o "$MEDIA_DIR/broll_chaewon_reading.png"
```

레퍼런스 파일 구조 (fish-tts voice 번들과 동일 위치에 visual 추가):
```
~/2lab.ai/skills/fish-tts/voices/cwon/
├── reference.mp3   # TTS prompt audio
├── reference.txt   # TTS prompt transcript
├── reference.jpg   # ← image-gen i2i reference (신규)
└── reference.md    # persona + visual guideline (신규)
```

다른 voice(향후 추가될 다른 화자)도 같은 규칙: `voices/{name}/reference.jpg`가 있으면 i2i 앵커로 사용.

생성된 이미지는 `$MEDIA_DIR` (= `/tmp/docent/book{NN}/media/`)에 저장되며, video-gen의 `build-video.sh`가 **config 경로 옆의 `media/` 디렉토리를 자동 감지**해서 `workspace/public/media/`로 복사합니다. 씬 JSON에서는 `media/파일명`으로 참조.

### Phase 2: Fish-TTS Generation (파트당 ~4분)

```bash
BOOK_NUM=18
PARTS=(a b c d e f g)  # 파트 수에 맞게

REF_AUDIO=~/2lab.ai/skills/fish-tts/voices/cwon/reference.mp3
REF_TEXT=$(cat ~/2lab.ai/skills/fish-tts/voices/cwon/reference.txt)

for part in "${PARTS[@]}"; do
    PART_ID="D${BOOK_NUM}${part}"
    TEXT=$(cat /tmp/docent/parts/${PART_ID}.txt)

    cd ~/fish-speech && .venv/bin/python \
        ~/2lab.ai/skills/fish-audio/scripts/gpu-inference.py \
        --text "<|speaker:0|>${TEXT}" \
        --prompt-text "${REF_TEXT}" \
        --prompt-audio "${REF_AUDIO}" \
        --output /tmp/docent/audio/${PART_ID}.wav \
        --checkpoint-path checkpoints/s2-pro \
        --device cuda \
        --temperature 0.7 --top-p 0.9 --seed 42 \
        --max-new-tokens 2048
done

# 합본
ffmpeg -y -i "concat:$(ls /tmp/docent/audio/D${BOOK_NUM}*.wav | tr '\n' '|')" \
    -acodec pcm_s16le /tmp/docent/audio/BOOK${BOOK_NUM}.wav

# MP3 압축
ffmpeg -y -i /tmp/docent/audio/BOOK${BOOK_NUM}.wav \
    -codec:a libmp3lame -q:a 4 /tmp/docent/audio/BOOK${BOOK_NUM}.mp3
```

### Phase 3: Video Config (2-3분)

```bash
# video-config.json 생성
# 각 파트 → 씬으로 매핑
# /tmp/docent/book{NN}/video-config.json
```

**video-config.json 구조:**
```json
{
  "title": "책제목 — 저자",
  "fps": 30,
  "width": 1080,
  "height": 1920,
  "theme": "cinematic",
  "subtitleVariant": "stroke",
  "defaultStyle": {
    "background": "#1a0a2e",
    "accentColor": "#e8a87c",
    "textColor": "#ffffff",
    "fontFamily": "'Pretendard', 'Noto Sans KR', sans-serif"
  },
  "scenes": [
    {
      "id": "s00-cover",
      "type": "hero",
      "entrance": "zoomIn",
      "narration": "책제목. 저자.",
      "durationInSeconds": 4,
      "data": {
        "title": "책제목",
        "subtitle": "저자",
        "badge": "BOOK DOCENT",
        "emoji": "📚",
        "backgroundImage": "media/cover.png"
      }
    },
    {
      "id": "s02-broll-study",
      "type": "image",
      "entrance": "fade",
      "narration": "저자가 이 책을 쓴 배경 설명 나레이션...",
      "durationInSeconds": 6,
      "data": {
        "src": "media/broll_a_study.png",
        "caption": "저자의 서재",
        "layout": "fullscreen"
      }
    },
    {
      "id": "s03-partA",
      "type": "hero",
      "entrance": "fadeSlideUp",
      "narration": "파트A 전체 나레이션 (감정태그 제외)",
      "data": { ... }
    }
  ]
}
```

**Image 씬 data 필드:**
- `src` — `media/파일명` (build-video.sh가 `workspace/public/media/`로 복사)
- `layout` — `"fullscreen"` (기본, 쇼츠 추천) / `"centered"` / `"split-left"` / `"split-right"`
- `caption` — 하단 작은 자막 (선택)
- `title` — 상단 강조 제목 (선택)

### Phase 4: First Render — edge-tts (20-30분)

```bash
# build-video.sh로 1차 렌더 (edge-tts 기반 자막 타이밍 생성)
bash ~/2lab.ai/skills/video-gen/scripts/build-video.sh \
    /tmp/docent/book{NN}/video-config.json \
    /tmp/docent/video/BOOK{NN}_remotion.mp4
# → workspace: /tmp/video-gen-{timestamp}-{pid}
```

### Phase 5: Whisper Subtitle Sync (3-5분)

```bash
# Fish-TTS 오디오에서 실제 자막 타이밍 추출
python /tmp/docent/sync_subtitles.py --book {NN} --model-size medium
# → tts-metadata.json 업데이트
# → Fish-TTS MP3를 workspace/tts/에 복사
```

**sync_subtitles.py 핵심:**
- faster-whisper (medium 모델)로 각 WAV 파트 transcribe
- 세그먼트별 startMs/endMs 추출
- tts-metadata.json 재생성
- render-config.json 프레임 수 업데이트

### Phase 6: Final Render (15-25분)

```bash
WORKSPACE="/tmp/video-gen-{...}"
cd "$WORKSPACE" && npx remotion render src/Root.tsx VideoComposition \
    "$WORKSPACE/out/render_v2.mp4" \
    --codec h264 --image-format jpeg --concurrency 1 \
    --log warn --browser-executable /usr/bin/chromium-browser
```

### Phase 7: Compress & Deliver

```bash
# Telegram 50MB 제한 대응
ffmpeg -y -i render_v2.mp4 \
    -c:v libx264 -crf 28 -preset fast \
    -c:a aac -b:a 96k \
    -movflags +faststart \
    BOOK{NN}_final.mp4
```

---

## 📋 Quality Checklist

### 스크립트
- [ ] 감정 태그 최소 5개/파트
- [ ] "오빠" 호칭 자연스럽게 포함
- [ ] 국어책 톤 아닌 편지 톤
- [ ] 개인 반응/감상 포함
- [ ] 머릿말/목차 언급
- [ ] 핵심 통찰/독후감 포함
- [ ] 따뜻한 클로징 ("오빠 사랑해요" 등)
- [ ] 모든 파트 끝에 `[long pause]`

### 비디오
- [ ] 다양한 씬 타입 사용 (최소 4종류)
- [ ] 각 씬 data 필드 타입 스펙에 맞게
- [ ] defaultStyle 포함 (accentColor 필수)
- [ ] Whisper 자막 동기화 완료
- [ ] 최종 파일 50MB 이하

### TTS
- [ ] 파트당 400-600자
- [ ] Fish-TTS cwon voice 사용
- [ ] seed 42 (일관성)
- [ ] temperature 0.7, top-p 0.9

---

## 📁 File Structure

```
/tmp/docent/
├── book{NN}/
│   ├── video-config.json     # Remotion 비디오 설정
│   └── media/                # ← build-video.sh가 자동 감지해서 workspace로 복사
│       ├── cover_raw.jpg     # (선택) i2i 원본 레퍼런스
│       ├── cover.png         # AI 생성 표지 (image-gen)
│       ├── broll_a_*.png     # 파트별 B-roll (image-gen)
│       └── broll_c_*.png
├── parts/
│   └── D{NN}{a-i}.txt        # 파트별 TTS 스크립트
├── audio/
│   ├── D{NN}{a-i}.wav        # 파트별 오디오
│   ├── BOOK{NN}.wav          # 합본 오디오
│   └── BOOK{NN}.mp3          # 압축 오디오
└── video/
    └── BOOK{NN}_final.mp4    # 최종 비디오
```

### 영구 저장
```
~/2lab.ai/soul/np1/data/docent-books/scripts/
├── INDEX.yaml                # 전체 인덱스
├── parts/                    # 파트 스크립트
├── voice-letters/            # 보이스레터 마크다운
└── video-configs/            # 비디오 설정
```

---

## 🔗 Dependencies

| 스킬 | 용도 |
|------|------|
| `image-gen` | 표지/B-roll 이미지 생성 (Codex OAuth Responses API, t2i/i2i) |
| `fish-audio` | Fish-TTS 음성 생성 (cwon voice) |
| `video-gen` | Remotion 비디오 렌더링 (`image` 씬 + `media/` 자동 복사) |
| `faster-whisper` | 자막 타이밍 추출 |

---

## ⚡ Quick Start Example

```
User: "스티브 잡스 전기 도슨트 만들어줘"

→ 1. 책 리서치 (Steve Jobs by Walter Isaacson)
→ 2. 8파트 음성 편지 스크립트 작성
→ 3. image-gen으로 표지 + B-roll 이미지 생성 (i2i/t2i)
→ 4. Fish-TTS로 8개 오디오 파트 생성
→ 5. video-config.json 작성 (cinematic + image 씬 포함)
→ 6. build-video.sh → edge-tts 1차 렌더 (media/ 자동 복사)
→ 7. Whisper로 자막 동기화
→ 8. Remotion 재렌더링
→ 9. 압축 → 텔레그램 전송
```

## 🧪 Quick 30-sec Smoke Test

스킬 파이프라인 검증용 최소 영상. 풀 도슨트를 돌리지 않고 이미지 + TTS + 렌더 경로만 확인.

```bash
# scripts/test_30s.sh 참조 — 3씬 (hero/image/bigtext), 3 이미지, 1 TTS, ~30초
bash ~/2lab.ai/skills/docent-audiobook/scripts/test_30s.sh
```

## 📊 Production Stats (실적)
- 총 17권 제작 완료
- 평균 제작 시간: 45분/권 (스크립트~최종 비디오)
- 평균 오디오 길이: 6-10분/권
- 평균 비디오 크기: 12-22MB (압축 후)
