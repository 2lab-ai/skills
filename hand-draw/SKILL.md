---
name: hand-draw
description: "100% hand-drawn image generation with Korean Hangul support. Zero font files — all characters rendered from manually-defined stroke primitives. Produces notebook-style illustrated cards with wobble effects. Actions: 손그림, 손글씨 이미지, hand-draw, 일러스트 만들어, 운동 이미지"
---
# Hand-Draw — 100% Font-Free Korean Illustration Engine

Generate hand-drawn style images with Korean text, stick figures, and decorative elements.
**No font files used at all** — every character (한글 + ASCII) rendered from stroke-level primitives.

## When to Use

- User requests hand-drawn / 손글씨 style images
- Exercise cards, study notes, cute illustrations
- Annotated diagrams with Korean + English text
- Any image where handwritten aesthetic is desired

## Architecture

```
scripts/
├── hangul_render.py   # Core: Hangul jamo stroke renderer + text API
└── draw_utils.py      # Wobble primitives, backgrounds, decorations
examples/
└── exercise_images.py # Full example: 6 exercise illustration cards
```

## Core Module: `hangul_render.py`

### How It Works

1. **Jamo Stroke Database**: All 19 initial consonants (ㄱ-ㅎ) and 21 medial vowels (ㅏ-ㅣ) defined as normalized polyline coordinates `[(x, y), ...]` in 0.0-1.0 space
2. **Unicode Decomposition**: `decompose_syllable('한')` → `(ㅎ, ㅏ, ㄴ)` via Unicode math: `code = 0xAC00 + (initial×21 + medial)×28 + final`
3. **Vowel Layout Detection**: `get_vowel_type()` → `'right'` (ㅏㅓㅣ), `'bottom'` (ㅗㅜㅡ), `'compound'` (ㅘㅝ)
4. **Syllable Block Composition**: Positions initial/medial/final jamo within bounding box based on vowel type
5. **Wobble Rendering**: All strokes subdivided into segments with random displacement for hand-drawn effect

### Key API

```python
from hangul_render import hand_write, hand_write_centered, hand_write_multiline

# Basic usage
img = Image.new("RGB", (600, 200), (255, 252, 245))
draw = ImageDraw.Draw(img)

# Write mixed Korean + ASCII text
hand_write(draw, x=20, y=30, text="안녕! Hello 123",
           color=(60, 60, 65), size=50, width=2, wobble_amt=1.5)

# Centered text
hand_write_centered(draw, cx=300, cy=100, text="가운데 정렬",
                    color=(225, 60, 75), size=40)

# Multi-line text
hand_write_multiline(draw, x=20, y=50, text="첫째 줄\n둘째 줄\n셋째 줄",
                     color=(60, 60, 65), size=30, line_spacing=1.4)
```

### Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| draw | ImageDraw | required | PIL ImageDraw object |
| x, y | int | required | Starting position |
| text | str | required | Korean + ASCII mixed text |
| color | tuple | required | RGB color, e.g. `(60, 60, 65)` |
| size | int | required | Character height in pixels |
| width | int | 2 | Stroke width |
| wobble_amt | float | 1.5 | Randomness for hand-drawn feel |

### Special Characters Supported

- **Korean**: All 11,172 syllable combinations (가-힣)
- **ASCII**: A-Z, a-z, 0-9
- **Symbols**: `! ? . , : ; / + - = * # @ % & ( ) [ ] ~ → ← ↑ ↓ " ' _ ♡ ★ ♪`

## Utility Module: `draw_utils.py`

### Primitives
```python
from draw_utils import wobble_line, wobble_rect, wobble_ellipse

wobble_line(draw, x1, y1, x2, y2, color, width)
wobble_rect(draw, x1, y1, x2, y2, color, width)
wobble_ellipse(draw, cx, cy, rx, ry, color, width)
```

### Decorations
```python
from draw_utils import hand_arrow, hand_heart, hand_star, hand_checkmark, hand_cross

hand_arrow(draw, x1, y1, x2, y2, color, width)
hand_heart(draw, cx, cy, size, color)
hand_star(draw, cx, cy, size, color)
hand_checkmark(draw, cx, cy, size, color)
hand_cross(draw, cx, cy, size, color)
hand_underline(draw, x, y, width_px, color)
```

### Backgrounds
```python
from draw_utils import draw_paper_bg, draw_grid_bg, draw_dot_bg

draw_paper_bg(img)      # Notebook paper with ruled lines + margin
draw_grid_bg(img)       # Graph paper grid
draw_dot_bg(img)        # Dot grid
```

### Stick Figure
```python
from draw_utils import stick_figure

stick_figure(draw, cx=200, cy=150, scale=1.2,
             arm_angle=45, leg_angle=30)
```

### Color Palette
```python
from draw_utils import PALETTE

PALETTE['bg']       # (255, 251, 243)  Warm paper
PALETTE['body']     # (60, 60, 65)     Dark text
PALETTE['accent']   # (225, 60, 75)    Red accent
PALETTE['accent2']  # (55, 125, 220)   Blue accent
PALETTE['green']    # (45, 165, 85)    Green
PALETTE['orange']   # (230, 140, 40)   Orange
PALETTE['pink']     # (235, 130, 160)  Pink
PALETTE['purple']   # (140, 80, 200)   Purple
PALETTE['machine']  # (148, 148, 158)  Gray
```

## Dependencies

- **Python 3.8+**
- **Pillow** (`pip install Pillow`)
- No font files needed (that's the whole point!)

## Example Usage

```bash
# Run the exercise card example
cd ~/2lab.ai/skills/hand-draw
python examples/exercise_images.py /tmp/my-output

# Quick test
python scripts/hangul_render.py  # Generates test_handwrite.png
```

## Design Philosophy

> "폰트 쓰지 말고 직접 써줘" — Every character is drawn stroke-by-stroke.

All text rendering happens through manually-defined stroke coordinates:
- Each consonant/vowel has its own polyline definition
- Unicode syllable decomposition handles 가-힣 automatically
- Wobble + jitter make each rendering unique
- No `.ttf`, `.otf`, or any font file is ever loaded

## Tips for Agents

1. Always `random.seed(N)` before generating for reproducible results
2. `size=30-50` works well for annotations, `size=20-25` for small notes
3. `width=3` for bold/emphasis, `width=2` for normal text
4. Use `draw_paper_bg()` first, then create `ImageDraw.Draw(img)` for content
5. Mix `hand_write` with `hand_heart` / `hand_star` for cute decorative style
