
import struct
import requests
import numpy as np

# Cubo identificado en la inspección FITS
URL = (
    "https://irsa.ipac.caltech.edu/ibe/data/spherex/dr1/"
    "hips5_cube/hips_20261026/Norder5/Dir0/Npix7945_cube.fits"
)

# Coordenadas del píxel de Barnard obtenidas mediante WCS
X = 98
Y = 102

ANCHO = 512
ALTO = 512
CANALES = 102
BYTES_POR_PIXEL = 4

# Inicio de los datos de cada extensión FITS
OFFSETS = {
    "IMAGE": 8640,
    "NHITS": 106971840,
    "FLAGS": 213940800,
}


def leer_valor(session, extension, canal):
    inicio = OFFSETS[extension]

    indice = canal * ANCHO * ALTO + Y * ANCHO + X
    offset = inicio + indice * BYTES_POR_PIXEL

    headers = {
        "Range": f"bytes={offset}-{offset + 3}"
    }

    respuesta = session.get(
        URL,
        headers=headers,
        timeout=30
    )

    if respuesta.status_code != 206:
        raise RuntimeError(
            f"Error HTTP {respuesta.status_code} "
            f"al leer {extension}, canal {canal + 1}"
        )

    if len(respuesta.content) != 4:
        raise RuntimeError(
            f"Se esperaban 4 bytes y llegaron "
            f"{len(respuesta.content)}"
        )

    if extension == "IMAGE":
        return struct.unpack(">f", respuesta.content)[0]

    return struct.unpack(">i", respuesta.content)[0]


def main():
    print("=" * 65)
    print("CONTROL DE CALIDAD ESPECTRAL SPHEREx - NAWI")
    print("=" * 65)

    print(f"Píxel: X={X}, Y={Y}")
    print(f"Canales: {CANALES}")

    resultados = {
        "IMAGE": [],
        "NHITS": [],
        "FLAGS": [],
    }

    with requests.Session() as session:
        for extension in resultados:
            print(f"\nLeyendo extensión {extension}...")

            for canal in range(CANALES):
                valor = leer_valor(
                    session,
                    extension,
                    canal
                )
                resultados[extension].append(valor)

    image = np.array(resultados["IMAGE"], dtype=float)
    nhits = np.array(resultados["NHITS"], dtype=int)
    flags = np.array(resultados["FLAGS"], dtype=int)

    print("\n" + "=" * 65)
    print("RESUMEN DE CALIDAD")
    print("=" * 65)

    print(f"Valores espectrales finitos: {np.isfinite(image).sum()}")
    print(f"Valores espectrales no finitos: {np.count_nonzero(~np.isfinite(image))}")

    print(f"\nNHITS mínimo: {nhits.min()}")
    print(f"NHITS máximo: {nhits.max()}")
    print(f"Canales con NHITS = 0: {np.count_nonzero(nhits == 0)}")

    print(f"\nFLAGS distintos: {np.unique(flags)}")

    print("\n" + "=" * 65)
    print("DETALLE POR CANAL")
    print("=" * 65)

    print("CANAL | IMAGE (MJy/sr) | NHITS | FLAGS")
    print("-" * 65)

    for i in range(CANALES):
        print(
            f"{i + 1:5} | "
            f"{image[i]:14.6f} | "
            f"{nhits[i]:5} | "
            f"{flags[i]}"
        )

    print("\nCONTROL DE CALIDAD FINALIZADO")


if __name__ == "__main__":
    main()
