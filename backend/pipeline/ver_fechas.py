import re
import time
import numpy as np
from astropy.coordinates import SkyCoord
from astropy.time import Time
import astropy.units as u
from astroquery.ipac.irsa import Irsa

pos = SkyCoord(269.4461*u.deg, 4.7704*u.deg)


def consultar(col, intentos=4):
    for i in range(intentos):
        try:
            return Irsa.query_sia(pos=(pos, 0.1*u.deg), collection=col)
        except Exception as e:
            print(f"  intento {i+1} falló: {str(e)[:80]}")
            time.sleep(20)
    return None


for col in ["spherex_qr3", "spherex_dr1"]:
    print("=" * 50, col)
    t = consultar(col)
    if t is None:
        print("No se pudo consultar.")
        continue
    print("Filas:", len(t))
    print("Columnas:", t.colnames)
    if len(t) == 0:
        continue
    if "t_min" in t.colnames:
        mjd = np.array(t["t_min"], dtype=float)
        print("Observación más vieja:", Time(np.nanmin(mjd), format="mjd").iso)
        print("Observación más nueva:", Time(np.nanmax(mjd), format="mjd").iso)
    urls = [str(x) for x in t["access_url"]]
    semanas = sorted(set(re.findall(r"(\d{4}W\d{2})", " ".join(urls))))
    print("Semanas de observación:", semanas)
    print("Primer access_url:", urls[0])