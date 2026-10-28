"""Word search generator with uniqueness checks and SVG rendering."""
import random
import re

# forward-only directions (easy for seniors): right, down, down-right, up-right
EASY_DIRS = [(0, 1), (1, 0), (1, 1), (-1, 1)]
ALL_DIRS = EASY_DIRS + [(0, -1), (-1, 0), (-1, -1), (1, -1)]
BAD = ["FUCK", "SHIT", "CUNT", "DICK", "COCK", "PISS", "SLUT", "WHORE", "BITCH", "NIGGER", "NIGGA", "FAG",
       "RAPE", "TWAT", "PORN", "ANUS", "PENIS", "KKK", "NAZI", "SEX", "TIT", "ASS", "CUM", "JIZZ", "DAMN",
       "KILL", "DEAD"]


def clean(word):
    return re.sub(r"[^A-Z]", "", word.upper())


def _lines(grid):
    n = len(grid)
    rows = ["".join(r) for r in grid]
    cols = ["".join(grid[r][c] for r in range(n)) for c in range(n)]
    diags = []
    for d in range(-n + 1, n):
        diags.append("".join(grid[r][r - d] for r in range(n) if 0 <= r - d < n))
        diags.append("".join(grid[r][d + n - 1 - r] for r in range(n) if 0 <= d + n - 1 - r < n))
    lines = rows + cols + diags
    return lines + [l[::-1] for l in lines]


def _count(word, lines):
    return sum(len(re.findall(f"(?={word})", l)) for l in lines)


def generate(words, size=14, dirs=EASY_DIRS, seed=0, tries=400):
    rng = random.Random(seed)
    targets = [(w, clean(w)) for w in words]
    assert all(len(c) <= size for _, c in targets), [w for w, c in targets if len(c) > size]
    cl = [c for _, c in targets]
    sub = [(a, b) for a in cl for b in cl if a != b and (a in b or a[::-1] in b)]
    assert not sub, f"substring words: {sub}"
    assert len(set(cl)) == len(cl), f"duplicate words: {cl}"
    for attempt in range(tries):
        grid = [[None] * size for _ in range(size)]
        placed = []
        ok = True
        for disp, w in sorted(targets, key=lambda t: -len(t[1])):
            options = []
            for dr, dc in dirs:
                for r in range(size):
                    for c in range(size):
                        er, ec = r + dr * (len(w) - 1), c + dc * (len(w) - 1)
                        if not (0 <= er < size and 0 <= ec < size):
                            continue
                        overlap, fits = 0, True
                        for i, ch in enumerate(w):
                            g = grid[r + dr * i][c + dc * i]
                            if g is None:
                                continue
                            if g != ch:
                                fits = False
                                break
                            overlap += 1
                        if fits and overlap < len(w):
                            options.append((overlap, rng.random(), r, c, dr, dc))
            if not options:
                ok = False
                break
            # pick a direction uniformly first (balanced mix of across/down/diagonal), then a spot,
            # with a mild preference for crossing an existing word
            avail = sorted({(o[4], o[5]) for o in options})
            used = {}
            for q in placed:
                used[(q["dr"], q["dc"])] = used.get((q["dr"], q["dc"]), 0) + 1
            weights = [(1.4 if a and b else 1.0) / (1 + used.get((a, b), 0)) ** 2 for a, b in avail]
            d = rng.choices(avail, weights=weights)[0]
            options = [o for o in options if (o[4], o[5]) == d]
            options.sort(key=lambda o: (-(o[0] > 0 and rng.random() < 0.35), o[1]))
            _, _, r, c, dr, dc = options[0]
            for i, ch in enumerate(w):
                grid[r + dr * i][c + dc * i] = ch
            placed.append(dict(word=disp, clean=w, r=r, c=c, dr=dr, dc=dc))
        if not ok:
            continue
        letters = "".join(t[1] for t in targets)
        pool = letters + "ABCDEFGHIJKLMNOPRSTUVWY" * 2
        for r in range(size):
            for c in range(size):
                if grid[r][c] is None:
                    grid[r][c] = rng.choice(pool)
        lines = _lines(grid)
        if any(_count(w, lines) != (2 if w == w[::-1] else 1) for _, w in targets):
            continue
        filler_bad = [b for b in BAD if _count(b, lines) and not any(b in w or b in w[::-1] for _, w in targets)]
        if filler_bad:
            continue
        return grid, placed
    raise RuntimeError(f"could not place words: {words}")


def svg(grid, placed=None, cell=34, font=23, show=False, font_family="Atkinson", stroke="#222"):
    n = len(grid)
    W = n * cell + 16
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {W}" width="100%">',
           f'<rect x="2" y="2" width="{W-4}" height="{W-4}" rx="14" fill="#fff" stroke="{stroke}" stroke-width="2.5"/>']
    o = 8
    if show and placed:
        for p in placed:
            L = len(p["clean"]) - 1
            x1, y1 = o + p["c"] * cell + cell / 2, o + p["r"] * cell + cell / 2
            x2, y2 = x1 + p["dc"] * L * cell, y1 + p["dr"] * L * cell
            out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#bdbdbd" stroke-width="{cell*0.72}" '
                       f'stroke-linecap="round" opacity="0.75"/>')
    for r in range(n):
        for c in range(n):
            x, y = o + c * cell + cell / 2, o + r * cell + cell / 2 + font * 0.36
            out.append(f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{font_family}" font-weight="700" '
                       f'font-size="{font}">{grid[r][c]}</text>')
    out.append("</svg>")
    return "".join(out)
