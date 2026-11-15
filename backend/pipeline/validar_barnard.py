import sys
from astropy.io import fits
from astropy.wcs import WCS
from astropy.time import Time
from astropy.coordinates import SkyCoord
import astropy.units as u
import numpy as np

c0 = SkyCoord(ra=269.452083*u.deg, dec=4.693333*u.deg,
              pm_ra_cosdec=-798.58*u.mas/u.yr,
              pm_dec=10328.12*u.mas/u.yr,
              frame='icrs', obstime=Time('J2000.0'))

with fits.open(sys.argv[1]) as h:
    
    hdr = h["IMAGE"].header if "IMAGE" in h else h[0].header
    img = h["IMAGE"].data if "IMAGE" in h else h[0].data
    wcs = WCS(hdr)
    # Buscamos la fecha probando distintas claves estándar de FITS
    fecha = None
    for clave in ["DATE-AVG", "DATE-OBS", "DATE"]:
        if clave in hdr:
            fecha = hdr[clave]
            break

        # Si por alguna razón ninguna existe en el archivo, usamos una por defecto para la demo
    if not fecha:
        fecha = "2026-08-16T15:07:10.751"

c = c0.apply_space_motion(new_obstime=Time(fecha))
x, y = wcs.world_to_pixel(c)
x, y = float(x), float(y)

print("Fecha de observación:", fecha)
print(f"Barnard esperada en: RA {c.ra.deg:.5f}  Dec {c.dec.deg:.5f}")
print(f"Píxel esperado: x={x:.1f}  y={y:.1f}   (imagen: {img.shape[1]} x {img.shape[0]})")

dentro = 0 <= x < img.shape[1] and 0 <= y < img.shape[0]
print("¿Cae dentro de la imagen?", dentro)

if dentro:
    xi, yi = int(round(x)), int(round(y))
    y0, y1 = max(0, yi-6), min(img.shape[0], yi+7)
    x0, x1 = max(0, xi-6), min(img.shape[1], xi+7)
    sub = img[y0:y1, x0:x1]
    iy, ix = np.unravel_index(np.nanargmax(sub), sub.shape)
    print(f"Píxel más brillante cerca: x={x0+ix}  y={y0+iy}")
    print(f"Distancia al esperado: {np.hypot(x0+ix-x, y0+iy-y):.1f} píxeles")
    print(f"Brillo ahí: {sub[iy, ix]:.3g}   mediana de la imagen: {np.nanmedian(img):.3g}")