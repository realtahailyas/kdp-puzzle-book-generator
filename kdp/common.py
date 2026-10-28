"""Shared helpers: KDP page geometry, HTML page shell, Chrome HTML->PDF."""
import html
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONTS = Path(os.environ.get("KDP_FONTS_DIR", ROOT / "assets" / "fonts"))


def find_chrome():
    """Chrome/Chromium used for HTML -> PDF. Override with the CHROME_PATH environment variable."""
    env = os.environ.get("CHROME_PATH")
    if env:
        return env
    for name in ("chrome", "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "msedge"):
        found = shutil.which(name)
        if found:
            return found
    for c in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
              "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"):
        if Path(c).exists():
            return c
    raise FileNotFoundError("Chrome/Chromium not found. Install it or set CHROME_PATH.")


TRIM_W, TRIM_H = 8.5, 11.0          # inches, interior trim (no bleed)
INSIDE, OUTSIDE, TOP, BOTTOM = 0.75, 0.5, 0.55, 0.6
SPINE_PER_PAGE_WHITE = 0.002252     # KDP white paper, inches per page
BLEED = 0.125


def esc(s):
    return html.escape(str(s))


def font_css():
    f = FONTS.as_uri()
    faces = [
        ("Atkinson", "AtkinsonHyperlegible-Regular.ttf", 400, "normal"),
        ("Atkinson", "AtkinsonHyperlegible-Bold.ttf", 700, "normal"),
        ("Atkinson", "AtkinsonHyperlegible-Italic.ttf", 400, "italic"),
        ("Playfair", "Playfair-Regular.ttf", 400, "normal"),
        ("Playfair", "Playfair-Bold.ttf", 700, "normal"),
        ("Playfair", "Playfair-ExtraBold.ttf", 800, "normal"),
        ("Playfair", "Playfair-Black.ttf", 900, "normal"),
        ("Playfair", "Playfair-Italic.ttf", 400, "italic"),
        ("Playfair", "Playfair-BoldItalic.ttf", 700, "italic"),
        ("Lora", "Lora-Regular.ttf", 400, "normal"),
        ("Lora", "Lora-Bold.ttf", 700, "normal"),
        ("Lora", "Lora-Italic.ttf", 400, "italic"),
        ("Lora", "Lora-SemiBoldItalic.ttf", 600, "italic"),
        ("Courier Prime", "CourierPrime-Regular.ttf", 400, "normal"),
        ("Courier Prime", "CourierPrime-Bold.ttf", 700, "normal"),
        ("Abril", "AbrilFatface-Regular.ttf", 400, "normal"),
        ("Oswald", "Oswald-Medium.ttf", 500, "normal"),
        ("Oswald", "Oswald-Bold.ttf", 700, "normal"),
        ("Lilita", "LilitaOne-Regular.ttf", 400, "normal"),
        ("Fredoka", "Fredoka-Regular.ttf", 400, "normal"),
        ("Fredoka", "Fredoka-SemiBold.ttf", 600, "normal"),
        ("Fredoka", "Fredoka-Bold.ttf", 700, "normal"),
        ("Great Vibes", "GreatVibes-Regular.ttf", 400, "normal"),
    ]
    # 'Easy' = Atkinson Hyperlegible letters + Fredoka digits (Atkinson's zero is slashed, which can confuse older readers)
    no_digits = "U+0000-002F,U+003A-FFFF"
    faces += [
        ("Easy", "AtkinsonHyperlegible-Regular.ttf", 400, "normal", no_digits),
        ("Easy", "AtkinsonHyperlegible-Bold.ttf", 700, "normal", no_digits),
        ("Easy", "AtkinsonHyperlegible-Italic.ttf", 400, "italic", no_digits),
        ("Easy", "Fredoka-Regular.ttf", 400, "normal", "U+0030-0039"),
        ("Easy", "Fredoka-Bold.ttf", 700, "normal", "U+0030-0039"),
        ("Easy", "Fredoka-Regular.ttf", 400, "italic", "U+0030-0039"),
    ]
    out = []
    for fam, file, wt, st, *rng in faces:
        if not (FONTS / file).exists():
            continue  # optional face not installed; the browser falls back to the next font
        url = f"{f}/{file}".replace("[", "%5B").replace("]", "%5D")
        ur = f"unicode-range:{rng[0]};" if rng else ""
        out.append(f"@font-face{{font-family:'{fam}';src:url('{url}');font-weight:{wt};font-style:{st};{ur}}}")
    return "\n".join(out)


BASE_CSS = """
@page { size: 8.5in 11in; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { background: #fff; color: #111; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { width: 8.5in; height: 11in; position: relative; overflow: hidden; page-break-after: always; break-after: page; }
.page:last-child { page-break-after: auto; break-after: auto; }
.inner { position: absolute; top: %(top)sin; bottom: %(bottom)sin; display: flex; flex-direction: column; }
.odd .inner { left: %(inside)sin; right: %(outside)sin; }
.even .inner { left: %(outside)sin; right: %(inside)sin; }
.folio { position: absolute; bottom: 0.3in; width: 100%%; text-align: center; font: 11pt 'Lora'; color: #555; }
""" % dict(top=TOP, bottom=BOTTOM, inside=INSIDE, outside=OUTSIDE)


class Book:
    """Collects pages; page 1 is a recto (odd) page."""

    def __init__(self, css=""):
        self.pages, self.css = [], css

    def add(self, body, folio=True, cls=""):
        n = len(self.pages) + 1
        side = "odd" if n % 2 else "even"
        fol = f'<div class="folio">{n}</div>' if folio else ""
        self.pages.append(f'<section class="page {side} {cls}"><div class="inner">{body}</div>{fol}</section>')
        return n

    def blank(self):
        self.pages.append('<section class="page"></section>')

    def pad_even(self):
        if len(self.pages) % 2:
            self.blank()

    def html(self, title):
        return (f"<!doctype html><html><head><meta charset='utf-8'><title>{esc(title)}</title>"
                f"<style>{font_css()}{BASE_CSS}{self.css}</style></head><body>{''.join(self.pages)}</body></html>")


def html_to_pdf(html_path, pdf_path, timeout=600):
    html_path, pdf_path = Path(html_path).resolve(), Path(pdf_path).resolve()
    cmd = [find_chrome(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
           "--virtual-time-budget=20000", f"--print-to-pdf={pdf_path}", html_path.as_uri()]
    subprocess.run(cmd, check=True, timeout=timeout, capture_output=True)
    # Chrome writes bloated PDFs (158 pages -> 10.6 MB); a clean re-save brings them to ~2.6 MB with identical content
    try:
        import pymupdf
        tmp = pdf_path.with_suffix(".tmp.pdf")
        doc = pymupdf.open(pdf_path)
        doc.save(tmp, garbage=4, deflate=True, deflate_fonts=True, use_objstms=1)
        doc.close()
        tmp.replace(pdf_path)
    except ImportError:
        pass
    return pdf_path


def spine_width(pages):
    return pages * SPINE_PER_PAGE_WHITE


def cover_size(pages, trim_w=TRIM_W, trim_h=TRIM_H):
    """Full-wrap cover dimensions (inches) including bleed."""
    s = spine_width(pages)
    return 2 * trim_w + s + 2 * BLEED, trim_h + 2 * BLEED, s
