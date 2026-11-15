import json
from pathlib import Path
from astropy.coordinates import SkyCoord, Distance
from astropy.time import Time
import astropy.units as u
import warnings
warnings.filterwarnings("ignore")

RAIZ = Path(__file__).resolve().parents[1] / "data"
OBJETOS = Path(__file__).resolve().parent / "objetos.json"
FECHA_CENTRO = "2026-01-01"   # mitad aproximada del periodo de observaciones


def cargar(slug):
    catalogo = json.loads(OBJETOS.read_text(encoding="utf-8"))["objetos"]
    if slug not in catalogo:
        raise SystemExit(f"Objeto desconocido: {slug}. Opciones: {', '.join(catalogo)}")

    crudo = catalogo[slug]
    a = crudo["astrometria"]

    # Formato plano, igual que el objetos.json anterior, para no romper los otros scripts
    o = {k: v for k, v in crudo.items() if k != "astrometria"}
    o.update(a)
    o["slug"] = slug
    o["epoca"] = a["fecha_referencia"]

    datos = dict(
        ra=a["ra_deg"] * u.deg,
        dec=a["dec_deg"] * u.deg,
        pm_ra_cosdec=a["pm_ra_cosdec_mas_yr"] * u.mas / u.yr,
        pm_dec=a["pm_dec_mas_yr"] * u.mas / u.yr,
        frame="icrs",
        obstime=Time(a["fecha_referencia"]),   # J2016.0 para Barnard, J2000.0 para los demas
    )
    if a.get("parallax_mas"):
        datos["distance"] = Distance(parallax=a["parallax_mas"] * u.mas)
        datos["radial_velocity"] = (a.get("radial_velocity_km_s") or 0.0) * u.km / u.s

    c0 = SkyCoord(**datos)
    centro = c0.apply_space_motion(new_obstime=Time(FECHA_CENTRO))
    return o, c0, centro