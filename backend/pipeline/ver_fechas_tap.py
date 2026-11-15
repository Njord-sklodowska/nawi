from astropy.time import Time
from astroquery.ipac.irsa import Irsa

ra, dec = 269.44616, 4.76971

query = f"""
SELECT 'https://irsa.ipac.caltech.edu/' || a.uri || '?center={ra},{dec}d&size=0.1' AS uri,
       p.time_bounds_lower AS mjd,
       p.energy_bandpassname AS banda
FROM spherex.artifact a
JOIN spherex.plane p ON a.planeid = p.planeid
WHERE 1 = CONTAINS(POINT('ICRS', {ra}, {dec}), p.poly)
ORDER BY p.time_bounds_lower
"""

t = Irsa.query_tap(query).to_table()
print("Observaciones que contienen a Barnard:", len(t))
if len(t):
    print("Más vieja:", Time(float(t["mjd"].min()), format="mjd").iso)
    print("Más nueva:", Time(float(t["mjd"].max()), format="mjd").iso)
    print("Bandas:", sorted(set(map(str, t["banda"]))))
    for fila in t[:5]:
        print(fila["uri"])
    t.write("observaciones_barnard.csv", format="csv", overwrite=True)
    print("Lista completa guardada en observaciones_barnard.csv")