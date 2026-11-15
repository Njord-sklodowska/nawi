
"""
Funciones astrométricas para NAWI.

Calcula la posición de un objeto en una fecha determinada
a partir de sus coordenadas de referencia, movimiento propio,
paralaje y velocidad radial cuando están disponibles.
"""

from math import isfinite

import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.time import Time

# Permite utilizar el módulo tanto como script como paquete.
try:
    from .catalogo import obtener_astrometria
except ImportError:
    from catalogo import obtener_astrometria


def posicion_en(
    ra_deg,
    dec_deg,
    pm_ra_cosdec_mas_yr,
    pm_dec_mas_yr,
    fecha_observacion,
    fecha_referencia="J2000.0",
    parallax_mas=None,
    radial_velocity_km_s=None,
):
    """
    Calcula la posición ICRS de un objeto para una fecha determinada.

    Si están disponibles la paralaje y la velocidad radial,
    utiliza ambas para calcular el movimiento espacial completo.
    """

    valores = {
        "RA": ra_deg,
        "Dec": dec_deg,
        "movimiento propio RA": pm_ra_cosdec_mas_yr,
        "movimiento propio Dec": pm_dec_mas_yr,
    }

    for nombre, valor in valores.items():
        try:
            numero = float(valor)
        except (TypeError, ValueError):
            raise ValueError(f"{nombre} debe ser un número válido.")

        if not isfinite(numero):
            raise ValueError(f"{nombre} debe ser un número finito.")

    ra_deg = float(ra_deg)
    dec_deg = float(dec_deg)
    pm_ra_cosdec_mas_yr = float(pm_ra_cosdec_mas_yr)
    pm_dec_mas_yr = float(pm_dec_mas_yr)

    if not -90 <= dec_deg <= 90:
        raise ValueError("La declinación debe estar entre -90 y 90 grados.")

    if not 0 <= ra_deg < 360:
        raise ValueError("La ascensión recta debe estar entre 0 y 360 grados.")

    # La paralaje y la velocidad radial deben estar disponibles juntas.
    if (parallax_mas is None) != (radial_velocity_km_s is None):
        raise ValueError(
            "La paralaje y la velocidad radial deben proporcionarse juntas."
        )

    distancia_pc = None
    velocidad_radial = None

    if parallax_mas is not None:
        try:
            parallax_mas = float(parallax_mas)
            radial_velocity_km_s = float(radial_velocity_km_s)
        except (TypeError, ValueError):
            raise ValueError(
                "La paralaje y la velocidad radial deben ser números válidos."
            )

        if not isfinite(parallax_mas) or parallax_mas <= 0:
            raise ValueError("La paralaje debe ser un número positivo y finito.")

        if not isfinite(radial_velocity_km_s):
            raise ValueError(
                "La velocidad radial debe ser un número finito."
            )

        # Conversión de paralaje en milisegundos de arco a parsecs.
        distancia_pc = 1000.0 / parallax_mas
        velocidad_radial = radial_velocity_km_s

    epoca_referencia = Time(fecha_referencia)
    epoca_observacion = Time(fecha_observacion)

    parametros_coordenada = {
        "ra": ra_deg * u.deg,
        "dec": dec_deg * u.deg,
        "pm_ra_cosdec": pm_ra_cosdec_mas_yr * u.mas / u.yr,
        "pm_dec": pm_dec_mas_yr * u.mas / u.yr,
        "frame": "icrs",
        "obstime": epoca_referencia,
    }

    # Incorporar distancia y velocidad radial si están disponibles.
    if distancia_pc is not None:
        parametros_coordenada["distance"] = distancia_pc * u.pc
        parametros_coordenada["radial_velocity"] = (
            velocidad_radial * u.km / u.s
        )

    coordenada_referencia = SkyCoord(**parametros_coordenada)

    coordenada_actualizada = coordenada_referencia.apply_space_motion(
        new_obstime=epoca_observacion
    )

    desplazamiento_arcsec = (
        coordenada_referencia.separation(coordenada_actualizada).arcsec
    )

    anios_transcurridos = (
        epoca_observacion.jyear - epoca_referencia.jyear
    )

    resultado = {
        "ra_deg": float(coordenada_actualizada.ra.deg),
        "dec_deg": float(coordenada_actualizada.dec.deg),
        "fecha_referencia": epoca_referencia.isot,
        "fecha_observacion": epoca_observacion.isot,
        "anios_transcurridos": float(anios_transcurridos),
        "desplazamiento_arcsec": float(desplazamiento_arcsec),
    }

    if distancia_pc is not None:
        resultado["distancia_pc"] = float(distancia_pc)
        resultado["parallax_mas"] = float(parallax_mas)
        resultado["radial_velocity_km_s"] = float(velocidad_radial)

    return resultado


def calcular_posicion(slug, fecha_observacion):
    """
    Calcula la posición de un objeto utilizando los datos del catálogo NAWI.

    Ejemplo:
        calcular_posicion("barnard", "2026-11-15")
    """

    datos = obtener_astrometria(slug)
    astrometria = datos["astrometria"]

    resultado = posicion_en(
        ra_deg=astrometria["ra_deg"],
        dec_deg=astrometria["dec_deg"],
        pm_ra_cosdec_mas_yr=astrometria["pm_ra_cosdec_mas_yr"],
        pm_dec_mas_yr=astrometria["pm_dec_mas_yr"],
        fecha_observacion=fecha_observacion,
        fecha_referencia=astrometria["fecha_referencia"],
        parallax_mas=astrometria.get("parallax_mas"),
        radial_velocity_km_s=astrometria.get("radial_velocity_km_s"),
    )

    return {
        "slug": slug,
        "nombre": datos["nombre"],
        **resultado,
        "fuente": datos["fuente"],
    }
