"""Shape-masked perfect mazes (DFS backtracker) with SVG rendering and solution paths."""
import math
import random
from collections import deque

# ---------- shapes: functions of (u, v) in [0,1]^2 (v grows downward) -> bool ----------

def _poly(pts):
    def inside(u, v):
        c, n = False, len(pts)
        for i in range(n):
            x1, y1 = pts[i]; x2, y2 = pts[(i + 1) % n]
            if (y1 > v) != (y2 > v) and u < (x2 - x1) * (v - y1) / (y2 - y1) + x1:
                c = not c
        return c
    return inside


def _circle(cx, cy, r):
    return lambda u, v: (u - cx) ** 2 + (v - cy) ** 2 <= r * r


def _rect(x0, y0, x1, y1):
    return lambda u, v: x0 <= u <= x1 and y0 <= v <= y1


def _union(*fs):
    return lambda u, v: any(f(u, v) for f in fs)


def _star(points=5, ro=0.5, ri=0.22, cx=0.5, cy=0.53):
    pts = []
    for k in range(points * 2):
        r = ro if k % 2 == 0 else ri
        a = -math.pi / 2 + k * math.pi / points
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return _poly(pts)


def _ell(cx, cy, rx, ry):
    return lambda u, v: ((u - cx) / rx) ** 2 + ((v - cy) / ry) ** 2 <= 1


def _petals(n=5, cx=0.5, cy=0.5, rr=0.3, r=0.2):
    return _union(*[_circle(cx + rr * math.cos(-math.pi / 2 + k * 2 * math.pi / n),
                            cy + rr * math.sin(-math.pi / 2 + k * 2 * math.pi / n), r) for k in range(n)], _circle(cx, cy, rr))


# No religious or holiday shapes (owner's rule): animals, nature and simple objects only.
SHAPES = {
    "square": _rect(0, 0, 1, 1),
    "circle": _circle(0.5, 0.5, 0.5),
    "star": _star(),
    "heart": lambda u, v: ((2 * u - 1) ** 2 + (1.25 * (0.62 - v) * 2 - math.sqrt(abs(2 * u - 1))) ** 2) <= 1.0,
    "house": _poly([(0.5, 0.0), (1.0, 0.42), (0.88, 0.42), (0.88, 1.0), (0.12, 1.0), (0.12, 0.42), (0.0, 0.42)]),
    "mug": _union(_rect(0.06, 0.12, 0.72, 0.95),
                  lambda u, v: 0.1 ** 2 <= (u - 0.74) ** 2 + (v - 0.5) ** 2 <= 0.25 ** 2 and u >= 0.7),
    "apple": _union(_circle(0.33, 0.58, 0.32), _circle(0.67, 0.58, 0.32), _ell(0.5, 0.72, 0.36, 0.27),
                    _rect(0.47, 0.1, 0.53, 0.3), _ell(0.64, 0.14, 0.12, 0.06)),
    "fish": _union(_ell(0.42, 0.5, 0.41, 0.33), _poly([(0.7, 0.5), (1.0, 0.18), (1.0, 0.82)])),
    "cat": _union(_circle(0.5, 0.6, 0.4), _poly([(0.1, 0.48), (0.12, 0.0), (0.46, 0.24)]),
                  _poly([(0.9, 0.48), (0.88, 0.0), (0.54, 0.24)])),
    "bear": _union(_circle(0.5, 0.6, 0.4), _circle(0.17, 0.2, 0.16), _circle(0.83, 0.2, 0.16)),
    "rabbit": _union(_circle(0.5, 0.7, 0.3), _ell(0.35, 0.25, 0.11, 0.25), _ell(0.65, 0.25, 0.11, 0.25)),
    "owl": _union(_ell(0.5, 0.56, 0.4, 0.44), _poly([(0.12, 0.42), (0.14, 0.0), (0.42, 0.2)]),
                  _poly([(0.88, 0.42), (0.86, 0.0), (0.58, 0.2)])),
    "cloud": _union(_circle(0.28, 0.6, 0.24), _circle(0.55, 0.42, 0.32), _circle(0.8, 0.62, 0.2),
                    _rect(0.2, 0.6, 0.85, 0.84), _circle(0.2, 0.7, 0.14)),
    "mushroom": _union(lambda u, v: v <= 0.55 and ((u - 0.5) / 0.5) ** 2 + ((v - 0.55) / 0.55) ** 2 <= 1,
                       _rect(0.32, 0.5, 0.68, 1.0)),
    "turtle": _union(lambda u, v: v <= 0.66 and ((u - 0.44) / 0.4) ** 2 + ((v - 0.66) / 0.5) ** 2 <= 1,
                     _rect(0.02, 0.6, 0.86, 0.76), _circle(0.9, 0.56, 0.1), _rect(0.14, 0.7, 0.28, 0.96),
                     _rect(0.58, 0.7, 0.72, 0.96)),
    "butterfly": _union(_ell(0.25, 0.28, 0.23, 0.22), _ell(0.75, 0.28, 0.23, 0.22), _ell(0.3, 0.79, 0.17, 0.18),
                        _ell(0.7, 0.79, 0.17, 0.18), _rect(0.45, 0.12, 0.55, 0.96)),
    "flower": _union(*[_circle(0.5 + 0.3 * math.cos(-math.pi / 2 + k * 2 * math.pi / 5),
                               0.5 + 0.3 * math.sin(-math.pi / 2 + k * 2 * math.pi / 5), 0.2) for k in range(5)],
                     _circle(0.5, 0.5, 0.2)),
    "rocket": _union(_poly([(0.5, 0.0), (0.7, 0.25), (0.7, 0.78), (0.3, 0.78), (0.3, 0.25)]),
                     _poly([(0.3, 0.5), (0.06, 0.9), (0.3, 0.84)]), _poly([(0.7, 0.5), (0.94, 0.9), (0.7, 0.84)]),
                     _rect(0.38, 0.76, 0.62, 1.0)),
    "egg": lambda u, v: ((u - 0.5) / (0.36 - 0.16 * (0.52 - v))) ** 2 + ((v - 0.52) / 0.48) ** 2 <= 1,
    "leaf": lambda u, v: abs(u - v) <= 0.62 * math.sin(math.pi * min(max((u + v) / 2, 0), 1)) * 0.75 and 0.02 <= (u + v) / 2 <= 0.98,
    "sun": _union(_circle(0.5, 0.5, 0.3), *[_poly([(0.5 + 0.26 * math.cos(a - 0.3), 0.5 + 0.26 * math.sin(a - 0.3)),
                                                   (0.5 + 0.5 * math.cos(a), 0.5 + 0.5 * math.sin(a)),
                                                   (0.5 + 0.26 * math.cos(a + 0.3), 0.5 + 0.26 * math.sin(a + 0.3))])
                                            for a in [k * math.pi / 4 for k in range(8)]]),
    "hexagon": _poly([(0.5 + 0.5 * math.cos(math.pi / 6 + k * math.pi / 3), 0.5 + 0.5 * math.sin(math.pi / 6 + k * math.pi / 3))
                      for k in range(6)]),
    "diamond": _poly([(0.5, 0.0), (1.0, 0.5), (0.5, 1.0), (0.0, 0.5)]),
}


def make_mask(shape, rows, cols):
    f = SHAPES[shape]
    m = [[f((c + 0.5) / cols, (r + 0.5) / rows) for c in range(cols)] for r in range(rows)]
    # keep the largest 4-connected component
    seen, best = set(), []
    for r in range(rows):
        for c in range(cols):
            if m[r][c] and (r, c) not in seen:
                comp, q = [], deque([(r, c)])
                seen.add((r, c))
                while q:
                    a, b = q.popleft(); comp.append((a, b))
                    for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        na, nb = a + da, b + db
                        if 0 <= na < rows and 0 <= nb < cols and m[na][nb] and (na, nb) not in seen:
                            seen.add((na, nb)); q.append((na, nb))
                if len(comp) > len(best):
                    best = comp
    keep = set(best)
    return [[(r, c) in keep for c in range(cols)] for r in range(rows)]


DIRS = {(-1, 0): "N", (1, 0): "S", (0, -1): "W", (0, 1): "E"}


class Maze:
    def __init__(self, shape="square", rows=10, cols=10, seed=0, straightness=0.0):
        m = make_mask(shape, rows, cols)
        rs = [r for r in range(rows) if any(m[r])]
        cs = [c for c in range(cols) if any(m[r][c] for r in range(rows))]
        self.mask = [row[cs[0]:cs[-1] + 1] for row in m[rs[0]:rs[-1] + 1]]  # crop empty margins
        self.rows, self.cols = len(self.mask), len(self.mask[0])
        self.cells = [(r, c) for r in range(self.rows) for c in range(self.cols) if self.mask[r][c]]
        rng = random.Random(seed)
        self.open = {cell: set() for cell in self.cells}
        self.icon_cells = max(2.0, 0.11 * max(self.rows, self.cols))
        start = rng.choice(self.cells)
        stack, visited, last = [start], {start}, None
        while stack:
            r, c = stack[-1]
            nbrs = [(r + dr, c + dc) for dr, dc in DIRS if self.inside(r + dr, c + dc) and (r + dr, c + dc) not in visited]
            if not nbrs:
                stack.pop(); last = None; continue
            if last and straightness and rng.random() < straightness and (r + last[0], c + last[1]) in nbrs:
                nxt = (r + last[0], c + last[1])
            else:
                nxt = rng.choice(nbrs)
            last = (nxt[0] - r, nxt[1] - c)
            self.open[(r, c)].add(nxt); self.open[nxt].add((r, c))
            visited.add(nxt); stack.append(nxt)
        self._choose_ends(rng)

    def inside(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols and self.mask[r][c]

    def _exterior(self):
        """Cells outside the mask that connect to the grid border (i.e. not enclosed holes)."""
        R, C = self.rows + 2, self.cols + 2
        ins = lambda r, c: 0 <= r - 1 < self.rows and 0 <= c - 1 < self.cols and self.mask[r - 1][c - 1]
        ext, q = {(0, 0)}, deque([(0, 0)])
        while q:
            r, c = q.popleft()
            for dr, dc in DIRS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < R and 0 <= nc < C and (nr, nc) not in ext and not ins(nr, nc):
                    ext.add((nr, nc)); q.append((nr, nc))
        return {(r - 1, c - 1) for r, c in ext}

    def _icon_clear(self, cell_rc, d):
        (r, c), (dr, dc) = cell_rc, d
        s = self.icon_cells
        cx = c + 0.5 + dc * (0.5 + s / 2 + 0.15)
        cy = r + 0.5 + dr * (0.5 + s / 2 + 0.15)
        x0, x1, y0, y1 = cx - s / 2 - 0.1, cx + s / 2 + 0.1, cy - s / 2 - 0.1, cy + s / 2 + 0.1
        for (rr, cc) in self.cells:
            if cc < x1 and cc + 1 > x0 and rr < y1 and rr + 1 > y0:
                return False
        return True

    def _boundary(self):
        ext = self._exterior()
        out = []
        for r, c in self.cells:
            for (dr, dc) in DIRS:
                if (r + dr, c + dc) in ext:
                    out.append(((r, c), (dr, dc)))
        clear = [b for b in out if self._icon_clear(*b)]
        return clear or out

    def _bfs(self, src):
        dist, par, q = {src: 0}, {src: None}, deque([src])
        while q:
            x = q.popleft()
            for y in self.open[x]:
                if y not in dist:
                    dist[y] = dist[x] + 1; par[y] = x; q.append(y)
        return dist, par

    def _choose_ends(self, rng):
        bnd = self._boundary()
        # prefer entering from the top/left half and leaving from the bottom/right half
        top = [b for b in bnd if b[1] == (-1, 0)] or bnd
        s0 = min(top, key=lambda b: (b[0][0], abs(b[0][1] - self.cols / 2)))
        dist, _ = self._bfs(s0[0])
        cand = [b for b in bnd if b[1] in ((1, 0), (0, 1), (0, -1))] or bnd
        end = max(cand, key=lambda b: (dist[b[0]], b[1] == (1, 0)))
        self.start, self.end = s0, end
        dist, par = self._bfs(self.start[0])
        path, x = [], self.end[0]
        while x is not None:
            path.append(x); x = par[x]
        self.path = path[::-1]

    def svg(self, cell=20, wall=3.2, solution=False, pad=None, color="#111", sol_color="#888",
            start_icon="", end_icon="", icon_size=None, width="100%", fill=None):
        icon_size = icon_size or self.icon_cells * cell
        m = wall * 1.6
        # icon placements (relative to maze origin)
        placed = []
        for (rc, dd), icon in ((self.start, start_icon), (self.end, end_icon)):
            if icon:
                (r, c), (dr, dc) = rc, dd
                cx = (c + 0.5) * cell + dc * (cell / 2 + icon_size / 2 + cell * 0.15)
                cy = (r + 0.5) * cell + dr * (cell / 2 + icon_size / 2 + cell * 0.15)
                placed.append((cx - icon_size / 2, cy - icon_size / 2, icon))
        x0 = min([-m] + [x for x, y, _ in placed]); y0 = min([-m] + [y for x, y, _ in placed])
        x1 = max([self.cols * cell + m] + [x + icon_size for x, y, _ in placed])
        y1 = max([self.rows * cell + m] + [y + icon_size for x, y, _ in placed])
        if pad is None:
            pad = 0
        ox, oy = pad - x0, pad - y0  # translate so everything is inside
        W, H = x1 - x0 + 2 * pad, y1 - y0 + 2 * pad
        segs, outer = [], []
        openings = {self.start, self.end}
        for (r, c) in self.cells:
            x, y = ox + c * cell, oy + r * cell
            for (dr, dc) in DIRS:
                nb = (r + dr, c + dc)
                if self.inside(*nb):
                    if nb in self.open[(r, c)] or (dr, dc) in ((-1, 0), (0, -1)):
                        continue  # passage, or interior wall drawn by the other cell
                    if (dr, dc) == (1, 0):
                        segs.append((x, y + cell, x + cell, y + cell))
                    else:
                        segs.append((x + cell, y, x + cell, y + cell))
                else:
                    if ((r, c), (dr, dc)) in openings:
                        continue
                    outer.append({(-1, 0): (x, y, x + cell, y), (1, 0): (x, y + cell, x + cell, y + cell),
                                  (0, -1): (x, y, x, y + cell), (0, 1): (x + cell, y, x + cell, y + cell)}[(dr, dc)])
        size = 'width="100%" height="100%"' if width == "fit" else f'width="{width}"'
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.1f} {H:.1f}" {size}>']
        if fill:
            out.append("".join(f'<rect x="{ox + c * cell - 0.3:.1f}" y="{oy + r * cell - 0.3:.1f}" width="{cell + 0.6:.1f}" '
                               f'height="{cell + 0.6:.1f}" fill="{fill}"/>' for r, c in self.cells))
        if solution:
            pts = " ".join(f"{ox + c * cell + cell / 2:.1f},{oy + r * cell + cell / 2:.1f}" for r, c in self.path)
            (sr, sc), (sdr, sdc) = self.start
            (er, ec), (edr, edc) = self.end
            p0 = f"{ox + (sc + 0.5 + sdc * 0.5) * cell:.1f},{oy + (sr + 0.5 + sdr * 0.5) * cell:.1f}"
            p1 = f"{ox + (ec + 0.5 + edc * 0.5) * cell:.1f},{oy + (er + 0.5 + edr * 0.5) * cell:.1f}"
            out.append(f'<polyline points="{p0} {pts} {p1}" fill="none" stroke="{sol_color}" stroke-width="{cell * 0.42:.1f}" '
                       'stroke-linecap="round" stroke-linejoin="round"/>')
        d = " ".join(f"M{a:.1f} {b:.1f}L{c_:.1f} {d_:.1f}" for a, b, c_, d_ in segs)
        out.append(f'<path d="{d}" stroke="{color}" stroke-width="{wall}" stroke-linecap="round" fill="none"/>')
        d = " ".join(f"M{a:.1f} {b:.1f}L{c_:.1f} {d_:.1f}" for a, b, c_, d_ in outer)
        out.append(f'<path d="{d}" stroke="{color}" stroke-width="{wall * 1.6:.1f}" stroke-linecap="round" fill="none"/>')
        for x, y, icon in placed:
            out.append(f'<g transform="translate({ox + x:.1f},{oy + y:.1f}) scale({icon_size / 100:.3f})">{icon}</g>')
        out.append("</svg>")
        return "".join(out)
