
"""
Prueba de lectura espectral SPHEREx para NAWI.

Integra:
- Astrometría calculada para una fecha.
- Localización del cubo mediante HEALPix.
- Conversión de coordenadas celestes a píxeles mediante WCS.
- Lectura de los 102 canales espectrales.
- Inspección básica de los valores obtenidos.
"""

import io

import requests
import numpy as np

from astropy.io import fits
from astropy.wcs import WCS

from astrometria import calcular_posicion
from hips_index import buscar_cubo, calcular_pixel


OBJETO = "barnard"
FECHA_OBSERVACION = "2026-11-15"

TIMEOUT = 60

INICIO_IMAGEN = 8640
ANCHO = 512
ALTO = 512
CANALES = 102
BYTES_POR_PIXEL = 4


def obtener_coordenadas_pixel(url, ra_deg, dec_deg):
    """
    Obtiene el encabezado FITS y convierte coordenadas celestes
    en coordenadas de píxel dentro de la imagen.
    """

    respuesta = requests.get(
        url,
        headers={"Range": "bytes=0-65535"},
        timeout=TIMEOUT,
    )

    if respuesta.status_code != 206:
        raise RuntimeError(
            "No se pudo descargar el encabezado FITS."
        )

    with fits.open(
        io.BytesIO(respuesta.content),
        ignore_missing_end=True,
    ) as hdul:

        header = hdul["IMAGE"].header.copy()

        # Eliminar el eje espectral para construir el WCS espacial.
        for clave in [
            "CTYPE3", "CNAME3", "CUNIT3",
            "CRPIX3", "CDELT3", "CRVAL3",
            "PS3_0", "PS3_1", "PS3_2",
            "PV3_3", "PC3_3", "NCHAN",
            "WLMIN", "WLMAX",
        ]:
            if clave in header:
                del header[clave]

        header["WCSAXES"] = 2

        wcs = WCS(header).celestial

        x, y = wcs.world_to_pixel_values(
            ra_deg,
            dec_deg,
        )

        return float(np.asarray(x).item()), float(np.asarray(y).item())


def leer_pixel_espectral(url, x, y):
    """
    Lee los 102 valores espectrales de un píxel.

    Cada plano contiene 512 x 512 valores float32.
    """

    columna = round(x)
    fila = round(y)

    if not (0 <= columna < ANCHO and 0 <= fila < ALTO):
        raise ValueError(
            "El píxel está fuera de los límites de la imagen."
        )

    print("\nLEYENDO LOS 102 CANALES")
    print("=" * 50)

    valores = []

    for canal in range(CANALES):

        indice = (
            canal * ANCHO * ALTO
            + fila * ANCHO
            + columna
        )

        inicio = INICIO_IMAGEN + indice * BYTES_POR_PIXEL
        fin = inicio + BYTES_POR_PIXEL - 1

        respuesta = requests.get(
            url,
            headers={"Range": f"bytes={inicio}-{fin}"},
            timeout=TIMEOUT,
        )

        if respuesta.status_code != 206:
            raise RuntimeError(
                f"Error leyendo canal {canal + 1}: "
                f"HTTP {respuesta.status_code}"
            )

        if len(respuesta.content) != BYTES_POR_PIXEL:
            raise RuntimeError(
                f"Lectura incompleta en canal {canal + 1}."
            )

        # FITS almacena los números en big-endian.
        valor = np.frombuffer(
            respuesta.content,
            dtype=">f4",
        )[0]

        valores.append(float(valor))

    return valores


def main():

    print("=" * 60)
    print("LECTURA ESPECTRAL SPHEREx - NAWI")
    print("=" * 60)

    # 1. Obtener las coordenadas actualizadas.
    posicion = calcular_posicion(
        OBJETO,
        FECHA_OBSERVACION,
    )

    ra = posicion["ra_deg"]
    dec = posicion["dec_deg"]

    print("\nDATOS ASTROMÉTRICOS")
    print("-" * 45)
    print("Objeto:", posicion["nombre"])
    print("Fecha:", posicion["fecha_observacion"])
    print("RA:", ra)
    print("Dec:", dec)
    print("Fuente:", posicion["fuente"]["estado"])

    # 2. Localizar el cubo SPHEREx.
    resultado = buscar_cubo(ra, dec)

    if not resultado["disponibilidad"]["disponible"]:
        raise RuntimeError(
            "El cubo SPHEREx no está disponible."
        )

    pixel_healpix = calcular_pixel(ra, dec)

    print("\nLOCALIZACIÓN HEALPix")
    print("-" * 45)
    print("Píxel:", pixel_healpix)

    print("\nCUBO SPHEREx")
    print("-" * 45)
    print("URL:", resultado["url"])
    print(
        "Tamaño:",
        resultado["disponibilidad"].get("tamano_mb", "No informado"),
    )

    # 3. Convertir las coordenadas celestes en píxeles.
    x, y = obtener_coordenadas_pixel(
        resultado["url"],
        ra,
        dec,
    )

    print("\nPOSICIÓN DENTRO DE LA IMAGEN")
    print("-" * 45)
    print(f"X: {x:.4f}")
    print(f"Y: {y:.4f}")

    # 4. Leer los valores de los 102 canales.
    valores = leer_pixel_espectral(
        resultado["url"],
        x,
        y,
    )

    arreglo = np.asarray(valores)
    validos = np.isfinite(arreglo)

    canales_no_finitos = [
        indice + 1
        for indice, valor in enumerate(valores)
        if not np.isfinite(valor)
    ]

    print("\nCANALES SIN VALORES FINITOS")
    print("=" * 50)
    print("Planos:", canales_no_finitos)

    print("\nRESULTADO ESPECTRAL")
    print("=" * 50)
    print("Canales leídos:", len(valores))

    for indice, valor in enumerate(valores[:10], start=1):
        print(f"Canal {indice:3}: {valor:.8g} MJy/sr")

    print("...")

    print(
        f"Canal 102: {valores[-1]:.8g} MJy/sr"
    )

    print("\nESTADÍSTICAS")
    print("=" * 50)
    print("Valores finitos:", int(validos.sum()))
    print("Valores no finitos:", int((~validos).sum()))

    if validos.any():
        print(
            "Mínimo:",
            float(np.min(arreglo[validos])),
        )

        print(
            "Máximo:",
            float(np.max(arreglo[validos])),
        )

        print(
            "Promedio:",
            float(np.mean(arreglo[validos])),
        )

    print("\nLECTURA ESPECTRAL FINALIZADA")


if __name__ == "__main__":
    main()
