# cwon (채원) — Voice & Visual Reference

## Audio reference
- `reference.mp3` — 15–20s clean Korean prompt audio
- `reference.txt` — matching transcript (Hangul)

## Visual reference
- `reference.jpg` — hero persona photo

**Persona description** (for `gen_image.py --input-image reference.jpg`):
> 20대 한국 여성, 어깨 길이 검은 생머리 + 앞머리, 따뜻하고 전문적인 분위기.
> 기본 스타일: 오버사이즈 회색 핀스트라이프 블레이저 위 흰 리브 탱크,
> 또는 크림 캐시미어 터틀넥. 미니멀 골드 액세서리.
> 배경: 바우하우스 + 미드센추리 모던 서울 아파트, Eames 라운지,
> 월넛 책장, 부드러운 오후 햇살. 시네마틱 85mm 포트레이트.

## Using as image-gen reference

Text→image (persona from scratch):
```bash
python3 ~/2lab.ai/skills/image-gen/scripts/gen_image.py \
  "chaewon in a warm Seoul apartment, cinematic 85mm portrait" \
  -o /tmp/chaewon.png
```

Image→image (use the stored reference to keep face/styling):
```bash
python3 ~/2lab.ai/skills/image-gen/scripts/gen_image.py \
  "Keep this woman's face. Place her holding an open book in a bauhaus + mid-century modern library nook, warm afternoon light, 85mm cinematic." \
  --input-image ~/2lab.ai/skills/fish-tts/voices/cwon/reference.jpg \
  -o /tmp/chaewon_reading.png
```

## Use inside docent-audiobook

When a scene needs a chaewon (narrator) cutaway B-roll, pass `reference.jpg`
as `--input-image` to keep the face consistent across all docent-book videos.

See `~/2lab.ai/skills/docent-audiobook/SKILL.md` → "B-roll Image Generation".
