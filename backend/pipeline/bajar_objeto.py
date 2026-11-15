import re, sys, time
import numpy as np
import requests
from astropy.coordinates import SkyCoord
from astropy.time import Time
import astropy.units as u
from astroquery.ipac.irsa import Irsa
import warnings
warnings.filterwarnings("ignore")
from comun import RAIZ, cargar

slug = sys.argv[1]
o, c0, centro = cargar(slug)
CARPETA = RAIZ / "raw" / slug
CARPETA.mkdir(parents=True, exist_ok=True)
COLECCIONES = ["spherex_dr1", "spherex_qr3"]
MARGEN = 200   # segundos de arco al borde del detector


def reintentar(f, intentos=4):
    for i in range(intentos):
        try:
            return f()
        except Exception as e:
            print(f"  intento {i+1} falló: {str(e)[:70]}")
            time.sleep(20)
    return None


def dentro_con_margen(poly, margen):
    n = len(poly) - 1
    inside = False
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[i+1]
        if (y1 > 0) != (y2 > 0) and 0 < (x2-x1)*(0-y1)/(y2-y1) + x1:
            inside = not inside
    dmin = 1e9
    for i in range(n):
        a = np.array(poly[i]); b = np.array(poly[i+1]); ab = b - a
        t = np.clip(np.dot(-a, ab)/np.dot(ab, ab), 0, 1)
        dmin = min(dmin, np.hypot(*(a + t*ab)))
    return inside and dmin >= margen


print(f"Objeto: {o['nombre']}  centro: {centro.ra.deg:.5f}, {centro.dec.deg:.5f}")
elegidas = {}
for col in COLECCIONES:
    print("Consultando", col)
    t = reintentar(lambda: Irsa.query_sia(pos=(centro, 0.01*u.deg), collection=col))
    if t is None:
        print("  no respondió, sigo con las demás colecciones"); continue
    print("  filas:", len(t))
    for r in t:
        if str(r["energy_bandpassname"]) != "SPHEREx-D6":
            continue
        url = str(r["access_url"])
        sem = re.search(r"(\d{4}W\d{2})", url).group(1)
        if sem in elegidas:
            continue
        tm = (float(r["t_min"]) + float(r["t_max"])) / 2
        c = c0.apply_space_motion(new_obstime=Time(tm, format="mjd"))
        nums = [float(x) for x in re.findall(r"[-\d.]+", str(r["s_region"]).split("ICRS")[1])]
        p = np.array(nums).reshape(-1, 2)
        poly = np.c_[(p[:, 0]-c.ra.deg)*np.cos(np.radians(c.dec.deg))*3600,
                     (p[:, 1]-c.dec.deg)*3600]
        if dentro_con_margen(poly, MARGEN):
            elegidas[sem] = url

print("Semanas elegidas:", sorted(elegidas))
centro_txt = f"{centro.ra.deg:.5f},{centro.dec.deg:.5f}"

for sem, url in sorted(elegidas.items()):
    destino = CARPETA / url.split("/")[-1]
    if destino.exists():
        print("ya existe:", destino.name); continue
    print("bajando", sem, "...")

    def bajar():
        r = requests.get(url, params={"center": centro_txt, "size": "0.1"}, timeout=180)
        r.raise_for_status()
        return r.content

    datos = reintentar(bajar)
    if datos:
        destino.write_bytes(datos)
        print("  guardado:", destino.name)

print("\nListo. Archivos en:", CARPETA)