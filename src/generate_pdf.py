# -*- coding: utf-8 -*-
"""
Cuaderno de verano de Laura - 30 dias de repaso de mates (2o primaria -> 3o).
Restas con llevadas (2 y 3 cifras), tablas de multiplicar progresivas y
problemas graficos. Diseñado para imprimir en BLANCO Y NEGRO, 1 hoja por dia.
"""
import os, random
random.seed(2026)

NAME = os.environ.get("KID_NAME", "Laura")

# ----------------------------------------------------------------------------
# Utilidades de restas
# ----------------------------------------------------------------------------
def digits(n, width):
    return [int(d) for d in str(n).rjust(width, "0")]

def count_borrows(a, b):
    w = max(len(str(a)), len(str(b)))
    da, db = digits(a, w), digits(b, w)
    borrow = 0
    cnt = 0
    for i in range(w - 1, -1, -1):
        cur = da[i] - borrow
        if cur < db[i]:
            cnt += 1
            borrow = 1
        else:
            borrow = 0
    return cnt

def gen_sub(lo_a, hi_a, lo_b, hi_b, borrows=None, min_result=1):
    """borrows=0 -> sin llevada; borrows>=1 -> con al menos esa cantidad; 'any' -> >=1"""
    for _ in range(20000):
        a = random.randint(lo_a, hi_a)
        b = random.randint(lo_b, min(hi_b, a))
        if a - b < min_result:
            continue
        c = count_borrows(a, b)
        if borrows == 0 and c != 0:
            continue
        if borrows == 1 and c != 1:
            continue
        if borrows == 2 and c < 2:
            continue
        if borrows == "any" and c == 0:
            continue
        return a, b
    return a, b

def uniq_subs(n, **kw):
    seen, out = set(), []
    tries = 0
    while len(out) < n and tries < 10000:
        tries += 1
        p = gen_sub(**kw)
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out

# ----------------------------------------------------------------------------
# Componentes visuales (HTML / SVG en blanco y negro)
# ----------------------------------------------------------------------------
def sub_problem(a, b, borrow_hint=True):
    w = max(len(str(a)), len(str(b)))
    da = str(a).rjust(w)
    db = str(b).rjust(w)
    def cells(s, cls=""):
        out = ""
        for ch in s:
            out += f'<span class="dc {cls}">{"" if ch==" " else ch}</span>'
        return out
    hint = ""
    if borrow_hint:
        hint = '<div class="brow">' + "".join('<span class="bcell"></span>' for _ in range(w)) + "</div>"
    ans = '<div class="arow">' + "".join('<span class="dc ansc"></span>' for _ in range(w)) + "</div>"
    return f'''<div class="sub">
      {hint}
      <div class="nrow">{cells(da)}</div>
      <div class="nrow"><span class="op">&minus;</span>{cells(db)}</div>
      <div class="bar"></div>
      {ans}
    </div>'''

def sub_grid(problems, borrow_hint=True):
    items = "".join(sub_problem(a, b, borrow_hint) for a, b in problems)
    return f'<div class="subgrid">{items}</div>'

def mult_items(pairs, answered=False):
    out = ""
    for x, y in pairs:
        out += f'<div class="mitem"><span class="mx">{x} &times; {y} =</span><span class="mbox"></span></div>'
    return f'<div class="mgrid">{out}</div>'

def mult_missing(triples):
    # (a, b, result) -> a x [] = result
    out = ""
    for a, b, r in triples:
        out += f'<div class="mitem"><span class="mx">{a} &times; </span><span class="mbox small"></span><span class="mx"> = {r}</span></div>'
    return f'<div class="mgrid">{out}</div>'

# --- SVG helpers -----------------------------------------------------------
def svg_array(rows, cols, r=9, gap=24):
    W = cols * gap + gap
    H = rows * gap + gap
    dots = ""
    for i in range(rows):
        for j in range(cols):
            cx = gap/2 + j*gap + gap/2
            cy = gap/2 + i*gap + gap/2
            dots += f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r}" fill="none" stroke="#111" stroke-width="2.2"/>'
    return f'<svg viewBox="0 0 {W:.0f} {H:.0f}" class="artsvg" style="max-width:{W:.0f}px">{dots}</svg>'

def svg_numberline(step, count, start=0):
    # jumps of `step`, `count` jumps
    pad = 26
    seg = 66
    W = pad*2 + seg*count
    H = 92
    line = f'<line x1="{pad}" y1="58" x2="{W-pad}" y2="58" stroke="#111" stroke-width="2.4"/>'
    ticks = ""
    labels = ""
    arcs = ""
    for i in range(count+1):
        x = pad + i*seg
        ticks += f'<line x1="{x}" y1="50" x2="{x}" y2="66" stroke="#111" stroke-width="2.4"/>'
        val = start + i*step
        labels += f'<text x="{x}" y="84" class="nl">{val}</text>'
        if i < count:
            x2 = pad + (i+1)*seg
            mx = (x+x2)/2
            arcs += f'<path d="M {x} 50 Q {mx} 8 {x2} 50" fill="none" stroke="#111" stroke-width="2" stroke-dasharray="1 0"/>'
            arcs += f'<text x="{mx:.0f}" y="30" class="nlj">+{step}</text>'
    return f'<svg viewBox="0 0 {W} {H}" class="artsvg" style="max-width:{min(W,520)}px">{line}{arcs}{ticks}{labels}</svg>'

def svg_base10(hundreds=0, tens=0, units=0, label=None):
    parts = []
    x = 4
    # hundreds as 3x3-ish big square with grid (represent 100)
    for _ in range(hundreds):
        g = f'<rect x="{x}" y="4" width="54" height="54" fill="none" stroke="#111" stroke-width="2.2"/>'
        for k in range(1,6):
            g += f'<line x1="{x}" y1="{4+k*9}" x2="{x+54}" y2="{4+k*9}" stroke="#111" stroke-width="1"/>'
            g += f'<line x1="{x+k*9}" y1="4" x2="{x+k*9}" y2="58" stroke="#111" stroke-width="1"/>'
        parts.append(g); x += 64
    # tens as tall rods
    for _ in range(tens):
        g = f'<rect x="{x}" y="4" width="14" height="54" fill="none" stroke="#111" stroke-width="2.2"/>'
        for k in range(1,10):
            g += f'<line x1="{x}" y1="{4+k*5.4:.1f}" x2="{x+14}" y2="{4+k*5.4:.1f}" stroke="#111" stroke-width="0.8"/>'
        parts.append(g); x += 22
    # units as small squares
    ux = x + 4
    uy = 4
    for i in range(units):
        parts.append(f'<rect x="{ux}" y="{uy}" width="12" height="12" fill="none" stroke="#111" stroke-width="2"/>')
        ux += 16
        if (i+1) % 5 == 0:
            ux = x + 4; uy += 16
    W = max(ux + 10, x + 90)
    H = 66
    return f'<svg viewBox="0 0 {W:.0f} {H}" class="artsvg" style="max-width:{min(int(W),300)}px">{"".join(parts)}</svg>'

# --- iconos para problemas -------------------------------------------------
def _icon(kind):
    # devuelve inner markup en viewBox 0 0 40 40
    if kind == "manzana":
        return ('<path d="M20 14 C13 8, 6 14, 9 24 C11 32, 17 36, 20 36 C23 36, 29 32, 31 24 C34 14, 27 8, 20 14 Z" '
                'fill="none" stroke="#111" stroke-width="2"/><path d="M20 14 C20 10 22 7 25 6" fill="none" stroke="#111" stroke-width="2"/>'
                '<path d="M22 9 C26 6 30 8 30 11 C27 13 23 12 22 9 Z" fill="none" stroke="#111" stroke-width="1.6"/>')
    if kind == "globo":
        return ('<ellipse cx="20" cy="16" rx="12" ry="14" fill="none" stroke="#111" stroke-width="2"/>'
                '<path d="M20 30 L20 38" stroke="#111" stroke-width="1.6"/><path d="M17 30 L20 33 L23 30 Z" fill="none" stroke="#111" stroke-width="1.6"/>')
    if kind == "moneda":
        return ('<circle cx="20" cy="20" r="15" fill="none" stroke="#111" stroke-width="2"/>'
                '<circle cx="20" cy="20" r="11" fill="none" stroke="#111" stroke-width="1"/>'
                '<text x="20" y="26" text-anchor="middle" font-size="15" font-family="Comic Neue" font-weight="700" fill="#111">&euro;</text>')
    if kind == "flor":
        p = '<circle cx="20" cy="20" r="4.5" fill="none" stroke="#111" stroke-width="1.8"/>'
        import math
        for a in range(0,360,60):
            cx = 20 + 9*math.cos(math.radians(a)); cy = 20 + 9*math.sin(math.radians(a))
            p += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="5" fill="none" stroke="#111" stroke-width="1.8"/>'
        return p
    if kind == "caramelo":
        return ('<circle cx="20" cy="20" r="9" fill="none" stroke="#111" stroke-width="2"/>'
                '<path d="M11 20 L3 14 L4 26 Z" fill="none" stroke="#111" stroke-width="1.6"/>'
                '<path d="M29 20 L37 14 L36 26 Z" fill="none" stroke="#111" stroke-width="1.6"/>')
    if kind == "galleta":
        d = '<circle cx="20" cy="20" r="15" fill="none" stroke="#111" stroke-width="2"/>'
        for (cx,cy) in [(14,15),(26,16),(20,24),(15,27),(27,26)]:
            d += f'<circle cx="{cx}" cy="{cy}" r="1.8" fill="#111"/>'
        return d
    if kind == "pez":
        return ('<path d="M8 20 C14 10, 28 10, 32 20 C28 30, 14 30, 8 20 Z" fill="none" stroke="#111" stroke-width="2"/>'
                '<path d="M32 20 L38 14 L38 26 Z" fill="none" stroke="#111" stroke-width="1.8"/>'
                '<circle cx="15" cy="18" r="1.7" fill="#111"/>')
    if kind == "estrella":
        import math
        pts = []
        for i in range(10):
            ang = -math.pi/2 + i*math.pi/5
            rad = 16 if i%2==0 else 7
            pts.append(f'{20+rad*math.cos(ang):.1f},{20+rad*math.sin(ang):.1f}')
        return f'<polygon points="{" ".join(pts)}" fill="none" stroke="#111" stroke-width="2"/>'
    return '<circle cx="20" cy="20" r="14" fill="none" stroke="#111" stroke-width="2"/>'

def icons_row(n, kind, cross=0):
    cells = ""
    for i in range(n):
        x = ('<line x1="4" y1="4" x2="36" y2="36" stroke="#111" stroke-width="2.4"/>'
             '<line x1="36" y1="4" x2="4" y2="36" stroke="#111" stroke-width="2.4"/>') if i >= n - cross else ""
        cells += f'<svg viewBox="0 0 40 40" class="ic">{_icon(kind)}{x}</svg>'
    return f'<div class="iconrow">{cells}</div>'

def icon_groups(groups, per, kind):
    boxes = ""
    for _ in range(groups):
        inner = "".join(f'<svg viewBox="0 0 40 40" class="ic sm">{_icon(kind)}</svg>' for _ in range(per))
        boxes += f'<div class="grpbox">{inner}</div>'
    return f'<div class="grouprow">{boxes}</div>'

def answer_lines(n=1, label="Solución:"):
    lines = "".join('<div class="ansline"></div>' for _ in range(n))
    op = '<div class="opbox">Operación:</div>'
    return f'<div class="probans">{op}{lines}<div class="sollabel">{label} <span class="solbox"></span></div></div>'

# ----------------------------------------------------------------------------
# Bloques de alto nivel
# ----------------------------------------------------------------------------
def explain(title, body_html):
    return f'''<div class="explain">
      <div class="explain-h"><span class="bulb">&#9733;</span> {title}</div>
      <div class="explain-body">{body_html}</div>
    </div>'''

def section(title, body_html):
    return f'<div class="sec"><div class="sec-h">{title}</div>{body_html}</div>'

def word_problem(num, text, illustration, nlines=1):
    return f'''<div class="wp">
      <div class="wp-h">Problema {num}</div>
      <div class="wp-text">{text}</div>
      <div class="wp-illus">{illustration}</div>
      {answer_lines(nlines)}
    </div>'''

# ----------------------------------------------------------------------------
# Tabla de multiplicar (referencia)
# ----------------------------------------------------------------------------
def table_reference(t, upto=10):
    rows = ""
    for n in range(1, upto+1):
        rows += f'<div class="trow"><span class="tl">{t} &times; {n}</span><span class="teq">=</span><span class="tr">{t*n}</span></div>'
    return f'<div class="tablecard"><div class="tablecard-h">La tabla del {t}</div><div class="tablebody">{rows}</div></div>'

def table_reference_blank(t, upto=10):
    rows = ""
    for n in range(1, upto+1):
        rows += f'<div class="trow"><span class="tl">{t} &times; {n}</span><span class="teq">=</span><span class="tr blank"></span></div>'
    return f'<div class="tablecard"><div class="tablecard-h">Completa la tabla del {t}</div><div class="tablebody">{rows}</div></div>'

# ============================================================================
# CONTENIDO DE LOS 30 DIAS
# ============================================================================
DAYS = []

def add_day(n, theme, body, tag="unos 15 minutos", new=False):
    DAYS.append(dict(n=n, theme=theme, body=body, tag=tag, new=new))

# ---- SEMANA 1: repaso y arranque ----
# Dia 1
add_day(1, "Empezamos: restas sin llevada",
    explain("Recuerda: colocamos las cifras bien alineadas",
        '<p>En una resta ponemos las <b>unidades debajo de las unidades</b> y las '
        '<b>decenas debajo de las decenas</b>. Restamos empezando por la derecha.</p>'
        '<div class="worked">'
        '<div class="wex">' + sub_problem(48, 25, borrow_hint=False) + '<div class="wexlab">8 &minus; 5 = 3 &nbsp;y&nbsp; 4 &minus; 2 = 2</div></div>'
        '</div>')
    + section("Calcula estas restas", sub_grid(uniq_subs(6, lo_a=20, hi_a=99, lo_b=10, hi_b=99, borrows=0), borrow_hint=False)))

# Dia 2 - NUEVO restas con llevada 2 cifras
d2ex = sub_problem(52, 27, borrow_hint=True)
add_day(2, "NUEVO: restas con llevada", new=True, body=
    explain("&iexcl;Cuando no puedo restar, pido prestado!",
        '<p>Si el numero de arriba es <b>mas pequeño</b>, la decena de al lado le '
        '<b>presta 10</b>. Ponemos una pequeña marca (la &laquo;llevada&raquo;).</p>'
        '<div class="steps">'
        '<div class="step"><span class="stepn">1</span> 2 &minus; 7 no puedo. Pido 1 decena: ahora tengo <b>12</b>. 12 &minus; 7 = <b>5</b>.</div>'
        '<div class="step"><span class="stepn">2</span> Como preste una decena, arriba quedan <b>4</b> decenas. 4 &minus; 2 = <b>2</b>.</div>'
        '</div>'
        '<div class="worked"><div class="wex">' + d2ex + '<div class="wexlab">Resultado: 25</div></div>'
        '<div class="b10note">Mira: 12 unidades = 1 decena y 2 unidades ' + svg_base10(tens=1, units=2) + '</div></div>')
    + section("Ahora tu. Recuerda apuntar la llevada",
        sub_grid(uniq_subs(6, lo_a=20, hi_a=99, lo_b=10, hi_b=89, borrows=1))))

# Dia 3
add_day(3, "Practico las restas con llevada", body=
    section("Calcula", sub_grid(uniq_subs(6, lo_a=30, hi_a=99, lo_b=10, hi_b=89, borrows=1)))
    + word_problem(1, "En una caja había <b>34</b> galletas. La familia se comió <b>16</b>. &iquest;Cuántas galletas quedan en la caja?",
        icons_row(12, "galleta", cross=0) , nlines=1))

# Dia 4 - NUEVO concepto multiplicacion + tabla del 2
add_day(4, "NUEVO: multiplicar es sumar grupos iguales", new=True, body=
    explain("Multiplicar = sumar el mismo número varias veces",
        '<p><b>3 &times; 4</b> significa <b>3 grupos de 4</b>. Es lo mismo que '
        '4 + 4 + 4 = <b>12</b>.</p>'
        '<div class="twocol"><div>' + svg_array(3,4) + '<div class="capt">3 filas de 4 = 12</div></div>'
        '<div>' + svg_numberline(2, 5) + '<div class="capt">De 2 en 2 (la tabla del 2)</div></div></div>')
    + section("Repasa la tabla del 2",
        '<div class="tworef">' + table_reference(2) + '<div class="prac">'
        + mult_items([(2,3),(2,5),(2,8),(2,6),(2,9),(2,4)]) + '</div></div>'))

# Dia 5 - tabla del 3
add_day(5, "Repaso la tabla del 3", body=
    explain("La tabla del 3: cuenta de 3 en 3",
        '<div>' + svg_numberline(3,6) + '</div>')
    + section("Practica la tabla del 3",
        '<div class="tworef">' + table_reference(3) + '<div class="prac">'
        + mult_items([(3,2),(3,4),(3,7),(3,5),(3,9),(3,6),(3,8),(3,3)]) + '</div></div>'))

# Dia 6 - mezcla
add_day(6, "Mezcla: restas y tablas", body=
    section("Restas con llevada", sub_grid(uniq_subs(4, lo_a=30, hi_a=99, lo_b=10, hi_b=89, borrows=1)))
    + section("Tablas del 2 y del 3", mult_items([(2,7),(3,6),(2,9),(3,8),(2,4),(3,5),(2,8),(3,9)]))
    + word_problem(1, "Ana tiene <b>3</b> cajas y en cada caja hay <b>2</b> manzanas. &iquest;Cuántas manzanas tiene en total?",
        icon_groups(3,2,"manzana"), nlines=1))

# Dia 7 - NUEVO restas 3 cifras sin llevada
add_day(7, "NUEVO: restas de 3 cifras", new=True, body=
    explain("Ahora con centenas, decenas y unidades",
        '<p>Igual que antes, pero con <b>una columna mas</b>: las <b>centenas</b>. '
        'Colocamos C con C, D con D, U con U y restamos desde la derecha.</p>'
        '<div class="worked"><div class="wex">' + sub_problem(376, 152, borrow_hint=False)
        + '<div class="wexlab">6&minus;2=4 &middot; 7&minus;5=2 &middot; 3&minus;1=2</div></div>'
        '<div class="b10note">' + svg_base10(hundreds=3, tens=7, units=6) + '<div class="capt">3 centenas, 7 decenas y 6 unidades = 376</div></div></div>')
    + section("Calcula (todavía sin llevada)", sub_grid(uniq_subs(6, lo_a=200, hi_a=999, lo_b=100, hi_b=999, borrows=0), borrow_hint=False)))

# ---- SEMANA 2 ----
# Dia 8 - NUEVO restas 3 cifras con 1 llevada
add_day(8, "NUEVO: 3 cifras con una llevada", new=True, body=
    explain("Pedimos prestado también con 3 cifras",
        '<p>Cuando una columna no se puede restar, la de al lado le presta 10, '
        'exactamente igual que con 2 cifras.</p>'
        '<div class="steps">'
        '<div class="step"><span class="stepn">1</span> Empieza por las <b>unidades</b>.</div>'
        '<div class="step"><span class="stepn">2</span> Si no puedes, pide prestado y apunta la llevada.</div>'
        '<div class="step"><span class="stepn">3</span> Sigue con decenas y centenas.</div></div>'
        '<div class="worked"><div class="wex">' + sub_problem(435, 128, borrow_hint=True) + '<div class="wexlab">Resultado: 307</div></div></div>')
    + section("Practica", sub_grid(uniq_subs(6, lo_a=200, hi_a=999, lo_b=110, hi_b=899, borrows=1))))

# Dia 9
add_day(9, "Practico restas de 3 cifras", body=
    section("Calcula", sub_grid(uniq_subs(6, lo_a=200, hi_a=999, lo_b=110, hi_b=899, borrows=1)))
    + word_problem(1, "Un álbum tiene <b>250</b> cromos. Laura ya ha pegado <b>134</b>. &iquest;Cuántos cromos le faltan por pegar?",
        '<div class="bignum">250 &minus; 134</div>', nlines=1))

# Dia 10 - NUEVO tabla del 4
add_day(10, "NUEVO: la tabla del 4", new=True, body=
    explain("La tabla del 4: cuenta de 4 en 4",
        '<p>4 &times; 3 son <b>3 grupos de 4</b>. Fíjate: la tabla del 4 es el <b>doble</b> de la del 2.</p>'
        '<div class="twocol"><div>' + svg_array(4,3) + '<div class="capt">4 &times; 3 = 12</div></div>'
        '<div>' + svg_numberline(4,5) + '</div></div>')
    + section("Practica la tabla del 4",
        '<div class="tworef">' + table_reference(4) + '<div class="prac">'
        + mult_items([(4,2),(4,5),(4,3),(4,7),(4,4),(4,6),(4,8),(4,9)]) + '</div></div>'))

# Dia 11
add_day(11, "Tabla del 4 y restas", body=
    section("Tabla del 4", mult_items([(4,6),(4,3),(4,8),(4,5),(4,9),(4,7),(4,4),(4,2)]))
    + section("Restas de 3 cifras", sub_grid(uniq_subs(3, lo_a=300, hi_a=999, lo_b=110, hi_b=799, borrows=1))))

# Dia 12 - NUEVO tabla del 5
add_day(12, "NUEVO: la tabla del 5", new=True, body=
    explain("La tabla del 5 termina siempre en 0 o en 5",
        '<p>Cuenta de 5 en 5, &iexcl;como los dedos de las manos! 5, 10, 15, 20... '
        'Los resultados <b>acaban en 0 o en 5</b>.</p>'
        '<div>' + svg_numberline(5,6) + '</div>')
    + section("Practica la tabla del 5",
        '<div class="tworef">' + table_reference(5) + '<div class="prac">'
        + mult_items([(5,3),(5,6),(5,2),(5,8),(5,4),(5,7),(5,9),(5,5)]) + '</div></div>'))

# Dia 13
add_day(13, "Tablas del 4 y del 5", body=
    section("Mezcla de tablas", mult_items([(4,7),(5,6),(4,4),(5,9),(5,3),(4,8),(5,7),(4,6),(5,8),(4,9)]))
    + word_problem(1, "En el jardín hay <b>5</b> macetas y en cada una crecen <b>3</b> flores. &iquest;Cuántas flores hay en total?",
        icon_groups(5,3,"flor"), nlines=1))

# Dia 14 - NUEVO restas 3 cifras con 2 llevadas
add_day(14, "NUEVO: restas con dos llevadas", new=True, body=
    explain("A veces hay que pedir prestado dos veces",
        '<p>No pasa nada si pides prestado en <b>dos columnas</b>. Ve paso a paso, '
        'de derecha a izquierda, y apunta cada llevada.</p>'
        '<div class="worked"><div class="wex">' + sub_problem(624, 158, borrow_hint=True) + '<div class="wexlab">Resultado: 466</div></div></div>')
    + section("Practica con calma", sub_grid(uniq_subs(6, lo_a=300, hi_a=999, lo_b=140, hi_b=899, borrows=2))))

# ---- SEMANA 3 ----
# Dia 15 - repaso medio camino
add_day(15, "&iexcl;Mitad del camino! Gran repaso", tag="repaso &middot; unos 15 min", body=
    section("Restas variadas", sub_grid(uniq_subs(4, lo_a=200, hi_a=999, lo_b=110, hi_b=899, borrows="any")))
    + section("Tablas del 2, 3, 4 y 5", mult_items([(3,7),(5,8),(2,9),(4,6),(5,4),(3,8),(4,9),(2,7)]))
    + word_problem(1, "Había <b>18</b> globos en la fiesta y se explotaron <b>7</b>. &iquest;Cuántos globos quedan?",
        icons_row(18,"globo",cross=7), nlines=1))

# Dia 16 - NUEVO tabla del 10
add_day(16, "NUEVO: la tabla del 10 (&iexcl;la más fácil!)", new=True, body=
    explain("Para multiplicar por 10, añade un cero",
        '<p>10 &times; 4 = <b>40</b>. Solo tienes que poner el numero y <b>añadir un 0</b> detrás.</p>'
        '<div>' + svg_numberline(10,5) + '</div>')
    + section("Practica la tabla del 10",
        '<div class="tworef">' + table_reference(10) + '<div class="prac">'
        + mult_items([(10,3),(10,7),(10,5),(10,9),(10,2),(10,6),(10,8),(10,4)]) + '</div></div>'))

# Dia 17
add_day(17, "Tablas del 5 y del 10", body=
    section("Mezcla de tablas", mult_items([(5,7),(10,6),(5,9),(10,3),(5,4),(10,8),(5,6),(10,9)]))
    + word_problem(1, "Cada bolsa de cromos cuesta <b>5</b> euros. Laura compra <b>4</b> bolsas. &iquest;Cuánto dinero gasta en total?",
        icon_groups(4,5,"moneda"), nlines=1))

# Dia 18 - NUEVO restas con ceros
add_day(18, "NUEVO: restas con ceros", new=True, body=
    explain("&iquest;Y si arriba hay un 0?",
        '<p>Cuando arriba hay un <b>0</b> y tienes que restar, el 0 también pide prestado '
        'a la cifra de su izquierda. Ve paso a paso.</p>'
        '<div class="worked"><div class="wex">' + sub_problem(300, 148, borrow_hint=True) + '<div class="wexlab">Resultado: 152</div></div></div>')
    + section("Practica", sub_grid([(300,148),(500,236),(400,127),(600,354),(200,86),(700,268)])))

# Dia 19 - NUEVO tabla del 6
add_day(19, "NUEVO: la tabla del 6", new=True, body=
    explain("La tabla del 6: cuenta de 6 en 6",
        '<p>6 &times; 4 son <b>4 grupos de 6</b>. Es el <b>doble</b> de la tabla del 3.</p>'
        '<div class="twocol"><div>' + svg_array(6,3) + '<div class="capt">6 &times; 3 = 18</div></div>'
        '<div>' + svg_numberline(6,5) + '</div></div>')
    + section("Practica la tabla del 6",
        '<div class="tworef">' + table_reference(6) + '<div class="prac">'
        + mult_items([(6,2),(6,4),(6,3),(6,6),(6,5),(6,7),(6,8),(6,9)]) + '</div></div>'))

# Dia 20
add_day(20, "Tablas 4, 5 y 6 + restas", body=
    section("Mezcla de tablas", mult_items([(4,8),(6,7),(5,9),(6,4),(4,6),(5,8),(6,9),(6,6)]))
    + section("Restas de 3 cifras", sub_grid(uniq_subs(3, lo_a=300, hi_a=999, lo_b=140, hi_b=899, borrows="any"))))

# Dia 21 - problemas
add_day(21, "Día de problemas", body=
    word_problem(1, "Un tren llevaba <b>420</b> pasajeros. En una estación se bajaron <b>135</b>. &iquest;Cuántos pasajeros siguen en el tren?",
        '<div class="bignum">420 &minus; 135</div>', nlines=1)
    + word_problem(2, "Hay <b>6</b> platos y en cada uno hay <b>4</b> caramelos. &iquest;Cuántos caramelos hay en total?",
        icon_groups(6,4,"caramelo"), nlines=1))

# ---- SEMANA 4 ----
# Dia 22 - NUEVO truco conmutativa 7,8,9
add_day(22, "NUEVO: el truco para el 7, 8 y 9", new=True, body=
    explain("&iexcl;Dar la vuelta no cambia el resultado!",
        '<p>7 &times; 2 es lo mismo que 2 &times; 7. Se llama <b>dar la vuelta</b>. '
        'Así, muchas multiplicaciones del 7, 8 y 9 <b>ya te las sabes</b> de otras tablas.</p>'
        '<div class="twocol"><div>' + svg_array(2,7) + '<div class="capt">2 &times; 7 = 14</div></div>'
        '<div>' + svg_array(7,2) + '<div class="capt">7 &times; 2 = 14 (&iexcl;igual!)</div></div></div>')
    + section("Escribe cada una &laquo;dándole la vuelta&raquo; y resuelve",
        mult_items([(7,2),(8,3),(9,2),(7,5),(8,5),(9,4),(7,3),(8,2)])))

# Dia 23
add_day(23, "Practico el 7 y restas", body=
    section("La tabla del 7 (usa el truco si lo necesitas)",
        '<div class="tworef">' + table_reference(7) + '<div class="prac">'
        + mult_items([(7,2),(7,3),(7,5),(7,4),(7,6),(7,7)]) + '</div></div>')
    + section("Restas", sub_grid(uniq_subs(2, lo_a=300, hi_a=999, lo_b=120, hi_b=799, borrows="any"))))

# Dia 24 - NUEVO problemas de dos pasos
add_day(24, "NUEVO: problemas de dos pasos", new=True, body=
    explain("Primero una cosa, y después la otra",
        '<p>Algunos problemas tienen <b>dos pasos</b>. Resuelve primero una operación '
        'y usa ese resultado para la segunda.</p>'
        '<div class="ex2"><b>Ejemplo:</b> Tengo 20&euro;. Compro 3 helados de 2&euro;. '
        '<br>Paso 1: 3 &times; 2 = <b>6&euro;</b>. &nbsp; Paso 2: 20 &minus; 6 = <b>14&euro;</b> me quedan.</div>')
    + word_problem(1, "Laura tiene <b>50</b> euros. Compra <b>4</b> libros de <b>10</b> euros cada uno. &iquest;Cuánto dinero le queda?",
        icon_groups(4,1,"moneda") + '<div class="hint2">Paso 1: 4 &times; 10 = ____ &nbsp;&middot;&nbsp; Paso 2: 50 &minus; ____ = ____</div>', nlines=2))

# Dia 25
add_day(25, "Reto: la tabla loca", body=
    section("Multiplicaciones mezcladas", mult_items([(3,8),(6,5),(4,7),(10,7),(5,6),(2,9),(6,8),(4,9),(7,3),(5,7),(3,9),(6,6)])))

# Dia 26
add_day(26, "Reto de restas", body=
    section("Restas mezcladas (2 y 3 cifras)",
        sub_grid(uniq_subs(3, lo_a=30, hi_a=99, lo_b=10, hi_b=89, borrows="any"))
        )
    + section("Más restas de 3 cifras", sub_grid(uniq_subs(3, lo_a=300, hi_a=999, lo_b=140, hi_b=899, borrows="any"))))

# Dia 27 - problemas graficos variados
add_day(27, "Problemas con dibujos", body=
    word_problem(1, "En la pecera había <b>15</b> peces. Se llevaron <b>6</b> a otra pecera. &iquest;Cuántos peces quedan?",
        icons_row(15,"pez",cross=6), nlines=1)
    + word_problem(2, "Hay <b>3</b> cajas con <b>6</b> galletas cada una. &iquest;Cuántas galletas hay?",
        icon_groups(3,6,"galleta"), nlines=1))

# Dia 28 - NUEVO por 1 y por 0
add_day(28, "NUEVO: multiplicar por 1 y por 0", new=True, body=
    explain("Dos reglas mágicas y muy fáciles",
        '<div class="rules">'
        '<div class="rule"><span class="rn">&times;1</span> Cualquier número <b>por 1</b> se queda igual. 7 &times; 1 = 7.</div>'
        '<div class="rule"><span class="rn">&times;0</span> Cualquier número <b>por 0</b> es 0. 7 &times; 0 = 0.</div>'
        '</div>')
    + section("Completa", mult_items([(8,1),(6,0),(4,1),(9,0),(1,7),(0,5),(10,1),(3,0)]))
    + section("Encuentra el número que falta", mult_missing([(5,4,20),(3,3,9),(4,5,20),(2,6,12)])))

# Dia 29 - gran repaso final
add_day(29, "Gran repaso final", tag="repaso &middot; unos 15 min", body=
    section("Restas", sub_grid(uniq_subs(4, lo_a=200, hi_a=999, lo_b=120, hi_b=899, borrows="any")))
    + section("Todas las tablas", mult_items([(4,8),(7,3),(6,6),(5,9),(3,7),(8,2),(10,6),(9,2)]))
    + word_problem(1, "Un cine tiene <b>200</b> asientos. Están ocupados <b>146</b>. &iquest;Cuántos asientos quedan libres?",
        '<div class="bignum">200 &minus; 146</div>', nlines=1))

# Dia 30 - diploma
add_day(30, "&iexcl;Lo has conseguido!", tag="&iexcl;último día!", body=
    section("Reto final: elige y resuelve",
        sub_grid(uniq_subs(2, lo_a=300, hi_a=999, lo_b=140, hi_b=899, borrows="any"))
        + mult_items([(6,7),(8,4),(5,8),(7,6)]))
    + '<div class="diploma"><div class="dip-h">DIPLOMA DE VERANO</div>'
      '<div class="dip-b">Este diploma es para</div>'
      '<div class="dip-name">' + NAME + '</div>'
      '<div class="dip-b">por haber repasado las mates de todo el verano.<br>&iexcl;Enhorabuena, campeona!</div>'
      '<div class="dip-medal"><svg viewBox="0 0 40 40" class="ic big">' + _icon("estrella") + '</svg></div>'
      '<div class="dip-sign">Firma: __________________</div></div>')

# ============================================================================
# CSS
# ============================================================================
CSS = """
@page { size: A4; margin: 11mm 12mm 9mm 12mm; }
* { box-sizing: border-box; }
body { font-family: 'Comic Neue', 'Comic Sans MS', sans-serif; color:#111; margin:0; }
.page { page-break-after: always; position: relative; }
.page:last-child { page-break-after: auto; }

/* Header */
.head { display:flex; align-items:stretch; gap:10px; margin-bottom:8px; }
.daybadge { border:3px solid #111; border-radius:16px; padding:6px 14px; text-align:center;
  min-width:96px; display:flex; flex-direction:column; justify-content:center; }
.daybadge .dl { font-size:11px; letter-spacing:2px; font-weight:700; text-transform:uppercase; }
.daybadge .dn { font-size:34px; font-weight:700; line-height:1; }
.headmid { flex:1; border:3px solid #111; border-radius:16px; padding:6px 14px; display:flex;
  flex-direction:column; justify-content:center; }
.theme { font-size:19px; font-weight:700; line-height:1.1; }
.tag { font-size:12px; margin-top:3px; }
.tag .clock { font-weight:700; }
.stars { display:flex; flex-direction:column; align-items:center; justify-content:center;
  border:3px solid #111; border-radius:16px; padding:4px 8px; }
.stars .slabel { font-size:8.5px; text-align:center; margin-bottom:2px; line-height:1; }
.stars .srow { display:flex; gap:2px; }
.star { width:17px; height:17px; }
.newflag { display:inline-block; border:2px solid #111; border-radius:8px; font-size:11px;
  padding:1px 7px; font-weight:700; margin-left:6px; vertical-align:middle; }

.namebar { display:flex; gap:18px; font-size:12.5px; margin:0 0 8px 2px; }
.namebar b { font-weight:700; }
.namebar .fill { border-bottom:1.6px solid #111; display:inline-block; min-width:120px; }

/* Explain box */
.explain { border:2.5px dashed #111; border-radius:14px; padding:9px 12px; margin-bottom:9px;
  background:#fafafa; }
.explain-h { font-size:15px; font-weight:700; margin-bottom:4px; }
.explain-h .bulb { margin-right:4px; }
.explain-body p { margin:3px 0; font-size:13px; line-height:1.35; }
.steps { margin:5px 0; }
.step { font-size:12.5px; margin:3px 0; display:flex; align-items:flex-start; gap:6px; }
.stepn { border:2px solid #111; border-radius:50%; width:19px; height:19px; min-width:19px;
  display:inline-flex; align-items:center; justify-content:center; font-weight:700; font-size:12px; }
.worked { display:flex; gap:16px; align-items:center; flex-wrap:wrap; margin-top:4px; }
.wex { text-align:center; }
.wexlab { font-size:11.5px; margin-top:2px; }
.b10note { font-size:11.5px; text-align:center; }
.twocol { display:flex; gap:20px; justify-content:space-around; align-items:flex-end; flex-wrap:wrap; }
.capt { font-size:11.5px; text-align:center; margin-top:2px; }
.ex2 { font-size:13px; background:#fff; border-radius:8px; padding:2px 0; line-height:1.4; }
.rules { display:flex; gap:14px; flex-wrap:wrap; }
.rule { flex:1; min-width:200px; font-size:13px; display:flex; align-items:center; gap:8px; }
.rn { border:2px solid #111; border-radius:8px; padding:3px 8px; font-weight:700; font-size:15px; min-width:40px; text-align:center; }

/* Sections */
.sec { margin-bottom:9px; }
.sec-h { font-size:14.5px; font-weight:700; border-bottom:2px solid #111; padding-bottom:2px; margin-bottom:7px; }

/* Restas */
.subgrid { display:flex; flex-wrap:wrap; gap:10px 20px; }
.sub { display:inline-block; padding:4px 6px 6px; }
.brow, .nrow, .arow { display:flex; justify-content:flex-end; }
.dc { width:26px; height:30px; font-size:25px; font-weight:700; text-align:center; line-height:30px; }
.op { width:22px; font-size:22px; font-weight:700; line-height:30px; text-align:center; }
.brow { height:16px; }
.bcell { width:26px; height:14px; }
.bar { border-top:3px solid #111; margin-top:1px; }
.ansc { border:1.6px dashed #999; border-radius:4px; height:30px; }
.arow { margin-top:4px; }
/* answer row width should match minuend incl op width -> add left pad */
.nrow .op + .dc, .arow { }

/* Multiplicaciones */
.mgrid { display:flex; flex-wrap:wrap; gap:9px 16px; }
.mitem { display:flex; align-items:center; gap:6px; font-size:19px; font-weight:700; }
.mx { white-space:nowrap; }
.mbox { border:1.8px dashed #999; border-radius:5px; width:40px; height:30px; display:inline-block; }
.mbox.small { width:34px; }

/* Tabla referencia */
.tworef { display:flex; gap:16px; align-items:flex-start; flex-wrap:wrap; }
.tablecard { border:2px solid #111; border-radius:12px; overflow:hidden; min-width:150px; }
.tablecard-h { background:#111; color:#fff; font-size:13px; font-weight:700; text-align:center; padding:3px 6px; }
.tablebody { padding:5px 10px; }
.trow { display:flex; align-items:center; gap:6px; font-size:15px; font-weight:700; padding:1px 0; }
.trow .tl { min-width:52px; }
.trow .tr { min-width:26px; text-align:right; }
.trow .tr.blank { border-bottom:1.6px solid #999; min-width:34px; }
.prac { flex:1; min-width:240px; }

/* number line / arrays */
.artsvg { height:auto; }
.artsvg .nl { font-size:15px; font-family:'Comic Neue'; font-weight:700; text-anchor:middle; }
.artsvg .nlj { font-size:12px; font-family:'Comic Neue'; text-anchor:middle; }

/* Problemas */
.wp { border:2px solid #111; border-radius:14px; padding:9px 12px; margin-bottom:9px; }
.wp-h { font-size:13px; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:3px; }
.wp-text { font-size:14px; line-height:1.4; margin-bottom:6px; }
.wp-illus { margin:4px 0 8px; }
.iconrow { display:flex; flex-wrap:wrap; gap:5px; }
.ic { width:38px; height:38px; }
.ic.sm { width:30px; height:30px; }
.ic.big { width:60px; height:60px; }
.grouprow { display:flex; flex-wrap:wrap; gap:12px; }
.grpbox { border:2px solid #111; border-radius:10px; padding:6px; display:flex; flex-wrap:wrap;
  gap:4px; max-width:170px; }
.probans { margin-top:2px; }
.opbox { font-size:12px; font-weight:700; margin-bottom:3px; }
.ansline { border-bottom:1.6px solid #111; height:22px; margin:6px 0; }
.sollabel { font-size:13px; font-weight:700; margin-top:4px; }
.solbox { display:inline-block; border:1.8px solid #111; border-radius:6px; min-width:90px; height:26px;
  vertical-align:middle; margin-left:4px; }
.bignum { font-size:26px; font-weight:700; text-align:center; letter-spacing:2px; margin:4px 0; }
.hint2 { font-size:12.5px; margin-top:6px; font-weight:700; }

/* Diploma */
.diploma { border:4px double #111; border-radius:16px; padding:14px; text-align:center; margin-top:10px; }
.dip-h { font-size:22px; font-weight:700; letter-spacing:3px; }
.dip-b { font-size:13px; margin:5px 0; }
.dip-name { font-size:30px; font-weight:700; border-bottom:2px solid #111; display:inline-block;
  padding:0 30px 3px; margin:6px 0; }
.dip-medal { margin:6px 0; }
.dip-sign { font-size:13px; margin-top:8px; }

.footer { position:absolute; bottom:-4mm; left:0; right:0; text-align:center; font-size:10.5px; color:#333; }
"""

# ============================================================================
# Render
# ============================================================================
def star_svg():
    return f'<svg viewBox="0 0 40 40" class="star">{_icon("estrella")}</svg>'

def render_page(d):
    newflag = '<span class="newflag">&#9733; NUEVO</span>' if d["new"] else ""
    stars = '<div class="srow">' + star_svg()*3 + '</div>'
    footer = f'&iexcl;Muy bien, {NAME}! &middot; Cuaderno de verano &middot; Día {d["n"]} de 30'
    head = f'''<div class="head">
      <div class="daybadge"><span class="dl">Día</span><span class="dn">{d["n"]}</span></div>
      <div class="headmid"><div class="theme">{d["theme"]}{newflag}</div>
        <div class="tag"><span class="clock">&#9201; {d["tag"]}</span></div></div>
      <div class="stars"><div class="slabel">Colorea al<br>terminar</div>{stars}</div>
    </div>'''
    namebar = f'''<div class="namebar"><span><b>Nombre:</b> {NAME}</span>
      <span><b>Fecha:</b> <span class="fill"></span></span></div>'''
    return f'<section class="page">{head}{namebar}{d["body"]}<div class="footer">{footer}</div></section>'

def cover():
    stars = "".join(f'<svg viewBox="0 0 40 40" style="width:34px;height:34px">{_icon("estrella")}</svg>' for _ in range(5))
    icons = "".join(f'<svg viewBox="0 0 40 40" style="width:44px;height:44px;margin:6px">{_icon(k)}</svg>'
                    for k in ["manzana","globo","flor","estrella","pez","moneda","caramelo","galleta"])
    return f'''<section class="page">
      <div style="border:4px double #111;border-radius:24px;padding:26px;text-align:center;margin-top:26px;">
        <div style="font-size:15px;letter-spacing:5px;font-weight:700;">CUADERNO DE VERANO</div>
        <div style="font-size:46px;font-weight:700;margin:14px 0 4px;">Las mates de {NAME}</div>
        <div style="font-size:17px;margin-bottom:14px;">30 días de repaso &middot; una hoja al día</div>
        <div style="margin:12px 0;">{stars}</div>
        <div style="font-size:14px;max-width:430px;margin:12px auto;line-height:1.5;">
          Cada día tiene una hojita para hacer en <b>unos 15 minutos</b>. Cuando algo es
          <b>nuevo</b>, hay una explicación con dibujos. &iexcl;Colorea las estrellas al terminar cada día!
        </div>
        <div style="display:flex;justify-content:center;flex-wrap:wrap;max-width:460px;margin:10px auto;">{icons}</div>
        <div style="margin-top:18px;font-size:15px;">
          <b>Restas con llevadas</b> &middot; <b>Tablas de multiplicar</b> &middot; <b>Problemas</b>
        </div>
      </div>
      <div style="text-align:center;margin-top:18px;font-size:13px;">
        Guía para las familias: acompaña a {NAME}, deja que se equivoque y lo intente de nuevo.
        Un ratito corto cada día vale más que mucho de golpe. &iexcl;Ánimo!
      </div>
    </section>'''

def parents_guide():
    return f'''<section class="page">
      <div class="sec-h" style="font-size:20px;">Guía rápida para las familias</div>
      <div style="font-size:13.5px;line-height:1.55;">
      <p><b>&iquest;Cómo funciona?</b> Hay 30 hojas, una por día. Cada hoja se hace en unos 15 minutos.
      El cuaderno es <b>progresivo</b>: primero repasa lo conocido y va añadiendo cosas nuevas poco a poco.</p>
      <p><b>Días con &#9733; NUEVO:</b> incluyen una explicación con dibujos. Léela con {NAME} antes de empezar
      los ejercicios y resuelve juntos el ejemplo.</p>
      <p><b>Qué trabaja este cuaderno:</b></p>
      <div style="margin-left:6px;">
        &bull; <b>Restas con llevadas</b>: de 2 cifras &rarr; 3 cifras &rarr; con dos llevadas &rarr; con ceros.<br>
        &bull; <b>Multiplicación</b>: se repasan las tablas del 2 y del 3, y se inician las del 4, 5, 6, 7, 10,
        además de multiplicar por 0 y por 1.<br>
        &bull; <b>Problemas</b>: siempre con dibujos, para entender qué operación hay que hacer.
      </div>
      <p><b>Consejos:</b> deja que use los dedos, dibuje o cuente si lo necesita; celebra el esfuerzo, no solo el
      acierto; si un día se atasca, para y retómalo otro rato. La marca de la &laquo;llevada&raquo; se apunta en el
      hueco pequeño de arriba de cada resta.</p>
      <p style="margin-top:14px;font-size:12px;color:#444;">Este cuaderno no incluye soluciones para que podáis
      corregir juntos y comentar cada ejercicio.</p>
      </div>
    </section>'''

html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><style>{CSS}</style></head>
<body>{cover()}{parents_guide()}{"".join(render_page(d) for d in DAYS)}</body></html>"""

with open("cuaderno.html", "w", encoding="utf-8") as f:
    f.write(html)
print("HTML generado:", len(html), "bytes,", len(DAYS), "dias")
