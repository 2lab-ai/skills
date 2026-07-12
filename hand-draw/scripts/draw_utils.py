#!/usr/bin/env python3
"""
Hand-drawn illustration utilities.
Wobble primitives, paper backgrounds, stick figures, decorative elements.
Works with hangul_render.py for fully hand-drawn image generation.

Usage:
    from draw_utils import wobble_line, wobble_rect, wobble_ellipse
    from draw_utils import hand_arrow, hand_heart, hand_star
    from draw_utils import draw_paper_bg
"""

from PIL import Image, ImageDraw
import math
import random

# ═══════════════════════════════════════════════
# COLOR PALETTE
# ═══════════════════════════════════════════════

PALETTE = {
    'bg': (255, 251, 243),         # Warm paper background
    'body': (60, 60, 65),          # Dark text / figure
    'accent': (225, 60, 75),       # Red accent
    'accent2': (55, 125, 220),     # Blue accent
    'machine': (148, 148, 158),    # Gray for equipment
    'green': (45, 165, 85),        # Green
    'gray': (125, 125, 138),       # Light gray
    'orange': (230, 140, 40),      # Orange
    'pink': (235, 130, 160),       # Pink
    'purple': (140, 80, 200),      # Purple
}


# ═══════════════════════════════════════════════
# WOBBLE PRIMITIVES
# ═══════════════════════════════════════════════

def wobble_line(draw, x1, y1, x2, y2, color=(60, 60, 65), width=3):
    """Draw a hand-drawn wobbly line between two points."""
    segs = max(4, int(math.hypot(x2-x1, y2-y1) / 10))
    prev = (x1, y1)
    for i in range(1, segs + 1):
        t = i / segs
        nx = x1 + (x2-x1)*t + random.uniform(-1.5, 1.5)
        ny = y1 + (y2-y1)*t + random.uniform(-1.5, 1.5)
        draw.line([prev, (nx, ny)], fill=color, width=width)
        prev = (nx, ny)


def wobble_rect(draw, x1, y1, x2, y2, color=(148, 148, 158), width=3):
    """Draw a hand-drawn wobbly rectangle."""
    wobble_line(draw, x1, y1, x2, y1, color, width)
    wobble_line(draw, x2, y1, x2, y2, color, width)
    wobble_line(draw, x2, y2, x1, y2, color, width)
    wobble_line(draw, x1, y2, x1, y1, color, width)


def wobble_ellipse(draw, cx, cy, rx, ry, color=(60, 60, 65), width=3):
    """Draw a hand-drawn wobbly ellipse."""
    pts = []
    n = 22
    for i in range(n + 2):
        a = 2 * math.pi * i / n
        pts.append((
            cx + rx * math.cos(a) + random.uniform(-2, 2),
            cy + ry * math.sin(a) + random.uniform(-2, 2)
        ))
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i+1]], fill=color, width=width)


# ═══════════════════════════════════════════════
# DECORATIVE ELEMENTS
# ═══════════════════════════════════════════════

def hand_arrow(draw, x1, y1, x2, y2, color=(225, 60, 75), width=2):
    """Draw a hand-drawn arrow from (x1,y1) to (x2,y2)."""
    wobble_line(draw, x1, y1, x2, y2, color, width)
    a = math.atan2(y2-y1, x2-x1)
    for da in [0.5, -0.5]:
        wobble_line(draw, x2-12*math.cos(a+da), y2-12*math.sin(a+da), x2, y2, color, width)


def hand_heart(draw, cx, cy, size=16, color=(225, 60, 75)):
    """Draw a hand-drawn heart shape."""
    pts = []
    for i in range(30):
        t = i / 30 * 2 * math.pi
        hx = size * 0.5 * (16 * math.sin(t)**3) / 16
        hy = -size * 0.5 * (13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t)) / 16
        pts.append((cx + hx + random.uniform(-0.5, 0.5), cy + hy + random.uniform(-0.5, 0.5)))
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i+1]], fill=color, width=2)


def hand_star(draw, cx, cy, size=12, color=(230, 140, 40)):
    """Draw a hand-drawn star shape."""
    pts = []
    for i in range(11):
        a = math.pi * 2 * i / 10 - math.pi / 2
        r = size if i % 2 == 0 else size * 0.4
        pts.append((cx + r*math.cos(a) + random.uniform(-1, 1), cy + r*math.sin(a) + random.uniform(-1, 1)))
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i+1]], fill=color, width=2)


def hand_checkmark(draw, cx, cy, size=12, color=(45, 165, 85), width=2):
    """Draw a hand-drawn checkmark."""
    wobble_line(draw, cx - size*0.3, cy, cx, cy + size*0.4, color, width)
    wobble_line(draw, cx, cy + size*0.4, cx + size*0.5, cy - size*0.3, color, width)


def hand_cross(draw, cx, cy, size=12, color=(225, 60, 75), width=2):
    """Draw a hand-drawn X mark."""
    wobble_line(draw, cx - size*0.4, cy - size*0.4, cx + size*0.4, cy + size*0.4, color, width)
    wobble_line(draw, cx + size*0.4, cy - size*0.4, cx - size*0.4, cy + size*0.4, color, width)


def hand_underline(draw, x, y, width_px, color=(225, 60, 75), stroke_width=2):
    """Draw a hand-drawn wavy underline."""
    pts = []
    segs = max(5, width_px // 15)
    for i in range(segs + 1):
        px = x + (width_px * i / segs)
        py = y + random.uniform(-2, 2) + math.sin(i * 0.8) * 2
        pts.append((px, py))
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i+1]], fill=color, width=stroke_width)


def hand_circle_highlight(draw, cx, cy, rx, ry, color=(225, 60, 75), width=2):
    """Draw a hand-drawn circle highlight (for circling/emphasizing)."""
    wobble_ellipse(draw, cx, cy, rx, ry, color, width)


# ═══════════════════════════════════════════════
# BACKGROUND STYLES
# ═══════════════════════════════════════════════

def draw_paper_bg(img, seed=42):
    """Draw a notebook paper background with ruled lines and margin."""
    draw = ImageDraw.Draw(img)
    w, h = img.size
    rng = random.Random(seed)

    # Paper texture - subtle dots
    for _ in range(400):
        x, y = rng.randint(0, w-1), rng.randint(0, h-1)
        c = rng.randint(240, 254)
        draw.point((x, y), fill=(c, c, c-5))

    # Horizontal ruled lines
    for yl in range(85, h, 50):
        for x in range(25, w-25, 3):
            if rng.random() < 0.88:
                draw.line([(x, yl), (x+2, yl)], fill=(222, 222, 232), width=1)

    # Margin line (pink/red)
    for y in range(10, h-10, 3):
        if rng.random() < 0.9:
            draw.line([(50, y), (50, y+2)], fill=(238, 188, 188), width=1)


def draw_grid_bg(img, spacing=30, color=(230, 230, 240), seed=42):
    """Draw a grid paper background."""
    draw = ImageDraw.Draw(img)
    w, h = img.size
    rng = random.Random(seed)

    # Paper texture
    for _ in range(300):
        x, y = rng.randint(0, w-1), rng.randint(0, h-1)
        c = rng.randint(242, 254)
        draw.point((x, y), fill=(c, c, c-3))

    # Vertical lines
    for xl in range(spacing, w, spacing):
        for y in range(0, h, 3):
            if rng.random() < 0.85:
                draw.line([(xl, y), (xl, y+2)], fill=color, width=1)

    # Horizontal lines
    for yl in range(spacing, h, spacing):
        for x in range(0, w, 3):
            if rng.random() < 0.85:
                draw.line([(x, yl), (x+2, yl)], fill=color, width=1)


def draw_dot_bg(img, spacing=20, dot_r=1, color=(215, 215, 225), seed=42):
    """Draw a dot grid background."""
    draw = ImageDraw.Draw(img)
    w, h = img.size
    rng = random.Random(seed)

    for _ in range(200):
        x, y = rng.randint(0, w-1), rng.randint(0, h-1)
        c = rng.randint(245, 254)
        draw.point((x, y), fill=(c, c, c-2))

    for xl in range(spacing, w, spacing):
        for yl in range(spacing, h, spacing):
            jx = rng.uniform(-0.5, 0.5)
            jy = rng.uniform(-0.5, 0.5)
            draw.ellipse(
                [xl-dot_r+jx, yl-dot_r+jy, xl+dot_r+jx, yl+dot_r+jy],
                fill=color
            )


# ═══════════════════════════════════════════════
# STICK FIGURE HELPERS
# ═══════════════════════════════════════════════

def stick_figure(draw, cx, cy, scale=1.0, color=(60, 60, 65), width=3,
                 head_r=None, body_len=None, arm_angle=45, leg_angle=30,
                 arm_len=None, leg_len=None):
    """Draw a basic standing stick figure.

    Args:
        cx, cy: Center of the head
        scale: Overall scale factor
        color: Line color
        width: Line width
        head_r: Head radius (auto-calculated if None)
        body_len: Body length (auto-calculated if None)
        arm_angle: Arm angle in degrees from horizontal
        leg_angle: Leg angle in degrees from vertical
        arm_len: Arm length (auto-calculated if None)
        leg_len: Leg length (auto-calculated if None)
    """
    s = scale
    hr = head_r or int(17 * s)
    bl = body_len or int(55 * s)
    al = arm_len or int(35 * s)
    ll = leg_len or int(45 * s)

    # Head
    wobble_ellipse(draw, cx, cy, hr, hr, color, width)

    # Body
    neck_y = cy + hr
    hip_y = neck_y + bl
    wobble_line(draw, cx, neck_y, cx, hip_y, color, width)

    # Arms
    shoulder_y = neck_y + bl * 0.25
    arm_a = math.radians(arm_angle)
    for sign in [-1, 1]:
        ax = cx + sign * al * math.cos(arm_a)
        ay = shoulder_y + al * math.sin(arm_a)
        wobble_line(draw, cx, shoulder_y, int(ax), int(ay), color, width)

    # Legs
    leg_a = math.radians(leg_angle)
    for sign in [-1, 1]:
        lx = cx + sign * ll * math.sin(leg_a)
        ly = hip_y + ll * math.cos(leg_a)
        wobble_line(draw, cx, hip_y, int(lx), int(ly), color, width)
        # Feet
        foot_dir = sign * 8 * s
        wobble_line(draw, int(lx), int(ly), int(lx + foot_dir), int(ly), color, max(1, width-1))
