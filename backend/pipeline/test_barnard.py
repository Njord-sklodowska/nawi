from astropy.coordinates import SkyCoord
from astropy.time import Time
import astropy.units as u

# Barnard, J2000. Confirmar los movimientos propios en SIMBAD.
c0 = SkyCoord(ra=269.452083*u.deg, dec=4.693333*u.deg,
              pm_ra_cosdec=-798.58*u.mas/u.yr,
              pm_dec=10328.12*u.mas/u.yr,
              frame='icrs', obstime=Time('J2000.0'))

def posicion_en(fecha_iso):
    """Posición de Barnard en la fecha de una observación."""
    return c0.apply_space_motion(new_obstime=Time(fecha_iso))

c = posicion_en('2026-11-14')
anios = c.obstime.jyear - 2000.0
medido = c0.separation(c).arcsec
esperado = 10.36 * anios   # ~10,36 arcsec/año de movimiento total
print(f"RA {c.ra.deg:.6f}  Dec {c.dec.deg:.6f}")
print(f"Desplazamiento: {medido:.1f}\"  (esperado ~{esperado:.1f}\")")
assert abs(medido - esperado) < 3, "El movimiento propio no coincide: revisar valores"