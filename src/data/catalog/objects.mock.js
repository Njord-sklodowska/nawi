/**
 * Catálogo de demostración de Nawi (fuente `mock`).
 *
 * Puntos clave:
 *  - Los `id` están alineados con backend/pipeline/objetos.json de la rama
 *    sergio-backend (repo Njord-sklodowska/nawi), porque viajan en la URL
 *    compartida (`?obj=`). Si el backend los cambia, se cambian acá.
 *
 * Qué contiene a propósito: SOLO identidad, tipo de objeto y propósito dentro
 * de la demo — lo que hoy se puede afirmar sin inventar nada.
 *
 * Qué NO contiene: observaciones, fechas de observación, bandas, resultados
 * científicos ni coordenadas verificadas.
 *
 * Sobre `coordinates`: son PLACEHOLDERS de la maqueta que ya estaban en la
 * interfaz. Se conservan para no romper el visor, pero cada uno viaja con
 * `status` y `statusLabel` para que la UI los muestre siempre etiquetados como
 * no validados o a confirmar. No se usan para consultar datos ni para calcular.
 * El único valor que aparece en el plan de trabajo es el de WISE 0855, citado
 * allí como época de referencia "a confirmar".
 */

export const MOCK_OBJECTS = Object.freeze([
  Object.freeze({
    id: 'barnard',
    name: 'Estrella de Barnard',
    kind: 'Estrella cercana de movimiento propio muy alto',
    purpose: 'movimiento',
    purposeLabel: 'Movimiento propio',
    tag: 'MOVIMIENTO',
    demoRole: 'Objeto principal de la demo',
    demoUse: 'Alineación entre fechas, desplazamiento visible y medición.',
    coordinates: Object.freeze({
      ra: '17h 57m 48.5s',
      dec: '+04° 41′ 36″',
      status: 'ilustrativo',
      statusLabel: 'NO VALIDADO',
      note: 'Placeholder de la maqueta: no fue validado contra catálogos.',
    }),
  }),
  Object.freeze({
    id: 'wise-0855',
    name: 'WISE 0855',
    kind: 'Enana marrón de movimiento propio rápido',
    purpose: 'bonus',
    purposeLabel: 'Bonus',
    tag: 'BONUS',
    demoRole: 'Objeto bonus, solo si se detecta',
    demoUse: 'Caso de movimiento propio extremo; en infrarrojo cercano es muy tenue.',
    coordinates: Object.freeze({
      ra: '08h 55m 10.8s',
      dec: '−07° 14′ 43″',
      status: 'referencia-de-plan',
      statusLabel: 'A CONFIRMAR',
      note: 'Valor citado en el plan como época de referencia; la época todavía no se confirmó.',
    }),
  }),
  Object.freeze({
    id: 'epsilon-indi-b',
    name: 'Epsilon Indi B',
    kind: 'Par de enanas marrones que orbita una estrella',
    purpose: 'sistema',
    purposeLabel: 'Sistema múltiple',
    tag: 'SISTEMA',
    demoRole: 'Alternativa al objeto principal',
    demoUse: 'Caso de sistema: falta verificar si el par se resuelve con la resolución de SPHEREx.',
    coordinates: Object.freeze({
      ra: '22h 04m 10.5s',
      dec: '−56° 46′ 58″',
      status: 'ilustrativo',
      statusLabel: 'NO VALIDADO',
      note: 'Placeholder de la maqueta: no fue validado contra catálogos.',
    }),
  }),
  Object.freeze({
    id: 'rw-aurigae',
    name: 'RW Aurigae',
    kind: 'Estrella variable',
    purpose: 'variabilidad',
    purposeLabel: 'Variabilidad',
    tag: 'VARIABLE',
    demoRole: 'Objeto de la función "Latido"',
    demoUse: 'Cambia de brillo, no de posición: sirve para la curva de brillo.',
    coordinates: Object.freeze({
      ra: '05h 07m 49.6s',
      dec: '+30° 24′ 05″',
      status: 'ilustrativo',
      statusLabel: 'NO VALIDADO',
      note: 'Placeholder de la maqueta: no fue validado contra catálogos.',
    }),
  }),
  Object.freeze({
    id: 'r-draconis',
    name: 'R Draconis',
    kind: 'Estrella variable',
    purpose: 'variabilidad',
    purposeLabel: 'Variabilidad',
    tag: 'VARIABLE',
    demoRole: 'Objeto de la función "Latido"',
    demoUse: 'Cambia de brillo, no de posición: sirve para la curva de brillo.',
    coordinates: Object.freeze({
      ra: '16h 01m 25.9s',
      dec: '+66° 48′ 10″',
      status: 'ilustrativo',
      statusLabel: 'NO VALIDADO',
      note: 'Placeholder de la maqueta: no fue validado contra catálogos.',
    }),
  }),
]);
