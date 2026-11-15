
from astrometria import posicion_en


# Datos de Barnard utilizados por Cecilia.
# Valores provisionales para esta prueba.

barnard = {
    "ra_deg": 269.452083,
    "dec_deg": 4.693333,
    "pm_ra_cosdec_mas_yr": -798.58,
    "pm_dec_mas_yr": 10328.12,
    "fecha_referencia": "J2000.0",
}

fecha = "2026-11-15"

resultado = posicion_en(
    ra_deg=barnard["ra_deg"],
    dec_deg=barnard["dec_deg"],
    pm_ra_cosdec_mas_yr=barnard["pm_ra_cosdec_mas_yr"],
    pm_dec_mas_yr=barnard["pm_dec_mas_yr"],
    fecha_observacion=fecha,
    fecha_referencia=barnard["fecha_referencia"],
)

print("=" * 50)
print("PRUEBA DE ASTROMETRÍA NAWI")
print("=" * 50)

print("Objeto: Barnard")
print(f"Fecha de observación: {fecha}")
print(f"RA actualizada: {resultado['ra_deg']:.8f}°")
print(f"Dec actualizada: {resultado['dec_deg']:.8f}°")
print(f"Años transcurridos: {resultado['anios_transcurridos']:.4f}")
print(
    f"Desplazamiento: "
    f"{resultado['desplazamiento_arcsec']:.2f} arcsec"
)

print("=" * 50)
print("PRUEBA FINALIZADA")
