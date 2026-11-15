from astropy.io import fits
from astropy.wcs import WCS
import matplotlib.pyplot as plt

# Ruta de tu archivo FITS
ruta_fits = r"C:\Users\mater\Downloads\barnard\barnard_recorte.fits"

# Abrimos el archivo
with fits.open(ruta_fits) as hdul:
  data = hdul[0].data
  wcs = WCS(hdul[0].header)

# Configuramos la ventana de visualización
plt.figure(figsize=(7, 7))
plt.imshow(
    data, origin="lower", cmap="gray", vmin=data.mean(), vmax=data.mean() * 5
)
plt.colorbar(label="Intensidad de brillo")
plt.title("Recorte FITS - Estrella de Barnard")
plt.xlabel("Píxeles X")
plt.ylabel("Píxeles Y")

# Opcional: marcar la posición exacta que calculó tu script (x=211.8, y=361.2)
plt.scatter(
    [211.8],
    [361.2],
    color="red",
    marker="x",
    s=100,
    label="Predicción (Barnard)",
)
plt.legend()

# Guardamos una copia en PNG para que puedas verla como foto normal
ruta_png = r"C:\Users\mater\Downloads\barnard\barnard_recorte.png"
plt.savefig(ruta_png, dpi=200)
print(f"¡Foto guardada con éxito en: {ruta_png}")

# Muestra la ventana interactiva en la compu
plt.show()