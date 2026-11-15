# Nawi: hallazgos de la Fase 1 (validación técnica)

Estado al domingo 15/11, 12:00. Solo datos de SPHEREx (IRSA), SIMBAD y cálculos con astropy.
Lo que no se midió figura como **pendiente**. No se inventó ningún número.

## Resultado general

**Compuerta 2 cumplida para la posición.** Barnard aparece donde la predice el cálculo en 7 de 7 fechas de `spherex_dr1`, con error de 0,2 a 0,7 píxeles. El brillo en ese punto es unas 2.000 a 5.600 veces la mediana de la imagen.

| Fecha | Píxel esperado (x, y) | Más brillante (x, y) | Distancia (px) |
|---|---|---|---|
| 2025-08-15 | 28,6 / 30,5 | 28 / 31 | 0,7 |
| 2025-08-18 | 29,2 / 30,3 | 29 / 30 | 0,3 |
| 2025-08-25 | 28,9 / 30,1 | 29 / 30 | 0,2 |
| 2026-03-19 | 28,7 / 27,9 | 29 / 28 | 0,3 |
| 2026-03-23 | 28,5 / 28,5 | 28 / 29 | 0,7 |
| 2026-04-10 | 28,4 / 27,7 | 28 / 28 | 0,5 |
| 2026-05-04 | 28,6 / 27,8 | 29 / 28 | 0,4 |

Los píxeles no se comparan entre imágenes distintas (cada una tiene su propia orientación). El desplazamiento real se mide en coordenadas del cielo y es trabajo del Rastro (pendiente).

## Las 7 preguntas

### 1. ¿Cuántas observaciones hay y en qué fechas?
- **Barnard, `spherex_dr1`:** 239 filas en un radio de 0,01° (cada fila es un detector de una exposición). Observaciones del **15/08/2025 al 05/05/2026**, en 10 semanas: 2025W33, W34, W35, W36, W40 y 2026W11, W12, W13, W15, W19.
- **Barnard, `spherex_qr3`:** la consulta se topó en 40 filas (límite que pusimos), con observaciones del **16/08/2026 al 22/09/2026**. No es el total.
- `spherex_qr` (QR2) no se puede buscar por el servicio SIA2.
- **Los otros 4 objetos: pendiente.**
- Ojo: `obs_release_date` es la fecha de publicación, no la de observación. La fecha real sale de `t_min`/`t_max` o de `DATE-AVG` en el encabezado del FITS.

### 2. ¿Las imágenes traen coordenadas utilizables (WCS)?
Sí. La extensión `IMAGE` trae WCS celeste y la validación con Barnard lo confirma. El archivo trae además `FLAGS`, `VARIANCE`, `ZODI`, `EPSF` y `WCS-WAVE`. Pixel de 6,15″.

### 3. ¿Se ve el movimiento entre fechas? ¿Hay saturación?
- Barnard se mueve unos **10,4″ por año** (movimiento propio de Gaia DR3 vía SIMBAD), es decir **1,7 píxeles por año**.
- En las fechas de `qr3` (35 días) el movimiento es menor a 0,2 píxel: no se ve. Con `dr1` más `qr3` hay más de un año de separación (unos 1,7 px).
- La **medición** del desplazamiento en el cielo está **pendiente** (Rastro).
- Saturación: el pico es de unas 1.000 a 1.700 unidades contra una mediana de 0,3 a 0,5, sin señales de recorte a simple vista. **Falta revisar la máscara `FLAGS`.**

### 4. ¿Cuánto pesan y cuánto tardan las descargas? ¿Qué recorte conviene?
- Un recorte de 0,1° (6 minutos de arco) da imágenes de unos 58×58 píxeles. El primero que se bajó pesó **3,8 MB**.
- Si el recorte cae cerca del borde del detector sale cortado (un caso dio 58×21 y Barnard quedó afuera). Hay que elegir observaciones con margen: el script `bajar_barnard.py` pide al menos 200″ de margen.
- IRSA anduvo de forma intermitente (errores 502 y de capacidades). El script reintenta solo. **Tiempo por descarga: no medido.**
- Recomendación: **0,1° de lado**, una observación por semana, un solo detector.

### 5. ¿En qué longitud de onda cae cada objeto?
- Los 7 archivos de Barnard son del **detector D6: banda de 4,41 a 5,01 µm** (según la tabla de IRSA).
- Dentro de cada imagen la longitud de onda cambia de un píxel a otro (la tabla `WCS-WAVE` lo describe). El script `ver_longitud_onda.py` intenta leerla: **resultado pendiente**.
- Consecuencia: en el Latido no se pueden mezclar bandas distintas sin avisarlo.

### 6. ¿Se detectan WISE 0855 y Epsilon Indi B?
**Pendiente.** Notas:
- WISE 0855 se mueve unos 8,15″ por año, y es muy tenue.
- Epsilon Indi B es un **par** de enanas marrones (T1 + T6) a menos de 1″ entre sí: SPHEREx las verá como un solo punto. Está a unos 6,7′ de la estrella central, hay que centrar el recorte en B.

### 7. ¿La época de las coordenadas de WISE 0855 es J2000?
**No.** Las del enunciado (08h55m10.831s, −7°14′42.53″) son de **alrededor de 2010,4**, la época del satélite WISE.
- SIMBAD da la posición en J2000 a 08h55m16.538s, −7°14′49.37″, unos 85″ al este.
- Dividida por el movimiento propio (8,12″/año en ascensión recta), la diferencia da 10,4 años. La declinación da 10,2 años. Es un cálculo propio, consistente.
- Se usa la posición de SIMBAD en J2000 más su movimiento propio.

## Datos de los 5 objetos (SIMBAD, época J2000)

| Objeto | RA (°) | Dec (°) | pm RA (mas/año) | pm Dec (mas/año) |
|---|---|---|---|---|
| Barnard | 269,45207696 | 4,69336497 | −801,551 | 10362,394 |
| WISE 0855 | 133,81890825 | −7,247048 | −8123,7 | 673,2 |
| Epsilon Indi B | 331,04414659 | −56,7828442 | 3981,977 | −2466,832 |
| RW Aur | 76,95652603 | 30,40143817 | 7,23 | −20,33 |
| R Dra | 248,16761083 | 66,75497942 | −20,643 | 6,149 |

## Pendientes y problemas encontrados

- Pendiente: observaciones de los otros 4 objetos, longitud de onda (preguntas 1 y 5), detección de WISE 0855 y Epsilon Indi B (6), `FLAGS`, tiempos de descarga.
- Los valores de Barnard usados al principio eran de memoria y se corrigieron con SIMBAD.
- Se descartó un script que usaba imágenes de DSS (SkyView): no son de SPHEREx.
- El servidor principal de SIMBAD devolvió 404 y se usó el espejo de Harvard.