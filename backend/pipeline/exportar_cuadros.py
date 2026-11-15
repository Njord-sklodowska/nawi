import json, sys
from pathlib import Path
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.time import Time
from astropy.coordinates import SkyCoord
import astropy.units as u
from reproject import reproject_interp
from PIL import Image
import warnings
warnings.filterwarnings("ignore")

SLUG = sys.argv[1] if len(sys.argv) > 1 else "barnard"
RAIZ = Path(__file__).resolve().parents[1] / "data"
ENTRADA = RAIZ / "raw" / SLUG
SALIDA = RAIZ / SLUG / "frames"
SALIDA.mkdir(parents=True, exist_ok=True)

# Datos del objeto (SIMBAD, J2000). Por ahora solo Barnard.
OBJ = {
    "barnard": dict(nombre="Estrella de Barnard", tipo="estrella_movimiento_propio",
                    ra=269.45207696, dec=4.69336497, pmra=-801.551, pmdec=10362.394),
}[SLUG]
CENTRO = (269.4461, 4.7704)   # mismo centro que los recortes bajados
N, PIX = 58, 6.15             # píxeles por lado, arcsec por píxel

c0 = SkyCoord(ra=OBJ["ra"]*u.deg, dec=OBJ["dec"]*u.deg,
              pm_ra_cosdec=OBJ["pmra"]*u.mas/u.yr, pm_dec=OBJ["pmdec"]*u.mas/u.yr,
              frame="icrs", obstime=Time("J2000.0"))

# Grilla común: norte arriba, este a la izquierda, mismo centro para todos
dest = WCS(naxis=2)
dest.wcs.ctype = ["RA---TAN", "DEC--TAN"]
dest.wcs.crval = list(CENTRO)
dest.wcs.crpix = [(N + 1) / 2, (N + 1) / 2]
dest.wcs.cdelt = [-PIX / 3600, PIX / 3600]

# 1) Leer y alinear todos los FITS
cuadros = []
for ruta in sorted(ENTRADA.glob("*.fits")):
    with fits.open(ruta) as h:
        hdr = h["IMAGE"].header
        datos = h["IMAGE"].data.astype(float)
        fecha = hdr["DATE-AVG"]
        img, _ = reproject_interp((datos, WCS(hdr, fobj=h)), dest, shape_out=(N, N))
    cuadros.append(dict(fecha=fecha, img=img, archivo=ruta.name))
cuadros.sort(key=lambda c: c["fecha"])
print(f"{len(cuadros)} cuadros alineados")

# 2) Una sola escala de brillo para todas las fechas
todo = np.concatenate([c["img"][np.isfinite(c["img"])] for c in cuadros])
lo = np.median(todo)
sigma = 1.4826 * np.median(np.abs(todo - lo))
hi = np.percentile(todo, 99.99)
soft = 5 * sigma
den = np.arcsinh((hi - lo) / soft)
print(f"escala: fondo={lo:.3g}  ruido={sigma:.3g}  tope={hi:.3g}")

# 3) Exportar PNG y armar datos.json
lista = []
for i, c in enumerate(cuadros):
    img = c["img"]
    valido = np.isfinite(img)
    v = np.clip(np.arcsinh((np.nan_to_num(img, nan=lo) - lo) / soft) / den, 0, 1)
    png = (np.flipud(v) * 255).astype(np.uint8)     # norte arriba
    nombre = f"{i:04d}.png"
    Image.fromarray(png, mode="L").save(SALIDA / nombre)

    pos = c0.apply_space_motion(new_obstime=Time(c["fecha"]))
    x, y = [float(t) for t in dest.world_to_pixel(pos)]
    lista.append(dict(
        fecha=c["fecha"][:19] + "Z",
        url=f"/media/{SLUG}/frames/{nombre}",
        longitud_onda_um=None,
        calidad_ok=bool(valido.mean() >= 0.9),
        pos_esperada_px={"x": round(x, 2), "y": round(N - 1 - y, 2)},
    ))

datos_json = dict(
    slug=SLUG, nombre=OBJ["nombre"], tipo=OBJ["tipo"],
    centro={"ra_deg": CENTRO[0], "dec_deg": CENTRO[1]},
    fov_arcmin=round(N * PIX / 60, 2), pixel_arcsec=PIX, tamano_px=N,
    estado="ok", motivo="", cuadros=lista, latido=[],
    rastro={"desplazamiento_arcsec": None, "direccion_deg": None,
            "incertidumbre_arcsec": None, "pm_publicado_arcsec_yr": None},
    revelar={"snr_vs_cuadros": []},
    conocido={"estado": "sin_datos", "coincidencias": []},
)
(RAIZ / SLUG / "datos.json").write_text(
    json.dumps(datos_json, ensure_ascii=False, indent=2), encoding="utf-8")
print("Listo:", RAIZ / SLUG)
