"""Reusable colour art for covers: patterns, sample grids, badges, page previews."""
import math
from pathlib import Path

from wordsearch import generate


def snow_pattern(color="#ffffff", opacity=0.09, size=90):
    flake = []
    for k in range(6):
        a = math.radians(k * 60)
        flake.append(f'<line x1="0" y1="0" x2="{14*math.cos(a):.1f}" y2="{14*math.sin(a):.1f}"/>')
    f = f'<g stroke="{color}" stroke-width="2.2" stroke-linecap="round">{"".join(flake)}</g>'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
           f'<g opacity="{opacity}"><g transform="translate(22 24)">{f}</g><g transform="translate(68 66) scale(0.6)">{f}</g>'
           f'<circle cx="70" cy="20" r="2.6" fill="{color}"/><circle cx="20" cy="72" r="2" fill="{color}"/></g></svg>')
    import base64
    return "url('data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode() + "')"


def sample_grid(words, size=9, colors=("#2f8a50", "#d22d36", "#e7a92b", "#2a6fb0"), seed=3, cell=40, font=26,
                ink="#1d1d1d", family="Atkinson"):
    grid, placed = generate(words, size=size, seed=seed)
    W = size * cell
    out = [f'<svg viewBox="0 0 {W} {W}" width="100%">']
    for k, p in enumerate(placed):
        L = len(p["clean"]) - 1
        x1, y1 = p["c"] * cell + cell / 2, p["r"] * cell + cell / 2
        x2, y2 = x1 + p["dc"] * L * cell, y1 + p["dr"] * L * cell
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{colors[k % len(colors)]}" stroke-width="{cell*0.8}" '
                   f'stroke-linecap="round" opacity="0.38"/>')
    for r in range(size):
        for c in range(size):
            out.append(f'<text x="{c*cell+cell/2}" y="{r*cell+cell/2+font*0.36}" text-anchor="middle" font-family="{family}" '
                       f'font-weight="700" font-size="{font}" fill="{ink}">{grid[r][c]}</text>')
    out.append("</svg>")
    return "".join(out)


def burst(points=16, r1=100, r2=78, fill="#f2c14e", stroke="none"):
    pts = []
    for k in range(points * 2):
        r = r1 if k % 2 == 0 else r2
        a = math.pi * k / points - math.pi / 2
        pts.append(f"{r*math.cos(a):.1f},{r*math.sin(a):.1f}")
    return f'<svg viewBox="-102 -102 204 204" width="100%"><polygon points="{" ".join(pts)}" fill="{fill}" stroke="{stroke}"/></svg>'


def page_png(interior_pdf, page_no, out_png, width_px=900):
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(str(interior_pdf))
    pg = doc[page_no - 1]
    img = pg.render(scale=width_px / pg.get_width()).to_pil()
    img.save(out_png)
    return Path(out_png).resolve().as_uri()


def check(color="#f2c14e"):
    return (f'<svg viewBox="0 0 24 24" width="18" height="18" style="flex:none;margin-top:3px"><circle cx="12" cy="12" r="11" fill="{color}"/>'
            '<path d="M6.5 12.5l3.5 3.5 7.5-8" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')
