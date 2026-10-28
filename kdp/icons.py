"""Simple black & white line icons in a 100x100 box (for print interiors).
No religious or holiday imagery (owner's rule): animals, food, everyday objects only."""
import math

S = 'stroke="#111" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"'
F = 'fill="#fff"'
G = 'fill="#d9d9d9"'
K = 'fill="#111"'
N = 'fill="none"'


def _u(fill, shapes):
    """Union silhouette: outline drawn once around overlapping primitives (no inner seams)."""
    return (f'<g fill="#111" stroke="#111" stroke-width="8" stroke-linejoin="round">{shapes}</g>'
            f'<g {fill}>{shapes}</g>')


def _dot(x, y, r=4, fill="#111"):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>'


def _sun():
    rays = "".join(f'M{50 + 31 * math.cos(a):.1f} {50 + 31 * math.sin(a):.1f}L{50 + 45 * math.cos(a):.1f} {50 + 45 * math.sin(a):.1f}'
                   for a in [k * math.pi / 4 for k in range(8)])
    return (f'<path d="{rays}" {S}/><circle cx="50" cy="50" r="23" {G} {S}/>'
            f'{_dot(42, 46, 3)}{_dot(58, 46, 3)}<path d="M41 57C46 62 54 62 59 57" {N} {S}/>')


def _clock(h=10, m=10, numbers=False):
    r0 = 40 if numbers else 34
    ticks = "".join(f'M{50 + r0 * math.sin(k * math.pi / 6):.1f} {50 - r0 * math.cos(k * math.pi / 6):.1f}'
                    f'L{50 + 42 * math.sin(k * math.pi / 6):.1f} {50 - 42 * math.cos(k * math.pi / 6):.1f}' for k in range(12))
    nums = "".join(f'<text x="{50 + 32 * math.sin(k * math.pi / 6):.1f}" y="{50 - 32 * math.cos(k * math.pi / 6) + 4.6:.1f}" '
                   f'text-anchor="middle" font-family="Fredoka" font-weight="600" font-size="13" fill="#111">{k or 12}</text>'
                   for k in range(12)) if numbers else ""
    ha = (h % 12 + m / 60) * math.pi / 6
    ma = m * math.pi / 30
    hl, ml = (17, 27) if numbers else (22, 32)
    return (f'<circle cx="50" cy="50" r="45" {F} {S}/><path d="{ticks}" stroke="#111" stroke-width="{3 if numbers else 4}" stroke-linecap="round"/>{nums}'
            f'<path d="M50 50L{50 + hl * math.sin(ha):.1f} {50 - hl * math.cos(ha):.1f}" stroke="#111" stroke-width="7" stroke-linecap="round"/>'
            f'<path d="M50 50L{50 + ml * math.sin(ma):.1f} {50 - ml * math.cos(ma):.1f}" stroke="#111" stroke-width="3.2" stroke-linecap="round"/>'
            f'{_dot(50, 50, 4.5)}')


def _flower():
    petals = "".join(f'<circle cx="{50 + 19 * math.cos(-math.pi / 2 + k * 2 * math.pi / 5):.1f}" '
                     f'cy="{38 + 19 * math.sin(-math.pi / 2 + k * 2 * math.pi / 5):.1f}" r="15" {F} {S}/>' for k in range(5))
    return (f'<path d="M50 56V96" {S} stroke-width="5"/><path d="M50 82C40 70 26 72 22 76C30 86 42 88 50 82Z" {G} {S}/>'
            f'<path d="M50 74C60 62 74 64 78 68C70 78 58 80 50 74Z" {G} {S}/>{petals}<circle cx="50" cy="38" r="11" {G} {S}/>')


ICONS = {
    # --- kept from the first set (secular) ---
    "star": f'<path d="M50 6l12.4 27 29.6 3.4-22 19.9 6.2 29.2L50 70.6 23.8 85.5 30 56.3 8 36.4l29.6-3.4z" {G} {S}/>',
    "mitten": f'<path d="M36 82V40C36 22 48 12 62 14C76 16 82 28 80 44L76 82Z" {G} {S}/><path d="M36 50C26 46 16 50 18 60C20 68 30 70 38 66" {G} {S}/>'
              f'<rect x="32" y="80" width="48" height="14" rx="3" {F} {S}/>',
    "mug": f'<path d="M16 30H70V82C70 90 64 94 56 94H30C22 94 16 90 16 82Z" {F} {S}/><path d="M70 42H78C90 42 90 70 78 70H70" {N} {S}/>'
           f'<path d="M30 20C26 14 34 10 30 4M44 20C40 14 48 10 44 4M58 20C54 14 62 10 58 4" {N} {S}/><path d="M16 44H70" {S}/>',
    "house": f'<path d="M50 8L92 46H80V92H20V46H8Z" {F} {S}/><rect x="42" y="64" width="16" height="28" {G} {S}/>'
             f'<rect x="26" y="52" width="12" height="12" {G} {S}/><rect x="62" y="52" width="12" height="12" {G} {S}/><rect x="64" y="14" width="10" height="20" {F} {S}/>',
    "snowflake": f'<g {S}><path d="M50 6V94M12 28L88 72M12 72L88 28"/><path d="M42 14L50 22L58 14M42 86L50 78L58 86M18 40L28 36L24 26M82 60L72 64L76 74M18 60L28 64L24 74M82 40L72 36L76 26" {N}/></g>',
    "penguin": f'<ellipse cx="50" cy="58" rx="30" ry="36" {K}/><ellipse cx="50" cy="62" rx="19" ry="27" fill="#fff"/>'
               f'<circle cx="43" cy="34" r="4" fill="#fff"/><circle cx="57" cy="34" r="4" fill="#fff"/>{_dot(43, 34, 2)}{_dot(57, 34, 2)}'
               f'<path d="M44 42L50 50L56 42Z" fill="#bbb" {S}/><path d="M34 94H46M54 94H66" stroke="#111" stroke-width="7" stroke-linecap="round"/>',
    "igloo": f'<path d="M8 86C8 40 92 40 92 86Z" {F} {S}/>'
             f'<path d="M10 72H90M22 60H78M30 60V72M70 60V72M50 52V60M24 72V86M76 72V86" {N} {S}/>'
             f'<path d="M38 86V72C38 60 62 60 62 72V86" {G} {S}/>',
    "tophat": f'<rect x="28" y="16" width="44" height="56" rx="3" {G} {S}/><path d="M10 74C10 68 90 68 90 74C90 82 10 82 10 74Z" {F} {S}/>'
              f'<rect x="28" y="56" width="44" height="10" {K}/>',
    "moon": f'<path d="M64 10C40 14 26 36 30 58C34 80 56 94 80 88C60 84 46 66 48 46C50 30 56 18 64 10Z" {G} {S}/>'
            f'<path d="M78 24l3 7 7 3-7 3-3 7-3-7-7-3 7-3z" {K}/>',
    "heart": f'<path d="M50 88C20 64 8 50 8 32C8 18 20 8 32 8C40 8 46 12 50 20C54 12 60 8 68 8C80 8 92 18 92 32C92 50 80 64 50 88Z" {G} {S}/>',
    "bear": f'<circle cx="24" cy="24" r="12" {G} {S}/><circle cx="76" cy="24" r="12" {G} {S}/><circle cx="50" cy="54" r="38" {F} {S}/>'
            f'<ellipse cx="50" cy="68" rx="16" ry="12" {G} {S}/>{_dot(50, 62, 5)}{_dot(37, 46)}{_dot(63, 46)}<path d="M44 74C48 78 52 78 56 74" {N} {S}/>',

    # --- animals ---
    "mouse": f'<circle cx="24" cy="30" r="18" {G} {S}/><circle cx="76" cy="30" r="18" {G} {S}/><ellipse cx="50" cy="58" rx="30" ry="28" {F} {S}/>'
             f'{_dot(40, 52)}{_dot(60, 52)}{_dot(50, 66, 5)}<path d="M42 68L18 62M42 73L20 78M58 68L82 62M58 73L80 78" {S} stroke-width="3"/>',
    "dog": f'<ellipse cx="20" cy="48" rx="12" ry="26" fill="#777" {S} transform="rotate(15 20 48)"/>'
           f'<ellipse cx="80" cy="48" rx="12" ry="26" fill="#777" {S} transform="rotate(-15 80 48)"/><circle cx="50" cy="50" r="32" {F} {S}/>'
           f'<ellipse cx="50" cy="67" rx="16" ry="12" {G} {S}/><ellipse cx="50" cy="61" rx="6" ry="4.5" {K}/>{_dot(38, 44)}{_dot(62, 44)}'
           f'<path d="M44 73C48 77 52 77 56 73" {N} {S}/>',
    "cat": _u(F, '<circle cx="50" cy="58" r="32"/><path d="M22 46L20 10L46 30Z"/><path d="M78 46L80 10L54 30Z"/>') +
           f'<path d="M26 34L25 18L37 28Z" {G}/><path d="M74 34L75 18L63 28Z" {G}/><ellipse cx="38" cy="54" rx="4" ry="6" {K}/>'
           f'<ellipse cx="62" cy="54" rx="4" ry="6" {K}/><path d="M45 65H55L50 70Z" {K}/><path d="M50 70C48 75 43 76 40 73M50 70C52 75 57 76 60 73" {N} {S} stroke-width="3"/>'
           f'<path d="M34 66L10 62M34 71L12 76M66 66L90 62M66 71L88 76" {S} stroke-width="3"/>',
    "rabbit": _u(F, '<ellipse cx="36" cy="28" rx="11" ry="25"/><ellipse cx="64" cy="28" rx="11" ry="25"/><circle cx="50" cy="66" r="28"/>') +
              f'<ellipse cx="36" cy="28" rx="5" ry="16" {G}/><ellipse cx="64" cy="28" rx="5" ry="16" {G}/>{_dot(40, 62)}{_dot(60, 62)}'
              f'<ellipse cx="50" cy="72" rx="4.5" ry="3.5" {K}/><path d="M50 76V80M44 82C47 84 53 84 56 82" {N} {S} stroke-width="3"/>'
              f'<path d="M38 74L18 70M38 78L20 84M62 74L82 70M62 78L80 84" {S} stroke-width="3"/>',
    "monkey": f'<circle cx="16" cy="52" r="13" {G} {S}/><circle cx="84" cy="52" r="13" {G} {S}/><circle cx="16" cy="52" r="6" {F}/><circle cx="84" cy="52" r="6" {F}/>'
              f'<circle cx="50" cy="50" r="34" fill="#888" {S}/><path d="M50 38C40 24 20 32 28 52C22 62 30 84 50 84C70 84 78 62 72 52C80 32 60 24 50 38Z" {F} {S}/>'
              f'{_dot(41, 50)}{_dot(59, 50)}{_dot(46, 64, 2.2)}{_dot(54, 64, 2.2)}<path d="M40 72C46 78 54 78 60 72" {N} {S}/>',
    "panda": f'<circle cx="24" cy="24" r="13" {K}/><circle cx="76" cy="24" r="13" {K}/><circle cx="50" cy="54" r="36" {F} {S}/>'
             f'<ellipse cx="36" cy="50" rx="9" ry="12" {K} transform="rotate(35 36 50)"/><ellipse cx="64" cy="50" rx="9" ry="12" {K} transform="rotate(-35 64 50)"/>'
             f'{_dot(37, 49, 3, "#fff")}{_dot(63, 49, 3, "#fff")}<ellipse cx="50" cy="66" rx="6" ry="4" {K}/><path d="M44 74C48 78 52 78 56 74" {N} {S}/>',
    "frog": _u(G, '<ellipse cx="50" cy="64" rx="42" ry="28"/><circle cx="29" cy="34" r="16"/><circle cx="71" cy="34" r="16"/>') +
            f'<circle cx="29" cy="34" r="9" {F} {S}/><circle cx="71" cy="34" r="9" {F} {S}/>{_dot(30, 35)}{_dot(70, 35)}'
            f'{_dot(45, 56, 2)}{_dot(55, 56, 2)}<path d="M24 66C36 80 64 80 76 66" {N} {S}/>',
    "bee": f'<ellipse cx="46" cy="30" rx="13" ry="18" {F} {S} transform="rotate(-20 46 30)"/><ellipse cx="64" cy="28" rx="13" ry="18" {F} {S} transform="rotate(20 64 28)"/>'
           f'<path d="M86 58L97 61L86 66Z" {K}/><ellipse cx="54" cy="60" rx="32" ry="24" {G} {S}/>'
           f'<path d="M50 38V82M66 40V80" stroke="#111" stroke-width="9"/><circle cx="20" cy="58" r="14" {F} {S}/>{_dot(15, 55, 3.5)}'
           f'<path d="M16 46C12 34 8 30 4 30M22 45C24 33 28 28 32 26" {N} {S}/><path d="M12 64C15 67 19 67 22 64" {N} {S} stroke-width="3"/>',
    "bird": f'<path d="M22 52L4 40L8 64Z" {G} {S}/><ellipse cx="46" cy="56" rx="30" ry="26" {F} {S}/><path d="M74 44L92 50L74 56Z" {G} {S}/>'
            f'{_dot(62, 44)}<path d="M28 56C38 46 56 50 58 62C48 72 34 70 28 56Z" {G} {S}/><path d="M40 82V94M54 82V94M34 94H44M50 94H60" {S}/>',
    "owl": _u(G, '<ellipse cx="50" cy="56" rx="34" ry="38"/><path d="M18 34L20 6L42 24Z"/><path d="M82 34L80 6L58 24Z"/>') +
           f'<circle cx="36" cy="42" r="13" {F} {S}/><circle cx="64" cy="42" r="13" {F} {S}/>{_dot(36, 43, 5)}{_dot(64, 43, 5)}'
           f'<path d="M45 52H55L50 62Z" {F} {S}/><path d="M20 56C20 72 28 84 38 88M80 56C80 72 72 84 62 88" {N} {S}/>'
           f'<path d="M42 72L46 76L50 72L54 76L58 72" {N} {S} stroke-width="3"/>'
           f'<path d="M40 94V98M60 94V98" {S}/>',
    "ladybug": f'<path d="M22 46L8 38M20 62L6 64M26 78L14 88M78 46L92 38M80 62L94 64M74 78L86 88" {S}/><circle cx="50" cy="22" r="14" {K}/>'
               f'<path d="M44 12C40 4 34 4 30 6M56 12C60 4 66 4 70 6" {N} {S}/><circle cx="50" cy="58" r="32" {G} {S}/><path d="M50 27V90" {S}/>'
               f'{_dot(36, 46, 6)}{_dot(64, 46, 6)}{_dot(31, 66, 6)}{_dot(69, 66, 6)}{_dot(41, 80, 5)}{_dot(59, 80, 5)}',
    "butterfly": f'<path d="M48 48C40 24 20 10 10 20C2 30 16 48 48 52Z" {G} {S}/><path d="M52 48C60 24 80 10 90 20C98 30 84 48 52 52Z" {G} {S}/>'
                 f'<path d="M48 54C30 56 14 70 22 84C30 94 46 80 49 60Z" {F} {S}/><path d="M52 54C70 56 86 70 78 84C70 94 54 80 51 60Z" {F} {S}/>'
                 f'<circle cx="26" cy="28" r="5" {F} {S}/><circle cx="74" cy="28" r="5" {F} {S}/>'
                 f'<ellipse cx="50" cy="56" rx="5" ry="24" {K}/><path d="M48 34C44 22 40 18 36 14M52 34C56 22 60 18 64 14" {N} {S}/>',
    "fish": f'<path d="M44 26C50 14 62 14 66 28" {G} {S}/><path d="M70 50L94 30V70Z" {G} {S}/><ellipse cx="44" cy="50" rx="36" ry="26" {F} {S}/>'
            f'{_dot(24, 44, 5)}{_dot(25.5, 42.5, 1.6, "#fff")}<path d="M34 30C40 42 40 58 34 70" {N} {S}/>'
            f'<path d="M48 42C52 46 52 54 48 58M60 38C64 45 64 55 60 62" {N} {S} stroke-width="3"/><path d="M9 55C12 55 14 57 15 59" {N} {S} stroke-width="3"/>',
    "snail": f'<path d="M10 88H80C90 88 94 80 92 70L90 54C89 46 79 46 79 54L78 74H16C8 74 6 84 10 88Z" {G} {S}/>'
             f'<path d="M83 50L79 32M88 50L94 34" {S}/>{_dot(79, 30, 4.5)}{_dot(95, 32, 4.5)}'
             f'<circle cx="46" cy="52" r="27" {F} {S}/><path d="M46 52A3 3 0 0 1 52 52A6 6 0 0 1 40 52A9 9 0 0 1 58 52A12 12 0 0 1 34 52A15 15 0 0 1 64 52A18 18 0 0 1 28 52" {N} {S}/>',
    "turtle": f'<path d="M24 64V84H36V64M60 64V84H72V64" {G} {S}/><ellipse cx="86" cy="58" rx="11" ry="10" {G} {S}/>{_dot(89, 55, 3)}'
              f'<path d="M14 68L3 73L14 76Z" {G} {S}/><path d="M12 70C12 38 30 26 46 26C62 26 80 38 80 70Z" {F} {S}/>'
              f'<path d="M30 68L28 48L46 36L64 48L62 68M28 48L16 54M64 48L76 54M46 36V27M38 68V60M54 68V60" {N} {S} stroke-width="3"/>'
              f'<rect x="8" y="66" width="76" height="10" rx="5" {G} {S}/>',
    "elephant": f'<ellipse cx="20" cy="44" rx="18" ry="27" {G} {S}/><ellipse cx="80" cy="44" rx="18" ry="27" {G} {S}/>' +
                _u(F, '<circle cx="50" cy="42" r="27"/><path d="M41 56C40 74 42 90 54 92C62 93 67 86 63 83C57 85 56 78 59 56Z"/>') +
                f'{_dot(40, 38)}{_dot(60, 38)}<path d="M46 66C49 68 52 68 55 66M45 76C48 78 52 78 55 76" {N} {S} stroke-width="3"/>',

    # --- food & nature ---
    "cheese": f'<path d="M8 50L76 24L92 50Z" {G} {S}/><path d="M8 50H92V82H8Z" {F} {S}/>'
              f'<circle cx="30" cy="66" r="7" {G} {S}/><circle cx="62" cy="70" r="5" {G} {S}/><circle cx="78" cy="60" r="4" {G} {S}/>'
              f'<ellipse cx="58" cy="40" rx="7" ry="3.5" {F} {S}/><ellipse cx="34" cy="44" rx="5" ry="2.5" {F} {S}/>',
    "bone": _u(F, '<circle cx="18" cy="38" r="13"/><circle cx="18" cy="62" r="13"/><circle cx="82" cy="38" r="13"/><circle cx="82" cy="62" r="13"/>'
                  '<rect x="18" y="40" width="64" height="20"/>'),
    "yarn": f'<path d="M70 72C82 82 78 94 94 92" {N} {S}/><circle cx="46" cy="46" r="34" {G} {S}/>'
            f'<path d="M18 30C40 36 60 56 66 78M14 50C34 52 54 66 58 80M28 16C46 30 70 50 80 60M48 12C62 24 76 36 80 46" {N} {S} stroke-width="3"/>',
    "carrot": f'<path d="M62 32C60 18 66 10 72 6M64 34C72 24 82 22 92 24M64 36C76 36 84 42 88 50" {N} {S} stroke-width="5"/>'
              f'<path d="M60 28C70 32 74 40 68 48L26 90C22 94 14 90 18 84L50 34C52 30 56 26 60 28Z" {G} {S}/>'
              f'<path d="M44 54L50 58M34 68L40 72M54 42L58 46" {S} stroke-width="3"/>',
    "honey": f'<path d="M22 36H78C82 36 84 40 82 44C94 56 94 80 78 92H22C6 80 6 56 18 44C16 40 18 36 22 36Z" {G} {S}/>'
             f'<rect x="20" y="24" width="60" height="13" rx="5" {F} {S}/><path d="M32 37V46C32 52 38 52 38 46V37M52 37V50C52 56 58 56 58 50V37" {F} {S}/>'
             f'<rect x="28" y="60" width="44" height="18" rx="4" {F} {S}/><path d="M36 69H64" {S} stroke-width="3"/>',
    "banana": f'<path d="M18 26C12 60 40 90 82 80C88 79 90 73 85 71C52 74 32 56 30 28C30 22 20 20 18 26Z" {G} {S}/>'
              f'<path d="M20 26L16 14" {S} stroke-width="6"/><path d="M26 44C30 60 42 70 60 74" {N} {S} stroke-width="3"/>',
    "bamboo": f'<rect x="28" y="6" width="15" height="88" rx="5" {G} {S}/><path d="M28 34H43M28 62H43" {S}/>'
              f'<rect x="56" y="20" width="15" height="74" rx="5" {G} {S}/><path d="M56 46H71M56 72H71" {S}/>'
              f'<path d="M43 34C54 24 62 24 72 18C62 30 54 34 43 34Z" {F} {S}/><path d="M56 46C46 40 36 44 22 40C34 52 46 52 56 46Z" {F} {S}/>',
    "lilypad": f'<path d="M50 58L64.4 29.8A42 30 0 1 0 89.5 47.7Z" {G} {S}/>'
               f'<path d="M50 58L18 46M50 58L22 74M50 58L50 88M50 58L78 76" {N} {S} stroke-width="3"/>'
               f'<path d="M62 20C58 10 66 6 70 14C74 4 84 8 78 18C88 18 86 28 76 26Z" {F} {S}/>',
    "nest": f'<ellipse cx="38" cy="46" rx="10" ry="13" {F} {S}/><ellipse cx="56" cy="44" rx="10" ry="13" {F} {S}/><ellipse cx="70" cy="50" rx="9" ry="12" {F} {S}/>'
            f'<path d="M8 52C8 84 92 84 92 52C80 60 20 60 8 52Z" {G} {S}/>'
            f'<path d="M14 60C30 68 70 68 86 60M20 70C34 78 66 78 80 70M8 52L2 46M92 52L98 46M30 76L24 84M70 76L76 84" {N} {S} stroke-width="3"/>',
    "leaf": f'<path d="M14 86C10 46 40 14 88 12C88 60 60 90 14 86Z" {G} {S}/>'
            f'<path d="M14 86C34 64 54 42 76 24M34 66L28 48M34 66L52 72M45 55L42 36M45 55L64 60M56 44L56 28M56 44L72 46" {N} {S} stroke-width="3"/>',
    "shell": f'<path d="M40 86H60L57 96H43Z" {F} {S}/><path d="M50 88L14 52C10 30 30 12 50 12C70 12 90 30 86 52Z" {G} {S}/>'
             f'<path d="M50 88L22 30M50 88L35 16M50 88V12M50 88L65 16M50 88L78 30" {N} {S} stroke-width="3"/>',
    "mushroom": f'<path d="M38 54H62L66 90C66 95 34 95 34 90Z" {F} {S}/><path d="M6 58C6 26 28 10 50 10C72 10 94 26 94 58Z" {G} {S}/>'
                f'<circle cx="28" cy="38" r="7" {F} {S}/><circle cx="54" cy="24" r="6" {F} {S}/><circle cx="74" cy="42" r="6" {F} {S}/><circle cx="48" cy="46" r="4" {F} {S}/>',
    "peanut": _u(G, '<circle cx="36" cy="36" r="24"/><circle cx="64" cy="64" r="24"/><circle cx="50" cy="50" r="16"/>') +
              f'<path d="M26 30L30 28M38 22L42 24M30 44L34 42M58 58L62 56M70 64L74 66M60 74L64 72M44 38L46 42" {S} stroke-width="3"/>',
    "strawberry": f'<path d="M50 92C26 76 14 56 16 40C18 28 34 26 50 32C66 26 82 28 84 40C86 56 74 76 50 92Z" {G} {S}/>'
                  f'<path d="M28 30L38 18L50 28L62 18L72 30L50 38Z" {F} {S}/><path d="M50 26V8" {S}/>'
                  + "".join(f'<ellipse cx="{x}" cy="{y}" rx="2" ry="3" {K}/>' for x, y in
                            [(32, 48), (50, 46), (68, 48), (40, 60), (60, 60), (50, 72), (30, 62), (70, 62), (44, 82), (56, 82)]),
    "apple": f'<path d="M50 30C38 20 14 22 14 50C14 74 30 92 42 92C46 92 48 90 50 90C52 90 54 92 58 92C70 92 86 74 86 50C86 22 62 20 50 30Z" {G} {S}/>'
             f'<path d="M50 30C50 20 52 14 56 8" {N} {S}/><path d="M54 18C62 8 76 8 80 12C74 20 62 22 54 18Z" {F} {S}/><path d="M26 46C26 38 30 34 36 32" {N} {S}/>',
    "pear": f'<path d="M50 22C40 22 38 34 36 44C34 52 20 58 20 74C20 88 34 94 50 94C66 94 80 88 80 74C80 58 66 52 64 44C62 34 60 22 50 22Z" {G} {S}/>'
            f'<path d="M50 22C50 14 52 10 56 6" {N} {S}/><path d="M53 14C59 6 71 6 73 10C67 16 59 18 53 14Z" {F} {S}/>',
    "cherry": f'<path d="M32 62C36 44 46 24 66 10M68 62C64 44 66 24 66 10" {N} {S}/><path d="M66 10C74 4 88 6 92 12C84 18 72 18 66 10Z" {F} {S}/>'
              f'<circle cx="30" cy="72" r="17" {G} {S}/><circle cx="70" cy="72" r="17" {G} {S}/><path d="M22 66C22 62 25 60 28 59" {N} {S} stroke-width="3"/>',
    "flower": _flower(),
    "sun": _sun(),
    "cloud": _u(F, '<circle cx="32" cy="56" r="18"/><circle cx="54" cy="42" r="24"/><circle cx="74" cy="58" r="16"/><rect x="14" y="54" width="76" height="22" rx="11"/>'),
    "tree": f'<rect x="42" y="56" width="16" height="38" rx="2" {F} {S}/>' +
            _u(G, '<circle cx="50" cy="32" r="26"/><circle cx="27" cy="50" r="18"/><circle cx="73" cy="50" r="18"/><circle cx="50" cy="54" r="18"/>'),

    # --- everyday things ---
    "umbrella": f'<path d="M50 50V84C50 93 37 93 37 84" {N} {S} stroke-width="5"/>'
                f'<path d="M6 50C6 26 26 10 50 10C74 10 94 26 94 50C88 44 80 44 75 50C70 44 60 44 50 50C40 44 30 44 25 50C20 44 12 44 6 50Z" {G} {S}/>'
                f'<path d="M50 10C40 20 34 34 25 50M50 10C60 20 66 34 75 50" {N} {S}/>',
    "key": f'<path d="M44 44H92V56H86V68H76V56H68V64H58V56H44Z" {G} {S}/><circle cx="28" cy="50" r="19" {G} {S}/><circle cx="24" cy="50" r="7" {F} {S}/>',
    "teapot": f'<path d="M22 56C12 50 8 40 4 34C8 50 10 66 24 72" {G} {S}/><path d="M76 46C94 42 96 72 78 74" {N} {S} stroke-width="6"/>'
              f'<path d="M20 80C14 58 26 38 50 38C74 38 86 58 80 80Z" {F} {S}/><path d="M32 39C32 28 68 28 68 39Z" {G} {S}/>'
              f'<circle cx="50" cy="24" r="5" {G} {S}/><rect x="20" y="78" width="60" height="9" rx="4" {G} {S}/><path d="M34 58H66" {S} stroke-width="3"/>',
    "book": f'<path d="M50 28C38 20 20 20 8 24V82C20 78 38 78 50 86C62 78 80 78 92 82V24C80 20 62 20 50 28Z" {F} {S}/><path d="M50 28V86" {S}/>'
            f'<path d="M16 38C26 36 36 36 42 40M16 50C26 48 36 48 42 52M16 62C26 60 36 60 42 64M58 40C64 36 74 36 84 38M58 52C64 48 74 48 84 50M58 64C64 60 74 60 84 62" {N} stroke="#111" stroke-width="3"/>',
    "clock": _clock(),
    "boat": f'<path d="M50 8V64H16Z" {F} {S}/><path d="M57 18V64H84Z" {G} {S}/><path d="M53 6V70" {S}/>'
            f'<path d="M8 70H92L80 88H20Z" {G} {S}/><path d="M6 96C14 92 22 92 30 96C38 100 46 100 54 96C62 92 70 92 78 96C86 100 92 98 96 96" {N} {S} stroke-width="3"/>',
    "ball": f'<circle cx="50" cy="50" r="42" {F} {S}/><path d="M50 8C32 26 32 74 50 92C68 74 68 26 50 8Z" {G} {S}/>'
            f'<path d="M10 40C30 50 70 50 90 40" {N} {S}/><circle cx="50" cy="50" r="42" {N} {S}/>',
    "kite": f'<path d="M50 74C44 82 56 86 50 96" {N} {S}/><path d="M44 84L50 82L48 88ZM52 90L58 88L56 94Z" {K}/>'
            f'<path d="M50 6L80 40L50 74L20 40Z" {G} {S}/><path d="M50 6V74M20 40H80" {S}/>',
    "car": f'<path d="M8 68V54C8 50 10 48 14 48H24L35 30H66L78 48H88C92 48 94 52 94 56V68Z" {G} {S}/>'
           f'<path d="M39 35H50V48H31Z" {F} {S}/><path d="M55 35H64L73 48H55Z" {F} {S}/>'
           f'<circle cx="28" cy="70" r="12" {F} {S}/>{_dot(28, 70, 4)}<circle cx="74" cy="70" r="12" {F} {S}/>{_dot(74, 70, 4)}',
    "rocket": f'<path d="M34 60L16 84L36 80Z" {G} {S}/><path d="M66 60L84 84L64 80Z" {G} {S}/>'
              f'<path d="M40 80C40 90 46 94 50 98C54 94 60 90 60 80Z" fill="#999" {S}/>'
              f'<path d="M50 6C66 18 70 40 66 80H34C30 40 34 18 50 6Z" {F} {S}/><circle cx="50" cy="42" r="9" {G} {S}/><path d="M40 20H60" {S}/>',
    "planet": f'<ellipse cx="50" cy="52" rx="46" ry="14" {N} {S} transform="rotate(-15 50 52)"/><circle cx="50" cy="50" r="26" {G} {S}/>'
              f'<path d="M30 40C40 45 60 44 72 38M28 56C40 60 58 60 74 54" {N} {S} stroke-width="3"/>'
              f'<path d="M4 52A46 14 0 0 0 96 52" {N} {S} transform="rotate(-15 50 52)"/>',
}


def icon(name, size=60):
    return f'<svg viewBox="0 0 100 100" width="{size}" height="{size}">{ICONS[name]}</svg>'


def coloring(name):
    """Icon with every fill turned white — for coloring pages."""
    s = ICONS[name]
    for g in ('fill="#d9d9d9"', 'fill="#777"', 'fill="#888"', 'fill="#999"', 'fill="#bbb"'):
        s = s.replace(g, 'fill="#fff"')
    return s
