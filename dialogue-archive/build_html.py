#!/usr/bin/env python3
"""
dialogue-archive: markdown 대화록 -> 메신저 스타일 블로그 HTML 변환기.

입력 형식 (RAW 또는 EDITED .md):
  # 제목
  **메타:** ...
  ---
  ## [HH:MM] 화자
  본문(markdown: ###, ####, **bold**, > quote, - list, `code`, 단락)
  ---
  ## [HH:MM] 화자
  ...

사용:
  python3 build_html.py <input.md> <output.html> [--right 화자이름]

--right 로 지정한 화자는 오른쪽(파란 말풍선), 나머지는 왼쪽(회색).
기본 right = "지혁".
"""
import sys, re, html, datetime

def md_inline(s: str) -> str:
    s = html.escape(s)
    # `code`
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    # **bold**
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    # *italic*
    s = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', s)
    return s

def md_block(body: str) -> str:
    """아주 가벼운 markdown -> html (대화 본문용)."""
    lines = body.split('\n')
    out, i = [], 0
    list_open = False
    def close_list():
        nonlocal list_open
        if list_open:
            out.append('</ul>')
            list_open = False
    while i < len(lines):
        ln = lines[i]
        raw = ln.rstrip()
        if not raw.strip():
            close_list(); i += 1; continue
        # headings
        m = re.match(r'^(#{2,4})\s+(.*)$', raw)
        if m:
            close_list()
            lvl = len(m.group(1))
            tag = {2: 'h3', 3: 'h4', 4: 'h5'}.get(lvl, 'h5')
            out.append(f'<{tag}>{md_inline(m.group(2))}</{tag}>')
            i += 1; continue
        # blockquote (연속 줄 묶기)
        if raw.lstrip().startswith('>'):
            close_list()
            q = []
            while i < len(lines) and lines[i].lstrip().startswith('>'):
                q.append(re.sub(r'^\s*>\s?', '', lines[i]))
                i += 1
            out.append('<blockquote>' + '<br>'.join(md_inline(x) for x in q) + '</blockquote>')
            continue
        # list
        if re.match(r'^\s*[-*]\s+', raw):
            if not list_open:
                out.append('<ul>'); list_open = True
            item = re.sub(r'^\s*[-*]\s+', '', raw)
            out.append(f'<li>{md_inline(item)}</li>')
            i += 1; continue
        # paragraph (연속 비공백 줄 묶기)
        close_list()
        para = [raw]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r'^\s*[-*>#]', lines[i]) \
              and not re.match(r'^(#{2,4})\s', lines[i]):
            para.append(lines[i].rstrip()); i += 1
        out.append('<p>' + '<br>'.join(md_inline(x) for x in para) + '</p>')
    close_list()
    return '\n'.join(out)

HEADER_RE = re.compile(r'^##(?!#)\s*(?:\[([^\]]+)\]\s*)?(.+?)\s*$')

def parse(md: str):
    """화자 헤더(`## [HH:MM] 화자`) 기준으로 메시지를 분리.
    메시지 본문 안의 `---` 수평선과 충돌하지 않는다."""
    lines = md.split('\n')
    # 제목
    title = '대화록'
    for l in lines:
        m = re.match(r'^#\s+(.*)$', l)
        if m:
            title = m.group(1).strip(); break
    msgs, cur = [], None
    preamble = []
    for ln in lines:
        h = HEADER_RE.match(ln)
        if h:
            if cur:
                msgs.append(cur)
            cur = {'time': (h.group(1) or '').strip(),
                   'who': h.group(2).strip(), 'body': [], 'note': False}
        elif cur is not None:
            cur['body'].append(ln)
        else:
            preamble.append(ln)
    if cur:
        msgs.append(cur)
    for m in msgs:
        # 본문 안 단독 --- 수평선 제거, 앞뒤 공백 정리
        body = '\n'.join(l for l in m['body'] if l.strip() != '---')
        m['body'] = body.strip()
    # 메타: 제목 이후 preamble 중 **...** 라인
    meta_lines = [l for l in preamble if l.strip().startswith('**')]
    meta = ' · '.join(re.sub(r'\*\*', '', l).strip() for l in meta_lines)
    return title, meta, msgs

TEMPLATE = """<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  :root{{
    --bg:#0b0f14; --panel:#11161d; --me:#2b6cff; --me2:#1f57d6;
    --you:#1c232c; --you-bd:#283543; --txt:#e7edf3; --mut:#8a97a6;
    --quote:#1a222b; --accent:#5aa2ff;
  }}
  *{{box-sizing:border-box}}
  body{{margin:0;background:var(--bg);color:var(--txt);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Apple SD Gothic Neo","Noto Sans KR",sans-serif;
    line-height:1.62;-webkit-font-smoothing:antialiased}}
  .wrap{{max-width:780px;margin:0 auto;padding:28px 16px 80px}}
  header.page{{text-align:center;padding:26px 10px 20px;border-bottom:1px solid #1d2530;margin-bottom:26px}}
  header.page h1{{font-size:1.5rem;margin:0 0 10px;letter-spacing:-.01em}}
  header.page .meta{{color:var(--mut);font-size:.82rem}}
  .day{{text-align:center;color:var(--mut);font-size:.74rem;margin:18px 0}}
  .row{{display:flex;margin:14px 0;gap:10px;align-items:flex-end}}
  .row.me{{justify-content:flex-end}}
  .avatar{{width:34px;height:34px;border-radius:50%;flex:0 0 34px;display:flex;
    align-items:center;justify-content:center;font-weight:700;font-size:.8rem;color:#fff}}
  .av-you{{background:linear-gradient(135deg,#3a4a5e,#222d3a)}}
  .av-me{{background:linear-gradient(135deg,#2b6cff,#1f57d6)}}
  .bubble{{max-width:78%;padding:12px 15px;border-radius:18px;font-size:.95rem;
    word-break:break-word;overflow-wrap:anywhere}}
  .me .bubble{{background:var(--me);border-bottom-right-radius:5px;color:#fff}}
  .you .bubble{{background:var(--you);border:1px solid var(--you-bd);border-bottom-left-radius:5px}}
  .name{{font-size:.72rem;color:var(--mut);margin:0 6px 3px}}
  .time{{font-size:.66rem;color:var(--mut);align-self:flex-end;white-space:nowrap;padding-bottom:3px}}
  .bubble p{{margin:.45em 0}}
  .bubble p:first-child{{margin-top:0}} .bubble p:last-child{{margin-bottom:0}}
  .bubble h3{{font-size:.98rem;margin:.7em 0 .35em;color:var(--accent)}}
  .me .bubble h3{{color:#dce8ff}}
  .bubble h4{{font-size:.9rem;margin:.6em 0 .3em}}
  .bubble h5{{font-size:.85rem;margin:.5em 0 .3em;color:var(--mut)}}
  .bubble ul{{margin:.4em 0;padding-left:1.15em}}
  .bubble li{{margin:.22em 0}}
  .bubble blockquote{{margin:.5em 0;padding:8px 12px;border-left:3px solid var(--accent);
    background:rgba(255,255,255,.05);border-radius:6px;font-style:italic}}
  .me .bubble blockquote{{border-left-color:#cfe0ff;background:rgba(255,255,255,.14)}}
  .bubble code{{background:rgba(255,255,255,.12);padding:1px 5px;border-radius:5px;
    font-size:.85em;font-family:ui-monospace,Menlo,Consolas,monospace}}
  .note{{max-width:100%;margin:22px auto;padding:14px 16px;background:var(--panel);
    border:1px dashed #2b3744;border-radius:12px;color:var(--mut);font-size:.85rem;text-align:center}}
  footer.page{{text-align:center;color:var(--mut);font-size:.72rem;margin-top:40px}}
</style></head>
<body><div class="wrap">
<header class="page"><h1>{title}</h1><div class="meta">{meta}</div></header>
{body}
<footer class="page">archived by dialogue-archive · generated {gen}</footer>
</div></body></html>"""

def render(title, meta, msgs, right_who):
    parts = []
    for m in msgs:
        if m['note']:
            parts.append(f'<div class="note">{md_block(m["body"])}</div>')
            continue
        is_me = (m['who'] == right_who)
        side = 'me' if is_me else 'you'
        av = 'av-me' if is_me else 'av-you'
        initial = html.escape(m['who'][:1]) if m['who'] else '?'
        name = html.escape(m['who'])
        time = html.escape(m['time'])
        bubble = (f'<div style="display:flex;flex-direction:column;max-width:78%">'
                  f'<div class="name" style="text-align:{"right" if is_me else "left"}">{name}</div>'
                  f'<div class="bubble">{md_block(m["body"])}</div></div>')
        avatar = f'<div class="avatar {av}">{initial}</div>'
        tm = f'<span class="time">{time}</span>'
        if is_me:
            row = f'<div class="row me">{tm}{bubble}{avatar}</div>'
        else:
            row = f'<div class="row you">{avatar}{bubble}{tm}</div>'
        parts.append(row)
    gen = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    return TEMPLATE.format(title=html.escape(title), meta=html.escape(meta),
                           body='\n'.join(parts), gen=gen)

def main():
    args = [a for a in sys.argv[1:]]
    right = '지혁'
    if '--right' in args:
        idx = args.index('--right'); right = args[idx+1]; del args[idx:idx+2]
    if len(args) < 2:
        print('usage: build_html.py <input.md> <output.html> [--right NAME]'); sys.exit(1)
    inp, outp = args[0], args[1]
    md = open(inp, encoding='utf-8').read()
    title, meta, msgs = parse(md)
    htmlout = render(title, meta, msgs, right)
    open(outp, 'w', encoding='utf-8').write(htmlout)
    print(f'wrote {outp}  ({len(msgs)} messages, right={right})')

if __name__ == '__main__':
    main()
