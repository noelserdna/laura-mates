# CLAUDE.md — contexto del proyecto para Claude Code

## Qué es
App web educativa para una niña de ~7 años (Laura) que repasa mates en verano:
restas con llevadas (2 y 3 cifras), tablas de multiplicar y problemas
ilustrados. Incluye un gato negro personalizable con tienda de skins/accesorios
comprados con estrellas. También hay un cuaderno imprimible en PDF.

## Principios de diseño (IMPORTANTE, respétalos)
- **Un solo archivo, sin dependencias, offline.** La app final es
  `public/index.html`: HTML + CSS + JS + SVG todo inline, sin CDN ni red. Debe
  poder abrirse en Safari (iPad) sin conexión. No añadas dependencias externas
  ni llamadas de red.
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
  - Inyecta `src/cat.js` (gato SVG + catálogo de la tienda) en el placeholder
    `__CATJS__`, los datos en `__DATA__` y el nombre en `__NAME__`.
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
  - Pantallas: `home` (mapa de días + gato + monedero + tienda), `createView`
    (crear gato), `shopView` (tienda), `introView` (explicación de días nuevos),
    `quizView` (ejercicios), `doneView` (fin de día + diploma).
  - Estado del quiz: `curDay`, `qi`, y para restas el modo `columns` con
    `dCells`/`dInfo` (una casilla por columna U/D/C, desbloqueo secuencial
    derecha→izquierda). Otros tipos usan `slots` (una o varias casillas).
  - Ayuda: `questionHint()` devuelve la explicación según el tipo
    (`colExplain`, `mulHint`, `missHint`, `probHint`); se muestra tras 2 fallos
    o con el botón 💡.
  - Progreso/monedero: `totalStars()` (suma de estrellas por día),
    `wallet()` = ganadas − `spent`; comprar descuenta de `spent`, nunca de los
    días. Avatar en `progress.av` (skin, eye, head, eyes, neck, owned[]).
  - Gato: `catSVG(state)` en `src/cat.js` compone capas (cuerpo, orejas, ojos,
    marcas de pelaje según skin, y accesorios de cabeza/gafas/cuello).

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
  al cambiar de dispositivo o borrar el navegador.
- Sumas llevando con el mismo formato por columnas.
- Huequito para apuntar la llevada encima de cada columna (como en papel).
- Más skins/accesorios (alitas, mochila, gorro de cumpleaños...).
- Sonidos de premio; medallas por rachas de días.
- Ajustar tras cuántos fallos aparece la explicación (ahora 2).
- Pista visual (dibujo de grupos) en las multiplicaciones.
