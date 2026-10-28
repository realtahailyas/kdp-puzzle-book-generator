"""Reusable large-print word search book builder (interior PDF)."""
from pathlib import Path

from common import Book, esc, html_to_pdf
from wordsearch import EASY_DIRS, generate, svg

CSS = """
.kicker { font: 700 16pt 'Lora'; letter-spacing: 0.18em; color: #555; text-align: center; text-transform: uppercase; }
.ptitle { font: 800 30pt/1.1 'Playfair'; text-align: center; margin: 2pt 0 8pt; color: #111; }
.prompt { font: italic 16pt/1.32 'Lora'; color: #333; text-align: center; border-top: 1.2pt solid #999;
          border-bottom: 1.2pt solid #999; padding: 6pt 10pt; margin: 0 0.3in 12pt; }
.prompt b { font: 700 16pt 'Atkinson'; font-style: normal; letter-spacing: 0.1em; color: #444; display: block; margin-bottom: 2pt; }
.grid { width: 6.1in; margin: 0 auto; }
.words { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6pt 12pt; margin: 12pt 0 0; }
.words div { font: 700 16.5pt 'Atkinson'; letter-spacing: 0.02em; display: flex; align-items: center; white-space: nowrap; }
.words.long div { font-size: 16pt; letter-spacing: 0; }
.words div::before { content: ''; width: 11pt; height: 11pt; border: 1.6pt solid #333; border-radius: 3pt; margin-right: 7pt; flex: none; }
.sol-head { font: 800 24pt 'Playfair'; text-align: center; margin-bottom: 10pt; }
.sols { display: grid; grid-template-columns: 1fr; grid-template-rows: 1fr 1fr; gap: 14pt; flex: 1; min-height: 0; }
.sol { display: flex; flex-direction: column; align-items: center; min-height: 0; }
.sol p { font: 700 16pt 'Lora'; text-align: center; margin-bottom: 4pt; }
.sol .g { width: 4.1in; }
.center { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
.big { font: 900 44pt/1.08 'Playfair'; }
.sub { font: italic 20pt/1.3 'Lora'; color: #333; margin-top: 14pt; }
.brand { font: 700 16pt 'Lora'; letter-spacing: 0.3em; text-transform: uppercase; color: #444; }
.body { font: 16pt/1.5 'Lora'; color: #222; }
.body h2 { font: 800 26pt 'Playfair'; margin: 0 0 12pt; text-align: center; }
.body p { margin-bottom: 10pt; }
.body ul { margin: 0 0 10pt 22pt; } .body li { margin-bottom: 6pt; }
.legal { font: 16pt/1.45 'Lora'; color: #333; }
.folio { font-size: 16pt !important; }
.lines div { border-bottom: 1pt solid #888; height: 0.42in; }
.toc div { display: flex; font: 17pt 'Lora'; margin-bottom: 12pt; }
.toc span.dots { flex: 1; border-bottom: 2pt dotted #999; margin: 0 8pt 6pt; }
"""


def snowflake(size=40, color="#666", sw=2.2):
    import math
    c, r = size / 2, size / 2 - 2
    parts = []
    for k in range(6):
        a = math.radians(k * 60)
        x, y = c + r * math.cos(a), c + r * math.sin(a)
        parts.append(f'<line x1="{c}" y1="{c}" x2="{x:.1f}" y2="{y:.1f}"/>')
        for f in (0.55,):
            bx, by = c + r * f * math.cos(a), c + r * f * math.sin(a)
            for s in (-1, 1):
                b = a + s * math.radians(40)
                parts.append(f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{bx + r*0.32*math.cos(b):.1f}" y2="{by + r*0.32*math.sin(b):.1f}"/>')
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}"><g stroke="{color}" stroke-width="{sw}" '
            f'stroke-linecap="round">{"".join(parts)}</g></svg>')


def build(cfg, out_dir):
    """cfg: title, subtitle, brand, puzzles[(title, prompt, words)], prompt_label, ornament(svg str),
    intro_paragraphs, end_title, memory_title"""
    out_dir = Path(out_dir)
    book = Book(CSS)
    orn = cfg.get("ornament", snowflake())
    n_puz = len(cfg["puzzles"])

    # 1 title page
    book.add(f'<div class="center">{orn}<div style="height:18pt"></div><div class="big">{cfg["title_html"]}</div>'
             f'<div class="sub">{esc(cfg["subtitle"])}</div><div style="height:60pt"></div>{orn}</div>'
             f'<div class="brand" style="text-align:center">{esc(cfg["brand"])}</div>', folio=False)
    # 2 copyright
    book.add(f'<div style="flex:1"></div><div class="legal"><p><b>{esc(cfg["title_plain"])}</b><br>{esc(cfg["subtitle"])}</p><br>'
             f'<p>Copyright © 2026 {esc(cfg["brand"])}. All rights reserved.</p><br>'
             '<p>No part of this book may be reproduced, stored, or transmitted in any form or by any means without '
             'written permission from the publisher, except for brief quotations in reviews.</p><br>'
             '<p>Puzzle grids are original and were created for this book. Every effort has been made to ensure the '
             'puzzles and solutions are accurate.</p><br><p>First edition, 2026</p></div>', folio=False)
    # 3 welcome / how to play
    intro = "".join(f"<p>{p}</p>" for p in cfg["intro_paragraphs"])
    sol_page = 5 + n_puz
    ex = cfg.get("example") or next(w for _, _, ws in cfg["puzzles"] for w in ws if " " in w and "'" not in w)
    book.add(f'<div class="body"><h2>Welcome!</h2>{intro}<h2 style="margin-top:18pt">How to Play</h2><ul>'
             '<li>Each puzzle has a list of words hidden in the grid.</li>'
             '<li>Words run <b>across</b>, <b>down</b>, or <b>diagonally</b>.</li>'
             '<li>Every word reads <b>forward</b> — no backward words to strain over!</li>'
             f'<li>Spaces and punctuation are left out of the grid. "{esc(ex)}" is hidden as {esc(ex.replace(" ", ""))}.</li>'
             '<li>Circle each word you find and tick its box in the list.</li></ul>'
             f'<p>Stuck? Solutions start on page {sol_page}.</p>'
             '<div style="margin-top:22pt;font:700 16pt Lora">This book belongs to:</div>'
             '<div class="lines" style="margin-top:6pt"><div></div></div></div>')
    # 4 contents
    mem_page = sol_page + (n_puz + 1) // 2
    book.add('<div class="body"><h2>Contents</h2></div><div class="toc" style="margin-top:20pt">'
             f'<div>Welcome &amp; How to Play<span class="dots"></span>3</div>'
             f'<div>Puzzles 1 – {n_puz}<span class="dots"></span>5</div>'
             f'<div>Solutions<span class="dots"></span>{sol_page}</div>'
             f'<div>{esc(cfg["memory_title"])}<span class="dots"></span>{mem_page}</div></div>'
             f'<div style="flex:1"></div><div style="text-align:center">{orn}</div>')

    # puzzles
    solved = []
    for i, (t, prompt, words) in enumerate(cfg["puzzles"], 1):
        grid, placed = generate(words, size=cfg.get("size", 14), dirs=EASY_DIRS, seed=cfg.get("seed", 7) * 1000 + i)
        solved.append((i, t, grid, placed))
        wl = "".join(f"<div>{esc(w)}</div>" for w in sorted(words, key=lambda w: w.replace(' ', '')))
        book.add(f'<div class="kicker">Puzzle {i}</div><div class="ptitle">{esc(t)}</div>'
                 f'<div class="prompt"><b>{esc(cfg["prompt_label"])}</b>{esc(prompt)}</div>'
                 f'<div class="grid">{svg(grid)}</div><div class="words{" long" if max(map(len, words)) > 13 else ""}">{wl}</div>')

    # solutions, 2 per page (large print: letters stay 16 pt or bigger)
    for k in range(0, len(solved), 2):
        cells = "".join(f'<div class="sol"><p>Puzzle {i} · {esc(t)}</p><div class="g">{svg(g, pl, show=True, font=28)}</div></div>'
                        for i, t, g, pl in solved[k:k + 2])
        book.add(f'<div class="sol-head">Solutions</div><div class="sols">{cells}</div>')

    # memory pages
    lines = '<div class="lines">' + "<div></div>" * 17 + "</div>"
    book.add(f'<div class="body"><h2>{esc(cfg["memory_title"])}</h2><p style="text-align:center;font-style:italic;'
             f'font-family:Lora">{esc(cfg["memory_prompt"])}</p></div>{lines}')
    book.add(f'<div class="body"><h2>{esc(cfg["memory_title"])}</h2></div>' + '<div class="lines">' + "<div></div>" * 19 + "</div>")
    # thank you page
    book.add(f'<div class="center"><div class="body" style="max-width:6in"><h2>{esc(cfg["end_title"])}</h2>'
             '<p>We hope these puzzles brought you many relaxing, happy hours.</p>'
             '<p>If you enjoyed this book, would you consider leaving a short review on Amazon? '
             'Reviews help small publishers like us more than you might imagine, and they help other puzzle lovers '
             'find books they will enjoy.</p>'
             f'<p style="margin-top:18pt"><b>Look for more large print books from {esc(cfg["brand"])}.</b></p></div>'
             f'<div style="height:24pt"></div>{orn}</div>')
    book.pad_even()

    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / "interior.html"
    html_path.write_text(book.html(cfg["title_plain"]), encoding="utf-8")
    pdf = html_to_pdf(html_path, out_dir / "interior.pdf")
    return pdf, len(book.pages), solved
