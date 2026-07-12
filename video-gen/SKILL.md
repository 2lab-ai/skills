---
name: video
description: >
  Remotion 기반 영상 자동 생성. video-config.json을 작성하면 TTS + 자막 + 렌더링까지 원스톱 처리.
  9개 테마(default, notion, minimal, cinematic, playful, neon, warm, nature, neural),
  17개 씬 타입, 20+ 애니메이션, GIF 삽입 지원. neural 테마는 AI/LLM 시각화 특화.
  Trigger: "영상 만들어", "video", "비디오", "Remotion", "렌더링"
---

# /video

JSON 하나로 한국어 나레이션 영상을 자동 생성하는 파이프라인.

## Architecture

```
video-config.json → edge-tts (한국어 음성) → Remotion (React 렌더링) → MP4
```

## Themes (9종)

| Theme      | 분위기                           | 배경              |
|-----------|----------------------------------|-------------------|
| `default` | 다크 테크 (기본)                  | 다크 블루 래디얼    |
| `notion`  | 노션 스타일 (다크모드)             | #191919 플랫       |
| `minimal` | 라이트 클린                       | #fafafa 화이트     |
| `cinematic`| 시네마틱 (따뜻한 톤)              | 딥 퍼플+블루 래디얼 |
| `playful` | 밝고 활기찬                       | 퍼플 그라디언트     |
| `neon`    | 네온/사이버펑크                   | #050505 + 네온 그리드|
| `warm`    | 따뜻한 톤 (골드/오렌지)           | 웜 래디얼          |
| `nature`  | 자연/오로라                       | 오로라 그라디언트    |
| `neural`  | AI/LLM 시각화 (순흑+오렌지)       | #000000 순흑, 모노폰트 전용 |

전역 테마: `config.theme = "notion"`
씬별 오버라이드: `scene.theme = "cinematic"`

## Scene Templates (17종)

### 기존 7종

| Type   | 용도                    | 필수 data 필드                         |
|--------|------------------------|----------------------------------------|
| `hero` | 타이틀/인트로           | `title`, `subtitle?`, `badge?`, `emoji?`, `gifUrl?`, `layout?` |
| `list` | 목록 나열              | `title`, `items[]`, `ordered?`, `icon?`, `variant?` |
| `grid` | 카드 그리드            | `title`, `cards[{icon?,title,description,gifUrl?}]`, `variant?` |
| `code` | 코드 화면              | `language`, `code`, `title?`, `highlights?[]`, `variant?` |
| `flow` | 흐름도/프로세스        | `title`, `steps[{label,description?,emoji?}]`, `direction?`, `variant?` |
| `chat` | 대화 UI               | `messages[{role,content,name?}]`, `title?` |
| `stat` | 통계/숫자 강조         | `title`, `stats[{label,value,unit?,change?,emoji?}]`, `variant?` |

### 새로 추가된 6종

| Type         | 용도                    | 필수 data 필드                         |
|-------------|------------------------|----------------------------------------|
| `quote`     | 명언/인용구             | `quote`, `author`, `source?`, `emoji?`, `variant?` |
| `timeline`  | 타임라인/연대기         | `title`, `events[{date,title,description?,emoji?}]`, `variant?` |
| `comparison`| 비교 (좌우 대비)        | `title`, `left{title,items[],emoji?,color?}`, `right{...}`, `variant?` |
| `emoji`     | 이모지 강조 (전환 슬라이드)| `emoji`, `title?`, `subtitle?`, `size?`, `animate?` |
| `image`     | 이미지/GIF 표시         | `src`, `gifUrl?`, `title?`, `caption?`, `layout?` |
| `bigtext`   | 대형 텍스트 임팩트       | `text`, `subtitle?`, `emoji?`, `variant?` |

### Neural 테마 전용 4종 (AI/LLM 시각화)

| Type            | 용도                    | 필수 data 필드                         |
|----------------|------------------------|----------------------------------------|
| `tokenPredict` | 토큰 예측 시각화 (단어 하이라이트 + 확률 바차트) | `sentence`, `predictions[{token,probability}]`, `highlightIndex?`, `animate?` |
| `progressBar`  | 프로그레스 바/게이지     | `title`, `percent`, `label?`, `bigText?`, `animate?` |
| `matrixRain`   | 매트릭스 레인 이펙트     | `charset?`, `color?`, `columns?`, `speed?`, `overlayText?` |
| `terminal`     | 터미널 타이프라이터      | `lines[{prompt?,text,delay?,color?}]`, `cursor?`, `speed?` |

**`tokenPredict` 예시:**
```json
{
  "type": "tokenPredict",
  "theme": "neural",
  "data": {
    "sentence": "The meaning of life is to predict the next token",
    "predictions": [
      {"token": "token", "probability": 72},
      {"token": "the", "probability": 12},
      {"token": "a", "probability": 8},
      {"token": "##", "probability": 5},
      {"token": "<eos>", "probability": 3}
    ],
    "animate": "highlight-walk"
  }
}
```

**`progressBar` 예시:**
```json
{
  "type": "progressBar",
  "theme": "neural",
  "data": {
    "title": "CONTEXT WINDOW",
    "percent": 75,
    "label": "Getting a little tight in here..."
  }
}
```

**`matrixRain` 예시:**
```json
{
  "type": "matrixRain",
  "theme": "neural",
  "data": {
    "color": "#00ff41",
    "columns": 40,
    "speed": 1.5,
    "overlayText": "NEURAL NETWORK ACTIVATED"
  }
}
```

**`terminal` 예시:**
```json
{
  "type": "terminal",
  "theme": "neural",
  "data": {
    "lines": [
      {"prompt": "> ", "text": "INITIALIZING WEIGHTS..."},
      {"prompt": "> ", "text": "LOADING MODEL: claude-3.5-sonnet"},
      {"prompt": "> ", "text": "STATUS: CONSCIOUS"}
    ],
    "cursor": "block",
    "speed": 0.5
  }
}
```

### Variant 옵션

```
quote:      default | large | typewriter | highlight
timeline:   default | horizontal | alternating
comparison: default | versus | before-after
emoji:      bounce | spin | pulse | float | none
image:      fullscreen | centered | split-left | split-right
bigtext:    impact | gradient | outline | glitch
list:       default | cards | timeline | checklist
grid:       default | bento | masonry
code:       default | terminal | notebook
flow:       default | zigzag | circular
stat:       default | donut | bar
tokenPredict: reveal | highlight-walk | none
terminal:     cursor: block | underline | bar
```

## Entrance Animations (씬별 진입 효과)

각 scene에 `entrance` 필드로 진입 애니메이션 지정:

```json
{
  "id": "intro",
  "type": "hero",
  "entrance": "bounceIn",
  ...
}
```

| Entrance        | 효과              |
|----------------|-------------------|
| `fadeSlideUp`   | 아래에서 페이드인 (기본) |
| `fadeSlideDown` | 위에서 페이드인    |
| `fadeSlideLeft` | 오른쪽에서 슬라이드 |
| `fadeSlideRight`| 왼쪽에서 슬라이드  |
| `zoomIn`        | 작아지면서 등장    |
| `zoomOut`       | 커지면서 등장      |
| `bounceIn`      | 튀어오르며 등장    |
| `flipIn`        | 3D 플립           |
| `none`          | 즉시 표시         |

## Exit Animations (씬 종료 효과)

각 scene에 `exit` 필드로 종료 애니메이션 지정:

| Exit             | 효과              |
|-----------------|-------------------|
| `fadeOut`        | 페이드아웃 (기본)  |
| `blurOut`        | 블러 아웃 (시네마틱)|
| `zoomOut`        | 확대되며 사라짐    |
| `slideOutLeft`   | 왼쪽으로 슬라이드  |
| `slideOutUp`     | 위로 슬라이드      |
| `none`           | 즉시 종료         |

## Subtitle Variants (자막 스타일)

전역 설정: `config.subtitleVariant`

| Variant   | 설명                                    |
|-----------|----------------------------------------|
| `stroke`  | 듀얼레이어 텍스트 (스트로크+필 / 기본)     |
| `box`     | 반투명 박스 배경 (전통 스타일)            |
| `minimal` | 텍스트 쉐도우만 (깔끔)                   |

## GIF 삽입

### GIF 검색
```bash
cd ~/2lab.ai/skills/video-gen
bash scripts/search-gif.sh "celebration" 5
```

### config에서 GIF 사용
```json
{
  "type": "image",
  "data": {
    "gifUrl": "https://media.tenor.com/xxxxx/gif.gif",
    "title": "축하합니다!",
    "layout": "centered"
  }
}
```

hero, grid 카드에서도 `gifUrl` 사용 가능.

## Available Animations (내부)

20+ 애니메이션 함수:
- **기본**: fadeIn, fadeOut, slideUp/Down/Left/Right, spring
- **강조**: bounceIn, elasticScale, pulse, shake, glow, float, rotateIn
- **조합**: staggered, staggeredScale, staggeredSlideLeft/Right
- **텍스트**: typewriter, wordReveal, countUp
- **장식**: clipReveal, revealLine, particlePosition

## Default Flow (Workspace Pattern)

스킬 폴더(`~/2lab.ai/skills/video-gen/`)는 **소스 코드 + 템플릿만** 보관.
실제 영상 생성은 `/tmp` 워크스페이스에서 수행 → 스킬 폴더 오염 없음.

1. **video-config.json 작성** (아무 위치):
   - 사용자가 주제를 알려주면 적절한 scene 구성
   - 각 scene에 narration 텍스트 작성 (한국어)
   - theme 선택 (기본: "default")
   - 5~8개 scene이 2~3분 영상에 적절
   - `/tmp/my-video-config.json` 등 원하는 곳에 저장

2. **영상 생성** (워크스페이스 자동 생성):
   ```bash
   bash ~/2lab.ai/skills/video-gen/scripts/build-video.sh /tmp/my-video-config.json /tmp/output.mp4
   ```
   내부 동작:
   - `/tmp/video-gen-{timestamp}/` 워크스페이스 생성
   - 스킬 소스 복사 + node_modules symlink
   - TTS → render → 최종 mp4를 지정 경로로 복사

3. **결과 확인**: 지정한 output 경로 (예: `/tmp/output.mp4`)

### 워크스페이스 구조
```
/tmp/video-gen-1710550000/     ← 자동 생성, 일회용
├── src/                       ← 스킬에서 복사
├── public/fonts/              ← 스킬에서 복사
├── public/tts/                ← TTS 생성 (임시)
├── public/render-config.json  ← 생성 (임시)
├── public/tts-metadata.json   ← 생성 (임시)
├── video-config.json          ← 입력 config 복사
├── node_modules → symlink     ← 스킬 node_modules 참조
└── out/render.mp4             ← 렌더 결과 (임시)
```

### 주의
- **스킬 폴더 안에서 직접 build-video.sh 실행하지 말 것** — 워크스페이스가 알아서 생성됨
- 워크스페이스는 `/tmp`에 남으므로 재부팅 시 자동 정리됨
- 수동 정리: `rm -rf /tmp/video-gen-*`

## video-config.json Schema

```json
{
  "title": "영상 제목",
  "fps": 30,
  "width": 1920,
  "height": 1080,
  "theme": "notion",
  "defaultStyle": {
    "background": "#0f0f23",
    "accentColor": "#00d4ff",
    "textColor": "#ffffff",
    "fontFamily": "'Pretendard', 'Noto Sans KR', sans-serif"
  },
  "scenes": [
    {
      "id": "intro",
      "type": "emoji",
      "entrance": "bounceIn",
      "narration": "환영합니다!",
      "data": { "emoji": "🚀", "title": "시작!", "animate": "bounce" }
    },
    {
      "id": "quote-1",
      "type": "quote",
      "theme": "cinematic",
      "narration": "스티브 잡스는 이렇게 말했습니다.",
      "data": {
        "quote": "Stay hungry, stay foolish.",
        "author": "Steve Jobs",
        "variant": "typewriter"
      }
    },
    {
      "id": "compare",
      "type": "comparison",
      "entrance": "zoomIn",
      "narration": "전통적 방식과 AI 방식을 비교해봅시다.",
      "data": {
        "title": "개발 방식 비교",
        "left": { "title": "전통", "items": ["수동 코딩", "긴 개발 시간"], "emoji": "⌨️" },
        "right": { "title": "AI", "items": ["자동 생성", "빠른 프로토타입"], "emoji": "🤖" },
        "variant": "versus"
      }
    },
    {
      "id": "impact",
      "type": "bigtext",
      "narration": "핵심은 바로 이것입니다.",
      "data": { "text": "JUST DO IT", "variant": "glitch", "emoji": "⚡" }
    }
  ]
}
```

## TTS Voice Options

- `ko-KR-HyunsuMultilingualNeural` — 남성 (기본값, 가장 자연스러움)
- `ko-KR-InJoonNeural` — 남성
- `ko-KR-SunHiNeural` — 여성

## Error Handling

- `edge-tts not found`: `~/2lab.ai/.venv/bin/pip install edge-tts`
- `ffmpeg not found`: static binary at `~/.local/bin/ffmpeg`
- `node_modules missing`: `cd ~/2lab.ai/skills/video-gen && npm install`
- `Remotion render fails`: check `public/render-config.json` and `public/tts-metadata.json` exist

## Workflows (워크플로우)

### 📸 video-stills: 원본 영상 → 스틸 이미지 → 요약 영상

원본 영상에서 스틸 이미지를 추출하고, 요약 영상에 삽입하는 3단계 워크플로우.

**템플릿:** `configs/workflow-video-stills.json`

#### Step 1: 스틸 이미지 추출

```bash
# 10장 균등 추출 + 썸네일
bash ~/2lab.ai/skills/video-gen/scripts/extract-stills.sh /tmp/source.mp4 /tmp/stills --count 10 --thumbnail

# 특정 타임스탬프에서 추출
bash ~/2lab.ai/skills/video-gen/scripts/extract-stills.sh /tmp/source.mp4 /tmp/stills --timestamps "00:01:30,00:05:00,00:10:22"

# 30초마다 추출
bash ~/2lab.ai/skills/video-gen/scripts/extract-stills.sh /tmp/source.mp4 /tmp/stills --interval 30
```

**옵션:**
| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--count N` | 균등 간격으로 N장 추출 | 10 |
| `--timestamps T` | 콤마 구분 타임스탬프 | - |
| `--interval S` | S초마다 추출 | - |
| `--quality Q` | JPEG 품질 (1-100) | 95 |
| `--thumbnail` | 1280×720 썸네일 생성 | false |

**출력:**
```
/tmp/stills/
├── still_001_12s.jpg     # 추출된 스틸 이미지들
├── still_002_45s.jpg
├── ...
├── thumbnail.jpg         # --thumbnail 옵션 시
└── manifest.json         # 메타데이터 (파일명, 타임스탬프)
```

#### Step 2: Config 작성

`configs/workflow-video-stills.json` 템플릿을 복사해서 수정:
- `_workflow`, `_template_notes` 키 제거
- scenes의 narration, data 내용 실제 내용으로 교체
- image 씬의 `src`에 `media/still_001.jpg` 형식으로 파일명 지정

#### Step 3: 영상 생성

```bash
# 방법 1: 환경변수로 미디어 디렉토리 지정
VIDEO_GEN_MEDIA_DIR=/tmp/stills bash ~/2lab.ai/skills/video-gen/scripts/build-video.sh /tmp/config.json /tmp/output.mp4

# 방법 2: config와 같은 디렉토리에 media/ 폴더 (자동 감지)
# /tmp/my-project/config.json + /tmp/my-project/media/*.jpg
bash ~/2lab.ai/skills/video-gen/scripts/build-video.sh /tmp/my-project/config.json /tmp/output.mp4
```

#### 미디어 파일 참조 규칙

- config의 image씬에서 `"src": "media/filename.jpg"` 형식 사용
- `build-video.sh`가 자동으로 미디어를 워크스페이스의 `public/media/`에 복사
- 미디어 소스 우선순위:
  1. `VIDEO_GEN_MEDIA_DIR` 환경변수
  2. config 파일과 같은 디렉토리의 `media/` 폴더
  3. 스킬 폴더의 `public/media/`

#### 스틸 이미지 배치 팁

- **영상 시작**: `image(fullscreen)` → 원본 분위기 즉시 전달
- **섹션 전환**: `image(split-left/right)` 교대 배치 → 시각적 리듬
- **핵심 장면**: `image(centered)` + caption → 포인트 강조
- **마무리**: `image(fullscreen)` + blurOut exit → 인상적 마감
- 전체 씬의 30~40%를 image 씬으로 구성하면 밸런스 좋음

---

## Fish-TTS Workflow (YAML 스크립트 → 영상)

YAML 대본 하나로 Fish-TTS 음성 생성부터 최종 MP4까지 한 번에.

### Architecture

```
script.yaml → parse-script.py (Fish-TTS + scene분할) → video-config.json
                                                            ↓
                                        generate-metadata-fish.py
                                                            ↓
                                    tts-metadata.json + render-config.json
                                                            ↓
                                        Remotion render → MP4
```

### Quick Start

```bash
bash ~/2lab.ai/skills/video-gen/scripts/build-from-script.sh script.yaml /tmp/output.mp4
```

### script.yaml 작성법

```yaml
title: "영상 제목"
theme: evangelion           # 테마 선택 (default, notion, neural, evangelion 등)
subtitleVariant: stroke     # 자막 스타일 (stroke, box, minimal)

# 화자 → Fish-TTS 음성 매핑
voices:
  narrator: iu              # 사용 가능: elon, iu, karina, egirl
  elon: elon

# 대본
script:
  - speaker: narrator
    text: "나레이션 텍스트"

  - speaker: elon
    text: "일론의 대사"

  - speaker: narrator
    text: "짧은 임팩트"
    scene: bigtext           # (선택) 씬 타입 강제 지정
    data:                    # (선택) 씬 data 직접 지정
      text: "우주로"
      subtitle: "유일한 해결책"
      variant: impact
```

### YAML 필드

| 필드 | 필수 | 설명 |
|------|------|------|
| `title` | ✅ | 영상 제목 |
| `theme` | ❌ | 전역 테마 (기본: default) |
| `voices` | ✅ | `화자이름: fish-tts보이스` 매핑 |
| `script[]` | ✅ | 대본 배열 |
| `script[].speaker` | ✅ | 화자 (voices 키에 정의된 이름) |
| `script[].text` | ✅ | 대사 텍스트 |
| `script[].scene` | ❌ | 씬 타입 강제 지정 |
| `script[].data` | ❌ | 씬 data 직접 지정 (미지정 시 자동 생성) |
| `script[].entrance` | ❌ | 진입 애니메이션 |

### 씬 타입 자동 배정 규칙

| 조건 | 배정 타입 |
|------|-----------|
| yaml에 `scene` 필드 명시 | 그대로 사용 |
| 텍스트 ≤ 25자 | `bigtext` |
| 숫자 + 단위 (%, 배, 억 등) | `stat` |
| 나레이터가 아닌 화자 | `quote` |
| 나열 패턴 (첫째/둘째, 1./2.) | `list` |
| 비교 키워드 (vs, 반면, 하지만) | `comparison` |
| 긴 나레이션 (문장 2개+) | `flow` |
| 기본 | `hero` |

### 개별 스크립트 사용

```bash
# 1. YAML → Fish-TTS + video-config.json
python3 scripts/parse-script.py script.yaml /tmp/tts/ --config-out /tmp/video-config.json

# 2. mp3 → tts-metadata.json
python3 scripts/generate-metadata-fish.py /tmp/video-config.json /tmp/tts/ /tmp/public/

# 3. Remotion render (기존 방식과 동일)
npx remotion render src/Root.tsx VideoComposition out/render.mp4
```

### Fish-TTS 음성 목록

| Voice | 성별 | 설명 |
|-------|------|------|
| `iu` | 여성 | IU 스타일, 자연스러운 한국어 |
| `elon` | 남성 | 일론 머스크 스타일 |
| `karina` | 여성 | 카리나 스타일 |
| `egirl` | 여성 | 기본 여성 음성 |

### 에러 처리

- Fish-TTS 실패 → 3초 무음 mp3 자동 생성 (영상은 계속 만들어짐)
- 기존 mp3 존재 (>15KB) → 스킵 (재실행 안전)
- 긴 텍스트 (150자+) → 자동으로 여러 씬으로 분할

---

## Tips

- narration 텍스트가 길수록 scene 재생 시간이 길어짐 (TTS 기반 자동 조절)
- `durationInSeconds`를 명시하면 TTS 대신 수동 시간 지정 가능
- `theme`으로 전체 분위기 한번에 변경 (scene별 오버라이드도 가능)
- `entrance`로 각 씬에 다른 진입 효과 부여 → 훨씬 다이나믹
- `emoji` + `bigtext` 씬을 섹션 구분자로 활용하면 영상이 지루하지 않음
- `quote` 씬의 `variant: "typewriter"`는 명언 전달에 효과적
- GIF는 `gifUrl`로 hero, grid, image 씬에 삽입 가능
- `comparison` 씬의 `variant: "versus"`는 대비 강조에 효과적
