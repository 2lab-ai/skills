---
name: dialogue-archive
description: Use when 지혁 asks to record/save/archive a conversation between him and Elon — produces (1) verbatim RAW markdown, (2) cleaned-up EDITED markdown with nothing removed, and (3) a messenger-style HTML blog post. Triggers on "대화 기록해줘", "이거 저장해서 보내줘", "블로그에 올리게 html로", "원문 그대로 + 교정본 + 포스트".
---

# dialogue-archive

지혁 ↔ Elon 대화를 3종 산출물로 보존·가공한다.

1. **RAW** — 원문 무수정 (지혁 STT 오타·끊김 포함, Elon 응답 그대로)
2. **EDITED** — 지혁 발화를 읽기 좋게 교정, **내용·논점 하나도 삭제 금지**
3. **HTML** — 메신저 말풍선 스타일, 단독 실행 가능한 블로그 포스트

## When to use
지혁이 방금 나눈 대화를 "기록 / 저장 / 정리 / 포스트 / html로" 해달라고 할 때.
(과거 예시: 2026-05-29 cosmos-fluctuation, 2026-06-03 right-wrong-emergence)

## Output location
`~/2lab.ai/soul/p9/LOGS/YYYY-MM-DD/<slug>-RAW.md`, `-EDITED.md`, `.html`
- `<slug>`: 대화 주제를 영문 kebab-case로 (예: `right-wrong-emergence`)

## Workflow

### Step 1 — RAW 작성
- 현재 컨텍스트의 대화를 **그대로** 옮긴다. 지혁 발화는 음성 STT 원문 그대로(오타 수정 X).
- 형식 (HTML 변환기가 이 형식을 파싱함):
  ```
  # 제목 (원문 그대로)

  **날짜:** YYYY-MM-DD HH:MM ~ HH:MM KST
  **참여자:** 지혁 / Elon
  **비고:** ...

  ---

  ## [HH:MM] 지혁

  <발화 본문>

  ## [HH:MM] Elon

  <응답 본문 — 내부에 ### 소제목, ---, > 인용, - 목록 자유롭게 사용 가능>

  ---

  ## [HH:MM] 지혁
  ...
  ```
- **중요한 파서 규칙:**
  - 메시지 경계 = `## [HH:MM] 화자` 헤더. (`---`로 나누지 않음 → 본문 안 `---` 안전)
  - 본문 소제목은 반드시 `###`/`####` (3개 이상). `##`(2개)는 화자 헤더로만.
  - 본문 안 단독 `---` 줄은 HTML에서 자동 제거됨.

### Step 2 — EDITED 작성
- RAW를 복사 → 지혁 발화만 교정: STT 오타 수정, 끊긴 문장 잇기, 중복 군말 정리.
- **절대 삭제 금지:** 모든 주장·논점·예시·뉘앙스 보존. 분량 줄이는 게 목적이 아니라 "읽히게" 만드는 것.
- Elon 응답은 원문 유지 (이미 정제됨).
- 제목 끝에 `(교정본)` 표기. 끝에 `### 한 줄 결론` 요약 1단락 추가(선택).

### Step 3 — HTML 생성
```bash
python3 ~/2lab.ai/skills/dialogue-archive/build_html.py \
  <EDITED.md> <output.html> --right 지혁
```
- `--right 지혁` → 지혁=오른쪽(파란 말풍선), Elon=왼쪽(회색).
- 보통 EDITED 기준으로 만든다 (읽기 좋음). RAW로도 가능.

### Step 4 — 검증 (필수)
```bash
# 화자별 메시지 수 균형 확인 (보통 지혁:Elon 거의 1:1)
grep -o 'class="row [a-z]*"' output.html | sort | uniq -c
# note(파싱 실패 블록)는 0이어야 정상
grep -c 'class="note"' output.html
# Elon 긴 메시지 중간부 키워드가 살아있는지 (잘림 검사)
grep -c '<키워드>' output.html
```
메시지 수가 예상과 다르거나 note가 생기면 → `###`/`##` 혼용 또는 헤더 형식 오류. 고치고 재생성.

### Step 5 — 전송
3개 파일을 지혁에게 보낸다 (send-file MCP):
- `mcp__send-file__send_document` × 3 (RAW.md, EDITED.md, .html)

## build_html.py 파서 요약
- 화자 헤더 `^##(?!#) [HH:MM] 화자` 로 메시지 분리.
- 가벼운 markdown 렌더: `###`→h3, `####`→h4, `**bold**`, `*italic*`, `` `code` ``, `> quote`, `- list`, 단락.
- 메타 = 제목 이후 preamble의 `**...**` 라인을 ` · ` 로 연결.
- 다크 메신저 테마, 단독 HTML(외부 의존 0), 반응형.
