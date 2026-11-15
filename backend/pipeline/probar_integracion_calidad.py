
"""
Prueba de integración del control de calidad espectral NAWI.

Lee IMAGE, NHITS y FLAGS de SPHEREx para Barnard
y utiliza el módulo calidad.py para analizar los resultados.
"""

import numpy as np

from probar_calidad_pixel import (
    URL,
    X,
    Y,
    CANALES,
    leer_valor,
)

from calidad import analizar_calidad, imprimir_informe


def main():
    print("=" * 65)
    print("INTEGRACIÓN ESPECTRAL Y CONTROL DE CALIDAD - NAWI")
    print("=" * 65)

    print(f"Píxel: X={X}, Y={Y}")
    print(f"Canales espectrales: {CANALES}")

    resultados = {
        "IMAGE": [],
        "NHITS": [],
        "FLAGS": [],
    }

    import requests

    with requests.Session() as session:
        for extension in resultados:
            print(f"\nLeyendo extensión {extension}...")

            for canal in range(CANALES):
                valor = leer_valor(
                    session,
                    extension,
                    canal
                )

                resultados[extension].append(valor)

    image = np.array(resultados["IMAGE"], dtype=float)
    nhits = np.array(resultados["NHITS"], dtype=np.int64)
    flags = np.array(resultados["FLAGS"], dtype=np.int64)

    print("\nDatos recuperados correctamente.")

    print("\nAnalizando calidad espectral...")

    resultado = analizar_calidad(
        image=image,
        nhits=nhits,
        flags=flags,
    )

    imprimir_informe(resultado)

    print("\n" + "=" * 65)
    print("VERIFICACIÓN DE INTEGRIDAD")
    print("=" * 65)

    resumen = resultado["resumen"]

    print(
        "Canales recuperados:",
        resumen["total_canales"]
    )

    print(
        "Canales disponibles:",
        resumen["canales_disponibles"]
    )

    print(
        "Canales sin datos:",
        resumen["canales_sin_datos"]
    )

    print(
        "Canales inconsistentes:",
        resumen["canales_inconsistentes"]
    )

    if resumen["total_canales"] != CANALES:
        raise RuntimeError(
            "La cantidad de canales no coincide."
        )

    if resumen["canales_inconsistentes"] != 0:
        raise RuntimeError(
            "Se encontraron inconsistencias entre IMAGE y NHITS."
        )

    print("\nINTEGRACIÓN FINALIZADA CORRECTAMENTE.")


if __name__ == "__main__":
    main()
