import sys, glob
from astropy.io import fits
from astropy.wcs import WCS
from astropy.time import Time
from astropy.coordinates import SkyCoord
import astropy.units as u
import numpy as np
import warnings
warnings.filterwarnings("ignore")

c0 = SkyCoord(ra=269.452083*u.deg, dec=4.693333*u.deg,
              pm_ra_cosdec=-798.58*u.mas/u.yr,
              pm_dec=10328.12*u.mas/u.yr,
              frame="icrs", obstime=Time("J2000.0"))

for ruta in sorted(glob.glob(sys.argv[1] + "/*.fits")):
    with fits.open(ruta) as h:
        hdr = h["IMAGE"].header
        img = h["IMAGE"].data
        wcs = WCS(hdr)
        if "DATE-AVG" not in hdr:
            raise SystemExit(f"{ruta}: no tiene DATE-AVG. No se puede validar.")
        fecha = hdr["DATE-AVG"]

    c = c0.apply_space_motion(new_obstime=Time(fecha))
    x, y = [float(v) for v in wcs.world_to_pixel(c)]
    dentro = 0 <= x < img.shape[1] and 0 <= y < img.shape[0]
    print(f"{fecha[:10]}  imagen {img.shape[1]}x{img.shape[0]}  "
          f"esperado x={x:.1f} y={y:.1f}  DENTRO={dentro}")
    if dentro:
        xi, yi = int(round(x)), int(round(y))
        y0, y1 = max(0, yi-6), min(img.shape[0], yi+7)
        x0, x1 = max(0, xi-6), min(img.shape[1], xi+7)
        sub = img[y0:y1, x0:x1]
        iy, ix = np.unravel_index(np.nanargmax(sub), sub.shape)
        print(f"    más brillante cerca: ({x0+ix},{y0+iy}), "
              f"a {np.hypot(x0+ix-x, y0+iy-y):.1f} px del esperado; "
              f"brillo {sub[iy,ix]:.3g} vs mediana {np.nanmedian(img):.3g}")