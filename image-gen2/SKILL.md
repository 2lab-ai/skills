---
name: image-gen2
description: Batch image generation factory. Give it one prompt template (with a {subject} slot) plus a subject list (csv/json/txt) and it generates dozens-to-hundreds of images concurrently with automatic machine verification and retry. ZERO runtime LLM calls — prompts are pure template+subject string substitution. Reuses the image-gen Codex/OAuth engine (no API key). Triggers — 대량 이미지, 배치 이미지 생성, image-gen2, 이미지 공장, 여러 장 생성, batch image, image factory, bulk image generation.
version: 1.0.0
author: Elon (p9)
license: MIT
metadata:
  hermes:
    tags: [batch, image-generation, codex, oauth, pipeline, factory]
    related_skills: [image-gen, codex]
---

# image-gen2 — Batch Image Factory

대량 배치 이미지 생성 파이프라인. 프롬프트 템플릿 1개 + subject 목록을 주면,
subject만 치환해 수십~수백 장을 동시 생성하고 자동 검수·재시도한다.

**설계 출처:** 한국 Threads `@zarvan_kim` 파이프라인(GPT Pro 구독으로 하루
15000장)을 우리 환경(Codex OAuth)으로 이식. 4대 원칙:
1. **런타임 LLM 호출 0** — 토큰 절약의 핵심. 프롬프트는 템플릿 + subject 문자열
   치환만. 매번 LLM으로 프롬프트 생성하지 않는다. 템플릿 작성은 사람/1회성.
2. **동시 생성** — ThreadPoolExecutor, 기본 concurrency 4 (Codex 쿼터 보수적).
3. **2단계 검수 (cheap-first)** — 1차 기계검증(파일 존재 + 해상도/종횡비 +
   PNG 무결성 + 최소 크기), 통과 못한 것만 2차 vision 판정(옵션, 현재 스텁).
4. **재시도 전략** — attempt 1·2 = 원본 프롬프트, attempt 3 = 짧은 safety/clarity
   suffix 추가, 그래도 실패 → `failed.jsonl` 기록 후 넘어감.

## image-gen vs image-gen2

| | image-gen (단일) | image-gen2 (배치) |
|---|---|---|
| 출력 | 1장 | N장 (수십~수백) |
| 입력 | 프롬프트 1개 | 템플릿 1개 + subject 목록 |
| 검수 | 없음 (사람이 눈으로) | 자동 기계검증 (+옵션 vision) |
| 재시도 | 없음 | 자동 (기본 3회, attempt3 suffix) |
| 동시성 | 1 | 기본 4 (조정 가능) |
| 엔진 | gen_image.py | gen_image.py 재사용 (subprocess) |

## 엔진 재사용

새 도구를 설치하지 않는다. 단일 생성 엔진을 그대로 subprocess로 호출:

```
~/2lab.ai/skills/image-gen/scripts/gen_image.py
```

Codex/ChatGPT OAuth 세션 사용(API 키 불필요). 검수는 `identify`(imagemagick).

## 워크플로우

1. **템플릿 작성** — `{subject}` 슬롯 1개 포함. (1회성, LLM 안 씀)
2. **subject 목록 준비** — csv/json/txt 중 택1.
3. **batch_gen.py 실행**.
4. **검수/재시도 자동** — 기계검증 실패 시 자동 재시도.
5. **결과 확인** — out-dir의 PNG들 + `failed.jsonl`(실패분만 기록).
6. **텔레그램 전송** — 여러 장이면 대표 N장 또는 zip으로.

## 사용법

### 1. subject 목록 파일

- **txt**: 한 줄에 subject 하나 (`#` 주석/빈 줄 무시)
- **csv**: `subject` 헤더 컬럼, 없으면 첫 컬럼
- **json**: `["a","b"]` 또는 `[{"subject":"a", ...}]`

예 (`subjects.txt`):
```
cat
rocket
coffee cup
```

### 2. 배치 실행

```bash
python3 ~/2lab.ai/skills/image-gen2/scripts/batch_gen.py \
  --template "A minimalist flat icon of a {subject}, centered, white background, vector style" \
  --subjects ~/2lab.ai/skills/image-gen2/examples/subjects.txt \
  --out-dir /tmp/icons \
  --concurrency 4 \
  --size 1024x1024 \
  --quality high
```

템플릿을 파일에서 읽으려면 `--template-file path` 사용.

### 3. 프롬프트 빌더 단독 (dry-run, LLM 0 검증)

실제 생성 전 어떤 프롬프트/파일명이 나올지 미리 확인:

```bash
python3 ~/2lab.ai/skills/image-gen2/scripts/prompt_builder.py \
  --template "A flat icon of a {subject}" \
  --subjects examples/subjects.txt
```

## 파라미터

| 플래그 | 기본값 | 설명 |
|---|---|---|
| `--template` | (택1 필수) | `{subject}` 포함 템플릿 문자열 |
| `--template-file` | (택1 필수) | 템플릿 파일 경로 |
| `--subjects` | (필수) | subject 목록 (csv/json/txt) |
| `--out-dir` | (필수) | 출력 디렉토리 |
| `--concurrency` | `4` | 동시 생성 worker 수 |
| `--size` | `1024x1024` | 요청 해상도 (종횡비 검증에 사용) |
| `--quality` | `high` | `auto \| low \| medium \| high` |
| `--retries` | `3` | 최대 시도 횟수 |
| `--retry-suffix` | (기본 제공) | attempt 3에 붙는 safety/clarity 문구 |
| `--min-bytes` | `5120` | 최소 PNG 크기 (무결성 가드) |
| `--vision-check` | off | 2차 vision 검수 활성화 (현재 TODO 스텁) |

## 출력 파일명

`{인덱스}_{subject슬러그}.png` (예: `001_cat.png`, `003_coffee_cup.png`).
공백→`_`, 특수문자 제거.

## 결과

- 진행상황: stdout에 `[N/총M] OK/FAIL filename (attempts=K)`.
- 요약: 성공/실패 수, 출력 디렉토리, Codex 쿼터 마지막 값.
- `failed.jsonl`: 실패분만 `{subject, prompt, attempts, last_error, attempt_log}`.
  (실패 없으면 파일 생성 안 됨.)
- exit 0 = 전부 성공, 2 = 일부 실패.

## 토큰 절약 원칙 (핵심)

**런타임 LLM 호출 0.** 프롬프트 생성에 모델을 쓰지 않는다 — 순수 파이썬 문자열
치환. 이게 `@zarvan_kim` 파이프라인이 대량으로 돌릴 수 있던 이유. 템플릿
작성만 사람이 1회 하고, 나머지 N장은 치환+생성+검증만 반복.

## 트러블슈팅

### Codex 쿼터 80%↑ ⚠
stderr 쿼터 라인에 `⚠` 뜨면 5h 또는 7d 윈도우가 80% 넘은 것. concurrency를
낮추거나(예 `--concurrency 2`) 윈도우 리셋을 기다린다.

### token_expired / HTTP 401
OAuth access_token 만료. `codex login status`가 0을 반환해도 토큰 자체가
만료됐을 수 있음. 한 번 `codex exec --skip-git-repo-check "ok"`를 돌려
토큰을 갱신하거나 `codex logout && codex login`.

### 해상도가 요청과 다름
Codex 백엔드는 모델/플랜에 따라 `--size`를 정확히 지키지 않을 수 있다
(1024x1024 요청 → 1254x1254 반환). 그래서 검수는 픽셀 정확 일치가 아니라
**종횡비 일치 + 최소 크기**로 한다 (정상 동작).

### 실패 재처리
`failed.jsonl`의 subject만 새 목록 파일로 추려서 다시 batch_gen.py 실행.
concurrency를 낮추면 쿼터/타임아웃 실패가 줄 수 있다.

## 정직한 한계

- **vision 검수는 스텁(MVP).** `--vision-check`는 자리만 만들어져 있고 실제
  vision 판정은 TODO(`batch_gen.py: vision_verify`). 코어는 기계검증+재시도.
- **15000장 규모는 우리 환경에선 불가.** 원본은 GPT Pro 전용 쿼터. 우리는
  Codex 구독 쿼터(5h/7d 윈도우)에 묶여 있어 그만큼 못 뽑는다.
- **ToS 회색지대.** 구독 세션(OAuth)으로 대량 자동 호출하는 것은 OpenAI
  약관상 회색지대. 쿼터 한도 내에서 보수적으로 쓸 것.

## 크레딧

파이프라인 설계 출처: Threads `@zarvan_kim` (대량 이미지 생성 4원칙).
우리 환경(Codex OAuth + image-gen 엔진)으로 이식.

## Changelog

- **1.0.0** (2026-06-17): 초기 버전. prompt_builder(LLM 0) + batch_gen
  (동시 생성 + 기계검증 + 재시도 + failed.jsonl). vision 검수 스텁.
