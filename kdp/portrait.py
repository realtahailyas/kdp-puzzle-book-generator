"""Simple, colorable cartoon portraits (B&W line art) built from features: hair, hat, glasses, facial hair, shirt.
portrait(features, uid) -> SVG inner markup for viewBox 0 0 100 110."""
import random

INK = "#111"
S = f'stroke="{INK}" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"'
SHADES = {"dark": "#3a3a3a", "gray": "#9a9a9a", "light": "#ffffff"}

HAIR = ["short", "spiky", "curly", "long", "bob", "bun", "ponytail", "bald"]
HATS = [None, "cap", "beanie", "sunhat", "beret", "chef", "flatcap", "bow"]
GLASSES = [None, "round", "square"]
FACE = [None, "mustache", "beard", "freckles"]
SHIRTS = ["plain", "stripes", "dots", "collar", "tie", "bowtie"]


def _hair_back(h, fill):
    if h == "long":
        return f'<path d="M27 78C24 52 25 20 50 20C75 20 76 52 73 78Z" fill="{fill}" {S}/>'
    if h == "bob":
        return f'<path d="M27 66C25 40 29 19 50 19C71 19 75 40 73 66Z" fill="{fill}" {S}/>'
    if h == "ponytail":
        return f'<ellipse cx="73" cy="52" rx="7" ry="16" transform="rotate(-18 73 52)" fill="{fill}" {S}/>'
    return ""


def _hair_front(h, fill):
    top = f'<path d="M30.5 44C29 26 39 20 50 20C62 20 72 26 69.5 44C66 35 58 31 50 31C42 31 34 35 30.5 44Z" fill="{fill}" {S}/>'
    if h == "short":
        return top
    if h == "spiky":
        return (f'<path d="M30.5 44C29 34 31 28 34 25L35 16L41 22L45 13L50 21L56 13L59 22L65 16L66 25C69 28 71 34 69.5 44'
                f'C66 35 58 31 50 31C42 31 34 35 30.5 44Z" fill="{fill}" {S}/>')
    if h == "curly":
        bumps = "".join(f'<circle cx="{x}" cy="{y}" r="7.5" fill="{fill}" {S}/>'
                        for x, y in ((32, 38), (35, 28), (43, 22), (50, 20), (57, 22), (65, 28), (68, 38)))
        return bumps + f'<path d="M33 40C38 33 44 31 50 31C56 31 62 33 67 40" fill="none" {S}/>'
    if h in ("long", "bob"):
        return f'<path d="M31 44C31 27 41 22 50 22C60 22 69 27 69 44C61 36 56 32 50 34C44 31 37 35 31 44Z" fill="{fill}" {S}/>'
    if h == "bun":
        return f'<circle cx="50" cy="17" r="8" fill="{fill}" {S}/>' + top
    if h == "ponytail":
        return top
    if h == "bald":
        return (f'<path d="M31 50C29.5 44 30 40 32 37" fill="none" {S} stroke-width="5" stroke="{fill if fill != "#ffffff" else INK}"/>'
                f'<path d="M69 50C70.5 44 70 40 68 37" fill="none" {S} stroke-width="5" stroke="{fill if fill != "#ffffff" else INK}"/>')
    return ""


def _hat(h, pal=None):
    pal = pal or {}
    W = f'fill="{pal.get("hat2", "#fff")}"'
    G = f'fill="{pal.get("hat", "#cfcfcf")}"'
    if h == "cap":
        return (f'<path d="M30 37C30 18 70 18 70 37Z" {G} {S}/><path d="M30 37H84C84 41 80 42 72 42H30Z" {W} {S}/>'
                f'<circle cx="50" cy="21" r="2" fill="{INK}"/>')
    if h == "beanie":
        return (f'<path d="M30 36C30 14 70 14 70 36Z" {G} {S}/><rect x="28" y="32" width="44" height="8" rx="3" {W} {S}/>'
                f'<circle cx="50" cy="13" r="5" {W} {S}/>')
    if h == "sunhat":
        return (f'<ellipse cx="50" cy="35" rx="35" ry="7" {W} {S}/><path d="M35 35C35 17 65 17 65 35Z" {W} {S}/>'
                f'<path d="M35.5 31H64.5" {S} stroke-width="5"/>')
    if h == "beret":
        return (f'<ellipse cx="46" cy="27" rx="23" ry="9" transform="rotate(-8 46 27)" fill="{pal.get("accent", "#3a3a3a")}" {S}/>'
                f'<path d="M47 18L48 13" {S}/>')
    if h == "chef":
        return (f'<path d="M34 34C26 30 28 16 38 18C38 8 52 6 56 14C64 8 76 16 70 26C72 30 68 34 66 34Z" {W} {S}/>'
                f'<rect x="33" y="30" width="34" height="9" {W} {S}/>')
    if h == "flatcap":
        return f'<path d="M29 37C29 22 64 18 72 29L82 34C80 38 72 39 29 38Z" {G} {S}/><path d="M66 27L72 36" {S}/>'
    if h == "bow":
        return (f'<path d="M58 22L72 15L71 30Z" {W} {S}/><path d="M58 22L46 13L46 29Z" {W} {S}/>'
                f'<circle cx="58" cy="22" r="3.2" fill="{INK}"/>')
    return ""


def _shirt(kind, uid, pal=None):
    pal = pal or {}
    sc, ac = pal.get("shirt", "#fff"), pal.get("accent", "#3a3a3a")
    body = "M12 110C12 88 30 80 50 80C70 80 88 88 88 110Z"
    out = [f'<path d="{body}" fill="{sc}" {S}/>']
    if kind == "stripes":
        out.append(f'<clipPath id="c{uid}"><path d="{body}"/></clipPath><g clip-path="url(#c{uid})">'
                   + "".join(f'<rect x="0" y="{y}" width="100" height="4" fill="{pal.get("stripe", "#9a9a9a")}"/>' for y in range(86, 110, 8)) + "</g>")
        out.append(f'<path d="{body}" fill="none" {S}/>')
    elif kind == "dots":
        out.append(f'<clipPath id="c{uid}"><path d="{body}"/></clipPath><g clip-path="url(#c{uid})">'
                   + "".join(f'<circle cx="{x + (6 if (y // 9) % 2 else 0)}" cy="{y}" r="2.3" fill="{pal.get("stripe", "#555")}"/>'
                             for y in range(88, 110, 9) for x in range(14, 92, 12)) + "</g>")
        out.append(f'<path d="{body}" fill="none" {S}/>')
    out.append(f'<path d="M42 80L50 90L58 80" fill="none" {S}/>')
    if kind == "collar":
        out.append(f'<path d="M42 80L50 90L40 92ZM58 80L50 90L60 92Z" fill="{pal.get("collar", "#fff")}" {S}/>')
    if kind == "tie":
        out.append(f'<path d="M50 90L46 94L49 110H51L54 94Z" fill="{ac}" {S} stroke-width="1.8"/>')
    if kind == "bowtie":
        out.append(f'<path d="M50 88L40 83V93ZM50 88L60 83V93Z" fill="{ac}" {S} stroke-width="1.8"/><circle cx="50" cy="88" r="2.4" fill="{INK}"/>')
    return "".join(out)


def portrait(f, uid="p", pal=None):
    """f: dict(hair, shade, hat, glasses, face, shirt, mood); pal: optional colors (skin, shirt, hair, hat, hat2, accent, stripe)"""
    pal = pal or {}
    fill = pal.get("hair") or SHADES.get(f.get("shade", "dark"), "#3a3a3a")
    sk = pal.get("skin", "#fff")
    hair = f.get("hair", "short")
    hat = f.get("hat")
    o = [_shirt(f.get("shirt", "plain"), uid, pal), f'<rect x="43" y="62" width="14" height="20" fill="{sk}" {S}/>']
    o.append(_hair_back(hair, fill))
    o.append(f'<ellipse cx="31" cy="48" rx="4.5" ry="6.5" fill="{sk}" {S}/><ellipse cx="69" cy="48" rx="4.5" ry="6.5" fill="{sk}" {S}/>')
    o.append(f'<ellipse cx="50" cy="46" rx="19" ry="22" fill="{sk}" {S}/>')
    o.append(f'<circle cx="43" cy="46" r="2.5" fill="{INK}"/><circle cx="57" cy="46" r="2.5" fill="{INK}"/>')
    o.append(f'<path d="M39.5 40.5Q43 38.5 46.5 40.5M53.5 40.5Q57 38.5 60.5 40.5" fill="none" {S} stroke-width="2"/>')
    o.append(f'<path d="M50 48Q47 54 51.5 55" fill="none" {S} stroke-width="2"/>')
    mood = f.get("mood", "smile")
    mouth = {"smile": "M44 59.5Q50 65 56 59.5", "grin": "M43.5 58.5Q50 67 56.5 58.5Z", "flat": "M45 61H55",
             "o": None}[mood]
    if mouth:
        o.append(f'<path d="{mouth}" fill="{"#fff" if mood == "grin" else "none"}" {S} stroke-width="2.2"/>')
    else:
        o.append(f'<ellipse cx="50" cy="61" rx="2.8" ry="3.4" fill="#fff" {S} stroke-width="2"/>')
    face = f.get("face")
    if face == "freckles":
        o.append("".join(f'<circle cx="{x}" cy="{y}" r="1" fill="{INK}"/>' for x, y in ((38, 52), (41, 54), (36, 55), (62, 52), (59, 54), (64, 55))))
    if face == "beard":
        o.append(f'<path d="M31.5 49C32 64 40 70 50 70C60 70 68 64 68.5 49C65 58 60 63 50 63.5C40 63 35 58 31.5 49Z" fill="{fill}" {S}/>'
                 f'<path d="M45 60Q50 63 55 60" fill="none" stroke="#fff" stroke-width="2"/>')
    if face in ("mustache", "beard"):
        o.append(f'<path d="M42 58.5Q46 54 50 56.5Q54 54 58 58.5Q50 59.5 42 58.5Z" fill="{fill}" {S} stroke-width="1.8"/>')
    g = f.get("glasses")
    if g == "round":
        o.append(f'<circle cx="43" cy="46" r="6" fill="none" {S} stroke-width="2.2"/><circle cx="57" cy="46" r="6" fill="none" {S} stroke-width="2.2"/>'
                 f'<path d="M49 46H51M37 45L31.5 43M63 45L68.5 43" {S} stroke-width="2.2"/>')
    elif g == "square":
        o.append(f'<rect x="36.5" y="41" width="12" height="10" rx="2" fill="none" {S} stroke-width="2.2"/>'
                 f'<rect x="51.5" y="41" width="12" height="10" rx="2" fill="none" {S} stroke-width="2.2"/>'
                 f'<path d="M48.5 45H51.5M36.5 44L31.5 43M63.5 44L68.5 43" {S} stroke-width="2.2"/>')
    if not (hat and hat not in ("bow",) and hair in ("short", "spiky", "curly")):
        o.append(_hair_front(hair, fill))
    elif hat in ("cap", "beanie", "flatcap", "beret", "chef", "sunhat"):
        o.append(f'<path d="M31 44C31 40 32 37 34 35M69 44C69 40 68 37 66 35" fill="none" {S} stroke-width="5" stroke="{fill if fill != "#ffffff" else INK}"/>')
    o.append(_hat(hat, pal))
    return "".join(o)


def svg(f, size_in=1.0, uid="p", pal=None):
    return (f'<svg viewBox="0 0 100 110" style="width:{size_in}in;height:{size_in * 1.1:.3f}in;display:block">'
            f'{portrait(f, uid, pal)}</svg>')


def random_features(rng):
    hair = rng.choice(HAIR)
    return dict(hair=hair, shade=rng.choice(list(SHADES)), hat=rng.choice(HATS),
                glasses=rng.choice(GLASSES), face=rng.choice(FACE), shirt=rng.choice(SHIRTS),
                mood=rng.choice(["smile", "grin", "flat", "o"]))


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from common import Book, html_to_pdf
    rng = random.Random(3)
    cells = "".join(f'<div style="border:1px solid #ccc;padding:4pt">{svg(random_features(rng), 1.5, f"t{i}")}</div>' for i in range(20))
    b = Book()
    b.add(f'<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:6pt">{cells}</div>')
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    (out / "portraits.html").write_text(b.html("portraits"), encoding="utf-8")
    html_to_pdf(out / "portraits.html", out / "portraits.pdf")
