# Nawi: backend simple (para Sergio)

Versión mínima del backend. Si algo crece, se separa después.

> Lo marcado con **(verificar)** se confirma en la Fase 1 leyendo la documentación o el notebook de tutorial.

---

## 1. Estructura

```
nawi/
├── README.md
├── .gitignore
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/              # settings.py y urls.py
│   ├── api/                 # una sola app: views.py y urls.py
│   ├── pipeline/
│   │   ├── objetos.json     # los 5 objetos
│   │   └── precalcular.py   # un solo script
│   └── data/
│       ├── ejemplo.json     # muestra para Jorge
│       └── <objeto>/
│           ├── frames/      # cuadros alineados
│           └── datos.json   # todo lo del objeto
└── frontend/
```

**Crear la estructura**
```bash
mkdir -p nawi/{frontend,backend/{config,api,pipeline,data}}
cd nawi
touch README.md .gitignore backend/requirements.txt
touch backend/pipeline/{objetos.json,precalcular.py} backend/data/ejemplo.json
```

**.gitignore**
```
.env
.venv/
__pycache__/
node_modules/
*.fits
backend/data/raw/
```

**requirements.txt**
```
django
djangorestframework
django-cors-headers
astropy
numpy
reproject
photutils
astroquery
pillow
```

---

## 2. API (tres rutas)

| Ruta | Devuelve |
|---|---|
| `GET /api/objetos/` | Lista de los 5 objetos (slug, nombre, tipo, cantidad de cuadros) |
| `GET /api/objetos/<slug>/` | El `datos.json` completo del objeto |
| `/media/<slug>/frames/<n>.png` | Cada cuadro (se sirve `data/` como archivos estáticos) |

Habilitar CORS para el frontend en desarrollo (Vite usa `http://localhost:5173` por defecto).

---

## 3. Formato de `datos.json`

Un archivo por objeto. Jorge lee lo que necesite.

```json
{
  "slug": "barnard",
  "nombre": "Estrella de Barnard",
  "tipo": "estrella_movimiento_propio",
  "centro": {"ra_deg": null, "dec_deg": null},
  "fov_arcmin": 4,
  "estado": "ok",
  "motivo": "",
  "cuadros": [
    {"fecha": "2025-06-01T00:00:00Z", "url": "/media/barnard/frames/0000.png",
     "longitud_onda_um": null, "calidad_ok": true}
  ],
  "latido": [
    {"fecha": "2025-06-01T00:00:00Z", "flujo": null, "error": null, "longitud_onda_um": null}
  ],
  "rastro": {
    "desplazamiento_arcsec": null,
    "direccion_deg": null,
    "incertidumbre_arcsec": null,
    "pm_publicado_arcsec_yr": null
  },
  "revelar": {"snr_vs_cuadros": []},
  "conocido": {"estado": "sin_datos", "coincidencias": []}
}
```

**Reglas**
- Los valores `null` se completan con datos reales. No inventar números.
- Si un objeto no se detecta o no tiene datos, `estado` es `"sin_deteccion"` o `"sin_datos"` y `motivo` lo explica. No fallar en silencio.
- `conocido.estado`: `conocido`, `candidato` o `sin_datos`. **`candidato` significa "no coincide con lo catalogado", nunca "descubrimiento".**
- Fechas en ISO 8601 (UTC), coordenadas en grados, distancias angulares en segundos de arco.

---

## 4. Objetos (`pipeline/objetos.json`)

```json
[
  {
    "slug": "barnard",
    "nombre": "Estrella de Barnard",
    "tipo": "estrella_movimiento_propio",
    "rol": "principal",
    "ra_deg": null, "dec_deg": null, "epoca": null,
    "pm_ra_cosdec_mas_yr": null, "pm_dec_mas_yr": null,
    "fov_arcmin": 4
  }
]
```

- Completar posición, época y movimiento propio con **SIMBAD o Gaia DR3** en la Fase 1.
- **WISE 0855:** las coordenadas del enunciado son 08h55m10.831s, -7d14m42.53s, pero hay que confirmar su época de referencia **(verificar)**. Se mueve unos 8,1″ por año.
- Los 5 objetos: `barnard`, `wise-0855`, `epsilon-indi-b`, `rw-aurigae`, `r-draconis`.

---

## 5. Pipeline (`pipeline/precalcular.py`)

Comando previsto: `python pipeline/precalcular.py barnard`

1. **Leer** el objeto desde `objetos.json`.
2. **Propagar la posición** a la fecha media de las observaciones con astropy (movimiento propio). Eso fija el centro del campo.
3. **Buscar observaciones** en IRSA por posición (servicio SIA2, colección `spherex_qr`; QR2 es la versión por defecto).
4. **Bajar recortes** del tamaño del campo con el servicio de recortes de IRSA **(verificar parámetros)**. Guardar en `data/raw/` y reutilizar si ya existen.
5. **Leer los FITS**: imagen, WCS y máscaras de calidad **(verificar nombres de extensiones en la guía de productos)**.
6. **Alinear** todos a una misma grilla (`reproject`).
7. **Exportar cuadros** a PNG con una escala de brillo consistente entre fechas.
8. **Latido** (Ceci): fotometría en la posición propagada de cada fecha, guardando la longitud de onda.
9. **Rastro** (Ceci): centroides por cuadro y ajuste lineal contra el tiempo, comparado con el movimiento propio publicado.
10. **Revelar**: apilar desplazando según el movimiento conocido y calcular cómo mejora la relación señal-ruido.
11. **Conocido** (Ceci): cruce con SIMBAD y Gaia.
12. **Escribir** `datos.json` y `frames/`.

Cada paso guarda caché. Si algo falla, se registra en `estado` y `motivo`.

---

## 6. Validación con Barnard

Un script corto, sin framework de tests: carga los cuadros alineados de Barnard y comprueba dos cosas.

1. La posición medida coincide con la propagada, dentro de unos pocos píxeles (el píxel de SPHEREx mide unos 6,2″; la tolerancia se define en la Fase 1).
2. El movimiento medido es consistente con el valor publicado.

Si el código generado con IA no pasa esto, hay un error de alineación, unidades o del signo del movimiento en ascensión recta.

---

## 7. Cómo trabajamos

- **Ramas:** `main` (estable), `sergio/pipeline`, `ceci/analisis`, `jorge/frontend`.
- Integrar cada 2 horas o al cerrar cada compuerta.
- No subir `.env`, FITS en bruto ni claves.
- Los cambios al formato de `datos.json` se avisan antes.
- El código generado con IA se revisa antes de integrar y se declara en el README.

---

## 8. Hitos del backend

| Cuándo | Hito | Quién |
|---|---|---|
| Sáb 15:00 | Repo creado con estructura, `.gitignore` y una rama por persona | Sergio |
| Sáb 16:00 | **`ejemplo.json` publicado** para que Jorge arranque | Ceci + Sergio |
| Sáb 16:30 | **Compuerta 1:** recorte real de Barnard abierto desde Python | Sergio |
| Sáb 18:00 | **Compuerta 2:** Barnard alineada en al menos 2 fechas, con posición coherente | Sergio + Ceci |
| Sáb 22:00 | `/api/objetos/` y `/api/objetos/barnard/` con datos reales | Sergio |
| Dom 02:00 | Los 5 objetos precalculados, con `latido` | Sergio + Ceci |
| Dom 10:00 | **Compuerta 3:** `revelar` y `rastro` validados con Barnard | Sergio + Ceci |
| Dom 14:00 | **Congelamiento de código** | Todos |

---

## 9. Fuentes

| Qué | Link |
|---|---|
| SPHEREx en IRSA | https://irsa.ipac.caltech.edu/Missions/spherex.html |
| Acceso a datos (SIA2, colecciones, Data Explorer) | https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-access |
| Productos de datos (formato FITS) | https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-products |
| Recortes | https://irsa.ipac.caltech.edu/data/SPHEREx/docs/cutout_tool.html |
| Tutoriales en Jupyter | https://caltech-ipac.github.io/irsa-tutorials/spherex/ |
| Gaia DR3 | https://archive.stsci.edu/missions-and-data/gaia |
| SIMBAD | https://simbad.u-strasbg.fr/simbad/ |
| astroquery | https://astroquery.readthedocs.io/en/stable/ |
