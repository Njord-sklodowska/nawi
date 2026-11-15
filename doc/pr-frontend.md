# Pull Request — frontend Nawi (`jorge/frontend` → `develop`)

- **Rama**: `jorge/frontend` (pusheada en `origin`)
- **Destino**: `develop` (`5aaf9e1`)
- **Remoto**: `git@github.com:Njord-sklodowska/nawi.git`
- **Comparación (abrir el PR acá)**:
  https://github.com/Njord-sklodowska/nawi/compare/develop...jorge/frontend

> **La creación del PR es manual.** En este entorno no hay `gh` CLI ni token de GitHub, así
> que no se puede abrir por API: hay que entrar al enlace de comparación y pegar título y
> cuerpo de abajo.
>
> Antes de abrirlo: `src/App.vue` y `src/styles.css` tienen cambios sin commitear (los está
> cerrando P5). Esos archivos tienen que quedar commiteados y pusheados; si no, la vista de
> comparación no los mostrará.

## Título propuesto

```text
Frontend Nawi: visor de observaciones SPHEREx con datos reales y capa de datos intercambiable
```

## Cuerpo (pegar tal cual)

````markdown
## Qué trae esta rama

- **Visor de observaciones reales**: catálogo de 5 objetos del backend y serie temporal de
  recortes PNG (58×58 px, 6,15″/píxel) con línea de tiempo, reproducción automática y
  comparación "antes y después".
- **Capa de datos intercambiable** (`src/data/catalog/`): `mock` por defecto y `api` real
  activable con `VITE_NAWI_DATA_SOURCE=api`. La vista no sabe de dónde vienen los datos.
- **Ficha por objeto**: coordenadas publicadas por el backend, recorte técnico y, cuando
  existe, panel de **latido** (curva de brillo). Hoy hay curva real solo para RW Aurigae
  (7 puntos en Jy).
- **Errores explícitos en español**: backend caído, 404, respuesta no JSON o formato
  inesperado se muestran en pantalla; nunca se rellena con datos falsos.
- **Tema oscuro y claro** (oscuro por defecto, preferencia recordada en `localStorage`).
- **Documentación**: `README.md`, `.env.example` y este archivo.

## Cómo probarlo

```bash
# dependencias
npm install
python3.12 -m venv backend/.venv
backend/.venv/bin/pip install -r backend/requirements.txt

# datos reales
cp .env.example .env.local
#   VITE_NAWI_DATA_SOURCE=api
#   VITE_API_BASE=http://127.0.0.1:8010

npm run dev          # frontend en :5178 y backend en :8010
```

Verificación rápida:
- `curl -s http://127.0.0.1:8010/api/estado/` → `{"estado": "ok"}`.
- <http://localhost:5178/?obj=rw-aurigae> → se ve el panel de latido con 7 puntos.
- <http://localhost:5178/?obj=barnard> → 9 cuadros y desplazamiento visible entre fechas.
- Bajar el backend y recargar: tiene que aparecer un mensaje de error legible, no una
  pantalla vacía.

## Decisiones de honestidad de datos

1. **Nada inventado en la capa de datos.** Si el backend no responde, las funciones rechazan con
   un mensaje en español y la UI lo muestra. No hay fallback silencioso a datos de demo.
2. **`illustrative: false` solo para cuadros que vinieron de una respuesta 200.** El rótulo
   "IMAGEN ILUSTRATIVA" queda exclusivamente para el modo `mock`.
3. **Longitud de onda ausente = "Banda sin dato".** No se completa con valores tipicos.
4. **Latido vacío = `estado: "sin_datos"` y `latido: []`.** Se descartan los puntos sin fecha o
   sin brillo, y los valores faltantes quedan en `null` (nunca en 0).
5. **Sin recálculos en el frontend.** Distancias, posiciones y brillos se muestran tal como los
   publica el backend; el frontend no los deriva.
6. **Calidad dudosa visible.** Si el backend marca `calidad_ok: false`, el visor lo avisa.
7. **Fechas en UTC sin corrimientos.** La fecha del cuadro se corta del ISO del backend para
   no mover el día según la zona horaria del navegador.

## Pendientes conocidos (no bloquean el PR)

- **Latido**: solo RW Aurigae tiene curva; R Draconis (variable) todavía no. El backend ya
  expone el campo y la UI está lista.
- **`estado` del detalle**: si el latido viene vacío, el detalle responde `estado: "sin_datos"`
  aunque el objeto tenga cuadros (caso Barnard, 9 cuadros). Conviene que la UI use ese campo
  solo para la sección de latido, no para ocultar el visor.
- **Longitud de onda**: falta en WISE 0855, Epsilon Indi B y R Draconis → se muestra
  "Banda sin dato".
- **Calidad**: WISE 0855 y Epsilon Indi B tienen todos sus cuadros marcados como dudosos.
- **`rastro`, `revelar` y `conocido`** del backend todavía vienen vacíos.
- **`doc/contrato-api.md`** es la propuesta original y quedó desactualizada: la API ya existe,
  el contrato vigente es la tabla de endpoints del `README.md`.
- **Licencia**: el repo todavía no define `LICENSE` ni titular.
````

## Nota para quien abra el PR

1. Abrir https://github.com/Njord-sklodowska/nawi/compare/develop...jorge/frontend
2. Pegar el título y el cuerpo de arriba.
3. Revisar que `README.md`, `.env.example` y `doc/pr-frontend.md` estén incluidos en el diff
   (si no aparecen, faltó commitearlos en la rama).
4. No hace falta CLI ni token: la creación es desde la web de GitHub.
