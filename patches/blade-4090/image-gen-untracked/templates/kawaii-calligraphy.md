# Kawaii Calligraphy Template

Threads `@xiaochou.chou` 스타일 — **귀여운 치비 캐릭터 + 큰 동양 서예 문구** 조합. 흰 배경에 수채화 일러스트 + 붓글씨가 나란히 놓이는 미니멀 포맷.

원본 출처: https://www.threads.com/@xiaochou.chou/post/DYSYSG3Gbqq

---

## 프롬프트 템플릿 (영어, GPT image 권장)

```
A minimalist illustration on a clean {bg_color} background, vertical {aspect} portrait composition.

LEFT side (~35% of canvas, vertically centered): a single cute chibi {animal}, {animal_description},
soft watercolor and ink wash technique, rounded organic shapes, gentle pastel colors,
no harsh outlines, small adorable scale, slightly off-center, leaving generous whitespace around it.
Optional tiny prop: {prop}.

RIGHT side (~55% of canvas): large vertical {language} calligraphy reading "{phrase}",
traditional {brush_style} brush style, jet-black sumi ink, fluid expressive strokes with natural
ink variations (dry brush texture, occasional bleeding edges), slightly imperfect organic feel.
Characters stacked vertically OR arranged in 2 columns depending on length.
Calligraphy is the visual anchor — bold and confident.

Mood: serene, contemplative, warm. NO borders, NO signature, NO watermark, NO frame.
NO extra text or English captions. NO other illustrations besides the single chibi.
Pure background with soft paper texture acceptable.

Style reference: kawaii Japanese stationery illustration meets traditional East Asian 書法/서예/書道,
similar to Xiaohongshu/Threads minimalist character + phrase posts (2024-2026 trend).
```

---

## 변수 슬롯

| 슬롯 | 설명 | 예시 |
|---|---|---|
| `{bg_color}` | 배경색 | `pure white`, `warm cream`, `soft beige`, `pale rice paper` |
| `{aspect}` | 종횡비 | `2:3` (인스타/스레드), `9:16` (스토리), `1:1` (피드) |
| `{animal}` | 메인 캐릭터 | `shiba inu puppy`, `panda cub`, `bunny`, `capybara`, `kitten`, `gosling`, `dumpling-shaped bird` |
| `{animal_description}` | 캐릭터 디테일 | `fluffy beige fur with white belly`, `tiny pink cheeks`, `closed sleepy eyes` |
| `{prop}` | 작은 소품 (선택) | `holding a tiny rice ball`, `with a small steaming teacup`, `sitting on a maple leaf`, `none` |
| `{language}` | 서예 언어 | `Chinese (Traditional)`, `Korean Hangul`, `Japanese Kanji/Hiragana` |
| `{phrase}` | 문구 | (아래 표 참고) |
| `{brush_style}` | 붓 스타일 | Chinese: `行書 semi-cursive`, `楷書 regular` / Korean: `한글 정자체 hangul calligraphy`, `흘림체` / Japanese: `行書`, `かな書道` |

---

## 추천 문구 (언어별)

### 한국어 (Korean)
- `오늘도 수고했어` — Good work today
- `천천히 가도 괜찮아` — It's OK to go slowly
- `잘 자` — Sleep well
- `너는 너로 충분해` — You are enough as you are
- `한 번 더, 딱 한 번만` — One more time, just once more
- `같이 가자` — Let's go together

### 중국어 (Chinese, 繁體)
- `今天也辛苦了` — Good work today too
- `慢慢來` — Take it slow
- `晚安` — Good night
- `你已經很棒了` — You're already amazing
- `沒事的` — It's OK
- `深呼吸` — Deep breath

### 일본어 (Japanese)
- `今日もお疲れさま` — Good work today
- `だいじょうぶ` — It's OK (hiragana, softer)
- `おやすみ` — Good night
- `がんばらなくていい` — You don't have to try hard
- `そのままでいい` — Stay as you are

---

## 사용법 (CLI)

```bash
# 변수 치환은 셸 변수 또는 직접 편집으로
python3 ~/2lab.ai/skills/image-gen/scripts/gen_image.py \
  "$(cat <<'EOF'
[위 프롬프트 템플릿 + 슬롯 채운 내용]
EOF
)" \
  --size 1024x1536 \
  --quality high \
  -o ~/output/kawaii-cal-001.png
```

### 빠른 예시 — 한국어 시바견

```bash
python3 ~/2lab.ai/skills/image-gen/scripts/gen_image.py \
  "A minimalist illustration on a pure white background, vertical 2:3 portrait composition.
LEFT side (~35% of canvas, vertically centered): a single cute chibi shiba inu puppy, fluffy beige fur with white belly and cheeks, tiny closed sleepy eyes, sitting with paws tucked under, soft watercolor and ink wash technique, rounded organic shapes, gentle pastel coloring, no harsh outlines, small adorable scale, generous whitespace around it.
RIGHT side (~55% of canvas): large vertical Korean Hangul calligraphy reading '오늘도 수고했어', traditional 흘림체 brush style, jet-black sumi ink, fluid expressive strokes with natural ink variations, slightly imperfect organic feel. Characters arranged in 2 vertical columns.
Mood: serene, warm. NO borders, NO signature, NO watermark. Pure white with subtle paper texture." \
  --size 1024x1536 --quality high \
  -o ~/output/kawaii-shiba-ko.png
```

---

## 팁

1. **언어 일관성**: 한 이미지 안에 한자+한글+영문 섞이면 GPT image 가 자주 혼동함. 한 언어만 명시.
2. **글자 수 ≤ 8자**: 길어지면 글자 모양이 깨짐. 7~8자가 sweet spot.
3. **캐릭터 단순화**: "single chibi X" 처럼 한 개체만. 여러 캐릭터 요청하면 분포가 어색해짐.
4. **quality=high 권장**: medium 으로는 붓글씨 획이 흐릿함.
5. **반복 생성**: gpt-image 는 한국어/중국어 글자를 90%만 정확히 렌더링 — 처음 시도가 어그러지면 동일 프롬프트로 2~3회 재생성.
6. **iterate 로 글자 수정**: 글자가 틀리게 나오면 `--input-image <첫_결과> --action edit` 로 "Replace the calligraphy text to read '...'" 지시.

---

## 변형 아이디어

- **밤 버전**: 배경 `deep indigo with subtle stars`, 흰 글씨 (서예 흰색 잉크), 캐릭터에 약간의 노란 빛
- **계절 버전**: `with falling cherry petals` / `with autumn maple leaf falling` 추가
- **시리즈 일관성**: 같은 캐릭터(예: 시바견) + 다른 문구로 7장 → 주간 카드 세트
- **인사 시리즈**: 월~일 요일별 다른 문구 ("월요일이지만 괜찮아" 등)
