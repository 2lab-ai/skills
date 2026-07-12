---
name: photo-restyle
description: AI 사진 작가 에이전트 — 사용자가 레퍼런스 사진 몇 장을 주면 그 인물/스타일을 학습(in-context)해, 원하는 컨셉(배경/포즈/의상/구도)으로 새 사진을 생성한다. 엔진은 image-gen 스킬(Codex OAuth, image-to-image). 트리거: "이런 사진 만들어줘", "내 사진으로 컨셉 사진", "사진 작가", "레퍼런스 사진 주면", photo-restyle.
version: 1.0.0
author: Elon (p9)
license: MIT
metadata:
  hermes:
    tags: [image-generation, image-to-image, photography, restyle, codex, creative]
    related_skills: [image-gen, sns-scraping]
---

# photo-restyle — AI 사진 작가 에이전트

레퍼런스 사진을 받아 **그 인물/피사체를 유지한 채** 새로운 컨셉으로 사진을 생성한다.
파인튜닝이 아니라 **in-context image-to-image** (레퍼런스를 입력 이미지로 함께 보냄).

엔진: [`image-gen`](../image-gen/SKILL.md) 스킬의 `gen_image.py` (Codex/ChatGPT OAuth, API 키 불필요).
이 스킬은 그 위에 **(1) 레퍼런스 분석 → (2) 컨셉 인터뷰 → (3) 프롬프트 합성 → (4) 생성 → (5) 전송**
워크플로우를 얹은 것이다.

---

## 언제 쓰나

- 지혁이 **사진 1장 이상을 첨부**하고 "이런 느낌으로", "컨셉 사진 만들어줘", "프로필 사진" 등을 요청
- 인물 사진의 **얼굴/정체성은 유지**하되 배경·의상·조명·구도를 바꾸고 싶을 때
- 여러 장의 레퍼런스(같은 인물 여러 각도 / 인물 + 스타일 레퍼런스)를 종합하고 싶을 때

text-to-image(레퍼런스 없이 프롬프트만)면 이 스킬 말고 `image-gen`을 직접 써라.

---

## 전제조건

```bash
codex login status   # ChatGPT/OAuth (구독 기반)여야 함. API-key 모드면 codex logout && codex login
```

레퍼런스 이미지는 PNG/JPG/JPEG/WEBP/GIF. 절대경로 권장.
지혁이 텔레그램으로 보낸 사진은 보통 `/tmp/`에 떨어진다 — 경로 확인 후 사용.

---

## 워크플로우 (5단계)

### 1. 레퍼런스 수집 + 분석 (Vision)

지혁이 보낸 사진 파일들을 모은다(한 디렉토리에 두면 wrapper가 편하다). 각 사진을 **Read 툴로 직접 보고**(멀티모달) 다음을 추출한다 — 추측 금지, 보이는 것만:

- **피사체**: 인물 수, 성별/연령대 인상, 얼굴 특징(유지해야 할 핵심)
- **조명**: 자연광/스튜디오/역광/골든아워, 하드 vs 소프트
- **색감/톤**: 따뜻/차가움, 채도, 필름룩 여부
- **구도/렌즈**: 클로즈업/반신/전신, 배경 흐림(보케=망원 인상), 광각 왜곡
- **분위기**: 무드, 의상 스타일, 배경 종류

분석 결과를 지혁에게 2-4줄로 요약해 보여준다(내가 뭘 봤는지 합의).

### 2. 컨셉 인터뷰

지혁이 이미 컨셉을 명시했으면 스킵. 아니면 **UIAskUserQuestion(user_choices)** 으로 묻는다.
핵심 5축 — 모르면 묻고, 명시됐으면 그대로 쓴다:

1. **배경/장소** (예: 카페, 도심 야경, 스튜디오 단색, 자연)
2. **의상** (예: 캐주얼, 정장, 코트, 한복)
3. **포즈/표정** (예: 정면 미소, 측면 응시, 걷는 동작)
4. **구도** (예: 얼굴 클로즈업, 상반신, 전신)
5. **무드/조명** (예: 시네마틱 85mm, 골든아워, 흑백)

추가 옵션: 사이즈(세로 1024x1536 / 가로 1536x1024 / 정사각 1024x1024), 장수.

### 3. 프롬프트 합성

레퍼런스 분석 + 컨셉을 영어 프롬프트로 합친다. **얼굴 유지 지시를 명시**:

```
Keep the same person and facial identity as the reference image(s).
Restyle into: <컨셉>. <조명/렌즈/무드>. Photorealistic, high detail.
```

예:
```
Keep the same woman and her facial identity from the reference photos.
Restyle into a cozy autumn cafe by a rain-streaked window, cream knit sweater,
soft relaxed half-smile, upper-body framing, cinematic 85mm portrait,
warm golden interior light, shallow depth of field. Photorealistic.
```

### 4. 생성

wrapper로 레퍼런스를 한 번에 첨부한다:

```bash
~/2lab.ai/skills/photo-restyle/scripts/restyle.sh \
  -p "Keep the same person... Restyle into ... Photorealistic." \
  -r /tmp/refs_dir \
  -o /tmp/restyle_out.png \
  --size 1024x1536 --quality high
```

또는 파일을 개별 지정(여러 -r 반복 가능, 디렉토리/파일 혼용 가능):

```bash
~/2lab.ai/skills/photo-restyle/scripts/restyle.sh \
  -p "Put the subject from the portraits into the style of the last image." \
  -r /tmp/face1.jpg -r /tmp/face2.jpg -r /tmp/style_ref.png \
  -o /tmp/restyle_out.png
```

- `restyle.sh`는 디렉토리면 그 안의 모든 이미지를 `--input-image`로 자동 첨부하고,
  `gen_image.py`가 레퍼런스 존재 시 자동으로 `action=edit`(image-to-image)로 전환한다.
- stderr에 Codex 쿼터(`[Codex PRO] | 5h: x% | 7d: y%`)가 찍힌다 — 80%↑면 ⚠. 쿼터 확인할 것.
- **여러 장 요청** = 프롬프트 변형(다른 컨셉/구도)으로 restyle.sh를 N번 호출. 한 호출은 1장.

### 5. 전송

생성된 PNG를 텔레그램으로 보낸다:

```
mcp__send-file__send_photo  filePath=/tmp/restyle_out.png  caption="<컨셉 한 줄>"
```

큰 파일/여러 장 묶음이면 `send_document`도 가능. 생성 후 산출물 경로를 지혁에게 알린다.

---

## 아카이브 (선택)

자주 쓰는 인물/컨셉이면 레퍼런스와 결과를 보관:
`~/2lab.ai/soul/p9/ARTIFACTS/photo-restyle/<subject>/`

---

## 비판적 주의 (Fact Discipline)

- **"학습"은 파인튜닝이 아니다.** in-context 레퍼런싱이다 — 결과가 레퍼런스와 다르면 "학습 실패"가
  아니라 프롬프트/레퍼런스 품질 문제. 과장 어휘("AI가 너를 학습했어") 쓰지 말 것.
- **얼굴 일관성은 보장 안 된다.** gpt-image류는 동일 인물을 완벽 재현하지 못할 수 있다.
  결과가 닮지 않으면 솔직히 말하고, 레퍼런스를 더 받거나 프롬프트에 얼굴 디테일을 추가해 재시도.
- **동의 없는 인물 사진 생성 금지.** 지혁 본인/동의된 인물만. 타인 deepfake 요청은 거절.
- 생성 실패(`No image_generation_call result found`) 시 `--events /tmp/ev.jsonl`로 원인 확인
  (image-gen Troubleshooting 참조).

---

## 트러블슈팅

| 증상 | 대응 |
|---|---|
| `codex login status` API-key 모드 | `codex logout && codex login` |
| 얼굴이 안 닮음 | 레퍼런스 더 첨부 / 프롬프트에 "keep exact facial identity" 강조 / 정면 고해상 레퍼런스 사용 |
| 텔레그램 사진이 경로에 없음 | 첨부 파일 실제 경로 확인(보통 `/tmp/`), 절대경로로 `-r` 지정 |
| 투명 배경 실패 | `--background opaque` |
| 쿼터 ⚠ 80%↑ | 생성 미루거나 장수 줄이기 |

---

## Changelog

- **1.0.0** (2026-06-14): 초기 버전. image-gen 위에 레퍼런스 분석→인터뷰→생성→전송 워크플로우 + `restyle.sh` 멀티 레퍼런스 wrapper. (영감: @masonjunlee Threads 사진 작가 에이전트 컨셉.)
