
"""
Genera el catálogo espectral de SPHEREx DR1.

Lee las extensiones SPECTRAL_CHANNELS y WCS-WAVE
mediante HTTP Range, sin descargar el cubo completo.
"""

import io
import json
from pathlib import Path

import requests
from astropy.io import fits

from hips_index import buscar_cubo


# Ubicación de las tablas confirmada en el FITS inspeccionado.
INICIO_TABLAS = 320898240
FIN_TABLAS = 320909759

DIRECTORIO_PROYECTO = Path(__file__).resolve().parents[1]
ARCHIVO_SALIDA = (
    DIRECTORIO_PROYECTO
    / "data"
    / "catalogo_espectral.json"
)


def descargar_tablas(url):
    """Descarga únicamente el bloque FITS que contiene las tablas."""

    respuesta = requests.get(
        url,
        headers={
            "Range": f"bytes={INICIO_TABLAS}-{FIN_TABLAS}"
        },
        timeout=60
    )

    if respuesta.status_code != 206:
        raise RuntimeError(
            f"Error HTTP al descargar tablas: {respuesta.status_code}"
        )

    contenido = respuesta.content

    if len(contenido) != FIN_TABLAS - INICIO_TABLAS + 1:
        raise RuntimeError("El tamaño recibido no coincide con lo esperado.")

    # Reconstruimos un FITS mínimo con PRIMARY + las dos tablas.
    buffer = io.BytesIO()
    fits.HDUList([fits.PrimaryHDU()]).writeto(buffer)

    contenido_fits = buffer.getvalue() + contenido

    with fits.open(io.BytesIO(contenido_fits)) as hdul:
        if "SPECTRAL_CHANNELS" not in hdul:
            raise RuntimeError("No se encontró SPECTRAL_CHANNELS.")

        if "WCS-WAVE" not in hdul:
            raise RuntimeError("No se encontró WCS-WAVE.")

        tabla = hdul["SPECTRAL_CHANNELS"].data
        tabla_wcs = hdul["WCS-WAVE"].data

        if len(tabla) != 102:
            raise RuntimeError(
                f"Se esperaban 102 canales; se encontraron {len(tabla)}."
            )

        canales = []

        for indice, fila in enumerate(tabla):

            canal = {
                "plano": indice + 1,
                "detector": int(fila["DETECTOR"]),
                "subcanal": int(fila["SUBCHAN"]),
                "longitud_onda_um": float(fila["WAVELENGTH"]),
                "longitud_onda_min_um": float(fila["WL_MIN"]),
                "longitud_onda_max_um": float(fila["WL_MAX"]),
                "resolucion_espectral": float(fila["R"]),
                "desviacion_resolucion": float(fila["R_STD"]),
                "ancho_banda_um": float(fila["BANDWIDTH"]),
            }

            canales.append(canal)

        # Comprobamos que la tabla WCS-WAVE coincida con
        # las longitudes de onda de SPECTRAL_CHANNELS.
        longitudes_wcs = tabla_wcs["WAVELENGTHS"][0].reshape(-1)

        if len(longitudes_wcs) != len(canales):
            raise RuntimeError(
                "La cantidad de longitudes de onda no coincide."
            )

        for canal, longitud_wcs in zip(canales, longitudes_wcs):
            if abs(
                canal["longitud_onda_um"] - float(longitud_wcs)
            ) > 0.0001:
                raise RuntimeError(
                    "Las tablas espectrales y WCS-WAVE no coinciden."
                )

    return canales


def crear_catalogo(url):
    """Genera y guarda el catálogo espectral."""

    canales = descargar_tablas(url)

    catalogo = {
        "producto": "SPHEREx DR1 All-Sky Cube",
        "unidad_longitud_onda": "um",
        "cantidad_canales": len(canales),
        "longitud_onda_min_um": min(
            c["longitud_onda_um"] for c in canales
        ),
        "longitud_onda_max_um": max(
            c["longitud_onda_um"] for c in canales
        ),
        "unidad_intensidad": "MJy/sr",
        "canales": canales,
    }

    ARCHIVO_SALIDA.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as archivo:
        json.dump(
            catalogo,
            archivo,
            indent=4,
            ensure_ascii=False
        )

    print("\nCATÁLOGO ESPECTRAL GENERADO")
    print("=" * 50)
    print(f"Canales: {catalogo['cantidad_canales']}")
    print(f"Desde: {catalogo['longitud_onda_min_um']} µm")
    print(f"Hasta: {catalogo['longitud_onda_max_um']} µm")
    print(f"Archivo: {ARCHIVO_SALIDA}")

    print("\nPrimeros cinco canales:")

    for canal in canales[:5]:
        print(
            f"Plano {canal['plano']:3} | "
            f"Detector {canal['detector']} | "
            f"Subcanal {canal['subcanal']:2} | "
            f"{canal['longitud_onda_um']:.3f} µm"
        )

    print("\nÚltimos cinco canales:")

    for canal in canales[-5:]:
        print(
            f"Plano {canal['plano']:3} | "
            f"{canal['longitud_onda_um']:.3f} µm"
        )


if __name__ == "__main__":

    resultado = buscar_cubo(
        269.45207696,
        4.69336497
    )

    if not resultado["disponibilidad"]["disponible"]:
        raise RuntimeError("El cubo SPHEREx no está disponible.")

    crear_catalogo(resultado["url"])
