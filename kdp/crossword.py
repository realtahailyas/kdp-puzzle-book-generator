"""American-style crossword engine: clue bank, symmetric block patterns, backtracking filler, checks and SVG rendering.

Rules enforced: square grid, black squares in 180-degree rotational symmetry, every white cell is part of an Across AND a
Down answer of 3+ letters, all white cells connected, every answer comes from the clue bank, no answer twice in a grid."""
import random
import re
from pathlib import Path

BANK_DIR = Path(__file__).resolve().parent / "xwbank"

# Content filter: answers that are never placed in a grid (family-friendly default; edit to taste).
BANNED = set("""
WAR ARMY ROB THIEF HAM BACON PORK PIG HOG BOAR SOW KEG PUB BEER WINE ALE RUM GIN CIGAR SMOKE BET CASINO DICE POKER
ARK HYMN PRAY PRAYER TOMB CHURCH ANGEL SAINT HEAVEN HELL DEVIL SIN BLESS FAITH SPIRIT GHOST WITCH MAGIC FAIRY WAND
KISS LOVE DATE DATES BRIDE GROOM WOO ROMANCE DANCE WALTZ BALLET DISCO PROM CAROL CHOIR OPERA ARIA ALTO
SING SANG SUNG SONG SONGS TUNE TUNES MUSIC PIANO FLUTE DRUM DRUMS HARP TUBA BAND LARK
GUN GUNS KILL DEAD DEATH BLOOD SKULL WIDOW GRAVE TOMB OLE SPY OMEN ALES PUBS SPYS PLYS ROBS MATE SEX ASS BUTT PISS CRAP SHIT DAMN DRUG DRUGS BOMB NAZI JAIL COPS EVIL CULT RAPE STAB RIOT GOD GODS LORD AMEN IDOL NUNS SIKH HOLY THEE THOU SINS VICE WINE BEER BETS POKER BINGO LOTTO JAZZ PROM DUET SOLO TUNE OPUS OBOE LUTE UKE SAX GIG JIG HYMNS
""".split())


def clean(ans):
    return re.sub(r"[^A-Z]", "", ans.upper())


def load_bank(extra_dirs=()):
    """answer -> list of clues (first one is the main clue)."""
    bank = {}
    for d in (BANK_DIR, *extra_dirs):
        for f in sorted(Path(d).glob("*.txt")):
            for line in f.read_text(encoding="utf-8").splitlines():
                if "|" not in line or line.startswith("#"):
                    continue
                ans, *clues = [x.strip() for x in line.split("|")]
                a = clean(ans)
                if len(a) < 3 or a in BANNED or not clues:
                    continue
                bank.setdefault(a, [])
                for c in clues:
                    if c and c not in bank[a]:
                        bank[a].append(c)
    return bank


# ---------------------------------------------------------------- patterns
def runs(grid):
    """All maximal white runs: (r, c, direction, length). grid[r][c] True = black."""
    n = len(grid)
    out = []
    for r in range(n):
        c = 0
        while c < n:
            if grid[r][c]:
                c += 1; continue
            s = c
            while c < n and not grid[r][c]:
                c += 1
            out.append((r, s, "A", c - s))
    for c in range(n):
        r = 0
        while r < n:
            if grid[r][c]:
                r += 1; continue
            s = r
            while r < n and not grid[r][c]:
                r += 1
            out.append((s, c, "D", r - s))
    return out


def connected(grid):
    n = len(grid)
    cells = [(r, c) for r in range(n) for c in range(n) if not grid[r][c]]
    if not cells:
        return False
    seen, st = {cells[0]}, [cells[0]]
    while st:
        r, c = st.pop()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (r + dr, c + dc)
            if 0 <= q[0] < n and 0 <= q[1] < n and not grid[q[0]][q[1]] and q not in seen:
                seen.add(q); st.append(q)
    return len(seen) == len(cells)


def pattern_ok(grid, max_len):
    n = len(grid)
    for r in range(n):
        for c in range(n):
            if grid[r][c] != grid[n - 1 - r][n - 1 - c]:
                return False
    rs = runs(grid)
    return all(3 <= L <= max_len for *_, L in rs) and connected(grid)


def make_pattern(n, rng, max_len=7, blocks=(30, 44), tries=4000):
    """Random symmetric pattern: add mirrored block pairs while every run stays >= 3, until all runs <= max_len."""
    for _ in range(tries):
        g = [[False] * n for _ in range(n)]
        nb = 0
        stuck = 0
        while stuck < 300:
            long_runs = [x for x in runs(g) if x[3] > max_len]
            if not long_runs and nb >= blocks[0]:
                break
            if long_runs and rng.random() < 0.85:
                r, c, d, L = rng.choice(long_runs)
                k = rng.randrange(3, L - 3) if L >= 7 else rng.randrange(L)
                rr, cc = (r, c + k) if d == "A" else (r + k, c)
            else:
                rr, cc = rng.randrange(n), rng.randrange(n)
            if g[rr][cc]:
                stuck += 1; continue
            g[rr][cc] = g[n - 1 - rr][n - 1 - cc] = True
            if any(L < 3 for *_, L in runs(g)) or not connected(g):
                g[rr][cc] = g[n - 1 - rr][n - 1 - cc] = False
                stuck += 1; continue
            nb += 1 if (rr, cc) == (n - 1 - rr, n - 1 - cc) else 2
            stuck = 0
            if nb > blocks[1]:
                break
        if blocks[0] <= nb <= blocks[1] and pattern_ok(g, max_len):
            return g
    raise RuntimeError("no pattern")


# ---------------------------------------------------------------- filler
def slots_of(grid):
    n = len(grid)
    out = []
    for r, c, d, L in runs(grid):
        cells = [(r, c + i) if d == "A" else (r + i, c) for i in range(L)]
        out.append({"r": r, "c": c, "d": d, "len": L, "cells": cells})
    return out


class Index:
    def __init__(self, words):
        self.by_len = {}
        self.pos = {}
        for w in words:
            self.by_len.setdefault(len(w), set()).add(w)
            for i, ch in enumerate(w):
                self.pos.setdefault((len(w), i, ch), set()).add(w)

    def match(self, pattern):
        """pattern: list of letters or None."""
        L = len(pattern)
        s = None
        for i, ch in enumerate(pattern):
            if ch is None:
                continue
            p = self.pos.get((L, i, ch), set())
            s = p if s is None else s & p
            if not s:
                return set()
        return set(self.by_len.get(L, set())) if s is None else set(s)


def fill(grid, idx, rng, weight=None, node_limit=60000, exclude=frozenset(), beam=12):
    """Fill the grid. weight(word) -> preference (lower = better). Returns (slots, {slot: word}) or None.
    Domains are kept per slot and narrowed on every placement (forward checking); slot choice = smallest domain;
    candidate order = preference, then a one-step lookahead that keeps crossing slots as open as possible."""
    import math
    slots = slots_of(grid)
    cross = {}   # slot -> list of (k, other slot, j): letter k of slot == letter j of other
    where = {}
    for i, s in enumerate(slots):
        for k, cell in enumerate(s["cells"]):
            where.setdefault(cell, []).append((i, k))
    for cell, lst in where.items():
        (a, ka), (b, kb) = lst
        cross.setdefault(a, []).append((ka, b, kb))
        cross.setdefault(b, []).append((kb, a, ka))
    dom = [set(idx.by_len.get(s["len"], ())) - set(exclude) for s in slots]
    assign = {}
    used = set()
    nodes = [0]
    wkey = weight or (lambda w: 0)

    def rec():
        nodes[0] += 1
        if nodes[0] > node_limit:
            return False
        open_ = [i for i in range(len(slots)) if i not in assign]
        if not open_:
            return True
        best = min(open_, key=lambda i: (len(dom[i] - used), -len(cross[i])))
        cand = list(dom[best] - used)
        if not cand:
            return False
        rng.shuffle(cand)
        cand.sort(key=lambda w: wkey(w) + rng.random() * 0.5)
        cand = cand[:beam * 3]
        scored = []
        for w in cand:
            sc = 0.0
            ok = True
            for k, o, j in cross[best]:
                if o in assign:
                    continue
                n = len(dom[o] & idx.pos.get((slots[o]["len"], j, w[k]), set()))
                if n == 0:
                    ok = False; break
                sc += math.log(n)
            if ok:
                scored.append((wkey(w) * 3 - sc, w))
        scored.sort()
        for _, w in scored[:beam]:
            saved = []
            ok = True
            for k, o, j in cross[best]:
                if o in assign:
                    continue
                nd = dom[o] & idx.pos.get((slots[o]["len"], j, w[k]), set())
                saved.append((o, dom[o]))
                dom[o] = nd
                if not (nd - used - {w}):
                    ok = False; break
            assign[best] = w; used.add(w)
            if ok and rec():
                return True
            del assign[best]; used.discard(w)
            for o, d in reversed(saved):
                dom[o] = d
        return False

    if rec():
        return slots, assign
    return None


# ---------------------------------------------------------------- numbering + checks
def number(grid):
    """Standard numbering. Returns (numbers dict cell->n, across list [(n, r, c, L)], down list)."""
    n = len(grid)
    nums, across, down = {}, [], []
    k = 0
    for r in range(n):
        for c in range(n):
            if grid[r][c]:
                continue
            sa = (c == 0 or grid[r][c - 1]) and c + 2 < n and not grid[r][c + 1] and not grid[r][c + 2]
            sd = (r == 0 or grid[r - 1][c]) and r + 2 < n and not grid[r + 1][c] and not grid[r + 2][c]
            if sa or sd:
                k += 1
                nums[(r, c)] = k
                if sa:
                    L = 0
                    while c + L < n and not grid[r][c + L]:
                        L += 1
                    across.append((k, r, c, L))
                if sd:
                    L = 0
                    while r + L < n and not grid[r + L][c]:
                        L += 1
                    down.append((k, r, c, L))
    return nums, across, down


def verify(grid, sol, bank):
    """sol: dict (r,c)->letter. Raises AssertionError on any problem; returns (across, down) answer lists."""
    n = len(grid)
    assert pattern_ok(grid, n), "pattern"
    for r in range(n):
        for c in range(n):
            assert (grid[r][c]) == ((r, c) not in sol), "cell/solution mismatch"
    nums, across, down = number(grid)
    A = [(k, "".join(sol[(r, c + i)] for i in range(L))) for k, r, c, L in across]
    D = [(k, "".join(sol[(r + i, c)] for i in range(L))) for k, r, c, L in down]
    words = [w for _, w in A + D]
    assert all(w in bank for w in words), [w for w in words if w not in bank]
    assert len(set(words)) == len(words), "repeat in grid"
    covered_a = {(r, c + i) for _, r, c, L in across for i in range(L)}
    covered_d = {(r + i, c) for _, r, c, L in down for i in range(L)}
    assert covered_a == covered_d == set(sol), "unchecked cell"
    return A, D


def svg(grid, sol=None, cell=36, num_font=16, letter_font=None, stroke="#111"):
    """Crossword grid as SVG. Numbers shown in puzzles; solution letters shown when sol is given."""
    n = len(grid)
    nums, _, _ = number(grid)
    W = n * cell
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-2 -2 {W + 4} {W + 4}" width="100%">']
    p.append(f'<rect x="0" y="0" width="{W}" height="{W}" fill="#fff"/>')
    for r in range(n):
        for c in range(n):
            x, y = c * cell, r * cell
            if grid[r][c]:
                p.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="#222"/>')
            else:
                p.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="none" stroke="{stroke}" stroke-width="1.4"/>')
                if sol:
                    lf = letter_font or cell * 0.62
                    p.append(f'<text x="{x + cell / 2}" y="{y + cell * 0.74}" font-family="Atkinson" font-weight="700" '
                             f'font-size="{lf}" text-anchor="middle">{sol[(r, c)]}</text>')
                elif (r, c) in nums:
                    p.append(f'<text x="{x + 2.5}" y="{y + num_font * 0.92}" font-family="Fredoka" font-weight="600" '
                             f'font-size="{num_font}">{nums[(r, c)]}</text>')
    p.append(f'<rect x="0" y="0" width="{W}" height="{W}" fill="none" stroke="{stroke}" stroke-width="3"/>')
    p.append("</svg>")
    return "".join(p)
