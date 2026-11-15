import sys
import json
import numpy as np
import astropy.units as u
from astropy.io import fits
from astropy.time import Time
from astropy.wcs import WCS
from astropy.wcs.utils import proj_plane_pixel_area
from comun import RAIZ, cargar
from astropy import log
log.setLevel("WARNING")

R_AP, R_IN, R_OUT = 3.5, 6.0, 9.0   # radios en pixeles: apertura y anillo de fondo

slug = sys.argv[1]
o, c0, centro = cargar(slug)
ruta_json = RAIZ / slug / "datos.json"
d = json.loads(ruta_json.read_text(encoding="utf-8"))

puntos = []
for ruta in sorted((RAIZ / "raw" / slug).glob("*.fits")):
    with fits.open(ruta) as h:
        hdr = h["IMAGE"].header
        img = h["IMAGE"].data.astype(float)
        var = h["VARIANCE"].data.astype(float)
        fecha = hdr["DATE-AVG"]
        unidad = str(hdr.get("BUNIT", "desconocida")).replace(" ", "")
        w = WCS(hdr, fobj=h)
        pos = c0.apply_space_motion(new_obstime=Time(fecha))
        xs, ys = [float(t) for t in w.world_to_pixel(pos)]
        ny, nx = img.shape

        yy, xx = np.indices(img.shape)
        r = np.hypot(xx - xs, yy - ys)
        ap = r <= R_AP
        anillo = (r >= R_IN) & (r <= R_OUT) & np.isfinite(img)
        dentro = (xs - R_AP >= 0 and ys - R_AP >= 0
                  and xs + R_AP <= nx - 1 and ys + R_AP <= ny - 1)
        if not dentro or not np.isfinite(img[ap]).all() or anillo.sum() < 20:
            print(f"{fecha[:10]}: apertura incompleta, se omite")
            continue

        fondo = np.median(img[anillo])
        flujo = float((img[ap] - fondo).sum())
        error = float(np.sqrt(np.nansum(var[ap])))

        if unidad == "MJy/sr":
            omega = proj_plane_pixel_area(w) * (np.pi / 180) ** 2   # sr por pixel
            flujo, error = flujo * 1e6 * omega, error * 1e6 * omega
            unidad_salida = "Jy"
        else:
            unidad_salida = unidad

        lam = WCS(hdr, fobj=h, key="W").pixel_to_world(
            min(max(xs, 0), nx - 1), min(max(ys, 0), ny - 1))
        puntos.append(dict(
            fecha=fecha[:19] + "Z",
            longitud_onda_um=round(float(lam[0].to_value(u.um)), 4),
            brillo=round(flujo, 6),
            brillo_error=round(error, 6),
            unidad=unidad_salida,
        ))
        print(f"{fecha[:10]}  {puntos[-1]['longitud_onda_um']} um  "
              f"{flujo:.5g} +/- {error:.2g} {unidad_salida}")

puntos.sort(key=lambda p: p["fecha"])
d["latido"] = puntos
ruta_json.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Listo: {len(puntos)} puntos en {ruta_json}")