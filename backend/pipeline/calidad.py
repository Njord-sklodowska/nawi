
"""
Módulo de control de calidad espectral de NAWI.

Analiza las extensiones IMAGE, NHITS y FLAGS
de los cubos espectrales SPHEREx.
"""

import numpy as np


def analizar_calidad(image, nhits, flags):
    """
    Analiza la calidad de cada canal espectral.

    Parámetros:
        image: valores espectrales de IMAGE.
        nhits: cantidad de contribuciones por canal.
        flags: indicadores de calidad por canal.

    Retorna:
        Diccionario con resumen y diagnóstico por canal.
    """

    image = np.asarray(image, dtype=float).ravel()
    nhits = np.asarray(nhits).ravel()
    flags = np.asarray(flags).ravel()

    if not (len(image) == len(nhits) == len(flags)):
        raise ValueError(
            "IMAGE, NHITS y FLAGS deben tener "
            "la misma cantidad de canales."
        )

    if len(image) == 0:
        raise ValueError("No hay canales para analizar.")

    if not np.all(np.isfinite(nhits)):
        raise ValueError("NHITS contiene valores no finitos.")

    if not np.all(np.isfinite(flags)):
        raise ValueError("FLAGS contiene valores no finitos.")

    if not np.all(nhits == np.floor(nhits)):
        raise ValueError("NHITS debe contener valores enteros.")

    if not np.all(flags == np.floor(flags)):
        raise ValueError("FLAGS debe contener valores enteros.")

    nhits = nhits.astype(np.int64)
    flags = flags.astype(np.int64)

    if np.any(nhits < 0):
        raise ValueError("NHITS no puede ser negativo.")

    if np.any(flags < 0):
        raise ValueError("FLAGS no puede ser negativo.")

    canales = []

    disponibles = 0
    sin_datos = 0
    inconsistentes = 0

    for indice in range(len(image)):
        valor = float(image[indice])
        contribuciones = int(nhits[indice])
        indicadores = int(flags[indice])

        finito = bool(np.isfinite(valor))

        if finito and contribuciones > 0:
            estado = "disponible"
            disponibles += 1

        elif not finito and contribuciones == 0:
            estado = "sin_datos"
            sin_datos += 1

        else:
            estado = "inconsistente"
            inconsistentes += 1

        bits_activados = [
            bit
            for bit in range(32)
            if indicadores & (1 << bit)
        ]

        canales.append({
            "canal": indice + 1,
            "valor_mjy_sr": valor if finito else None,
            "nhits": contribuciones,
            "flags": indicadores,
            "bits_activados": bits_activados,
            "estado": estado,
        })

    valores_finitos = image[np.isfinite(image)]

    resumen = {
        "total_canales": len(image),
        "canales_disponibles": disponibles,
        "canales_sin_datos": sin_datos,
        "canales_inconsistentes": inconsistentes,
        "valores_finitos": int(np.isfinite(image).sum()),
        "valores_no_finitos": int((~np.isfinite(image)).sum()),
        "canales_nhits_cero": int(np.count_nonzero(nhits == 0)),
        "nhits_minimo": int(nhits.min()),
        "nhits_maximo": int(nhits.max()),
        "flags_distintos": [
            int(valor) for valor in np.unique(flags)
        ],
        "canales_con_flags": int(np.count_nonzero(flags != 0)),
    }

    if len(valores_finitos) > 0:
        resumen.update({
            "valor_minimo_mjy_sr": float(valores_finitos.min()),
            "valor_maximo_mjy_sr": float(valores_finitos.max()),
            "valor_promedio_mjy_sr": float(valores_finitos.mean()),
        })
    else:
        resumen.update({
            "valor_minimo_mjy_sr": None,
            "valor_maximo_mjy_sr": None,
            "valor_promedio_mjy_sr": None,
        })

    return {
        "resumen": resumen,
        "canales": canales,
    }


def imprimir_informe(resultado):
    """
    Imprime el informe de calidad espectral.
    """

    resumen = resultado["resumen"]
    canales = resultado["canales"]

    print("=" * 65)
    print("INFORME DE CALIDAD ESPECTRAL - NAWI")
    print("=" * 65)

    print("\nRESUMEN")
    print("-" * 65)

    for nombre, valor in resumen.items():
        print(f"{nombre}: {valor}")

    print("\nDETALLE POR CANAL")
    print("-" * 80)

    print(
        f"{'CANAL':>5} | "
        f"{'IMAGE (MJy/sr)':>16} | "
        f"{'NHITS':>5} | "
        f"{'FLAGS':>10} | "
        f"{'ESTADO':<15}"
    )

    print("-" * 80)

    for canal in canales:
        valor = canal["valor_mjy_sr"]

        valor_texto = (
            f"{valor:.6f}"
            if valor is not None
            else "NaN"
        )

        print(
            f"{canal['canal']:5} | "
            f"{valor_texto:>16} | "
            f"{canal['nhits']:5} | "
            f"{canal['flags']:10} | "
            f"{canal['estado']:<15}"
        )

    print("\nANÁLISIS FINALIZADO")
