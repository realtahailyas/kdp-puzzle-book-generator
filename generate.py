"""Command-line entry point for the KDP puzzle book generator.

    python generate.py wordsearch examples/wordsearch_book.json -o output/wordsearch
    python generate.py sampler -o output/sampler
    python generate.py check output/wordsearch/interior.pdf
    python generate.py qa output/wordsearch
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "kdp"))

from common import Book, esc, html_to_pdf  # noqa: E402


def cmd_wordsearch(a):
    import ws_book
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    cfg["puzzles"] = [tuple(p) for p in cfg["puzzles"]]
    pdf, pages, _ = ws_book.build(cfg, a.out)
    print(f"wrote {pdf} ({pages} pages)")


SAMPLER_CSS = """
.t { font: 800 28pt 'Playfair'; text-align: center; margin-bottom: 6pt; }
.s { font: italic 15pt 'Lora'; text-align: center; color: #444; margin-bottom: 14pt; }
.box { width: 6.2in; margin: 0 auto; }
.words { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6pt 12pt; margin-top: 12pt; font: 700 16pt 'Atkinson'; }
"""


def cmd_sampler(a):
    """One page each of a word search, a shaped maze and a sudoku, plus a solutions page."""
    from maze import Maze
    from puzzles import sudoku, sudoku_svg
    from wordsearch import EASY_DIRS, generate, svg

    words = ["GARDEN", "TULIP", "DAISY", "ROSE", "IVY", "FERN", "LILY", "POPPY", "ORCHID", "SUNFLOWER"]
    grid, placed = generate(words, size=13, dirs=EASY_DIRS, seed=a.seed)
    maze = Maze("heart", rows=22, cols=22, seed=a.seed)
    puz, sol = sudoku(a.seed, givens=36)

    book = Book(SAMPLER_CSS)
    wl = "".join(f"<div>{esc(w)}</div>" for w in sorted(words))
    book.add(f'<div class="t">Word Search</div><div class="s">Find every flower in the grid.</div>'
             f'<div class="box">{svg(grid)}</div><div class="words">{wl}</div>')
    book.add(f'<div class="t">Heart Maze</div><div class="s">Find the path from start to finish.</div>'
             f'<div class="box">{maze.svg(cell=20)}</div>')
    book.add(f'<div class="t">Sudoku</div><div class="s">Fill every row, column and box with 1 to 9.</div>'
             f'<div class="box">{sudoku_svg(puz)}</div>')
    book.add('<div class="t">Solutions</div>'
             f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:16pt">'
             f'<div>{svg(grid, placed, show=True)}</div><div>{maze.svg(cell=20, solution=True)}</div>'
             f'<div>{sudoku_svg(puz, sol)}</div></div>')
    book.pad_even()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    html_path = out / "interior.html"
    html_path.write_text(book.html("Puzzle sampler"), encoding="utf-8")
    pdf = html_to_pdf(html_path, out / "interior.pdf")
    print(f"wrote {pdf} ({len(book.pages)} pages)")


def cmd_check(a):
    import check_pdf
    pages = [int(x) for x in a.render.split(",")] if a.render else []
    check_pdf.check(a.pdf, pages, a.prefix or str(Path(a.pdf).with_suffix("")))


def cmd_qa(a):
    import qa
    qa.main(a.books)


def main():
    p = argparse.ArgumentParser(description="Generate print-ready KDP puzzle book interiors.")
    sub = p.add_subparsers(dest="cmd", required=True)

    w = sub.add_parser("wordsearch", help="build a large-print word search interior from a JSON config")
    w.add_argument("config")
    w.add_argument("-o", "--out", default="output/wordsearch")
    w.set_defaults(func=cmd_wordsearch)

    s = sub.add_parser("sampler", help="build a 4-page sampler: word search, maze, sudoku, solutions")
    s.add_argument("-o", "--out", default="output/sampler")
    s.add_argument("--seed", type=int, default=7)
    s.set_defaults(func=cmd_sampler)

    c = sub.add_parser("check", help="print page count, size and font embedding for a PDF")
    c.add_argument("pdf")
    c.add_argument("--render", help="comma-separated page numbers to render to PNG")
    c.add_argument("--prefix", help="PNG path prefix for --render")
    c.set_defaults(func=cmd_check)

    q = sub.add_parser("qa", help="KDP preflight for book folders (interior.pdf, optional cover.pdf/listing.md)")
    q.add_argument("books", nargs="+")
    q.set_defaults(func=cmd_qa)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
