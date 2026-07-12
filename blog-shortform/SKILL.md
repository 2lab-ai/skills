---
name: blog-shortform
description: 블로그 URL 1개를 받아 60초 9:16 숏폼 영상(mp4)을 자동 생성하는 파이프라인. 한국 블로그 4종(티스토리/네이버/벨로그/브런치)에서 본문·이미지를 추출하고, 2인 대화 대본을 만든 뒤 로컬 fish-tts(soma-voice HTTP)와 GPT Image 2(gpt-image-2)로 음성·이미지를 생성해 Remotion v4로 합성한다. "블로그 URL로 숏폼 만들어줘", "이 글로 릴스 영상 만들어줘", "blog to shortform", "blog-shortform", "blog-url-to-shortform" 같은 요청에서 발동한다.
---

# Blog URL → Shortform Video Skill (fish-tts 판)

블로그 글 URL 하나만 받아서 60초 짜리 세로 숏폼 영상(mp4)을 만들어주는 **오케스트레이션 스킬**.

> 원본 `blog-shotform-gen` 플러그인을 fork. **외부 API 키가 0개**:
> - ElevenLabs TTS → 로컬 fish-tts (`http://blade-4090:9999`)
> - OpenAI Images API → image-gen 스킬 (Codex/ChatGPT OAuth 세션)
>
> 한국어 클론 보이스 사용 가능 + 비용 0.

## 핵심 원칙

1. **사용자는 URL만 제공** — 본문·시나리오·대본·음성·이미지는 자동 생성
2. **3-Phase 점진 실행** — 무료 단계(대본)에서 사용자 승인 → 유료 단계(이미지) → 합성 단계(Remotion)
   - **fish-tts 는 로컬 GPU 라 비용 0** — 그래도 샘플 1개 확인 후 전체 호출 (Phase 2 체크포인트 유지)
3. **결정론적 산출물 경로** — `${BLOG_SHORTFORM_PROJECTS_DIR:-$HOME/blog-shortform-projects}/<YYYYMMDD-HHMM>_<slug>/`
4. **결정 호출 전 확인** — TTS 샘플 1개 + 이미지 샘플 1개 → 사용자 승인 후 전체 진행

## 입력

| 항목 | 필수 | 비고 |
|---|---|---|
| 블로그 URL | ✅ | 티스토리/네이버/벨로그/브런치 우선 |
| 톤 | ❌ | 기본: 친근한 한국어 구어체 |
| 화자 | ❌ | 기본: A=cwon(여, 채원) + B=elon(남, 한국어 클론) |
| 길이 | ❌ | 기본 60초 |

## 환경 변수 (`.env`)

**키 없이도 동작**. 옵션 값만 조정하고 싶을 때 `.env` 만들면 됨:

```
FISH_TTS_URL=http://blade-4090:9999
FISH_TTS_VOICE_A=cwon        # 화자 A (여성, 30대 리드)
FISH_TTS_VOICE_B=elon        # 화자 B (남성, 20대 리액션)
FISH_TTS_TIMEOUT=180

IMAGE_SIZE=1024x1536         # image-gen 스킬에 전달
IMAGE_QUALITY=high
```

API 키는 **하나도 필요 없음**:
- fish-tts: 로컬 GPU (`blade-4090`)
- 이미지: image-gen 스킬 → Codex OAuth 세션 (`codex login` 한 번이면 됨)

> 사용 가능한 voice 목록: `curl -s http://blade-4090:9999/api/voices`
> 기본 제공: `cwon`(alias `chaewon`,`cown`), `elon`, `karina`, `iu`, `egirl`

## 의존성

- **fish-tts 서비스**: `blade-4090` 의 `ai.2lab.soma-voice.main.service` (systemd user) 가 실행 중이어야 함
  - 헬스체크: `curl -s http://blade-4090:9999/health` → `{"status":"ok"}`
  - 켜기: `ssh blade-4090 systemctl --user start ai.2lab.soma-voice.main.service`
  - 자세한 사용법은 `~/2lab.ai/skills/fish-tts/SKILL.md`
- Python 3.10+ (3.14 검증됨) + `pip install requests beautifulsoup4`
  - `.env` 는 인라인 파서로 처리(`python-dotenv` 불필요)
  - OpenAI 는 SDK 대신 `requests` 로 REST 직접 호출
- ffmpeg + ffprobe (Phase 2 mp3 결합 / 길이 측정) — `brew install ffmpeg` / `apt install ffmpeg`
- Node.js v20 LTS 이상 (Phase 3 Remotion 빌드) — v25 에서도 동작

## Phase 1 — URL → 대본 (무료, 빠름)

### Step 1.1: URL 입력 받기
사용자가 URL 하나를 던지면 시작. 형식 검증(http/https 로 시작).

### Step 1.2: 본문 추출
```bash
python3 ~/2lab.ai/skills/blog-shortform/scripts/extract_blog.py "<URL>" \
    > <project_dir>/extracted.json
```
- stdout 이 JSON. 키 `{platform, url, title, body, body_images, char_count}`
- **반드시 프로젝트 디렉토리에 `extracted.json` 으로 저장** (Phase 2 Step 2.6 에서 본문 이미지 substitute 에 사용)
- 플랫폼 자동 감지: 도메인 매칭(`tistory.com`, `blog.naver.com`/`m.blog.naver.com`, `velog.io`, `brunch.co.kr`)
- 네이버는 iframe 재요청을 자동 처리
- 본문이 500자 미만이면 경고 메시지

### Step 1.3: 본문 요약 → 주제·핵심 포인트
Claude 가 직접 수행. 추출된 `title`/`body` 를 보고:
- **주제** (한 줄, 시청자 후크용)
- **핵심 포인트 3개** (각 1문장, 본론에서 다룰 내용)
- **반전/CTA 후보** (마지막 컷에 쓸 메시지)

### Step 1.4: 2인 대화 대본 생성
원본 플러그인은 `shortform-script-generator` 외부 스킬을 호출했지만, 이 fork 에서는 Claude 가 직접 다음 형식으로 대본을 작성한다:

- 총 길이: **60초**
- 컷 수: **10개**
- 화자 A: `cwon` (30대 여성, 자신감 있는 리드)
- 화자 B: `elon` (20대 후반 남성, 질문/리액션)
- 언어: **ko**, 친근한 구어체
- 각 컷 한국어 텍스트는 **25~30자** 안 (fish-tts 한국어 발화 속도 기준 컷당 약 6초)
- 컷 사이 0.15초 무음 가정, 총 발화 합계 약 55~58초

핵심 포인트 3개를 본론(컷 4~7)에 녹이고, 첫 컷은 스크롤 스토퍼, 마지막 컷은 CTA/반전.

### Step 1.5: 대본 → `captions_draft.json`

다음 스키마로 직접 저장:

```json
{
  "source": {"url": "...", "title": "..."},
  "spec": {"language": "ko", "totalSec": 60, "cuts": 10},
  "captions": [
    {"index": 1, "startSec": 0.0,  "endSec": 6.0,  "speaker": "A", "text": "..."},
    {"index": 2, "startSec": 6.15, "endSec": 12.0, "speaker": "B", "text": "..."}
  ]
}
```

위치: `~/blog-shortform-projects/<YYYYMMDD-HHMM>_<slug>/captions_draft.json` (또는 `$BLOG_SHORTFORM_PROJECTS_DIR` 로 지정한 경로). 디렉토리가 없으면 함께 생성.

### Step 1.6: 사용자 체크포인트
대본 표를 그대로 보여주고 다음 질문을 던짐:
- 첫 컷이 스크롤 스토퍼로 충분한지
- 톤이 적절한지
- 핵심 포인트가 잘 들어갔는지

수정 요청 시 해당 컷만 다시 작성. 승인되면 Phase 2 진입.

## Phase 2 — TTS + 이미지 (모두 비용 0)

`captions_draft.json` 을 입력으로 fish-tts + image-gen 을 호출해 `public/audio/voice.mp3` 와 `public/images/cut_NN.png` 를 채운다.

### Step 2.1: 환경 검증
- `curl -s http://blade-4090:9999/health` → `{"status":"ok"}` 확인
- `codex login status` → `Logged in using ChatGPT` 확인 (image-gen 용)
- `which ffmpeg && which ffprobe` 확인 (없으면 `apt install ffmpeg`)
- 하나라도 실패하면 사용자에게 안내하고 즉시 중단

### Step 2.2: TTS 샘플 확인
보이스 매핑이 의도와 맞는지 컷 1로 확인:
```bash
python3 ~/2lab.ai/skills/blog-shortform/scripts/tts_fish.py <project_dir> --cut 1
```
출력된 `public/audio/cuts/cut_01.mp3` 를 사용자에게 안내(파일 경로 + 재생 방법). 톤 OK 면 다음 단계.

> ⚠️ 콜드 스타트(모델 로드)는 ~48초, 워밍업 후 청크당 ~5~25초. fish-tts SKILL 문서 참조.

### Step 2.3: 전체 TTS 생성
```bash
python3 ~/2lab.ai/skills/blog-shortform/scripts/tts_fish.py <project_dir>
```
- 컷별 mp3 가 `public/audio/cuts/cut_NN.mp3` 로 저장
- 통합본 `public/audio/voice.mp3` 자동 결합 (ffmpeg `libmp3lame` 재인코딩 + 0.15s 무음)
  - **`-c copy` 사용 금지** — fish-tts 출력 MP3 의 청크 경계 클릭/팝 회피 (fish-tts SKILL 경고)

### Step 2.4: 타이밍 재계산
```bash
python3 ~/2lab.ai/skills/blog-shortform/scripts/recompute_timing.py <project_dir>
```
- `captions.json` 생성 (실측 startSec/endSec + audio 경로)
- 총 길이 60초 ±3초 안이면 그대로 진행
- 벗어나면 stderr 에 경고. 사용자에게 (a) 긴 컷 텍스트 축약 재생성 (b) Remotion duration 을 실측값으로 사용 중 택일을 제시

### Step 2.5: 이미지 샘플 확인
```bash
python3 ~/2lab.ai/skills/blog-shortform/scripts/gen_images.py <project_dir> --cut 1
```
- `public/images/cut_01.png` 생성. 스타일이 의도와 맞는지 사용자가 확인
- 캐릭터 일관성은 보장 못 함 — 스타일(색조·구도) 일관성만 확인

### Step 2.6: 전체 이미지 생성
```bash
python3 ~/2lab.ai/skills/blog-shortform/scripts/gen_images.py <project_dir> \
    --substitute 3,6,9 --blog-images <project_dir>/extracted.json
```
- 컷 3·6·9 는 블로그 본문 이미지로 대체 (다양성 + 캐릭터 일관성 부담 줄임)
- 나머지 컷은 gpt-image-2 신규 생성
- `--blog-images` 는 Phase 1 에서 저장해둔 `extracted.json` 또는 본문 이미지 URL 배열 JSON

### Step 2.7: Phase 2 산출물 점검
프로젝트 디렉토리에 다음이 모두 존재해야 함:
```
projects/<run>/
├── captions_draft.json      (Phase 1)
├── extracted.json           (Phase 1, body_images 포함)
├── captions.json            (Step 2.4)
└── public/
    ├── audio/
    │   ├── voice.mp3        (Step 2.3)
    │   └── cuts/cut_NN.mp3  (Step 2.3)
    └── images/cut_NN.png    (Step 2.6)
```

## Phase 3 — Remotion 합성 (느림, 무료)

`captions.json` + `public/audio/voice.mp3` + `public/images/cut_NN.png` 가 모두 준비됐다면 Remotion v4 프로젝트를 결정론적으로 생성해 mp4 로 렌더한다.

### Step 3.1: 스캐폴드
```bash
python3 ~/2lab.ai/skills/blog-shortform/scripts/scaffold_remotion.py <project_dir>
```
- 1080×1920 / 30fps / Composition id `BlogShortform`
- 생성되는 파일:
  - `package.json` (Remotion v4 + React 19 + TS5)
  - `tsconfig.json`, `remotion.config.ts`
  - `src/index.ts`, `src/Root.tsx`
  - `src/data/scenes.ts` (FPS·WIDTH·HEIGHT·TOTAL_SEC·VOICE_FILE)
  - `src/data/captions.ts` (Caption[] — startSec/endSec/text/speaker/image)
  - `src/components/SpeechCaption.tsx` (Pretendard fallback, 외곽선)
  - `src/compositions/BlogShortform.tsx` (KenBurnsImg + Audio + Sequence × N)
- 자산 누락 시 즉시 중단 (Phase 2 가 완료돼 있어야 함)

### Step 3.2: 의존성 설치
```bash
cd <project_dir>
npm install --prefer-offline --no-audit --no-fund
```
- 첫 실행은 ~470MB, 1~3분. 2회차부터는 npm 캐시 덕분에 수초 안에 끝남
- Node v20 LTS 이상

### Step 3.3: 렌더
```bash
npm run build
```
- `out/video.mp4` 생성. 45초 영상 기준 약 1분 (M-series Mac, RTX 4090 Linux 도 비슷)
- H.264 / AAC 48kHz / 1080×1920 / 30fps

### Step 3.4: 검증
```bash
ffprobe -v error -show_entries format=duration,size:stream=codec_name,width,height,r_frame_rate \
        -of default <project_dir>/out/video.mp4
```
- 길이가 `captions.json` 의 `totalSec` 와 ±0.1초 안인지
- 1080×1920, 30fps, h264/aac 모두 정상인지

### Step 3.5: 미리보기/수정 (선택)
```bash
npm run dev   # Remotion Studio (브라우저 GUI)
```
자막 타이밍 미세 조정이 필요하면 `src/data/captions.ts` 의 startSec/endSec 만 손보고 다시 `npm run build`.

## 사용자와의 대화 패턴

**사용자**: `https://example.tistory.com/blog-post 이 글로 숏폼 만들어줘`

**Claude 의 응답 흐름**:
1. URL 확인 + Phase 1 시작 안내
2. `extract_blog.py` 실행 → 제목·본문 글자수·본문 이미지 N 장 요약 + `extracted.json` 저장
3. 본문 요약 → 주제·핵심 포인트 3개 제시
4. Claude 가 직접 2인 대화 대본 작성 → 마크다운 표로 출력
5. **체크포인트 ①**: 대본 OK? 컷 수정 요청 있으면 해당 컷만 재작성 → `captions_draft.json` 저장
6. fish-tts 헬스 + `.env`(OPENAI_API_KEY) + ffmpeg/ffprobe 검증
7. `tts_fish.py --cut 1` → **체크포인트 ②** 음성 톤 OK? (`cwon`/`elon` 매핑 확인)
8. 전체 TTS → `recompute_timing.py` → 총 길이가 60초 ±3초 안인지 보고
9. `gen_images.py --cut 1` → **체크포인트 ③** 이미지 스타일 OK?
10. 전체 이미지 (`--skip-existing` 로 컷 1 재생성 회피, 필요시 `--substitute`)
11. `scaffold_remotion.py` → `npm install` → `npm run build` (필요 시 background)
12. ffprobe 로 최종 mp4 검증 후 절대 경로 보고

## 금지 사항

- fish-tts 와 image-gen 둘 다 비용 0 이지만, **사용자 톤/스타일 확인 전 전체 호출 금지** (Step 2.2 / 2.5 샘플 의무) — 명시적으로 "전체 자동 진행" 지시 있을 때만 스킵
- 타인 블로그 URL 이 입력되면 본문 이미지를 영상에 그대로 쓰지 않고 인용 표시를 권장
- 본문 추출 실패 시 빈 대본을 만들지 말고 즉시 중단하여 사용자에게 URL 을 재확인 요청
- Codex OAuth 만료 시 `codex exec --skip-git-repo-check '...'` 한 번으로 자동 refresh 시도, 그래도 안 되면 사용자에게 `codex login` 안내

## 트러블슈팅

| 증상 | 대응 |
|---|---|
| `extract_blog.py` 가 본문 500자 미만 반환 | 셀렉터가 안 맞은 것. `--debug` 옵션으로 raw HTML 확인 후 셀렉터 보강 |
| 네이버 블로그 추출 실패 | iframe URL 직접 입력 옵션: `python3 extract_blog.py --naver-postview "<PostView URL>"` |
| `tts_fish.py` 가 health 7번 에러로 종료 | blade-4090 의 systemd 서비스 다운. `ssh blade-4090 systemctl --user restart ai.2lab.soma-voice.main.service` |
| `tts_fish.py` 가 컷 하나에서 500 에러 (`voice 'X' not found`) | `.env` 의 `FISH_TTS_VOICE_A/B` 가 `/api/voices` 목록과 일치하는지 확인 |
| `tts_fish.py` 가 컷마다 ~30초 이상 걸림 | 콜드 스타트(모델 로드)일 가능성. 두 번째 컷부터는 빨라짐. 정 느리면 `FISH_TTS_TIMEOUT=300` 으로 늘리기 |
| 컷별 mp3 의 합이 60초 ±3초 밖 | (a) 긴 컷 텍스트 축약 후 `tts_fish.py --cut N` 재생성 (b) Remotion 총 길이를 `captions.json.totalSec` 로 사용 — 사용자 선택 |
| `gen_images.py` 가 `token_expired` 로 실패 | `codex exec --skip-git-repo-check 'pong'` 한 번 호출해 OAuth refresh, 그래도 안 되면 `codex login` 재로그인 |
| `cut_NN.mp3` 결합본에서 클릭/팝 들림 | `tts_fish.py` 가 `-c copy` 가 아닌 libmp3lame 재인코딩을 사용하는지 확인 (concat_mp3 함수 참조) |

## 원본 대비 변경점

| 항목 | 원본 (`blog-shotform-gen`) | 이 fork |
|---|---|---|
| TTS | ElevenLabs `eleven_multilingual_v2` (유료, API 키 필요) | fish-tts (`http://blade-4090:9999`, 로컬 GPU, 무료) |
| 화자 ID | `ELEVENLABS_VOICE_A/B` (영문/한국어 클론 voice id 발급) | `FISH_TTS_VOICE_A/B` (기본 `cwon`/`elon`) |
| 결합 방법 | `ffmpeg -c copy concat` | `ffmpeg libmp3lame` 재인코딩 (클릭 회피) |
| 이미지 생성 | OpenAI `/v1/images/generations` (유료, API 키 필요) | image-gen 스킬 위임 → Codex OAuth (구독 기반, 무료) |
| 대본 생성 | 외부 `shortform-script-generator` 스킬 호출 | Claude 가 SKILL.md 가이드로 직접 작성 |
| 의존 API 키 | ElevenLabs + OpenAI | **없음** |
| 한국어 클론 | ElevenLabs Voice Library 등록 필요 | `~/2lab.ai/skills/fish-tts/voices/` 에 reference.{mp3,txt} 만 있으면 추가 가능 |

## 출처

- 원본 플러그인: https://github.com/gaebalai/claudecode-to/tree/main/plugins/blog-shotform-gen
- fish-tts: `~/2lab.ai/skills/fish-tts/SKILL.md`
- soma-voice 서비스: `/opt/soma-voice/main/`
