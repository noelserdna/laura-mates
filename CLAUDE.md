# CLAUDE.md — contexto del proyecto para Claude Code

## Qué es
App web educativa para una niña de ~7 años (Laura) que repasa mates en verano:
restas con llevadas (2 y 3 cifras, con el "1" de la llevada pintado encima de
cada columna), tablas de multiplicar del 2 al 10 (con dibujos de grupos y
trucos por tabla), problemas ilustrados de 1 y 2 pasos y de comparación.
Incluye una colonia de gatos personalizables con nombre (se adoptan con
estrellas y pasean por la pantalla de inicio; al acariciarlos maúllan), tienda
de skins/accesorios, medallas, rachas, regalos sorpresa, sonidos (Web Audio),
repaso automático de fallos, días extra generados en el dispositivo (botón ➕)
y un tutor con IA opcional (Claude Haiku). También hay un cuaderno imprimible
en PDF.

## Principios de diseño (IMPORTANTE, respétalos)
- **Un solo archivo, sin dependencias, offline.** La app final es
  `public/index.html`: HTML + CSS + JS + SVG todo inline, sin CDN ni red. Debe
  poder abrirse en Safari (iPad) sin conexión. No añadas dependencias externas.
  Única excepción de red: el tutor IA opcional (ver abajo), que solo llama a
  `api.anthropic.com` si la familia lo activó, y ante cualquier fallo degrada
  en silencio al modo offline.
- **La clave de API NUNCA en el repo ni en `public/`.** GitHub Pages es
  público. La clave la escribe la familia en la "Zona de familia" y vive solo
  en `localStorage` bajo `laura_mates_familia` (clave separada del progreso
  para que "Borrar mi progreso" no la toque).
- **No uses frameworks ni build tools de JS.** El "build" es un script Python
  que ensambla el HTML. Mantén esa simplicidad.
- **Persistencia con `localStorage`** bajo la clave `laura_mates`, siempre
  envuelto en `try/catch` (algunos entornos lo bloquean; no debe romper).
- **Pensado para una niña de 7 años:** botones grandes, teclado numérico en
  pantalla (no el del sistema), colores y emojis, mensajes amables, y ayuda
  cuando se equivoca. En papel el PDF es en blanco y negro; en pantalla es a
  color.

## Cómo se construye
- `src/build_app.py` (Python 3, sin librerías) genera `public/index.html`.
  - Contiene el **curriculum** (lista `DAYS`, 30 días) y el **CSS/HTML/JS** de la
    app como plantilla (variable `HTML`).
  - Inyecta `src/cat.js` (gato SVG + catálogo) en `__CATJS__`, `src/ai.js`
    (tutor IA opcional) en `__AIJS__`, los datos en `__DATA__` y el nombre en
    `__NAME__`.
  - Salida: `public/index.html`. Nombre configurable con `KID_NAME`.
- Regenerar tras cualquier cambio en `src/`:
  ```bash
  python src/build_app.py
  ```
  Editar `public/index.html` a mano NO es la fuente de verdad; se sobrescribe.

## Arquitectura del código (dentro de build_app.py)
- **Generadores de contenido (Python):** `gen_sub`/`uniq_subs` crean restas con
  control de llevadas (`borrows`: 0, 1, 2 o "any"); `sub/mul/miss/prob/steps`
  construyen las preguntas; `DAYS` define los 30 días (tema, intro opcional,
  lista de preguntas `qs`).
- **App (JS, dentro de la plantilla HTML):**
  - Pantallas: `home` (mapa + gato + medallas + monedero + tienda), `createView`
    (crear gato), `shopView` (tienda), `introView` (explicación de días nuevos),
    `quizView` (ejercicios, con gato acompañante que reacciona), `doneView`
    (celebración de fin de día + regalos/medallas/diploma) y `familyView`
    (Zona de familia, tras puerta parental `parentGate()`).
  - Estado del quiz: `curDay` (SIEMPRE un clon del día: `next()` puede añadir
    repeticiones de preguntas falladas), `qi`, y para restas el modo `columns`
    con `dCells`/`dInfo` (una casilla por columna U/D/C, desbloqueo secuencial
    derecha→izquierda; al resolver una columna con llevada se pinta un "1" en
    la `.cbox` de la siguiente). Otros tipos usan `slots` con `tr` (intentos
    por casilla — así los `steps` de 2 pasos puntúan bien las estrellas).
  - Ayuda en 2 niveles: `questionHint(deep)` — sin `deep` da estrategia sin
    resultado; `deep` (2º toque de 💡 o 4 fallos) da la respuesta. Pulsar 💡
    marca `revealed` (no hay estrella gratis). Tras 2 fallos salta sola.
  - Refuerzo: pregunta fallada se repite al final del día (`rep:true`, no
    puntúa) y va al banco `progress.errs` (máx 10) → tarjeta "🔁 Mi repaso".
  - Progreso/monedero: `totalStars()` = estrellas por día + `progress.extra`
    (bonus por días perfectos/rachas/repasos) + `progress.bonus` (retos IA);
    `wallet()` = ganadas − `spent`. Racha en `progress.streak` (aguanta 1 día
    de descanso), regalos cada 5 días (`lastGift`), medallas en
    `progress.medals` (`MEDALS`/`checkMedals`), estadísticas por tipo en
    `progress.stats`. Avatar en `progress.av` (skin, eye, head, eyes, neck,
    back, owned[]).
  - Gato: `catSVG(state)` en `src/cat.js` compone capas (cola animada, espalda,
    cuerpo, orejas, cabeza, marcas de pelaje, ojos con `mood` "feliz"/"uy" y
    accesorios). Skins de premio: `solverano` (día 15) y `arcoiris` (día 30).
  - Colonia: `progress.av` es SIEMPRE el gato activo (nombre en `av.catName`);
    los demás viven en `progress.cats[]` con `progress.activeIdx`. `save()`
    llama a `syncCat()` (vuelca av→cats); `loadCat(i)` hace el cambio inverso.
    Adopción en la tienda (`adoptCat`, precio creciente, máx 6). En el home,
    `renderColony()`+`colonyTick` (interval 50 ms, solo con home visible)
    pasean los gatos; `petCat()` = maullido (`sfxMeow`) + salto + corazón.
  - Días extra: botón ➕ en el mapa → `makeExtraDay()` genera en JS (sin red)
    un día n≥31 (restas `genSubJS`, tablas con hechos difíciles, miss y
    problema con plantillas `extraProb`) y lo guarda en `progress.extraDays`.
    TODO recorrido de días debe usar `allDays()` (= `DATA.days` + extras),
    nunca `DATA.days` directo (salvo la medalla `mfin`, que es de los 30
    originales a propósito).
  - Sonidos: osciladores Web Audio (`sfxOk/sfxNo/sfxWin/sfxCoin`), silenciables
    con `progress.mute` (botón 🔊 del quiz).
- **Tutor IA (`src/ai.js`, opcional):**
  - Config de familia en `localStorage` `laura_mates_familia` (`famConf`):
    enabled, key, límites diarios (retos/pistas/msgs con techos duros `AI_MAX`)
    y contadores de uso/coste.
  - `aiCall(system, user, schema, maxTok, tipo)`: fetch a
    `api.anthropic.com/v1/messages` (modelo `claude-haiku-4-5`, cabecera
    `anthropic-dangerous-direct-browser-access`, `output_config` json_schema
    para JSON garantizado). Cualquier error → `null` (la app sigue igual);
    2×401 desactiva la IA sola; 429/529 → cooldown 10 min.
  - Usos: `startReto()` (tanda de 6 ejercicios adaptados al progreso, mapeados
    con `aiMapEjercicios` a los tipos nativos y validados en cliente — la
    respuesta correcta SIEMPRE se calcula en cliente), `aiHintCol`/
    `aiHintSingle` (pista personalizada tras 2 fallos, se antepone a la
    determinista), `aiDayMsg` (mensaje del gato en fin de día, cacheado en
    `progress.aiMsgs` para no repagar). Texto del modelo SIEMPRE escapado con
    `escT()` antes de innerHTML.

## Cómo verificar cambios
No hay tests automáticos. Verifica en un navegador (idealmente headless con
Playwright/Chromium) o abriendo `public/index.html`:
1. Crear gato → mapa.
2. Un día de restas: casillas por columna, desbloqueo secuencial, explicación
   tras 2 fallos, botón 💡.
3. Un día de multiplicación/problema: casilla única, pista.
4. Ganar estrellas → tienda: comprar (descuenta monedero) y equipar (gato se
   actualiza en vivo).
5. Recargar: el progreso persiste (localStorage).

## Deploy
GitHub Pages vía `.github/workflows/deploy.yml`: en cada push a `main` ejecuta
`python src/build_app.py` y publica `public/`. Ver README.

## Ideas para seguir (backlog sugerido)
- Botón "Guardar copia / Restaurar" progreso (código o archivo) para no perderlo
  al cambiar de dispositivo o borrar el navegador (¡nunca incluir la clave IA!).
- Sumas llevando con el mismo formato por columnas.
- Regenerar el cuaderno PDF con el curriculum nuevo (tablas del 8 y 9,
  problemas de comparación y 2 pasos) — `generate_pdf.py` sigue con el viejo.
- Mapa de días como camino de aventura (en vez de rejilla).
- Modo "practicar una tabla" suelto (fuera de los días).
- Más voces del gato: maullido con Web Audio al acariciarlo.
