"""
Re-estira el contraste de los cuadros ya exportados y registra la visualización.

Por qué existe: los PNG de backend/data/<slug>/frames/ se generaron con un
asinh cuyos parámetros dejaban el fondo casi negro (WISE 0855 usaba solo el
rango 0-27 de 0-255). Los FITS crudos no están versionados (backend/data/raw/
está en .gitignore), así que no se puede re-exportar desde el origen: este
script re-estira el PNG existente.

Honestidad: esto es una transformación de PRESENTACIÓN sobre un PNG que ya
venía estirado. No inventa píxeles ni cambia posiciones; solo reasigna el
rango tonal. Queda registrado en datos.json -> visualizacion para que sea
auditable.

Uso:
    python mejorar_contraste.py <slug>     # un objeto
    python mejorar_contraste.py --todos    # los cinco

Referencia:
    https://docs.astropy.org/en/stable/visualization/normalization.html
"""

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parents[1] / "data"

# Percentiles del estiramiento. Se recortan las colas (ruido y píxeles
# calientes) para que el rango útil ocupe todo el histograma.
P_BAJO = 1.0
P_ALTO = 99.5

METODO = "estiramiento-por-percentiles"
VERSION = 1


def estirar(imagenes, p_bajo=P_BAJO, p_alto=P_ALTO):
    """
    Calcula los límites con TODOS los cuadros del objeto y devuelve, para cada
    imagen, la versión re-escalada a 0-255.

    Los límites se comparten entre fechas a propósito: si cada cuadro se
    estirara por separado, un cambio de brillo real se confundiría con un
    cambio de escala.
    """
    pila = np.concatenate([img.ravel() for img in imagenes])
    pila = pila[np.isfinite(pila)]
    if pila.size == 0:
        raise SystemExit("No hay píxeles válidos para calcular el contraste.")

    lo = float(np.percentile(pila, p_bajo))
    hi = float(np.percentile(pila, p_alto))
    if hi <= lo:
        lo, hi = float(pila.min()), float(pila.max())
    if hi <= lo:
        raise SystemExit("La imagen es uniforme: no hay contraste que estirar.")

    salida = [np.clip((img - lo) / (hi - lo), 0.0, 1.0) for img in imagenes]
    return salida, lo, hi


def procesar(slug):
    carpeta = RAIZ / slug
    frames = sorted((carpeta / "frames").glob("*.png"))
    ruta_json = carpeta / "datos.json"

    if not frames:
        print(f"{slug}: sin cuadros, se omite.")
        return False
    if not ruta_json.exists():
        print(f"{slug}: falta datos.json, se omite.")
        return False

    datos = json.loads(ruta_json.read_text(encoding="utf-8"))
    imagenes = [np.array(Image.open(f)).astype(float) for f in frames]

    antes = [np.percentile(img, 99) for img in imagenes]
    estiradas, lo, hi = estirar(imagenes)
    despues = [np.percentile(img * 255, 99) for img in estiradas]

    for ruta, img in zip(frames, estiradas):
        # Se mantiene el modo 'L' (8 bits) para no cambiar el formato que ya
        # consume el frontend.
        Image.fromarray((img * 255).round().astype(np.uint8), mode="L").save(ruta)

    datos["visualizacion"] = {
        "metodo": METODO,
        "percentiles": {"bajo": P_BAJO, "alto": P_ALTO},
        "rango_original": {"min": round(lo, 2), "max": round(hi, 2)},
        "cuadros_procesados": len(frames),
        "nota": (
            "El PNG ya venía estirado desde el FITS. Este paso reasigna el rango "
            "tonal para presentación: no agrega detalle ni modifica posiciones."
        ),
        "version": VERSION,
    }
    ruta_json.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        f"{slug}: {len(frames)} cuadros | rango {lo:.0f}-{hi:.0f} "
        f"| p99 antes {np.mean(antes):.0f} -> después {np.mean(despues):.0f}"
    )
    return True


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)

    if sys.argv[1] == "--todos":
        slugs = sorted(p.name for p in RAIZ.iterdir() if (p / "datos.json").exists())
    else:
        slugs = [sys.argv[1]]

    hechos = [slug for slug in slugs if procesar(slug)]
    print(f"\nListo: {len(hechos)} objeto(s) procesado(s).")


if __name__ == "__main__":
    main()
