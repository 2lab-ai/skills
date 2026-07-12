#!/usr/bin/env python3
"""
flowchart-diagram — "How to Adult" 스타일 미니멀 플로우차트 렌더러.
흰 배경 + 흑백(#2B2B2B) & 오렌지(#F0511E) + Y/N 다이아몬드 + 직각 화살표 + 상하 오렌지 룰.

스펙(JSON dict)을 받아 SVG 생성 → chromium headless로 PNG 렌더.

Spec schema:
{
  "title": "Bath or shower?",
  "width": 820, "height": 1180,
  "rules": true,                      # 상/하단 오렌지 가로줄
  "boxes": [
     {"id":"q1","x":280,"y":110,"w":260,"h":58,"text":"Do you have a bath?","style":"question"},
     {"id":"a1","x":40,"y":470,"w":210,"h":56,"text":"Have a shower","style":"action"}
  ],
  "diamonds": [ {"x":190,"y":210,"label":"N"}, {"x":560,"y":210,"label":"Y"} ],
  "edges": [ {"points":[[410,168],[410,196]],"color":"black","arrow":false},
             {"points":[[190,224],[190,300],[160,300]],"color":"black","arrow":true} ]
}
styles: question(dark border/text), action(orange border/text), plain
diamond label "Y"=orange fill, "N"=dark fill (white letter)
edge color: "black"(#2B2B2B) or "orange"(#F0511E)
"""
import argparse, json, os, subprocess, sys, tempfile

DARK = "#2B2B2B"
ORANGE = "#F0511E"
WHITE = "#FFFFFF"
FONT = "Helvetica, Arial, 'Liberation Sans', sans-serif"


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def box_svg(b):
    style = b.get("style", "question")
    stroke = ORANGE if style == "action" else DARK
    tcolor = ORANGE if style == "action" else DARK
    x, y, w, h = b["x"], b["y"], b["w"], b["h"]
    fs = b.get("font_size", 22)
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" ry="2" '
        f'fill="{WHITE}" stroke="{stroke}" stroke-width="2"/>'
        f'<text x="{x + w/2:.1f}" y="{y + h/2:.1f}" fill="{tcolor}" '
        f'font-family="{FONT}" font-size="{fs}" text-anchor="middle" '
        f'dominant-baseline="central">{esc(b["text"])}</text>'
    )


def diamond_svg(d):
    cx, cy = d["x"], d["y"]
    r = d.get("r", 16)
    label = d.get("label", "Y").upper()
    fill = ORANGE if label == "Y" else DARK
    pts = f"{cx},{cy-r} {cx+r},{cy} {cx},{cy+r} {cx-r},{cy}"
    return (
        f'<polygon points="{pts}" fill="{fill}"/>'
        f'<text x="{cx}" y="{cy}" fill="{WHITE}" font-family="{FONT}" '
        f'font-size="14" font-weight="bold" text-anchor="middle" '
        f'dominant-baseline="central">{label}</text>'
    )


def edge_svg(e):
    color = ORANGE if e.get("color") == "orange" else DARK
    pts = " ".join(f"{p[0]},{p[1]}" for p in e["points"])
    marker = ""
    if e.get("arrow", True):
        marker = f' marker-end="url(#arrow-{ "o" if color==ORANGE else "d" })"'
    return (
        f'<polyline points="{pts}" fill="none" stroke="{color}" '
        f'stroke-width="2" stroke-linejoin="miter"{marker}/>'
    )


def build_svg(spec):
    W = spec.get("width", 820)
    H = spec.get("height", 1180)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}">',
        f'<rect width="{W}" height="{H}" fill="{WHITE}"/>',
        '<defs>',
        f'<marker id="arrow-d" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" '
        f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{DARK}"/></marker>',
        f'<marker id="arrow-o" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" '
        f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{ORANGE}"/></marker>',
        '</defs>',
    ]
    if spec.get("rules", True):
        parts.append(f'<rect x="40" y="34" width="{W-80}" height="5" fill="{ORANGE}"/>')
        parts.append(f'<rect x="40" y="{H-44}" width="{W-80}" height="5" fill="{ORANGE}"/>')
    if spec.get("title"):
        parts.append(
            f'<text x="{W/2:.1f}" y="72" fill="{DARK}" font-family="{FONT}" '
            f'font-size="30" text-anchor="middle">{esc(spec["title"])}</text>'
        )
    for e in spec.get("edges", []):
        parts.append(edge_svg(e))
    for b in spec.get("boxes", []):
        parts.append(box_svg(b))
    for d in spec.get("diamonds", []):
        parts.append(diamond_svg(d))
    parts.append('</svg>')
    return "\n".join(parts)


def render_png(spec, out_png):
    # NOTE: snap chromium cannot write to /tmp — use a HOME-based work dir,
    # then copy the result to the requested output path.
    import shutil
    from shutil import which
    W = spec.get("width", 820)
    H = spec.get("height", 1180)
    svg = build_svg(spec)
    html = (
        f'<!DOCTYPE html><html><head><meta charset="utf-8">'
        f'<style>html,body{{margin:0;padding:0;background:{WHITE}}}</style></head>'
        f'<body>{svg}</body></html>'
    )
    work = os.path.expanduser("~/2lab.ai/.tmp-render")
    os.makedirs(work, exist_ok=True)
    base = f"fc_{os.getpid()}"
    html_path = os.path.join(work, base + ".html")
    png_path = os.path.join(work, base + ".png")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    chromium = next((c for c in ("chromium-browser", "chromium", "google-chrome") if which(c)), None)
    if not chromium:
        raise RuntimeError("no chromium found")

    err = ""
    for headless in ("--headless=new", "--headless"):
        if os.path.exists(png_path):
            os.unlink(png_path)
        cmd = [
            chromium, headless, "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
            "--force-device-scale-factor=2", "--default-background-color=FFFFFFFF",
            f"--screenshot={png_path}", f"--window-size={W},{H}", f"file://{html_path}",
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        err = r.stderr[-400:]
        if os.path.exists(png_path) and os.path.getsize(png_path) > 1000:
            shutil.copy(png_path, out_png)
            try:
                os.unlink(html_path); os.unlink(png_path)
            except OSError:
                pass
            return out_png
    raise RuntimeError(f"chromium render failed: {err}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", help="JSON spec file")
    ap.add_argument("--example", action="store_true", help="render bath/shower example")
    ap.add_argument("--output", "-o", default="/tmp/flowchart.png")
    args = ap.parse_args()

    if args.example or not args.spec:
        spec = bath_shower_spec()
    else:
        with open(args.spec, encoding="utf-8") as f:
            spec = json.load(f)
    out = render_png(spec, args.output)
    print(f"OK -> {out}")


def bath_shower_spec():
    """How to Adult — 'Bath or shower?' (faithful clean re-render)."""
    return {
        "title": "Bath or shower?",
        "width": 860, "height": 1220, "rules": True,
        "boxes": [
            {"id": "q1", "x": 300, "y": 110, "w": 260, "h": 58, "text": "Do you have a bath?", "style": "question"},
            {"id": "q2", "x": 55,  "y": 320, "w": 300, "h": 58, "text": "Do you have a shower?", "style": "question", "font_size": 20},
            {"id": "q3", "x": 560, "y": 320, "w": 200, "h": 58, "text": "Stressed?", "style": "question"},
            {"id": "a_shower1", "x": 60, "y": 520, "w": 220, "h": 56, "text": "Have a shower", "style": "action"},
            {"id": "a_sink", "x": 60, "y": 640, "w": 220, "h": 56, "text": "Wash in a sink", "style": "action"},
            {"id": "a_bath1", "x": 470, "y": 520, "w": 200, "h": 56, "text": "Have a bath", "style": "action"},
            {"id": "q4", "x": 530, "y": 640, "w": 300, "h": 58, "text": "Do you have a shower?", "style": "question", "font_size": 20},
            {"id": "a_shower2", "x": 470, "y": 860, "w": 220, "h": 56, "text": "Have a shower", "style": "action"},
            {"id": "a_bath2", "x": 470, "y": 980, "w": 200, "h": 56, "text": "Have a bath", "style": "action"},
        ],
        "diamonds": [
            {"x": 195, "y": 250, "label": "N"},   # q1 -> q2
            {"x": 560, "y": 250, "label": "Y"},   # q1 -> q3
            {"x": 120, "y": 440, "label": "Y"},   # q2 -> shower
            {"x": 240, "y": 440, "label": "N"},   # q2 -> sink
            {"x": 540, "y": 440, "label": "Y"},   # q3 -> bath
            {"x": 665, "y": 440, "label": "N"},   # q3 -> q4
            {"x": 600, "y": 770, "label": "Y"},   # q4 -> shower2
            {"x": 720, "y": 770, "label": "N"},   # q4 -> bath2
        ],
        "edges": [
            # q1 down split
            {"points": [[430, 168], [430, 210], [195, 210], [195, 234]], "color": "black"},
            {"points": [[430, 168], [430, 210], [560, 210], [560, 234]], "color": "orange"},
            {"points": [[195, 266], [195, 320]], "color": "black"},        # to q2
            {"points": [[560, 266], [560, 320]], "color": "orange"},       # to q3
            # q2 split
            {"points": [[120, 378], [120, 424]], "color": "orange"},
            {"points": [[240, 378], [240, 424]], "color": "black"},
            {"points": [[120, 456], [120, 520]], "color": "orange"},       # -> shower1
            {"points": [[240, 456], [240, 600], [170, 600], [170, 640]], "color": "black"},  # -> sink
            # q3 split
            {"points": [[540, 378], [540, 424]], "color": "orange"},
            {"points": [[665, 378], [665, 424]], "color": "black"},
            {"points": [[540, 456], [540, 520]], "color": "orange"},       # -> bath1
            {"points": [[665, 456], [665, 600], [685, 600], [685, 640]], "color": "black"},  # -> q4
            # q4 split
            {"points": [[600, 698], [600, 744]], "color": "orange"},
            {"points": [[720, 698], [720, 744]], "color": "black"},
            {"points": [[600, 786], [600, 860]], "color": "orange"},       # -> shower2
            {"points": [[720, 786], [720, 940], [620, 940], [620, 980]], "color": "black"},  # -> bath2
        ],
    }


if __name__ == "__main__":
    main()
