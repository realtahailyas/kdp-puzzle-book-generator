"""Pre-upload QA for book folders: interior + cover geometry, fonts, margins, barcode zone, listing limits.
Usage: python qa.py book_dir [book_dir ...]
A book folder holds interior.pdf, optionally cover.pdf, listing.md and build_info.json (checks for missing files are skipped)."""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pypdfium2 as pdfium
from pypdf import PdfReader

from common import BLEED, TRIM_H, TRIM_W, cover_size

DPI = 60
EDGE, GUTTER = 0.25, 0.375   # KDP minimums (no bleed, 24-150 pages)


def fonts_ok(reader):
    bad = set()
    for p in reader.pages:
        res = p.get("/Resources") or {}
        for _, f in (res.get("/Font") or {}).items():
            f = f.get_object()
            if f.get("/Subtype") == "/Type3":
                bad.add("Type3"); continue
            d = f.get("/FontDescriptor")
            if d is None and "/DescendantFonts" in f:
                d = f["/DescendantFonts"][0].get_object().get("/FontDescriptor")
            d = d.get_object() if d is not None else {}
            if not any(x in d for x in ("/FontFile", "/FontFile2", "/FontFile3")):
                bad.add(str(f.get("/BaseFont")))
    return bad


def interior(book):
    pdf = book / "interior.pdf"
    r = PdfReader(str(pdf))
    errs = []
    n = len(r.pages)
    if n % 2:
        errs.append(f"odd page count {n}")
    for i, p in enumerate(r.pages):
        w, h = float(p.mediabox.width) / 72, float(p.mediabox.height) / 72
        if abs(w - TRIM_W) > 0.01 or abs(h - TRIM_H) > 0.01:
            errs.append(f"page {i + 1} size {w:.3f}x{h:.3f}")
            break
    bad = fonts_ok(r)
    if bad:
        errs.append(f"fonts not embedded: {bad}")
    doc = pdfium.PdfDocument(str(pdf))
    e, g = round(EDGE * DPI), round(GUTTER * DPI)
    for i in range(n):
        a = np.asarray(doc[i].render(scale=DPI / 72).to_pil().convert("L"))
        ink = a < 200
        H, W = ink.shape
        odd = (i + 1) % 2 == 1
        outer = ink[:, W - e:] if odd else ink[:, :e]
        inner = ink[:, :g] if odd else ink[:, W - g:]
        if ink[:e].any() or ink[H - e:].any() or outer.any() or inner.any():
            errs.append(f"page {i + 1}: ink inside the {EDGE}in edge / {GUTTER}in gutter band")
    return n, errs


def cover(book, pages):
    pdf = book / "cover.pdf"
    r = PdfReader(str(pdf))
    W, H, s = cover_size(pages)
    b = r.pages[0].mediabox
    errs = []
    if abs(float(b.width) / 72 - W) > 0.002 or abs(float(b.height) / 72 - H) > 0.002:
        errs.append(f"cover {float(b.width) / 72:.4f}x{float(b.height) / 72:.4f}, expected {W:.4f}x{H:.4f}")
    bad = fonts_ok(r)
    if bad:
        errs.append(f"cover fonts not embedded: {bad}")
    a = np.asarray(pdfium.PdfDocument(str(pdf))[0].render(scale=DPI / 72).to_pil().convert("RGB")).astype(int)
    # barcode zone: back cover, 2.0 x 1.2 in, 0.25 in from the trim's right and bottom edges
    x1 = round((BLEED + TRIM_W - 0.25) * DPI); x0 = x1 - round(2.0 * DPI)
    y1 = round((BLEED + TRIM_H - 0.25) * DPI); y0 = y1 - round(1.2 * DPI)
    zone = a[y0:y1, x0:x1]
    if np.abs(zone - zone.reshape(-1, 3).mean(0)).max() > 40:
        errs.append("barcode zone is not plain")
    return (W, H, s), errs


def large_print(book):
    """KDP large print = content 16 pt or larger. Checked only when listing.md says Large print: Yes."""
    if not (book / "listing.md").exists():
        return []
    t = (book / "listing.md").read_text(encoding="utf-8")
    if not re.search(r"\| Large print \| ✅ Yes", t):
        return []
    import pymupdf
    small = set()
    for i, p in enumerate(pymupdf.open(book / "interior.pdf")):
        for b in p.get_text("dict")["blocks"]:
            for ln in b.get("lines", []):
                for s in ln["spans"]:
                    if s["text"].strip() and s["size"] < 15.95:
                        small.add(i + 1)
    return [f"large print: text under 16 pt on pages {sorted(small)[:10]}"] if small else []


def listing(book):
    t = (book / "listing.md").read_text(encoding="utf-8")
    errs = []
    kws = re.findall(r"^\d\. (.+)$", t.split("### 7 Keywords")[1].split("###")[0], re.M)
    if len(kws) != 7 or any(len(k) > 50 for k in kws):
        errs.append(f"keywords: {[(k, len(k)) for k in kws]}")
    title = re.search(r"\| Book Title \| (.+?) \|", t).group(1)
    sub = re.search(r"\| Subtitle \| (.+?) \|", t).group(1)
    if len(title) + len(sub) > 200:
        errs.append(f"title+subtitle {len(title) + len(sub)} chars")
    desc = t.split("```html")[1].split("```")[0]
    if len(desc) > 4000:
        errs.append(f"description {len(desc)} chars")
    banned = re.findall(r"(?i)christmas|xmas|santa|halloween|easter|valentine|thanksgiving|church|bible|pork|bacon|beer|wine|casino", t)
    if banned:
        errs.append(f"banned words in listing: {banned}")
    return title, len(title) + len(sub), len(desc), errs


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if not args:
        sys.exit("usage: qa.py book_dir [book_dir ...]")
    books = [Path(p) for p in args]
    all_ok = True
    for b in books:
        n, e1 = interior(b)
        dims, e2 = cover(b, n) if (b / "cover.pdf").exists() else (cover_size(n), [])
        title, tl, dl, e3 = listing(b) if (b / "listing.md").exists() else ("", 0, 0, [])
        e4 = []
        if (b / "build_info.json").exists():
            info = json.loads((b / "build_info.json").read_text())
            e4 = [] if info["pages"] == n else [f"build_info pages {info['pages']} != {n}"]
        errs = e1 + e2 + e3 + e4 + large_print(b)
        all_ok &= not errs
        print(f"{'OK  ' if not errs else 'FAIL'} {b.name}: {n} pages, cover {dims[0]:.3f}x{dims[1]:.2f} spine {dims[2]:.3f}, "
              f"title+sub {tl} chars, desc {dl} chars")
        for e in errs:
            print("     -", e)
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
