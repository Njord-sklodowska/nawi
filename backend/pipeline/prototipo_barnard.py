
"""
Prototipo integral de Barnard - NAWI.

Flujo:
1. Calcula la posición astrométrica.
2. Localiza el cubo SPHEREx mediante HEALPix.
3. Obtiene las coordenadas del píxel mediante WCS.
4. Lee IMAGE, NHITS y FLAGS.
5. Analiza la calidad espectral.
"""

import argparse
import io

import numpy as np
import requests

from astropy.io import fits
from astropy.wcs import WCS

from astrometria import calcular_posicion
from hips_index import buscar_cubo
from calidad import analizar_calidad, imprimir_informe


# Configuración del cubo SPHEREx DR1
TIMEOUT = 60

ANCHO = 512
ALTO = 512
CANALES = 102
BYTES_POR_PIXEL = 4

# Inicio de los datos de cada extensión FITS.
OFFSETS = {
    "IMAGE": 8640,
    "NHITS": 106971840,
    "FLAGS": 213940800,
}


def obtener_coordenadas_pixel(session, url, ra_deg, dec_deg):
    """Convierte coordenadas celestes en coordenadas de píxel."""

    respuesta = session.get(
        url,
        headers={"Range": "bytes=0-65535"},
        timeout=TIMEOUT,
    )

    if respuesta.status_code != 206:
        raise RuntimeError(
            f"No se pudo obtener el encabezado FITS. "
            f"HTTP {respuesta.status_code}"
        )

    with fits.open(
        io.BytesIO(respuesta.content),
        ignore_missing_end=True,
    ) as hdul:

        header = hdul["IMAGE"].header.copy()

        # Conservar únicamente la información espacial del WCS.
        for clave in [
            "CTYPE3", "CNAME3", "CUNIT3",
            "CRPIX3", "CDELT3", "CRVAL3",
            "PS3_0", "PS3_1", "PS3_2",
            "PV3_3", "PC3_3", "NCHAN",
            "WLMIN", "WLMAX",
        ]:
            header.pop(clave, None)

        header["WCSAXES"] = 2

        wcs = WCS(header).celestial

        x, y = wcs.world_to_pixel_values(
            ra_deg,
            dec_deg,
        )

    x = float(np.asarray(x).item())
    y = float(np.asarray(y).item())

    if not np.isfinite(x) or not np.isfinite(y):
        raise ValueError("El WCS produjo coordenadas no válidas.")

    if not (0 <= round(x) < ANCHO and 0 <= round(y) < ALTO):
        raise ValueError(
            f"El objeto queda fuera del cubo: X={x}, Y={y}"
        )

    return x, y


def leer_extension_pixel(session, url, x, y, extension):
    """Lee los 102 valores de un píxel de una extensión FITS."""

    if extension not in OFFSETS:
        raise ValueError(f"Extensión desconocida: {extension}")

    columna = round(x)
    fila = round(y)

    if not (0 <= columna < ANCHO and 0 <= fila < ALTO):
        raise ValueError("Coordenadas de píxel fuera de los límites.")

    inicio_extension = OFFSETS[extension]

    # IMAGE utiliza float32; NHITS y FLAGS utilizan int32.
    dtype = ">f4" if extension == "IMAGE" else ">i4"

    valores = []

    for canal in range(CANALES):
        indice = (
            canal * ANCHO * ALTO
            + fila * ANCHO
            + columna
        )

        inicio = inicio_extension + indice * BYTES_POR_PIXEL
        fin = inicio + BYTES_POR_PIXEL - 1

        respuesta = session.get(
            url,
            headers={"Range": f"bytes={inicio}-{fin}"},
            timeout=TIMEOUT,
        )

        if respuesta.status_code != 206:
            raise RuntimeError(
                f"Error leyendo {extension}, canal {canal + 1}: "
                f"HTTP {respuesta.status_code}"
            )

        if len(respuesta.content) != BYTES_POR_PIXEL:
            raise RuntimeError(
                f"Lectura incompleta en {extension}, "
                f"canal {canal + 1}."
            )

        valor = np.frombuffer(
            respuesta.content,
            dtype=dtype,
        )[0]

        valores.append(valor.item())

    return np.asarray(valores)


def ejecutar_prototipo(objeto, fecha):
    """Ejecuta el flujo integral de análisis de Barnard."""

    print("=" * 65)
    print("PROTOTIPO INTEGRAL SPHEREx - NAWI")
    print("=" * 65)

    with requests.Session() as session:

        # 1. Astrometría
        print("\n1. CÁLCULO ASTROMÉTRICO")
        print("-" * 50)

        posicion = calcular_posicion(objeto, fecha)

        ra = posicion["ra_deg"]
        dec = posicion["dec_deg"]

        print("Objeto:", posicion["nombre"])
        print("Fecha:", posicion["fecha_observacion"])
        print("RA:", ra)
        print("Dec:", dec)
        print("Fuente:", posicion["fuente"]["estado"])

        # 2. Localización HEALPix y cubo
        print("\n2. LOCALIZACIÓN DEL CUBO SPHEREx")
        print("-" * 50)

        resultado_cubo = buscar_cubo(ra, dec)
        disponibilidad = resultado_cubo["disponibilidad"]

        print("Orden HEALPix:", resultado_cubo["orden_healpix"])
        print("NSIDE:", resultado_cubo["nside"])
        print("Píxel:", resultado_cubo["pixel"])
        print("URL:", resultado_cubo["url"])
        print("HTTP:", disponibilidad["http"])
        print("Disponible:", disponibilidad["disponible"])

        if not disponibilidad["disponible"]:
            raise RuntimeError(
                "El cubo SPHEREx no está disponible."
            )

        url = resultado_cubo["url"]

        # 3. Conversión WCS
        print("\n3. CONVERSIÓN DE COORDENADAS WCS")
        print("-" * 50)

        x, y = obtener_coordenadas_pixel(
            session,
            url,
            ra,
            dec,
        )

        print(f"X: {x:.4f}")
        print(f"Y: {y:.4f}")

        # 4. Lectura de las tres extensiones
        datos = {}

        for extension in ("IMAGE", "NHITS", "FLAGS"):
            print(f"\n4. LEYENDO EXTENSIÓN {extension}")
            print("-" * 50)

            datos[extension] = leer_extension_pixel(
                session,
                url,
                x,
                y,
                extension,
            )

            print(
                f"Canales recuperados: "
                f"{len(datos[extension])}"
            )

        # 5. Análisis de calidad
        print("\n5. ANÁLISIS DE CALIDAD ESPECTRAL")
        print("-" * 50)

        resultado_calidad = analizar_calidad(
            datos["IMAGE"],
            datos["NHITS"],
            datos["FLAGS"],
        )

        imprimir_informe(resultado_calidad)

        # 6. Resultado final
        resumen = resultado_calidad["resumen"]

        print("\n6. RESULTADO DEL PROTOTIPO")
        print("=" * 65)
        print("Objeto:", posicion["nombre"])
        print("Identificador:", objeto)
        print("Fecha:", fecha)
        print("Píxel HEALPix:", resultado_cubo["pixel"])
        print(f"Píxel de imagen: X={x:.4f}, Y={y:.4f}")
        print("Canales espectrales:", CANALES)
        print("Canales disponibles:", resumen["canales_disponibles"])
        print("Canales sin datos:", resumen["canales_sin_datos"])
        print("Canales inconsistentes:", resumen["canales_inconsistentes"])

        if resumen["canales_inconsistentes"] == 0:
            print("\nINTEGRACIÓN FINALIZADA CORRECTAMENTE.")
        else:
            print("\nATENCIÓN: SE DETECTARON INCONSISTENCIAS.")

        print("=" * 65)

        return {
            "objeto": posicion,
            "cubo": resultado_cubo,
            "pixel": {
                "x": x,
                "y": y,
            },
            "espectro": datos["IMAGE"],
            "nhits": datos["NHITS"],
            "flags": datos["FLAGS"],
            "calidad": resultado_calidad,
        }


def main():
    parser = argparse.ArgumentParser(
        description="Ejecuta el prototipo integral SPHEREx de NAWI."
    )

    parser.add_argument(
        "--objeto",
        default="barnard",
        help="Identificador del objeto del catálogo.",
    )

    parser.add_argument(
        "--fecha",
        default="2026-11-15",
        help="Fecha de observación YYYY-MM-DD.",
    )

    args = parser.parse_args()

    try:
        ejecutar_prototipo(
            args.objeto,
            args.fecha,
        )

    except Exception as error:
        print("\nERROR EN EL PROTOTIPO:")
        print(error)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
