
from astrometria import calcular_posicion
from catalogo import AstrometriaNoDisponibleError


print("=" * 55)
print("PRUEBA DE CÁLCULO ASTROMÉTRICO NAWI")
print("=" * 55)

fecha = "2026-11-15"

for slug in ["barnard", "wise-0855"]:

    print(f"\nOBJETO: {slug}")
    print("-" * 40)

    try:
        resultado = calcular_posicion(slug, fecha)

        print("Nombre:", resultado["nombre"])
        print("Fecha de observación:", resultado["fecha_observacion"])
        print("RA calculada:", resultado["ra_deg"])
        print("Dec calculada:", resultado["dec_deg"])
        print("Años transcurridos:", resultado["anios_transcurridos"])
        print("Desplazamiento (arcsec):", resultado["desplazamiento_arcsec"])
        print("Estado de fuente:", resultado["fuente"]["estado"])

    except AstrometriaNoDisponibleError as error:
        print("ASTROMETRÍA PENDIENTE:", error)

print("\nPRUEBA FINALIZADA")
