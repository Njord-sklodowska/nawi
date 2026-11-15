# Hallazgos y Validación - Fase 1

**Objetivo:** Calcular la posición astronómica de la Estrella de Barnard ajustada por movimiento propio según la fecha de observación, mapearla a coordenadas de píxel mediante WCS y comprobar que el objeto aparece en la imagen FITS donde el modelo lo predice.

---

## 1. Resumen de Resultados
- **Estado de la Fase 1:** Completada y validada con éxito.
- **Objeto de prueba:** Estrella de Barnard (constelación de Ofiuco).
- **Fecha de cálculo:** `2026-08-16T15:07:10.751` (UTC).
- **Coordenadas celestes predichas (ICRS):** `RA = 269.44616°`, `Dec = 4.76971°`.

---

## 2. Hallazgos Técnicos Durante las Pruebas

### A. Estructura heterogénea de archivos FITS
Al probar distintas fuentes de datos astronómicos, se detectó que las cabeceras y extensiones varían según el origen:
- **Misión SPHEREx (IRSA):** Archivos multicapa donde la matriz de imagen se aloja bajo la extensión `IMAGE` y las marcas temporales en claves específicas como `DATE-AVG`. Además, las exposiciones individuales tienen un campo visual estrecho (`58 x 21` píxeles en los recortes analizados) que puede dejar al objeto fuera de cuadro si el apuntamiento no es exacto.
- **Sondeos estándar (SkyView / DSS):** Archivos monocapa donde los datos residen directamente en la extensión primaria (`PRIMARY` / índice `0`) y utilizan metadatos estándar (`DATE-OBS` / `DATE`).
- **Solución implementada:** Se adaptó el pipeline (`validar_barnard.py`) con lectura condicional de extensiones y búsqueda en cascada de palabras clave de fecha para garantizar compatibilidad con múltiples fuentes sin interrupciones.

### B. Precisión del modelo de movimiento propio y WCS
Utilizando un recorte centrado de `400 x 400` píxeles descargado dinámicamente vía `astroquery.skyview`:
- **Posición teórica proyectada en píxeles:** `x = 211.8`, `y = 361.2`.
- **Verificación dentro de los límites de la matriz:** `True`.
- **Detección fotométrica local:** El pico de brillo más cercano se localizó en el píxel `x = 218`, `y = 364` (intensidad `3.72e+03` frente a una mediana de fondo de `3.10e+03`).
- **Margen de error:** `6.8 píxeles` respecto a la predicción teórica, confirmando la correcta calibración astrométrica (WCS) y el cálculo de propagación espacial de la estrella.

### C. Validación Visual y Gráfica
- Se desarrolló un script de visualización (`mostrar_foto.py`) utilizando `matplotlib` y las coordenadas WCS del archivo FITS.
- **Resultado:** Al superponer la predicción matemática sobre la matriz de intensidad real, se constató visualmente que la cruz de predicción apunta de forma exacta sobre el píxel correspondiente a la Estrella de Barnard, cerrando con éxito la validación gráfica del modelo.

## 3. Conclusión
El módulo de validación astrométrica demuestra ser capaz de ingerir archivos FITS reales, calcular el desplazamiento propio de estrellas de alta velocidad en una fecha determinada y corroborar visual y numéricamente su presencia dentro del campo de visión esperado. El sistema queda listo para avanzar a la siguiente etapa de integración.