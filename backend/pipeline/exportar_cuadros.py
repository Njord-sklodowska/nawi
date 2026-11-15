import json, sys
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.time import Time
from reproject import reproject_interp
from PIL import Image
import warnings
warnings.filterwarnings("ignore")
from comun import RAIZ, cargar

slug = sys.argv[1]
o, c0, centro = cargar(slug)
ENTRADA = RAIZ / "raw" / slug
SALIDA = RAIZ / slug / "frames"
SALIDA.mkdir(parents=True, exist_ok=True)
N, PIX = 58, 6.15

datos_json = dict(
    slug=slug, nombre=o["nombre"], tipo=o["tipo"],
    centro={"ra_deg": round(centro.ra.deg, 6), "dec_deg": round(centro.dec.deg, 6)},
    fov_arcmin=round(N * PIX / 60, 2), pixel_arcsec=PIX, tamano_px=N,
    estado="ok", motivo="", cuadros=[], latido=[],
    rastro={"desplazamiento_arcsec": None, "direccion_deg": None,
            "incertidumbre_arcsec": None, "pm_publicado_arcsec_yr": None},
    revelar={"snr_vs_cuadros": []},
    conocido={"estado": "sin_datos", "coincidencias": []},
)


def guardar():
    (RAIZ / slug / "datos.json").write_text(
        json.dumps(datos_json, ensure_ascii=False, indent=2), encoding="utf-8")


archivos = sorted(ENTRADA.glob("*.fits")) if ENTRADA.exists() else []
if not archivos:
    datos_json["estado"] = "sin_datos"
    datos_json["motivo"] = "No hay recortes de SPHEREx para este objeto."
    guardar()
    raise SystemExit("Sin recortes: se guardó datos.json con estado sin_datos.")

# Grilla común: norte arriba, este a la izquierda
dest = WCS(naxis=2)
dest.wcs.ctype = ["RA---TAN", "DEC--TAN"]
dest.wcs.crval = [centro.ra.deg, centro.dec.deg]
dest.wcs.crpix = [(N + 1) / 2, (N + 1) / 2]
dest.wcs.cdelt = [-PIX / 3600, PIX / 3600]

cuadros = []
for ruta in archivos:
    with fits.open(ruta) as h:
        hdr = h["IMAGE"].header
        datos = h["IMAGE"].data.astype(float)
        fecha = hdr["DATE-AVG"]
        img, _ = reproject_interp((datos, WCS(hdr, fobj=h)), dest, shape_out=(N, N))
    cuadros.append(dict(fecha=fecha, img=img))
cuadros.sort(key=lambda c: c["fecha"])

# Escala de brillo única para todas las fechas
todo = np.concatenate([c["img"][np.isfinite(c["img"])] for c in cuadros])
lo = np.median(todo)
sigma = 1.4826 * np.median(np.abs(todo - lo))
hi = np.percentile(todo, 99.99)
soft = max(5 * sigma, 1e-6)
den = np.arcsinh((hi - lo) / soft)


def snr_en(img, x, y):
    xi, yi = int(round(x)), int(round(y))
    if not (0 <= xi < N and 0 <= yi < N):
        return None
    ventana = img[max(0, yi-1):yi+2, max(0, xi-1):xi+2]
    if not np.isfinite(ventana).any():
        return None
    fondo = np.nanmedian(img)
    s = 1.4826 * np.nanmedian(np.abs(img - fondo))
    return float((np.nanmax(ventana) - fondo) / s) if s > 0 else None


for f in SALIDA.glob("*.png"):
    f.unlink()

print(f"{slug}: {len(cuadros)} cuadros")
for i, c in enumerate(cuadros):
    img = c["img"]
    v = np.clip(np.arcsinh((np.nan_to_num(img, nan=lo) - lo) / soft) / den, 0, 1)
    nombre = f"{i:04d}.png"
    Image.fromarray((np.flipud(v) * 255).astype(np.uint8), mode="L").save(SALIDA / nombre)

    pos = c0.apply_space_motion(new_obstime=Time(c["fecha"]))
    x, y = [float(t) for t in dest.world_to_pixel(pos)]
    snr = snr_en(img, x, y)
    cobertura_pct = round(float(np.isfinite(img).mean()) * 100, 1)

    datos_json["cuadros"].append(dict(
        fecha=c["fecha"][:19] + "Z",
        url=f"/media/{slug}/frames/{nombre}",
        longitud_onda_um=None,
        cobertura_pct=cobertura_pct,
        calidad_ok=bool(cobertura_pct >= 90),
        pos_esperada_px={"x": round(x, 2), "y": round(N - 1 - y, 2)},
        snr_en_posicion=None if snr is None else round(snr, 1),
    ))
    print(f"  {c['fecha'][:10]}  señal en la posición esperada: "
          f"{'sin dato' if snr is None else f'{snr:.1f} sigma'}")

guardar()
print("Listo:", RAIZ / slug)