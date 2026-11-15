from astroquery.skyview import SkyView

print("Descargando un recorte más amplio para la Estrella de Barnard...")

# Ampliamos el tamaño de la imagen a 400x400 píxeles
paths = SkyView.get_images(
    position="17h 57m 48.5s +04d 41m 36s", survey=["DSS"], pixels=[400, 400]
)

if paths:
  hdu_list = paths[0]
  ruta_salida = r"C:\Users\mater\Downloads\barnard\barnard_recorte.fits"
  hdu_list.writeto(ruta_salida, overwrite=True)
  print(f"¡Listo! Archivo actualizado en: {ruta_salida}")
else:
  print("No se pudo descargar.")