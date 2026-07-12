# cwon-text-cards — 텍스트 카드 영상 생성

1:1 정사각형 텍스트 카드 영상. 다크 배경 + 흰 텍스트 + 단어별 하이라이트. Fish TTS cwon 보이스 기본.

**Triggers:** "텍스트카드", "text card", "텍카", "카드 영상", "카드영상", "textcard", "글 영상", "텍스트 영상"

---

## ⚡ 사용법 (대표님이 이렇게 말하면 실행)

```
"텍스트카드 만들어줘 [주제]"
"이 내용으로 텍카 만들어줘"
"카드 영상 만들어줘 [주제]"
"이 드래프트로 텍스트카드 만들어줘"
```

### 예시

```
"텍스트카드 만들어줘 일론머스크 최근 뉴스"
→ 1. Claude가 스크립트 작성
→ 2. Fish TTS cwon으로 음성 생성
→ 3. Whisper로 단어별 타임스탬프
→ 4. Pillow로 프레임 렌더링
→ 5. ffmpeg로 1080x1080 영상 조립
→ 6. 텔레그램으로 전송

"이 텍스트로 텍카 만들어줘: AI가 세상을 바꾸고 있다..."
→ 직접 입력한 텍스트로 바로 영상 생성
```

---

## 파이프라인

```
Topic/Text ──► Script (Claude, 주제일 때만)
                  │
                  ▼
              Voice (Fish TTS cwon)
                  │
                  ▼
              Timestamps (Whisper CPU)
                  │
                  ▼
              Frames (Pillow, word-by-word)
                  │
                  ▼
              Assembly (ffmpeg → 1:1 MP4)
```

## CLI 직접 실행

```bash
# 드래프트 JSON 기반
cd ~/2lab.ai/skills/shorts && \
.venv/bin/python ~/2lab.ai/skills/cwon-text-cards/scripts/textcard.py \
  --draft ~/.verticals/drafts/123.json \
  --source "TECHCRUNCH.COM" \
  --tts fish --voice cwon \
  --output /tmp/textcard_output.mp4

# 직접 텍스트
cd ~/2lab.ai/skills/shorts && \
.venv/bin/python ~/2lab.ai/skills/cwon-text-cards/scripts/textcard.py \
  --text "Your script here." \
  --source "BLOOMBERG.COM" --title "Article Title" \
  --tts fish --voice cwon

# Edge TTS (무료, 빠름)
cd ~/2lab.ai/skills/shorts && \
.venv/bin/python ~/2lab.ai/skills/cwon-text-cards/scripts/textcard.py \
  --text "Your script here." \
  --tts edge --voice en-US-GuyNeural

# 커스텀 색상
--accent-color "#00D9FF"   # 시안
--accent-color "#FFD700"   # 골드
--accent-color "#C85050"   # 코랄 (기본)
--accent-color "#7B68EE"   # 퍼플
```

## 실행 전 주의

**반드시 `shorts` 스킬의 venv 사용:**
```bash
cd ~/2lab.ai/skills/shorts && .venv/bin/python ~/2lab.ai/skills/cwon-text-cards/scripts/textcard.py ...
```
shorts/.venv에 Pillow, whisper, edge-tts 등 의존성이 설치되어 있음.

## Flags

| Flag | Options | Default |
|------|---------|---------|
| `--draft` | 드래프트 JSON 경로 | - |
| `--text` | 직접 스크립트 텍스트 | - |
| `--source` | 출처 (상단 표시) | "" |
| `--title` | 제목 (출처 아래) | draft의 youtube_title |
| `--tts` | edge, fish | edge |
| `--voice` | cwon, iu, karina (fish) / en-US-GuyNeural (edge) | - |
| `--lang` | en, ko, ja 등 | en |
| `--accent-color` | 하이라이트 색상 hex | #C85050 |
| `--group-size` | 한 화면 단어 수 | 4 |
| `--output` / `-o` | 출력 경로 | ~/.verticals/media/textcard_latest.mp4 |
| `--music` | 배경 음악 경로 | none |

## 비주얼 스타일

- **포맷**: 1080×1080 (1:1 정사각형)
- **배경**: #0A0A0E (near-black)
- **텍스트**: 흰색 DejaVu Sans Bold 58px, 중앙 정렬
- **하이라이트**: 현재 단어 코랄(#C85050) 강조, 약간 크게
- **출처**: 상단 좌측 회색(#666666) 22px
- **제목**: 출처 아래 회색 20px

## 파일 구조

```
~/2lab.ai/skills/cwon-text-cards/
├── SKILL.md              ← 이 파일
└── scripts/
    └── textcard.py       ← 메인 생성기

# 의존하는 외부 리소스
~/2lab.ai/skills/shorts/.venv/          ← Python 의존성
~/2lab.ai/skills/fish-tts/voices/cwon/  ← 채원 보이스
~/fish-speech/                          ← Fish TTS 엔진
~/2lab.ai/soul/np1/data/docent-books/scripts/merge_smooth.py  ← 오디오 병합
```

## 워크플로우 (Claude가 자동으로 하는 것)

1. **주제만 받았을 때**: shorts 스킬로 `draft` 먼저 생성 → textcard.py에 전달
2. **텍스트를 받았을 때**: 바로 textcard.py `--text`로 실행
3. **드래프트 JSON 받았을 때**: textcard.py `--draft`로 실행
4. **결과물**: /tmp/textcard_*.mp4 → 텔레그램으로 전송

## TTS 옵션

| Provider | 특징 | 속도 | 비용 |
|----------|------|------|------|
| Fish TTS cwon | 채원 목소리, 자연스러움 | ~2분 | 무료 (GPU) |
| Edge TTS | MS 기본 목소리, 빠름 | ~5초 | 무료 |

기본: **Fish TTS cwon** (대표님이 "edge로" 하면 Edge TTS)
