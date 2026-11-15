import sys
import numpy as np
from astropy.io import fits
from astropy.time import Time
from astropy.wcs import WCS
from comun import RAIZ, cargar

slug = sys.argv[1]
o, c0, centro = cargar(slug)
for ruta in sorted((RAIZ / "raw" / slug).glob("*.fits")):
    with fits.open(ruta) as h:
        hdr = h["IMAGE"].header
        img = h["IMAGE"].data.astype(float)
        w = WCS(hdr, fobj=h)
        pos = c0.apply_space_motion(new_obstime=Time(hdr["DATE-AVG"]))
        xs, ys = [float(t) for t in w.world_to_pixel(pos)]
    ny, nx = img.shape
    yy, xx = np.indices(img.shape)
    r = np.hypot(xx - xs, yy - ys)
    ap = r <= 3.5
    anillo = (r >= 6) & (r <= 9)
    print(f"{hdr['DATE-AVG'][:10]}  imagen {nx}x{ny}  estrella en ({xs:.1f},{ys:.1f})  "
          f"NaN apertura: {int((~np.isfinite(img[ap])).sum())}/{int(ap.sum())}  "
          f"NaN anillo: {int((~np.isfinite(img[anillo])).sum())}/{int(anillo.sum())}  "
          f"pico: {np.nanmax(img):.3g}")