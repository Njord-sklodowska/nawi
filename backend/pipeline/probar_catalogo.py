
from catalogo import (
    cargar_catalogo,
    obtener_objeto,
    obtener_astrometria,
    AstrometriaNoDisponibleError,
)


print("=" * 55)
print("PRUEBA DEL CATÁLOGO ASTRONÓMICO NAWI")
print("=" * 55)

# 1. Comprobar carga del catálogo
catalogo = cargar_catalogo()
objetos = catalogo["objetos"]

print(f"\nObjetos encontrados: {len(objetos)}")

# 2. Recorrer todos los objetos
for slug, datos in objetos.items():

    print("\n" + "-" * 45)
    print(f"Identificador: {slug}")
    print(f"Nombre: {datos['nombre']}")

    try:
        resultado = obtener_astrometria(slug)
        astro = resultado["astrometria"]

        print("Estado: ASTROMETRÍA DISPONIBLE")
        print(f"RA: {astro['ra_deg']}°")
        print(f"Dec: {astro['dec_deg']}°")
        print(
            f"Movimiento propio RA: "
            f"{astro['pm_ra_cosdec_mas_yr']} mas/año"
        )
        print(
            f"Movimiento propio Dec: "
            f"{astro['pm_dec_mas_yr']} mas/año"
        )
        print(f"Referencia: {astro['fecha_referencia']}")
        print(f"Fuente: {resultado['fuente']['estado']}")

    except AstrometriaNoDisponibleError:
        print("Estado: PENDIENTE DE DATOS ASTROMÉTRICOS")

# 3. Comprobar búsqueda de un objeto
print("\n" + "=" * 55)
print("PRUEBA DE BÚSQUEDA")
print("=" * 55)

barnard = obtener_objeto("barnard")
print(f"Objeto encontrado: {barnard['nombre']}")

print("\nPRUEBA FINALIZADA")
