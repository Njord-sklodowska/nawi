
"""
Buscador de observaciones SPHEREx mediante IRSA SIA2.

Consulta las colecciones DR1 y QR3 alrededor de las
coordenadas de un objeto y guarda los resultados.
"""

from pathlib import Path

import astropy.units as u
from astropy.coordinates import SkyCoord
from astroquery.ipac.irsa import Irsa, conf


# Configuración
conf.timeout = 60

COLECCIONES = [
    "spherex_dr1",
    "spherex_qr3",
]

DIRECTORIO_RESULTADOS = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "observaciones"
)


def buscar_observaciones(
    nombre,
    coordenadas,
    radio_arcmin=10,
):
    """
    Busca observaciones SPHEREx alrededor de una posición.

    Parámetros:
        nombre: nombre del objeto.
        coordenadas: SkyCoord con posición ICRS.
        radio_arcmin: radio de búsqueda en minutos de arco.

    Devuelve:
        Diccionario con las tablas encontradas.
    """

    DIRECTORIO_RESULTADOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    resultados = {}

    print("\n" + "=" * 65)
    print(f"BUSCANDO OBSERVACIONES: {nombre}")
    print("=" * 65)

    print(
        f"RA: {coordenadas.ra.deg:.8f} grados"
    )
    print(
        f"DEC: {coordenadas.dec.deg:.8f} grados"
    )
    print(f"Radio: {radio_arcmin} arcmin")

    for coleccion in COLECCIONES:

        print("\n" + "-" * 65)
        print(f"Colección: {coleccion}")
        print("-" * 65)

        try:
            tabla = Irsa.query_sia(
                pos=(
                    coordenadas,
                    radio_arcmin * u.arcmin,
                ),
                collection=coleccion,
            )

            cantidad = len(tabla)

            print(
                f"Observaciones encontradas: {cantidad}"
            )

            if cantidad == 0:
                resultados[coleccion] = tabla
                continue

            # Guardamos la respuesta completa.
            archivo = (
                DIRECTORIO_RESULTADOS
                / f"{nombre}_{coleccion}.ecsv"
            )

            tabla.write(
                archivo,
                format="ascii.ecsv",
                overwrite=True,
            )

            print(f"Resultados guardados en: {archivo}")

            # Mostramos columnas importantes.
            columnas = [
                columna
                for columna in [
                    "obs_id",
                    "s_ra",
                    "s_dec",
                    "t_min",
                    "t_max",
                    "access_url",
                ]
                if columna in tabla.colnames
            ]

            print("\nPrimeras observaciones:")

            if columnas:
                print(tabla[:5][columnas])

            resultados[coleccion] = tabla

        except Exception as error:
            print(
                f"ERROR consultando {coleccion}:"
            )
            print(error)

            resultados[coleccion] = None

    return resultados


def main():

    # Posición de Barnard en J2000.
    barnard = SkyCoord(
        "17h57m48.498470s +04d41m36.113880s",
        frame="icrs",
    )

    buscar_observaciones(
        nombre="barnard",
        coordenadas=barnard,
        radio_arcmin=10,
    )


if __name__ == "__main__":
    main()
