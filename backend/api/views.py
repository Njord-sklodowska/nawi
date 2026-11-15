"""
API de NAWI.

Rutas:
    GET /api/estado/
    GET /api/objetos/
    GET /api/objetos/<slug>/
    GET /api/objetos/<slug>/posicion/?fecha=YYYY-MM-DD
    GET /api/objetos/<slug>/cuadros/

Integración de las dos líneas de backend:
  - catálogo y astrometría (pipeline/catalogo.py, pipeline/astrometria.py)
  - datos precalculados y cuadros PNG (backend/data/<slug>/datos.json + /media/)
"""

import json
import re
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from pipeline.catalogo import (
    ErrorCatalogo,
    ObjetoNoEncontradoError,
    cargar_catalogo,
    obtener_objeto,
)

# `pipeline.astrometria` necesita astropy. Se importa dentro de la vista para que
# el resto de la API (catálogo y cuadros) siga funcionando sin astropy instalado.
try:  # pragma: no cover
    from pipeline.astrometria import calcular_posicion  # noqa: F401
except ImportError:  # pragma: no cover
    calcular_posicion = None

DATA = Path(settings.BASE_DIR) / "data"
SLUG_OK = re.compile(r"^[a-z0-9-]+$")

VACIO = {
    "estado": "sin_datos",
    "motivo": "Todavía no se precalcularon datos para este objeto.",
    "cuadros": [],
    "latido": [],
    "rastro": {
        "desplazamiento_arcsec": None,
        "direccion_deg": None,
        "incertidumbre_arcsec": None,
        "pm_publicado_arcsec_yr": None,
    },
    "revelar": {"snr_vs_cuadros": []},
    "conocido": {"estado": "sin_datos", "coincidencias": []},
}


def _datos(slug):
    """Lee backend/data/<slug>/datos.json si existe y el slug es seguro."""
    if not isinstance(slug, str) or not SLUG_OK.match(slug):
        return None
    ruta = DATA / slug / "datos.json"
    if not ruta.exists():
        return None
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _astrometria(objeto):
    valor = objeto.get("astrometria")
    return valor if isinstance(valor, dict) else None


@require_GET
def estado_api(request):
    return JsonResponse({
        "estado": "ok",
        "mensaje": "API de NAWI funcionando",
        "version": "1.1",
    })


@require_GET
def listar_objetos(request):
    """
    Lista plana de objetos con lo necesario para pintar el selector:
    identidad, rol, astrometría y si ya hay cuadros precalculados.
    """
    try:
        catalogo = cargar_catalogo()
        objetos = catalogo["objetos"]
    except ErrorCatalogo as error:
        return JsonResponse({"error": str(error)}, status=500)

    salida = []
    for slug, objeto in objetos.items():
        astrometria = _astrometria(objeto) or {}
        datos = _datos(slug)
        salida.append({
            "slug": slug,
            "nombre": objeto.get("nombre", slug),
            "tipo": objeto.get("tipo"),
            "rol": objeto.get("rol"),
            "fov_arcmin": objeto.get("fov_arcmin"),
            "ra_deg": astrometria.get("ra_deg"),
            "dec_deg": astrometria.get("dec_deg"),
            "epoca": astrometria.get("epoca")
            or astrometria.get("fecha_referencia"),
            "pm_ra_cosdec_mas_yr": astrometria.get("pm_ra_cosdec_mas_yr"),
            "pm_dec_mas_yr": astrometria.get("pm_dec_mas_yr"),
            "astrometria_disponible": isinstance(astrometria, dict) and bool(astrometria),
            "estado": (datos or {}).get("estado", "sin_datos"),
            "cantidad_cuadros": len((datos or {}).get("cuadros", [])),
        })

    return JsonResponse(salida, safe=False)


@require_GET
def detalle_objeto(request, slug):
    """
    Ficha completa: catálogo + astrometría + datos precalculados (cuadros,
    latido, rastro, revelar, conocido). Si todavía no hay datos precalculados
    devuelve la ficha del catálogo con `estado: sin_datos`.
    """
    try:
        objeto = obtener_objeto(slug)
    except ObjetoNoEncontradoError:
        return JsonResponse(
            {"error": "objeto_desconocido",
             "mensaje": "Ese objeto no está en Nawi."},
            status=404,
        )
    except ErrorCatalogo as error:
        return JsonResponse({"error": str(error)}, status=500)

    ficha = {
        "slug": slug,
        "nombre": objeto.get("nombre", slug),
        "tipo": objeto.get("tipo"),
        "rol": objeto.get("rol"),
        "fov_arcmin": objeto.get("fov_arcmin"),
        "astrometria": _astrometria(objeto),
        "fuente": objeto.get("fuente"),
    }

    datos = _datos(slug)
    if datos is None:
        ficha.update(VACIO)
        return JsonResponse(ficha)

    # Los datos precalculados mandan; del catálogo solo se agrega lo que falte.
    for clave, valor in ficha.items():
        datos.setdefault(clave, valor)
    return JsonResponse(datos)


@require_GET
def cuadros_objeto(request, slug):
    """Solo la serie temporal, para el visor."""
    try:
        obtener_objeto(slug)
    except ObjetoNoEncontradoError:
        return JsonResponse(
            {"error": "objeto_desconocido",
             "mensaje": "Ese objeto no está en Nawi."},
            status=404,
        )
    except ErrorCatalogo as error:
        return JsonResponse({"error": str(error)}, status=500)

    datos = _datos(slug)
    if datos is None:
        return JsonResponse({"slug": slug, **VACIO})

    return JsonResponse({
        "slug": slug,
        "estado": datos.get("estado", "sin_datos"),
        "motivo": datos.get("motivo", ""),
        "fov_arcmin": datos.get("fov_arcmin"),
        "pixel_arcsec": datos.get("pixel_arcsec"),
        "tamano_px": datos.get("tamano_px"),
        "cuadros": datos.get("cuadros", []),
    })


@require_GET
def posicion_objeto(request, slug):
    """Posición del objeto propagada por movimiento propio a una fecha."""
    fecha = request.GET.get("fecha")

    if calcular_posicion is None:
        return JsonResponse(
            {"error": "astrometria_no_disponible",
             "mensaje": "Falta astropy en el entorno del backend."},
            status=503,
        )

    if not fecha:
        return JsonResponse(
            {"error": "Falta el parámetro obligatorio: fecha (YYYY-MM-DD)"},
            status=400,
        )

    try:
        resultado = calcular_posicion(slug, fecha)
        return JsonResponse(resultado)
    except ObjetoNoEncontradoError:
        return JsonResponse(
            {"error": "Objeto no encontrado", "slug": slug},
            status=404,
        )
    except ErrorCatalogo as error:
        return JsonResponse({"error": str(error)}, status=500)
    except (ValueError, TypeError, OverflowError) as error:
        return JsonResponse(
            {"error": f"No se pudo calcular la posición: {error}"},
            status=400,
        )


# Alias por compatibilidad con la versión anterior de la API.
lista_objetos = listar_objetos
