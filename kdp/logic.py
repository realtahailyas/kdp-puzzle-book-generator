"""Murdle-style 3-category logic grid mysteries (suspects x places x items).
Every puzzle is checked two ways: brute force (exactly one solution) and a simple human-style propagation
solver (grid elimination + transitivity), so it can be solved by pure logic without guessing."""
import itertools
import random

TRAITS = {  # key: (true phrase, false phrase)
    "glasses": ("wears glasses", "does not wear glasses"),
    "hat": ("wears a hat", "does not wear a hat"),
    "tall": ("is tall", "is short"),
    "left": ("is left-handed", "is right-handed"),
}


class Grid:
    """Truth state of the three sub-grids. None = unknown."""

    def __init__(self, n):
        self.n = n
        self.sp = [[None] * n for _ in range(n)]
        self.si = [[None] * n for _ in range(n)]
        self.pi = [[None] * n for _ in range(n)]

    def get(self, g, a, b):
        return getattr(self, g)[a][b]

    def set(self, g, a, b, v):
        cur = getattr(self, g)[a][b]
        if cur is None:
            getattr(self, g)[a][b] = v
            return True
        if cur != v:
            raise ValueError("contradiction")
        return False

    def known(self):
        return sum(v is not None for g in (self.sp, self.si, self.pi) for row in g for v in row)

    def solved(self):
        return self.known() == 3 * self.n * self.n


def holds(clue, P, I, traits):
    """Is clue true for assignment P[s] = place, I[s] = item?"""
    t = clue[0]
    if t == "SP":
        return (P[clue[1]] == clue[2]) == clue[3]
    if t == "SI":
        return (I[clue[1]] == clue[2]) == clue[3]
    if t == "PI":
        s = P.index(clue[1])
        return (I[s] == clue[2]) == clue[3]
    if t == "TP":
        s = P.index(clue[2])
        return traits[s][clue[1]] == clue[3]
    if t == "TI":
        s = I.index(clue[2])
        return traits[s][clue[1]] == clue[3]
    if t == "OR":
        return holds(clue[1], P, I, traits) or holds(clue[2], P, I, traits)
    raise ValueError(t)


def count_solutions(n, clues, traits, limit=2):
    found = 0
    for P in itertools.permutations(range(n)):
        for I in itertools.permutations(range(n)):
            if all(holds(c, P, I, traits) for c in clues):
                found += 1
                if found >= limit:
                    return found
    return found


def _atom(c):
    """positive SP/SI/PI clue -> (grid, a, b)"""
    return {"SP": "sp", "SI": "si", "PI": "pi"}[c[0]], c[1], c[2]


def propagate(n, clues, traits):
    g = Grid(n)
    for c in clues:
        t = c[0]
        if t in ("SP", "SI", "PI"):
            g.set({"SP": "sp", "SI": "si", "PI": "pi"}[t], c[1], c[2], c[3])
    changed = True
    while changed:
        changed = False
        # trait clues
        for c in clues:
            if c[0] in ("TP", "TI"):
                grid = "sp" if c[0] == "TP" else "si"
                for s in range(n):
                    if traits[s][c[1]] != c[3]:
                        changed |= g.set(grid, s, c[2], False)
        # either/or clues
        for c in clues:
            if c[0] == "OR":
                a, b = _atom(c[1]), _atom(c[2])
                if g.get(*a) is False:
                    changed |= g.set(*b, True)
                if g.get(*b) is False:
                    changed |= g.set(*a, True)
        # one yes per row/column in each sub-grid
        for name in ("sp", "si", "pi"):
            M = getattr(g, name)
            for a in range(n):
                for b in range(n):
                    if M[a][b] is True:
                        for k in range(n):
                            if k != b:
                                changed |= g.set(name, a, k, False)
                            if k != a:
                                changed |= g.set(name, k, b, False)
                row = [M[a][k] for k in range(n)]
                if row.count(False) == n - 1 and None in row:
                    changed |= g.set(name, a, row.index(None), True)
                col = [M[k][a] for k in range(n)]
                if col.count(False) == n - 1 and None in col:
                    changed |= g.set(name, col.index(None), a, True)
        # transitivity across the three grids
        for s in range(n):
            for p in range(n):
                for i in range(n):
                    SP, SI, PI = g.sp[s][p], g.si[s][i], g.pi[p][i]
                    if SP and PI:
                        changed |= g.set("si", s, i, True)
                    if SP and SI:
                        changed |= g.set("pi", p, i, True)
                    if SI and PI:
                        changed |= g.set("sp", s, p, True)
                    if SP and PI is False:
                        changed |= g.set("si", s, i, False)
                    if SP and SI is False:
                        changed |= g.set("pi", p, i, False)
                    if SI and PI is False:
                        changed |= g.set("sp", s, p, False)
                    if SI and SP is False:
                        changed |= g.set("pi", p, i, False)
                    if PI and SP is False:
                        changed |= g.set("si", s, i, False)
                    if PI and SI is False:
                        changed |= g.set("sp", s, p, False)
    return g


def clue_pool(n, P, I, traits, kinds, rng):
    pool = []
    for s in range(n):
        for k in range(n):
            if "SP+" in kinds and P[s] == k:
                pool.append(("SP", s, k, True))
            if "SP-" in kinds and P[s] != k:
                pool.append(("SP", s, k, False))
            if "SI+" in kinds and I[s] == k:
                pool.append(("SI", s, k, True))
            if "SI-" in kinds and I[s] != k:
                pool.append(("SI", s, k, False))
    for p in range(n):
        s = P.index(p)
        for i in range(n):
            if "PI+" in kinds and I[s] == i:
                pool.append(("PI", p, i, True))
            if "PI-" in kinds and I[s] != i:
                pool.append(("PI", p, i, False))
    if "T" in kinds:
        for tr in TRAITS:
            vals = [traits[s][tr] for s in range(n)]
            if all(vals) or not any(vals):
                continue  # trait gives no information here
            for p in range(n):
                pool.append(("TP", tr, p, traits[P.index(p)][tr]))
            for i in range(n):
                pool.append(("TI", tr, i, traits[I.index(i)][tr]))
    if "OR" in kinds:
        # one true atom + one false atom, both positive statements
        atoms_true = [("SP", s, P[s], True) for s in range(n)] + [("SI", s, I[s], True) for s in range(n)]
        atoms_false = [("SP", s, k, True) for s in range(n) for k in range(n) if P[s] != k] + \
                      [("PI", p, i, True) for p in range(n) for i in range(n) if I[P.index(p)] != i]
        for _ in range(12):
            a, b = rng.choice(atoms_true), rng.choice(atoms_false)
            pool.append(("OR",) + ((a, b) if rng.random() < 0.5 else (b, a)))
    rng.shuffle(pool)
    return pool


LEVELS = {
    1: dict(kinds={"SP-", "SI-", "PI+", "PI-", "SP+"}, max_pos=1, clues=(3, 5)),
    2: dict(kinds={"SP-", "SI-", "PI+", "PI-", "T", "SP+"}, max_pos=1, clues=(4, 7), need={"T"}),
    3: dict(kinds={"SP-", "SI-", "PI-", "PI+", "T", "OR"}, max_pos=0, clues=(5, 8), need={"T", "OR"}),
}


def _kind(c):
    if c[0] in ("TP", "TI"):
        return "T"
    if c[0] == "OR":
        return "OR"
    return c[0]


def make(n, traits, level, key, rng, tries=400):
    """key: ('place', p) -> culprit is whoever is in place p; ('item', i) -> whoever has item i.
    culprit: suspect index that must satisfy the key. Returns (P, I, clues)."""
    cfg = LEVELS[level]
    kind, val, culprit = key
    for _ in range(tries):
        P = list(range(n)); rng.shuffle(P)
        I = list(range(n)); rng.shuffle(I)
        if kind == "place":
            j = P.index(val); P[j], P[culprit] = P[culprit], P[j]
        else:
            j = I.index(val); I[j], I[culprit] = I[culprit], I[j]
        pool = clue_pool(n, P, I, traits, cfg["kinds"], rng)
        chosen, known = [], 0
        for c in pool:
            if c[0] in ("SP", "SI") and c[3] and sum(1 for x in chosen if x[0] in ("SP", "SI") and x[3]) >= cfg["max_pos"]:
                continue
            try:
                k = propagate(n, chosen + [c], traits).known()
            except ValueError:
                continue
            if k > known:
                chosen.append(c); known = k
                if known == 3 * n * n:
                    break
        if known < 3 * n * n:
            continue
        # drop clues that are not needed
        for c in list(chosen):
            rest = [x for x in chosen if x is not c]
            if propagate(n, rest, traits).solved():
                chosen = rest
        kinds = {_kind(c) for c in chosen}
        lo, hi = cfg["clues"]
        if not (lo <= len(chosen) <= hi) or not cfg.get("need", set()) <= kinds:
            continue
        # the culprit's own direct placement must not be given away by a single clue
        if any(c[0] == "SP" and c[3] and c[1] == culprit for c in chosen):
            continue
        assert count_solutions(n, chosen, traits) == 1
        rng.shuffle(chosen)
        return P, I, chosen
    raise RuntimeError("could not build puzzle")


def text(c, S, Pl, It, pre=None):
    """Clue -> English. S/Pl/It: display names; pre: place -> preposition (default 'in')."""
    pre = pre or {}
    at = lambda k: f"{pre.get(Pl[k], 'in')} the {Pl[k]}"
    t = c[0]
    if t == "SP":
        out = f"{S[c[1]]} was {'' if c[3] else 'not '}{at(c[2])}."
    elif t == "SI":
        out = f"{S[c[1]]} {'had' if c[3] else 'did not have'} the {It[c[2]]}."
    elif t == "PI":
        out = (f"The person {at(c[1])} had the {It[c[2]]}." if c[3]
               else f"Whoever was {at(c[1])} did not have the {It[c[2]]}.")
    elif t == "TP":
        out = f"The person {at(c[2])} {TRAITS[c[1]][0 if c[3] else 1]}."
    elif t == "TI":
        out = f"The person who had the {It[c[2]]} {TRAITS[c[1]][0 if c[3] else 1]}."
    elif t == "OR":
        a = text(c[1], S, Pl, It, pre).rstrip(".")
        b = text(c[2], S, Pl, It, pre).rstrip(".")
        b = b[0].lower() + b[1:] if b.startswith(("The ", "Whoever")) else b
        out = f"At least one of these is true: {a}, OR {b}."
    return out


def grid_svg(S, Pl, It, width_in=5.6, solution=None):
    """Classic staircase logic grid. solution=(P, I) draws ticks in the answer cells."""
    n = len(S)
    cell, lab_w, lab_h = 46, 150, 150
    W = lab_w + 2 * n * cell
    H = lab_h + 2 * n * cell
    o = [f'<svg viewBox="-4 -4 {W + 8} {H + 8}" style="width:{width_in}in;display:block">']
    font = 'font-family="Atkinson" font-weight="700"'
    # column headers (rotated)
    for k, name in enumerate(list(Pl) + list(It)):
        x = lab_w + k * cell + cell / 2 + 6
        o.append(f'<text transform="translate({x},{lab_h - 8}) rotate(-90)" font-size="17" {font}>{name}</text>')
    # group bands
    o.append(f'<text x="{lab_w + n * cell / 2}" y="16" text-anchor="middle" font-size="15" font-family="Oswald" '
             f'letter-spacing="2">PLACES</text>')
    o.append(f'<text x="{lab_w + n * cell * 1.5}" y="16" text-anchor="middle" font-size="15" font-family="Oswald" '
             f'letter-spacing="2">ITEMS</text>')
    rows = list(S) + list(It)
    for r, name in enumerate(rows):
        y = lab_h + r * cell + cell / 2 + 6
        o.append(f'<text x="{lab_w - 8}" y="{y}" text-anchor="end" font-size="17" {font}>{name}</text>')
    o.append(f'<text transform="translate(14,{lab_h + n * cell / 2}) rotate(-90)" text-anchor="middle" font-size="15" '
             f'font-family="Oswald" letter-spacing="2">SUSPECTS</text>')
    o.append(f'<text transform="translate(14,{lab_h + n * cell * 1.5}) rotate(-90)" text-anchor="middle" font-size="15" '
             f'font-family="Oswald" letter-spacing="2">ITEMS</text>')
    blocks = [(0, 0), (1, 0), (0, 1)]  # (col block, row block): S x P, S x I, I x P
    for cb, rb in blocks:
        x0, y0 = lab_w + cb * n * cell, lab_h + rb * n * cell
        for k in range(n + 1):
            w = 3.2 if k in (0, n) else 1.4
            o.append(f'<path d="M{x0} {y0 + k * cell}H{x0 + n * cell}M{x0 + k * cell} {y0}V{y0 + n * cell}" stroke="#111" stroke-width="{w}"/>')
    if solution:
        P, I = solution
        marks = []
        for s in range(n):
            marks.append((P[s], s))            # S x P
            marks.append((n + I[s], s))        # S x I
            marks.append((P[s], n + I[s]))     # I x P
        for c, r in marks:
            cx, cy = lab_w + c * cell + cell / 2, lab_h + r * cell + cell / 2
            o.append(f'<circle cx="{cx}" cy="{cy}" r="{cell * 0.3}" fill="#111"/>')
    o.append("</svg>")
    return "".join(o)


if __name__ == "__main__":
    rng = random.Random(1)
    tr = [dict(glasses=g, hat=h, tall=t, left=l) for g, h, t, l in
          [(1, 0, 1, 0), (0, 1, 0, 1), (1, 1, 0, 0), (0, 0, 1, 1)]]
    for lvl, n in ((1, 3), (2, 4), (3, 4)):
        P, I, cl = make(n, tr[:n], lvl, ("place", 0, 1), rng)
        S = ["Ann", "Ben", "Cal", "Dee"][:n]; Pl = ["Gym", "Library", "Kitchen", "Garden"][:n]; It = ["Map", "Key", "Book", "Kite"][:n]
        print(lvl, P, I)
        for c in cl:
            print("  ", text(c, S, Pl, It))
