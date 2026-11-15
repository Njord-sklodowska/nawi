
"""
Índice espacial para los cubos HiPS de SPHEREx DR1.

Calcula el píxel HEALPix correspondiente a una posición celeste
y construye la URL del cubo FITS asociado.

No descarga el cubo: solamente comprueba su disponibilidad.
"""

import argparse
import sys

import astropy.units as u
import requests
from astropy_healpix import HEALPix


# Configuración oficial del cubo SPHEREx DR1
ORDEN_HEALPIX = 5
NSIDE = 2 ** ORDEN_HEALPIX

BASE_URL = (
    "https://irsa.ipac.caltech.edu/ibe/data/spherex/dr1/"
    "hips5_cube/hips_20261026"
)

TIMEOUT = 30


def calcular_pixel(ra_deg: float, dec_deg: float) -> int:
    """Calcula el índice HEALPix NESTED para una coordenada celeste."""

    if not 0 <= ra_deg < 360:
        raise ValueError("La ascensión recta (RA) debe estar entre 0 y 360 grados.")

    if not -90 <= dec_deg <= 90:
        raise ValueError("La declinación (Dec) debe estar entre -90 y 90 grados.")

    healpix = HEALPix(
        nside=NSIDE,
        order="nested"
    )

    pixel = healpix.lonlat_to_healpix(
        ra_deg * u.deg,
        dec_deg * u.deg
    )

    return int(pixel)


def construir_url_cubo(pixel: int) -> str:
    """Construye la URL del archivo FITS correspondiente al píxel."""

    cantidad_pixeles = 12 * NSIDE**2

    if not 0 <= pixel < cantidad_pixeles:
        raise ValueError(
            f"Píxel inválido: debe estar entre 0 y {cantidad_pixeles - 1}."
        )

    directorio = (pixel // 10000) * 10000

    return (
        f"{BASE_URL}/Norder{ORDEN_HEALPIX}/"
        f"Dir{directorio}/Npix{pixel}_cube.fits"
    )


def consultar_disponibilidad(url: str) -> dict:
    """Comprueba si el archivo remoto está disponible sin descargarlo."""

    try:
        respuesta = requests.head(
            url,
            timeout=TIMEOUT,
            allow_redirects=True
        )

        resultado = {
            "disponible": respuesta.status_code == 200,
            "http": respuesta.status_code,
            "url": url,
            "tamano_bytes": None,
        }

        longitud = respuesta.headers.get("Content-Length")

        if longitud:
            resultado["tamano_bytes"] = int(longitud)

        return resultado

    except requests.RequestException as error:
        return {
            "disponible": False,
            "http": None,
            "url": url,
            "error": str(error),
            "tamano_bytes": None,
        }


def buscar_cubo(ra_deg: float, dec_deg: float) -> dict:
    """Ejecuta el proceso completo de localización del cubo."""

    pixel = calcular_pixel(ra_deg, dec_deg)
    url = construir_url_cubo(pixel)
    disponibilidad = consultar_disponibilidad(url)

    return {
        "ra_deg": ra_deg,
        "dec_deg": dec_deg,
        "orden_healpix": ORDEN_HEALPIX,
        "nside": NSIDE,
        "pixel": pixel,
        "directorio": (pixel // 10000) * 10000,
        "url": url,
        "disponibilidad": disponibilidad,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Localiza cubos HiPS de SPHEREx mediante HEALPix."
    )

    parser.add_argument(
        "--ra",
        type=float,
        required=True,
        help="Ascensión recta en grados."
    )

    parser.add_argument(
        "--dec",
        type=float,
        required=True,
        help="Declinación en grados."
    )

    args = parser.parse_args()

    try:
        resultado = buscar_cubo(args.ra, args.dec)

        print("\n" + "=" * 55)
        print("LOCALIZADOR DE CUBOS SPHEREx HiPS")
        print("=" * 55)

        print(f"RA:              {resultado['ra_deg']}")
        print(f"Dec:             {resultado['dec_deg']}")
        print(f"Orden HEALPix:   {resultado['orden_healpix']}")
        print(f"NSIDE:           {resultado['nside']}")
        print(f"Píxel:           {resultado['pixel']}")
        print(f"Directorio:      {resultado['directorio']}")
        print(f"\nURL:\n{resultado['url']}")

        estado = resultado["disponibilidad"]

        print("\n" + "-" * 55)
        print("COMPROBACIÓN REMOTA")
        print("-" * 55)

        print(f"HTTP:            {estado['http']}")
        print(f"Disponible:      {estado['disponible']}")

        if estado["tamano_bytes"] is not None:
            tamano_mb = estado["tamano_bytes"] / (1024 ** 2)
            print(f"Tamaño:          {tamano_mb:.2f} MB")

        if estado.get("error"):
            print(f"Error:           {estado['error']}")

        print("=" * 55)

    except (ValueError, requests.RequestException) as error:
        print(f"ERROR: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
