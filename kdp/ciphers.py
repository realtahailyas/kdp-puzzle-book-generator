"""Kid-friendly ciphers: encoders, key charts (SVG/HTML) and write-in layouts."""
import string

A = string.ascii_uppercase


def words(msg):
    return [w for w in msg.upper().split() if w]


def a1z26(msg):
    return "  /  ".join("-".join(str(A.index(ch) + 1) for ch in w if ch in A) for w in words(msg))


def shift(msg, k):
    return " ".join("".join(A[(A.index(ch) + k) % 26] if ch in A else ch for ch in w) for w in words(msg))


def backwards(msg):
    return " ".join(w[::-1] for w in words(msg))


POLY = [r for r in "ABCDEFGHIKLMNOPQRSTUVWXYZ"]  # I and J share a square


def polybius(msg):
    out = []
    for w in words(msg):
        out.append(" ".join(f"{POLY.index('I' if ch == 'J' else ch) // 5 + 1}{POLY.index('I' if ch == 'J' else ch) % 5 + 1}"
                            for ch in w if ch in A))
    return "  /  ".join(out)


MORSE = {"A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.", "G": "--.", "H": "....", "I": "..", "J": ".---",
         "K": "-.-", "L": ".-..", "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.", "S": "...", "T": "-",
         "U": "..-", "V": "...-", "W": ".--", "X": "-..-", "Y": "-.--", "Z": "--.."}


def morse(msg):
    return "  /  ".join(" ".join(MORSE[ch] for ch in w if ch in A) for w in words(msg))


def no_vowels(msg):
    return " ".join("".join("_" if ch in "AEIOU" else ch for ch in w) for w in words(msg))


def zigzag(msg):
    """2-rail fence on the letters only -> (top row, bottom row)"""
    s = "".join(ch for ch in msg.upper() if ch in A)
    return s[0::2], s[1::2]


def decode(kind, text):
    """Inverse of the text codes (used to double-check every printed coded message)."""
    if kind == "a1z26":
        return " ".join("".join(A[int(n) - 1] for n in w.strip().split("-")) for w in text.split("/"))
    if kind in ("shift1", "shift3"):
        return shift(text, -int(kind[-1]))
    if kind == "backwards":
        return backwards(text)
    if kind == "polybius":
        return " ".join("".join(POLY[(int(p[0]) - 1) * 5 + int(p[1]) - 1] for p in w.split()) for w in text.split("/"))
    if kind == "morse":
        inv = {v: k for k, v in MORSE.items()}
        return " ".join("".join(inv[c] for c in w.split()) for w in text.split("/"))
    raise ValueError(kind)


# ---------------- pigpen ----------------
PIG = {}
for k, ch in enumerate("ABCDEFGHI"):
    PIG[ch] = ("grid", divmod(k, 3), False)
for k, ch in enumerate("JKLMNOPQR"):
    PIG[ch] = ("grid", divmod(k, 3), True)
for k, ch in enumerate("STUV"):
    PIG[ch] = ("x", k, False)
for k, ch in enumerate("WXYZ"):
    PIG[ch] = ("x", k, True)


def pig_glyph(ch, size=0.42, stroke=5):
    kind, pos, dot = PIG[ch]
    o = [f'<svg viewBox="0 0 50 50" style="width:{size}in;height:{size}in;display:block">']
    st = f'stroke="#111" stroke-width="{stroke}" fill="none" stroke-linecap="round" stroke-linejoin="round"'
    if kind == "grid":
        r, c = pos
        d = []
        if c > 0: d.append("M8 8V42")
        if c < 2: d.append("M42 8V42")
        if r > 0: d.append("M8 8H42")
        if r < 2: d.append("M8 42H42")
        o.append(f'<path d="{"".join(d)}" {st}/>')
    else:
        d = {0: "M8 10L25 40L42 10", 1: "M10 8L40 25L10 42", 2: "M40 8L10 25L40 42", 3: "M8 40L25 10L42 40"}[pos]
        o.append(f'<path d="{d}" {st}/>')
    if dot:
        cx, cy = 25, 25
        if kind == "x":
            cx, cy = {0: (25, 18), 1: (21, 25), 2: (29, 25), 3: (25, 32)}[pos]
        o.append(f'<circle cx="{cx}" cy="{cy}" r="4.5" fill="#111"/>')
    o.append("</svg>")
    return "".join(o)


def pig_key(size_in=6.4):
    """The four pigpen diagrams with letters."""
    W, H = 1000, 270
    o = [f'<svg viewBox="0 0 {W} {H}" style="width:{size_in}in;display:block">']
    st = 'stroke="#111" stroke-width="7" fill="none" stroke-linecap="round"'
    fnt = 'font-family="Fredoka" font-weight="600" font-size="34" text-anchor="middle"'
    for b, letters, dot in ((0, "ABCDEFGHI", False), (1, "JKLMNOPQR", True)):
        x0, y0, cw = 10 + b * 235, 20, 70
        o.append(f'<path d="M{x0 + cw} {y0}V{y0 + 3 * cw}M{x0 + 2 * cw} {y0}V{y0 + 3 * cw}M{x0} {y0 + cw}H{x0 + 3 * cw}'
                 f'M{x0} {y0 + 2 * cw}H{x0 + 3 * cw}" {st}/>')
        for k, ch in enumerate(letters):
            r, c = divmod(k, 3)
            cx, cy = x0 + c * cw + cw / 2, y0 + r * cw + cw / 2
            o.append(f'<text x="{cx - (10 if dot else 0)}" y="{cy + 12}" {fnt}>{ch}</text>')
            if dot:
                o.append(f'<circle cx="{cx + 16}" cy="{cy}" r="7" fill="#111"/>')
    for b, letters, dot in ((0, "STUV", False), (1, "WXYZ", True)):
        cx, cy, R = 585 + b * 265, 125, 100
        o.append(f'<path d="M{cx - R} {cy - R}L{cx + R} {cy + R}M{cx + R} {cy - R}L{cx - R} {cy + R}" {st}/>')
        for k, ch in enumerate(letters):
            dx, dy = {0: (0, -60), 1: (-60, 0), 2: (60, 0), 3: (0, 60)}[k]
            o.append(f'<text x="{cx + dx - (12 if dot and k in (0, 3) else 0)}" y="{cy + dy + 12}" {fnt}>{ch}</text>')
            if dot:
                ddx, ddy = {0: (14, -2), 1: (0, 26), 2: (0, 26), 3: (14, -2)}[k]
                o.append(f'<circle cx="{cx + dx + ddx}" cy="{cy + dy + ddy}" r="7" fill="#111"/>')
    o.append("</svg>")
    return "".join(o)


# ---------------- shape code ----------------
# Shapes only: nothing that looks like a letter (no X, no F, no V-shapes)
SHAPE_D = [
    '<circle cx="25" cy="25" r="16" {s}/>',
    '<rect x="10" y="10" width="30" height="30" {s}/>',
    '<path d="M25 8L42 40H8Z" {s}/>',
    '<path d="M25 6L44 25L25 44L6 25Z" {s}/>',
    '<path d="M25 6L30 19L44 20L33 29L37 43L25 35L13 43L17 29L6 20L20 19Z" {s}/>',
    '<path d="M25 42C10 32 6 24 6 17C6 11 11 7 16 7C20 7 23 9 25 13C27 9 30 7 34 7C39 7 44 11 44 17C44 24 40 32 25 42Z" {s}/>',
    '<path d="M25 8V42M8 25H42" {s}/>',
    '<circle cx="25" cy="25" r="13" fill="#111"/>',
    '<path d="M6 25Q15 10 25 25T44 25" {s}/>',
    '<path d="M16 9H34L43 25L34 41H16L7 25Z" {s}/>',
    '<circle cx="25" cy="25" r="16" {s}/><circle cx="25" cy="25" r="5" fill="#111"/>',
    '<rect x="10" y="10" width="30" height="30" {s}/><path d="M10 10L40 40" {s}/>',
    '<path d="M25 8L42 40H8Z" {s}/><circle cx="25" cy="30" r="4" fill="#111"/>',
    '<path d="M25 6C25 6 40 24 40 32C40 40 33 45 25 45C17 45 10 40 10 32C10 24 25 6 25 6Z" {s}/>',
    '<path d="M14 38C6 38 6 26 14 26C14 16 28 14 31 22C38 18 46 26 40 32C44 38 38 40 36 38Z" {s}/>',
    '<rect x="9" y="17" width="32" height="16" rx="8" {s}/>',
]


def shape_glyph(idx, size=0.42):
    s = 'stroke="#111" stroke-width="4.5" fill="none" stroke-linejoin="round" stroke-linecap="round"'
    return f'<svg viewBox="0 0 50 50" style="width:{size}in;height:{size}in;display:block">{SHAPE_D[idx].format(s=s)}</svg>'


def shape_map(msg):
    letters = []
    for ch in msg.upper():
        if ch in A and ch not in letters:
            letters.append(ch)
    assert len(letters) <= len(SHAPE_D), letters
    return {ch: k for k, ch in enumerate(sorted(letters))}


def write_in(msg, glyph, size=0.42, box=True):
    """Each letter as a glyph with an empty box underneath for the answer."""
    out = ['<div style="display:flex;flex-wrap:wrap;gap:6pt 22pt;justify-content:center">']
    for w in words(msg):
        out.append('<div style="display:flex;gap:4pt">')
        for ch in w:
            if ch not in A:
                continue
            out.append(f'<div style="display:flex;flex-direction:column;align-items:center;gap:3pt">{glyph(ch)}'
                       + (f'<div style="width:{size}in;height:{size * 1.05}in;border:2pt solid #111;border-radius:4pt"></div>' if box else "")
                       + '</div>')
        out.append("</div>")
    out.append("</div>")
    return "".join(out)


def boxes(msg, size=0.38):
    """Empty answer boxes shaped like the message."""
    out = ['<div style="display:flex;flex-wrap:wrap;gap:8pt 20pt;justify-content:center">']
    for w in words(msg):
        out.append('<div style="display:flex;gap:3pt">' + "".join(
            f'<div style="width:{size}in;height:{size * 1.1}in;border:2pt solid #111;border-radius:4pt"></div>' for ch in w if ch in A) + "</div>")
    out.append("</div>")
    return "".join(out)
