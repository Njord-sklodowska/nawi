# Pull Request — frontend Nawi (`jorge/frontend` → `develop`)

- **Rama**: `jorge/frontend` (pusheada en `origin`)
- **Destino**: `develop`
- **Remoto**: `git@github.com:Njord-sklodowska/nawi.git`
- **Comparación (abrir el PR acá)**:
  https://github.com/Njord-sklodowska/nawi/compare/develop...jorge/frontend

> **La creación del PR es manual.** En este entorno no hay `gh` CLI ni token de GitHub, así
> que no se puede abrir por API: hay que entrar al enlace de comparación, pegar el título y el
> cuerpo de abajo, y crearlo desde la web.
>
> Antes de abrirlo, confirmar que no queden cambios sin commitear en `src/App.vue` /
> `src/styles.css` / `src/components/**`: si están sin commitear, la comparación no los muestra.

## Título propuesto

```text
Frontend Nawi: visor de observaciones SPHEREx con datos reales, rastro validado y capa de datos intercambiable
```

## Cuerpo (pegar tal cual)

````markdown
## Qué trae esta rama

- **Prototipo funcional del visor** en Vue 3 + Vite + Bootstrap 5: catálogo de objetos, serie
  temporal de recortes, línea de tiempo con reproducción automática y comparación
  "antes y después".
- **Capa de datos intercambiable** (`src/data/catalog/`): fuente `mock` (demostración, sin red)
  y fuente `api` contra el backend Django. La vista no sabe de dónde vienen los datos.
- **Los cinco objetos con cuadros reales** del backend (37 recortes en total), con longitud de
  onda y ancho de banda publicados.
- **Latido (curva de brillo)** de RW Aurigae: 7 mediciones en Jy con su error, dibujadas en SVG
  sin librerías; el panel solo aparece cuando hay curva.
- **Rastro de Barnard medido y validado**: 10,61 ± 0,23″ en 9 cuadros contra 10,39″/año
  publicados por el catálogo, con `frase_simple` en lenguaje llano.
- **Zoom de escalas enteras y suavizado opcional**: píxel real por defecto; si se interpola, la
  interfaz avisa que no son los píxeles originales.
- **Estados vacíos honestos**: objetos sin cuadros, sin latido, con calidad dudosa, con núcleo
  saturado o con señal débil se explican con texto en vez de quedar en blanco.
- **Estado de la fuente reactivo** (`demo` / `live` / `pending` / `error`): si el backend no
  responde, la barra lateral deja de afirmar "datos del backend" y muestra el error real.
- **Tema oscuro y claro** (oscuro por defecto, preferencia recordada).
- **Build de producción con datos reales** (`.env.production`) y documentación (`README.md`,
  `doc/contrato-api.md`).

## Qué se ve hoy con los datos reales

| Objeto | Cuadros | Longitud de onda | Latido | Rastro | Calidad |
|---|---|---|---|---|---|
| Estrella de Barnard | 9 | 4,39 – 4,92 μm | — | **medido** (10,61 ± 0,23″) | ok |
| WISE 0855-0714 | 7 | 4,41 – 4,97 μm | — | — | dudosa (señal débil, 1–5 σ) |
| Epsilon Indi B | 2 | 4,52 – 4,66 μm | — | — | dudosa |
| RW Aurigae | 7 | 4,41 – 4,96 μm | **7 puntos (Jy)** | — | ok |
| R Draconis | 12 | 4,42 – 4,81 μm | — | — | dudosa (núcleo saturado) |

Recortes de 58 × 58 px con 6,15″ por píxel (campo de 5,95′).

## Cómo probarlo

```bash
npm install
python3.12 -m venv backend/.venv
backend/.venv/bin/pip install -r backend/requirements.txt

cp .env.example .env.local     # y dejar:
#   VITE_NAWI_DATA_SOURCE=api
#   VITE_API_BASE=http://127.0.0.1:8010

npm run dev                    # frontend :5178 + backend :8010
```

Verificación rápida con el backend arriba:

- `curl -s http://127.0.0.1:8010/api/estado/` → `{"estado": "ok"}`.
- <http://localhost:5178/?obj=rw-aurigae> → panel "Curva de brillo" con 7 mediciones.
- <http://localhost:5178/?obj=barnard> → 9 cuadros y el panel de rastro con la validación.
- <http://localhost:5178/?obj=wise-0855> → aviso de señal débil y calidad dudosa.
- Bajar el backend y recargar → "Catálogo no disponible" con el mensaje de conexión (y la barra
  lateral deja de decir "datos del backend").

Build de producción (usa `.env.production`, que apunta al backend local):

```bash
npm run build && npm run preview
# para un backend público:
VITE_API_BASE=https://api.tu-dominio npm run build
```

## Decisiones de honestidad de datos

1. **Nada inventado.** Si el backend no responde, la capa de datos rechaza con un mensaje en
   español y la interfaz lo muestra; no hay caída silenciosa al mock.
2. **`illustrative: false` solo para cuadros que vinieron de una respuesta 200.** El rótulo
   "IMAGEN ILUSTRATIVA" queda exclusivamente para el modo `mock`.
3. **Longitud de onda ausente → "Banda sin dato".** No se completa con valores típicos.
4. **Latido vacío ≠ objeto sin datos.** El detalle separa `estado` (del objeto, según sus
   cuadros) de `latidoEstado` y `motivoLatido` (de la curva). Barnard tiene 9 cuadros y ninguna
   curva: se dice así, sin marcar todo el objeto como "sin datos".
5. **El rastro se muestra con su incertidumbre y su comparación.** Se informa el valor medido, el
   publicado por el catálogo y cuántos cuadros se usaron; no se redondea a favor ni se oculta la
   diferencia.
6. **La calidad se avisa.** `calidad_ok: false` (señal débil, núcleo saturado) se muestra en el
   visor; los recortes dudosos no se presentan como mediciones firmes.
7. **El suavizado se declara.** Con interpolación activa, la interfaz avisa que no son píxeles
   originales.
8. **Sin recálculos en el frontend.** Posiciones, brillos y desplazamientos se muestran tal como
   los publica el backend.

## Pendientes conocidos (no bloquean el PR)

- **Latido solo de RW Aurigae.** R Draconis es variable y todavía no tiene curva (su núcleo está
  saturado en las imágenes de SPHEREx).
- **`revelar` y `conocido` vacíos** en los cinco objetos del backend.
- **Rastro solo de Barnard**; el resto de los objetos no tiene desplazamiento medido.
- **Epsilon Indi B tiene 2 cuadros** (y ambos marcados como dudosos): el visor lo muestra, pero
  no alcanza para una serie temporal útil.
- **Recortes de 58 × 58 px con 6,15″/píxel**: el zoom solo agranda; no hay más detalle real.
- **Sin `LICENSE`**: falta definir licencia y titular en el repo.
- **Backend en `DEBUG=True`** y CORS limitado a los orígenes de desarrollo: para publicar hay que
  configurar el backend real y su CORS.
- **`VITE_API_BASE` en `.env.production` apunta a `127.0.0.1:8010`**: para un deploy público hay
  que sobreescribirlo con la URL real del backend.
````

## Nota para quien abra el PR

1. Abrir https://github.com/Njord-sklodowska/nawi/compare/develop...jorge/frontend
2. Pegar el título y el cuerpo de arriba.
3. Revisar que el diff incluya `README.md`, `.env.example`, `.env.production`, `doc/` y
   `src/data/catalog/`.
4. No hace falta CLI ni token: la creación es desde la web de GitHub.
