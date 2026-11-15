# Contrato de API propuesto — frontend ↔ backend (Nawi)

**Estado:** propuesta del frontend. Los endpoints todavía no existen
(`backend/api/urls.py` y `backend/api/views.py` están vacíos).

**Objetivo:** que el frontend deje de usar la fuente `mock` y consuma datos reales
sin cambiar la vista. Hoy la capa `src/data/catalog` ya tiene el contrato
`listObjects()` / `listFrames(slug)`; solo falta una fuente `api.source.js` que
haga fetch.

---

## 1. `GET /api/objetos`

Devuelve la lista de objetos. Puede ser el `backend/pipeline/objetos.json` tal
como está, envuelto o no.

```json
[
  {
    "slug": "barnard",
    "nombre": "Estrella de Barnard",
    "tipo": "estrella_movimiento_propio",
    "rol": "principal",
    "ra_deg": 269.45207696,
    "dec_deg": 4.69336497,
    "epoca": "J2000",
    "pm_ra_cosdec_mas_yr": -801.551,
    "pm_dec_mas_yr": 10362.394,
    "fov_arcmin": 4
  }
]
```

Los cinco `slug` acordados: `barnard`, `wise-0855`, `epsilon-indi-b`,
`rw-aurigae`, `r-draconis`.

Notas:
- `slug` es el identificador que viaja en la URL del frontend (`?obj=`); no debe
  cambiar sin avisar.
- El frontend **no** calcula posiciones: si el campo se centra propagando el
  movimiento propio, esa posición debe venir calculada por el backend.
- `tipo` y `rol` los usa la interfaz solo para mostrar texto; valores nuevos no
  rompen nada.

---

## 2. `GET /api/objetos/{slug}/cuadros`

Devuelve la serie temporal de cuadros ya alineados y listos para mostrar.

```json
{
  "objeto": "barnard",
  "cuadros": [
    {
      "id": "barnard-2026W12",
      "fecha": "2026-03-21",
      "mjd": 61130.5,
      "banda": "SPHEREx-D6",
      "lambda_um": 1.02,
      "url": "/media/barnard/barnard-2026W12.webp",
      "ancho": 400,
      "alto": 400,
      "escala_arcsec_px": 6.2,
      "illustrative": false,
      "calidad": { "nhits_min": 1, "flags": 0 }
    }
  ]
}
```

Requisitos que el frontend necesita:

| Campo | Para qué |
|---|---|
| `fecha` (ISO 8601) | Se muestra en el visor y en la línea de tiempo |
| `banda` / `lambda_um` | Se muestra por cuadro (la curva de brillo mezcla longitudes de onda si falta) |
| `url` | Imagen **PNG o WebP**, no FITS: el navegador no lee FITS |
| `illustrative` | `false` habilita el rótulo "DATOS DEL BACKEND"; con `true` se sigue marcando como ilustrativo |
| `calidad` | Opcional; permite avisar de cuadros contaminados |

Pendiente de decidir con backend:

1. **Dónde viven los FITS.** El `.gitignore` de `cecilia/backend` excluye `*.fits`
   y `backend/data/raw/`, así que las imágenes derivadas (WebP/PNG) y el JSON
   tienen que servirse aparte o precalcularse en el repo.
2. **Tamaño y formato** de los cuadros (recomendado: WebP, 400–600 px de lado).
3. **CORS** para desarrollo local (`django-cors-headers` ya está en
   `requirements.txt`).

---

## 3. Errores esperados

| Caso | Respuesta sugerida |
|---|---|
| Slug inexistente | `404` con `{ "error": "objeto desconocido" }` |
| Objeto sin observaciones | `200` con `cuadros: []` (el frontend muestra "sin datos") |
| Backend caído | El frontend cae al video de respaldo de la demo |

---

## 4. Cómo se activa en el frontend

```bash
VITE_NAWI_DATA_SOURCE=api npm run dev
```

Hoy esa variable solo cambia los rótulos a "Catálogo sin conectar", porque
`api.source.js` rechaza a propósito: no hay endpoints. Cuando existan, se
implementan `listObjects()` y `listFrames()` con este contrato y la vista no se
toca.
