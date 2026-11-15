import json
from pathlib import Path

import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.time import Time

import warnings
warnings.filterwarnings("ignore")

RAIZ = Path(__file__).resolve().parents[1] / "data"
OBJETOS = Path(__file__).resolve().parent / "objetos.json"
FECHA_CENTRO = "2026-01-01"


def cargar(slug):
    datos = json.loads(OBJETOS.read_text(encoding="utf-8-sig"))
    lista = datos["objetos"]

    if slug not in lista:
        raise SystemExit(
            f"Objeto desconocido: {slug}. Opciones: {', '.join(lista)}"
        )

    o = lista[slug]
    a = o["astrometria"]

    fecha_referencia = a["fecha_referencia"]

    c0 = SkyCoord(
        ra=a["ra_deg"] * u.deg,
        dec=a["dec_deg"] * u.deg,
        pm_ra_cosdec=a["pm_ra_cosdec_mas_yr"] * u.mas / u.yr,
        pm_dec=a["pm_dec_mas_yr"] * u.mas / u.yr,
        frame="icrs",
        obstime=Time(fecha_referencia),
    )

    centro = c0.apply_space_motion(
        new_obstime=Time(FECHA_CENTRO)
    )

    return o, c0, centro