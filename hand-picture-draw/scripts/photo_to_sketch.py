#!/usr/bin/env python3
"""
Photo-to-Sketch Converter — hand-picture-draw skill
Converts photos into realistic hand-drawn pencil/charcoal sketches.

Techniques:
  1. Dodge-and-burn (core pencil effect)
  2. Edge enhancement (Canny/Laplacian for sharp contours)
  3. Paper texture overlay
  4. Cross-hatch tonal simulation
  5. Wobble/jitter for hand-drawn imperfection

Usage:
  python photo_to_sketch.py input.jpg output.png [--style pencil|charcoal|ink|watercolor]
"""

import argparse
import math
import os
import random
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops


# ═══════════════════════════════════════════════
# Style Presets
# ═══════════════════════════════════════════════

STYLES = {
    "pencil": {
        "blur_kernel": 61,
        "edge_weight": 0.15,
        "darkness": 0.95,
        "paper_opacity": 0.08,
        "contrast_boost": 1.2,
        "hatching": True,
        "hatch_density": 0.6,
        "wobble": True,
        "invert_bg": True,
        "description": "연필 스케치 — 부드러운 그라데이션 + 자연스러운 선",
    },
    "charcoal": {
        "blur_kernel": 41,
        "edge_weight": 0.25,
        "darkness": 1.1,
        "paper_opacity": 0.12,
        "contrast_boost": 1.4,
        "hatching": True,
        "hatch_density": 0.8,
        "wobble": True,
        "invert_bg": True,
        "description": "숯 드로잉 — 강한 명암 + 거친 질감",
    },
    "ink": {
        "blur_kernel": 31,
        "edge_weight": 0.4,
        "darkness": 1.3,
        "paper_opacity": 0.05,
        "contrast_boost": 1.6,
        "hatching": False,
        "hatch_density": 0.0,
        "wobble": True,
        "invert_bg": True,
        "description": "펜 잉크 — 깔끔한 윤곽선 + 높은 대비",
    },
    "watercolor": {
        "blur_kernel": 81,
        "edge_weight": 0.1,
        "darkness": 0.7,
        "paper_opacity": 0.15,
        "contrast_boost": 1.0,
        "hatching": False,
        "hatch_density": 0.0,
        "wobble": False,
        "invert_bg": True,
        "colorize": True,
        "description": "수채화 — 부드러운 색감 + 번짐 효과",
    },
}


# ═══════════════════════════════════════════════
# Core Engine
# ═══════════════════════════════════════════════


def load_and_prep(path: str, max_dim: int = 1200) -> np.ndarray:
    """Load image, resize if needed, return BGR numpy array."""
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {path}")
    h, w = img.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    return img


def dodge_burn_sketch(gray: np.ndarray, blur_kernel: int = 61) -> np.ndarray:
    """
    Core pencil sketch via dodge-and-burn.
    Gray → Invert → GaussianBlur → ColorDodge blend.
    """
    inverted = 255 - gray
    blurred = cv2.GaussianBlur(inverted, (blur_kernel, blur_kernel), 0)
    # Color dodge: result = image * 256 / (256 - blur)
    # Prevent division by zero
    sketch = cv2.divide(gray, 255 - blurred, scale=256.0)
    sketch = np.clip(sketch, 0, 255).astype(np.uint8)
    return sketch


def enhance_edges(gray: np.ndarray, weight: float = 0.2) -> np.ndarray:
    """Extract edges using Canny + Laplacian blend for sharp contours."""
    # Bilateral filter to reduce noise but keep edges
    filtered = cv2.bilateralFilter(gray, 9, 75, 75)

    # Canny edges
    canny = cv2.Canny(filtered, 30, 100)
    canny_inv = 255 - canny  # White bg, dark lines

    # Laplacian for softer edge detection
    lap = cv2.Laplacian(filtered, cv2.CV_64F)
    lap = np.uint8(np.clip(np.absolute(lap), 0, 255))
    lap_inv = 255 - lap

    # Blend canny and laplacian
    edges = cv2.addWeighted(canny_inv, 0.6, lap_inv, 0.4, 0)
    return edges


def generate_paper_texture(h: int, w: int, intensity: float = 0.08) -> np.ndarray:
    """Generate realistic paper grain texture."""
    # Base noise
    noise = np.random.normal(128, 20, (h, w)).astype(np.uint8)
    # Blur for fiber-like pattern
    texture = cv2.GaussianBlur(noise, (3, 3), 0)
    # Normalize to paper-white range
    texture = cv2.normalize(texture, None, int(245 * (1 - intensity)), 255, cv2.NORM_MINMAX)
    return texture.astype(np.uint8)


def add_hatching(img: np.ndarray, gray: np.ndarray, density: float = 0.6) -> np.ndarray:
    """
    Add cross-hatching lines based on tonal values.
    Darker areas get denser hatching.
    """
    h, w = img.shape[:2]
    result = img.copy()

    # Define hatching zones
    # Dark (0-80): dense cross-hatch
    # Mid (80-160): single direction hatch
    # Light (160-255): no hatching

    spacing_base = max(3, int(6 * (1 - density)))

    for angle_deg in [45, -45]:
        angle = math.radians(angle_deg)
        cos_a, sin_a = math.cos(angle), math.sin(angle)

        # Generate parallel lines across the image
        max_dist = int(math.sqrt(h * h + w * w))
        spacing = spacing_base

        for d in range(-max_dist, max_dist, spacing):
            # Line start/end points
            x0 = int(w / 2 + d * cos_a - max_dist * sin_a)
            y0 = int(h / 2 + d * sin_a + max_dist * cos_a)
            x1 = int(w / 2 + d * cos_a + max_dist * sin_a)
            y1 = int(h / 2 + d * sin_a - max_dist * cos_a)

            # Sample points along the line to check darkness
            num_samples = 10
            should_draw = False
            threshold = 160 if angle_deg == 45 else 80  # Cross-hatch only for darker areas

            for i in range(num_samples):
                t = i / max(num_samples - 1, 1)
                sx = int(x0 + t * (x1 - x0))
                sy = int(y0 + t * (y1 - y0))
                if 0 <= sx < w and 0 <= sy < h:
                    if gray[sy, sx] < threshold:
                        should_draw = True
                        break

            if should_draw:
                # Add wobble to the line
                pts = []
                steps = max(2, abs(x1 - x0 + y1 - y0) // 20)
                for i in range(steps + 1):
                    t = i / steps
                    px = int(x0 + t * (x1 - x0) + random.gauss(0, 0.8))
                    py = int(y0 + t * (y1 - y0) + random.gauss(0, 0.8))
                    pts.append([px, py])

                if len(pts) >= 2:
                    pts_arr = np.array(pts, dtype=np.int32)
                    # Darkness-dependent line opacity
                    cv2.polylines(result, [pts_arr], False, 180, 1, cv2.LINE_AA)

    return result


def apply_wobble(img_pil: Image.Image, strength: float = 1.5) -> Image.Image:
    """
    Apply subtle geometric distortion for hand-drawn imperfection.
    Uses displacement map approach.
    """
    w, h = img_pil.size
    arr = np.array(img_pil)

    # Generate displacement fields
    dx = np.random.normal(0, strength, (h, w)).astype(np.float32)
    dy = np.random.normal(0, strength, (h, w)).astype(np.float32)

    # Smooth the displacement for natural warping
    dx = cv2.GaussianBlur(dx, (15, 15), 0) * 2
    dy = cv2.GaussianBlur(dy, (15, 15), 0) * 2

    # Create mapping
    map_x = np.float32(np.tile(np.arange(w), (h, 1))) + dx
    map_y = np.float32(np.tile(np.arange(h).reshape(-1, 1), (1, w))) + dy

    # Remap
    result = cv2.remap(arr, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return Image.fromarray(result)


def add_vignette(img: np.ndarray, strength: float = 0.3) -> np.ndarray:
    """Add subtle vignette (darker edges) like scanned paper."""
    h, w = img.shape[:2]
    # Create gradient mask
    Y, X = np.ogrid[:h, :w]
    cx, cy = w / 2, h / 2
    dist = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    max_dist = np.sqrt(cx ** 2 + cy ** 2)
    mask = dist / max_dist
    mask = np.clip(mask * strength, 0, 1)

    if len(img.shape) == 3:
        mask = np.stack([mask] * 3, axis=-1)

    result = (img.astype(np.float32) * (1 - mask * 0.3)).astype(np.uint8)
    return result


def colorize_sketch(sketch_gray: np.ndarray, original_bgr: np.ndarray, opacity: float = 0.3) -> np.ndarray:
    """Blend sketch with faded original colors for watercolor effect."""
    # Desaturate original
    hsv = cv2.cvtColor(original_bgr, cv2.COLOR_BGR2HSV)
    hsv[:, :, 1] = (hsv[:, :, 1] * 0.5).astype(np.uint8)  # Reduce saturation
    hsv[:, :, 2] = np.clip(hsv[:, :, 2].astype(np.float32) * 1.2, 0, 255).astype(np.uint8)
    faded = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    # Convert sketch to 3 channels
    sketch_bgr = cv2.cvtColor(sketch_gray, cv2.COLOR_GRAY2BGR)

    # Blend: sketch * (1-opacity) + faded * opacity, with multiply
    result = cv2.addWeighted(sketch_bgr, 1 - opacity, faded, opacity, 0)

    # Apply sketch as luminance mask
    sketch_norm = sketch_gray.astype(np.float32) / 255.0
    sketch_mask = np.stack([sketch_norm] * 3, axis=-1)
    result = (result.astype(np.float32) * sketch_mask).astype(np.uint8)

    return result


# ═══════════════════════════════════════════════
# Main Pipeline
# ═══════════════════════════════════════════════


def photo_to_sketch(
    input_path: str,
    output_path: str,
    style: str = "pencil",
    max_dim: int = 1200,
    seed: int = 42,
) -> str:
    """
    Convert photo to hand-drawn sketch.

    Args:
        input_path: Path to source photo
        output_path: Path to save result
        style: pencil | charcoal | ink | watercolor
        max_dim: Max dimension (resize if larger)
        seed: Random seed for reproducibility

    Returns:
        output_path on success
    """
    random.seed(seed)
    np.random.seed(seed)

    cfg = STYLES.get(style, STYLES["pencil"])
    print(f"[photo_to_sketch] Style: {style} — {cfg['description']}")

    # 1. Load and prep
    img_bgr = load_and_prep(input_path, max_dim)
    h, w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    print(f"[1/6] Loaded: {w}x{h}")

    # 2. Pre-processing: contrast enhancement
    if cfg["contrast_boost"] != 1.0:
        gray = cv2.convertScaleAbs(gray, alpha=cfg["contrast_boost"], beta=0)
    print(f"[2/6] Contrast boost: {cfg['contrast_boost']}")

    # 3. Core dodge-and-burn sketch
    sketch = dodge_burn_sketch(gray, blur_kernel=cfg["blur_kernel"])
    print(f"[3/6] Dodge-burn sketch (kernel={cfg['blur_kernel']})")

    # 4. Edge enhancement
    if cfg["edge_weight"] > 0:
        edges = enhance_edges(gray, cfg["edge_weight"])
        # Multiply blend: sketch * edges / 255
        sketch = cv2.multiply(sketch, edges, scale=1.0 / 255.0).astype(np.uint8)
        print(f"[4/6] Edge enhancement (weight={cfg['edge_weight']})")
    else:
        print(f"[4/6] Edge enhancement: skipped")

    # 5. Darkness adjustment
    if cfg["darkness"] != 1.0:
        sketch = np.clip(sketch.astype(np.float32) * cfg["darkness"], 0, 255).astype(np.uint8)

    # 6. Hatching
    if cfg.get("hatching") and cfg["hatch_density"] > 0:
        sketch = add_hatching(sketch, gray, cfg["hatch_density"])
        print(f"[5/6] Cross-hatching (density={cfg['hatch_density']})")
    else:
        print(f"[5/6] Hatching: skipped")

    # 7. Paper texture overlay
    if cfg["paper_opacity"] > 0:
        texture = generate_paper_texture(h, w, cfg["paper_opacity"])
        sketch = cv2.multiply(sketch, texture, scale=1.0 / 255.0).astype(np.uint8)
        print(f"[6/6] Paper texture (opacity={cfg['paper_opacity']})")
    else:
        print(f"[6/6] Paper texture: skipped")

    # 8. Colorize (watercolor mode)
    if cfg.get("colorize"):
        result_bgr = colorize_sketch(sketch, img_bgr, opacity=0.35)
    else:
        result_bgr = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)

    # 9. Vignette
    result_bgr = add_vignette(result_bgr, strength=0.25)

    # 10. Convert to PIL for wobble
    result_pil = Image.fromarray(cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB))

    if cfg.get("wobble"):
        result_pil = apply_wobble(result_pil, strength=1.2)
        print(f"[+] Wobble distortion applied")

    # Save
    result_pil.save(output_path, quality=95)
    print(f"[done] Saved: {output_path}")
    return output_path


def generate_all_styles(input_path: str, output_dir: str, max_dim: int = 1200) -> list:
    """Generate all 4 styles for comparison."""
    os.makedirs(output_dir, exist_ok=True)
    results = []
    for style_name in STYLES:
        out = os.path.join(output_dir, f"sketch_{style_name}.png")
        photo_to_sketch(input_path, out, style=style_name, max_dim=max_dim)
        results.append(out)
        print()
    return results


# ═══════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Photo to Hand-Drawn Sketch")
    parser.add_argument("input", help="Input photo path")
    parser.add_argument("output", help="Output image path")
    parser.add_argument("--style", default="pencil", choices=list(STYLES.keys()),
                        help="Sketch style (default: pencil)")
    parser.add_argument("--max-dim", type=int, default=1200,
                        help="Max dimension (default: 1200)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed (default: 42)")
    parser.add_argument("--all-styles", action="store_true",
                        help="Generate all 4 styles (output = directory)")
    args = parser.parse_args()

    if args.all_styles:
        generate_all_styles(args.input, args.output, args.max_dim)
    else:
        photo_to_sketch(args.input, args.output, style=args.style,
                        max_dim=args.max_dim, seed=args.seed)
