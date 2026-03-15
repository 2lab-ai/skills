---
name: video
description: Remotion 기반 영상 자동 생성. video-config.json을 작성하면 TTS + 자막 + 렌더링까지 원스톱으로 처리한다.
---

# /video

JSON 하나로 한국어 나레이션 영상을 자동 생성하는 파이프라인.

## Architecture

```
video-config.json → edge-tts (한국어 음성) → Remotion (React 렌더링) → MP4
```

## Scene Templates

| Type   | 용도                    | 필수 data 필드                         |
|--------|------------------------|----------------------------------------|
| `hero` | 타이틀/인트로           | `title`, `subtitle?`, `badge?`         |
| `list` | 목록 나열              | `title`, `items[]`, `ordered?`         |
| `grid` | 카드 그리드            | `title`, `cards[{icon?,title,description}]` |
| `code` | 코드 화면              | `language`, `code`, `title?`, `highlights?[]` |
| `flow` | 흐름도/프로세스        | `title`, `steps[{label,description?}]`, `direction?` |
| `chat` | 대화 UI               | `messages[{role,content,name?}]`, `title?` |
| `stat` | 통계/숫자 강조         | `title`, `stats[{label,value,unit?,change?}]` |

## Default Flow

1. **video-config.json 생성**:
   - 사용자가 주제를 알려주면 적절한 scene 구성
   - 각 scene에 narration 텍스트 작성 (한국어)
   - 5~8개 scene이 2~3분 영상에 적절

2. **config 검증**:
   ```bash
   cd ~/2lab.ai/tools/video-gen
   npx tsx scripts/validate-config.ts video-config.json
   ```

3. **영상 생성** (전체 파이프라인):
   ```bash
   bash scripts/build-video.sh video-config.json out/video.mp4
   ```

   이 스크립트가 순서대로:
   - edge-tts로 scene별 MP3 생성
   - 자막 타임스탬프 추출 (SentenceBoundary)
   - Remotion으로 React → MP4 렌더링

4. **결과 확인**: `out/video.mp4`

## video-config.json Schema

```json
{
  "title": "영상 제목",
  "fps": 30,
  "width": 1920,
  "height": 1080,
  "defaultStyle": {
    "background": "#0f0f23",
    "accentColor": "#00d4ff",
    "textColor": "#ffffff",
    "fontFamily": "'Pretendard', 'Noto Sans KR', sans-serif"
  },
  "scenes": [
    {
      "id": "unique-scene-id",
      "type": "hero",
      "narration": "이 장면에서 읽을 한국어 나레이션 텍스트",
      "data": {
        "title": "메인 타이틀",
        "subtitle": "서브 타이틀"
      }
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
- `node_modules missing`: `cd ~/2lab.ai/tools/video-gen && npm install`
- `Remotion render fails`: check `public/render-config.json` and `public/tts-metadata.json` exist

## Tips

- narration 텍스트가 길수록 scene 재생 시간이 길어짐 (TTS 기반 자동 조절)
- `durationInSeconds`를 명시하면 TTS 대신 수동 시간 지정 가능
- `style.accentColor`로 scene별 색상 변경 가능
- `code` scene의 `highlights` 배열로 특정 줄 강조
- `stat` scene의 `value`가 숫자면 카운트업 애니메이션 적용

## Finish

- 생성된 파일: `out/video.mp4`
- TTS 캐시: `public/tts/` (재사용 가능)
- 메타데이터: `public/tts-metadata.json`
