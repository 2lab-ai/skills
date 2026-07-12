#!/usr/bin/env python3
"""
Example: Generate hand-drawn exercise illustration cards.
Uses hangul_render + draw_utils for 100% font-free rendering.

Usage:
    # Requires Pillow (pip install Pillow)
    python exercise_images.py [output_dir]
"""

import sys
import os
import random

# Add scripts directory to path
SCRIPT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts')
sys.path.insert(0, SCRIPT_DIR)

from hangul_render import hand_write
from draw_utils import (
    wobble_line, wobble_rect, wobble_ellipse,
    hand_arrow, hand_heart, hand_star,
    draw_paper_bg, PALETTE
)
from PIL import Image, ImageDraw

# Colors
BG = PALETTE['bg']
BODY = PALETTE['body']
ACCENT = PALETTE['accent']
ACCENT2 = PALETTE['accent2']
MACHINE = PALETTE['machine']
GREEN = PALETTE['green']
GRAY = PALETTE['gray']
ORANGE = PALETTE['orange']

OUTPUT_DIR = sys.argv[1] if len(sys.argv) > 1 else "/tmp/hand-draw-examples"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def draw_figure(draw, cx, cy, pose, s=1.3):
    """Draw exercise-specific stick figures."""
    hr = int(17*s)

    if pose == "leg_ext":
        wobble_rect(draw, cx-int(50*s),cy-int(10*s),cx+int(10*s),cy+int(25*s), MACHINE, 3)
        wobble_line(draw, cx-int(50*s),cy-int(10*s),cx-int(55*s),cy-int(60*s), MACHINE, 4)
        wobble_ellipse(draw, cx-int(40*s),cy-int(65*s), hr, hr, BODY, 3)
        wobble_line(draw, cx-int(40*s),cy-int(48*s),cx-int(25*s),cy+int(5*s), BODY, 3)
        wobble_line(draw, cx-int(35*s),cy-int(30*s),cx-int(50*s),cy-int(5*s), BODY, 2)
        wobble_line(draw, cx-int(35*s),cy-int(30*s),cx-int(15*s),cy-int(5*s), BODY, 2)
        wobble_line(draw, cx-int(25*s),cy+int(5*s),cx+int(10*s),cy+int(10*s), BODY, 3)
        wobble_line(draw, cx+int(10*s),cy+int(10*s),cx+int(65*s),cy, BODY, 4)
        wobble_rect(draw, cx+int(55*s),cy-int(8*s),cx+int(70*s),cy+int(8*s), MACHINE, 3)

    elif pose == "squat":
        wobble_line(draw, cx-int(55*s),cy-int(42*s),cx+int(55*s),cy-int(42*s), BODY, 4)
        wobble_ellipse(draw, cx-int(55*s),cy-int(42*s), int(6*s),int(14*s), BODY, 3)
        wobble_ellipse(draw, cx+int(55*s),cy-int(42*s), int(6*s),int(14*s), BODY, 3)
        wobble_ellipse(draw, cx,cy-int(55*s), hr, hr, BODY, 3)
        wobble_line(draw, cx,cy-int(38*s),cx-int(8*s),cy+int(15*s), BODY, 3)
        wobble_line(draw, cx,cy-int(30*s),cx-int(30*s),cy-int(42*s), BODY, 3)
        wobble_line(draw, cx,cy-int(30*s),cx+int(30*s),cy-int(42*s), BODY, 3)
        wobble_line(draw, cx-int(8*s),cy+int(15*s),cx-int(35*s),cy+int(25*s), BODY, 3)
        wobble_line(draw, cx-int(35*s),cy+int(25*s),cx-int(30*s),cy+int(70*s), BODY, 3)
        wobble_line(draw, cx-int(8*s),cy+int(15*s),cx+int(20*s),cy+int(25*s), BODY, 3)
        wobble_line(draw, cx+int(20*s),cy+int(25*s),cx+int(25*s),cy+int(70*s), BODY, 3)
        wobble_line(draw, cx-int(38*s),cy+int(70*s),cx-int(22*s),cy+int(70*s), BODY, 3)
        wobble_line(draw, cx+int(18*s),cy+int(70*s),cx+int(33*s),cy+int(70*s), BODY, 3)

    elif pose == "v_squat":
        wobble_line(draw, cx-int(55*s),cy-int(75*s),cx-int(55*s),cy+int(80*s), MACHINE, 5)
        wobble_line(draw, cx-int(55*s),cy-int(75*s),cx,cy-int(75*s), MACHINE, 4)
        wobble_line(draw, cx-int(45*s),cy-int(65*s),cx-int(25*s),cy+int(40*s), MACHINE, 7)
        wobble_ellipse(draw, cx-int(32*s),cy-int(75*s), hr-2, hr-2, BODY, 3)
        wobble_line(draw, cx-int(30*s),cy-int(55*s),cx-int(20*s),cy+int(10*s), BODY, 3)
        wobble_line(draw, cx-int(20*s),cy+int(10*s),cx+int(5*s),cy+int(40*s), BODY, 3)
        wobble_line(draw, cx+int(5*s),cy+int(40*s),cx+int(10*s),cy+int(68*s), BODY, 3)
        wobble_line(draw, cx-int(20*s),cy+int(10*s),cx-int(8*s),cy+int(40*s), BODY, 3)
        wobble_line(draw, cx-int(8*s),cy+int(40*s),cx-int(5*s),cy+int(68*s), BODY, 3)
        wobble_line(draw, cx-int(15*s),cy+int(72*s),cx+int(20*s),cy+int(72*s), MACHINE, 5)

    elif pose == "split_squat":
        wobble_ellipse(draw, cx,cy-int(60*s), hr, hr, BODY, 3)
        wobble_line(draw, cx,cy-int(42*s),cx,cy+int(12*s), BODY, 3)
        wobble_line(draw, cx,cy-int(25*s),cx-int(22*s),cy+int(15*s), BODY, 2)
        wobble_line(draw, cx,cy-int(25*s),cx+int(22*s),cy+int(15*s), BODY, 2)
        wobble_rect(draw, cx-int(28*s),cy+int(10*s),cx-int(16*s),cy+int(22*s), BODY, 2)
        wobble_rect(draw, cx+int(16*s),cy+int(10*s),cx+int(28*s),cy+int(22*s), BODY, 2)
        wobble_line(draw, cx,cy+int(12*s),cx-int(28*s),cy+int(30*s), BODY, 3)
        wobble_line(draw, cx-int(28*s),cy+int(30*s),cx-int(25*s),cy+int(70*s), BODY, 3)
        wobble_line(draw, cx,cy+int(12*s),cx+int(32*s),cy+int(35*s), BODY, 3)
        wobble_line(draw, cx+int(32*s),cy+int(35*s),cx+int(40*s),cy+int(65*s), BODY, 3)

    elif pose == "leg_press":
        wobble_line(draw, cx-int(70*s),cy+int(30*s),cx-int(10*s),cy+int(30*s), MACHINE, 5)
        wobble_line(draw, cx-int(75*s),cy-int(10*s),cx-int(60*s),cy+int(30*s), MACHINE, 6)
        wobble_ellipse(draw, cx-int(68*s),cy-int(5*s), hr-3, hr-3, BODY, 3)
        wobble_line(draw, cx-int(60*s),cy+int(5*s),cx-int(20*s),cy+int(5*s), BODY, 3)
        wobble_line(draw, cx-int(45*s),cy+int(5*s),cx-int(50*s),cy+int(25*s), BODY, 2)
        wobble_line(draw, cx-int(20*s),cy+int(5*s),cx-int(5*s),cy-int(20*s), BODY, 3)
        wobble_line(draw, cx-int(5*s),cy-int(20*s),cx+int(20*s),cy-int(55*s), BODY, 3)
        wobble_line(draw, cx-int(20*s),cy+int(5*s),cx-int(10*s),cy-int(18*s), BODY, 3)
        wobble_line(draw, cx-int(10*s),cy-int(18*s),cx+int(15*s),cy-int(50*s), BODY, 3)
        wobble_line(draw, cx+int(5*s),cy-int(65*s),cx+int(35*s),cy-int(40*s), MACHINE, 7)
        for i in range(4):
            wy = cy+int(40*s)+i*int(14*s)
            wobble_rect(draw, cx+int(25*s),wy,cx+int(55*s),wy+int(10*s), MACHINE, 2)

    elif pose == "leg_curl":
        wobble_line(draw, cx-int(65*s),cy+int(10*s),cx+int(35*s),cy+int(10*s), MACHINE, 5)
        wobble_line(draw, cx-int(55*s),cy+int(10*s),cx-int(55*s),cy+int(35*s), MACHINE, 3)
        wobble_line(draw, cx+int(25*s),cy+int(10*s),cx+int(25*s),cy+int(35*s), MACHINE, 3)
        wobble_ellipse(draw, cx-int(60*s),cy-int(5*s), hr-3, hr-3, BODY, 3)
        wobble_line(draw, cx-int(48*s),cy+int(3*s),cx+int(25*s),cy+int(3*s), BODY, 3)
        wobble_line(draw, cx-int(40*s),cy+int(3*s),cx-int(48*s),cy+int(28*s), BODY, 2)
        wobble_line(draw, cx+int(25*s),cy+int(3*s),cx+int(40*s),cy+int(3*s), BODY, 3)
        wobble_line(draw, cx+int(40*s),cy+int(3*s),cx+int(38*s),cy-int(35*s), BODY, 4)
        wobble_rect(draw, cx+int(32*s),cy-int(42*s),cx+int(46*s),cy-int(30*s), MACHINE, 3)
        wobble_line(draw, cx+int(50*s),cy+int(10*s),cx+int(50*s),cy-int(50*s), MACHINE, 4)
        wobble_line(draw, cx+int(50*s),cy-int(50*s),cx+int(39*s),cy-int(36*s), MACHINE, 3)


# ═══════════════════════════════════════════════
# EXERCISE DATA
# ═══════════════════════════════════════════════

exercises = [
    {"num": "1", "name": "레그 익스텐션", "pose": "leg_ext", "target": "대퇴사두근",
     "notes": [
         ("워밍업으로 딱!!", 295, 88, ACCENT, 28, True),
         ("무릎 라인에", 325, 168, ACCENT2, 22, False),
         ("머신 축 맞추기~", 310, 198, ACCENT2, 22, False),
         ("허벅지 앞쪽이", 300, 295, ACCENT, 22, False),
         ("불타는 느낌!!", 318, 325, ACCENT, 25, True),
         ("3칸 / 15개", 345, 398, BODY, 32, True),
         ("REST 1.5분", 358, 445, GREEN, 24, False),
     ], "deco": [("arrow", 320, 230, 255, 260), ("heart", 488, 88), ("star", 505, 445)]},

    {"num": "2", "name": "스쿼트", "pose": "squat", "target": "전신",
     "notes": [
         ("운동의 왕!!", 315, 88, ACCENT, 30, True),
         ("킹갓스쿼트", 325, 125, ACCENT, 26, True),
         ("가슴 펴고!", 330, 192, ACCENT2, 22, False),
         ("허리 중립 유지~", 310, 222, ACCENT2, 22, False),
         ("발 전체로 밀기!", 318, 355, ACCENT, 24, True),
         ("40kg / 12개", 338, 408, BODY, 32, True),
         ("REST 2.5분", 358, 458, GREEN, 24, False),
     ], "deco": [("arrow", 325, 250, 195, 250), ("star", 498, 92)]},

    {"num": "3", "name": "V스쿼트", "pose": "v_squat", "target": "대퇴사두 둔근",
     "notes": [
         ("머신이라", 328, 88, ACCENT2, 26, False),
         ("안전해요~", 335, 118, ACCENT2, 26, False),
         ("등 패드에 붙이기!", 305, 215, ACCENT, 22, True),
         ("5개만!!", 355, 308, ACCENT, 30, True),
         ("근력 포커스", 335, 348, ACCENT, 22, False),
         ("20kg / 5개", 350, 408, BODY, 32, True),
         ("REST 3분", 368, 458, GREEN, 24, False),
     ], "deco": [("arrow", 320, 250, 208, 248), ("star", 478, 308), ("star", 495, 318)]},

    {"num": "4", "name": "스플릿 스쿼트", "pose": "split_squat", "target": "둔근 한쪽씩",
     "notes": [
         ("한쪽 다리씩!", 305, 88, ACCENT, 28, True),
         ("균형 중요~", 335, 122, ACCENT, 24, False),
         ("앞무릎 90도!", 315, 202, ACCENT2, 24, True),
         ("힙업 효과!!", 328, 318, ACCENT, 26, True),
         ("10kg / 12개", 340, 400, BODY, 32, True),
         ("REST 2.5분", 358, 448, GREEN, 24, False),
     ], "deco": [("arrow", 305, 230, 195, 285), ("heart", 488, 318), ("heart", 502, 308)]},

    {"num": "5", "name": "레그프레스", "pose": "leg_press", "target": "대퇴사두 둔근",
     "notes": [
         ("발판에 발", 328, 88, ACCENT2, 24, False),
         ("어깨너비로!", 335, 118, ACCENT2, 24, False),
         ("허리 뜨지 않게!!", 318, 218, ACCENT, 24, True),
         ("20개!!", 378, 298, ACCENT, 32, True),
         ("펌핑 타임~", 355, 338, ACCENT, 24, False),
         ("80kg / 20개", 332, 408, BODY, 32, True),
         ("REST 2분", 375, 458, GREEN, 24, False),
     ], "deco": [("arrow", 340, 255, 218, 238), ("star", 488, 298)]},

    {"num": "6", "name": "레그컬", "pose": "leg_curl", "target": "햄스트링",
     "notes": [
         ("마무리 운동~", 315, 88, ACCENT2, 26, False),
         ("허벅지 뒤쪽!", 325, 122, ACCENT2, 24, True),
         ("엎드려서", 345, 202, ACCENT, 22, False),
         ("발목에 패드!", 325, 232, ACCENT, 24, False),
         ("천천히 올리고 내리기", 295, 318, ACCENT, 22, False),
         ("3칸 / 12개", 352, 398, BODY, 32, True),
         ("REST 1.5분", 362, 445, GREEN, 24, False),
         ("수고했어!!", 338, 495, ACCENT, 28, True),
     ], "deco": [("heart", 478, 495), ("heart", 498, 488), ("heart", 488, 508), ("star", 508, 88)]},
]


def main():
    for ex in exercises:
        random.seed(int(ex["num"]) * 137 + 42)
        print(f"Drawing {ex['num']}. {ex['name']}...")

        img = Image.new("RGB", (570, 570), BG)
        draw_paper_bg(img)
        draw = ImageDraw.Draw(img)

        # Title
        hand_write(draw, 60, 16, f"{ex['num']}.", BODY, 40, width=3)
        hand_write(draw, 100, 14, ex["name"], BODY, 38, width=3)

        # Target
        hand_write(draw, 62, 55, f"타겟 {ex['target']}", GRAY, 16, width=2)

        # Figure
        draw_figure(draw, 150, 300, ex["pose"])

        # Annotations
        for note in ex["notes"]:
            txt, nx, ny, col, sz, bold = note
            w = 3 if bold else 2
            hand_write(draw, nx, ny, txt, col, sz, width=w)

        # Decorations
        for deco in ex.get("deco", []):
            if deco[0] == "arrow":
                hand_arrow(draw, deco[1], deco[2], deco[3], deco[4])
            elif deco[0] == "heart":
                hand_heart(draw, deco[1], deco[2])
            elif deco[0] == "star":
                hand_star(draw, deco[1], deco[2])

        outpath = os.path.join(OUTPUT_DIR, f"{ex['num']}_{ex['name'].replace(' ', '')}.png")
        img.save(outpath, "PNG")
        print(f"  -> {outpath}")

    print(f"\nDone! {len(exercises)} images saved to {OUTPUT_DIR}")
    print("100% hand-drawn, zero font files used.")


if __name__ == '__main__':
    main()
