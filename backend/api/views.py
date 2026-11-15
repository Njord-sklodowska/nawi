from django.http import JsonResponse
from django.views.decorators.http import require_GET

from pipeline.catalogo import (
    cargar_catalogo,
    obtener_objeto,
    ObjetoNoEncontradoError,
    ErrorCatalogo,
)
from pipeline.astrometria import calcular_posicion


@require_GET
def estado_api(request):
    return JsonResponse({
        "estado": "ok",
        "mensaje": "API de NAWI funcionando",
        "version": "1.0"
    })


@require_GET
def listar_objetos(request):
    try:
        catalogo = cargar_catalogo()
        objetos = catalogo["objetos"]

        resultado = []
        for slug, objeto in objetos.items():
            resultado.append({
                "slug": slug,
                "nombre": objeto.get("nombre", slug),
                "tipo": objeto.get("tipo"),
                "rol": objeto.get("rol"),
                "fov_arcmin": objeto.get("fov_arcmin"),
                "astrometria_disponible": isinstance(
                    objeto.get("astrometria"), dict
                ),
            })

        return JsonResponse({
            "total": len(resultado),
            "objetos": resultado
        })

    except ErrorCatalogo as error:
        return JsonResponse({"error": str(error)}, status=500)


@require_GET
def detalle_objeto(request, slug):
    try:
        objeto = obtener_objeto(slug)
        return JsonResponse({
            "slug": slug,
            **objeto
        })

    except ObjetoNoEncontradoError:
        return JsonResponse(
            {"error": "Objeto no encontrado", "slug": slug},
            status=404
        )
    except ErrorCatalogo as error:
        return JsonResponse({"error": str(error)}, status=500)


@require_GET
def posicion_objeto(request, slug):
    fecha = request.GET.get("fecha")

    if not fecha:
        return JsonResponse(
            {"error": "Falta el par?metro obligatorio: fecha (YYYY-MM-DD)"},
            status=400
        )

    try:
        resultado = calcular_posicion(slug, fecha)
        return JsonResponse(resultado)

    except ObjetoNoEncontradoError:
        return JsonResponse(
            {"error": "Objeto no encontrado", "slug": slug},
            status=404
        )
    except ErrorCatalogo as error:
        return JsonResponse({"error": str(error)}, status=500)
    except (ValueError, TypeError, OverflowError) as error:
        return JsonResponse(
            {"error": f"No se pudo calcular la posici?n: {error}"},
            status=400
        )
