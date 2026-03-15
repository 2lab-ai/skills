---
name: video
description: >
  Remotion 기반 영상 자동 생성. video-config.json을 작성하면 TTS + 자막 + 렌더링까지 원스톱 처리.
  8개 테마(default, notion, minimal, cinematic, playful, neon, warm, nature),
  13개 씬 타입, 20+ 애니메이션, GIF 삽입 지원.
  Trigger: "영상 만들어", "video", "비디오", "Remotion", "렌더링"
---

# /video

JSON 하나로 한국어 나레이션 영상을 자동 생성하는 파이프라인.

## Architecture

```
video-config.json → edge-tts (한국어 음성) → Remotion (React 렌더링) → MP4
```

## Themes (8종)

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

전역 테마: `config.theme = "notion"`
씬별 오버라이드: `scene.theme = "cinematic"`

## Scene Templates (13종)

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

## Default Flow

1. **video-config.json 생성**:
   - 사용자가 주제를 알려주면 적절한 scene 구성
   - 각 scene에 narration 텍스트 작성 (한국어)
   - theme 선택 (기본: "default")
   - 5~8개 scene이 2~3분 영상에 적절

2. **영상 생성** (전체 파이프라인):
   ```bash
   cd ~/2lab.ai/skills/video-gen
   bash scripts/build-video.sh video-config.json out/video.mp4
   ```

3. **결과 확인**: `out/video.mp4`

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

## Tips

- narration 텍스트가 길수록 scene 재생 시간이 길어짐 (TTS 기반 자동 조절)
- `durationInSeconds`를 명시하면 TTS 대신 수동 시간 지정 가능
- `theme`으로 전체 분위기 한번에 변경 (scene별 오버라이드도 가능)
- `entrance`로 각 씬에 다른 진입 효과 부여 → 훨씬 다이나믹
- `emoji` + `bigtext` 씬을 섹션 구분자로 활용하면 영상이 지루하지 않음
- `quote` 씬의 `variant: "typewriter"`는 명언 전달에 효과적
- GIF는 `gifUrl`로 hero, grid, image 씬에 삽입 가능
- `comparison` 씬의 `variant: "versus"`는 대비 강조에 효과적
