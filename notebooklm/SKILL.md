---
name: notebooklm
description: Drive Google NotebookLM from natural language — create notebooks, ingest sources, query, generate podcasts/reports/mindmaps/videos, download artifacts. Wraps notebooklm-mcp-cli (jacob-bd/notebooklm-mcp-cli).
triggers:
  ko: ["노트북엘엠", "노트북LM", "노트북lm", "NotebookLM", "팟캐스트 만들어", "스터디 가이드", "오디오 오버뷰", "마인드맵 만들어", "딥다이브"]
  en: ["notebooklm", "notebook lm", "deep dive podcast", "audio overview", "study guide", "mind map", "research mode"]
auth: cookie (Chromium browser, ~2-4 weeks)
when_to_use:
  - 사용자가 PDF/URL/유튜브 등 여러 자료를 모아 정리·요약·팟캐스트로 만들고 싶을 때
  - "이 자료들로 딥다이브 팟캐스트 만들어줘"
  - 시험/스터디 가이드, 마인드맵, 인포그래픽, 슬라이드, 비디오 오버뷰 생성
  - 노트북 내용에 대해 질의 (chat/query)
  - 여러 노트북에 동일 작업 배치(batch) 또는 노트북 간 통합 질의(cross)
---

# NotebookLM Skill

Google NotebookLM을 CLI/MCP로 조종한다. 인증은 한 번 `nlm login` 으로 쿠키 추출 후 ~2-4주 자동 갱신.

## TL;DR for me (Claude)

1. 사용자가 NotebookLM 작업을 요청하면 **먼저 `nlm auth status` 한 줄로 인증 체크**.
2. 인증 안 됐으면 → `nlm login` 안내 (브라우저 떠야 함, 사용자 액션 필요).
3. 작업은 가능하면 **MCP 도구** (`mcp__notebooklm-mcp__*`) 사용. MCP 미등록이면 **`nlm` CLI**로 폴백.
4. UUID는 길다 → 자주 쓰는 노트북은 **alias** 사용: `nlm alias set hal <uuid>`.
5. 생성 명령은 모두 `--confirm` 필요 (자동화용). 다운로드는 별도 단계.

## Install / Setup

```bash
bash ~/2lab.ai/skills/notebooklm/scripts/install.sh
# → Python ≥3.11 체크 → pipx 설치 → nlm/notebooklm-mcp PATH 확인 → 인증 체크 → Claude Code MCP 등록
```

수동 (한 줄):

```bash
pipx install notebooklm-mcp-cli && nlm login && claude mcp add --scope user notebooklm-mcp notebooklm-mcp
```

스모크 테스트:

```bash
bash ~/2lab.ai/skills/notebooklm/scripts/smoke.sh
```

## Authentication

```bash
nlm login                       # 기본 프로파일, 브라우저 열림
nlm login --profile work        # 멀티 계정
nlm login --manual --file cookies.json   # 쿠키 파일 직접 임포트 (WSL/headless)
nlm auth status                 # 현재 인증 상태
nlm auth list                   # 프로파일 목록
```

- 쿠키 수명 ~2-4주. 만료 시 `nlm login` 재실행.
- 모든 명령에 `--profile <name>` 으로 프로파일 전환 가능.
- WSL2면 `nlm login --wsl` (Windows Chrome 사용).

## Core Recipes

### R1. 새 노트북 + 자료 추가 + 질의

```bash
NB=$(nlm notebook create "Z13 Strix Halo 조사" --json | jq -r .id)
nlm alias set z13 $NB

nlm source add z13 --url "https://rog.asus.com/laptops/rog-flow/rog-flow-z13-2025/" --wait
nlm source add z13 --url "https://www.youtube.com/watch?v=..." --wait    # 유튜브 OK
nlm source add z13 --file ~/Downloads/strix-halo-whitepaper.pdf --wait
nlm source add z13 --text "내 메모: 128GB 통합메모리 핵심" --title "내 메모"

nlm notebook query z13 "Strix Halo의 통합 메모리가 LLM 추론에 주는 이점은?"
```

지원 파일: PDF, TXT, MD, DOCX, CSV, EPUB, MP3, M4A, WAV, AAC, OGG, OPUS, MP4, JPG, PNG, GIF, WEBP.

### R2. 딥다이브 팟캐스트 생성 + 다운로드

```bash
nlm audio create z13 --format deep_dive --length default --confirm
# format: deep_dive | brief | critique | debate
# length: short | default | long

# 폴링 (상태 확인)
nlm studio status z13                  # 모든 아티팩트 + 상태
# completed 로 바뀌면 ↓
nlm download audio z13 --output ~/podcasts/z13-deep-dive.mp3
```

특정 소스만 사용: `--source-ids <id1,id2>`
다국어: `--language ko` (BCP-47)

### R3. 학습 자료 풀세트 (퀴즈/플래시카드/마인드맵)

```bash
nlm quiz create z13 --count 10 --difficulty 3 --confirm
nlm flashcards create z13 --difficulty hard --confirm
nlm mindmap create z13 --title "Strix Halo Map" --confirm
nlm report create z13 --format "Study Guide" --confirm

nlm studio status z13                  # artifact id 확보
nlm download quiz z13 <artifact-id> --format html      # 인터랙티브 HTML
nlm download flashcards z13 <artifact-id> --format markdown
nlm download mind-map z13                              # 기본 텍스트
nlm download report z13 --output ~/study/z13-guide.md
```

### R4. 비주얼 (인포그래픽 / 슬라이드 / 비디오)

```bash
nlm infographic create z13 --orientation portrait --detail detailed --confirm
nlm slides create z13 --format detailed_deck --length default --confirm
nlm video create z13 --format explainer --style whiteboard --confirm
# styles: auto_select|classic|whiteboard|kawaii|anime|watercolor|retro_print|heritage|paper_craft

nlm download infographic z13
nlm download slide-deck z13 --format pptx
nlm download video z13
```

슬라이드 수정 (새 deck 생성됨, 원본 유지):

```bash
nlm slides revise <artifact-id> --slide '1 제목을 더 크게' --slide '3 이미지 제거' --confirm
```

### R5. 리서치 모드 (자동으로 소스 찾고 임포트)

```bash
nlm research start "Strix Halo vs Apple M4 Max for local LLM inference" \
    --notebook-id z13 --mode deep --auto-import
# mode: fast (~30s, ~10 sources) | deep (~5min, 40-80 sources)
# --auto-import: 완료 후 자동으로 소스 추가

nlm research status z13                # 폴링
nlm research import z13 <task-id> --cited-only  # 인용된 것만
```

### R6. 데이터 추출 (테이블)

```bash
nlm data-table create z13 "Compare RAM bandwidth, TDP, price across all sources" --confirm
nlm studio status z13
nlm download data-table z13 <artifact-id>     # CSV
nlm export to-sheets z13 <artifact-id>        # Google Sheets로 export
```

### R7. 배치 & 크로스 노트북

```bash
# 여러 노트북에 동일 질의
nlm batch query "Summarize key points" --notebook nb1,nb2,nb3

# 노트북 통합 질의 (합쳐서 답변)
nlm cross query "Common themes" --notebooks nb1,nb2,nb3
```

### R8. 채팅 (인터랙티브 REPL)

```bash
nlm chat start z13
# REPL 안에서:
#   /sources   - 소스 목록
#   /clear     - 대화 리셋
#   /help      - 도움말
#   /exit      - 종료
```

채팅 스타일 변경:

```bash
nlm chat configure z13 --goal learning_guide
nlm chat configure z13 --response-length longer     # longer | default | shorter
```

## Command Map (요약)

| 카테고리 | 명령 | 비고 |
|---|---|---|
| 인증 | `nlm login [--profile X]`, `nlm auth status` | 쿠키 ~2-4주 |
| 노트북 | `notebook list/create/get/describe/rename/delete/query` | `--json` 출력 가능 |
| 소스 | `source list/add/get/describe/content/rename/delete/stale/sync` | `--file`, `--url`, `--text`, `--drive`; `--wait` |
| 채팅 | `chat start <id>`, `chat configure` | REPL |
| 스튜디오 | `studio status/delete` | 아티팩트 상태 |
| 생성 | `audio/report/quiz/flashcards/mindmap/slides/infographic/video/data-table create` | 모두 `--confirm` 필요 |
| 다운로드 | `download audio/video/report/mind-map/slide-deck/infographic/data-table/quiz/flashcards` | quiz/flashcards: `--format json\|markdown\|html` |
| 익스포트 | `export to-docs <nb> <art>`, `export to-sheets <nb> <art>` | Reports → Docs, Tables → Sheets |
| 공유 | `share status/public/private/invite <email> [--role editor]` | |
| 리서치 | `research start/status/import` | fast / deep |
| 별칭 | `alias set/get/list/delete` | UUID 단축 |
| 배치/크로스 | `batch query/add-source/create/delete/studio`, `cross query` | 여러 노트북 |
| 진단 | `nlm doctor`, `nlm --ai` | doctor: 환경 검사; --ai: AI용 풀 가이드 |

## MCP Integration (Claude Code)

```bash
claude mcp add --scope user notebooklm-mcp notebooklm-mcp
# Claude Code 재시작 → mcp__notebooklm-mcp__* 도구 35개 노출
```

MCP 우선 사용 권장: stdio 트랜스포트, 인증은 CLI 인증과 공유 (`~/.notebooklm-mcp-cli/`).

HTTP 트랜스포트 (다른 도구에서 호출 시):

```bash
notebooklm-mcp --transport http --host 0.0.0.0 --port 8000
```

## Storage

```
~/.notebooklm-mcp-cli/
├── auth.json              # 쿠키, 토큰
├── config.toml            # 기본 프로파일, 언어 등
├── chrome-profile/        # Chrome 프로파일 (login 시)
└── profiles/
    ├── default/
    └── work/              # --profile work 사용 시
```

## Limitations & Gotchas

- **세션 ~20분**: 명령 안 쓰면 만료. 자동 복구 3-레이어 있어서 보통은 신경 안 써도 됨.
- **무료 일일 ~50회**: 생성 명령은 쿼터에 잘 걸림. Plus/Pro는 더 높음.
- **쿠키 만료 2-4주**: `nlm auth status` 실패 → `nlm login`.
- **생성은 비동기**: `create` 후 `studio status` 폴링 → `completed` 되면 `download`.
- **`--confirm` 필수**: 모든 create/delete에 명시. 자동화 시 빠뜨리면 prompt에 막힘.
- **WSL2 인증**: `nlm login --wsl` 또는 `--manual --file cookies.json`.
- **422 schema mismatch**: 일부 API 응답 변경에 민감 → CLI 업데이트 (`pipx upgrade notebooklm-mcp-cli`).
- **유튜브 transcription**: 자막 없는 영상은 add 시 실패.
- **rate limit 429**: 자동 재시도 3회 (지수 백오프). 그래도 실패 시 1분 후 재시도.

## Troubleshooting

| 증상 | 원인 | 처치 |
|---|---|---|
| `Authentication failed: Profile not found` | 한 번도 로그인 안 함 | `nlm login` |
| `Cookies have expired` | 쿠키 만료 | `nlm login` 재실행 |
| `429 Too Many Requests` | 일일 쿼터 | 1분 대기 후 재시도; Plus 업그레이드 고려 |
| WSL에서 Chrome 못 찾음 | WSL2 환경 | `nlm login --wsl` 또는 `--manual --file cookies.json` |
| 생성이 영원히 pending | 백엔드 처리 지연 | `studio status --full` 로 상태 확인; 5분 후 재시도 |
| `pipx` 없음 | 미설치 | `sudo apt install pipx && pipx ensurepath` |
| 명령 못 찾음 | PATH 누락 | `pipx ensurepath` + 셸 재시작 |

## Quick Cheat Sheet for Me

사용자가 "노트북엘엠으로 X 만들어줘" 라고 하면:

```
1. nlm auth status            → 인증 OK 확인
2. nlm notebook create "X"    → 새 노트북 (있으면 alias 사용)
3. nlm source add <id> ...    → 자료 추가 (--wait 권장)
4. nlm <kind> create <id> --confirm   → 생성 (audio/report/quiz/...)
5. nlm studio status <id>     → completed 대기
6. nlm download <kind> <id>   → 로컬 파일로
```

전체 사용 가능한 풀 가이드는 `nlm --ai` 로 언제든 조회 가능.
