import sys
from astropy.io import fits
from astropy.wcs import WCS
from astropy.wcs.utils import proj_plane_pixel_scales
from astropy.coordinates import SkyCoord
import astropy.units as u

with fits.open(sys.argv[1]) as h:
    hdr = h["IMAGE"].header
    ny, nx = h["IMAGE"].data.shape
    cel = WCS(hdr, fobj=h)
    print(f"Imagen: {nx} x {ny} píxeles")
    print("Escala (segundos de arco por píxel):", proj_plane_pixel_scales(cel) * 3600)

    x, y = cel.world_to_pixel(SkyCoord(269.44616 * u.deg, 4.76971 * u.deg))
    x, y = float(x), float(y)
    print(f"Barnard cae en x={x:.1f} y={y:.1f}")
    print("¿Dentro de la imagen?", 0 <= x < nx and 0 <= y < ny)

    try:
        esp = WCS(hdr, fobj=h, key="W")
        print("Longitud de onda en ese punto:", esp.pixel_to_world(min(max(x, 0), nx - 1), min(max(y, 0), ny - 1)))
    except Exception as e:
        print("No pude leer la longitud de onda:", e)