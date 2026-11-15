import json
from pathlib import Path
import numpy as np
from PIL import Image

base = Path(__file__).resolve().parents[1] / "data" / "barnard"
d = json.loads((base / "datos.json").read_text(encoding="utf-8"))

for c in d["cuadros"]:
    png = np.array(Image.open(base / "frames" / Path(c["url"]).name))
    iy, ix = np.unravel_index(np.argmax(png), png.shape)
    ex, ey = c["pos_esperada_px"]["x"], c["pos_esperada_px"]["y"]
    print(f'{c["fecha"][:10]}  esperado=({ex:.1f},{ey:.1f})  '
          f'más brillante=({ix},{iy})  dist={np.hypot(ix-ex, iy-ey):.1f}px  '
          f'calidad_ok={c["calidad_ok"]}')