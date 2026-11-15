
"""
Catálogo de objetos astronómicos de NAWI.

Permite cargar objetos desde objetos.json y recuperar
sus parámetros astrométricos de forma validada.
"""

import json
import math
from pathlib import Path


RUTA_CATALOGO = Path(__file__).with_name("objetos.json")


class ErrorCatalogo(Exception):
    """Error general del catálogo de NAWI."""


class ObjetoNoEncontradoError(ErrorCatalogo):
    """El objeto solicitado no existe en el catálogo."""


class AstrometriaNoDisponibleError(ErrorCatalogo):
    """El objeto todavía no tiene datos astrométricos."""


def cargar_catalogo():
    """Carga y devuelve el contenido de objetos.json."""

    if not RUTA_CATALOGO.exists():
        raise ErrorCatalogo(
            f"No se encontró el catálogo: {RUTA_CATALOGO}"
        )

    try:
        with RUTA_CATALOGO.open("r", encoding="utf-8") as archivo:
            catalogo = json.load(archivo)

    except json.JSONDecodeError as error:
        raise ErrorCatalogo(
            f"El archivo JSON contiene un error: {error}"
        ) from error

    if not isinstance(catalogo, dict):
        raise ErrorCatalogo("La estructura principal debe ser un objeto JSON.")

    objetos = catalogo.get("objetos")

    if not isinstance(objetos, dict):
        raise ErrorCatalogo(
            "El catálogo no contiene una sección 'objetos' válida."
        )

    return catalogo


def obtener_objeto(slug):
    """
    Recupera un objeto por su identificador.

    Ejemplo:
        obtener_objeto("barnard")
    """

    if not isinstance(slug, str) or not slug.strip():
        raise ValueError("El identificador del objeto no es válido.")

    catalogo = cargar_catalogo()
    objetos = catalogo["objetos"]

    if slug not in objetos:
        raise ObjetoNoEncontradoError(
            f"El objeto '{slug}' no existe en el catálogo."
        )

    return objetos[slug]


def obtener_astrometria(slug):
    """
    Recupera y valida los parámetros astrométricos de un objeto.

    Devuelve los parámetros y su información de procedencia.
    """

    objeto = obtener_objeto(slug)
    astrometria = objeto.get("astrometria")

    if not isinstance(astrometria, dict):
        raise AstrometriaNoDisponibleError(
            f"El objeto '{slug}' todavía no tiene astrometría."
        )

    campos = (
        "ra_deg",
        "dec_deg",
        "pm_ra_cosdec_mas_yr",
        "pm_dec_mas_yr",
        "fecha_referencia",
    )

    for campo in campos:
        if campo not in astrometria or astrometria[campo] is None:
            raise AstrometriaNoDisponibleError(
                f"Falta el parámetro '{campo}' para '{slug}'."
            )

    campos_numericos = (
        "ra_deg",
        "dec_deg",
        "pm_ra_cosdec_mas_yr",
        "pm_dec_mas_yr",
    )

    for campo in campos_numericos:
        valor = astrometria[campo]

        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ErrorCatalogo(
                f"El parámetro '{campo}' de '{slug}' debe ser numérico."
            )

        if not math.isfinite(valor):
            raise ErrorCatalogo(
                f"El parámetro '{campo}' de '{slug}' no es finito."
            )

    if not 0 <= astrometria["ra_deg"] < 360:
        raise ErrorCatalogo(
            f"La ascensión recta de '{slug}' está fuera de rango."
        )

    if not -90 <= astrometria["dec_deg"] <= 90:
        raise ErrorCatalogo(
            f"La declinación de '{slug}' está fuera de rango."
        )

    if not isinstance(astrometria["fecha_referencia"], str):
        raise ErrorCatalogo(
            f"La fecha de referencia de '{slug}' debe ser texto."
        )

    if not astrometria["fecha_referencia"].strip():
        raise ErrorCatalogo(
            f"La fecha de referencia de '{slug}' está vacía."
        )

    return {
        "nombre": objeto.get("nombre", slug),
        "astrometria": astrometria,
        "fuente": objeto.get("fuente", {}),
    }
