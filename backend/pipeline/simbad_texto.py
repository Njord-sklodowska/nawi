import time
import requests

NOMBRES = ["eps Ind B", "eps Indi B", "eps Ind Bb", "eps Ind A"]
CLAVES = ("Object", "Coordinates(ICRS", "Proper motions", "Parallax", "Spectral type")

def ficha(nombre, intentos=4):
    for i in range(intentos):
        try:
            r = requests.get(
                "https://simbad.cfa.harvard.edu/simbad/sim-id",
                params={"output.format": "ASCII", "Ident": nombre},
                timeout=60,
            )
            r.raise_for_status()
            return r.text
        except Exception as e:
            print(f"  intento {i+1} falló: {str(e)[:70]}")
            time.sleep(10)
    return None

for n in NOMBRES:
    print("=" * 50, n)
    t = ficha(n)
    if t is None:
        print("No se pudo consultar."); continue
    hallado = False
    for linea in t.splitlines():
        if linea.startswith(CLAVES):
            print(linea.strip()); hallado = True
    if not hallado:
        print("SIMBAD no devolvió datos para ese nombre. Primeras líneas:")
        print("\n".join(t.splitlines()[:8]))