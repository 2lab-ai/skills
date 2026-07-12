#!/usr/bin/env python3
"""
beautiful-pdf renderer

Usage:
  render.py --input report.md --output report.pdf \
            --title "Title" --subtitle "Subtitle" \
            --author "Author" --date "2026-05-07" \
            [--theme editorial|minimal|dark] [--toc] [--no-cover]
"""
import argparse
import re
import sys
from pathlib import Path

from markdown_it import MarkdownIt
from weasyprint import HTML, CSS

SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = SKILL_ROOT / "templates"
ASSETS_DIR = SKILL_ROOT / "assets"


def parse_args():
    p = argparse.ArgumentParser(description="beautiful-pdf renderer")
    p.add_argument("--input", required=True, help="Path to markdown source")
    p.add_argument("--output", required=True, help="Path to output PDF")
    p.add_argument("--title", default="", help="Cover title")
    p.add_argument("--subtitle", default="", help="Cover subtitle")
    p.add_argument("--author", default="", help="Cover author / publisher")
    p.add_argument("--date", default="", help="Cover date")
    p.add_argument("--theme", default="editorial", help="editorial / minimal / dark")
    p.add_argument("--toc", action="store_true", help="Include auto-TOC")
    p.add_argument("--no-cover", action="store_true", help="Skip cover page")
    return p.parse_args()


# ---------- callout / divider preprocessor ----------
CALLOUT_RE = re.compile(
    r"^> \[!(?P<kind>[a-zA-Z]+)\]\s*(?P<title>.*?)\n(?P<body>(?:^>.*\n?)+)",
    re.MULTILINE,
)


def preprocess(md_text: str) -> str:
    """Convert > [!kind] Title\n> body... into HTML callouts."""
    def repl(m):
        kind = m.group("kind").lower()
        title = m.group("title").strip() or kind.upper()
        body = re.sub(r"^>\s?", "", m.group("body"), flags=re.MULTILINE).strip()
        body_html_inline = body.replace("\n\n", "</p><p>").replace("\n", " ")
        return (
            f'\n<div class="callout callout-{kind}">'
            f'<span class="callout-title">{title}</span>'
            f'<div class="callout-body"><p>{body_html_inline}</p></div>'
            f'</div>\n\n'
        )

    return CALLOUT_RE.sub(repl, md_text)


# ---------- TOC builder ----------
def build_toc(md_text: str) -> str:
    """Pull H2 lines into a TOC ordered list."""
    items = []
    for m in re.finditer(r"^##\s+(.+)$", md_text, re.MULTILINE):
        items.append(m.group(1).strip())
    if not items:
        return ""
    lis = "\n".join(
        f'  <li><span class="toc-title">{i}</span></li>' for i in items
    )
    return f'''<section class="toc">
  <h2>목차</h2>
  <ol>
{lis}
  </ol>
</section>'''


# ---------- Cover ----------
def build_cover(args) -> str:
    if args.no_cover:
        return ""
    eyebrow = (args.author or "REPORT").upper()
    meta_lines = []
    if args.date:
        meta_lines.append(f"<div><dt>발행일</dt><dd>{args.date}</dd></div>")
    if args.author:
        meta_lines.append(f"<div><dt>발행</dt><dd>{args.author}</dd></div>")
    meta_block = "\n".join(meta_lines)
    return f'''<section class="cover">
  <div>
    <div class="cover-eyebrow">{eyebrow}</div>
    <h1 class="cover-title">{args.title}</h1>
    <p class="cover-subtitle">{args.subtitle}</p>
    <div class="cover-divider"></div>
  </div>
  <div>
    <dl class="cover-meta">
      {meta_block}
    </dl>
    <div class="cover-footer">A Beautiful Report · Generated {args.date}</div>
  </div>
</section>'''


def main():
    args = parse_args()
    md_path = Path(args.input).expanduser().resolve()
    pdf_path = Path(args.output).expanduser().resolve()
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    raw = md_path.read_text(encoding="utf-8")
    pre = preprocess(raw)

    md = MarkdownIt("commonmark", {"html": True, "linkify": True, "typographer": True})
    md.enable(["table", "strikethrough"])
    body_html = md.render(pre)

    css_file = TEMPLATE_DIR / f"{args.theme}.css"
    if not css_file.exists():
        css_file = TEMPLATE_DIR / "default.css"

    cover_html = build_cover(args)
    toc_html = build_toc(raw) if args.toc else ""

    html_doc = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>{args.title or md_path.stem}</title>
</head>
<body>
{cover_html}
{toc_html}
<main class="content">
{body_html}
</main>
</body>
</html>
"""

    base = TEMPLATE_DIR.as_uri() + "/"
    HTML(string=html_doc, base_url=base).write_pdf(
        str(pdf_path),
        stylesheets=[CSS(filename=str(css_file))],
        optimize_size=("fonts", "images"),
    )

    size = pdf_path.stat().st_size
    print(f"WROTE {pdf_path} ({size:,} bytes)")


if __name__ == "__main__":
    main()
