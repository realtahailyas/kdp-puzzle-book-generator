"""Check a PDF: page count, size, embedded fonts; optionally render pages to PNG."""
import sys
from pypdf import PdfReader

def check(path, render=(), out_prefix=None, scale=0.9):
    r = PdfReader(path)
    b = r.pages[0].mediabox
    fonts, emb = set(), set()
    for p in r.pages:
        res = p.get('/Resources') or {}
        for k, f in (res.get('/Font') or {}).items():
            f = f.get_object()
            if f.get('/Subtype') == '/Type3':
                fonts.add('Type3'); emb.add('Type3'); continue
            name = f['/BaseFont']; fonts.add(name)
            d = f.get('/FontDescriptor')
            if d is None and '/DescendantFonts' in f:
                d = f['/DescendantFonts'][0].get_object().get('/FontDescriptor')
            if d is not None:
                d = d.get_object()
                if any(x in d for x in ('/FontFile', '/FontFile2', '/FontFile3')): emb.add(name)
    print(sorted(fonts)); print(f"pages={len(r.pages)} size={float(b.width)/72:.3f}x{float(b.height)/72:.3f}in fonts={len(fonts)} not_embedded={fonts-emb}")
    if render:
        import pypdfium2 as P
        d = P.PdfDocument(path)
        for i in render:
            d[i - 1].render(scale=scale).to_pil().save(f"{out_prefix}_{i}.png")

if __name__ == "__main__":
    path, prefix = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None
    pages = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else []
    check(path, pages, prefix)
