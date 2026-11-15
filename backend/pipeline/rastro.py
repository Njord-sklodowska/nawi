import sys, json
import numpy as np
from astropy.io import fits
from astropy.time import Time
from astropy.wcs import WCS
import warnings
warnings.filterwarnings("ignore")
from comun import RAIZ, cargar

slug = sys.argv[1]
o, c0, centro = cargar(slug)
ruta_json = RAIZ / slug / "datos.json"
d = json.loads(ruta_json.read_text(encoding="utf-8"))
MEDIO = 2   # ventana de 5x5 píxeles alrededor del pico

filas = []
for ruta in sorted((RAIZ / "raw" / slug).glob("*.fits")):
    with fits.open(ruta) as h:
        hdr = h["IMAGE"].header
        img = h["IMAGE"].data.astype(float)
        w = WCS(hdr, fobj=h)
        fecha = hdr["DATE-AVG"]
    pos = c0.apply_space_motion(new_obstime=Time(fecha))
    xs, ys = [float(t) for t in w.world_to_pixel(pos)]
    ny, nx = img.shape
    yy, xx = np.indices(img.shape)
    r = np.hypot(xx - xs, yy - ys)

    cerca = np.where(r <= 3, img, np.nan)
    if not np.isfinite(cerca).any():
        print(f"{fecha[:10]}: sin datos cerca de la posición, se omite"); continue
    py, px = np.unravel_index(np.nanargmax(cerca), img.shape)
    if not (MEDIO <= px < nx - MEDIO and MEDIO <= py < ny - MEDIO):
        print(f"{fecha[:10]}: pico en el borde, se omite"); continue
    anillo = (r >= 6) & (r <= 9) & np.isfinite(img)
    if anillo.sum() < 20:
        print(f"{fecha[:10]}: fondo insuficiente, se omite"); continue
    ventana = img[py-MEDIO:py+MEDIO+1, px-MEDIO:px+MEDIO+1] - np.median(img[anillo])
    if not np.isfinite(ventana).all():
        print(f"{fecha[:10]}: píxeles vacíos en el núcleo, se omite"); continue
    pesos = np.clip(ventana, 0, None)
    if pesos.sum() <= 0:
        print(f"{fecha[:10]}: sin señal, se omite"); continue
    d1 = np.arange(-MEDIO, MEDIO + 1)
    cx = px + float((pesos.sum(axis=0) * d1).sum() / pesos.sum())
    cy = py + float((pesos.sum(axis=1) * d1).sum() / pesos.sum())
    sky = w.pixel_to_world(cx, cy)
    d_ra = (sky.ra.deg - centro.ra.deg) * np.cos(np.radians(centro.dec.deg)) * 3600
    d_dec = (sky.dec.deg - centro.dec.deg) * 3600
    filas.append((Time(fecha).jyear, d_ra, d_dec, fecha[:10]))
    print(f"{fecha[:10]}  usado: dRA={d_ra:+.2f}\"  dDec={d_dec:+.2f}\"")

if len(filas) < 4:
    raise SystemExit(f"Solo {len(filas)} cuadros utilizables: no alcanza para ajustar (se piden 4).")
f = np.array([(a, b, c) for a, b, c, _ in filas])
t = f[:, 0] - f[:, 0].min()
span = float(t.max())
if span < 0.2:
    raise SystemExit("La base temporal es muy corta (menos de 0.2 años).")

(c_ra, _), cov_ra = np.polyfit(t, f[:, 1], 1, cov=True)
(c_de, _), cov_de = np.polyfit(t, f[:, 2], 1, cov=True)
e_ra, e_de = float(np.sqrt(cov_ra[0, 0])), float(np.sqrt(cov_de[0, 0]))
pm = float(np.hypot(c_ra, c_de))
e_pm = float(np.sqrt((c_ra * e_ra) ** 2 + (c_de * e_de) ** 2) / pm)
ang = float(np.degrees(np.arctan2(c_ra, c_de)) % 360)
pub = float(np.hypot(o["pm_ra_cosdec_mas_yr"], o["pm_dec_mas_yr"]) / 1000)
desp, inc = pm * span, e_pm * span
puntos = ["norte", "noreste", "este", "sureste", "sur", "suroeste", "oeste", "noroeste"]
rumbo = puntos[int(((ang + 22.5) // 45) % 8)]
ini, fin = filas[0][3], filas[-1][3]

frase = (f"Entre el {ini} y el {fin} ({span:.1f} años), {o['nombre']} se movió unos "
         f"{desp:.1f} segundos de arco hacia el {rumbo}, unas {desp / 6.15:.1f} veces el "
         f"tamaño de un píxel de SPHEREx. El movimiento publicado predice "
         f"{pub * span:.1f} segundos de arco.")

d["rastro"] = dict(
    desplazamiento_arcsec=round(desp, 2), direccion_deg=round(ang, 1),
    incertidumbre_arcsec=round(inc, 2), pm_publicado_arcsec_yr=round(pub, 3),
    pm_medido_arcsec_yr=round(pm, 3), cuadros_usados=len(filas),
    fecha_inicio=ini, fecha_fin=fin, frase_simple=frase)
ruta_json.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")

print(f"\nMovimiento medido:  {pm:.3f} +/- {e_pm:.3f} arcsec/año")
print(f"Movimiento publicado: {pub:.3f} arcsec/año   (diferencia: {(pm - pub) / e_pm:+.1f} sigma)")
print(frase)