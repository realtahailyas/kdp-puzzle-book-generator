"""Sudoku, cryptogram, word scramble and missing-vowel generators."""
import random
import re
import string

# ---------------- Sudoku ----------------

def _candidates(g, i):
    r, c = divmod(i, 9)
    used = set(g[r * 9:(r + 1) * 9]) | {g[k * 9 + c] for k in range(9)}
    br, bc = 3 * (r // 3), 3 * (c // 3)
    used |= {g[(br + a) * 9 + bc + b] for a in range(3) for b in range(3)}
    return [d for d in range(1, 10) if d not in used]


def _solve(g, rng=None, limit=2):
    """Count solutions up to `limit` (fills g with the first one found when rng is given)."""
    count = 0
    best, bi = None, -1
    for i in range(81):
        if g[i] == 0:
            cand = _candidates(g, i)
            if not cand:
                return 0
            if best is None or len(cand) < len(best):
                best, bi = cand, i
                if len(cand) == 1:
                    break
    if best is None:
        return 1
    if rng:
        rng.shuffle(best)
    for d in best:
        g[bi] = d
        n = _solve(g, rng, limit)
        if n and rng:
            return n
        count += n
        if count >= limit:
            g[bi] = 0
            return count
    g[bi] = 0
    return count


def sudoku(seed, givens=38):
    rng = random.Random(seed)
    sol = [0] * 81
    _solve(sol, rng, 1)
    puzzle = sol[:]
    cells = list(range(81))
    rng.shuffle(cells)
    for i in cells:
        if sum(1 for v in puzzle if v) <= givens:
            break
        j = 80 - i  # symmetric removal looks nicer
        keep = puzzle[i], puzzle[j]
        puzzle[i] = puzzle[j] = 0
        if _solve(puzzle[:], None, 2) != 1:
            puzzle[i], puzzle[j] = keep
    assert _solve(puzzle[:], None, 2) == 1
    return puzzle, sol


def sudoku_svg(puzzle, sol=None, cell=40, font=26):
    W = 9 * cell + 8
    o = 4
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {W}" width="100%">']
    for k in range(10):
        sw = 4 if k % 3 == 0 else 1.4
        p = o + k * cell
        out.append(f'<line x1="{o}" y1="{p}" x2="{o + 9 * cell}" y2="{p}" stroke="#111" stroke-width="{sw}" stroke-linecap="square"/>')
        out.append(f'<line x1="{p}" y1="{o}" x2="{p}" y2="{o + 9 * cell}" stroke="#111" stroke-width="{sw}" stroke-linecap="square"/>')
    for i in range(81):
        r, c = divmod(i, 9)
        x, y = o + c * cell + cell / 2, o + r * cell + cell / 2 + font * 0.36
        if puzzle[i]:
            out.append(f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Atkinson" font-weight="700" font-size="{font}">{puzzle[i]}</text>')
        elif sol:
            out.append(f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Lora" font-style="italic" font-size="{font * 0.9}" fill="#666">{sol[i]}</text>')
    out.append("</svg>")
    return "".join(out)

# ---------------- Cryptogram ----------------

def cipher(seed):
    rng = random.Random(seed)
    letters = list(string.ascii_uppercase)
    while True:
        shuffled = letters[:]
        rng.shuffle(shuffled)
        if all(a != b for a, b in zip(letters, shuffled)):
            return dict(zip(letters, shuffled))


def cryptogram(text, seed, hints=2):
    key = cipher(seed)
    enc = "".join(key.get(ch, ch) for ch in text.upper())
    rng = random.Random(seed + 1)
    present = sorted({ch for ch in text.upper() if ch.isalpha()})
    hint_letters = rng.sample(present, min(hints, len(present)))
    return enc, {key[h]: h for h in hint_letters}

# ---------------- Word scramble ----------------

def scramble(word, seed):
    rng = random.Random(seed)
    w = word.upper()
    letters = [c for c in w if c.isalpha()]
    best = None
    for _ in range(200):
        rng.shuffle(letters)
        cand = "".join(letters)
        same = sum(a == b for a, b in zip(cand, re.sub(r"[^A-Z]", "", w)))
        if cand != re.sub(r"[^A-Z]", "", w) and (best is None or same < best[0]):
            best = (same, cand)
            if same == 0:
                break
    return best[1]

# ---------------- Missing vowels ----------------

def no_vowels(phrase):
    return re.sub(r"[AEIOU]", "_", phrase.upper())
