#!/usr/bin/env python3
"""
TRULY hand-drawn Korean Hangul renderer.
NO FONT FILES USED AT ALL.
Each jamo (자모) stroke defined manually as line segments.
Syllables decomposed via Unicode, jamo composed into blocks, drawn with wobble.

Usage:
    from hangul_render import hand_write, wobble_circle, wobble_stroke

    img = Image.new("RGB", (600, 200), (255, 252, 245))
    draw = ImageDraw.Draw(img)
    hand_write(draw, 20, 30, "안녕하세요!", (60, 60, 65), 50, width=2)
"""

from PIL import Image, ImageDraw
import math
import random

# ═══════════════════════════════════════════════
# JAMO STROKE DEFINITIONS
# Each jamo = list of strokes
# Each stroke = list of (x, y) points (0.0-1.0 normalized)
# Connected by lines in sequence
# ═══════════════════════════════════════════════

INITIAL_CONSONANTS = [
    'ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'
]
MEDIAL_VOWELS = [
    'ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ'
]
FINAL_CONSONANTS = [
    '','ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ','ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'
]

# Vowels that go to the RIGHT of the consonant (vertical vowels)
RIGHT_VOWELS = {'ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅣ'}
# Vowels that go BELOW the consonant (horizontal vowels)
BOTTOM_VOWELS = {'ㅗ','ㅛ','ㅜ','ㅠ','ㅡ'}
# Compound vowels (right + bottom)
COMPOUND_VOWELS = {'ㅘ','ㅙ','ㅚ','ㅝ','ㅞ','ㅟ','ㅢ'}


def define_jamo_strokes():
    """Define stroke paths for each jamo. Each stroke is a polyline [(x,y), ...]."""
    s = {}

    # ═══ CONSONANTS ═══
    # ㄱ (giyeok)
    s['ㄱ'] = [
        [(0.15, 0.2), (0.85, 0.2)],  # top horizontal
        [(0.85, 0.2), (0.85, 0.85)],  # right vertical down
    ]
    # ㄲ (ssang giyeok)
    s['ㄲ'] = [
        [(0.1, 0.2), (0.45, 0.2)], [(0.45, 0.2), (0.45, 0.85)],
        [(0.55, 0.2), (0.9, 0.2)], [(0.9, 0.2), (0.9, 0.85)],
    ]
    # ㄴ (nieun)
    s['ㄴ'] = [
        [(0.2, 0.15), (0.2, 0.8)],   # left vertical down
        [(0.2, 0.8), (0.85, 0.8)],    # bottom horizontal
    ]
    # ㄷ (digeut)
    s['ㄷ'] = [
        [(0.2, 0.2), (0.8, 0.2)],    # top horizontal
        [(0.2, 0.2), (0.2, 0.8)],    # left vertical
        [(0.2, 0.8), (0.8, 0.8)],    # bottom horizontal
    ]
    # ㄸ (ssang digeut)
    s['ㄸ'] = [
        [(0.05, 0.2), (0.45, 0.2)], [(0.05, 0.2), (0.05, 0.8)], [(0.05, 0.8), (0.45, 0.8)],
        [(0.55, 0.2), (0.95, 0.2)], [(0.55, 0.2), (0.55, 0.8)], [(0.55, 0.8), (0.95, 0.8)],
    ]
    # ㄹ (rieul) - zigzag
    s['ㄹ'] = [
        [(0.15, 0.15), (0.85, 0.15)],  # top
        [(0.85, 0.15), (0.85, 0.38)],   # right down
        [(0.85, 0.38), (0.15, 0.38)],   # middle left
        [(0.15, 0.38), (0.15, 0.62)],   # left down
        [(0.15, 0.62), (0.85, 0.62)],   # middle right
        [(0.85, 0.62), (0.85, 0.85)],   # right down
        [(0.15, 0.85), (0.85, 0.85)],   # bottom
    ]
    # ㅁ (mieum) - square
    s['ㅁ'] = [
        [(0.2, 0.2), (0.8, 0.2)],
        [(0.8, 0.2), (0.8, 0.8)],
        [(0.8, 0.8), (0.2, 0.8)],
        [(0.2, 0.8), (0.2, 0.2)],
    ]
    # ㅂ (bieup)
    s['ㅂ'] = [
        [(0.2, 0.1), (0.2, 0.75)],   # left vertical
        [(0.8, 0.1), (0.8, 0.75)],   # right vertical
        [(0.2, 0.45), (0.8, 0.45)],  # middle horizontal
        [(0.2, 0.75), (0.8, 0.75)],  # bottom horizontal
        [(0.5, 0.75), (0.5, 0.9)],   # bottom center tick
    ]
    # ㅃ (ssang bieup)
    s['ㅃ'] = s['ㅂ']  # simplified
    # ㅅ (siot) - inverted V / tent
    s['ㅅ'] = [
        [(0.5, 0.15), (0.15, 0.85)],  # left diagonal
        [(0.5, 0.15), (0.85, 0.85)],  # right diagonal
    ]
    # ㅆ (ssang siot)
    s['ㅆ'] = [
        [(0.35, 0.15), (0.1, 0.85)], [(0.35, 0.15), (0.5, 0.85)],
        [(0.65, 0.15), (0.5, 0.85)], [(0.65, 0.15), (0.9, 0.85)],
    ]
    # ㅇ (ieung) - circle
    s['ㅇ'] = 'circle'
    # ㅈ (jieut) - siot + top line
    s['ㅈ'] = [
        [(0.2, 0.15), (0.8, 0.15)],   # top horizontal
        [(0.5, 0.3), (0.15, 0.85)],    # left diagonal
        [(0.5, 0.3), (0.85, 0.85)],    # right diagonal
    ]
    # ㅉ (ssang jieut)
    s['ㅉ'] = s['ㅈ']
    # ㅊ (chieut)
    s['ㅊ'] = [
        [(0.45, 0.05), (0.55, 0.05)],  # top dot/stroke
        [(0.2, 0.2), (0.8, 0.2)],      # horizontal
        [(0.5, 0.35), (0.15, 0.85)],
        [(0.5, 0.35), (0.85, 0.85)],
    ]
    # ㅋ (kieuk)
    s['ㅋ'] = [
        [(0.15, 0.2), (0.85, 0.2)],   # top horizontal
        [(0.15, 0.5), (0.85, 0.5)],   # middle horizontal
        [(0.85, 0.2), (0.85, 0.85)],  # right vertical
    ]
    # ㅌ (tieut)
    s['ㅌ'] = [
        [(0.2, 0.15), (0.8, 0.15)],   # top
        [(0.2, 0.15), (0.2, 0.85)],   # left vertical
        [(0.2, 0.5), (0.8, 0.5)],     # middle
        [(0.2, 0.85), (0.8, 0.85)],   # bottom
    ]
    # ㅍ (pieup)
    s['ㅍ'] = [
        [(0.2, 0.15), (0.2, 0.85)],   # left
        [(0.8, 0.15), (0.8, 0.85)],   # right
        [(0.2, 0.35), (0.8, 0.35)],   # top middle
        [(0.2, 0.65), (0.8, 0.65)],   # bottom middle
        [(0.2, 0.85), (0.8, 0.85)],   # bottom
    ]
    # ㅎ (hieut)
    s['ㅎ'] = [
        [(0.35, 0.08), (0.65, 0.08)],  # top stroke
        [(0.2, 0.28), (0.8, 0.28)],    # horizontal bar
        'circle_lower',                 # circle in lower half
    ]

    # ═══ VOWELS ═══
    # ㅏ (a) - vertical + short right tick
    s['ㅏ'] = [
        [(0.3, 0.05), (0.3, 0.95)],   # vertical line
        [(0.3, 0.45), (0.85, 0.45)],   # horizontal tick right
    ]
    # ㅐ (ae)
    s['ㅐ'] = [
        [(0.2, 0.05), (0.2, 0.95)],
        [(0.2, 0.45), (0.6, 0.45)],
        [(0.7, 0.05), (0.7, 0.95)],
    ]
    # ㅑ (ya)
    s['ㅑ'] = [
        [(0.25, 0.05), (0.25, 0.95)],
        [(0.25, 0.35), (0.85, 0.35)],
        [(0.25, 0.6), (0.85, 0.6)],
    ]
    # ㅒ (yae)
    s['ㅒ'] = s['ㅐ']
    # ㅓ (eo) - vertical + short left tick
    s['ㅓ'] = [
        [(0.7, 0.05), (0.7, 0.95)],
        [(0.15, 0.45), (0.7, 0.45)],
    ]
    # ㅔ (e)
    s['ㅔ'] = [
        [(0.3, 0.05), (0.3, 0.95)],
        [(0.3, 0.45), (0.7, 0.45)],
        [(0.8, 0.05), (0.8, 0.95)],
    ]
    # ㅕ (yeo)
    s['ㅕ'] = [
        [(0.7, 0.05), (0.7, 0.95)],
        [(0.15, 0.35), (0.7, 0.35)],
        [(0.15, 0.6), (0.7, 0.6)],
    ]
    # ㅖ (ye)
    s['ㅖ'] = s['ㅔ']
    # ㅗ (o) - horizontal + short up tick
    s['ㅗ'] = [
        [(0.05, 0.65), (0.95, 0.65)],
        [(0.5, 0.15), (0.5, 0.65)],
    ]
    # ㅘ (wa)
    s['ㅘ'] = [
        [(0.05, 0.6), (0.55, 0.6)],
        [(0.3, 0.15), (0.3, 0.6)],
        [(0.65, 0.05), (0.65, 0.95)],
        [(0.65, 0.45), (0.95, 0.45)],
    ]
    # ㅙ (wae)
    s['ㅙ'] = s['ㅘ']
    # ㅚ (oe)
    s['ㅚ'] = [
        [(0.05, 0.6), (0.55, 0.6)],
        [(0.3, 0.15), (0.3, 0.6)],
        [(0.75, 0.05), (0.75, 0.95)],
    ]
    # ㅛ (yo)
    s['ㅛ'] = [
        [(0.05, 0.65), (0.95, 0.65)],
        [(0.35, 0.15), (0.35, 0.65)],
        [(0.65, 0.15), (0.65, 0.65)],
    ]
    # ㅜ (u) - horizontal + short down tick
    s['ㅜ'] = [
        [(0.05, 0.35), (0.95, 0.35)],
        [(0.5, 0.35), (0.5, 0.9)],
    ]
    # ㅝ (wo)
    s['ㅝ'] = [
        [(0.05, 0.35), (0.55, 0.35)],
        [(0.3, 0.35), (0.3, 0.85)],
        [(0.65, 0.05), (0.65, 0.95)],
        [(0.15, 0.5), (0.65, 0.5)],
    ]
    # ㅞ (we)
    s['ㅞ'] = s['ㅝ']
    # ㅟ (wi)
    s['ㅟ'] = [
        [(0.05, 0.35), (0.55, 0.35)],
        [(0.3, 0.35), (0.3, 0.85)],
        [(0.75, 0.05), (0.75, 0.95)],
    ]
    # ㅠ (yu)
    s['ㅠ'] = [
        [(0.05, 0.35), (0.95, 0.35)],
        [(0.35, 0.35), (0.35, 0.9)],
        [(0.65, 0.35), (0.65, 0.9)],
    ]
    # ㅡ (eu) - just horizontal
    s['ㅡ'] = [
        [(0.05, 0.5), (0.95, 0.5)],
    ]
    # ㅢ (ui)
    s['ㅢ'] = [
        [(0.05, 0.4), (0.55, 0.4)],
        [(0.75, 0.05), (0.75, 0.95)],
    ]
    # ㅣ (i) - just vertical
    s['ㅣ'] = [
        [(0.5, 0.05), (0.5, 0.95)],
    ]

    return s


JAMO_STROKES = define_jamo_strokes()


def decompose_syllable(ch):
    """Decompose a Korean syllable into (initial, medial, final) jamo indices."""
    code = ord(ch)
    if code < 0xAC00 or code > 0xD7A3:
        return None
    offset = code - 0xAC00
    final_idx = offset % 28
    offset = offset // 28
    medial_idx = offset % 21
    initial_idx = offset // 21
    return initial_idx, medial_idx, final_idx


def get_vowel_type(medial_idx):
    """Determine if vowel goes right, bottom, or compound."""
    v = MEDIAL_VOWELS[medial_idx]
    if v in RIGHT_VOWELS:
        return 'right'
    elif v in BOTTOM_VOWELS:
        return 'bottom'
    else:
        return 'compound'


def wobble_stroke(draw, points, x, y, w, h, color, width, wobble_amt=2.0):
    """Draw a wobbly polyline, scaled to (x, y, w, h) bounding box."""
    scaled = []
    for px, py in points:
        sx = x + px * w + random.uniform(-wobble_amt, wobble_amt)
        sy = y + py * h + random.uniform(-wobble_amt, wobble_amt)
        scaled.append((sx, sy))

    for i in range(len(scaled) - 1):
        # Subdivide for more natural wobble
        x1, y1 = scaled[i]
        x2, y2 = scaled[i + 1]
        segs = max(3, int(math.hypot(x2-x1, y2-y1) / 8))
        prev = (x1, y1)
        for j in range(1, segs + 1):
            t = j / segs
            nx = x1 + (x2-x1)*t + random.uniform(-wobble_amt*0.5, wobble_amt*0.5)
            ny = y1 + (y2-y1)*t + random.uniform(-wobble_amt*0.5, wobble_amt*0.5)
            draw.line([prev, (nx, ny)], fill=color, width=width)
            prev = (nx, ny)


def wobble_circle(draw, cx, cy, r, color, width, wobble_amt=2.0):
    """Draw a wobbly circle."""
    pts = []
    n = 24
    for i in range(n + 2):
        angle = 2 * math.pi * i / n
        px = cx + r * math.cos(angle) + random.uniform(-wobble_amt, wobble_amt)
        py = cy + r * math.sin(angle) + random.uniform(-wobble_amt, wobble_amt)
        pts.append((px, py))
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i+1]], fill=color, width=width)


def draw_jamo(draw, jamo_char, x, y, w, h, color, width=2, wobble_amt=1.5):
    """Draw a single jamo character in the given bounding box."""
    strokes = JAMO_STROKES.get(jamo_char)
    if strokes is None:
        return

    if strokes == 'circle':
        wobble_circle(draw, x + w*0.5, y + h*0.5, min(w, h)*0.38, color, width, wobble_amt)
        return

    for stroke in strokes:
        if stroke == 'circle_lower':
            wobble_circle(draw, x + w*0.5, y + h*0.65, min(w, h)*0.25, color, width, wobble_amt)
        elif isinstance(stroke, list):
            wobble_stroke(draw, stroke, x, y, w, h, color, width, wobble_amt)


def draw_syllable(draw, ch, x, y, size, color, width=2, wobble_amt=1.5):
    """Draw a complete Korean syllable at (x, y) with given size."""
    result = decompose_syllable(ch)
    if result is None:
        return size * 0.5

    initial_idx, medial_idx, final_idx = result
    initial = INITIAL_CONSONANTS[initial_idx]
    medial = MEDIAL_VOWELS[medial_idx]
    has_final = final_idx > 0
    final = FINAL_CONSONANTS[final_idx] if has_final else None

    vtype = get_vowel_type(medial_idx)
    s = size
    pad = s * 0.05

    if vtype == 'right':
        if has_final:
            # Top-left: initial, Top-right: vowel, Bottom: final
            cw = s * 0.48; ch_c = s * 0.52
            vw = s * 0.42; vh = s * 0.52
            draw_jamo(draw, initial, x+pad, y+pad, cw, ch_c, color, width, wobble_amt)
            draw_jamo(draw, medial, x+cw+pad, y+pad, vw, vh, color, width, wobble_amt)
            if final:
                draw_jamo(draw, final, x+pad, y+ch_c+pad*2, s*0.85, s*0.35, color, width, wobble_amt)
        else:
            # Left: initial, Right: vowel
            cw = s * 0.48; ch_c = s * 0.8
            vw = s * 0.42; vh = s * 0.8
            draw_jamo(draw, initial, x+pad, y+pad, cw, ch_c, color, width, wobble_amt)
            draw_jamo(draw, medial, x+cw+pad, y+pad, vw, vh, color, width, wobble_amt)

    elif vtype == 'bottom':
        if has_final:
            # Top: initial, Middle: vowel, Bottom: final
            draw_jamo(draw, initial, x+pad+s*0.1, y+pad, s*0.7, s*0.35, color, width, wobble_amt)
            draw_jamo(draw, medial, x+pad, y+s*0.33, s*0.9, s*0.3, color, width, wobble_amt)
            if final:
                draw_jamo(draw, final, x+pad+s*0.1, y+s*0.62, s*0.7, s*0.32, color, width, wobble_amt)
        else:
            # Top: initial, Bottom: vowel
            draw_jamo(draw, initial, x+pad+s*0.1, y+pad, s*0.7, s*0.45, color, width, wobble_amt)
            draw_jamo(draw, medial, x+pad, y+s*0.45, s*0.9, s*0.45, color, width, wobble_amt)

    elif vtype == 'compound':
        if has_final:
            draw_jamo(draw, initial, x+pad, y+pad, s*0.4, s*0.45, color, width, wobble_amt)
            draw_jamo(draw, medial, x+pad, y+pad, s*0.9, s*0.58, color, width, wobble_amt)
            if final:
                draw_jamo(draw, final, x+pad+s*0.1, y+s*0.6, s*0.7, s*0.34, color, width, wobble_amt)
        else:
            draw_jamo(draw, initial, x+pad, y+pad, s*0.4, s*0.55, color, width, wobble_amt)
            draw_jamo(draw, medial, x+pad, y+pad, s*0.9, s*0.85, color, width, wobble_amt)

    return s


def draw_ascii_char(draw, ch, x, y, size, color, width=2, wobble_amt=1.5):
    """Draw basic ASCII characters (numbers, symbols) by hand."""
    s = size
    strokes = {
        '0': [[(0.2,0.1),(0.8,0.1),(0.8,0.9),(0.2,0.9),(0.2,0.1)]],
        '1': [[(0.4,0.1),(0.5,0.1),(0.5,0.9)], [(0.3,0.9),(0.7,0.9)]],
        '2': [[(0.2,0.2),(0.5,0.1),(0.8,0.2),(0.8,0.4),(0.2,0.9),(0.8,0.9)]],
        '3': [[(0.2,0.1),(0.8,0.1),(0.8,0.45),(0.4,0.45)],[(0.8,0.45),(0.8,0.9),(0.2,0.9)]],
        '4': [[(0.7,0.9),(0.7,0.1),(0.15,0.6),(0.85,0.6)]],
        '5': [[(0.8,0.1),(0.2,0.1),(0.2,0.45),(0.7,0.45),(0.8,0.65),(0.7,0.9),(0.2,0.9)]],
        '6': [[(0.7,0.1),(0.3,0.1),(0.2,0.5),(0.2,0.9),(0.8,0.9),(0.8,0.5),(0.2,0.5)]],
        '7': [[(0.2,0.1),(0.8,0.1),(0.5,0.9)]],
        '8': [[(0.5,0.1),(0.2,0.1),(0.2,0.45),(0.8,0.45),(0.8,0.1),(0.5,0.1)],
              [(0.2,0.45),(0.2,0.9),(0.8,0.9),(0.8,0.45)]],
        '9': [[(0.8,0.5),(0.2,0.5),(0.2,0.1),(0.8,0.1),(0.8,0.5),(0.8,0.9),(0.3,0.9)]],
        '/': [[(0.8,0.1),(0.2,0.9)]],
        '.': [[(0.45,0.8),(0.55,0.8),(0.55,0.9),(0.45,0.9)]],
        ',': [[(0.45,0.75),(0.5,0.85),(0.42,0.95)]],
        '-': [[(0.2,0.5),(0.8,0.5)]],
        '_': [[(0.1,0.9),(0.9,0.9)]],
        ':': [[(0.45,0.25),(0.55,0.35)],[(0.45,0.65),(0.55,0.75)]],
        ';': [[(0.45,0.25),(0.55,0.35)],[(0.45,0.65),(0.5,0.75),(0.42,0.85)]],
        '?': [[(0.25,0.2),(0.5,0.1),(0.75,0.2),(0.75,0.4),(0.5,0.55)],[(0.48,0.75),(0.52,0.8)]],
        'k': [[(0.2,0.1),(0.2,0.9)],[(0.7,0.1),(0.2,0.55),(0.75,0.9)]],
        'g': [[(0.8,0.3),(0.5,0.1),(0.2,0.3),(0.2,0.5),(0.8,0.5),(0.8,0.3)],[(0.8,0.5),(0.8,0.9),(0.3,0.9)]],
        'A': [[(0.15,0.9),(0.5,0.1),(0.85,0.9)],[(0.3,0.55),(0.7,0.55)]],
        'B': [[(0.2,0.9),(0.2,0.1),(0.65,0.1),(0.75,0.25),(0.65,0.45),(0.2,0.45)],[(0.65,0.45),(0.8,0.6),(0.7,0.9),(0.2,0.9)]],
        'C': [[(0.8,0.2),(0.5,0.1),(0.2,0.3),(0.2,0.7),(0.5,0.9),(0.8,0.8)]],
        'D': [[(0.2,0.9),(0.2,0.1),(0.6,0.1),(0.8,0.3),(0.8,0.7),(0.6,0.9),(0.2,0.9)]],
        'E': [[(0.8,0.1),(0.2,0.1),(0.2,0.9),(0.8,0.9)],[(0.2,0.5),(0.65,0.5)]],
        'F': [[(0.2,0.9),(0.2,0.1),(0.8,0.1)],[(0.2,0.5),(0.65,0.5)]],
        'G': [[(0.8,0.2),(0.5,0.1),(0.2,0.3),(0.2,0.7),(0.5,0.9),(0.8,0.7),(0.8,0.5),(0.55,0.5)]],
        'H': [[(0.2,0.1),(0.2,0.9)],[(0.8,0.1),(0.8,0.9)],[(0.2,0.5),(0.8,0.5)]],
        'I': [[(0.3,0.1),(0.7,0.1)],[(0.5,0.1),(0.5,0.9)],[(0.3,0.9),(0.7,0.9)]],
        'J': [[(0.4,0.1),(0.8,0.1)],[(0.65,0.1),(0.65,0.75),(0.45,0.9),(0.25,0.75)]],
        'K': [[(0.2,0.1),(0.2,0.9)],[(0.8,0.1),(0.2,0.5),(0.8,0.9)]],
        'L': [[(0.2,0.1),(0.2,0.9),(0.8,0.9)]],
        'M': [[(0.15,0.9),(0.15,0.1),(0.5,0.5),(0.85,0.1),(0.85,0.9)]],
        'N': [[(0.2,0.9),(0.2,0.1),(0.8,0.9),(0.8,0.1)]],
        'O': [[(0.2,0.1),(0.8,0.1),(0.8,0.9),(0.2,0.9),(0.2,0.1)]],
        'P': [[(0.2,0.9),(0.2,0.1),(0.7,0.1),(0.8,0.25),(0.7,0.45),(0.2,0.45)]],
        'Q': [[(0.2,0.1),(0.8,0.1),(0.8,0.9),(0.2,0.9),(0.2,0.1)],[(0.6,0.7),(0.85,0.95)]],
        'R': [[(0.2,0.9),(0.2,0.1),(0.7,0.1),(0.7,0.45),(0.2,0.45)],[(0.45,0.45),(0.8,0.9)]],
        'S': [[(0.8,0.2),(0.5,0.1),(0.2,0.2),(0.2,0.4),(0.8,0.6),(0.8,0.8),(0.5,0.9),(0.2,0.8)]],
        'T': [[(0.15,0.1),(0.85,0.1)],[(0.5,0.1),(0.5,0.9)]],
        'U': [[(0.2,0.1),(0.2,0.75),(0.5,0.9),(0.8,0.75),(0.8,0.1)]],
        'V': [[(0.15,0.1),(0.5,0.9),(0.85,0.1)]],
        'W': [[(0.1,0.1),(0.3,0.9),(0.5,0.4),(0.7,0.9),(0.9,0.1)]],
        'X': [[(0.2,0.1),(0.8,0.9)],[(0.8,0.1),(0.2,0.9)]],
        'Y': [[(0.15,0.1),(0.5,0.5),(0.85,0.1)],[(0.5,0.5),(0.5,0.9)]],
        'Z': [[(0.2,0.1),(0.8,0.1),(0.2,0.9),(0.8,0.9)]],
        'a': [[(0.7,0.3),(0.5,0.2),(0.25,0.35),(0.25,0.7),(0.5,0.85),(0.7,0.7)],[(0.7,0.2),(0.7,0.85)]],
        'b': [[(0.25,0.1),(0.25,0.85)],[(0.25,0.45),(0.5,0.3),(0.7,0.45),(0.7,0.7),(0.5,0.85),(0.25,0.7)]],
        'c': [[(0.7,0.35),(0.5,0.25),(0.3,0.4),(0.3,0.7),(0.5,0.85),(0.7,0.75)]],
        'd': [[(0.75,0.1),(0.75,0.85)],[(0.75,0.45),(0.5,0.3),(0.3,0.45),(0.3,0.7),(0.5,0.85),(0.75,0.7)]],
        'e': [[(0.3,0.55),(0.7,0.55),(0.7,0.35),(0.5,0.25),(0.3,0.4),(0.3,0.7),(0.5,0.85),(0.7,0.75)]],
        'f': [[(0.7,0.15),(0.5,0.1),(0.4,0.2),(0.4,0.9)],[(0.25,0.4),(0.6,0.4)]],
        'h': [[(0.25,0.1),(0.25,0.9)],[(0.25,0.45),(0.5,0.3),(0.7,0.45),(0.7,0.9)]],
        'i': [[(0.48,0.15),(0.52,0.2)],[(0.5,0.35),(0.5,0.9)]],
        'j': [[(0.55,0.15),(0.58,0.2)],[(0.55,0.35),(0.55,0.8),(0.4,0.9),(0.3,0.85)]],
        'l': [[(0.5,0.1),(0.5,0.9)]],
        'm': [[(0.15,0.9),(0.15,0.3)],[(0.15,0.4),(0.3,0.3),(0.4,0.4),(0.4,0.9)],[(0.4,0.4),(0.55,0.3),(0.65,0.4),(0.65,0.9)]],
        'n': [[(0.25,0.3),(0.25,0.9)],[(0.25,0.45),(0.5,0.3),(0.7,0.45),(0.7,0.9)]],
        'o': [[(0.3,0.35),(0.5,0.25),(0.7,0.35),(0.7,0.7),(0.5,0.85),(0.3,0.7),(0.3,0.35)]],
        'p': [[(0.25,0.3),(0.25,0.95)],[(0.25,0.45),(0.5,0.3),(0.7,0.45),(0.7,0.65),(0.5,0.8),(0.25,0.65)]],
        'r': [[(0.3,0.3),(0.3,0.9)],[(0.3,0.5),(0.5,0.3),(0.7,0.35)]],
        's': [[(0.65,0.35),(0.45,0.25),(0.3,0.38),(0.65,0.65),(0.5,0.85),(0.3,0.75)]],
        't': [[(0.4,0.1),(0.4,0.8),(0.55,0.9),(0.65,0.85)],[(0.25,0.35),(0.6,0.35)]],
        'u': [[(0.25,0.3),(0.25,0.7),(0.5,0.85),(0.7,0.7)],[(0.7,0.3),(0.7,0.85)]],
        'v': [[(0.2,0.3),(0.5,0.85),(0.8,0.3)]],
        'w': [[(0.15,0.3),(0.3,0.85),(0.45,0.5),(0.6,0.85),(0.8,0.3)]],
        'x': [[(0.25,0.3),(0.7,0.85)],[(0.7,0.3),(0.25,0.85)]],
        'y': [[(0.2,0.3),(0.5,0.65)],[(0.8,0.3),(0.3,0.95)]],
        'z': [[(0.25,0.3),(0.7,0.3),(0.25,0.85),(0.7,0.85)]],
        ' ': [],
        '!': [[(0.5,0.1),(0.5,0.65)],[(0.48,0.8),(0.52,0.85)]],
        '~': [[(0.15,0.5),(0.35,0.35),(0.65,0.65),(0.85,0.5)]],
        '→': [[(0.1,0.5),(0.85,0.5)],[(0.7,0.3),(0.85,0.5),(0.7,0.7)]],
        '←': [[(0.15,0.5),(0.9,0.5)],[(0.3,0.3),(0.15,0.5),(0.3,0.7)]],
        '↑': [[(0.5,0.15),(0.5,0.85)],[(0.3,0.35),(0.5,0.15),(0.7,0.35)]],
        '↓': [[(0.5,0.15),(0.5,0.85)],[(0.3,0.65),(0.5,0.85),(0.7,0.65)]],
        '(': [[(0.6,0.1),(0.35,0.5),(0.6,0.9)]],
        ')': [[(0.4,0.1),(0.65,0.5),(0.4,0.9)]],
        '[': [[(0.65,0.1),(0.35,0.1),(0.35,0.9),(0.65,0.9)]],
        ']': [[(0.35,0.1),(0.65,0.1),(0.65,0.9),(0.35,0.9)]],
        '+': [[(0.2,0.5),(0.8,0.5)],[(0.5,0.2),(0.5,0.8)]],
        '=': [[(0.2,0.38),(0.8,0.38)],[(0.2,0.62),(0.8,0.62)]],
        '*': [[(0.3,0.3),(0.7,0.7)],[(0.7,0.3),(0.3,0.7)],[(0.5,0.2),(0.5,0.8)]],
        '#': [[(0.35,0.1),(0.35,0.9)],[(0.65,0.1),(0.65,0.9)],[(0.15,0.35),(0.85,0.35)],[(0.15,0.65),(0.85,0.65)]],
        '@': [[(0.7,0.5),(0.55,0.35),(0.4,0.45),(0.4,0.6),(0.55,0.7),(0.7,0.6),(0.7,0.35),(0.55,0.2),(0.3,0.25),(0.2,0.5),(0.3,0.8),(0.6,0.9),(0.8,0.8)]],
        '%': [[(0.8,0.1),(0.2,0.9)],[(0.25,0.15),(0.35,0.15),(0.35,0.3),(0.25,0.3),(0.25,0.15)],[(0.65,0.7),(0.75,0.7),(0.75,0.85),(0.65,0.85),(0.65,0.7)]],
        '&': [[(0.8,0.85),(0.4,0.45),(0.55,0.2),(0.4,0.1),(0.3,0.2),(0.3,0.35),(0.7,0.7),(0.7,0.85),(0.5,0.85),(0.2,0.65)]],
        '"': [[(0.35,0.1),(0.35,0.3)],[(0.65,0.1),(0.65,0.3)]],
        "'": [[(0.5,0.1),(0.5,0.3)]],
        '♡': 'heart',
        '★': 'star',
        '♪': [[(0.6,0.15),(0.6,0.7),(0.4,0.85),(0.3,0.7),(0.45,0.6),(0.6,0.7)],[(0.6,0.15),(0.8,0.1),(0.8,0.3)]],
    }

    char_strokes = strokes.get(ch)
    if char_strokes is None:
        # Try case-insensitive
        char_strokes = strokes.get(ch.upper()) or strokes.get(ch.lower())
    if char_strokes is None:
        return s * 0.4
    if char_strokes == 'heart':
        _draw_heart(draw, x + s*0.3, y + s*0.4, s*0.3, color, width)
        return s * 0.65
    if char_strokes == 'star':
        _draw_star(draw, x + s*0.3, y + s*0.45, s*0.3, color, width)
        return s * 0.65
    if not char_strokes:
        return s * 0.35

    char_w = s * 0.65
    for polyline in char_strokes:
        wobble_stroke(draw, polyline, x, y, char_w, s, color, width, wobble_amt)

    return char_w


def _draw_heart(draw, cx, cy, size, color, width):
    """Draw a small heart shape."""
    pts = []
    for i in range(30):
        t = i / 30 * 2 * math.pi
        hx = size * 0.5 * (16 * math.sin(t)**3) / 16
        hy = -size * 0.5 * (13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t)) / 16
        pts.append((cx + hx + random.uniform(-0.5, 0.5), cy + hy + random.uniform(-0.5, 0.5)))
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i+1]], fill=color, width=width)


def _draw_star(draw, cx, cy, size, color, width):
    """Draw a small star shape."""
    pts = []
    for i in range(11):
        a = math.pi * 2 * i / 10 - math.pi / 2
        r = size if i % 2 == 0 else size * 0.4
        pts.append((cx + r*math.cos(a) + random.uniform(-1, 1), cy + r*math.sin(a) + random.uniform(-1, 1)))
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i+1]], fill=color, width=width)


def hand_write(draw, x, y, text, color, size, width=2, wobble_amt=1.5):
    """Write text entirely by hand - Korean syllables decomposed into jamo strokes.

    Args:
        draw: PIL ImageDraw object
        x: Starting x coordinate
        y: Starting y coordinate
        text: String to render (Korean + ASCII mixed OK)
        color: RGB tuple, e.g. (60, 60, 65)
        size: Character size in pixels
        width: Stroke width (default 2)
        wobble_amt: Randomness amount for hand-drawn effect (default 1.5)

    Returns:
        x position after the last character (for chaining)
    """
    cx = x
    for ch in text:
        code = ord(ch)
        # Random per-char jitter
        jx = random.uniform(-1.5, 1.5)
        jy = random.uniform(-2.5, 2.5)
        sz_var = size + random.uniform(-size*0.06, size*0.06)

        if 0xAC00 <= code <= 0xD7A3:
            # Korean syllable
            draw_syllable(draw, ch, cx + jx, y + jy, sz_var, color, width, wobble_amt)
            cx += sz_var * 0.95
        elif ch == ' ':
            cx += size * 0.35
        else:
            advance = draw_ascii_char(draw, ch, cx + jx, y + jy, sz_var, color, width, wobble_amt)
            cx += advance * 1.05

    return cx


# ═══════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════

def hand_write_centered(draw, cx, cy, text, color, size, width=2, wobble_amt=1.5):
    """Write text centered at (cx, cy)."""
    # Estimate width
    est_width = 0
    for ch in text:
        code = ord(ch)
        if 0xAC00 <= code <= 0xD7A3:
            est_width += size * 0.95
        elif ch == ' ':
            est_width += size * 0.35
        else:
            est_width += size * 0.65 * 1.05

    start_x = cx - est_width / 2
    start_y = cy - size / 2
    return hand_write(draw, start_x, start_y, text, color, size, width, wobble_amt)


def hand_write_multiline(draw, x, y, text, color, size, line_spacing=1.4, width=2, wobble_amt=1.5):
    """Write multi-line text. Lines separated by newline characters."""
    lines = text.split('\n')
    cy = y
    for line in lines:
        hand_write(draw, x, cy, line, color, size, width, wobble_amt)
        cy += size * line_spacing
    return cy


# Export for use in main script
if __name__ == '__main__':
    # Quick test
    img = Image.new("RGB", (800, 400), (255, 252, 245))
    draw = ImageDraw.Draw(img)
    hand_write(draw, 20, 30, "안녕하세요! 손글씨 테스트", (60, 60, 65), 50, width=2)
    hand_write(draw, 20, 100, "가나다라마바사아자차카타파하", (60, 60, 65), 40, width=2)
    hand_write(draw, 20, 160, "ABCDEFGHIJKLM", (60, 60, 65), 40, width=2)
    hand_write(draw, 20, 220, "nopqrstuvwxyz", (60, 60, 65), 40, width=2)
    hand_write(draw, 20, 290, "0123456789 + = * # @", (60, 60, 65), 35, width=2)
    hand_write(draw, 20, 345, "♡ ★ ♪ Hello World!", (225, 60, 75), 40, width=2)
    img.save("test_handwrite.png")
    print("Test saved to test_handwrite.png!")
