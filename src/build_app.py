# -*- coding: utf-8 -*-
"""Genera una app HTML interactiva y offline: las mates de Laura para iPad.

Uso:
    python src/build_app.py            # genera public/index.html (nombre: Laura)
    KID_NAME=Marta python src/build_app.py   # personaliza el nombre

No tiene dependencias externas: solo Python 3. Lee src/cat.js y escribe
public/index.html (un único archivo autocontenido que funciona sin conexión).
"""
import os, json, random
random.seed(2026)
NAME = os.environ.get("KID_NAME", "Laura")

# ---------- generadores de restas (con control de llevadas) ----------
def digs(n, w): return [int(d) for d in str(n).rjust(w, "0")]
def count_borrows(a, b):
    w = max(len(str(a)), len(str(b))); da, db = digs(a, w), digs(b, w); bo = 0; c = 0
    for i in range(w-1, -1, -1):
        cur = da[i]-bo
        if cur < db[i]: c += 1; bo = 1
        else: bo = 0
    return c
def gen_sub(lo_a, hi_a, lo_b, hi_b, borrows=None, min_result=1):
    a = b = 0
    for _ in range(20000):
        a = random.randint(lo_a, hi_a); b = random.randint(lo_b, min(hi_b, a))
        if a-b < min_result: continue
        c = count_borrows(a, b)
        if borrows == 0 and c != 0: continue
        if borrows == 1 and c != 1: continue
        if borrows == 2 and c < 2: continue
        if borrows == "any" and c == 0: continue
        return a, b
    return a, b
def uniq_subs(n, **kw):
    seen, out, t = set(), [], 0
    while len(out) < n and t < 10000:
        t += 1; p = gen_sub(**kw)
        if p not in seen: seen.add(p); out.append(p)
    return out

# ---------- constructores de preguntas ----------
def sub(a, b): return {"t": "sub", "a": a, "b": b}
def subs(n, **kw): return [sub(a, b) for a, b in uniq_subs(n, **kw)]
def mul(x, y): return {"t": "mul", "x": x, "y": y}
def muls(pairs): return [mul(x, y) for x, y in pairs]
def miss(a, b, r): return {"t": "miss", "a": a, "r": r}   # a x ? = r  (resp b)
def prob(text, illus, ans): return {"t": "prob", "text": text, "illus": illus, "ans": ans}
def steps(text, illus, parts): return {"t": "steps", "text": text, "illus": illus, "parts": parts}

def row(e, n, cross=0): return {"mode": "row", "e": e, "n": n, "cross": cross}
def groups(e, g, per): return {"mode": "groups", "e": e, "g": g, "per": per}
def bignum(txt): return {"mode": "bignum", "text": txt}

# emojis
AP="🍎"; GL="🎈"; FL="🌸"; CO="🪙"; CA="🍬"; CK="🍪"; FI="🐟"

# ---------- intros (HTML listo) ----------
def wex(a, b):
    """ejemplo resuelto de resta, en vertical, con la respuesta en verde"""
    w = max(len(str(a)), len(str(b))); r = a-b
    def cells(s):
        s = str(s).rjust(w)
        return "".join(f'<span class="wc">{"" if ch==" " else ch}</span>' for ch in s)
    def cellsg(s):
        s = str(s).rjust(w)
        return "".join(f'<span class="wc g">{"" if ch==" " else ch}</span>' for ch in s)
    return (f'<div class="wex"><div class="wr">{cells(a)}</div>'
            f'<div class="wr"><span class="wop">−</span>{cells(b)}</div>'
            f'<div class="wbar"></div><div class="wr">{cellsg(r)}</div></div>')

def emrow(e, n): return '<div class="emrow">' + e*n + '</div>'
def arr(rows, cols, e="⚫"):
    out = ""
    for _ in range(rows): out += '<div>' + ("🔵"*cols) + '</div>'
    return f'<div class="arr">{out}</div>'

INTRO = {}
INTRO[1] = ("Recuerda: coloca bien las cifras",
    "<p>En una resta ponemos las <b>unidades debajo de las unidades</b> y las <b>decenas debajo de las decenas</b>. Empezamos por la derecha.</p>"
    + wex(48,25) + "<p class='hint'>8 − 5 = 3 &nbsp;·&nbsp; 4 − 2 = 2</p>")
INTRO[2] = ("¡Cuando no puedo restar, pido prestado!",
    "<p>Si el número de arriba es <b>más pequeño</b>, la decena de al lado le <b>presta 10</b>.</p>"
    "<p>👉 2 − 7 no puedo. Pido prestado: ahora tengo <b>12</b>. 12 − 7 = <b>5</b>.<br>"
    "👉 Como presté una decena, arriba quedan <b>4</b>. 4 − 2 = <b>2</b>.</p>" + wex(52,27))
INTRO[4] = ("Multiplicar es sumar grupos iguales",
    "<p><b>3 × 4</b> son <b>3 grupos de 4</b>. Es lo mismo que 4 + 4 + 4 = <b>12</b>.</p>"
    "<div class='grp3'><div class='gb'>🍎🍎🍎🍎</div><div class='gb'>🍎🍎🍎🍎</div><div class='gb'>🍎🍎🍎🍎</div></div>"
    "<p class='hint'>3 grupos de 4 manzanas = 12 🍎</p>")
INTRO[5] = ("La tabla del 3: cuenta de 3 en 3",
    "<p>3, 6, 9, 12, 15... ¡vas sumando 3 cada vez!</p><div class='nline'>3 → 6 → 9 → 12 → 15 → 18</div>")
INTRO[7] = ("Ahora con centenas, decenas y unidades",
    "<p>Igual que antes, pero con <b>una columna más</b>: las <b>centenas</b>. Colocamos C con C, D con D, U con U.</p>" + wex(376,152))
INTRO[8] = ("Pedimos prestado también con 3 cifras",
    "<p>Empieza por las <b>unidades</b>. Si no puedes restar, pide prestado y sigue con decenas y centenas.</p>" + wex(435,128))
INTRO[10] = ("La tabla del 4: cuenta de 4 en 4",
    "<p>4 × 3 son <b>3 grupos de 4</b>. La tabla del 4 es el <b>doble</b> de la del 2.</p><div class='nline'>4 → 8 → 12 → 16 → 20</div>")
INTRO[12] = ("La tabla del 5 termina en 0 o en 5",
    "<p>Cuenta de 5 en 5, ¡como los dedos de las manos! ✋🖐️</p><div class='nline'>5 → 10 → 15 → 20 → 25 → 30</div>")
INTRO[14] = ("A veces hay que pedir prestado dos veces",
    "<p>No pasa nada si pides prestado en <b>dos columnas</b>. Ve con calma, de derecha a izquierda.</p>" + wex(624,158))
INTRO[16] = ("La tabla del 10: ¡la más fácil!",
    "<p>Para multiplicar por 10, solo <b>añade un cero</b>. 10 × 4 = <b>40</b>.</p><div class='nline'>10 → 20 → 30 → 40 → 50</div>")
INTRO[18] = ("¿Y si arriba hay un 0?",
    "<p>Cuando arriba hay un <b>0</b> y tienes que restar, ese 0 también pide prestado a su izquierda.</p>" + wex(300,148))
INTRO[19] = ("La tabla del 6: cuenta de 6 en 6",
    "<p>Es el <b>doble</b> de la tabla del 3.</p><div class='nline'>6 → 12 → 18 → 24 → 30</div>")
INTRO[22] = ("El truco: ¡dar la vuelta!",
    "<p>7 × 2 es lo mismo que 2 × 7. Si le <b>das la vuelta</b>, muchas ya te las sabes.</p>"
    "<div class='grp3'><div class='gb'>🔵🔵🔵🔵🔵🔵🔵</div><div class='gb'>🔵🔵🔵🔵🔵🔵🔵</div></div><p class='hint'>2 × 7 = 14 &nbsp; y &nbsp; 7 × 2 = 14</p>")
INTRO[24] = ("Problemas de dos pasos",
    "<p>Algunos problemas tienen <b>dos pasos</b>. Haz primero una operación y usa el resultado para la segunda.</p>"
    "<p class='hint'>Ej: Tengo 20€, compro 3 helados de 2€. → 3 × 2 = 6€ · 20 − 6 = <b>14€</b></p>")
INTRO[28] = ("Dos reglas mágicas",
    "<p>✨ Cualquier número <b>× 1</b> se queda igual: 7 × 1 = 7.<br>✨ Cualquier número <b>× 0</b> es 0: 7 × 0 = 0.</p>")

# ---------- construir los 30 días ----------
DAYS = []
def day(n, theme, qs, new=False, repaso=False, diploma=False):
    intro = None
    if n in INTRO:
        intro = {"title": INTRO[n][0], "html": INTRO[n][1]}
    DAYS.append({"n": n, "theme": theme, "new": new or (n in INTRO), "repaso": repaso,
                 "diploma": diploma, "intro": intro, "qs": qs})

day(1, "Empezamos: restas sin llevada", subs(6, lo_a=20, hi_a=99, lo_b=10, hi_b=99, borrows=0), new=True)
day(2, "Restas con llevada", subs(6, lo_a=20, hi_a=99, lo_b=10, hi_b=89, borrows=1), new=True)
day(3, "Practico restas con llevada",
    subs(5, lo_a=30, hi_a=99, lo_b=10, hi_b=89, borrows=1) + [prob("Había 12 globos y se escaparon 5. ¿Cuántos quedan?", row(GL,12,5), 7)])
day(4, "Multiplicar es sumar grupos", muls([(2,3),(2,5),(2,8),(2,6),(2,9),(2,4)]), new=True)
day(5, "La tabla del 3", muls([(3,2),(3,4),(3,7),(3,5),(3,9),(3,6),(3,8),(3,3)]), new=True)
day(6, "Mezcla: restas y tablas",
    subs(4, lo_a=30, hi_a=99, lo_b=10, hi_b=89, borrows=1) + muls([(2,7),(3,6),(2,9),(3,8)])
    + [prob("Ana tiene 3 cajas y en cada caja hay 2 manzanas. ¿Cuántas manzanas tiene?", groups(AP,3,2), 6)])
day(7, "Restas de 3 cifras", subs(6, lo_a=200, hi_a=999, lo_b=100, hi_b=999, borrows=0), new=True)
day(8, "3 cifras con una llevada", subs(6, lo_a=200, hi_a=999, lo_b=110, hi_b=899, borrows=1), new=True)
day(9, "Practico restas de 3 cifras",
    subs(5, lo_a=200, hi_a=999, lo_b=110, hi_b=899, borrows="any") + [prob("El álbum tiene 250 cromos y Laura ya pegó 134. ¿Cuántos le faltan?", bignum("250 − 134"), 116)])
day(10, "La tabla del 4", muls([(4,2),(4,5),(4,3),(4,7),(4,4),(4,6),(4,8),(4,9)]), new=True)
day(11, "Tabla del 4 y restas",
    muls([(4,6),(4,3),(4,8),(4,5),(4,9),(4,7)]) + subs(3, lo_a=300, hi_a=999, lo_b=110, hi_b=799, borrows="any"))
day(12, "La tabla del 5", muls([(5,3),(5,6),(5,2),(5,8),(5,4),(5,7),(5,9),(5,5)]), new=True)
day(13, "Tablas del 4 y del 5",
    muls([(4,7),(5,6),(4,4),(5,9),(5,3),(4,8),(5,7),(4,6)]) + [prob("Hay 5 macetas y en cada una crecen 3 flores. ¿Cuántas flores hay?", groups(FL,5,3), 15)])
day(14, "Restas con dos llevadas", subs(6, lo_a=300, hi_a=999, lo_b=140, hi_b=899, borrows=2), new=True)
day(15, "¡Mitad del camino! Gran repaso",
    subs(4, lo_a=200, hi_a=999, lo_b=110, hi_b=899, borrows="any") + muls([(3,7),(5,8),(4,6),(2,9)])
    + [prob("Había 18 globos y se explotaron 7. ¿Cuántos quedan?", row(GL,18,7), 11)], repaso=True)
day(16, "La tabla del 10", muls([(10,3),(10,7),(10,5),(10,9),(10,2),(10,6),(10,8),(10,4)]), new=True)
day(17, "Tablas del 5 y del 10",
    muls([(5,7),(10,6),(5,9),(10,3),(5,4),(10,8)]) + [prob("Cada bolsa de cromos cuesta 5€. Laura compra 4 bolsas. ¿Cuánto gasta?", groups(CO,4,5), 20)])
day(18, "Restas con ceros", [sub(a,b) for a,b in [(300,148),(500,236),(400,127),(600,354),(200,86),(700,268)]], new=True)
day(19, "La tabla del 6", muls([(6,2),(6,4),(6,3),(6,6),(6,5),(6,7),(6,8),(6,9)]), new=True)
day(20, "Tablas 4, 5 y 6 + restas",
    muls([(4,8),(6,7),(5,9),(6,4),(4,6),(6,9)]) + subs(3, lo_a=300, hi_a=999, lo_b=140, hi_b=899, borrows="any"))
day(21, "Día de problemas",
    [prob("Un tren llevaba 420 pasajeros y se bajaron 135. ¿Cuántos siguen en el tren?", bignum("420 − 135"), 285),
     prob("Hay 6 platos y en cada uno hay 4 caramelos. ¿Cuántos caramelos hay?", groups(CA,6,4), 24)])
day(22, "El truco del 7, 8 y 9", muls([(7,2),(8,3),(9,2),(7,5),(8,5),(9,4),(7,3),(8,2)]), new=True)
day(23, "Practico el 7 y restas",
    muls([(7,2),(7,3),(7,5),(7,4),(7,6),(7,7)]) + subs(2, lo_a=300, hi_a=999, lo_b=120, hi_b=799, borrows="any"))
day(24, "Problemas de dos pasos",
    [steps("Laura tiene 50€. Compra 4 libros de 10€ cada uno. ¿Cuánto dinero le queda?", groups(CO,4,1),
           [{"label":"Paso 1: 4 × 10 =", "ans":40},{"label":"Paso 2: 50 − 40 =", "ans":10}])], new=True)
day(25, "Reto: la tabla loca", muls([(3,8),(6,5),(4,7),(10,7),(5,6),(2,9),(6,8),(4,9),(7,3),(5,7),(3,9),(6,6)]))
day(26, "Reto de restas",
    subs(3, lo_a=30, hi_a=99, lo_b=10, hi_b=89, borrows="any") + subs(3, lo_a=300, hi_a=999, lo_b=140, hi_b=899, borrows="any"))
day(27, "Problemas con dibujos",
    [prob("En la pecera había 15 peces y se llevaron 6. ¿Cuántos quedan?", row(FI,15,6), 9),
     prob("Hay 3 cajas con 6 galletas cada una. ¿Cuántas galletas hay?", groups(CK,3,6), 18)])
day(28, "Multiplicar por 1 y por 0",
    muls([(8,1),(6,0),(4,1),(9,0),(1,7),(0,5),(10,1),(3,0)]) + [miss(5,4,20),miss(3,3,9),miss(4,5,20),miss(2,6,12)], new=True)
day(29, "Gran repaso final",
    subs(4, lo_a=200, hi_a=999, lo_b=120, hi_b=899, borrows="any") + muls([(4,8),(7,3),(6,6),(5,9),(3,7),(8,2)])
    + [prob("Un cine tiene 200 asientos y 146 están ocupados. ¿Cuántos quedan libres?", bignum("200 − 146"), 54)], repaso=True)
day(30, "¡Lo has conseguido!",
    subs(2, lo_a=300, hi_a=999, lo_b=140, hi_b=899, borrows="any") + muls([(6,7),(8,4),(5,8),(7,6)]), diploma=True)

DATA = {"name": NAME, "days": DAYS}
data_json = json.dumps(DATA, ensure_ascii=False)

# ============================ HTML / CSS / JS ============================
HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<title>Las mates de __NAME__</title>
<style>
:root{
  --bg1:#7b5cff; --bg2:#4dc9e6; --card:#ffffff; --ink:#2a2350; --muted:#8a86a8;
  --ok:#20c079; --okd:#128a53; --no:#ff6b6b; --sun:#ffcc33; --pink:#ff7ac0;
  --shadow:0 10px 30px rgba(40,20,90,.18);
}
*{box-sizing:border-box; -webkit-tap-highlight-color:transparent;}
html,body{margin:0; height:100%;}
body{
  font-family:-apple-system,"SF Pro Rounded","Segoe UI Rounded","Comic Sans MS",system-ui,sans-serif;
  color:var(--ink);
  background:linear-gradient(160deg,var(--bg1),var(--bg2));
  background-attachment:fixed;
  -webkit-user-select:none; user-select:none; overflow-x:hidden;
}
.app{max-width:820px; margin:0 auto; padding:16px 14px 20px; min-height:100%;}
.hidden{display:none !important;}
button{font-family:inherit; cursor:pointer; border:none;}

/* ---------- HOME ---------- */
.home-hd{text-align:center; color:#fff; margin:6px 0 12px;}
.home-hd .sub{font-size:15px; opacity:.9; letter-spacing:2px; text-transform:uppercase;}
.home-hd h1{font-size:34px; margin:4px 0 2px; text-shadow:0 3px 0 rgba(0,0,0,.12);}
.stats{display:flex; gap:10px; justify-content:center; margin:10px 0 16px; flex-wrap:wrap;}
.stat{background:rgba(255,255,255,.9); border-radius:16px; padding:8px 16px; box-shadow:var(--shadow); text-align:center; min-width:110px;}
.stat b{display:block; font-size:26px; line-height:1;}
.stat span{font-size:12px; color:var(--muted);}
.grid{display:grid; grid-template-columns:repeat(5,1fr); gap:10px;}
@media (max-width:520px){.grid{grid-template-columns:repeat(4,1fr);}}
.daycard{background:var(--card); border-radius:18px; padding:10px 6px 8px; box-shadow:var(--shadow);
  text-align:center; position:relative; transition:transform .1s; border:3px solid transparent;}
.daycard:active{transform:scale(.95);}
.daycard .dn{font-size:22px; font-weight:800;}
.daycard .dl{font-size:9.5px; color:var(--muted); line-height:1.05; height:23px; overflow:hidden; margin-top:2px;}
.daycard .st{font-size:12px; margin-top:3px; height:16px; letter-spacing:-1px;}
.daycard.done{background:linear-gradient(160deg,#fff,#e9 fff2);}
.daycard.done{background:#eafff4;}
.daycard.next{border-color:var(--sun); box-shadow:0 0 0 3px rgba(255,204,51,.4),var(--shadow);}
.daycard .newdot{position:absolute; top:-6px; right:-6px; background:var(--pink); color:#fff;
  font-size:9px; font-weight:800; padding:2px 6px; border-radius:10px; box-shadow:0 3px 8px rgba(0,0,0,.2);}
.homefoot{text-align:center; color:#fff; opacity:.85; font-size:12px; margin-top:16px; line-height:1.5;}
.reset{background:rgba(255,255,255,.2); color:#fff; border-radius:12px; padding:6px 14px; font-size:12px; margin-top:10px;}

/* ---------- INTRO CARD ---------- */
.topbar{display:flex; align-items:center; gap:8px; margin-bottom:12px;}
.back{background:rgba(255,255,255,.9); border-radius:14px; padding:8px 14px; font-size:16px; font-weight:700; box-shadow:var(--shadow);}
.topttl{color:#fff; font-weight:800; font-size:17px; flex:1; text-shadow:0 2px 0 rgba(0,0,0,.12);}
.dots{display:flex; gap:5px; flex-wrap:wrap; justify-content:center; margin-bottom:10px;}
.dot{width:12px; height:12px; border-radius:50%; background:rgba(255,255,255,.45);}
.dot.done{background:var(--ok);} .dot.cur{background:#fff; transform:scale(1.35);}

.card{background:var(--card); border-radius:24px; padding:20px 18px; box-shadow:var(--shadow);}
.intro h2{margin:0 0 8px; font-size:22px; color:var(--bg1);}
.intro p{font-size:16px; line-height:1.5; margin:8px 0;}
.intro .hint{background:#fff6da; border-radius:12px; padding:8px 12px; font-size:15px;}
.nline{background:#eef7ff; border-radius:12px; padding:10px; text-align:center; font-size:19px; font-weight:800; color:#2b7fd0; letter-spacing:1px;}
.grp3{display:flex; gap:10px; justify-content:center; flex-wrap:wrap; margin:8px 0;}
.gb{background:#f2eeff; border:2px dashed #b9a9ff; border-radius:14px; padding:8px 10px; font-size:22px; letter-spacing:2px;}
.emrow{font-size:24px; text-align:center; letter-spacing:3px;}
.wex{display:inline-block; margin:6px auto; text-align:right; background:#f7f5ff; padding:10px 14px; border-radius:14px;}
.wex-wrap{text-align:center;}
.wr{display:flex; justify-content:flex-end;}
.wc{width:30px; font-size:30px; font-weight:800; text-align:center;}
.wc.g{color:var(--okd);}
.wop{width:24px; font-size:26px; font-weight:800; text-align:center;}
.wbar{border-top:4px solid var(--ink); margin:2px 0;}
.startbtn{display:block; width:100%; margin-top:16px; background:linear-gradient(160deg,var(--sun),#ff9d2e);
  color:#5a3b00; font-size:20px; font-weight:800; padding:15px; border-radius:18px; box-shadow:var(--shadow);}

/* ---------- QUESTION ---------- */
.qwrap{padding-bottom:8px;}
.qcard{background:var(--card); border-radius:24px; padding:18px 16px; box-shadow:var(--shadow); text-align:center; position:relative;}
.qkind{font-size:12px; text-transform:uppercase; letter-spacing:2px; color:var(--muted); font-weight:800;}
.qtext{font-size:18px; line-height:1.4; margin:8px 4px 12px;}
.illus{margin:6px 0 12px;}
.emgrid{font-size:30px; line-height:1.5; letter-spacing:4px; word-break:break-word;}
.em{display:inline-block; transition:.2s;}
.em.gone{opacity:.28; position:relative;}
.em.gone::after{content:"✖"; position:absolute; left:0; right:0; top:-2px; color:var(--no); font-size:26px;}
.gboxes{display:flex; gap:8px; justify-content:center; flex-wrap:wrap;}
.gbox{background:#f2eeff; border:2px dashed #b9a9ff; border-radius:14px; padding:8px; font-size:24px; letter-spacing:2px; max-width:150px;}
.big{font-size:38px; font-weight:800; letter-spacing:2px; color:var(--bg1);}

/* vertical subtraction */
.vsub{display:inline-block; text-align:right; margin:4px auto;}
.vrow{display:flex; justify-content:flex-end; align-items:center;}
.vc{width:40px; font-size:40px; font-weight:800; text-align:center; line-height:1.1;}
.vop{width:30px; font-size:34px; font-weight:800; text-align:center;}
.vbar{border-top:5px solid var(--ink); margin:3px 0;}
/* casillas por columna (U/D/C) en las restas */
.arow2{margin-top:6px;}
.labrow{margin-top:2px;}
.acell{width:40px; display:inline-flex; flex-direction:column; align-items:center;}
.dbox{width:34px; height:46px; border:3px solid #d7d2ee; border-radius:10px; background:#fbfaff;
  font-size:30px; font-weight:800; display:flex; align-items:center; justify-content:center; color:var(--ink);}
.dbox.active{border-color:var(--bg1); box-shadow:0 0 0 4px rgba(123,92,255,.15);}
.dbox.ok{border-color:var(--ok); background:#e9fff4; color:var(--okd);}
.dbox.bad{border-color:var(--no); background:#fff0f0; animation:shake .35s;}
.dlab{font-size:11px; font-weight:800; color:var(--muted); margin-top:3px;}
.dbox.lockcol{background:#eceaf4; border-color:#e2e0ee;}
.lk{font-size:15px; opacity:.4;}
.qhint{background:#fff6da; border:2px solid #ffd97a; border-radius:14px; padding:10px 12px; font-size:15px;
  font-weight:700; color:#8a5a00; margin-top:8px; line-height:1.4; text-align:left;}
.hintbtn{position:absolute; top:10px; right:10px; background:linear-gradient(160deg,#ffd54a,#ff9d2e); color:#5a3b00;
  font-weight:800; font-size:13px; border-radius:12px; padding:7px 11px; box-shadow:var(--shadow); z-index:2;}

/* multiplication line */
.mline{font-size:40px; font-weight:800; color:var(--bg1);}

/* answer slots */
.slots{display:flex; gap:12px; justify-content:center; flex-wrap:wrap; margin:8px 0 4px;}
.slotlab{font-size:15px; color:var(--muted); font-weight:700; align-self:center;}
.slot{min-width:96px; height:60px; border:3px solid #d7d2ee; border-radius:16px; background:#fbfaff;
  font-size:34px; font-weight:800; display:flex; align-items:center; justify-content:center; color:var(--ink); padding:0 8px;}
.slot.active{border-color:var(--bg1); box-shadow:0 0 0 4px rgba(123,92,255,.15);}
.slot.ok{border-color:var(--ok); background:#e9fff4; color:var(--okd);}
.slot.bad{border-color:var(--no); background:#fff0f0; animation:shake .35s;}
@keyframes shake{0%,100%{transform:translateX(0)}25%{transform:translateX(-7px)}75%{transform:translateX(7px)}}
.caret{width:3px; height:34px; background:var(--bg1); display:inline-block; animation:blink 1s step-end infinite; margin-left:2px;}
@keyframes blink{50%{opacity:0}}
.fb{min-height:30px; font-size:19px; font-weight:800; margin:8px 0 2px;}
.fb.ok{color:var(--okd);} .fb.no{color:var(--no);}

/* keypad */
.pad{display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-top:14px;}
.key{background:var(--card); border-radius:18px; padding:16px 0; font-size:28px; font-weight:800; box-shadow:var(--shadow); color:var(--ink);}
.key:active{transform:scale(.94);}
.key.wide{grid-column:span 3; background:linear-gradient(160deg,var(--ok),var(--okd)); color:#fff; font-size:22px;}
.key.del{background:#fff0f0; color:var(--no);}

/* ---------- DONE ---------- */
.done-card{background:var(--card); border-radius:26px; padding:26px 20px; box-shadow:var(--shadow); text-align:center;}
.done-card h2{font-size:28px; margin:6px 0; color:var(--bg1);}
.bigstars{font-size:46px; letter-spacing:4px; margin:10px 0;}
.done-msg{font-size:17px; line-height:1.5;}
.score{font-size:16px; color:var(--muted); margin:8px 0;}
.done-btns{display:flex; gap:10px; margin-top:16px; flex-wrap:wrap;}
.done-btns button{flex:1; min-width:130px; padding:14px; border-radius:16px; font-size:16px; font-weight:800; box-shadow:var(--shadow);}
.bnext{background:linear-gradient(160deg,var(--sun),#ff9d2e); color:#5a3b00;}
.bhome{background:#efeaff; color:var(--bg1);}
.diploma{border:5px double var(--sun); border-radius:20px; padding:18px; margin-top:10px; background:#fffdf5;}
.diploma .dh{font-size:22px; font-weight:800; letter-spacing:2px; color:#c78a00;}
.diploma .dnm{font-size:30px; font-weight:800; margin:8px 0; color:var(--bg1);}

/* confetti */
#confetti{position:fixed; inset:0; pointer-events:none; overflow:hidden; z-index:60;}
.cf{position:absolute; font-size:22px; animation:fall linear forwards;}
@keyframes fall{to{transform:translateY(110vh) rotate(360deg); opacity:.9;}}

/* ---------- AVATAR / HERO ---------- */
.cat{width:100%; height:auto; display:block;}
.hero{background:rgba(255,255,255,.94); border-radius:22px; box-shadow:var(--shadow); padding:10px 12px; margin-bottom:14px;
  display:flex; align-items:center; gap:10px;}
.heroCat{width:78px; min-width:78px;}
.hInfo{flex:1;}
.hHi{font-size:18px; font-weight:800; color:var(--ink);}
.hSub{font-size:12px; color:var(--muted); margin:1px 0 3px;}
.wallet{display:inline-flex; align-items:center; gap:4px; background:#fff6da; color:#a06b00; font-weight:800;
  border-radius:12px; padding:5px 11px; font-size:15px;}
.tiendaBtn{background:linear-gradient(160deg,var(--pink),#ff4f9a); color:#fff; font-weight:800; font-size:14px; line-height:1.2;
  border-radius:16px; padding:10px 14px; box-shadow:var(--shadow); text-align:center;}

/* ---------- CREATE ---------- */
.createCard{background:var(--card); border-radius:24px; padding:20px; box-shadow:var(--shadow); text-align:center;}
.createCard h2{color:var(--bg1); margin:2px 0 4px; font-size:25px;}
.createCard p{color:var(--muted); font-size:14px; margin:0 0 6px;}
.bigCat{width:180px; margin:6px auto 2px;}
.pickTtl{font-weight:800; font-size:15px; margin:14px 0 8px; color:var(--ink);}
.swatches{display:flex; gap:12px; justify-content:center; flex-wrap:wrap;}
.sw{width:48px; height:48px; border-radius:50%; border:4px solid #fff; box-shadow:0 0 0 2px #ddd;}
.sw.sel{box-shadow:0 0 0 4px var(--bg1); transform:scale(1.1);}

/* ---------- SHOP ---------- */
.catBig{background:var(--card); border-radius:22px; box-shadow:var(--shadow); padding:8px; text-align:center; margin-bottom:12px;}
.catBig .bigCat{width:140px; margin:0 auto 6px;}
.tabs{display:flex; gap:8px; overflow-x:auto; padding-bottom:6px; margin-bottom:12px; -webkit-overflow-scrolling:touch;}
.tab{background:rgba(255,255,255,.7); color:var(--ink); font-weight:800; font-size:14px; border-radius:14px; padding:9px 14px; white-space:nowrap;}
.tab.sel{background:#fff; box-shadow:var(--shadow); color:var(--bg1);}
.items{display:grid; grid-template-columns:repeat(3,1fr); gap:10px; padding-bottom:16px;}
@media(max-width:520px){.items{grid-template-columns:repeat(2,1fr);}}
.item{background:var(--card); border-radius:18px; box-shadow:var(--shadow); padding:10px 8px; text-align:center; border:3px solid transparent;}
.item.equipped{border-color:var(--ok);}
.iEmoji{font-size:34px; height:40px;}
.iName{font-size:13px; font-weight:800; margin:2px 0;}
.iBtn{width:100%; border-radius:12px; padding:9px; font-weight:800; font-size:13px; margin-top:4px;}
.iBtn.buy{background:#f0ecfa; color:#a99; }
.iBtn.buy.can{background:linear-gradient(160deg,var(--sun),#ff9d2e); color:#5a3b00;}
.iBtn.equip{background:#efeaff; color:var(--bg1);}
.iBtn.on{background:var(--ok); color:#fff;}
.iBtn[disabled]{opacity:.55;}
.iLock{font-size:11px; color:var(--muted); margin-top:3px;}
</style>
</head>
<body>
<div id="confetti"></div>
<div class="app">
  <!-- HOME -->
  <div id="home">
    <div class="home-hd"><div class="sub">Cuaderno de verano</div><h1>Las mates de __NAME__</h1></div>
    <div class="hero" id="hero"></div>
    <div class="stats">
      <div class="stat"><b id="st-days">0</b><span>días hechos</span></div>
      <div class="stat"><b id="st-total">0</b><span>⭐ ganadas</span></div>
    </div>
    <div class="grid" id="grid"></div>
    <div class="homefoot">Elige un día y toca para empezar. ¡Gana estrellas y viste a tu gato! 🐱⭐<br>
      <button class="reset" id="resetBtn">Borrar mi progreso</button>
    </div>
  </div>

  <!-- CREATE -->
  <div id="createView" class="hidden">
    <div class="createCard">
      <h2>¡Crea tu gato! 🐱</h2>
      <p>Este será tu gato negro. Podrás vestirlo con las estrellas que ganes.</p>
      <div class="bigCat" id="c-cat"></div>
      <div class="pickTtl">Elige el color de sus ojos</div>
      <div class="swatches" id="c-eyes"></div>
      <button class="startbtn" id="c-done">¡Listo! Empezar 🚀</button>
    </div>
  </div>

  <!-- SHOP -->
  <div id="shopView" class="hidden">
    <div class="topbar"><button class="back" id="s-back">← Mapa</button><div class="topttl">🛍️ Tienda del gato</div></div>
    <div class="catBig"><div class="bigCat" id="s-cat"></div><span class="wallet" id="s-wallet"></span></div>
    <div class="tabs" id="s-tabs"></div>
    <div class="items" id="s-items"></div>
  </div>

  <!-- INTRO -->
  <div id="introView" class="hidden">
    <div class="topbar"><button class="back" id="i-back">← Mapa</button><div class="topttl" id="i-ttl"></div></div>
    <div class="card intro"><h2 id="i-h2"></h2><div id="i-body"></div>
      <button class="startbtn" id="i-start">¡Empezar! 🚀</button></div>
  </div>

  <!-- QUESTION -->
  <div id="quizView" class="hidden">
    <div class="topbar"><button class="back" id="q-back">← Mapa</button><div class="topttl" id="q-ttl"></div></div>
    <div class="dots" id="q-dots"></div>
    <div class="qwrap">
      <div class="qcard">
        <button class="hintbtn hidden" id="q-hintbtn">💡 Pista</button>
        <div class="qkind" id="q-kind"></div>
        <div id="q-body"></div>
        <div class="slots" id="q-slots"></div>
        <div class="fb" id="q-fb"></div>
        <div class="qhint hidden" id="q-hint"></div>
      </div>
      <div class="pad" id="q-pad"></div>
    </div>
  </div>

  <!-- DONE -->
  <div id="doneView" class="hidden">
    <div class="done-card" id="done-card"></div>
  </div>
</div>

<script>
const DATA = __DATA__;
const NAME = DATA.name;
const PRAISE = ["¡Genial! 🎉","¡Muy bien! 🌟","¡Eres una crack! 💪","¡Perfecto! ✨","¡Bravo! 🥳","¡Lo clavaste! 🎯"];
const TRYAG = ["Casi… ¡prueba otra vez! 💛","Uy, inténtalo de nuevo 🙂","No pasa nada, ¡otra vez! 🌈"];

// ================= GATO (SVG) + CATÁLOGO DE LA TIENDA =================
__CATJS__
const EYE_LIST=[{id:"verde",c:"#3ad07a",n:"Verde"},{id:"ambar",c:"#ffb02e",n:"Ámbar"},{id:"azul",c:"#4bb8ff",n:"Azul"},{id:"rosa",c:"#ff77c8",n:"Rosa"},{id:"lila",c:"#b98cff",n:"Lila"}];
const SKINS=[{id:"clasico",name:"Clásico",cost:0},{id:"esmoquin",name:"Esmoquin",cost:10},{id:"corazon",name:"Corazón",cost:12},{id:"rayado",name:"Rayitas",cost:12},{id:"vaca",name:"Manchitas",cost:15},{id:"galaxia",name:"Galaxia",cost:20}];
const SKIN_EMOJI={clasico:"🐱",esmoquin:"🤵",corazon:"💗",rayado:"🐯",vaca:"🐄",galaxia:"🌌"};
const ITEMS=[
 {id:"lazo",slot:"head",name:"Lazo",emoji:"🎀",cost:5},
 {id:"fiesta",slot:"head",name:"Gorro fiesta",emoji:"🎉",cost:4},
 {id:"flor",slot:"head",name:"Flor",emoji:"🌸",cost:6},
 {id:"gorro",slot:"head",name:"Gorro de lana",emoji:"🧢",cost:8},
 {id:"mago",slot:"head",name:"Sombrero mago",emoji:"🪄",cost:12},
 {id:"corona",slot:"head",name:"Corona",emoji:"👑",cost:15},
 {id:"gafas",slot:"eyes",name:"Gafas",emoji:"👓",cost:6},
 {id:"gafas_sol",slot:"eyes",name:"Gafas de sol",emoji:"🕶️",cost:8},
 {id:"antifaz",slot:"eyes",name:"Antifaz",emoji:"🦸",cost:10},
 {id:"cascabel",slot:"neck",name:"Cascabel",emoji:"🔔",cost:5},
 {id:"pajarita",slot:"neck",name:"Pajarita",emoji:"🎗️",cost:6},
 {id:"bandana",slot:"neck",name:"Bandana",emoji:"💠",cost:7},
 {id:"bufanda",slot:"neck",name:"Bufanda",emoji:"🧣",cost:9}
];
function avInit(){
  if(!progress.av) progress.av={created:false,name:NAME,eye:"verde",skin:"clasico",head:null,eyes:null,neck:null,owned:["clasico"]};
  const a=progress.av;
  if(!a.owned) a.owned=["clasico"];
  if(a.owned.indexOf("clasico")<0) a.owned.push("clasico");
  if(!a.skin) a.skin="clasico";
  if(!a.eye) a.eye="verde";
  if(!a.name) a.name=NAME;
}
function avState(){ const a=progress.av; return {skin:a.skin,eye:a.eye,head:a.head,eyes:a.eyes,neck:a.neck}; }
function totalStars(){ let s=0; DATA.days.forEach(d=>{ if(progress[d.n]!=null) s+=progress[d.n]; }); return s; }
function wallet(){ return totalStars()-(progress.spent||0); }
function owns(id){ return progress.av.owned.indexOf(id)>=0; }

// ---- storage (a prueba de fallos) ----
let progress = {};
function load(){ try{ progress = JSON.parse(localStorage.getItem("laura_mates")||"{}"); }catch(e){ progress={}; } }
function save(){ try{ localStorage.setItem("laura_mates", JSON.stringify(progress)); }catch(e){} }
load(); avInit();

// ---- helpers de respuesta ----
function answerOf(q){
  if(q.t==="sub") return q.a-q.b;
  if(q.t==="mul") return q.x*q.y;
  if(q.t==="miss") return q.r/q.a;
  if(q.t==="prob") return q.ans;
  return null;
}
function esc(s){return s;}

// ---- render de ilustraciones ----
function illusHTML(il){
  if(!il) return "";
  if(il.mode==="bignum") return '<div class="big">'+il.text.replace("−","−")+'</div>';
  if(il.mode==="row"){
    let s='<div class="emgrid">';
    for(let i=0;i<il.n;i++){ s+='<span class="em'+(i>=il.n-il.cross?' gone':'')+'">'+il.e+'</span>'; }
    return s+'</div>';
  }
  if(il.mode==="groups"){
    let s='<div class="gboxes">';
    for(let g=0;g<il.g;g++){ s+='<div class="gbox">'+il.e.repeat(il.per)+'</div>'; }
    return s+'</div>';
  }
  return "";
}

// ---- render del enunciado por tipo ----
function bodyHTML(q){
  if(q.t==="sub"){
    const w=Math.max((''+q.a).length,(''+q.b).length);
    const pa=(''+q.a).padStart(w,' '), pb=(''+q.b).padStart(w,' ');
    const c=s=>[...s].map(ch=>'<span class="vc">'+(ch===' '?'':ch)+'</span>').join('');
    const labs = w===3?["C","D","U"]:(w===2?["D","U"]:["U"]);
    let boxes='', labels='';
    for(let i=0;i<w;i++){ boxes+='<span class="acell"><span class="dbox" data-i="'+i+'"></span></span>';
      labels+='<span class="acell"><span class="dlab">'+labs[i]+'</span></span>'; }
    return '<div class="vsub"><div class="vrow">'+c(pa)+'</div>'+
           '<div class="vrow"><span class="vop">−</span>'+c(pb)+'</div>'+
           '<div class="vbar"></div>'+
           '<div class="vrow arow2">'+boxes+'</div>'+
           '<div class="vrow labrow">'+labels+'</div></div>';
  }
  if(q.t==="mul") return '<div class="mline">'+q.x+' × '+q.y+' =</div>';
  if(q.t==="miss") return '<div class="mline">'+q.a+' × ? = '+q.r+'</div>';
  if(q.t==="prob"||q.t==="steps") return '<div class="qtext">'+q.text+'</div><div class="illus">'+illusHTML(q.illus)+'</div>';
  return "";
}
function kindLabel(q){
  return {sub:"Resta ✏️",mul:"Multiplicación ✖️",miss:"¿Qué número falta? 🔍",prob:"Problema 🧩",steps:"Problema de 2 pasos 🧩"}[q.t]||"";
}

// ---- estado del quiz ----
let curDay=null, qi=0, slots=[], activeSlot=0, tries=0, firstTryCorrect=0, revealed=false;
let mode="single", dCells=[], dInfo=[], dAns=0, dW=1, dActive=0, qClean=true;

function show(id){ ["home","createView","shopView","introView","quizView","doneView"].forEach(v=>document.getElementById(v).classList.toggle("hidden",v!==id)); window.scrollTo(0,0); }

// ---- HOME ----
function renderHome(){
  let days=0;
  DATA.days.forEach(d=>{ if(progress[d.n]!=null) days++; });
  document.getElementById("st-days").textContent=days;
  document.getElementById("st-total").textContent=totalStars();
  document.getElementById("hero").innerHTML=
    '<div class="heroCat">'+catSVG(avState())+'</div>'+
    '<div class="hInfo"><div class="hHi">¡Hola, '+progress.av.name+'! 👋</div>'+
    '<div class="hSub">Este es tu gato negro</div>'+
    '<span class="wallet">⭐ '+wallet()+' para gastar</span></div>'+
    '<button class="tiendaBtn" id="goShop">🛍️<br>Tienda</button>';
  document.getElementById("goShop").onclick=openShop;
  const nextDay = (DATA.days.find(d=>progress[d.n]==null)||{}).n;
  const g=document.getElementById("grid"); g.innerHTML="";
  DATA.days.forEach(d=>{
    const done=progress[d.n]!=null;
    const el=document.createElement("button");
    el.className="daycard"+(done?" done":"")+(d.n===nextDay?" next":"");
    let st = done ? "⭐".repeat(progress[d.n]) : (d.n===nextDay?"👉":"");
    el.innerHTML=(d.new?'<span class="newdot">NUEVO</span>':'')+
      '<div class="dn">'+d.n+'</div><div class="dl">'+d.theme+'</div><div class="st">'+st+'</div>';
    el.onclick=()=>openDay(d.n);
    g.appendChild(el);
  });
  show("home");
}

function openDay(n){
  curDay=DATA.days.find(d=>d.n===n); qi=0; firstTryCorrect=0;
  if(curDay.intro){
    document.getElementById("i-ttl").textContent="Día "+n;
    document.getElementById("i-h2").textContent=curDay.intro.title;
    document.getElementById("i-body").innerHTML=curDay.intro.html;
    show("introView");
  } else { startQuiz(); }
}

function startQuiz(){ qi=0; show("quizView"); renderQ(); }

function renderDots(){
  const d=document.getElementById("q-dots"); d.innerHTML="";
  curDay.qs.forEach((_,i)=>{ const s=document.createElement("div");
    s.className="dot"+(i<qi?" done":"")+(i===qi?" cur":""); d.appendChild(s); });
}

function renderQ(){
  const q=curDay.qs[qi]; tries=0; revealed=false;
  document.getElementById("q-ttl").textContent="Día "+curDay.n+" · "+(qi+1)+"/"+curDay.qs.length;
  document.getElementById("q-kind").textContent=kindLabel(q);
  document.getElementById("q-body").innerHTML=bodyHTML(q);
  document.getElementById("q-fb").textContent=""; document.getElementById("q-fb").className="fb"; hideHint();
  // entrada
  slots=[]; activeSlot=0; dboxes=[]; dActive=0; mode="single";
  const sc=document.getElementById("q-slots"); sc.innerHTML="";
  if(q.t==="sub"){
    mode="columns"; qClean=true;
    const W=Math.max((''+q.a).length,(''+q.b).length); dW=W; dAns=q.a-q.b;
    const A=(''+q.a).padStart(W,'0').split('').map(Number);
    const B=(''+q.b).padStart(W,'0').split('').map(Number);
    let borrow=0; dInfo=new Array(W);
    for(let i=W-1;i>=0;i--){ const bin=borrow; const top=A[i]-borrow; let res,bout=0;
      if(top<B[i]){ res=top+10-B[i]; bout=1; borrow=1; } else { res=top-B[i]; borrow=0; }
      dInfo[i]={ai:A[i],bi:B[i],top:top,res:res,bin:bin,bout:bout}; }
    const names=W===3?["centenas","decenas","unidades"]:(W===2?["decenas","unidades"]:["unidades"]);
    dCells=[];
    document.querySelectorAll('#q-body .dbox').forEach((el,i)=>{ dCells.push({val:"",res:dInfo[i].res,locked:false,wrong:0,el:el,name:names[i]}); });
    dActive=W-1; drawCols();
  } else if(q.t==="steps"){
    mode="steps";
    q.parts.forEach((p,i)=>{
      const lab=document.createElement("div"); lab.className="slotlab"; lab.textContent=p.label; sc.appendChild(lab);
      const s=document.createElement("div"); s.className="slot"+(i===0?" active":""); s.dataset.i=i; s.onclick=()=>selSlot(i);
      sc.appendChild(s); slots.push({val:"",ans:p.ans,done:false,el:s});
    });
    drawSlots();
  } else {
    mode="single";
    const s=document.createElement("div"); s.className="slot active"; s.onclick=()=>selSlot(0);
    sc.appendChild(s); slots.push({val:"",ans:answerOf(q),done:false,el:s});
    drawSlots();
  }
  document.getElementById("q-hintbtn").classList.toggle("hidden", mode==="columns");
  renderDots(); buildPad();
}

function selSlot(i){ if(slots[i].done) return; activeSlot=i; drawSlots(); }
function drawSlots(){
  slots.forEach((s,i)=>{
    s.el.classList.toggle("active", i===activeSlot && !s.done);
    if(s.done){ s.el.innerHTML=s.val; }
    else if(i===activeSlot){ s.el.innerHTML=(s.val||"")+'<span class="caret"></span>'; }
    else { s.el.innerHTML=s.val||""; }
  });
}

function buildPad(){
  const pad=document.getElementById("q-pad"); pad.innerHTML="";
  const keys=["1","2","3","4","5","6","7","8","9","⌫","0","✓"];
  keys.forEach(k=>{
    const b=document.createElement("button");
    if(k==="⌫"){ b.className="key del"; b.textContent="⌫"; b.onclick=delDigit; }
    else if(k==="✓"){
      if(mode==="columns"){ b.className="key"; b.style.background="linear-gradient(160deg,#ffd54a,#ff9d2e)"; b.style.color="#5a3b00"; b.textContent="💡"; b.onclick=()=>showHint(colExplain(dActive)); }
      else { b.className="key"; b.style.background="linear-gradient(160deg,var(--ok),var(--okd))"; b.style.color="#fff"; b.textContent="✓"; b.onclick=check; }
    }
    else { b.className="key"; b.textContent=k; b.onclick=()=>typeDigit(k); }
    pad.appendChild(b);
  });
}
function typeDigit(k){
  if(mode==="columns"){ colType(k); return; }
  const s=slots[activeSlot]; if(s.done)return; if(s.val.length<4){ s.val+=k; drawSlots(); }
}
function delDigit(){
  if(mode==="columns"){ const c=dCells[dActive]; if(c && !c.locked){ c.val=""; drawCols(); } return; }
  if(slots[activeSlot].done)return; slots[activeSlot].val=slots[activeSlot].val.slice(0,-1); drawSlots();
}
function drawCols(){
  dCells.forEach((c,i)=>{
    c.el.classList.remove("active","ok","bad","lockcol");
    if(c.locked){ c.el.classList.add("ok"); c.el.textContent=c.val; }
    else if(i===dActive){ c.el.classList.add("active"); c.el.innerHTML=(c.val!==""?c.val:'<span class="caret"></span>'); }
    else { c.el.classList.add("lockcol"); c.el.innerHTML='<span class="lk">🔒</span>'; }
  });
}
function colType(k){
  const c=dCells[dActive]; const fb=document.getElementById("q-fb");
  if(parseInt(k,10)===c.res){
    c.val=k; c.locked=true;
    if(dActive>0){
      dActive--; hideHint(); drawCols();
      fb.className="fb ok"; fb.textContent="¡Muy bien! Ahora las "+dCells[dActive].name+" 👇";
    } else {
      drawCols();
      if(qClean && !revealed) firstTryCorrect++;
      fb.className="fb ok"; fb.textContent=PRAISE[Math.floor(qi+curDay.n)%PRAISE.length];
      burst(); setTimeout(next,900);
    }
  } else {
    c.val=k; qClean=false; c.wrong++; drawCols();
    c.el.classList.add("bad"); setTimeout(()=>{ if(!c.locked){ c.val=""; drawCols(); } },460);
    fb.className="fb no"; fb.textContent=TRYAG[c.wrong%TRYAG.length];
    if(c.wrong>=2){ revealed=true; showHint(colExplain(dActive)); }
  }
}
function colExplain(i){
  const info=dInfo[i]; const c=dCells[i];
  const cap=c.name.charAt(0).toUpperCase()+c.name.slice(1);
  if(info.bout){
    const base = info.bin ? ("Como prestaste antes, arriba queda "+info.ai+"−1 = "+info.top+". ") : "";
    return base+cap+": "+info.top+" − "+info.bi+" no se puede, así que pides prestado 1. "+info.top+" + 10 = "+(info.top+10)+", y "+(info.top+10)+" − "+info.bi+" = "+info.res+". ¡No olvides la llevada!";
  } else if(info.bin){
    return cap+": como prestaste antes, arriba queda "+info.ai+"−1 = "+info.top+". "+info.top+" − "+info.bi+" = "+info.res+".";
  }
  return cap+": "+info.ai+" − "+info.bi+" = "+info.res+".";
}
function mulHint(x,y){
  const res=x*y;
  if(x===0||y===0) return "Cualquier número por 0 es 0. Por eso "+x+" × "+y+" = 0.";
  if(x===1) return "El 1 no cambia el número: 1 × "+y+" = "+y+".";
  if(y===1) return "El 1 no cambia el número: "+x+" × 1 = "+x+".";
  const a=Math.max(x,y), bb=Math.min(x,y);
  if(bb<=6){ const arr=[]; for(let i=0;i<bb;i++) arr.push(a); return x+" × "+y+" es sumar "+a+" un total de "+bb+" veces: "+arr.join(" + ")+" = "+res+"."; }
  return x+" × "+y+": cuenta de "+a+" en "+a+", "+bb+" saltos. El resultado es "+res+".";
}
function missHint(a,r){
  const t=r/a; const arr=[]; for(let i=1;i<=t;i++) arr.push(a*i);
  return a+" × ? = "+r+". Cuenta de "+a+" en "+a+": "+arr.join(", ")+". Das "+t+" saltos, así que el número que falta es "+t+".";
}
function probHint(q){
  const il=q.illus||{};
  if(il.mode==="row") return "Cuenta solo los dibujos que NO están tachados. Quedan "+q.ans+".";
  if(il.mode==="groups") return "Hay "+il.g+" grupos de "+il.per+". Cuéntalos todos (o suma "+il.per+" “"+il.g+" veces”). En total son "+q.ans+".";
  if(il.mode==="bignum") return "Colócalo en columnas y resta de derecha a izquierda (unidades, decenas, centenas). El resultado es "+q.ans+".";
  return "Piensa qué operación necesitas y hazla con calma. El resultado es "+q.ans+".";
}
function questionHint(){
  const q=curDay.qs[qi];
  if(mode==="columns") return colExplain(dActive);
  if(q.t==="mul") return mulHint(q.x,q.y);
  if(q.t==="miss") return missHint(q.a,q.r);
  if(q.t==="prob") return probHint(q);
  if(q.t==="steps"){ const p=q.parts[activeSlot]; return "Fíjate en “"+p.label+"” y resuélvelo. El resultado es "+p.ans+"."; }
  return "La respuesta es "+(slots[0]?slots[0].ans:"")+".";
}
function showHint(txt){ const el=document.getElementById("q-hint"); el.innerHTML="💡 "+txt; el.classList.remove("hidden"); }
function hideHint(){ const el=document.getElementById("q-hint"); if(el) el.classList.add("hidden"); }

function check(){
  if(mode==="columns"){ showHint(colExplain(dActive)); return; }
  const q=curDay.qs[qi]; const fb=document.getElementById("q-fb");
  // para steps, comprobamos el slot activo; para el resto, el único
  const s=slots[activeSlot];
  if(s.done){ return; }
  if(s.val===""){ return; }
  tries++;
  if(parseInt(s.val,10)===s.ans){
    s.done=true; s.el.classList.remove("active","bad"); s.el.classList.add("ok"); s.el.innerHTML=s.val;
    // ¿quedan slots?
    const nextOpen=slots.findIndex(x=>!x.done);
    if(nextOpen===-1){
      if(tries===1 && !revealed) firstTryCorrect++;
      fb.className="fb ok"; fb.textContent=PRAISE[Math.floor(qi+curDay.n)%PRAISE.length];
      burst();
      setTimeout(next, 900);
    } else {
      activeSlot=nextOpen; drawSlots();
      fb.className="fb ok"; fb.textContent="¡Bien! Sigue 👍";
    }
  } else {
    s.el.classList.add("bad"); setTimeout(()=>s.el.classList.remove("bad"),400);
    fb.className="fb no"; fb.textContent=TRYAG[tries%TRYAG.length];
    if(tries>=2){ revealed=true; showHint(questionHint()); }
    s.val=""; drawSlots();
  }
}

function next(){
  qi++;
  if(qi>=curDay.qs.length){ finishDay(); }
  else { renderQ(); }
}

function finishDay(){
  const total=curDay.qs.length;
  let stars = firstTryCorrect>=total ? 3 : (firstTryCorrect>=Math.ceil(total*0.6) ? 2 : 1);
  const prev=progress[curDay.n]||0;
  progress[curDay.n]=Math.max(prev,stars); save();
  bigConfetti();
  const c=document.getElementById("done-card");
  const nextN = (DATA.days.find(d=>progress[d.n]==null)||{}).n;
  let dip="";
  if(curDay.diploma){
    dip='<div class="diploma"><div class="dh">🏅 DIPLOMA DE VERANO 🏅</div>'+
        '<div>Este diploma es para</div><div class="dnm">'+NAME+'</div>'+
        '<div>por repasar las mates de todo el verano.<br>¡Enhorabuena, campeona! 🌟</div></div>';
  }
  c.innerHTML='<div class="bigstars">'+'⭐'.repeat(stars)+'☆'.repeat(3-stars)+'</div>'+
    '<h2>¡Día '+curDay.n+' completado!</h2>'+
    '<div class="score">Acertaste a la primera '+firstTryCorrect+' de '+total+'</div>'+
    '<div class="done-msg">'+(stars===3?'¡Increíble, todo perfecto! 🥳':'¡Muy buen trabajo! 💪')+'</div>'+
    '<div class="wallet" style="margin:10px auto 0;">🛍️ Tienes '+wallet()+' ⭐ para la tienda</div>'+
    dip+
    '<div class="done-btns">'+
      '<button class="bhome" id="d-home">🗺️ Mapa</button>'+
      '<button class="bhome" id="d-shop">🛍️ Tienda</button>'+
      (nextN?'<button class="bnext" id="d-next">Día '+nextN+' →</button>':'<button class="bnext" id="d-again">Repetir 🔁</button>')+
    '</div>';
  document.getElementById("d-home").onclick=renderHome;
  document.getElementById("d-shop").onclick=openShop;
  const dn=document.getElementById("d-next"); if(dn) dn.onclick=()=>openDay(nextN);
  const da=document.getElementById("d-again"); if(da) da.onclick=()=>openDay(curDay.n);
  show("doneView");
}

// ================= CREAR GATO + TIENDA =================
let createEye="verde";
function renderCreate(){
  createEye = progress.av.eye || "verde";
  drawCreateCat();
  const box=document.getElementById("c-eyes"); box.innerHTML="";
  EYE_LIST.forEach(e=>{ const b=document.createElement("button");
    b.className="sw"+(e.id===createEye?" sel":""); b.style.background=e.c;
    b.onclick=()=>{ createEye=e.id; renderCreate(); }; box.appendChild(b); });
  show("createView");
}
function drawCreateCat(){ document.getElementById("c-cat").innerHTML=catSVG({skin:"clasico",eye:createEye}); }
function finishCreate(){ progress.av.eye=createEye; progress.av.created=true; save(); burst(); renderHome(); }

let shopTab="skin";
function openShop(){ shopTab="skin"; renderShop(); }
function renderShop(){
  document.getElementById("s-cat").innerHTML=catSVG(avState());
  document.getElementById("s-wallet").textContent="⭐ "+wallet()+" para gastar";
  const tabs=[["skin","Pelaje 🐈"],["head","Cabeza 🎩"],["eyes","Gafas 👓"],["neck","Cuello 🎀"],["eyecolor","Ojos 👀"]];
  const tb=document.getElementById("s-tabs"); tb.innerHTML="";
  tabs.forEach(t=>{ const b=document.createElement("button"); b.className="tab"+(t[0]===shopTab?" sel":"");
    b.textContent=t[1]; b.onclick=()=>{ shopTab=t[0]; renderShop(); }; tb.appendChild(b); });
  const box=document.getElementById("s-items"); box.innerHTML="";
  if(shopTab==="eyecolor"){
    EYE_LIST.forEach(e=>{
      const on=progress.av.eye===e.id;
      const el=document.createElement("div"); el.className="item"+(on?" equipped":"");
      el.innerHTML='<div class="iEmoji"><span style="display:inline-block;width:32px;height:32px;border-radius:50%;background:'+e.c+';margin-top:4px"></span></div>'+
        '<div class="iName">'+e.n+'</div><button class="iBtn '+(on?"on":"equip")+'">'+(on?"Puestos ✓":"Poner")+'</button>';
      el.querySelector("button").onclick=()=>{ progress.av.eye=e.id; save(); renderShop(); };
      box.appendChild(el);
    });
    show("shopView"); return;
  }
  let list = (shopTab==="skin")
    ? SKINS.map(s=>({id:s.id,name:s.name,emoji:SKIN_EMOJI[s.id],cost:s.cost,slot:"skin"}))
    : ITEMS.filter(i=>i.slot===shopTab);
  list.forEach(it=>{
    const bought = it.cost===0 || owns(it.id);
    const equipped = (it.slot==="skin") ? progress.av.skin===it.id : progress.av[it.slot]===it.id;
    const el=document.createElement("div"); el.className="item"+(equipped?" equipped":"");
    let btn;
    if(!bought){ const can=wallet()>=it.cost;
      btn='<button class="iBtn buy'+(can?" can":"")+'"'+(can?"":" disabled")+'>⭐ '+it.cost+'</button>'; }
    else if(equipped){ btn='<button class="iBtn on">'+(it.slot==="skin"?"Puesto ✓":"Puesto ✓ (quitar)")+'</button>'; }
    else { btn='<button class="iBtn equip">Poner</button>'; }
    el.innerHTML='<div class="iEmoji">'+it.emoji+'</div><div class="iName">'+it.name+'</div>'+btn;
    const b=el.querySelector("button");
    if(b) b.onclick=()=>{ if(!bought) buyItem(it); else equipItem(it); };
    box.appendChild(el);
  });
  show("shopView");
}
function buyItem(it){
  if(wallet()<it.cost) return;
  progress.spent=(progress.spent||0)+it.cost;
  progress.av.owned.push(it.id);
  if(it.slot==="skin") progress.av.skin=it.id; else progress.av[it.slot]=it.id;
  save(); burst(); renderShop();
}
function equipItem(it){
  if(it.slot==="skin"){ progress.av.skin=it.id; }
  else { progress.av[it.slot] = (progress.av[it.slot]===it.id ? null : it.id); }
  save(); renderShop();
}

// ---- confetti ----
function spawn(list,ms){
  const box=document.getElementById("confetti");
  list.forEach(()=>{
    const s=document.createElement("div"); s.className="cf";
    s.textContent=["⭐","🌟","🎉","✨","💛","🎈","🌈"][Math.floor(Math.random()*7)];
    s.style.left=(Math.random()*100)+"vw"; s.style.top="-30px";
    s.style.animationDuration=(1.6+Math.random()*1.4)+"s"; s.style.fontSize=(16+Math.random()*22)+"px";
    box.appendChild(s); setTimeout(()=>s.remove(),ms);
  });
}
function burst(){ spawn(new Array(10).fill(0),2600); }
function bigConfetti(){ spawn(new Array(40).fill(0),3200); }

// ---- eventos ----
document.getElementById("i-back").onclick=renderHome;
document.getElementById("q-back").onclick=renderHome;
document.getElementById("s-back").onclick=renderHome;
document.getElementById("c-done").onclick=finishCreate;
document.getElementById("i-start").onclick=startQuiz;
document.getElementById("q-hintbtn").onclick=()=>showHint(questionHint());
document.getElementById("resetBtn").onclick=()=>{ if(confirm("¿Borrar todo (estrellas y gato) y empezar de cero?")){ progress={}; avInit(); save(); renderCreate(); } };

// ---- arranque ----
if(!progress.av.created){ renderCreate(); } else { renderHome(); }
</script>
</body>
</html>
"""

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
with open(os.path.join(_HERE, "cat.js"), encoding="utf-8") as f:
    cat_js = f.read()
html = (HTML.replace("__CATJS__", cat_js)
            .replace("__DATA__", data_json)
            .replace("__NAME__", NAME))
_out_dir = os.path.join(_ROOT, "public")
os.makedirs(_out_dir, exist_ok=True)
_out = os.path.join(_out_dir, "index.html")
with open(_out, "w", encoding="utf-8") as f:
    f.write(html)
print("App generada:", len(html), "bytes ·", len(DAYS), "días ->", _out)
