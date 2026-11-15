import sys
from astropy.io import fits
from astropy.wcs import WCS

CLAVES = ("MJD", "DATE", "TIME", "WAVE", "LAM", "BAND", "DETECTOR", "EXPT")

with fits.open(sys.argv[1]) as h:
    h.info()
    for i, hdu in enumerate(h):
        print(f"\n--- [{i}] {hdu.name} ---")
        for k in hdu.header:
            if any(c in k.upper() for c in CLAVES):
                print(f"  {k} = {hdu.header[k]}")
        try:
            print("  Coordenadas del cielo (WCS):", WCS(hdu.header).has_celestial)
        except Exception as e:
            print("  WCS: error", e)