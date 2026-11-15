import json, re
from pathlib import Path
from django.conf import settings
from django.http import JsonResponse

DATA = Path(settings.BASE_DIR) / "data"
OBJETOS = Path(settings.BASE_DIR) / "pipeline" / "objetos.json"
SLUG_OK = re.compile(r"^[a-z0-9-]+$")


def _conocidos():
    lista = json.loads(OBJETOS.read_text(encoding="utf-8"))
    return {o["slug"]: o for o in lista}


def _leer(slug):
    ruta = DATA / slug / "datos.json"
    if ruta.exists():
        return json.loads(ruta.read_text(encoding="utf-8"))
    return None


def lista_objetos(request):
    salida = []
    for slug, o in _conocidos().items():
        d = _leer(slug)
        salida.append({
            "slug": slug,
            "nombre": o["nombre"],
            "tipo": o["tipo"],
            "estado": d["estado"] if d else "sin_datos",
            "cantidad_cuadros": len(d["cuadros"]) if d else 0,
        })
    return JsonResponse(salida, safe=False)


def detalle_objeto(request, slug):
    conocidos = _conocidos()
    if not SLUG_OK.match(slug) or slug not in conocidos:
        return JsonResponse(
            {"error": "objeto_desconocido",
             "mensaje": "Ese objeto no está en Nawi."},
            status=404)
    d = _leer(slug)
    if d is None:
        o = conocidos[slug]
        return JsonResponse({
            "slug": slug, "nombre": o["nombre"], "tipo": o["tipo"],
            "estado": "sin_datos",
            "motivo": "Todavía no se precalcularon datos para este objeto.",
            "cuadros": [], "latido": [],
        })
    return JsonResponse(d)