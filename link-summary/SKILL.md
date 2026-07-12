# link-summary — SNS 링크 딥 요약 + 음성 브리핑

X(Twitter)/Threads 링크를 받으면 전체 스레드를 스크래핑하고, 번역/분석/음성 브리핑까지 원스톱으로 처리.

**Triggers:** X/Twitter URL, Threads URL, 일반 웹 링크, "link-summary", "링크 요약"

---

## 📋 LinkSummary 출력 6요소 (지혁 사양, 2026-05-18)

**모든 archive는 이 6개 요소를 출력한다. 게이트 통과 항목만.**

| # | 요소 | 위치 | 게이트 |
|---|---|---|---|
| 1 | **TL;DR** | `### 3.1` | 항상 1줄 |
| 2 | **Executive summary 계층적** (high→low) | `### 3.2 → 3.3 → 3.4` | G1 compact면 3.4 SKIP |
| 3 | **원본 보존** (verbatim) | `## 1. 원문` | 항상 무손실 |
| 4 | **번역** (원문 한국어 아닐 때만) | `## 2. 번역` | 한국어 원문 → 생략 |
| 5 | **팩트체크** | `### 3.5` | compact면 ≤3항목 |
| 6 | **함의 + 심층 분석 v3** | `### 3.7 → 3.8 글A → 3.9 글B` | G4 (3.7) + G8 (3.8/3.9 게이트) |

**6요소가 없으면 archive 아님.** 1~5는 항상 시도, 6번 v3 글A/B는 G8 통과 시만.

---

## 🚨🚨🚨 HARD GATES (2026-05-17 셀프 리플렉션 + Codex 리뷰 머지)

이전에 "강제 연결 X / max 1 lens" 같은 추상 원칙은 **모두 무시되었다**. 1주일 67개 archive에서 행동 변화 0. 그래서 **기계로 검사 가능한 게이트 7개**로 대체한다.

**G1. MODE 자동 결정 (Phase 2.5)** — `Repeat_7d >= 2` 또는 24h 내 동일 작자+동일 CTA/레포 재포스트 → 자동 `Mode: compact`. 풀-archive 생성 금지.

**G2. Front matter 필수 필드** — `Platform / Repeat_7d / Mode / Actionability / Next_Action` 5개 누락 시 작업 실패.

**G3. 3.6 비판 게이트** — 최대 2개 불릿. 각 불릿은 **원문 verbatim 인용 1개 또는 수치/링크 1개** 필수. 4-슬롯(engagement/authority/overclaim/cherry-pick) 자동 채우기 금지. 적용되는 것만.

**G4. 3.7 함의 게이트** — 최대 2개 불릿, 각 1문장. 직접 액션 없으면 `- 직접 적용 인사이트 없음` **단 1줄**로 종료. Context Rot Week chain 연결은 0 또는 1개만.

**G5. 접근 실패 Stop-rule** — 403 / login wall / robots block 등 1차 스크래핑 실패 시: 분석/맥락 확장 금지. front matter `Verification: ACCESS_FAILED` 명시 + 가공 섹션 SKIP (3.1 TL;DR 1줄 + 3.5에 실패 사유만).

**G6. Korean creator tone — 증거 기반 판정** — 한국 Threads/LinkedIn의 캐주얼 톤(예: "팝콘 먹으면서", "썰 풀어볼게")은 **자동 engagement bait 감점 금지**. 명백한 CTA / 구매 유도 / data inflation에만 적용. 감점 시 원문 인용 강제 (G3에 포함).

**G7. Index row = 포인터** — `index.md` row의 Summary/Notes는 **TL;DR 수준 ≤240자**. 상세 분석/팩트체크/함의/코호트 설명 index 금지.

**검증** (작업 종료 직전 self-check 강제):
```bash
# Hard gate verification (서브에이전트는 archive 저장 후 이 체크 실행)
python3 -c "
import re, sys, yaml
p = sys.argv[1]
with open(p, 'rb') as f: raw = f.read()
assert raw.startswith(b'\xef\xbb\xbf'), 'BOM missing'
text = raw[3:].decode('utf-8')
# Front matter 필수 필드
m = re.match(r'---\n(.*?)\n---', text, re.S)
assert m, 'YAML front matter missing'
fm = yaml.safe_load(m.group(1))
for k in ['Platform', 'Repeat_7d', 'Mode', 'Actionability', 'Next_Action']:
    assert k in fm, f'front matter missing: {k}'
# Mode=compact면 3.4 SKIP
if fm['Mode'] == 'compact':
    assert '### 3.4 상세 분석' not in text, 'compact mode cannot have 3.4'
# 3.7 함의: 직접 적용 인사이트 없음 단독 줄 또는 ≤2 불릿
print('OK')
" "$ARCHIVE_PATH"
```

위반 시 archive 재작성. 거짓 통과 보고 시 작업 실패.

---

## 📊 메타 함정 경고 (Codex 지적)

**셀프-리플렉션 자체가 또 다른 템플릿으로 굳을 위험.** 문제 발견 글쓰기가 보상되면 행동 변화 없이 "문제 리스트만 정교"해진다. 이 HARD GATES는 그래서 추가하는 원칙이 아니라 **분량을 자르는 도구**다. archive에 글자 더 쓰지 말고, **쓰지 마라**.

---

## 🚨🚨🚨 MANDATORY: 서브에이전트 위임 (2026-04-28 지혁 지시)

**메인 컨텍스트는 링크 처리하지 않는다. 무조건 서브에이전트에게 위임한다.**

### 왜?
지혁이 링크를 연속으로 보내면 메인 컨텍스트에 lens chain / cross-reference가 누적되면서 output이 점점 비대해지고 퀄리티가 좇같아진다. 서브에이전트는 fresh context로 시작하므로 매번 깨끗한 결과가 나온다.

### 메인 컨텍스트가 하는 일 (오직 이것만)
1. 링크 수신 → bd 등록 (선택) + TodoWrite 큐
2. **`Agent` tool로 `general-purpose` 서브에이전트 dispatch**
3. 서브에이전트 결과(짧은 보고) 받아서 **3-5줄로 지혁에게 전달**
4. 끝.

**메인은 절대 직접 스크래핑 / 번역 / 아카이브 / 텔레그램 전송 / 인덱스 업데이트 안 한다.**

### 서브에이전트에게 던질 prompt 템플릿

```
You are processing an SNS link via the link-summary skill (full path:
~/2lab.ai/skills/link-summary/SKILL.md). Read that SKILL.md first to
understand the 6-phase workflow.

URL: <지혁이 보낸 URL>
Timestamp received: <KST timestamp>

Execute ALL phases yourself:
1. Scrape. **먼저 sns-scraping 스킬을 읽고 그 전략대로 긁어라 — patchright 한 방으로 끝내지 마라:**
   `~/2lab.ai/skills/sns-scraping/SKILL.md`
   (X = 3-phase: profile scroll + Google `site:x.com/{user}/status` discovery +
   individual tweet full-text fetch / Threads = og:description).
   환경: `~/.scrapling-venv/bin/python3` + patchright,
   `LD_LIBRARY_PATH="$HOME/.local/lib/chromium-deps/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"`.
   X.com login wall → nitter.poast.org / nitter.net / nitter.privacydev.net fallback.

   **🚨 LONG-FORM / 외부 essay 원문 확보 의무 (2026-06-02 분노 / 2026-06-05 jina fallback 확립):**
   본문이 **X article(`x.com/i/article/...`) 또는 외부 essay/뉴스레터/블로그 링크 한 줄**이면,
   그 **본문 전문 verbatim 확보가 너의 일.** 확보 순서:
   1. **jina reader 한 방 (검증된 1순위):**
      `curl -s "https://r.jina.ai/https://x.com/{user}/status/{id}"`
      X long-form 본문은 트윗 status 페이지에 note-tweet으로 박혀 있어 jina가 로그인 월을
      우회하고 전문을 렌더한다. **`/i/article/...` URL에 직접 붙지 마라 — 로그인 월이다. jina는 status URL에 건다.**
   2. 외부 essay/블로그 → jina 동일: `curl -s "https://r.jina.ai/{essay_url}"`.
      막히면 작자 공개 미러(letters.*, substack 등) WebSearch.
   - **"저작권"/"로그인 월" 핑계로 self-summary·요약을 원문 자리에 넣기 = 작업 실패.**
   - jina + 미러 모두 실패한 경우에만 G5(ACCESS_FAILED). 그 전에 jina 1회 + 미러 1회 이상 강제.

   **G5 (Access Stop-rule):** 위 미러 검색 포함 모든 접근 경로 실패 시에만 적용. 분석/맥락 확장 금지.
   front matter `Verification: ACCESS_FAILED` 명시 후 3.4/3.6/3.7 SKIP, 3.1
   TL;DR 1줄 + 3.5에 실패 사유만 적고 종료. **요약으로 원문 자리를 메우지 말 것.**

2. **Phase 2.5 — Repeat 체크 (G1):**
   ```bash
   AUTHOR=<@handle>
   grep -c "@${AUTHOR}" /home/zhugehyuk/2lab.ai/soul/p9/ARTIFACTS/link-summaries/index.md \
     | head -1  # 최근 7일 윈도우 근사
   ```
   - `Repeat_7d >= 2` OR 24h 내 동일 작자+동일 레포/CTA 재포스트
     → `Mode: compact` 강제. 풀-archive 생성 금지.
   - compact mode: 3.4 SKIP / 3.5 ≤3항목 / 3.6 ≤1항목 / 3.7 1줄.
   - 평시(`Mode: full`): 모든 섹션 생성 가능 단 G3/G4 분량 제한.

3. Fact-check authority claims, numbers, cited research via WebSearch.
   Verify identity if any title is named.

   **자매 archive 일관성 (Codex 지적):** 같은 작자의 다른 archive와 동일
   사실(예: GitHub star 수, 회사명)을 cross-check. 불일치 발견 시 신뢰도
   --, 최신 1차 소스로 통일.

4. Create dense archive at
   /home/zhugehyuk/2lab.ai/soul/p9/ARTIFACTS/link-summaries/YYYY-MM/
   YYYY-MM-DD-<handle>-<slug>.md

   **MANDATORY 3-section structure (지혁 2026-04-30 강화 — 위반 시 작업 실패):**

   ### 1. 원문 (Original — verbatim, 무손실)
   - 스크래핑된 원본 텍스트를 **글자 그대로(verbatim)** 저장. 절대 요약·압축·재배열 금지.
   - 트윗 스레드는 1→2→3 self-reply 모두 포함. 댓글 체인도 가능한 만큼 원문 보존.
   - 모든 이미지: `src` URL 표기 + patchright screenshot 파일 경로 명시 + ALT 텍스트 인용.
   - 이미지 OCR/Vision 텍스트 설명은 **여기 원문 아닌 가공(섹션 3)에 분리**.
   - **🚨 LONG-FORM 본문 = 원문 (2026-06-02): 본문이 X article/외부 essay 링크면, 그 essay
     전문(미러에서 확보)이 원문 섹션의 핵심이다. 작자 self-summary·요약을 원문 자리에 넣으면 사기다.**
     essay 전문 확보 실패 시 → 1단계 G5(ACCESS_FAILED)로 처리하되 요약을 채워넣지 말 것.

   ### 2. 번역 (Translation)
   - 원문이 한국어가 **아닌 경우에만** 작성. 한국어 원문이면 통째로 생략.
   - 요약 없이 전문 직역. 의역/해설/함의 섞지 말 것 (가공 섹션이 따로 있음).
   - 이미지 ALT 텍스트도 번역.

   ### 3. 가공 (Analysis — 익스큐티브 서머리 / 위→아래 = 한눈→상세)

   **🚨 계층 강제 (2026-05-15 지혁 지시):** 가공 섹션은 익스큐티브 서머리 형식.
   사람이 위에서부터 읽으면서 필요한 깊이에서 멈출 수 있어야 한다.
   "TL;DR → 핵심 발견 → 컨텍스트 → 상세 분석 → 비판 → 함의" 순.

   - **3.1 TL;DR** — 한 줄. 이 글의 정수.
   - **3.2 핵심 발견 (Key Findings)** — 불릿 3-5개, 각 1줄. 가장 중요한 사실/주장만.
   - **3.3 컨텍스트** — 1-2문장. 누가/언제/왜 발화했는지, 왜 지금 중요한가.
   - **3.4 상세 분석** — 이미지 OCR/Vision 텍스트 설명 + 함의/관점/맥락. 깊게.
     - 이미지: `> **[IMAGE: Figure N — 제목]**` 블록
     - **G1 compact mode면 이 섹션 SKIP.**
   - **3.5 팩트 체크** — ✅/⚠️/❌/🔍 항목별. compact mode면 최대 3항목.
   - **3.6 비판/리스크 (G3 게이트)** — **최대 2개 불릿.**
     - 각 불릿은 **원문 verbatim 인용 1개 또는 수치/링크 1개** 필수.
     - 4-슬롯(engagement bait / authority halo / overclaim / cherry-pick) 자동 채우기 금지. **적용되는 것만.**
     - G6 (Korean tone): 한국 SNS 캐주얼 톤은 자동 engagement bait 감점 X. 명백한 CTA/구매 유도/data inflation에만 적용.
     - compact mode면 최대 1항목.
   - **3.7 함의 So What (G4 게이트)** — **최대 2개 불릿, 각 1문장.**
     - 직접 액션/함의 없으면 **반드시 1줄만**: `- 직접 적용 인사이트 없음`
     - Context Rot Week chain 연결은 **0 또는 1개만** (강제 연결 금지).
     - compact mode면 1줄.

   - **3.8 심층 분석 v3 글A (옵션, 게이트 통과 시만)** — 7-9 포스트 쓰레드 시리즈
     - 목적: 함의/분석을 짧은 문장으로 쪼개서 읽히게 (지혁 트레드 재사용 가능 형식)
     - **포스트 매핑 (7-9 포스트 표준 구조)**:
       - `1/N`: **훅** (인지 충돌 / 통념 깨기 / 모순 노출) — 1-2문장
       - `2/N` ~ `3/N`: **핵심 증거** (숫자 + 1차 소스 인용 + 해석) — 각 포스트 인용 `> ` 블록 필수
       - `4/N` ~ `6/N`: **분석 레이어** (왜 이게 중요한가 / 작동 메커니즘 / 2차 효과)
       - `7/N`: **반론 steelman** (반대 입장 강하게 옹호 → 그래도 이게 우세한 이유)
       - `8/N`: **행동 지침** (독자가 내일 뭐 할지 — 측정 가능한 액션)
       - `N/N` (마지막): **TLDR + 출처 링크** (원문 + 1차 소스)
     - **N = 7~9**. 8 미만이면 액션 또는 steelman 압축, 9 초과 금지.
     - 라벨링: **`1/N`, `2/N` 분수형만 허용**. "쓰레드1", "Post 1" 금지.
     - 문체: **비존대 평어체** (지혁 톤 — "~다", "~한다" 끝맺음). 필러 0, 짧은 문장, 능동태, 단정적.
     - **강제**: 1차 소스 직접 인용을 **각 증거 포스트(2/N, 3/N)에 1개 이상** 포함 (`> ` 블록)
     - **금지**: 추측 표현 / 금지 문자 / 금지 표현 (아래 v3 금지 목록)
     - **G6 비적용**: Korean tone exemption은 3.6에만. **글A는 비존대 평어체 강제**라 G6 무관.

   - **3.9 심층 분석 v3 글B (옵션, 게이트 통과 시만)** — 글A 압축 장문
     - **형식: 3-9 단락, 단락당 480자 미만** (한국어 기준, 공백 포함). 단락 = 빈줄로 분리.
     - **글A 주장/인용 유지, 중복만 제거.** 새 주장 추가 금지 (글A에 없는 주장 → 1차 소스 부족).
     - **단락마다 소스 태그 1개 이상** (`[S1]`, `[S2]` 형식). 마지막 단락 또는 별도 `**Sources**` 블록에서 `[S1] URL` 형태로 매핑.
     - 문체: 글A와 동일 — **비존대 평어체**, 능동태, 단정적.
     - **금지**: 추측 표현 / 금지 문자 / 금지 표현 (글A와 동일 목록)
     - **G6 비적용**: 글B도 비존대 평어체 강제. G6 무관.

   **v3 작성 게이트 (G8 — 인플레이션 방지, 2026-05-18 지혁 v3 요구 + Codex 머지)**
   - `Mode: compact` → 3.8, 3.9 SKIP
   - `Actionability: 0` → 3.8, 3.9 SKIP
   - `Actionability: 1` → 3.8만 생성, 3.9 SKIP
   - `Actionability: 2` 이상 → 3.8, 3.9 둘 다 생성 가능
   - `PrimarySources < 2` → 3.8, 3.9 SKIP (1차 소스 부족 시 v3 적용 무의미)

   **v3 금지 목록 (3.8/3.9에만 적용)**
   - **금지 문자**: `『 』`, `→` (유니코드 화살표 U+2192), `->`, `⇒`, `▶`, `②③④⑤⑥⑦⑧⑨⑩` (원숫자), `·` (중간점 U+00B7), `※`, 기타 비표준 화살표/장식
   - **금지 표현**: "흥미롭게도", "흥미로운 점은", "사실은", "사실", "기본적으로", "결론적으로", "정리하자면", "한마디로", "요약하면"
   - **추측 금지 변형 (한)**: "아마도", "~일 것이다", "~일듯", "~같다", "추정", "추측", "가능성", "~로 보인다", "~인 듯하다"
   - **추측 금지 변형 (영)**: maybe, probably, likely, seems, appears, presumably
   - **감정 수사**: "놀라운", "충격적인", "혁명적인", "엄청난", "대단한" (숫자가 놀라움을 만들게)
   - **라벨링**: "쓰레드1", "쓰레드 2", "Post 1", "포스트 1" → **`1/N` 분수형만 허용**
   - **이모지**: ✅⚠️❌🔍🎯 등 절대 금지 (3.5 팩트체크 라벨에만 ✅/⚠️/❌/🔍 허용)
   - **자기 칭찬/메타 발언**: "이 글에서 보듯", "위에서 말했듯", "이미 살펴봤듯이"

   **⚠️ 절대 금지:**
   - 원문 섹션을 "압축/핵심만"으로 표기하고 요약 넣기 (사기)
   - 이미지 src URL/screenshot path 누락 (재검증 불가)
   - 가공 내용을 원문/번역에 섞기 (분리 원칙 위반)
   - 원문이 한글인데 "번역" 섹션에 가공된 한글 넣기
   - 3.6/3.7 분량 게이트 초과 (G3/G4 위반 = 작업 실패)

5. **Pre-write self-check (G1~G8 검증)** — archive 저장 전 다음 코드 실행:
   ```python
   import re, sys
   try:
       import yaml
   except ImportError:
       yaml = None
   FORBIDDEN_CHARS = ['『', '』', '→', '⇒', '▶', '※', '·']
   FORBIDDEN_CIRCLED = ['②','③','④','⑤','⑥','⑦','⑧','⑨','⑩']
   FORBIDDEN_PHRASES = ['흥미롭게도','흥미로운 점은','사실은','기본적으로','결론적으로','정리하자면','한마디로','요약하면']
   FORBIDDEN_SPECULATE = ['아마도','일 것이다','일듯','같다','추정','추측','가능성','로 보인다','인 듯하다',
                          'maybe','probably','likely','seems','appears','presumably']
   FORBIDDEN_EMO = ['놀라운','충격적인','혁명적인','엄청난','대단한']
   def check(archive_path):
       with open(archive_path, 'rb') as f: raw = f.read()
       assert raw.startswith(b'\xef\xbb\xbf'), 'BOM missing (인코딩 게이트 위반)'
       text = raw[3:].decode('utf-8')
       m = re.match(r'---\n(.*?)\n---', text, re.S)
       assert m, 'G2 violation: YAML front matter missing'
       fm_text = m.group(1)
       for k in ['Platform', 'Repeat_7d', 'Mode', 'Actionability', 'Next_Action']:
           assert k in fm_text, f'G2 violation: front matter missing {k}'
       if 'Mode: compact' in fm_text:
           assert '### 3.4 상세 분석' not in text, 'G1 violation: compact mode cannot have 3.4'
       # G4: 3.7 함의 게이트
       m37 = re.search(r'### 3\.7 함의[^#]*', text)
       if m37:
           bullets = re.findall(r'^- ', m37.group(0), re.M)
           if '직접 적용 인사이트 없음' not in m37.group(0):
               assert len(bullets) <= 2, f'G4 violation: 3.7 has {len(bullets)} bullets (max 2)'
       # G3: 3.6 비판 게이트
       m36 = re.search(r'### 3\.6 비판/리스크[^#]*', text)
       if m36:
           bullets = re.findall(r'^- ', m36.group(0), re.M)
           assert len(bullets) <= 2, f'G3 violation: 3.6 has {len(bullets)} bullets (max 2)'
       # G8: v3 글A/B 게이트 (3.8/3.9 있을 때만)
       m38 = re.search(r'### 3\.8 .*?(?=^### |\Z)', text, re.S | re.M)
       m39 = re.search(r'### 3\.9 .*?(?=^### |\Z)', text, re.S | re.M)
       v3_text = (m38.group(0) if m38 else '') + (m39.group(0) if m39 else '')
       if v3_text:
           # 금지 토큰 검사
           for ch in FORBIDDEN_CHARS + FORBIDDEN_CIRCLED:
               assert ch not in v3_text, f'G8 violation: forbidden char "{ch}" in v3'
           for p in FORBIDDEN_PHRASES + FORBIDDEN_SPECULATE + FORBIDDEN_EMO:
               assert p not in v3_text, f'G8 violation: forbidden phrase "{p}" in v3'
           # 글A 포스트 라벨 1/N 형식 (####까지 허용, 분자≤분모 강제)
           if m38:
               # `#### 1/7`, `### 1/7`, `**1/7**`, `1/7 hook` 모두 잡기
               labels = re.findall(r'(?:^#{2,6}\s+|^\*\*|^)(\d+)/(\d+)\b', m38.group(0), re.M)
               if labels:
                   n_total = int(labels[0][1])
                   assert 7 <= n_total <= 9, f'G8 violation: v3 글A N={n_total} (must be 7~9)'
                   # 분모 통일 + 분자 ≤ 분모 (8/7, 9/7 같은 overflow 금지)
                   for num_s, den_s in labels:
                       num, den = int(num_s), int(den_s)
                       assert den == n_total, f'G8 violation: 글A N inconsistent ({num}/{den} vs {n_total})'
                       assert num <= n_total, f'G8 violation: 글A label {num}/{den} numerator exceeds N'
                   # 라벨 "Post 1", "쓰레드1" 금지
                   assert not re.search(r'(Post\s+\d|쓰레드\s*\d|포스트\s*\d)', m38.group(0)), \
                       'G8 violation: 글A bad labels (use 1/N only)'
                   # 글A 안에 ####보다 깊은 헤더 금지 (####는 포스트 라벨용으로 허용)
                   assert not re.search(r'^#{5,}\s', m38.group(0), re.M), \
                       'G8 violation: 글A has ##### or deeper sub-headers'
           # 글B 단락 480자
           if m39:
               # 단락 = 빈줄 분리, 메타라인/소스블록 제외
               paras = [p.strip() for p in re.split(r'\n\s*\n', m39.group(0)) if p.strip()]
               body_paras = [p for p in paras if not p.startswith(('###','**Sources','- [S','[S'))]
               for i, p in enumerate(body_paras):
                   assert len(p) < 480, f'G8 violation: 글B para {i+1} = {len(p)} chars (≥480)'
       return 'OK'
   print(check(sys.argv[1]))
   ```
   - 통과해야 텔레그램 전송 진행. 실패 시 archive 수정 → 재검사.

6. Send archive to Telegram via mcp__send-file__send_document
   with caption ≤900 chars (leave 124 char buffer for Telegram limit).

7. **Index update (G7 게이트)**: `~/2lab.ai/soul/p9/ARTIFACTS/link-summaries/index.md`
   에 새 topmost row 삽입.
   - **Index row = 포인터.** Summary/Notes는 TL;DR 수준 **≤240자.**
   - 상세 분석/팩트체크/함의/코호트 설명/critique 인덱스에 쓰지 말 것.
   - 상세는 archive 파일에서만.

8. TTS phase: SKIP (disabled since 2026-03-31).

Critical thinking required:
- Flag overclaims, marketing hype, engagement farming patterns.
- If author cites authority/data, verify it.
- Do NOT inflate cross-references just to fill space.
- Connect to existing chain ONLY if the connection is real, not invented.

Report back to the parent agent in EXACTLY this format (≤250 words total):
- Slug: <filename slug>
- TG msgId: <id>
- Index updated: yes/no
- BOM verified: yes/no
- TL;DR: <1 sentence — 한눈에 정수>
- Key Findings: <3-5 bullets, each ≤1 line>
- Context: <1-2 sentences — 누가/언제/왜>
- Critique: <1-2 sentences or "none">
- So What (지혁 함의): <1-2 sentences — 실용 액션>

이 보고는 메인 에이전트가 그대로 지혁에게 전달할 수 있도록 익스큐티브
서머리 형식으로 작성. 메인은 이걸 재가공하지 않고 거의 그대로 relay.

Do not include the full archive content in your reply.
```

### Agent tool 호출 예시

```
Agent({
  description: "Process SNS link via link-summary",
  subagent_type: "general-purpose",
  prompt: <위 템플릿 + 실제 URL/timestamp>
})
```

### 메인이 지혁에게 보고하는 형식 (익스큐티브 서머리, 2026-05-15 지혁 지시)

서브에이전트 보고를 거의 그대로 relay. **계층적, 위→아래 = 한눈→상세**.

```
✅ <slug>

🎯 **TL;DR**
<1줄 정수>

🔑 **핵심 발견**
• <발견 1>
• <발견 2>
• <발견 3>

📚 **컨텍스트**
<1-2 문장 — 누가/언제/왜>

⚠️ **비판/리스크** (있으면, 없으면 생략)
<1-2 문장>

💡 **So What (지혁 함의)**
<1-2 액션/통찰>

📨 TG msgId <id>, index + BOM 검증 통과. bd <id> 종료.
```

**원칙:**
- 사람이 스크롤하며 필요한 깊이에서 멈출 수 있게 한다.
- 헤더(🎯/🔑/📚/⚠️/💡)로 시각 hierarchy 강제.
- 메인이 cross-reference / lens chain / soma 함의를 **추가로 늘리지 마라**.
- 지혁이 더 알고 싶으면 아카이브 파일 직접 읽는다.

---

## 🚨 큐잉 규칙: 작업 중 링크 수신 시 (2026-04-11 추가)

**지혁이 링크를 연속으로 보낼 때, 현재 작업과 짬뽕하지 않는다.**

### 원칙 (서브에이전트 위임 시대)
1. 모든 링크는 **서브에이전트에게 위임**한다 (위 MANDATORY 섹션 참조).
2. **여러 링크를 동시에 받으면 → 서브에이전트 여러 개 병렬 dispatch 가능** (각자 독립 컨텍스트).
3. 단, **같은 파일 동시 수정 위험** (예: index.md) → 서브에이전트들에게 "index.md 수정은 sequential lock 가정, 충돌 시 retry" 명시.
4. 메인 컨텍스트는 dispatch 후 결과만 모아서 보고. 직접 처리 금지.

### 워크플로우
```
[링크 A 처리 중]
  ↓ 지혁이 링크 B 보냄
  → TodoWrite에 "🔗 링크 B 처리" status=pending으로 추가
  → 링크 A 계속 처리 (Phase 1~6 완료)
  ↓ 링크 A 완료
  → TodoWrite에서 링크 B를 in_progress로 변경
  → 링크 B 처리 시작
  ↓ 지혁이 링크 C, D 보냄
  → 둘 다 TodoWrite 큐 끝에 pending으로 추가
  → 링크 B 완료 후 C, C 완료 후 D
```

### TodoWrite 형식
```
content: "🔗 [URL 또는 @handle 요약] 처리"
activeForm: "🔗 [URL 또는 @handle 요약] 처리 중"
status: "pending" | "in_progress" | "completed"
```

### 수신 즉시 응답
링크 받으면 즉시 서브에이전트 dispatch + 지혁에게 짧게 알림:
> "🚀 서브에이전트에 위임 (URL <slug>). 결과 받으면 보고."

**서브에이전트는 fresh context로 시작하므로 메인 컨텍스트 비대화 없이 원 바이 원 처리된다.**

---

## ⚡ 핵심 원칙: 글 먼저, 음성 나중

**절대 다 끝날 때까지 기다리지 않는다.**

1. 스크래핑 + 번역/분석 완료 → **즉시 텔레그램으로 보냄** (텍스트 메시지 + md 파일)
2. 음성 생성 (GPU ~60초) → **완료되면 따로 보냄**

지혁이 글을 읽는 동안 음성이 뒤따라온다.

---

## 워크플로우

### Phase 1: 스크래핑 (sns-scraping 스킬 사용)

**X/Twitter:**
```bash
export LD_LIBRARY_PATH="$HOME/.local/lib/chromium-deps/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"
~/.scrapling-venv/bin/python3 -c "
from patchright.sync_api import sync_playwright
# ... tweet fetch with data-testid='tweetText'
"
```

**Threads:**
```bash
# Same patchright approach, [data-pressable-container='true'] selector
```

### Phase 2: 링크 탐색 + 팩트 체크 + 리플라이 체인 (2026-04-13 강화)

본문에 포함된 링크(인용 트윗, 외부 URL)를 1단계까지 추적:
- 인용 트윗 → patchright로 원문 가져오기
- 외부 링크 → WebFetch로 본문 추출
- 이미지 → ALT 텍스트 + 스크린샷 저장

**🚨 팩트 체크 (필수 — 지혁 10회+ 지적):**
- 트윗에서 **권위자/직함이 언급되면** (예: "AMD AI Director", "Google VP") → WebSearch로 신원 확인
- **데이터/수치가 인용되면** → 1차 소스(GitHub issue, 논문, 공식 발표) 찾아서 검증
- **"연구에 따르면", "보고서에 따르면"** → 해당 연구/보고서 직접 확인
- 팩트 체크 결과는 아카이브의 `## 3. 가공` 아래 `### 3.5 팩트 체크`에**만** 기록 (섹션명 통일 — Codex 지적 내부 모순 해결)
- ✅ 확인됨 / ⚠️ 부분적 / ❌ 거짓 / 🔍 미확인 으로 표시

**🚨 리플라이 체인 탐색 (필수 — 지혁 지적: "x 글은 엮인글에 이미지 좇나 다 많은데 그거 엮인글 다 봐야지"):**
- X 글의 리플라이에 **이미지, 스크린샷, 데이터**가 포함된 경우가 많음
- patchright로 리플라이 영역 스크롤 + 이미지 다운로드
- 인증 벽으로 막히면 → WebSearch로 해당 트윗의 주요 리플라이/반응 탐색
- 특히 **원저자의 셀프 리플(스레드)** 와 **"link in the comments"** 패턴 확인
- 발견된 추가 콘텐츠는 아카이브에 포함

### Phase 3: 원문/번역/가공 3분리 → 파일 전송 (지혁 2026-04-30 강화)

**🚨🚨🚨 절대 규칙: 원문 / 번역 / 가공 3개 섹션은 반드시 분리 저장. 하나라도 압축/누락 시 작업 실패로 간주.**

#### 1️⃣ 원문 (Original — 무손실 verbatim)

**🚨 스크래핑은 `~/2lab.ai/skills/sns-scraping/SKILL.md`의 3-phase 전략을 쓴다. 자기 멋대로 단발 fetch하고 포기 금지.**

**🚨🚨 X long-form article (`x.com/i/article/...`) 특수 케이스 (2026-06-05 jina fallback 확립):**
- long-form article은 본문 트윗이 article 링크 한 줄뿐이지만, **essay 전문은 그 트윗 status 페이지에 note-tweet으로 통째로 박혀 있다.**
- **확보 1순위 = jina reader 한 방:** `curl -s "https://r.jina.ai/https://x.com/{user}/status/{id}"`
  → 로그인 월 우회하고 본문 verbatim 렌더 (2026-06-05 @0xcodez article 17.5KB 전문 확보로 검증).
- **`x.com/i/article/<id>` URL에 patchright로 직접 붙지 마라 — 로그인 월이다.** jina는 항상 status URL에 건다.
- self-summary/quote-reply 요약을 원문 자리에 넣기 = 사기 = 작업 실패. jina도 막히면 공개 미러 WebSearch, 그래도 안 되면 G5 ACCESS_FAILED (요약 대체 금지).

- **절대 요약·압축·재배열·생략 금지.** 스크래핑된 원본 텍스트를 **글자 그대로(verbatim)** 저장.
- 한국어 원문이면 그대로. 영어/일어/중국어 원문이면 그 언어 그대로 (번역 X).
- 트윗 스레드는 1번 글 → 2번 글 → ... 순서대로 모든 self-reply 포함.
- 댓글/리플라이 체인도 (스크래핑된 한도 내에서) 원문 그대로 보존.
- **이미지/스크린샷 처리:**
  - 모든 이미지의 `src` URL을 표기 (`![ALT](https://pbs.twimg.com/...)` 형태로)
  - patchright screenshot으로 캡처한 파일 경로 명시 (`/tmp/scrape_xxx.png`)
  - ALT 텍스트가 있으면 그대로 인용
  - 이미지 텍스트 설명(OCR/Vision)은 **원문 섹션이 아니라 가공 섹션**에 분리해서 넣는다 (원문에 추측 텍스트 섞으면 안 됨)
- 표/코드 블록도 원본 형식 그대로 보존.

#### 2️⃣ 번역 (Translation — 한국어 직역, 원문이 한글이면 SKIP)

- 원문이 **한국어가 아닌 경우에만** 작성. 한국어 원문이면 이 섹션 빈 채로 두거나 헤더 자체 생략.
- **요약 없이 전문 직역.** 원문 1문장 = 번역 1문장 매칭 원칙.
- 의역 최소화. 원문 의미 정확히 전달이 우선.
- 이미지 ALT 텍스트도 번역.
- 주의: 번역에 분석/해설/함의 섞지 말 것 (가공 섹션이 따로 있음).

#### 3️⃣ 가공 (Analysis — 익스큐티브 서머리 형식, 2026-05-15 지혁 지시)

**🚨 계층 강제**: 가공 섹션은 익스큐티브 서머리. 사람이 위에서부터 읽으면서
필요한 깊이에서 멈출 수 있어야 한다. 평면적 나열 금지.

**필수 순서 (위→아래 = 한눈→상세):**

##### 3.1 TL;DR
한 줄. 이 글의 정수. 30자 이내 권장.

##### 3.2 핵심 발견 (Key Findings)
불릿 3-5개. 각 1줄. 가장 중요한 사실/주장만 추출.

##### 3.3 컨텍스트
1-2문장. 누가/언제/왜 발화했는지. 왜 지금 중요한가.

##### 3.4 상세 분석
이미지 OCR/Vision 텍스트 설명 + 함의/관점/맥락. 깊게.
이미지 블록 예시:
```
> **[IMAGE: Figure 1 — SWE-bench 점수 추이]**
> X축: Release Date, Y축: Score (%)
> Sonnet 3.5: 49.0% → Opus 4: 72.5% → Opus 4.5: 80.9%
> 우상향 곡선, 18개월 만에 65% 상대적 향상.
```

##### 3.5 팩트 체크
- ✅ 확인됨 / ⚠️ 부분적 / ❌ 거짓 / 🔍 미확인
- 인용된 권위/데이터/연구 각 항목별

##### 3.6 비판/리스크 (G3 게이트 — 2026-05-17 강화)
- **최대 2개 불릿.** compact mode면 최대 1.
- 각 불릿은 **원문 verbatim 인용 1개 또는 수치/링크 1개** 필수 (증거 없는 flag 금지).
- "Engagement bait / Authority halo / Overclaim / Cherry-pick" 4-슬롯 자동 채우기 금지. 적용되는 것만.
- **G6 Korean creator tone**: 한국 SNS 캐주얼 톤(`팝콘 먹으면서`, `썰 풀어볼게`)을 자동 engagement bait 감점 금지. 명백한 CTA / 구매 유도 / data inflation에만 적용.
- 신뢰도 평가(선택). 5/14 코호트 분류는 한 archive당 max 1회.

##### 3.7 함의 (So What — G4 게이트, 2026-05-17 강화)
- **최대 2개 불릿, 각 1문장.** compact mode면 1줄.
- 직접 액션/함의 없으면 **반드시 1줄만**:
  - `- 직접 적용 인사이트 없음`
- Context Rot Week chain 연결은 **0 또는 1개만** (강제 연결 금지).
- "soma/p9 함의 0이라며 4개 sub-section 채우기" 패턴 금지 (지난 1주 67개 archive의 가장 큰 인플레이션 원천).

#### 아카이브 파일 구조 (필수 템플릿)

```markdown
---
Source: [URL]
Platform: X|Threads|LinkedIn|Reddit|GitHub|Web|YouTube
Author: @handle (실명/직함, 검증 결과)
Date: YYYY-MM-DD HH:MM TZ
Repeat_7d: <int>     # G1: index.md 기준 동일 Author 최근 7일 등장 횟수
Mode: full|compact   # G1: Repeat_7d >= 2 면 compact 강제
Actionability: 0-3   # G4: 0=정보, 1=참고, 2=시도해볼 만, 3=즉시 실행
Next_Action: none|note|try|todo|bd  # 후속 액션 유형
Stats: 조회/❤️/리포/답글/뷰
Tags: #tag1 #tag2
Verification: 팩트체크 결과 한 줄 요약 (또는 ACCESS_FAILED)
---

# [제목]

## 1. 원문 (Original — verbatim, 무손실)

[원본 텍스트 글자 그대로. 이미지는 src URL + 스크린샷 path 명시.]

### 이미지/스크린샷 인덱스
- `<screenshot path>` — full page screenshot
- `![ALT1](src URL)` — 인라인 이미지 1
- ...

## 2. 번역 (Translation — 한국어 직역, 원문 한글이면 생략)

[전문 직역. 원문 한글이면 이 섹션 통째로 생략.]

## 3. 가공 (Analysis — 익스큐티브 서머리)

### 3.1 TL;DR
[한 줄. 이 글의 정수.]

### 3.2 핵심 발견 (Key Findings)
- 발견 1
- 발견 2
- 발견 3
(3-5개, 각 1줄)

### 3.3 컨텍스트
[1-2문장. 누가/언제/왜 발화. 왜 지금 중요한가.]

### 3.4 상세 분석
[이미지 OCR/Vision + 함의/관점/맥락. 깊게. **compact mode면 이 섹션 SKIP.**]

### 3.5 팩트 체크
- ✅/⚠️/❌/🔍 항목별 (compact mode면 최대 3항목)

### 3.6 비판/리스크 (G3: max 2 bullets, evidence required)
- [원문 인용/수치 1개 포함한 비판 1]
- [원문 인용/수치 1개 포함한 비판 2]
<!-- 없으면 이 섹션 전체 생략 -->

### 3.7 함의 (So What — G4: max 2 bullets or "직접 적용 인사이트 없음" 단독)
- [실용 함의 1]
- [실용 함의 2]
<!-- 또는 단 1줄: - 직접 적용 인사이트 없음 -->
```

**G2 / G3 / G4 위반 시 archive 재작성. self-check 코드는 위 서브에이전트 prompt 5단계 참조.**

**⚠️ 절대 하지 말 것:**
- 원문 섹션을 "압축, 핵심만"이라고 표기하고 요약 넣기 — **이건 사기다**
- 이미지 src URL/screenshot path 누락하기 — 나중에 재검증 불가
- 가공 섹션 내용을 원문/번역에 섞기 — 분리 원칙 위반
- 원문이 한글인데 "번역" 섹션에 가공된 한글 넣기 — 그건 가공이지 번역 아님

#### 🚨 인코딩 강제 (2026-05-14 지혁 지적, 일주일치 한글 깨짐 사고 후)

**아카이브 .md 파일 저장 시 반드시 UTF-8 BOM + NFC 정규화 적용. 위반 시 한글 깨짐.**

- **이유**: BOM(`EF BB BF`) 없으면 Windows Notepad / 텔레그램 모바일 미리보기 / 일부 텍스트 뷰어가 charset 자동 감지 실패 → CP949/CP1252로 오인식 → 한글 전부 깨짐. NFC 미정규화면 macOS/iOS에서 자모 분리(한굴) 발생.

- **필수 저장 패턴** (Python):
  ```python
  import unicodedata
  text_nfc = unicodedata.normalize("NFC", text)
  out = b"\xef\xbb\xbf" + text_nfc.encode("utf-8")
  with open(archive_path, "wb") as f:
      f.write(out)
  ```

- **Write tool 사용 시**: 파일 저장 후 즉시 bash 스크립트로 재포장 (Write tool은 BOM 옵션 없음):
  ```bash
  python3 -c "
  import unicodedata, sys
  p = sys.argv[1]
  with open(p, 'rb') as f: raw = f.read()
  if raw.startswith(b'\xef\xbb\xbf'): sys.exit(0)
  text = unicodedata.normalize('NFC', raw.decode('utf-8'))
  with open(p, 'wb') as f: f.write(b'\xef\xbb\xbf' + text.encode('utf-8'))
  " /path/to/archive.md
  ```

- **검증**: `head -c 3 archive.md | xxd` → `efbb bf` 보여야 통과.

- **부작용 없음**: 대부분 마크다운 렌더러(Obsidian, GitHub, VSCode) BOM 무시. 깨짐 픽스 비용 0 + 호환성 ↑.

### Phase 4: 익스큐티브 서머리 → 텔레그램 텍스트 (2026-05-15 지혁 지시)

Phase 3 파일 전송 **후에** 익스큐티브 서머리를 텔레그램 텍스트로 전송.
**계층적, 위→아래 = 한눈→상세.** 사람이 스크롤하며 필요한 깊이에서 멈출 수 있게.

**텔레그램 텍스트 메시지 포맷 (필수 hierarchy):**
```
📌 [제목]
✍️ @author · source · YYYY-MM-DD

🎯 **TL;DR**
[한 줄 — 이 글의 정수]

🔑 **핵심 발견**
• [발견 1]
• [발견 2]
• [발견 3]

📚 **컨텍스트**
[1-2 문장 — 누가/언제/왜 발화. 왜 지금 중요한가.]

🔍 **팩트 체크** (검증된 권위/숫자/연구가 있으면)
• ✅ [확인됨]
• ⚠️ [부분적]
• ❌ [거짓]

⚠️ **비판/리스크** (overclaim / engagement farming flag가 있으면)
[1-2 문장. 없으면 이 블록 생략]

💡 **So What (지혁 함의)**
[1-2 액션/통찰 — 지혁이 뭘 해야 하는가, 또는 어떤 통찰을 가져가는가]

🏷️ #tag1 #tag2 #tag3
```

**원칙:**
- 헤더(🎯/🔑/📚/🔍/⚠️/💡)로 시각 hierarchy 강제.
- 빈 블록은 헤더째로 생략 (예: 비판 없으면 ⚠️ 줄 안 씀).
- 평면적 나열 / 한 덩어리 문단 금지.
- 텔레그램 마크다운 굵게(`**...**`)는 지원, italic(`*..*`)도 지원.

### Phase 5: 음성 브리핑 (fish-tts, iu voice) → 따로 전송

> **⚠️ TTS 임시 비활성화 (2026-03-31): Phase 4 건너뛰기. 텍스트 + md만 전송.**

Phase 3에서 보낸 후 바로 시작. 완료되면 mp3 전송.

요약 스크립트(200~400자) 작성 → fish-tts iu 보이스로 생성 → 텔레그램 전송

```bash
cd ~/fish-speech && .venv/bin/python \
  ~/2lab.ai/skills/fish-audio/scripts/gpu-inference.py \
  --text '<|speaker:0|>요약 텍스트' \
  --prompt-text "$(cat ~/2lab.ai/skills/fish-tts/voices/iu/reference.txt)" \
  --prompt-audio ~/2lab.ai/skills/fish-tts/voices/iu/reference.mp3 \
  --output /tmp/link-summary-SLUG.wav \
  --checkpoint-path checkpoints/s2-pro \
  --device cuda --temperature 0.7 --top-p 0.9 --seed 42 --max-new-tokens 2048

# wav → mp3 변환
ffmpeg -i /tmp/link-summary-SLUG.wav -b:a 192k /tmp/link-summary-SLUG.mp3 -y

# 텔레그램 전송
mcp__send-file__send_document /tmp/link-summary-SLUG.mp3
```

긴 요약 (200자+) → 청크 분할 + 무음 패딩 + 병합:
```bash
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 1.5 /tmp/silence.wav -y
# concat list 생성 후
ffmpeg -f concat -safe 0 -i /tmp/concat.txt -c copy /tmp/merged.wav -y
ffmpeg -i /tmp/merged.wav -b:a 192k /tmp/link-summary.mp3 -y
```

### Phase 6: 인덱스 업데이트 (G7 게이트 — 2026-05-17 강화)

`~/2lab.ai/soul/p9/ARTIFACTS/link-summaries/index.md`에 새 항목 추가.

**G7 룰: Index row = 포인터. 재-archive 금지.**

- Summary/Notes 컬럼: **TL;DR 수준 ≤240자.** 한 줄로 끝.
- ❌ 상세 분석 / 팩트체크 결과 / 비판 / 코호트 분류 / 함의 인덱스에 쓰지 말 것.
- 그런 건 archive 파일에서만. 인덱스는 "어디 가서 더 읽지?"의 지도일 뿐.
- 이유: 2026-05 시점 index.md가 488KB까지 비대해져 "찾기/회상" 용도를 오히려 방해.

**행 포맷 (간략):**
```markdown
| Date | Author | Platform | TL;DR (≤240자) | Mode | Archive |
|---|---|---|---|---|---|
| 2026-05-17 | @bamtolai | Threads | Codex Chrome Extension으로 Codex×Gemini 브라우저 오케스트레이션 자랑 스레드. 실제 산출물 미공개. | full | [link](2026-05/...) |
```

월별 추가 액션: monthly digest 생성 (5/14 코호트 집계, 작자 누적 카운트, 폐기 후보)은 별도 작업 — link-summary 1회 워크플로우 안에서 하지 않는다.

---

## 전송 순서 (필수)

```
[스크래핑 + 전문 번역 완료]
  ↓ 즉시
  1. 📄 아카이브 md 파일 (send_document) — 원문 + 전문 번역 + 분석
  ↓ 바로
  2. 📝 텔레그램 텍스트 메시지 (요약 + 함의 + 관점)
  ↓ GPU 작업 (~60초)
  3. 🎙️ 음성 mp3 (send_document)
```

⚠️ **파일 먼저, 요약 나중. 원문과 번역은 반드시 파일로.**
⚠️ **TTS 비활성화 상태에서는 2가지(md 파일 + 요약 텍스트) 전송.**
⚠️ **글은 음성 기다리지 않고 즉시 보낸다.**

---

## 텔레그램 메시지 포매팅 가이드 (익스큐티브 서머리 hierarchy)

**Phase 4와 동일 포맷. 위→아래 = 한눈→상세. 빈 블록은 헤더째 생략.**

```
📌 [제목]
✍️ @author · source · YYYY-MM-DD

🎯 **TL;DR**
[한 줄 — 이 글의 정수]

🔑 **핵심 발견**
• [발견 1]
• [발견 2]
• [발견 3]

📚 **컨텍스트**
[1-2 문장 — 누가/언제/왜]

🔍 **팩트 체크** (검증된 권위/숫자가 있을 때만)
• ✅ [확인됨]
• ⚠️ [부분적]
• ❌ [거짓]

⚠️ **비판/리스크** (overclaim/engagement farming flag 있을 때만)
[1-2 문장]

💡 **So What (지혁 함의)**
[1-2 액션/통찰]

🏷️ #tag1 #tag2 #tag3
```

**원칙:**
- 헤더 emoji(🎯/🔑/📚/🔍/⚠️/💡)로 시각 hierarchy 강제.
- 사람이 TL;DR만 읽고 중단해도 의미가 통해야.
- 비판/팩트 체크 없으면 그 블록 통째 생략 (노이즈 X).
- 코드/기술 용어는 `백틱` 처리. 텔레그램 markdown `**bold**` / `*italic*` 지원.

---

## 제약사항

- fish-tts: 청크당 ~200자, 총 500자 이하 권장
- GPU 메모리 17GB — 동시 작업 불가
- 음성 생성 시간: ~200자 기준 ~65초
- 첫 실행 모델 로딩 ~45초
- 끝부분 무음 1.5초 필수

---

## 향후 확장

- [ ] 일반 웹 링크 지원 (뉴스, 블로그)
- [ ] YouTube 링크 → 자막 추출 + 요약
- [ ] 자동 태깅 (LLM 기반)
- [ ] 주간 다이제스트 생성
