from astropy.coordinates import SkyCoord
from astropy.time import Time
import astropy.units as u
import numpy as np

# Valores de SIMBAD (Gaia DR3), época J2000
PMRA, PMDEC = -801.551, 10362.394   # mas/año

c0 = SkyCoord(ra=269.45207696*u.deg, dec=4.69336497*u.deg,
              pm_ra_cosdec=PMRA*u.mas/u.yr, pm_dec=PMDEC*u.mas/u.yr,
              frame="icrs", obstime=Time("J2000.0"))

def posicion_en(fecha_iso):
    return c0.apply_space_motion(new_obstime=Time(fecha_iso))

c = posicion_en("2026-11-14")
anios = c.obstime.jyear - 2000.0
medido = c0.separation(c).arcsec
esperado = np.hypot(PMRA, PMDEC) / 1000 * anios

print(f"RA {c.ra.deg:.6f}  Dec {c.dec.deg:.6f}")
print(f"Desplazamiento: {medido:.1f}\"  (esperado ~{esperado:.1f}\")")
assert abs(medido - esperado) < 3, "El movimiento propio no coincide: revisar valores"
print("OK")
