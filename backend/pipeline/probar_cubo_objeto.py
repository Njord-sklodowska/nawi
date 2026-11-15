
"""
Prueba de integración astrométrica y espacial de NAWI.

1. Obtiene la posición del objeto desde el catálogo.
2. Calcula su posición para una fecha determinada.
3. Localiza el píxel HEALPix correspondiente.
4. Comprueba la disponibilidad del cubo SPHEREx.
"""

from astrometria import calcular_posicion
from catalogo import AstrometriaNoDisponibleError
from hips_index import buscar_cubo


def localizar_objeto(slug, fecha):
    """Calcula la posición y localiza su cubo SPHEREx."""

    posicion = calcular_posicion(slug, fecha)

    cubo = buscar_cubo(
        posicion["ra_deg"],
        posicion["dec_deg"]
    )

    return {
        "objeto": posicion,
        "cubo": cubo,
    }


def main():

    print("=" * 60)
    print("INTEGRACIÓN ASTROMETRÍA + HEALPix + SPHEREx")
    print("=" * 60)

    slug = "barnard"
    fecha = "2026-11-15"

    try:
        resultado = localizar_objeto(slug, fecha)

        objeto = resultado["objeto"]
        cubo = resultado["cubo"]
        disponibilidad = cubo["disponibilidad"]

        print("\nDATOS DEL OBJETO")
        print("-" * 45)
        print("Identificador:", objeto["slug"])
        print("Nombre:", objeto["nombre"])
        print("Fecha:", objeto["fecha_observacion"])
        print("RA calculada:", objeto["ra_deg"])
        print("Dec calculada:", objeto["dec_deg"])
        print("Fuente:", objeto["fuente"]["estado"])

        print("\nLOCALIZACIÓN ESPACIAL")
        print("-" * 45)
        print("Orden HEALPix:", cubo["orden_healpix"])
        print("NSIDE:", cubo["nside"])
        print("Píxel:", cubo["pixel"])
        print("Directorio:", cubo["directorio"])

        print("\nCUBO SPHEREx")
        print("-" * 45)
        print("URL:", cubo["url"])
        print("HTTP:", disponibilidad["http"])
        print("Disponible:", disponibilidad["disponible"])

        if disponibilidad.get("tamano_bytes") is not None:
            tamano_mb = disponibilidad["tamano_bytes"] / (1024 ** 2)
            print(f"Tamaño: {tamano_mb:.2f} MB")

        if disponibilidad.get("error"):
            print("Error:", disponibilidad["error"])

        print("\nPRUEBA DE INTEGRACIÓN FINALIZADA")

    except AstrometriaNoDisponibleError as error:
        print("ASTROMETRÍA NO DISPONIBLE:", error)

    except (ValueError, TypeError) as error:
        print("ERROR DE DATOS:", error)


if __name__ == "__main__":
    main()
