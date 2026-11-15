# Nawi: plan de trabajo (versión 2)

**Equipo:** Sergio (backend y datos), Jorge (frontend), Ceci (segunda línea de backend, validación, coordinación y presentación).
**Base:** el plan original del equipo, el enunciado del desafío "Planet X and SPHEREx" (NASA Space Apps 2026) y los ajustes acordados.

> El reparto de roles es una propuesta. Si alguien rinde más en otro lugar, se intercambia.

---

## 0. Qué cambió respecto de la versión 1

1. **Tiempo real: unas 30 horas, no 48.** El cronograma ahora es por reloj, con descanso y un corte duro de código.
2. **Se precalcula primero.** La demo no depende de IRSA en vivo. La consulta en vivo es un extra. Se elimina MySQL.
3. **Objeto principal de la demo: la estrella de Barnard.** WISE 0855 pasa a ser un bonus, porque es muy tenue en el infrarrojo cercano y no sabemos si SPHEREx la detecta bien.
4. **Corrección por movimiento propio (nuevo e importante).** Estos objetos se mueven rápido. WISE 0855 se mueve cerca de 8,1 segundos de arco por año, así que hoy está a varios minutos de arco de las coordenadas del enunciado, que corresponden a una época de referencia. Si se consulta con esas coordenadas fijas y un campo chico, puede aparecer vacío. Hay que centrar el campo en la posición propagada a la fecha de las observaciones.
5. **Se cubre un hueco del MVP: las estrellas variables.** RW Aurigae y R Draconis cambian de brillo, no de posición. Se agrega "Latido" (curva de brillo).
6. **D2 usa SIMBAD y Gaia, no JPL.** JPL es para asteroides y cometas, y los cinco objetos de prueba son estrellas y enanas marrones.
7. **D1 mide con centroides automáticos**, no con clics manuales, y siempre informa la incertidumbre.
8. **Se suma impacto visual y conexión con el usuario:** "Revelar", "Rastro" y "En palabras simples".
9. **Pregunta nueva para la Fase 1:** cada imagen de SPHEREx mira distintas longitudes de onda según la posición. Hay que saber en qué longitud de onda cae cada objeto, porque si no, la curva de brillo mezcla variabilidad con espectro.
10. **Se agrega la tabla de fuentes con links** (sección 6).
11. **Se quitan:** MySQL, JPL, y los recursos de socios (NEOSSat y CADC).

---

## 1. Qué es Nawi

Una herramienta web pública donde cualquier persona ingresa un objeto (o coordenadas del cielo) y ve **una serie de imágenes de SPHEREx como un pequeño video**, para encontrar objetos que se mueven o cambian de brillo.

**Pitch en una frase:** *Nawi te presta un ojo infrarrojo de la NASA: viajá en el tiempo, seguí el rastro de lo que se mueve y hacé aparecer lo que el ruido esconde.*

**Para quién es:** estudiantes, docentes y curiosos que nunca abrieron un dato de la NASA, y voluntarios de ciencia ciudadana como los de Backyard Worlds, que ya descubrieron cometas y enanas marrones comparando imágenes.

> El nombre viene del quichua (ñawi, "ojo"). Confirmar la escritura y el significado con un hablante de quichua santiagueño antes de usarlo en la presentación.

---

## 2. Qué pide el desafío (lo que manda)

- Herramienta web pública que muestra imágenes de SPHEREx a lo largo del tiempo.
- El usuario ingresa **ascensión recta y declinación**.
- Se muestra una **serie de imágenes, como un video**, para identificar objetos en movimiento.
- El código debe ser abierto y fácil de actualizar con datos nuevos.

**Los 5 objetos de prueba y su papel en la demo**

| Objeto | Qué es | Papel en la demo |
|---|---|---|
| **Estrella de Barnard** | Estrella cercana de movimiento propio muy alto | **Principal.** Valida alineación, movimiento y medición. Si aparece saturada o con artefactos, el principal pasa a ser Epsilon Indi. |
| **WISE 0855** | Enana marrón de movimiento rápido (RA 08h55m10.831s, dec -7d14m42.53s, época de referencia a confirmar) | **Bonus**, si se detecta. |
| **Epsilon Indi B** | Par de enanas marrones que orbita una estrella | Alternativa al principal. Probablemente el par no se separe con píxeles de 6,2″, a verificar. |
| **RW Aurigae** | Estrella variable | "Latido" |
| **R Draconis** | Estrella variable | "Latido" |

---

## 3. Funcionalidades por prioridad

### MVP (obligatorio para la demo)
| # | Nombre | Qué hace | Responsable principal |
|---|---|---|---|
| M1 | **Galería de objetos** | Entrada por nombre, por coordenadas, o con un clic en uno de los 5 objetos. Aplica la corrección por movimiento propio. | Jorge + Ceci |
| M2 | **Datos precalculados** | Imágenes, fechas y metadatos ya procesados de los 5 objetos, servidos desde archivos | Sergio |
| M3 | **Recortes alineados** | Recortes reales de SPHEREx (FITS) reproyectados a una misma grilla | Sergio |
| M4 | **Máquina del tiempo** | Secuencia reproducible (play, pausa, deslizador, fecha visible) | Jorge |
| M5 | **Antes y después** | Comparador con control para alternar dos fechas | Jorge |
| M6 | **Latido** | Curva de brillo por fecha para RW Aurigae y R Draconis, indicando la longitud de onda de cada punto | Ceci |
| M7 | **Link para compartir** | Coordenadas (y objeto) en la URL | Jorge + Sergio |
| M8 | **Los 5 objetos probados** | Cada uno verificado y documentado: qué se ve y qué no | Los tres |

### Diferenciales (en este orden de prioridad)
| # | Nombre | Qué hace | Responsable principal | Depende de |
|---|---|---|---|---|
| D1 | **Revelar** ("del ruido a la señal") | Apila imágenes de distintas fechas desplazándolas según el movimiento conocido, y muestra un gráfico de cómo mejora la señal | Sergio (cálculo) + Jorge (efecto) | Alineación correcta (M3) |
| D2 | **Rastro** | Dibuja la trayectoria del objeto y mide su desplazamiento (segundos de arco, dirección, incertidumbre) con centroides automáticos. Se valida contra el movimiento propio publicado. | Ceci (validación) + Sergio | WCS utilizable en las imágenes |
| D3 | **¿Ya lo conocemos?** | Cruza con SIMBAD y Gaia y marca "conocido" o "candidato a revisar" | Ceci + Jorge | Consulta por posición y época |
| D4 | **En palabras simples** | Convierte los números calculados en una frase cotidiana. Solo usa valores que calculó el código, sin inventar datos. | Ceci + Jorge | D2 |

### Extras (solo si todo lo anterior anda, en este orden)
1. **Mañana**: dónde va a estar el objeto dentro de unos años según su movimiento propio, validado comprobando que la predicción para hoy coincide con lo observado.
2. **Entrenamiento**: un objeto simulado, claramente rotulado como simulación, para que el usuario practique cómo se descubre algo.
3. **Escuchá el latido**: el brillo de las variables convertido en sonido (Web Audio).
4. **Campo de visión elegible**, metadatos visibles (indicadores de contaminación) y superposición con Gaia o WISE (Aladin Lite).
5. **Puerta**: animación de apertura con diseño propio (sin usar nombres, logos ni símbolos de obras con derechos).
6. Espectros al vuelo, interfaz completa en español, "Viaje 2010→hoy" con WISE (más riesgoso: otras bandas).

---

## 4. Cronograma y fases

**Hora de Argentina.** Hoy sábado 14 de noviembre, entrega el domingo 15 a las 20:00.

| Cuándo | Fase |
|---|---|
| Sáb 14:00 a 15:00 | Fase 0: alineación |
| Sáb 15:00 a 18:00 | Fase 1: validación técnica |
| Sáb 18:00 a 22:00 | Fase 2: prototipo de punta a punta |
| Sáb 22:00 a Dom 02:00 | Fase 3: MVP completo |
| Dom 02:00 a 08:00 | **Descanso de todo el equipo** |
| Dom 08:00 a 12:00 | Fase 4: diferenciales |
| Dom 12:00 a 14:00 | Fase 5: pulido. **14:00: se congela el código.** |
| Dom 14:00 a 19:00 | Fase 6: presentación y carga |
| **Dom 19:00** | **Entrega** (1 hora de margen antes de las 20:00) |

**Compuertas** (si no se cumplen, se corta o se simplifica sin culpa):
- **Compuerta 1, sáb 16:30:** imágenes reales de SPHEREx abiertas desde Python.
- **Compuerta 2, sáb 18:00:** Barnard alineada en al menos 2 fechas con el movimiento visible.
- **Compuerta 3, dom 10:00:** "Revelar" funciona sobre algún objeto. Si no, se descarta y se sigue con "Rastro".
- **Corte duro, dom 12:00:** lo que no funciona hasta acá no entra al pitch.

---

### Fase 0: Alineación (los 3 juntos)
- [ ] Leer el enunciado y esta versión del plan.
- [ ] Sergio explica en pocos minutos qué es un archivo FITS y qué devuelve una consulta a IRSA.
- [ ] Ceci crea el repositorio público en GitHub (con licencia abierta) y define ramas: una principal y una por persona.
- [ ] Repasar los notebooks de IRSA y WiseView (como modelo de interfaz).
- [ ] Acordar cada cuánto integran.

**Criterio de salida:** repo creado, entorno listo y objetivo claro.

---

### Fase 1: Validación técnica (crítica)
**Objetivo:** comprobar que se pueden obtener, abrir y alinear imágenes reales de SPHEREx.

| Persona | Tareas |
|---|---|
| **Sergio** | Consulta a IRSA desde Python (notebooks de tutorial, SIA2, recortes). Probar con **Barnard**. Abrir recortes de **al menos dos fechas**. |
| **Ceci** | Con astropy, calcular la posición de Barnard propagada a la fecha de cada observación (movimiento propio de SIMBAD o Gaia) y comprobar que el objeto aparece donde se predice. Registrar los hallazgos por escrito. |
| **Jorge** | Proyecto React + Vite con Bootstrap. Layout base (selector + zona de imagen + deslizador). |

**Preguntas que esta fase tiene que responder (por escrito):**
1. ¿Cuántas observaciones hay para cada uno de los 5 objetos y en qué fechas?
2. ¿Las imágenes traen coordenadas utilizables (WCS) para alinear y medir?
3. ¿Se ve el movimiento entre fechas? ¿Barnard sale saturada o con artefactos?
4. ¿Cuánto pesan y cuánto tardan las descargas? ¿Qué tamaño de recorte conviene (3 a 5 minutos de arco para empezar)?
5. ¿En qué longitud de onda cae cada objeto en cada observación?
6. ¿Se detectan WISE 0855 y Epsilon Indi B?
7. ¿La época de las coordenadas del enunciado para WISE 0855 es J2000 o la del descubrimiento?

> **Si esta fase falla:** problema de los tres. Se detiene todo y se resuelve. Plan B de datos: bajar a mano los recortes desde el explorador web de IRSA y trabajar con archivos locales. Consultar también a mentores y organizadores.

---

### Fase 2: Prototipo de punta a punta (Barnard)
| Persona | Tareas |
|---|---|
| **Sergio** | Script de **precálculo**: para un objeto, baja recortes, los reproyecta a una grilla común, genera cuadros y un JSON de metadatos (fechas, banda, indicadores de calidad). |
| **Ceci** | Backend en Django REST que sirve lo precalculado. Manejo de errores (sin datos, objeto desconocido). |
| **Jorge** | Selector conectado al backend. Máquina del tiempo (secuencia con play, pausa y deslizador). |

**Criterio de salida:** elegís Barnard y ves la secuencia con imágenes reales de distintas fechas.

---

### Fase 3: MVP completo
| Persona | Tareas |
|---|---|
| **Sergio** | Precalcular los 5 objetos. Soportar la serie completa. Dejar el script fácil de re-ejecutar con datos nuevos. |
| **Ceci** | **Latido** (fotometría de apertura, por ejemplo con photutils, indicando la longitud de onda de cada punto). Documentar qué se ve y qué no en cada objeto. |
| **Jorge** | Antes y después, link para compartir, galería de objetos con acceso rápido a los 5. |

**Criterio de salida:** los 5 objetos funcionan, la secuencia se reproduce, un link abre la misma vista y las variables muestran su curva.

> **Esto ya es una demo presentable.** Si el tiempo se acaba acá, el proyecto cumple el desafío.

---

### Fase 4: Diferenciales
**Antes de empezar,** revisar las respuestas de la Fase 1. Si las imágenes no traen WCS utilizable, D2 se reduce a una comparación visual y D1 se reevalúa.

**D1, Revelar:** Sergio apila los cuadros desplazándolos según el movimiento conocido y calcula cómo mejora la relación señal-ruido. Jorge arma el efecto visual (el objeto se afila al sumar) y el gráfico de mejora. *Nota:* con Barnard, que es brillante, el efecto se ve sobre todo en el ruido de fondo. El efecto más dramático depende de un objeto tenue (WISE 0855 o Epsilon Indi B), a definir en la Fase 1.

**D2, Rastro:** Sergio y Ceci miden el desplazamiento con centroides automáticos y lo informan con su incertidumbre. **Se valida contra el movimiento propio publicado.** Jorge dibuja la trayectoria.

**D3, ¿Ya lo conocemos?:** Ceci consulta SIMBAD y Gaia por posición y época. Redacción cuidadosa: "no coincide con lo conocido" significa **candidato a revisar**, nunca descubrimiento confirmado.

**D4, En palabras simples:** frases construidas solo con números calculados (por ejemplo, el desplazamiento comparado con algo cotidiano), revisadas por Ceci.

**Criterio de salida:** al menos D1 o D2 validado con Barnard, y D3 con un ejemplo real.

---

### Fase 5: Pulido (hasta las 14:00)
- Corregir errores a la vista, rendimiento y datos de respaldo.
- Interfaz clara, con textos en español para el usuario común.
- Pruebas de punta a punta. **Congelar versión estable a las 14:00.**

---

### Fase 6: Presentación (14:00 a 19:00)
**Responsable principal: Ceci, con Jorge. Sergio prepara la demo en vivo.**
- [ ] Guion de 3 a 5 minutos (sección 7).
- [ ] Demo ensayada con datos reales, mínimo dos veces completas.
- [ ] Video de respaldo grabado de la demo.
- [ ] Diapositiva de arquitectura y de validación (Barnard contra el valor publicado).
- [ ] README con instrucciones, fuentes, créditos y **declaración del uso de IA**.
- [ ] Una persona lista para preguntas técnicas y otra para las científicas.
- [ ] Subir la entrega **antes de las 19:00**.

---

## 5. Arquitectura

**Principio: precalcular primero.** Un script de Python, para cada objeto, consulta IRSA, baja recortes, los reproyecta a una grilla común y guarda cuadros (PNG o WebP) más un JSON con fechas, bandas, indicadores de calidad, movimiento propio y series de brillo. El backend en Django REST sirve esos archivos. La consulta en vivo a IRSA es un extra, nunca el camino de la demo.

**Centrado del campo:** para cada objeto, el centro se calcula propagando su posición por movimiento propio a la fecha media de las observaciones (con astropy). Si un usuario ingresa coordenadas fijas de un objeto veloz, la interfaz avisa que puede estar fuera del campo y ofrece "buscar por nombre".

**Stack:** React + Vite, Bootstrap 5, Django REST Framework, Astropy, NumPy, reproject, photutils, astroquery, Plotly.js (curva de brillo), Aladin Lite (extra), Git y GitHub. Sin base de datos externa: archivos o SQLite.

---

## 6. Dónde se obtienen los datos (fuentes y links)

| Qué | Para qué se usa | Link |
|---|---|---|
| **SPHEREx en IRSA** (portal principal) | Punto de entrada a los datos y herramientas | https://irsa.ipac.caltech.edu/Missions/spherex.html |
| **Quick Release (QR2)** | Descripción de las publicaciones semanales. QR2 es la versión por defecto y reemplaza a QR1. | https://irsa.ipac.caltech.edu/data/SPHEREx/docs/overview_qr.html |
| **Acceso a datos SPHEREx** | APIs (SIA2: colecciones `spherex_qr`, `spherex_qr_deep`, `spherex_qr_cal`), Data Explorer web, ejemplos con `wget` y `curl` | https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-access |
| **Productos de datos** | Formato de los archivos (MEF), nombres de archivo, extensiones | https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-products |
| **Recortes (cutouts)** | Bajar solo la zona de interés (los archivos completos pesan cientos de megas) | https://irsa.ipac.caltech.edu/data/SPHEREx/docs/cutout_tool.html |
| **Tutoriales en Jupyter** | Ejemplos de acceso con Python | https://caltech-ipac.github.io/irsa-tutorials/spherex/ |
| **SPHEREx en la nube (AWS)** | Alternativa de descarga desde el repositorio abierto de AWS | https://registry.opendata.aws/spherex-qr/ |
| **APIs de imágenes de IRSA** | Imágenes de WISE, 2MASS y otros (para extras y comparaciones) | https://irsa.ipac.caltech.edu/docs/program_interface/api_images.html |
| **TAP de IRSA** | Consultas por tabla | https://irsa.ipac.caltech.edu/TAP/sync |
| **Gaia (usar Data Release 3)** | Posiciones, movimiento propio y cruce de catálogos | https://archive.stsci.edu/missions-and-data/gaia |
| **SIMBAD (CDS)** | Datos de objetos por nombre, movimiento propio y cruce para D3 | https://simbad.u-strasbg.fr/simbad/ |
| **astroquery** | Librería de Python para consultar IRSA, SIMBAD y otros servicios | https://astroquery.readthedocs.io/en/stable/ |
| **WiseView** | Modelo de interfaz usado por el público para hacer descubrimientos | http://byw.tools/wiseview |
| **SPXQuery** (no oficial, de la comunidad) | Referencia opcional para descarga y fotometría de series de tiempo | https://spxquery.readthedocs.io/en/latest/ |

> Los sitios que no son del gobierno de EE. UU. tienen sus propias condiciones de uso y citación. Revisarlas y acreditar a NASA/IPAC (IRSA), SPHEREx, Gaia/ESA y SIMBAD/CDS en el README y en la presentación.

**Datos de referencia para validar:** el movimiento propio de WISE 0855 está publicado en torno a 8,1 segundos de arco por año (por ejemplo https://arxiv.org/pdf/1605.08620). Para Barnard, tomar el valor de SIMBAD o Gaia en la Fase 1.

---

## 7. Estructura del pitch (3 a 5 minutos)

1. **Gancho local (20 s):** Santiago del Estero guarda en su suelo el rastro de un objeto que llegó del espacio hace unos 4.000 años (Campo del Cielo). Hoy, el cielo sigue guardando movimientos que casi nadie mira.
2. **Problema:** SPHEREx observa más de mil millones de objetos. Nadie puede revisarlos uno por uno.
3. **Idea histórica:** Plutón se descubrió comparando dos fotos. Miles de voluntarios hicieron lo mismo.
4. **Solución:** Nawi, un ojo infrarrojo de la NASA para cualquiera, en español.
5. **Demo en vivo (90 s):** entrás por nombre → **Máquina del tiempo** con Barnard → **Rastro** y la frase "En palabras simples" → **Revelar** → **Latido** de RW Aurigae → **¿Ya lo conocemos?**
6. **Validación:** nuestra medición de Barnard comparada con el valor publicado.
7. **Honestidad y futuro:** qué hace hoy, qué queda, y que se actualiza con los datos semanales de SPHEREx.
8. **Cierre:** *"Nawi: un ojo de la NASA, para todos."*

> Cada diferencial se menciona en el pitch solo si funciona en la demo.

---

## 8. Riesgos y cómo manejarlos

| Riesgo | Qué hacer |
|---|---|
| Descargas lentas o caída de IRSA | Todo precalculado y guardado en el repo. Video de respaldo. |
| El objeto sale fuera del campo por su movimiento propio | Centrar con propagación por movimiento propio (sección 5) |
| Barnard saturada o con artefactos | Usar Epsilon Indi como principal |
| WISE 0855 o Epsilon Indi B no se detectan | Documentarlo con honestidad y priorizar los que sí se ven |
| La curva de brillo mezcla longitudes de onda | Mostrar la longitud de onda de cada punto y compararlas por banda |
| Las imágenes no traen WCS utilizable | Reducir D2 a comparación visual con marcadores |
| "Revelar" no mejora con pocas épocas | Descartar en la compuerta 3 y pasar a "Rastro" |
| Falla internet en la demo | Plan B con datos y video guardados |
| Se agranda el alcance | Respetar compuertas y corte duro |
| Cansancio | Descanso obligatorio de 02:00 a 08:00 |

---

## 9. Reglas del equipo

1. **No se pasa a la fase siguiente sin cumplir el criterio de salida de la anterior.**
2. **Integrar seguido:** rama principal estable y ramas por persona.
3. **Probar siempre con datos reales.** Lo simulado se rotula como simulación.
4. **Todo el código generado con IA se valida con Barnard.** Si no da lo esperado, hay un error.
5. **Cada integrante debe poder explicar el método**, porque el jurado va a preguntar.
6. **Resultados siempre como "candidatos", nunca como "descubrimientos".**

---

## 10. Checklist final antes de entregar

- [ ] Los 5 objetos de prueba funcionan o están documentados con honestidad.
- [ ] La secuencia se reproduce y el comparador alterna.
- [ ] Un link con coordenadas abre la misma vista.
- [ ] Las variables muestran su curva de brillo.
- [ ] Los diferenciales que se mencionan funcionan en la demo.
- [ ] Datos de respaldo y video de respaldo en el repo.
- [ ] Demo ensayada al menos dos veces.
- [ ] Repo público con licencia, README, fuentes, créditos y declaración de uso de IA.
- [ ] Nombre "Nawi" confirmado con un hablante de quichua santiagueño.
- [ ] **Entregado antes de las 19:00.**
