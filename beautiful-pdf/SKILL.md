---
name: beautiful-pdf
description: Convert markdown to a beautifully designed editorial-style PDF report. Uses Pretendard variable font, Swiss-Coffee + Cool-Blue palette, minimalist-maximalism layout, cover page, table of contents, section dividers, page numbers. Optimized for Korean+English mixed reports. Use when user asks for "report PDF", "보고서 PDF", "아름다운 PDF", "예쁜 PDF", or wants to publish a markdown document as a polished document.
---

# beautiful-pdf — 아름다운 보고서 PDF 스킬

## 의도
Markdown 원고를 **에디토리얼 톤의 우아한 PDF**로 변환한다. 단순 변환이 아니라 **표지 / 목차 / 본문 / 푸터** 4-layer 레이아웃 + Pretendard 변동 폰트 + Swiss Coffee 베이스 팔레트 적용.

## 전제 (verify before run)

```bash
# 1. venv + weasyprint 설치 확인
~/2lab.ai/.venv/bin/python3 -c "import weasyprint, markdown_it; print(weasyprint.__version__)"

# 2. 폰트 존재 확인
ls ~/2lab.ai/skills/beautiful-pdf/assets/fonts/PretendardVariable.woff2

# 3. 디폴트 CSS / 렌더 스크립트 존재
ls ~/2lab.ai/skills/beautiful-pdf/templates/default.css
ls ~/2lab.ai/skills/beautiful-pdf/scripts/render.py
```

없으면:
- pip → `~/2lab.ai/.venv/bin/python3 -m pip install weasyprint markdown-it-py`
- 폰트 → `curl -L -o PretendardVariable.woff2 https://github.com/orioncactus/pretendard/raw/main/packages/pretendard/dist/web/variable/woff2/PretendardVariable.woff2`

## 사용법

```bash
~/2lab.ai/.venv/bin/python3 ~/2lab.ai/skills/beautiful-pdf/scripts/render.py \
  --input  /path/to/report.md \
  --output /path/to/report.pdf \
  --title  "리포트 제목" \
  --subtitle "부제 / 한 줄 요약" \
  --author "발행자 (선택)" \
  --date   "2026-05-07"
```

옵션:
- `--theme editorial` (default) — 신문 / 잡지 톤
- `--theme minimal` — 더 기본적인 white space 위주
- `--theme dark` — 다크 모드 (인쇄보단 화면용)
- `--toc` — 목차 자동 생성 (H2 기준)
- `--no-cover` — 표지 생략

## Markdown 원고 가이드

스킬이 더 잘 받아주는 마크업:

### 일반 (자동 처리)
- `# H1` — 본문 안에선 섹션 타이틀로
- `## H2` — 챕터, 자동으로 page-break 가능
- `### H3` / `#### H4` — 서브헤딩
- 표, 코드 블록, 인용, 이미지 모두 지원
- `---` (hr) — 시각적 디바이더 (점 3개로 변환)

### 강조 박스 (확장 마크업)
원고 안에 다음 패턴 쓰면 카드 박스로 처리:

```
> [!key] 핵심 요약
> 한 문장 또는 짧은 단락. 본문에서 강조하고 싶은 부분.
```

```
> [!warn] 리스크
> 경고 / 위험 / 주의 사항
```

```
> [!stat] 수치 하이라이트
> $1.85 ↑ +23% (2026-05-06)
```

### Drop cap
H2 직후 첫 문단 첫 글자가 자동으로 drop cap.

## 디자인 토큰 (default 테마)

| 토큰 | 값 | 의도 |
|---|---|---|
| Primary | `#1A1A1A` | 본문 |
| Background | `#FAF7F2` (Swiss Coffee) | 페이지 |
| Accent | `#1B4965` (Cool Blue) | 헤딩 / 링크 |
| Muted | `#6B6B6B` | 메타 정보 |
| Highlight | `#F4A261` | 강조 박스 보더 |
| Border | `#D9D2C5` | 표 / 디바이더 |

폰트:
- **Pretendard Variable** — 본문 / 헤딩 (한글 + 라틴)
- **JetBrains Mono / Monospace** — 코드

## 출력 사양
- A4 (210×297mm)
- 마진: 22mm 18mm 25mm 18mm
- 본문 10.5pt / 1.65 line-height
- H1 30pt / H2 18pt / H3 13pt
- 푸터: 페이지 번호 (n / total)
- 표지: 큰 타이틀 + 얇은 디바이더 라인 + 부제 + 날짜 + 발행자

## 사후 검증

```bash
# 페이지 수 + 파일 크기 확인
file /path/to/report.pdf
ls -la /path/to/report.pdf
```

페이지 수 너무 적으면 (예상 < 5p) layout 깨진 의심. CSS / 폰트 경로 확인.

## 한계
- 매우 복잡한 LaTeX 수식 미지원 (단순 inline은 가능)
- 대량 이미지 (>20장) 시 weasyprint 느려질 수 있음
- 외부 폰트 추가 시 assets/fonts에 .woff2 넣고 default.css `@font-face` 추가 필요

## 확장 아이디어
- `--theme magazine` — 2단 구성
- `--theme academic` — 인용 / 각주 / 참고문헌 자동 포맷
- 자동 차트 삽입 (matplotlib/plotly png) — 입력 frontmatter에 데이터 넘겨주면 차트 그려서 삽입
