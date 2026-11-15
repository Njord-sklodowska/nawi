import json
from pathlib import Path
from astropy.coordinates import SkyCoord
from astropy.time import Time
import astropy.units as u
import warnings
warnings.filterwarnings("ignore")

RAIZ = Path(__file__).resolve().parents[1] / "data"
OBJETOS = Path(__file__).resolve().parent / "objetos.json"
FECHA_CENTRO = "2026-01-01"   # mitad aproximada del período de observaciones


def cargar(slug):
    lista = {o["slug"]: o for o in json.loads(OBJETOS.read_text(encoding="utf-8"))}
    if slug not in lista:
        raise SystemExit(f"Objeto desconocido: {slug}. Opciones: {', '.join(lista)}")
    o = lista[slug]
    c0 = SkyCoord(ra=o["ra_deg"]*u.deg, dec=o["dec_deg"]*u.deg,
                  pm_ra_cosdec=o["pm_ra_cosdec_mas_yr"]*u.mas/u.yr,
                  pm_dec=o["pm_dec_mas_yr"]*u.mas/u.yr,
                  frame="icrs", obstime=Time("J2000.0"))
    centro = c0.apply_space_motion(new_obstime=Time(FECHA_CENTRO))
    return o, c0, centro