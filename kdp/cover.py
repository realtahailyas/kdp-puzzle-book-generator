"""Full-wrap paperback cover (back + spine + front) as HTML -> PDF at exact KDP size."""
from pathlib import Path

from common import BLEED, TRIM_H, TRIM_W, cover_size, font_css, html_to_pdf

COVER_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.wrap { position: relative; overflow: hidden; }
.panel { position: absolute; top: 0; overflow: hidden; }
.safe { position: absolute; }
"""


def build_cover(out_dir, pages, back_html, spine_html, front_html, bg_css, extra_css="", title="cover"):
    W, H, s = cover_size(pages)
    back_w = BLEED + TRIM_W
    css = (f"@page {{ size: {W:.4f}in {H:.4f}in; margin: 0; }}" + COVER_CSS +
           f".wrap {{ width: {W:.4f}in; height: {H:.4f}in; {bg_css} }}"
           f".back {{ left: 0; width: {back_w:.4f}in; height: {H:.4f}in; }}"
           f".spine {{ left: {back_w:.4f}in; width: {s:.4f}in; height: {H:.4f}in; }}"
           f".front {{ left: {back_w + s:.4f}in; width: {back_w:.4f}in; height: {H:.4f}in; }}"
           # safe areas: 0.25in inside trim (+ bleed on outer edges)
           f".back .safe {{ left: {BLEED + 0.375:.4f}in; right: 0.5in; top: {BLEED + 0.375:.4f}in; bottom: {BLEED + 0.375:.4f}in; }}"
           f".front .safe {{ left: 0.5in; right: {BLEED + 0.375:.4f}in; top: {BLEED + 0.375:.4f}in; bottom: {BLEED + 0.375:.4f}in; }}"
           + extra_css)
    html = (f"<!doctype html><html><head><meta charset='utf-8'><title>{title}</title><style>{font_css()}{css}</style></head><body>"
            f"<div class='wrap'><div class='panel back'>{back_html}</div><div class='panel spine'>{spine_html}</div>"
            f"<div class='panel front'>{front_html}</div></div></body></html>")
    out_dir = Path(out_dir)
    hp = out_dir / "cover.html"
    hp.write_text(html, encoding="utf-8")
    pdf = html_to_pdf(hp, out_dir / "cover.pdf")
    _exact_size(pdf, W, H)
    return pdf, (W, H, s)


def _exact_size(pdf, W, H):
    """Chrome rounds the page size by a hair; pin the boxes to the exact KDP dimensions."""
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import RectangleObject
    r = PdfReader(str(pdf))
    w = PdfWriter()
    for pg in r.pages:
        box = RectangleObject([0, 0, round(W * 72, 3), round(H * 72, 3)])
        pg.mediabox = box
        pg.cropbox = box
        w.add_page(pg)
    with open(pdf, "wb") as fh:
        w.write(fh)


def front_png(cover_pdf, pages, out_png, width_px=1600):
    """Crop the front panel (trim only) from the cover PDF for thumbnails / marketing."""
    import pypdfium2 as pdfium
    W, H, s = cover_size(pages)
    doc = pdfium.PdfDocument(str(cover_pdf))
    page = doc[0]
    scale = width_px / (TRIM_W * 72)
    img = page.render(scale=scale).to_pil()
    px = img.width / W
    x0 = (BLEED + TRIM_W + s) * px
    box = (round(x0), round(BLEED * px), round(x0 + TRIM_W * px), round((BLEED + TRIM_H) * px))
    img.crop(box).save(out_png)
    return out_png
