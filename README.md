# Las mates de Laura 🐱⭐

App web interactiva (y cuaderno imprimible) para que una niña de ~7 años repase
las mates en verano: **restas con llevadas** (con el "1" de la llevada pintado
encima de cada columna, como en papel), **tablas de multiplicar del 2 al 10**
con dibujos de grupos, **problemas ilustrados** de 1 y 2 pasos y de comparación,
con autocorrección paso a paso, teclado en pantalla, pistas en dos niveles,
repaso automático de fallos, sonidos, medallas, rachas, regalos sorpresa y un
**gato negro personalizable** (¡vivo!: parpadea, mueve la cola y reacciona) con
una **tienda** de skins y accesorios que se desbloquean con las estrellas ganadas.

La app es un **único archivo HTML autocontenido**, sin dependencias ni conexión:
funciona offline en el iPad (ideal para viajes) y guarda el progreso en el
navegador (`localStorage`).

### Tutor con IA (opcional)

Desde la **Zona de familia** (protegida con una multiplicación que la peque aún
no sabe hacer) se puede pegar una clave de API de Claude para activar un tutor
con IA (modelo Haiku): el gato inventa **retos con ejercicios nuevos adaptados**
a su progreso real, da **pistas personalizadas** cuando falla y escribe
**mensajes de ánimo**. Con límites de uso diario configurables y aviso de coste
(≈0,05 $/día como máximo con los límites por defecto).

> 🔑 **La clave nunca se guarda en el repo ni en la web publicada**: se escribe
> una vez en el dispositivo y vive solo en su `localStorage` (en una clave
> separada del progreso). Sin clave o sin conexión, la app funciona exactamente
> igual: la IA es siempre un extra, nunca un requisito.

## Estructura

```
laura-mates/
├── public/
│   └── index.html          # App final (generada). Esto es lo que se despliega.
├── src/
│   ├── build_app.py        # Generador de la app web (inyecta cat.js + ai.js + datos)
│   ├── cat.js              # Gato negro en SVG + catálogo de la tienda
│   ├── ai.js               # Tutor IA opcional (Claude Haiku, clave solo en el dispositivo)
│   └── generate_pdf.py     # (Opcional) genera el cuaderno imprimible en PDF
├── Cuaderno_de_verano_Laura.pdf   # Cuaderno imprimible (B/N, 30 días)
├── .github/workflows/deploy.yml   # Deploy automático a GitHub Pages
└── CLAUDE.md               # Contexto para Claude Code
```

## Cómo construir la app

Solo necesita **Python 3** (sin librerías externas):

```bash
python src/build_app.py
# -> escribe public/index.html
```

Para generarla con otro nombre de niño/a:

```bash
KID_NAME=Marta python src/build_app.py
```

Para probarla en local, abre `public/index.html` en el navegador (o sirve la
carpeta):

```bash
python -m http.server -d public 8000   # luego abre http://localhost:8000
```

## Deploy en GitHub Pages

1. Crea un repo en GitHub y sube este proyecto:
   ```bash
   git init
   git add .
   git commit -m "Las mates de Laura: app + cuaderno"
   git branch -M main
   git remote add origin https://github.com/<usuario>/laura-mates.git
   git push -u origin main
   ```
2. En GitHub: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. El workflow `.github/workflows/deploy.yml` construye `public/index.html` y lo
   publica automáticamente en cada `push` a `main`. La URL será
   `https://<usuario>.github.io/laura-mates/`.

> Nota: `public/index.html` también está commiteado, así que la web funciona
> aunque no se ejecute el build.

## El cuaderno imprimible (opcional)

`src/generate_pdf.py` genera el PDF de 30 días en blanco y negro. Necesita
Playwright con Chromium y la fuente *Comic Neue*:

```bash
pip install playwright
playwright install chromium
sudo apt-get install -y fonts-comic-neue   # o instala la fuente en tu sistema
python src/generate_pdf.py
```

## Licencia / uso

Proyecto personal y educativo. Úsalo y modifícalo libremente para tus peques.
